from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- Ensure project root is on sys.path so `import app...` works ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # folder that contains 'app/' and 'alembic/'
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Now safe to import app modules
from app.main import app
from app.db.session import Base, get_db


# --- Use an in-memory SQLite DB for tests ---
# check_same_thread=False to allow use across threads in test client
engine = create_engine("sqlite+pysqlite:///:memory:", future=True, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@pytest.fixture(scope="session", autouse=True)
def _create_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Override the app's DB dependency for all tests ---
@pytest.fixture(autouse=True)
def _override_db_dependency(monkeypatch, db_session):
    def _get_db_for_tests():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_db_for_tests  # type: ignore
    yield
    app.dependency_overrides.pop(get_db, None)


# --- Fake OTP service so tests don't require Redis ---
class _FakeOtpService:
    def __init__(self):
        self.store = {}

    async def set(self, identifier: str, code: str, ttl: int = 300) -> None:
        self.store[identifier] = code

    async def get(self, identifier: str):
        return self.store.get(identifier)

    async def verify_and_consume(self, identifier: str, code: str) -> bool:
        val = self.store.get(identifier)
        if val and val == code:
            del self.store[identifier]
            return True
        return False


@pytest.fixture(autouse=True)
def _patch_otp_service(monkeypatch):
    # Patch the singleton used by the app
    import app.services.otp as otp_module  # local import after sys.path fix
    fake = _FakeOtpService()
    monkeypatch.setattr(otp_module, "otp_service", fake, raising=True)
    return fake
