import uuid
import enum
from sqlalchemy import Column, String, Enum as SAEnum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class ComplianceStatus(str, enum.Enum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    PARTIALLY_COMPLIANT = "PARTIALLY_COMPLIANT"
    UNDER_REVIEW = "UNDER_REVIEW"
    NOT_APPLICABLE = "NOT_APPLICABLE"

class PartyComplianceRecord(Base):
    __tablename__ = "partycompliancerecords"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # party_id will be a FK to a PoliticalParties table we will create later
    party_id = Column(UUID(as_uuid=True), index=True) 
    clause_id = Column(UUID(as_uuid=True), ForeignKey("charterclauses.id"))
    evidence_id = Column(UUID(as_uuid=True), ForeignKey("complianceevidence.id"))
    compliance_status = Column(SAEnum(ComplianceStatus), nullable=False)
    public_notes = Column(String)
    last_assessed_at = Column(DateTime)
    next_review_due_at = Column(DateTime)
    assessed_by_admin_id = Column(UUID(as_uuid=True), ForeignKey("admins.id"))