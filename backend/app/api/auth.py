"""Routes d'authentification."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from ..db.database import get_db
from ..db.models import Profile, Company, Subscription
from ..security.auth import get_current_user, AuthUser

router = APIRouter()


class OnboardingRequest(BaseModel):
    """Demande d'onboarding."""
    company_name: str
    accepted_terms: bool
    user_id: str


class ProfileResponse(BaseModel):
    """Réponse profil."""
    user_id: str
    company_id: str
    company_name: str
    role: str
    plan_id: str | None
    created_at: datetime


@router.post("/onboarding")
async def onboarding(
    request: OnboardingRequest,
    db: Session = Depends(get_db)
):
    """Onboarding: création entreprise + profil."""
    if not request.accepted_terms:
        raise HTTPException(
            status_code=400,
            detail="Vous devez accepter les conditions d'utilisation"
        )
    
    # Vérifier si le profil existe déjà
    existing = db.query(Profile).filter(Profile.id == request.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profil déjà existant")
    
    # Créer l'entreprise
    company = Company(name=request.company_name)
    db.add(company)
    db.flush()
    
    # Créer le profil OWNER
    profile = Profile(
        id=request.user_id,
        company_id=company.id,
        role="OWNER"
    )
    db.add(profile)
    
    # Créer l'abonnement TRIAL
    subscription = Subscription(
        company_id=company.id,
        plan_id="TRIAL",
        status="active",
        started_at=datetime.utcnow()
    )
    db.add(subscription)
    
    db.commit()
    
    return {
        "message": "Onboarding réussi",
        "company_id": str(company.id),
        "profile_id": str(profile.id)
    }


@router.get("/me", response_model=ProfileResponse)
async def get_me(
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère le profil de l'utilisateur courant."""
    profile = db.query(Profile).filter(Profile.id == current_user.user_id).first()
    company = db.query(Company).filter(Company.id == profile.company_id).first()
    subscription = db.query(Subscription).filter(
        Subscription.company_id == profile.company_id
    ).first()
    
    return ProfileResponse(
        user_id=str(profile.id),
        company_id=str(profile.company_id),
        company_name=company.name,
        role=profile.role,
        plan_id=subscription.plan_id if subscription else None,
        created_at=profile.created_at
    )
