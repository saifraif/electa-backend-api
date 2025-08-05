import uuid
import enum
from sqlalchemy import Column, String, Enum, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base_class import Base

class ActionType(str, enum.Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAIL = "LOGIN_FAIL"

class AuditLog(Base):
    __tablename__ = "auditlogs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), nullable=True) # FK to Admins
    citizen_id = Column(UUID(as_uuid=True), nullable=True) # FK to Citizens
    action = Column(Enum(ActionType), nullable=False)
    table_name = Column(String, nullable=True)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    changes = Column(JSONB, nullable=True)
    timestamp = Column(DateTime, nullable=False)