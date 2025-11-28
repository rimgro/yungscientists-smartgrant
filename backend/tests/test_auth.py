from uuid import UUID

import pytest
from httpx import AsyncClient

from src.core import security
from src.modules.auth.models import User


@pytest.mark.asyncio
async def test_register_and_login_flow(client: AsyncClient, session_factory):
    payload = {
        "name": "Alice",
        "email": "alice@example.com",
        "password": "supersecret",
        "bank_id": "BANK123",
    }

    register_resp = await client.post("/api/v1/auth/register", json=payload)
    assert register_resp.status_code == 201
    created = register_resp.json()
    assert created["email"] == payload["email"]
    assert "password" not in created

    async with session_factory() as session:
        user = await session.get(User, UUID(created["id"]))
        assert user is not None
        assert security.verify_password(payload["password"], user.hashed_password)

    token_resp = await client.post(
        "/api/v1/auth/login", json={"email": payload["email"], "password": payload["password"]}
    )
    assert token_resp.status_code == 200
    token_data = token_resp.json()
    assert token_data["token_type"] == "bearer"
    assert token_data["access_token"]

    me_resp = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token_data['access_token']}"}
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == payload["email"]


@pytest.mark.asyncio
async def test_duplicate_email_and_bad_password(client: AsyncClient):
    payload = {
        "name": "Bob",
        "email": "bob@example.com",
        "password": "verysecret",
    }

    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    duplicate = await client.post("/api/v1/auth/register", json=payload)
    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "Email already registered"

    bad_login = await client.post("/api/v1/auth/login", json={"email": payload["email"], "password": "bad"})
    assert bad_login.status_code == 401
