import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class ComplianceEvidence(Base):
    __tablename__ = "complianceevidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_url = Column(String, nullable=False)
    description = Column(String)
    uploaded_at = Column(DateTime)
    uploaded_by_admin_id = Column(UUID(as_uuid=True), ForeignKey("admins.id"))