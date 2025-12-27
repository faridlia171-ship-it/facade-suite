from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from app.db.database import get_db
from app.db.models import Profile, Company, Subscription
from app.security.auth import get_current_user, AuthUser

router = APIRouter()


class OnboardingRequest(BaseModel):
    company_name: str
    accepted_terms: bool


@router.post("/onboarding")
def onboarding(
    payload: OnboardingRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not payload.accepted_terms:
        raise HTTPException(status_code=400, detail="Conditions non acceptées")

    user_id = UUID(current_user.user_id)

    existing = db.query(Profile).filter(Profile.id == user_id).first()
    if existing:
        return {"status": "already_onboarded"}

    company = Company(name=payload.company_name)
    db.add(company)
    db.flush()

    profile = Profile(
        id=user_id,
        company_id=company.id,
        role="OWNER",
        created_at=datetime.utcnow(),
    )
    db.add(profile)

    subscription = Subscription(
        company_id=company.id,
        plan_id="TRIAL",
        status="active",
        started_at=datetime.utcnow(),
    )
    db.add(subscription)

    db.commit()

    return {
        "status": "ok",
        "company_id": str(company.id),
        "user_id": str(user_id),
    }


@router.get("/me")
def me(
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = (
        db.query(Profile)
        .filter(Profile.id == UUID(current_user.user_id))
        .first()
    )

    if not profile:
        raise HTTPException(status_code=404, detail="Profil introuvable")

    return {
        "user_id": str(profile.id),
        "company_id": str(profile.company_id),
        "role": profile.role,
    }
