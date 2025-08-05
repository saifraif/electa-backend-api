import uuid
import enum
from sqlalchemy import Column, String, Enum as SAEnum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class SourceType(str, enum.Enum):
    URL = "URL"
    PDF = "PDF"
    IMAGE = "IMAGE"

class CredibilityTier(str, enum.Enum):
    TIER_1_GOVERNMENT = "TIER_1_GOVERNMENT"
    TIER_2_NEWS_MEDIA = "TIER_2_NEWS_MEDIA"
    TIER_3_EXPERT = "TIER_3_EXPERT"

class Source(Base):
    __tablename__ = "sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_reference = Column(String, nullable=False)
    source_type = Column(SAEnum(SourceType), nullable=False)
    description = Column(String, nullable=True)
    external_publisher_name = Column(String, nullable=True)
    credibility_tier = Column(SAEnum(CredibilityTier), nullable=False)
    uploaded_by_admin_id = Column(UUID(as_uuid=True), ForeignKey("admins.id"), nullable=True)
    created_at = Column(DateTime, nullable=True)