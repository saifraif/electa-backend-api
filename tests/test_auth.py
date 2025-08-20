# D:\Application\Electa\app\app\electa-backend-api\tests\test_auth.py
from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest_asyncio.fixture
async def client():
    """
    httpx>=0.28 requires ASGITransport; we set base_url to include /api/v1
    because main.py mounts routers with prefix="/api/v1".
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test/api/v1") as ac:
        yield ac


@pytest.mark.asyncio
async def test_request_and_verify_otp(_patch_otp_service, client: AsyncClient):
    body = {"mobile_number": "01700000000", "password": "Secret123!"}

    # Request OTP
    r1 = await client.post("/auth/register/request-otp", json=body)
    assert r1.status_code == 200, r1.text

    # OTP stored by fake service from tests/conftest.py
    code = _patch_otp_service.store["01700000000"]

    # Verify OTP (creates user + returns JWT)
    r2 = await client.post(f"/auth/register/verify-otp?otp={code}", json=body)
    assert r2.status_code == 200, r2.text
    data = r2.json()
    assert "access_token" in data and data["token_type"] == "bearer"

    # Reusing the same OTP must fail (consumed)
    r3 = await client.post(f"/auth/register/verify-otp?otp={code}", json=body)
    assert r3.status_code in (400, 401)


@pytest.mark.asyncio
async def test_login(_patch_otp_service, client: AsyncClient):
    body = {"mobile_number": "01711111111", "password": "Secret123!"}

    # Register via OTP flow first
    r_req = await client.post("/auth/register/request-otp", json=body)
    assert r_req.status_code == 200, r_req.text
    code = _patch_otp_service.store["01711111111"]

    r_ver = await client.post(f"/auth/register/verify-otp?otp={code}", json=body)
    assert r_ver.status_code == 200, r_ver.text

    # Now login with password
    r = await client.post("/auth/login", json=body)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "access_token" in data and data["token_type"] == "bearer"
