from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.security import oauth2_scheme, SECRET_KEY, ALGORITHM
from app.db.session import get_db
from app.models.citizen import Citizen, VerificationStatus

# All routes here live under /ekyc (final path: /api/v1/ekyc/*)
router = APIRouter(prefix="/ekyc")


def get_current_citizen(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> Citizen:
    """
    Resolve the current citizen from a Bearer token (JWT).
    Token must contain `sub` with the citizen UUID.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        citizen_id = uuid.UUID(sub)
    except (JWTError, ValueError):
        raise credentials_exception

    citizen = db.query(Citizen).filter(Citizen.id == citizen_id).first()
    if not citizen:
        raise credentials_exception
    return citizen


@router.post("/initiate", status_code=status.HTTP_200_OK)
def initiate_ekyc_flow(
    current_citizen: Citizen = Depends(get_current_citizen),
):
    """
    Initiates the e-KYC process for the authenticated citizen.

    In a real flow:
      - Generate a unique `state` tied to the citizen and persist it (e.g., Redis/DB).
      - Build a partner authorization URL containing that state.
      - Client would open the partner page and return via our /callback.

    This mock returns a placeholder partner URL.
    """
    # Example of a unique state (persist it if implementing for real):
    # state = secrets.token_urlsafe(24)
    # persist_state_for_citizen(current_citizen.id, state)

    mock_state = "xyz123"
    mock_bank_auth_url = (
        "https://mockbank.electa.com/auth?"
        "client_id=electa"
        f"&state={mock_state}"
        "&redirect_uri=/api/v1/ekyc/callback"
    )
    return {"redirect_url": mock_bank_auth_url}


@router.get("/callback", status_code=status.HTTP_200_OK)
def handle_ekyc_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    """
    Handles the callback from the partner after user authorization.

    In a real flow:
      1. Validate `state` (CSRF protection) and map it back to the intended citizen.
      2. Exchange `code` for access token at the partner.
      3. Retrieve verified identity data and update our records.

    This mock accepts only a specific code and marks the first citizen as verified.
    """
    # 1) Validate state (skipped in mock)
    # 2) Exchange authorization code (mocked)
    if code != "mock_success_code":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid authorization code",
        )

    # Mocked user data we would get from the bank (unused here but illustrative)
    mock_user_data_from_bank = {
        "full_name": "Saima Wazed",
        "nid": "1982123456789",
    }

    # 3) Update a citizen record (mock: just take the first one)
    citizen_to_verify = db.query(Citizen).first()
    if not citizen_to_verify:
        return {"status": "error", "message": "No user found to verify."}

    citizen_to_verify.verification_status = VerificationStatus.NID_VERIFIED
    db.commit()

    return {
        "status": "success",
        "message": f"User {citizen_to_verify.mobile_number} has been NID Verified.",
    }
