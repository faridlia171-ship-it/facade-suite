"""Routes d'authentification."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from ..db.database import get_db
from ..db.models import Profile, Company, Subscription
from ..security.auth import get_current_user, AuthUser

router = APIRouter()


class OnboardingRequest(BaseModel):
    company_name: str
    accepted_terms: bool


@router.post("/onboarding")
async def onboarding(
    request: OnboardingRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Onboarding sécurisé :
    - l'utilisateur est identifié via le JWT Supabase
    - user_id vient du token, PAS du frontend
    """

    if not request.accepted_terms:
        raise HTTPException(
            status_code=400,
            detail="Vous devez accepter les conditions d'utilisation"
        )

    user_id = current_user.user_id

    # Vérifier si le profil existe déjà
    existing = db.query(Profile).filter(Profile.id == user_id).first()
    if existing:
        return {
            "message": "Onboarding déjà effectué",
            "company_id": str(existing.company_id),
            "profile_id": str(existing.id),
        }

    # Créer l'entreprise
    company = Company(name=request.company_name)
    db.add(company)
    db.flush()

    # Créer le profil OWNER
    profile = Profile(
        id=user_id,
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
        "profile_id": str(profile.id),
    }
