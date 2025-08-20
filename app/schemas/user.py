from pydantic import BaseModel, Field
import uuid

# Schema for the request body when creating a new user (after OTP verification)
class UserCreate(BaseModel):
    # UPDATED LINE: Using Field with 'pattern' instead of constr with 'regex'
    mobile_number: str = Field(pattern=r"^\+?[0-9]{10,15}$")
    password: str

# Schema for the response body when returning user information
class User(BaseModel):
    id: uuid.UUID
    mobile_number: str
    role: str

    class Config:
        orm_mode = True