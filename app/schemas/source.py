import uuid
from pydantic import BaseModel
from typing import Optional

# We can re-use the enums directly from our database models
from app.models.source import SourceType, CredibilityTier

# Properties to receive on source creation
class SourceCreate(BaseModel):
    source_reference: str
    source_type: SourceType
    description: Optional[str] = None
    credibility_tier: CredibilityTier

# Properties to return to client
class Source(SourceCreate):
    id: uuid.UUID
    uploaded_by_admin_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True