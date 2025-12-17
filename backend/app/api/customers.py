"""Routes de gestion des clients - CRUD complet."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

from ..db.database import get_db
from ..db.models import Customer, AuditLog
from ..security.auth import get_current_user, AuthUser, check_company_access

router = APIRouter()


class CustomerCreate(BaseModel):
    """Création d'un client."""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None


class CustomerUpdate(BaseModel):
    """Mise à jour d'un client."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None


class CustomerResponse(BaseModel):
    """Réponse client."""
    id: str
    company_id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    city: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


def log_audit(db: Session, company_id: str, user_id: str, action: str):
    """Enregistre une action dans les logs d'audit."""
    audit_log = AuditLog(
        company_id=company_id,
        user_id=user_id,
        action=action
    )
    db.add(audit_log)
    db.commit()


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer: CustomerCreate,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crée un nouveau client."""
    new_customer = Customer(
        company_id=current_user.company_id,
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        city=customer.city
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    
    # Log audit
    log_audit(db, current_user.company_id, current_user.user_id, f"Created customer: {customer.name}")
    
    return CustomerResponse(
        id=str(new_customer.id),
        company_id=str(new_customer.company_id),
        name=new_customer.name or "",
        email=new_customer.email,
        phone=new_customer.phone,
        city=new_customer.city,
        created_at=new_customer.created_at.isoformat()
    )


@router.get("", response_model=List[CustomerResponse])
async def list_customers(
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Liste tous les clients de l'entreprise."""
    customers = db.query(Customer).filter(
        Customer.company_id == current_user.company_id
    ).all()
    
    return [
        CustomerResponse(
            id=str(c.id),
            company_id=str(c.company_id),
            name=c.name or "",
            email=c.email,
            phone=c.phone,
            city=c.city,
            created_at=c.created_at.isoformat()
        )
        for c in customers
    ]


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: UUID,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère un client par ID."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client non trouvé")
    
    check_company_access(str(customer.company_id), current_user.company_id)
    
    return CustomerResponse(
        id=str(customer.id),
        company_id=str(customer.company_id),
        name=customer.name or "",
        email=customer.email,
        phone=customer.phone,
        city=customer.city,
        created_at=customer.created_at.isoformat()
    )


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: UUID,
    customer_data: CustomerUpdate,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Met à jour un client."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client non trouvé")
    
    check_company_access(str(customer.company_id), current_user.company_id)
    
    if customer_data.name is not None:
        customer.name = customer_data.name
    if customer_data.email is not None:
        customer.email = customer_data.email
    if customer_data.phone is not None:
        customer.phone = customer_data.phone
    if customer_data.city is not None:
        customer.city = customer_data.city
    
    db.commit()
    db.refresh(customer)
    
    # Log audit
    log_audit(db, current_user.company_id, current_user.user_id, f"Updated customer: {customer.name}")
    
    return CustomerResponse(
        id=str(customer.id),
        company_id=str(customer.company_id),
        name=customer.name or "",
        email=customer.email,
        phone=customer.phone,
        city=customer.city,
        created_at=customer.created_at.isoformat()
    )


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: UUID,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprime un client."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client non trouvé")
    
    check_company_access(str(customer.company_id), current_user.company_id)
    
    customer_name = customer.name
    db.delete(customer)
    db.commit()
    
    # Log audit
    log_audit(db, current_user.company_id, current_user.user_id, f"Deleted customer: {customer_name}")
    
    return None
