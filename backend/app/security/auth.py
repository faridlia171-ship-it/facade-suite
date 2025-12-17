"""Authentification et autorisation JWT Supabase."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import Optional
import httpx

from ..settings import settings
from ..db.database import get_db
from ..db.models import Profile, Company

security = HTTPBearer()


class AuthUser:
    """Utilisateur authentifié."""
    def __init__(self, user_id: str, email: str, company_id: str, role: str):
        self.user_id = user_id
        self.email = email
        self.company_id = company_id
        self.role = role
    
    def is_owner(self) -> bool:
        """Vérifie si l'utilisateur est OWNER."""
        return self.role == "OWNER"


async def verify_supabase_token(token: str) -> dict:
    """Vérifie et décode un JWT Supabase."""
    try:
        # Vérification du JWT avec le secret Supabase
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=[settings.ALGORITHM],
            audience="authenticated"
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token invalide: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> AuthUser:
    """Récupère l'utilisateur courant depuis le token JWT."""
    token = credentials.credentials
    payload = await verify_supabase_token(token)
    
    user_id = payload.get("sub")
    email = payload.get("email")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide: user_id manquant"
        )
    
    # Récupérer le profil utilisateur
    profile = db.query(Profile).filter(Profile.id == user_id).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil utilisateur non trouvé"
        )
    
    return AuthUser(
        user_id=user_id,
        email=email,
        company_id=str(profile.company_id),
        role=profile.role
    )


async def require_owner(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
    """Vérifie que l'utilisateur est OWNER."""
    if not current_user.is_owner():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux propriétaires"
        )
    return current_user


def check_company_access(resource_company_id: str, user_company_id: str):
    """Vérifie l'accès multi-tenant."""
    if resource_company_id != user_company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé: ressource d'une autre entreprise"
        )
