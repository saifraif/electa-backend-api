import uuid
from pydantic import BaseModel, Field # Import Field
from typing import Optional

# Base properties for an Ideology
class IdeologyBase(BaseModel):
    # Add a validator to ensure the title is not an empty string
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

# Properties to receive via API on creation
class IdeologyCreate(IdeologyBase):
    pass

# Properties to return to client
class Ideology(IdeologyBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

# Schema for a citizen updating their selected ideologies
class CitizenIdeologyUpdate(BaseModel):
    ideology_ids: list[uuid.UUID]