"""Routes d'authentification et onboarding."""

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
    db: Session = Depends(get_db),
):
    """Crée le profil + company pour un utilisateur Supabase."""
    if not request.accepted_terms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conditions non acceptées"
        )

    # 🔒 Sécurité : on utilise TOUJOURS l'user du JWT
    user_id = current_user.user_id

    # Vérifier si le profil existe déjà
    existing = db.query(Profile).filter(Profile.id == user_id).first()
    if existing:
        return {
            "message": "Profil déjà existant",
            "company_id": str(existing.company_id),
            "profile_id": str(existing.id),
        }

    try:
        # Créer la company
        company = Company(name=request.company_name)
        db.add(company)
        db.flush()

        # Créer le profil OWNER
        profile = Profile(
            id=user_id,
            company_id=company.id,
            role="OWNER",
            created_at=datetime.utcnow(),
        )
        db.add(profile)

        # Créer abonnement TRIAL
        subscription = Subscription(
            company_id=company.id,
            plan_id="TRIAL",
            status="active",
            started_at=datetime.utcnow(),
        )
        db.add(subscription)

        db.commit()

        return {
            "message": "Onboarding réussi",
            "company_id": str(company.id),
            "profile_id": str(profile.id),
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur base de données onboarding: {str(e)}"
        )
