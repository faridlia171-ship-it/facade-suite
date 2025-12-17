"""API endpoints pour les sociétés."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from uuid import UUID

from ..db.database import get_db
from ..db.models import Company, Subscription
from ..security.auth import get_current_user, require_owner, AuthUser

router = APIRouter()


class CompanyResponse(BaseModel):
    id: str
    name: str
    created_at: str

    class Config:
        from_attributes = True


class CompanyUpdate(BaseModel):
    name: str


@router.get("/me", response_model=CompanyResponse)
async def get_my_company(
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère les informations de la société de l'utilisateur."""
    company = db.query(Company).filter(
        Company.id == current_user.company_id
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return CompanyResponse(
        id=str(company.id),
        name=company.name,
        created_at=company.created_at.isoformat()
    )


@router.put("/me", response_model=CompanyResponse)
async def update_my_company(
    company_data: CompanyUpdate,
    current_user: AuthUser = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """Met à jour les informations de la société (OWNER uniquement)."""
    company = db.query(Company).filter(
        Company.id == current_user.company_id
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    company.name = company_data.name
    db.commit()
    db.refresh(company)
    
    return CompanyResponse(
        id=str(company.id),
        name=company.name,
        created_at=company.created_at.isoformat()
    )


@router.get("/subscription")
async def get_subscription(
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère l'abonnement de la société."""
    subscription = db.query(Subscription).filter(
        Subscription.company_id == current_user.company_id
    ).first()
    
    if not subscription:
        return {
            "plan_id": "TRIAL",
            "status": "trial",
            "message": "Default trial plan"
        }
    
    return {
        "plan_id": subscription.plan_id,
        "status": subscription.status,
        "started_at": subscription.started_at.isoformat() if subscription.started_at else None
    }
