# D:\Application\Electa\app\electa-backend-api\app\schemas\token.py

from pydantic import BaseModel, Field, ConfigDict


class Token(BaseModel):
    """
    Response model for access tokens.
    """
    access_token: str = Field(..., description="JWT access token string")
    token_type: str = Field(default="bearer", description="Token type, usually 'bearer'")

    model_config = ConfigDict(from_attributes=True)


class TokenPayload(BaseModel):
    """
    Payload extracted from JWT.
    """
    sub: str | None = Field(default=None, description="Subject (user ID)")
    exp: int | None = Field(default=None, description="Expiration timestamp (Unix epoch)")

    model_config = ConfigDict(from_attributes=True)
