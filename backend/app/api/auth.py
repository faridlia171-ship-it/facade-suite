"""Routes d'authentification et onboarding."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import cast, String
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from ..db.database import get_db
from ..db.models import Profile, Company, Subscription
from ..security.auth import get_current_user, AuthUser

router = APIRouter()


class OnboardingRequest(BaseModel):
    company_name: str
    accepted_terms: bool
    user_id: str


class ProfileResponse(BaseModel):
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
    if not request.accepted_terms:
        raise HTTPException(
            status_code=400,
            detail="Vous devez accepter les conditions d'utilisation"
        )

    # 🔐 Validation UUID (format)
    try:
        UUID(request.user_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="user_id invalide (UUID attendu)"
        )

    # ✅ CAST SQL (TEXT = TEXT)
    try:
        existing = (
            db.query(Profile)
            .filter(cast(Profile.id, String) == request.user_id)
            .first()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur base de données (profile lookup): {str(e)}"
        )

    if existing:
        return {
            "message": "Profil déjà existant",
            "company_id": str(existing.company_id),
            "profile_id": str(existing.id)
        }

    try:
        company = Company(name=request.company_name)
        db.add(company)
        db.flush()

        profile = Profile(
            id=request.user_id,  # TEXT → cohérent avec DB
            company_id=company.id,
            role="OWNER"
        )
        db.add(profile)

        subscription = Subscription(
            company_id=company.id,
            plan_id="TRIAL",
            status="active",
            started_at=datetime.utcnow()
        )
        db.add(subscription)

        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur création onboarding: {str(e)}"
        )

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
    profile = (
        db.query(Profile)
        .filter(cast(Profile.id, String) == current_user.user_id)
        .first()
    )

    if not profile:
        raise HTTPException(status_code=404, detail="Profil utilisateur non trouvé")

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
