from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from app import schemas, models
from app.db.session import get_db
from app.api.v1.endpoints.admin import get_current_admin

router = APIRouter()

@router.post("/compliance/evidence", response_model=schemas.ComplianceEvidence, status_code=status.HTTP_201_CREATED)
def create_new_evidence(
    *,
    db: Session = Depends(get_db),
    evidence_in: schemas.ComplianceEvidenceCreate,
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    Create a new evidence record.
    (In a real app, this would be tied to a file upload process).
    """
    db_evidence = models.ComplianceEvidence(
        **evidence_in.dict(),
        uploaded_at=datetime.utcnow(),
        uploaded_by_admin_id=current_admin.id
    )
    db.add(db_evidence)
    db.commit()
    db.refresh(db_evidence)
    return db_evidence

@router.post("/compliance/records", response_model=schemas.PartyComplianceRecord, status_code=status.HTTP_201_CREATED)
def create_compliance_record(
    *,
    db: Session = Depends(get_db),
    record_in: schemas.PartyComplianceRecordCreate,
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    Create a new party compliance record.
    """
    db_record = models.PartyComplianceRecord(
        **record_in.dict(),
        last_assessed_at=datetime.utcnow(),
        assessed_by_admin_id=current_admin.id
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record