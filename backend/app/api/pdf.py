"""Routes de génération de PDF."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID
import hashlib
from datetime import datetime

from ..db.database import get_db
from ..db.models import Quote, QuoteVersion, QuoteLine, Project, Customer, Company, Subscription
from ..security.auth import get_current_user, AuthUser, check_company_access
from ..pdf.generator import generate_quote_pdf

router = APIRouter()


class PDFGenerateRequest(BaseModel):
    """Demande de génération PDF."""
    quote_version_id: str


class PDFGenerateResponse(BaseModel):
    """Réponse génération PDF."""
    pdf_path: str
    verification_hash: str
    verification_url: str


@router.post("/generate", response_model=PDFGenerateResponse)
async def generate_pdf(
    request: PDFGenerateRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Génère un PDF pour une version de devis."""
    version = db.query(QuoteVersion).filter(
        QuoteVersion.id == request.quote_version_id
    ).first()
    
    if not version:
        raise HTTPException(status_code=404, detail="Version de devis non trouvée")
    
    # Vérifier accès
    quote = db.query(Quote).filter(Quote.id == version.quote_id).first()
    project = db.query(Project).filter(Project.id == quote.project_id).first()
    check_company_access(str(project.company_id), current_user.company_id)
    
    # Récupérer toutes les données nécessaires
    customer = db.query(Customer).filter(Customer.id == project.customer_id).first()
    company = db.query(Company).filter(Company.id == project.company_id).first()
    subscription = db.query(Subscription).filter(
        Subscription.company_id == project.company_id
    ).first()
    lines = db.query(QuoteLine).filter(
        QuoteLine.quote_version_id == version.id
    ).all()
    
    # Déterminer si filigrane nécessaire
    is_trial = subscription.plan_id == "TRIAL" if subscription else True
    
    # Générer le PDF
    pdf_data = generate_quote_pdf(
        company_name=company.name,
        customer_name=customer.name,
        customer_city=customer.city,
        project_name=project.name,
        version=version.version,
        lines=lines,
        total=float(version.total) if version.total else 0.0,
        is_trial=is_trial
    )
    
    # Générer le hash de vérification
    hash_content = f"{version.id}-{datetime.utcnow().isoformat()}-{pdf_data[:100]}"
    verification_hash = hashlib.sha256(hash_content.encode()).hexdigest()
    
    # TODO: Upload vers Supabase Storage
    pdf_path = f"pdfs/{project.company_id}/{quote.id}/v{version.version}.pdf"
    
    # Enregistrer le chemin dans la version
    version.pdf_path = pdf_path
    db.commit()
    
    return PDFGenerateResponse(
        pdf_path=pdf_path,
        verification_hash=verification_hash,
        verification_url=f"/public/verify/{verification_hash}"
    )


@router.get("/verify/{hash}")
async def verify_pdf(hash: str, db: Session = Depends(get_db)):
    """Page publique de vérification d'un PDF."""
    # TODO: Implémenter la vérification du hash
    return {
        "valid": True,
        "message": "PDF authentique généré par Facade Suite"
    }
