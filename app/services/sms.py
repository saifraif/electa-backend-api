from __future__ import annotations

import os
from typing import Protocol, Optional

from app.core.config import settings


class SmsProvider(Protocol):
    async def send_otp(self, to_number: str, code: str) -> None: ...


class MockSmsProvider:
    async def send_otp(self, to_number: str, code: str) -> None:
        # Just log to stdout; safe for dev
        print(f"[MOCK SMS] To: {to_number} | Code: {code}")


class DisabledSmsProvider:
    async def send_otp(self, to_number: str, code: str) -> None:
        # Do nothing
        pass


_twilio_loaded = False
_TwilioClient = None


def _load_twilio():
    global _twilio_loaded, _TwilioClient
    if _twilio_loaded:
        return
    try:
        from twilio.rest import Client as TwilioClient  # type: ignore
        _TwilioClient = TwilioClient
    except Exception:
        _TwilioClient = None
    _twilio_loaded = True


class TwilioSmsProvider:
    def __init__(
        self,
        account_sid: Optional[str],
        auth_token: Optional[str],
        from_number: Optional[str],
    ) -> None:
        _load_twilio()
        if _TwilioClient is None:
            raise RuntimeError("twilio package not installed. Add 'twilio' to requirements.txt")

        if not account_sid or not auth_token or not from_number:
            raise RuntimeError("Missing Twilio credentials (TWILIO_ACCOUNT_SID/AUTH_TOKEN/FROM_NUMBER)")

        self._client = _TwilioClient(account_sid, auth_token)
        self._from = from_number

    async def send_otp(self, to_number: str, code: str) -> None:
        # Twilio REST client is sync; call directly (FastAPI will run it in thread pool)
        self._client.messages.create(
            body=f"Your one-time code is: {code}",
            from_=self._from,
            to=to_number,
        )


_sms_provider_singleton: Optional[SmsProvider] = None


def get_sms_provider() -> SmsProvider:
    global _sms_provider_singleton
    if _sms_provider_singleton:
        return _sms_provider_singleton

    provider = (settings.__dict__.get("sms_provider")  # type: ignore
                or getattr(settings, "sms_provider", "mock"))
    provider = (provider or "mock").lower()

    if provider == "mock":
        _sms_provider_singleton = MockSmsProvider()
    elif provider == "disabled":
        _sms_provider_singleton = DisabledSmsProvider()
    elif provider == "twilio":
        _sms_provider_singleton = TwilioSmsProvider(
            account_sid=getattr(settings, "twilio_account_sid", None),
            auth_token=getattr(settings, "twilio_auth_token", None),
            from_number=getattr(settings, "twilio_from_number", None),
        )
    else:
        _sms_provider_singleton = MockSmsProvider()

    return _sms_provider_singleton
