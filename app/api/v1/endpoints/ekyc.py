from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.citizen import Citizen, VerificationStatus

router = APIRouter()

# Placeholder for a dependency that would get the current logged-in citizen
# In a real flow, the citizen_id would be tied to the 'state' parameter
def get_current_citizen(db: Session, citizen_id: int = 1): # Mocking user with ID 1
    # This is a placeholder. A real implementation would get the user from a JWT.
    # user = db.query(Citizen).filter(Citizen.id == citizen_id).first()
    # return user
    pass

@router.post("/ekyc/initiate", status_code=status.HTTP_200_OK)
def initiate_ekyc_flow(db: Session = Depends(get_db)):
    """
    Initiates the e-KYC process.
    
    Returns a mock redirect URL to a partner bank's authorization page.
    """
    # In a real flow, 'state' would be a unique, securely generated token.
    mock_bank_auth_url = "https://mockbank.electa.com/auth?client_id=electa&state=xyz123&redirect_uri=/api/v1/ekyc/callback"
    
    return {"redirect_url": mock_bank_auth_url}

@router.get("/ekyc/callback", status_code=status.HTTP_200_OK)
def handle_ekyc_callback(code: str, state: str, db: Session = Depends(get_db)):
    """
    Handles the callback from the partner bank after user authorization.
    
    In a real flow, this would exchange the 'code' for an access token and
    then fetch the user's verified NID data from the bank.
    """
    # 1. Verify the 'state' parameter to prevent CSRF attacks (skipped in mock)
    
    # 2. Exchange the authorization 'code' for user data (mocked)
    if code != "mock_success_code":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid authorization code")
    
    # Mocked user data we would get from the bank
    mock_user_data_from_bank = {
        "full_name": "Saima Wazed",
        "nid": "1982123456789"
    }
    
    # 3. Update the citizen's status in our database
    # For this test, we'll just assume we're updating the first user in the table.
    # A real implementation would look up the user based on the 'state' parameter.
    citizen_to_verify = db.query(Citizen).first()
    if citizen_to_verify:
        citizen_to_verify.verification_status = VerificationStatus.NID_VERIFIED
        db.commit()
        return {"status": "success", "message": f"User {citizen_to_verify.mobile_number} has been NID Verified."}
    
    return {"status": "error", "message": "No user found to verify."}