import uuid
from sqlalchemy import Column, String, Enum, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base
import enum

class VerificationStatus(str, enum.Enum):
    MOBILE_VERIFIED = "MOBILE_VERIFIED"
    PENDING_NID = "PENDING_NID"
    NID_VERIFIED = "NID_VERIFIED"
    REJECTED_NID = "REJECTED_NID"

class CitizenRole(str, enum.Enum):
    CITIZEN = "CITIZEN"
    TRUSTED_CONTRIBUTOR = "TRUSTED_CONTRIBUTOR"

class Citizen(Base):
    __tablename__ = "citizens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mobile_number = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    
    verification_status = Column(Enum(VerificationStatus), nullable=False, default=VerificationStatus.MOBILE_VERIFIED)
    role = Column(Enum(CitizenRole), nullable=False, default=CitizenRole.CITIZEN)
    
    rejection_reason = Column(Text, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)