import uuid
from pydantic import BaseModel, EmailStr

# Properties to return to the client
class Admin(BaseModel):
    id: uuid.UUID
    email: EmailStr
    role: str

    class Config:
        from_attributes = True # Use this instead of orm_mode in Pydantic v2