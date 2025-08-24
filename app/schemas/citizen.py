# D:\Application\Electa\app\electa-backend-api\app\schemas\citizen.py

from pydantic import BaseModel, Field, ConfigDict
import uuid


class CitizenBase(BaseModel):
    """
    Shared fields for all Citizen schemas.
    """
    mobile_number: str = Field(
        ...,
        pattern=r"^\+?[0-9]{10,15}$",
        description="Citizen's mobile number (10–15 digits, optional leading +)",
    )
    role: str = Field(default="citizen", description="Role of the user")


class CitizenCreate(CitizenBase):
    """
    Schema used when creating a new citizen (after OTP verification).
    """
    password: str = Field(..., min_length=6, description="Plaintext password for registration")


class CitizenUpdate(BaseModel):
    """
    Schema for updating citizen info (optional fields).
    """
    password: str | None = Field(default=None, min_length=6, description="New password (optional)")
    role: str | None = Field(default=None, description="Role change (optional)")


class CitizenOut(CitizenBase):
    """
    Response schema returned in API responses.
    """
    id: uuid.UUID

    # ✅ Needed for Pydantic v2 to read from SQLAlchemy ORM objects
    model_config = ConfigDict(from_attributes=True)
