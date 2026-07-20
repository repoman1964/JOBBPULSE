"""Auth endpoint tests."""

import pytest
from httpx import AsyncClient

from app.tests.conftest import register_owner, unique_email


@pytest.mark.asyncio
async def test_register_login_me_flow(client: AsyncClient):
    email = unique_email("reg")
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "full_name": "Jane Contractor",
            "company_name": "Jane Paint Pros",
            "trade": "painting",
        },
    )
    assert reg.status_code == 201
    data = reg.json()["data"]
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["user"]["email"] == email
    assert data["company"]["name"] == "Jane Paint Pros"
    assert data["membership"]["role"] == "owner"

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert login.status_code == 200
    token = login.json()["data"]["access_token"]

    me = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 200
    me_data = me.json()["data"]
    assert me_data["user"]["email"] == email
    assert me_data["permissions"]["can_manage_team"] is True
    assert me_data["permissions"]["can_approve_and_publish"] is True


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    email = unique_email("dup")
    first = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "full_name": "One",
            "company_name": "One Co",
        },
    )
    assert first.status_code == 201
    second = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "full_name": "Two",
            "company_name": "Two Co",
        },
    )
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "EMAIL_EXISTS"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    data = await register_owner(client)
    email = data["user"]["email"]
    res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "wrong-password"},
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    data = await register_owner(client)
    res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": data["refresh_token"]},
    )
    assert res.status_code == 200
    assert res.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_me_requires_auth(client: AsyncClient):
    res = await client.get("/api/v1/auth/me")
    assert res.status_code == 401
