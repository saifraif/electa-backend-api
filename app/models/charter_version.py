import uuid
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class CharterVersion(Base):
    __tablename__ = "charterversions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_name = Column(String, nullable=False)
    effective_date = Column(DateTime)
    review_deadline = Column(DateTime)
    is_active = Column(Boolean, default=True)