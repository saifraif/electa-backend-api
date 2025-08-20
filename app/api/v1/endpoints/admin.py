from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime
from jose import JWTError, jwt
import uuid

from app import schemas, models
from app.db.session import get_db
from app.core.security import create_access_token, oauth2_scheme, SECRET_KEY, ALGORITHM
from app.utils.auditing import log_admin_action
from app.models.audit_log import ActionType

router = APIRouter()

@router.post("/admin/login", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    admin = db.query(models.Admin).filter(models.Admin.email == form_data.username).first()
    if not admin:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    admin.last_login_at = datetime.utcnow()
    db.commit()

    access_token = create_access_token(data={"sub": str(admin.id), "role": admin.role.value})
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_admin(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id: str = payload.get("sub")
        if admin_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    admin = db.query(models.Admin).filter(models.Admin.id == uuid.UUID(admin_id)).first()
    if admin is None:
        raise credentials_exception
    return admin

@router.post("/admin/candidates", response_model=schemas.Candidate, status_code=201)
def create_new_candidate(
    *,
    db: Session = Depends(get_db),
    candidate_in: schemas.CandidateCreate,
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    Create a new candidate profile and log the action.
    """
    candidate = models.Candidate(**candidate_in.dict(), created_at=datetime.utcnow())
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    # Log this action to the audit trail
    log_admin_action(
        db=db,
        admin_id=current_admin.id,
        action=ActionType.CREATE,
        table_name="candidates",
        entity_id=candidate.id
    )

    return candidate