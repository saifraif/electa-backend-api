from __future__ import annotations

import random
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

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

# 👇 This is the important bit: all routes in this file live under /auth
router = APIRouter(prefix="/auth")

# Per-route rate limits
limiter = Limiter(key_func=get_remote_address)


class LoginRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    mobile_number: str
    password: str


def _generate_otp() -> int:
    return random.randint(100000, 999999)


@router.post("/register/request-otp", status_code=200)
@limiter.limit("5/minute")
async def request_otp(request: Request, user_in: UserCreate):
    """
    Generate an OTP, store in Redis (via otp_service), and send via SMS provider.
    """
    code = _generate_otp()
    await otp_service.set(user_in.mobile_number, str(code))

    sms = get_sms_provider()
    await sms.send_otp(user_in.mobile_number, str(code))

    return {"message": "OTP has been sent."}


@router.post("/register/verify-otp", response_model=Token)
@limiter.limit("10/minute")
async def verify_otp(user_in: UserCreate, otp: int, db: Session = Depends(get_db)):
    """
    Verify OTP, create user, return JWT.
    """
    ok = await otp_service.verify_and_consume(user_in.mobile_number, str(otp))
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    existing = db.query(Citizen).filter(Citizen.mobile_number == user_in.mobile_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Mobile number already registered")

    new_user = Citizen(
        mobile_number=user_in.mobile_number,
        password_hash=get_password_hash(user_in.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(subject=str(new_user.id))
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """
    Password login: verify user and issue JWT.
    """
    user: Optional[Citizen] = (
        db.query(Citizen).filter(Citizen.mobile_number == body.mobile_number).first()
    )
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}
