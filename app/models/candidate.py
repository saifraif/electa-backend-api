import uuid
import enum
from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class ProfileStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    # party_id will be added later when we create the PoliticalParties model
    
    profile_photo_url = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    vision_statement = Column(String, nullable=True)
    
    status = Column(Enum(ProfileStatus), nullable=False, default=ProfileStatus.DRAFT)
    # The claimed_by_candidate_id field will be implemented in a future phase
    
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)