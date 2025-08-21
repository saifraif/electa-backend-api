from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.security import (
    create_access_token,
    oauth2_scheme,
    SECRET_KEY,
    ALGORITHM,
)
from app.db.session import get_db
from app.models.audit_log import ActionType
from app.utils.auditing import log_admin_action

router = APIRouter()


@router.post("/admin/login", response_model=schemas.Token)
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Admin login endpoint.
    Expects form-encoded fields: username (email) and password.
    Returns: { "access_token": "<JWT>", "token_type": "bearer" }
    """
    admin = (
        db.query(models.Admin)
        .filter(models.Admin.email == form_data.username)
        .first()
    )

    # TODO: add real password verification when password hashes are available:
    # if not admin or not verify_password(form_data.password, admin.hashed_password):
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    admin.last_login_at = datetime.utcnow()
    db.commit()

    access_token = create_access_token(
        subject=str(admin.id),
        additional_claims={"role": admin.role.value},
    )
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_admin(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    Resolve the current admin from a Bearer token.
    Raises 401 if the token is invalid or the admin cannot be found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id_raw = payload.get("sub")
        if admin_id_raw is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        admin_uuid = uuid.UUID(str(admin_id_raw))
    except Exception:
        raise credentials_exception

    admin = db.query(models.Admin).filter(models.Admin.id == admin_uuid).first()
    if admin is None:
        raise credentials_exception
    return admin


@router.post("/admin/candidates", response_model=schemas.Candidate, status_code=status.HTTP_201_CREATED)
def create_new_candidate(
    *,
    db: Session = Depends(get_db),
    candidate_in: schemas.CandidateCreate,
    current_admin: models.Admin = Depends(get_current_admin),
):
    """
    Create a new candidate profile and log the action to the audit trail.
    """
    candidate = models.Candidate(
        **candidate_in.dict(),
        created_at=datetime.utcnow(),
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    log_admin_action(
        db=db,
        admin_id=current_admin.id,
        action=ActionType.CREATE,
        table_name="candidates",
        entity_id=candidate.id,
    )

    return candidate
