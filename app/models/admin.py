import uuid
import enum
from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class AdminRole(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    DATA_EDITOR = "DATA_EDITOR"
    MODERATOR = "MODERATOR"
    VERIFICATION_OFFICER = "VERIFICATION_OFFICER"

class Admin(Base):
    __tablename__ = "admins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    # Note: In a real app, admin passwords would also be hashed.
    # For the MVP, we are simplifying and will manage passwords out of band.
    
    role = Column(Enum(AdminRole), nullable=False, default=AdminRole.DATA_EDITOR)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True)