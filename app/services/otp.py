# app/services/otp.py
from __future__ import annotations
import asyncio
from typing import Optional
import redis.asyncio as redis

from app.core.config import settings

OTP_PREFIX = "otp:"
DEFAULT_TTL_SECONDS = 300  # 5 minutes

class OTPService:
    def __init__(self, url: Optional[str] = None):
        self._url = url or settings.redis_url
        if not self._url:
            raise RuntimeError("REDIS_URL is not configured")
        self._r = redis.from_url(self._url, decode_responses=True)

    async def set(self, identifier: str, code: str, ttl: int = DEFAULT_TTL_SECONDS) -> None:
        await self._r.setex(f"{OTP_PREFIX}{identifier}", ttl, code)

    async def get(self, identifier: str) -> Optional[str]:
        return await self._r.get(f"{OTP_PREFIX}{identifier}")

    async def verify_and_consume(self, identifier: str, code: str) -> bool:
        key = f"{OTP_PREFIX}{identifier}"
        val = await self._r.get(key)
        if val and val == code:
            await self._r.delete(key)
            return True
        return False

otp_service = OTPService()
