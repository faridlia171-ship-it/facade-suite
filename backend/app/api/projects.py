"""Routes de gestion des chantiers - CRUD complet."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

from ..db.database import get_db
from ..db.models import Project, Customer, Quote, AuditLog
from ..security.auth import get_current_user, AuthUser, check_company_access

router = APIRouter()


class ProjectCreate(BaseModel):
    """Création d'un chantier."""
    customer_id: str
    name: str


class ProjectUpdate(BaseModel):
    """Mise à jour d'un chantier."""
    name: Optional[str] = None
    status: Optional[str] = None


class ProjectResponse(BaseModel):
    """Réponse chantier."""
    id: str
    company_id: str
    customer_id: str
    name: str
    status: str
    created_at: str

    class Config:
        from_attributes = True


def log_audit(db: Session, company_id: str, user_id: str, action: str):
    """Enregistre une action dans les logs d'audit."""
    audit_log = AuditLog(company_id=company_id, user_id=user_id, action=action)
    db.add(audit_log)
    db.commit()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crée un nouveau chantier avec devis automatique."""
    # Vérifier que le client existe et appartient à la bonne société
    customer = db.query(Customer).filter(Customer.id == project.customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client non trouvé")
    
    check_company_access(str(customer.company_id), current_user.company_id)
    
    # Créer le chantier
    new_project = Project(
        company_id=current_user.company_id,
        customer_id=project.customer_id,
        name=project.name,
        status="draft"
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    # Créer le devis automatiquement
    quote = Quote(
        project_id=new_project.id,
        status="draft",
        current_version=1
    )
    db.add(quote)
    db.commit()
    
    # Log audit
    log_audit(db, current_user.company_id, current_user.user_id, f"Created project: {project.name}")
    
    return ProjectResponse(
        id=str(new_project.id),
        company_id=str(new_project.company_id),
        customer_id=str(new_project.customer_id),
        name=new_project.name or "",
        status=new_project.status or "",
        created_at=new_project.created_at.isoformat()
    )


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Liste tous les chantiers de l'entreprise."""
    projects = db.query(Project).filter(
        Project.company_id == current_user.company_id
    ).all()
    
    return [
        ProjectResponse(
            id=str(p.id),
            company_id=str(p.company_id),
            customer_id=str(p.customer_id),
            name=p.name or "",
            status=p.status or "",
            created_at=p.created_at.isoformat()
        )
        for p in projects
    ]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère un chantier par ID."""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chantier non trouvé")
    
    check_company_access(str(project.company_id), current_user.company_id)
    
    return ProjectResponse(
        id=str(project.id),
        company_id=str(project.company_id),
        customer_id=str(project.customer_id),
        name=project.name or "",
        status=project.status or "",
        created_at=project.created_at.isoformat()
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Met à jour un chantier."""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chantier non trouvé")
    
    check_company_access(str(project.company_id), current_user.company_id)
    
    if project_data.name is not None:
        project.name = project_data.name
    if project_data.status is not None:
        project.status = project_data.status
    
    db.commit()
    db.refresh(project)
    
    # Log audit
    log_audit(db, current_user.company_id, current_user.user_id, f"Updated project: {project.name}")
    
    return ProjectResponse(
        id=str(project.id),
        company_id=str(project.company_id),
        customer_id=str(project.customer_id),
        name=project.name or "",
        status=project.status or "",
        created_at=project.created_at.isoformat()
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprime un chantier."""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chantier non trouvé")
    
    check_company_access(str(project.company_id), current_user.company_id)
    
    project_name = project.name
    db.delete(project)
    db.commit()
    
    # Log audit
    log_audit(db, current_user.company_id, current_user.user_id, f"Deleted project: {project_name}")
    
    return None
