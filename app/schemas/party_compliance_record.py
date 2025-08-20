import uuid
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.party_compliance_record import ComplianceStatus

class PartyComplianceRecordBase(BaseModel):
    party_id: uuid.UUID
    clause_id: uuid.UUID
    evidence_id: uuid.UUID
    compliance_status: ComplianceStatus
    public_notes: Optional[str] = None

class PartyComplianceRecordCreate(PartyComplianceRecordBase):
    pass

class PartyComplianceRecord(PartyComplianceRecordBase):
    id: uuid.UUID
    last_assessed_at: Optional[datetime] = None
    assessed_by_admin_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True