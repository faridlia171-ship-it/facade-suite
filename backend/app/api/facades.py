"""Routes de gestion des façades."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from ..db.database import get_db
from ..db.models import Facade, Project
from ..security.auth import get_current_user, AuthUser, check_company_access

router = APIRouter()


class FacadeCreate(BaseModel):
    """Création d'une façade."""
    project_id: str
    code: str  # A, B, C, D


class FacadeDuplicate(BaseModel):
    """Duplication d'une façade."""
    source_facade_id: str
    target_code: str


class FacadeResponse(BaseModel):
    """Réponse façade."""
    id: str
    project_id: str
    code: str
    duplicated_from: Optional[str]


@router.post("", response_model=FacadeResponse)
async def create_facade(
    facade: FacadeCreate,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crée une nouvelle façade."""
    # Vérifier que le projet appartient bien à l'entreprise
    project = db.query(Project).filter(Project.id == facade.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Chantier non trouvé")
    
    check_company_access(str(project.company_id), current_user.company_id)
    
    new_facade = Facade(
        project_id=facade.project_id,
        code=facade.code
    )
    db.add(new_facade)
    db.commit()
    db.refresh(new_facade)
    
    return FacadeResponse(
        id=str(new_facade.id),
        project_id=str(new_facade.project_id),
        code=new_facade.code,
        duplicated_from=str(new_facade.duplicated_from) if new_facade.duplicated_from else None
    )


@router.post("/duplicate", response_model=FacadeResponse)
async def duplicate_facade(
    request: FacadeDuplicate,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Duplique une façade (opposée)."""
    source = db.query(Facade).filter(Facade.id == request.source_facade_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Façade source non trouvée")
    
    # Vérifier accès
    project = db.query(Project).filter(Project.id == source.project_id).first()
    check_company_access(str(project.company_id), current_user.company_id)
    
    # Créer la duplication
    duplicated = Facade(
        project_id=source.project_id,
        code=request.target_code,
        duplicated_from=source.id
    )
    db.add(duplicated)
    db.commit()
    db.refresh(duplicated)
    
    return FacadeResponse(
        id=str(duplicated.id),
        project_id=str(duplicated.project_id),
        code=duplicated.code,
        duplicated_from=str(duplicated.duplicated_from)
    )


@router.get("/project/{project_id}", response_model=list[FacadeResponse])
async def list_facades(
    project_id: UUID,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Liste les façades d'un chantier."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Chantier non trouvé")
    
    check_company_access(str(project.company_id), current_user.company_id)
    
    facades = db.query(Facade).filter(Facade.project_id == project_id).all()
    
    return [
        FacadeResponse(
            id=str(f.id),
            project_id=str(f.project_id),
            code=f.code,
            duplicated_from=str(f.duplicated_from) if f.duplicated_from else None
        )
        for f in facades
    ]
