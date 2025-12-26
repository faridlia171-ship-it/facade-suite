"""
Routes d'authentification et d'onboarding.
Compatible SUPABASE AUTH + schéma DB réel.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from ..db.database import get_db
from ..db.models import Profile, Company, Subscription
from ..security.auth import get_current_user, AuthUser

router = APIRouter()


# =========================
# SCHEMAS
# =========================

class OnboardingRequest(BaseModel):
    company_name: str
    accepted_terms: bool


class OnboardingResponse(BaseModel):
    message: str
    company_id: UUID
    profile_id: UUID


class ProfileResponse(BaseModel):
    user_id: UUID
    company_id: UUID
    company_name: str
    role: str
    plan_id: str | None
    created_at: datetime


# =========================
# ROUTES
# =========================

@router.post(
    "/onboarding",
    response_model=OnboardingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def onboarding(
    request: OnboardingRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Crée l'entreprise + profil OWNER + abonnement TRIAL.
    Appelé UNE SEULE FOIS après création Supabase user.
    """

    if not request.accepted_terms:
        raise HTTPException(
            status_code=400,
            detail="Vous devez accepter les conditions d'utilisation",
        )

    # 🔒 Sécurité : empêcher double onboarding
    existing_profile = (
        db.query(Profile)
        .filter(Profile.id == UUID(current_user.user_id))
        .first()
    )

    if existing_profile:
        raise HTTPException(
            status_code=409,
            detail="Onboarding déjà effectué pour cet utilisateur",
        )

    # 1️⃣ Création entreprise
    company = Company(
        name=request.company_name,
    )
    db.add(company)
    db.flush()  # récupère company.id

    # 2️⃣ Création profil OWNER
    profile = Profile(
        id=UUID(current_user.user_id),
        company_id=company.id,
        role="OWNER",
    )
    db.add(profile)

    # 3️⃣ Abonnement TRIAL
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
        "company_id": company.id,
        "profile_id": profile.id,
    }


@router.get(
    "/me",
    response_model=ProfileResponse,
)
async def get_me(
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retourne le profil courant (utilisé par le front).
    """

    profile = (
        db.query(Profile)
        .filter(Profile.id == UUID(current_user.user_id))
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profil non trouvé (onboarding non effectué)",
        )

    company = (
        db.query(Company)
        .filter(Company.id == profile.company_id)
        .first()
    )

    subscription = (
        db.query(Subscription)
        .filter(Subscription.company_id == profile.company_id)
        .first()
    )

    return ProfileResponse(
        user_id=profile.id,
        company_id=profile.company_id,
        company_name=company.name,
        role=profile.role,
        plan_id=subscription.plan_id if subscription else None,
        created_at=profile.created_at,
    )
