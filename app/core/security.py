from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings

# === Settings / constants ===
SECRET_KEY: str = settings.secret_key
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = settings.access_token_expire_minutes

# NOTE: tokenUrl is used by the OpenAPI docs only; it does not affect runtime validation.
# Change to "/api/v1/admin/login" if you want admin login in Swagger's "Authorize" flow.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# === Password hashing ===
def get_password_hash(password: str) -> str:
    """Hash a plaintext password (bcrypt)."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against its bcrypt hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Passlib can raise if hash is invalid or algorithm mismatch.
        return False


# === JWT helpers ===
def create_access_token(
    subject: Union[str, Dict[str, Any]],
    expires_delta: Optional[timedelta] = None,
    *,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a signed JWT.
    - If 'subject' is a string, it's placed under 'sub'
    - If 'subject' is a dict, it's merged directly into the payload (must include 'sub' yourself)
    - Adds issued-at ('iat') and expiration ('exp')
    """
    now = datetime.now(tz=timezone.utc)
    delta = expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    if isinstance(subject, str):
        to_encode: Dict[str, Any] = {"sub": subject}
    else:
        to_encode = {**subject}  # must contain 'sub'

    if additional_claims:
        to_encode.update(additional_claims)

    to_encode.update(
        {
            "iat": int(now.timestamp()),
            "exp": int((now + delta).timestamp()),
        }
    )
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and verify a JWT. Raises JWTError on failure."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


# === FastAPI dependencies to reuse in routers ===
def get_current_token_payload(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Dependency: Extract and verify Bearer token from Authorization header.
    Returns the payload or raises 401 on any verification error.
    """
    try:
        return decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_subject(payload: Dict[str, Any] = Depends(get_current_token_payload)) -> str:
    """
    Dependency: Return the 'sub' (subject) claim from the verified token payload.
    Adapt this to load your domain entity (Admin/Citizen) from DB if needed.
    """
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return str(sub)
