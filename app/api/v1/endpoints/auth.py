from __future__ import annotations

import random
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate  # expects mobile_number, password
from app.schemas.token import Token
from app.models.citizen import Citizen
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from app.db.session import get_db
from app.services.otp import otp_service
from app.services.sms import get_sms_provider
from app.limits import limiter  # ✅ shared limiter wired in main.py

# All routes here live under /auth (final path: /api/v1/auth/*)
router = APIRouter(prefix="/auth")


# ---------------------------
# Pydantic request models
# ---------------------------
class LoginRequest(BaseModel):
    mobile_number: str
    password: str


class VerifyOtpRequest(BaseModel):
    """
    Payload for OTP verification + password set during registration.
    """
    mobile_number: str
    password: str
    otp: int


# ---------------------------
# Helpers
# ---------------------------
def _generate_otp() -> int:
    return random.randint(100000, 999999)


# ---------------------------
# Routes
# ---------------------------
@router.post("/register/request-otp", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def request_otp(request: Request, user_in: UserCreate):
    """
    Generate an OTP, store in Redis (via otp_service), and send via SMS provider.
    """
    mobile = user_in.mobile_number.strip()
    if not mobile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number required",
        )

    code = _generate_otp()
    await otp_service.set(mobile, str(code))

    sms = get_sms_provider()
    await sms.send_otp(mobile, str(code))

    return {"message": "OTP has been sent."}


@router.post("/register/verify-otp", response_model=Token)
@limiter.limit("10/minute")
async def verify_otp(
    request: Request,
    payload: VerifyOtpRequest,
    db: Session = Depends(get_db),
):
    """
    Verify OTP, create user (if not exists), and return JWT.
    """
    mobile = payload.mobile_number.strip()
    if not mobile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number required",
        )

    ok = await otp_service.verify_and_consume(mobile, str(payload.otp))
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    existing = db.query(Citizen).filter(Citizen.mobile_number == mobile).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number already registered",
        )

    new_user = Citizen(
        mobile_number=mobile,
        password_hash=get_password_hash(payload.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(subject=str(new_user.id))
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(
    request: Request,
    body: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Password login: verify user and issue JWT.
    """
    mobile = body.mobile_number.strip()
    if not mobile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number required",
        )

    user: Optional[Citizen] = (
        db.query(Citizen).filter(Citizen.mobile_number == mobile).first()
    )
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}
