"""Routes de gestion des photos - Upload Supabase Storage."""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
import httpx
from datetime import datetime, timedelta

from ..db.database import get_db
from ..db.models import Photo, Facade, Project
from ..security.auth import get_current_user, AuthUser, check_company_access
from ..settings import settings

router = APIRouter()


class PhotoResponse(BaseModel):
    """Réponse photo."""
    id: str
    facade_id: str
    storage_path: str
    signed_url: str
    quality: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


async def get_supabase_signed_url(storage_path: str, expires_in: int = 3600) -> str:
    """Génère une URL signée Supabase Storage."""
    # URL de l'API Supabase Storage pour signed URLs
    url = f"{settings.SUPABASE_URL}/storage/v1/object/sign/{settings.STORAGE_BUCKET}/{storage_path}"
    
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
        "apikey": settings.SUPABASE_SERVICE_KEY
    }
    
    payload = {"expiresIn": expires_in}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate signed URL"
            )
        
        data = response.json()
        signed_path = data.get("signedURL")
        
        if not signed_path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No signed URL returned"
            )
        
        # Construct full URL
        return f"{settings.SUPABASE_URL}/storage/v1{signed_path}"


@router.post("/{facade_id}/upload", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    facade_id: UUID,
    file: UploadFile = File(...),
    quality: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload une photo de façade sur Supabase Storage."""
    # Vérifier que la façade existe et appartient à la bonne société
    facade = db.query(Facade).filter(Facade.id == facade_id).first()
    if not facade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Façade non trouvée")
    
    project = db.query(Project).filter(Project.id == facade.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chantier non trouvé")
    
    check_company_access(str(project.company_id), current_user.company_id)
    
    # Valider le type de fichier
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type de fichier non supporté. Utilisez: {', '.join(allowed_types)}"
        )
    
    # Générer le chemin de stockage
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    storage_path = f"{current_user.company_id}/{project.id}/{facade_id}/{timestamp}.{file_extension}"
    
    # Upload sur Supabase Storage
    upload_url = f"{settings.SUPABASE_URL}/storage/v1/object/{settings.STORAGE_BUCKET}/{storage_path}"
    
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
        "apikey": settings.SUPABASE_SERVICE_KEY
    }
    
    file_content = await file.read()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            upload_url,
            content=file_content,
            headers={**headers, "Content-Type": file.content_type}
        )
        
        if response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {response.text}"
            )
    
    # Créer l'enregistrement en base
    photo = Photo(
        facade_id=facade_id,
        storage_path=storage_path,
        quality=quality
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    
    # Générer l'URL signée
    signed_url = await get_supabase_signed_url(storage_path)
    
    return PhotoResponse(
        id=str(photo.id),
        facade_id=str(photo.facade_id),
        storage_path=photo.storage_path,
        signed_url=signed_url,
        quality=photo.quality,
        created_at=photo.created_at.isoformat()
    )


@router.get("/facade/{facade_id}", response_model=List[PhotoResponse])
async def list_photos_by_facade(
    facade_id: UUID,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Liste toutes les photos d'une façade."""
    # Vérifier l'accès
    facade = db.query(Facade).filter(Facade.id == facade_id).first()
    if not facade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Façade non trouvée")
    
    project = db.query(Project).filter(Project.id == facade.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chantier non trouvé")
    
    check_company_access(str(project.company_id), current_user.company_id)
    
    # Récupérer les photos
    photos = db.query(Photo).filter(Photo.facade_id == facade_id).all()
    
    result = []
    for photo in photos:
        signed_url = await get_supabase_signed_url(photo.storage_path)
        result.append(
            PhotoResponse(
                id=str(photo.id),
                facade_id=str(photo.facade_id),
                storage_path=photo.storage_path,
                signed_url=signed_url,
                quality=photo.quality,
                created_at=photo.created_at.isoformat()
            )
        )
    
    return result


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    photo_id: UUID,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprime une photo."""
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo non trouvée")
    
    # Vérifier l'accès
    facade = db.query(Facade).filter(Facade.id == photo.facade_id).first()
    project = db.query(Project).filter(Project.id == facade.project_id).first()
    
    check_company_access(str(project.company_id), current_user.company_id)
    
    # Supprimer de Supabase Storage
    delete_url = f"{settings.SUPABASE_URL}/storage/v1/object/{settings.STORAGE_BUCKET}/{photo.storage_path}"
    
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
        "apikey": settings.SUPABASE_SERVICE_KEY
    }
    
    async with httpx.AsyncClient() as client:
        await client.delete(delete_url, headers=headers)
    
    # Supprimer de la base
    db.delete(photo)
    db.commit()
    
    return None
