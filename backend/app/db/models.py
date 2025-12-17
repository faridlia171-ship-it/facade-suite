"""Modèles SQLAlchemy pour Facade Suite."""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from .database import Base


class Company(Base):
    """Entreprise cliente (tenant)."""
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    profiles = relationship("Profile", back_populates="company")
    customers = relationship("Customer", back_populates="company")
    projects = relationship("Project", back_populates="company")
    audit_logs = relationship("AuditLog", back_populates="company")


class Profile(Base):
    """Profil utilisateur lié à auth.users."""
    __tablename__ = "profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True)  # Référence auth.users
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint("role IN ('OWNER', 'USER')", name="check_role"),
    )
    
    # Relations
    company = relationship("Company", back_populates="profiles")
    audit_logs = relationship("AuditLog", back_populates="user")


class Customer(Base):
    """Client du chantier."""
    __tablename__ = "customers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    city = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    company = relationship("Company", back_populates="customers")
    projects = relationship("Project", back_populates="customer")


class Project(Base):
    """Chantier."""
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    name = Column(String)
    status = Column(String, default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    company = relationship("Company", back_populates="projects")
    customer = relationship("Customer", back_populates="projects")
    facades = relationship("Facade", back_populates="project")
    quotes = relationship("Quote", back_populates="project")
    metrage_refs = relationship("MetrageRef", back_populates="project")


class Facade(Base):
    """Façade d'un chantier."""
    __tablename__ = "facades"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    code = Column(String)  # A, B, C, D
    duplicated_from = Column(UUID(as_uuid=True), ForeignKey("facades.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    project = relationship("Project", back_populates="facades")
    photos = relationship("Photo", back_populates="facade")


class Photo(Base):
    """Photo de façade."""
    __tablename__ = "photos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facade_id = Column(UUID(as_uuid=True), ForeignKey("facades.id"), nullable=False)
    storage_path = Column(String, nullable=False)
    quality = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint("quality IN ('green', 'orange', 'red')", name="check_quality"),
    )
    
    # Relations
    facade = relationship("Facade", back_populates="photos")


class MetrageRef(Base):
    """Référence de métrage."""
    __tablename__ = "metrage_refs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    type = Column(String)  # agglo, custom
    width_cm = Column(Numeric)
    height_cm = Column(Numeric)
    
    # Relations
    project = relationship("Project", back_populates="metrage_refs")


class Quote(Base):
    """Devis."""
    __tablename__ = "quotes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    status = Column(String)
    current_version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    project = relationship("Project", back_populates="quotes")
    versions = relationship("QuoteVersion", back_populates="quote")


class QuoteVersion(Base):
    """Version d'un devis."""
    __tablename__ = "quote_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quote_id = Column(UUID(as_uuid=True), ForeignKey("quotes.id"), nullable=False)
    version = Column(Integer, nullable=False)
    total = Column(Numeric)
    pdf_path = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    quote = relationship("Quote", back_populates="versions")
    lines = relationship("QuoteLine", back_populates="quote_version")


class QuoteLine(Base):
    """Ligne de devis."""
    __tablename__ = "quote_lines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quote_version_id = Column(UUID(as_uuid=True), ForeignKey("quote_versions.id"), nullable=False)
    label = Column(String)
    quantity = Column(Numeric)
    unit_price = Column(Numeric)
    total = Column(Numeric)
    
    # Relations
    quote_version = relationship("QuoteVersion", back_populates="lines")


class Plan(Base):
    """Plan d'abonnement."""
    __tablename__ = "plans"
    
    id = Column(String, primary_key=True)
    max_projects = Column(Integer)
    max_users = Column(Integer)
    
    # Relations
    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    """Abonnement d'une entreprise."""
    __tablename__ = "subscriptions"
    
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), primary_key=True)
    plan_id = Column(String, ForeignKey("plans.id"))
    status = Column(String)
    started_at = Column(DateTime(timezone=True))
    
    # Relations
    plan = relationship("Plan", back_populates="subscriptions")


class AuditLog(Base):
    """Log d'audit."""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    action = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    company = relationship("Company", back_populates="audit_logs")
    user = relationship("Profile", back_populates="audit_logs")
