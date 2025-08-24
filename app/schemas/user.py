from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

# ---------------------------
# Request Schemas
# ---------------------------
class UserCreate(BaseModel):
    """
    Schema for the request body when creating a new user (after OTP verification).
    """
    mobile_number: str = Field(
        ...,
        pattern=r"^\+?[0-9]{10,15}$",
        description="Mobile number in E.164 format (10-15 digits, optional + prefix).",
        example="+919876543210",
    )
    password: str = Field(
        ...,
        min_length=6,
        description="Plaintext password (will be hashed before storage).",
        example="securePass123",
    )


# ---------------------------
# Response Schemas
# ---------------------------
class User(BaseModel):
    """
    Schema for returning user information.
    """
    id: UUID
    mobile_number: str
    role: str

    model_config = ConfigDict(from_attributes=True)
