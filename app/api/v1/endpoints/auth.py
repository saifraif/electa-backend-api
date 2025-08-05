import random
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, User
from app.schemas.token import Token
from app.models.citizen import Citizen
from app.core.security import get_password_hash, create_access_token
from app.db.session import get_db # We will create this dependency soon

router = APIRouter()

# In-memory dictionary to act as a temporary OTP store.
# In a real system, this would be Redis.
otp_storage = {}

@router.post("/auth/register/request-otp", status_code=200)
def request_otp(user_in: UserCreate):
    """
    Generate a mock OTP and log it to the console.
    In a real system, this would send an SMS.
    """
    # Check if user already exists
    # In a real app, you would have a dedicated CRUD function for this
    # db = next(get_db()) # A simple way to get a db session here
    # existing_user = db.query(Citizen).filter(Citizen.mobile_number == user_in.mobile_number).first()
    # if existing_user:
    #     raise HTTPException(status_code=400, detail="Mobile number already registered")

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
        # Here we would log to AuditLogs
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Check if user already exists
    existing_user = db.query(Citizen).filter(Citizen.mobile_number == user_in.mobile_number).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Mobile number already registered")
        
    # Create new user object
    hashed_password = get_password_hash(user_in.password)
    new_user = Citizen(
        mobile_number=user_in.mobile_number,
        password_hash=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Clean up OTP
    del otp_storage[user_in.mobile_number]
    
    # Generate JWT
    access_token = create_access_token(data={"sub": str(new_user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}