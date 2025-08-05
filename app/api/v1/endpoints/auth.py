import random
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate
from app.schemas.token import Token
from app.models.citizen import Citizen
from app.core.security import get_password_hash, create_access_token
from app.db.session import get_db
from app.middleware.rate_limiter import limiter # Import the limiter

router = APIRouter()

# In-memory dictionary to act as a temporary OTP store.
otp_storage = {}

@router.post("/auth/register/request-otp", status_code=200)
@limiter.limit("1/minute") # This applies the rate limit
def request_otp(request: Request, user_in: UserCreate):
    """
    Generate a mock OTP and log it to the console.
    This endpoint is rate-limited to 1 request per minute per IP.
    """
    otp = random.randint(100000, 999999)
    otp_storage[user_in.mobile_number] = otp

    print(f"--- OTP for {user_in.mobile_number}: {otp} ---") # Mock SMS

    return {"message": "OTP has been sent (check console log)."}

@router.post("/auth/register/verify-otp", response_model=Token)
def verify_otp(user_in: UserCreate, otp: int, db: Session = Depends(get_db)):
    """
    Verify the OTP, create a new user, and return a JWT token.
    """
    stored_otp = otp_storage.get(user_in.mobile_number)

    if not stored_otp or stored_otp != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    existing_user = db.query(Citizen).filter(Citizen.mobile_number == user_in.mobile_number).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Mobile number already registered")

    hashed_password = get_password_hash(user_in.password)
    new_user = Citizen(
        mobile_number=user_in.mobile_number,
        password_hash=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    del otp_storage[user_in.mobile_number]

    access_token = create_access_token(data={"sub": str(new_user.id)})

    return {"access_token": access_token, "token_type": "bearer"}