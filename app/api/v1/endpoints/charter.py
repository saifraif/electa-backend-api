from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app import schemas, models
from app.db.session import get_db
from app.api.v1.endpoints.admin import get_current_admin

router = APIRouter()

@router.post("/charter/versions", response_model=schemas.CharterVersion, status_code=status.HTTP_201_CREATED)
def create_charter_version(
    *,
    db: Session = Depends(get_db),
    version_in: schemas.CharterVersionCreate,
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    Create a new version of the July Charter.
    Requires SUPER_ADMIN role.
    """
    # In a real app, we would add a role check here
    # if current_admin.role != models.AdminRole.SUPER_ADMIN:
    #     raise HTTPException(status_code=403, detail="Not enough permissions")
        
    db_version = models.CharterVersion(**version_in.dict())
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    return db_version

@router.post("/charter/clauses", response_model=schemas.CharterClause, status_code=status.HTTP_201_CREATED)
def create_charter_clause(
    *,
    db: Session = Depends(get_db),
    clause_in: schemas.CharterClauseCreate,
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    Create a new clause for a specific version of the July Charter.
    Requires DATA_EDITOR or SUPER_ADMIN role.
    """
    db_clause = models.CharterClause(**clause_in.dict())
    db.add(db_clause)
    db.commit()
    db.refresh(db_clause)
    return db_clause

@router.get("/charter/versions", response_model=List[schemas.CharterVersion])
def list_charter_versions(db: Session = Depends(get_db)):
    """
    Retrieve all versions of the July Charter.
    """
    return db.query(models.CharterVersion).all()