from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    """
    Schema for JWT tokens returned by authentication endpoints.
    """
    access_token: str
    token_type: str

    model_config = ConfigDict(from_attributes=True)
