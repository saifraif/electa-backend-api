import uuid
from pydantic import BaseModel
from typing import Optional

# Properties to receive via API on candidate creation
class CandidateCreate(BaseModel):
    full_name: str
    # party_id will be added in a future task

# Properties to return to the client
class Candidate(CandidateCreate):
    id: uuid.UUID
    status: str

    class Config:
        from_attributes = True