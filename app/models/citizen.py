# D:\Application\Electa\app\electa-backend-api\app\models\citizen.py

import uuid
import enum
from sqlalchemy import Column, String, Enum, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base


class VerificationStatus(str, enum.Enum):
    MOBILE_VERIFIED = "MOBILE_VERIFIED"
    PENDING_NID = "PENDING_NID"
    NID_VERIFIED = "NID_VERIFIED"
    REJECTED_NID = "REJECTED_NID"


class CitizenRole(str, enum.Enum):
    CITIZEN = "CITIZEN"
    TRUSTED_CONTRIBUTOR = "TRUSTED_CONTRIBUTOR"


class Citizen(Base):
    """
    SQLAlchemy model for citizens table.
    """
    __tablename__ = "citizens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mobile_number = Column(String(20), unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    verification_status = Column(
        Enum(VerificationStatus, name="verificationstatus"),
        nullable=False,
        default=VerificationStatus.MOBILE_VERIFIED,
    )
    role = Column(
        Enum(CitizenRole, name="citizenrole"),
        nullable=False,
        default=CitizenRole.CITIZEN,
    )

    rejection_reason = Column(Text, nullable=True)
    last_login_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)
