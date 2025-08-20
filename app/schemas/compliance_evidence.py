import uuid
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ComplianceEvidenceBase(BaseModel):
    file_url: str
    description: Optional[str] = None

class ComplianceEvidenceCreate(ComplianceEvidenceBase):
    pass

class ComplianceEvidence(ComplianceEvidenceBase):
    id: uuid.UUID
    uploaded_at: Optional[datetime] = None
    uploaded_by_admin_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True