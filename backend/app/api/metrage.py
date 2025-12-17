"""Routes de métrage photo."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

from ..db.database import get_db
from ..db.models import MetrageRef, Project, Photo
from ..security.auth import get_current_user, AuthUser, check_company_access

router = APIRouter()


class MetrageRefCreate(BaseModel):
    """Création d'une référence de métrage."""
    project_id: str
    type: str  # agglo, custom
    width_cm: Optional[float] = None
    height_cm: Optional[float] = None


class MetrageRefResponse(BaseModel):
    """Réponse référence métrage."""
    id: str
    project_id: str
    type: str
    width_cm: Optional[float]
    height_cm: Optional[float]


class MetrageCalculation(BaseModel):
    """Calcul de métrage."""
    photo_id: str
    ref_width_px: int
    ref_height_px: int
    facade_width_px: int
    facade_height_px: int
    openings: Optional[List[dict]] = []


class MetrageResult(BaseModel):
    """Résultat de métrage."""
    surface_m2: float
    width_m: float
    height_m: float
    openings_m2: float
    net_surface_m2: float


@router.post("/ref", response_model=MetrageRefResponse)
async def create_metrage_ref(
    ref: MetrageRefCreate,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crée une référence de métrage."""
    project = db.query(Project).filter(Project.id == ref.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Chantier non trouvé")
    
    check_company_access(str(project.company_id), current_user.company_id)
    
    # Valeurs par défaut pour agglo 20x50
    if ref.type == "agglo":
        ref.width_cm = 50.0
        ref.height_cm = 20.0
    
    new_ref = MetrageRef(
        project_id=ref.project_id,
        type=ref.type,
        width_cm=ref.width_cm,
        height_cm=ref.height_cm
    )
    db.add(new_ref)
    db.commit()
    db.refresh(new_ref)
    
    return MetrageRefResponse(
        id=str(new_ref.id),
        project_id=str(new_ref.project_id),
        type=new_ref.type,
        width_cm=float(new_ref.width_cm) if new_ref.width_cm else None,
        height_cm=float(new_ref.height_cm) if new_ref.height_cm else None
    )


@router.post("/calculate", response_model=MetrageResult)
async def calculate_metrage(
    calc: MetrageCalculation,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calcule le métrage d'une façade."""
    # Vérifier que la photo existe et appartient à l'entreprise
    photo = db.query(Photo).filter(Photo.id == calc.photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo non trouvée")
    
    # Vérifier accès (via façade -> projet)
    from ..db.models import Facade
    facade = db.query(Facade).filter(Facade.id == photo.facade_id).first()
    project = db.query(Project).filter(Project.id == facade.project_id).first()
    check_company_access(str(project.company_id), current_user.company_id)
    
    # Récupérer la référence de métrage
    metrage_ref = db.query(MetrageRef).filter(
        MetrageRef.project_id == project.id
    ).first()
    
    if not metrage_ref:
        raise HTTPException(status_code=404, detail="Référence de métrage non trouvée")
    
    # Calcul du ratio pixels/cm
    ref_width_cm = float(metrage_ref.width_cm)
    ref_height_cm = float(metrage_ref.height_cm)
    
    px_per_cm_width = calc.ref_width_px / ref_width_cm
    px_per_cm_height = calc.ref_height_px / ref_height_cm
    
    # Moyenne pour correction perspective simple
    px_per_cm = (px_per_cm_width + px_per_cm_height) / 2
    
    # Dimensions de la façade en mètres
    width_m = (calc.facade_width_px / px_per_cm) / 100
    height_m = (calc.facade_height_px / px_per_cm) / 100
    
    surface_m2 = width_m * height_m
    
    # Calcul des ouvertures
    openings_m2 = 0.0
    if calc.openings:
        for opening in calc.openings:
            opening_width_px = opening.get("width_px", 0)
            opening_height_px = opening.get("height_px", 0)
            opening_width_m = (opening_width_px / px_per_cm) / 100
            opening_height_m = (opening_height_px / px_per_cm) / 100
            openings_m2 += opening_width_m * opening_height_m
    
    net_surface_m2 = surface_m2 - openings_m2
    
    return MetrageResult(
        surface_m2=round(surface_m2, 2),
        width_m=round(width_m, 2),
        height_m=round(height_m, 2),
        openings_m2=round(openings_m2, 2),
        net_surface_m2=round(net_surface_m2, 2)
    )
