# D:\Application\Electa\app\app\electa-backend-api\app\core\config.py
from __future__ import annotations

import json
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    
    # SMS
    sms_provider: str = Field(default="mock", env="SMS_PROVIDER")  
    # mock|twilio|disabled
    twilio_account_sid: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = Field(default=None, env="TWILIO_AUTH_TOKEN")
    twilio_from_number: Optional[str] = Field(default=None, env="TWILIO_FROM_NUMBER")


    # Where to load .env from, allow env var overrides
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App metadata
    project_name: str = Field(default="ELECTA API", env="PROJECT_NAME")
    env: str = Field(default="dev", env="ENV")

    # Security / Auth
    secret_key: str = Field(env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Database / cache
    sqlalchemy_database_uri: str = Field(env="SQLALCHEMY_DATABASE_URI")
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")

    # CORS
    # Accept JSON array or comma-separated string in env
    cors_origins: List[str] = Field(default_factory=list, env="CORS_ORIGINS")

    def cors_origins_normalized(self) -> List[str]:
        if isinstance(self.cors_origins, list):
            return [str(o) for o in self.cors_origins]
        if isinstance(self.cors_origins, str):
            # Try JSON first; fallback to comma-separated
            try:
                arr = json.loads(self.cors_origins)
                if isinstance(arr, list):
                    return [str(o) for o in arr]
            except Exception:
                pass
            return [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        return [str(self.cors_origins)]


settings = Settings()
