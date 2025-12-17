"""Routes de gestion des devis avec versioning V1/V2/V3."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from decimal import Decimal

from ..db.database import get_db
from ..db.models import Quote, QuoteVersion, QuoteLine, Project, AuditLog
from ..security.auth import get_current_user, AuthUser, check_company_access

router = APIRouter()


class QuoteLineCreate(BaseModel):
    """Création d'une ligne de devis."""
    label: str
    quantity: float
    unit_price: float


class QuoteLineResponse(BaseModel):
    """Réponse ligne de devis."""
    id: str
    label: str
    quantity: float
    unit_price: float
    total: float

    class Config:
        from_attributes = True


class QuoteVersionResponse(BaseModel):
    """Réponse version de devis."""
    id: str
    version: int
    total: float
    pdf_path: Optional[str]
    created_at: str
    lines: List[QuoteLineResponse]

    class Config:
        from_attributes = True


class QuoteResponse(BaseModel):
    """Réponse devis complet."""
    id: str
    project_id: str
    status: str
    current_version: int
    created_at: str
    versions: List[QuoteVersionResponse]

    class Config:
        from_attributes = True


class QuoteVersionCreate(BaseModel):
    """Création d'une nouvelle version de devis."""
    lines: List[QuoteLineCreate]


def log_audit(db: Session, company_id: str, user_id: str, action: str):
    """Enregistre une action dans les logs d'audit."""
    audit_log = AuditLog(company_id=company_id, user_id=user_id, action=action)
    db.add(audit_log)
    db.commit()


@router.get("/{project_id}", response_model=QuoteResponse)
async def get_quote_by_project(
    project_id: UUID,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère le devis d'un chantier avec toutes ses versions."""
    # Vérifier l'accès au projet
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chantier non trouvé")
    
    check_company_access(str(project.company_id), current_user.company_id)
    
    # Récupérer le devis
    quote = db.query(Quote).filter(Quote.project_id == project_id).first()
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Devis non trouvé")
    
    # Récupérer toutes les versions avec leurs lignes
    versions = db.query(QuoteVersion).filter(
        QuoteVersion.quote_id == quote.id
    ).order_by(QuoteVersion.version.desc()).all()
    
    versions_response = []
    for version in versions:
        lines = db.query(QuoteLine).filter(
            QuoteLine.quote_version_id == version.id
        ).all()
        
        lines_response = [
            QuoteLineResponse(
                id=str(line.id),
                label=line.label or "",
                quantity=float(line.quantity) if line.quantity else 0.0,
                unit_price=float(line.unit_price) if line.unit_price else 0.0,
                total=float(line.total) if line.total else 0.0
            )
            for line in lines
        ]
        
        versions_response.append(
            QuoteVersionResponse(
                id=str(version.id),
                version=version.version,
                total=float(version.total) if version.total else 0.0,
                pdf_path=version.pdf_path,
                created_at=version.created_at.isoformat(),
                lines=lines_response
            )
        )
    
    return QuoteResponse(
        id=str(quote.id),
        project_id=str(quote.project_id),
        status=quote.status or "draft",
        current_version=quote.current_version or 1,
        created_at=quote.created_at.isoformat(),
        versions=versions_response
    )


@router.post("/{project_id}/version", response_model=QuoteVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_quote_version(
    project_id: UUID,
    version_data: QuoteVersionCreate,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crée une nouvelle version du devis (V1, V2, V3...)."""
    # Vérifier l'accès au projet
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chantier non trouvé")
    
    check_company_access(str(project.company_id), current_user.company_id)
    
    # Récupérer ou créer le devis
    quote = db.query(Quote).filter(Quote.project_id == project_id).first()
    if not quote:
        quote = Quote(project_id=project_id, status="draft", current_version=0)
        db.add(quote)
        db.commit()
        db.refresh(quote)
    
    # Incrémenter la version
    new_version_number = quote.current_version + 1
    
    # Calculer le total
    total = sum(
        line.quantity * line.unit_price
        for line in version_data.lines
    )
    
    # Créer la nouvelle version
    new_version = QuoteVersion(
        quote_id=quote.id,
        version=new_version_number,
        total=Decimal(str(total))
    )
    db.add(new_version)
    db.commit()
    db.refresh(new_version)
    
    # Créer les lignes
    lines_response = []
    for line_data in version_data.lines:
        line_total = line_data.quantity * line_data.unit_price
        
        line = QuoteLine(
            quote_version_id=new_version.id,
            label=line_data.label,
            quantity=Decimal(str(line_data.quantity)),
            unit_price=Decimal(str(line_data.unit_price)),
            total=Decimal(str(line_total))
        )
        db.add(line)
        db.commit()
        db.refresh(line)
        
        lines_response.append(
            QuoteLineResponse(
                id=str(line.id),
                label=line.label or "",
                quantity=float(line.quantity),
                unit_price=float(line.unit_price),
                total=float(line.total)
            )
        )
    
    # Mettre à jour la version courante du devis
    quote.current_version = new_version_number
    db.commit()
    
    # Log audit
    log_audit(
        db,
        current_user.company_id,
        current_user.user_id,
        f"Created quote version V{new_version_number} for project {project.name}"
    )
    
    return QuoteVersionResponse(
        id=str(new_version.id),
        version=new_version.version,
        total=float(new_version.total),
        pdf_path=new_version.pdf_path,
        created_at=new_version.created_at.isoformat(),
        lines=lines_response
    )


@router.put("/{quote_id}/status", response_model=QuoteResponse)
async def update_quote_status(
    quote_id: UUID,
    status: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Met à jour le statut du devis (draft, sent, negotiation, accepted, refused)."""
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Devis non trouvé")
    
    # Vérifier l'accès
    project = db.query(Project).filter(Project.id == quote.project_id).first()
    check_company_access(str(project.company_id), current_user.company_id)
    
    # Valider le statut
    valid_statuses = ["draft", "sent", "negotiation", "accepted", "refused"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Use one of: {', '.join(valid_statuses)}"
        )
    
    quote.status = status
    db.commit()
    db.refresh(quote)
    
    # Log audit
    log_audit(
        db,
        current_user.company_id,
        current_user.user_id,
        f"Updated quote status to {status}"
    )
    
    # Return full quote with versions
    return await get_quote_by_project(quote.project_id, current_user, db)
