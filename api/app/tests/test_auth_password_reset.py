"""Forgot-password / reset-password against api/."""

from urllib.parse import parse_qs, urlparse

import pytest
from httpx import AsyncClient

from app.tests.conftest import unique_email


async def _verified_user(client: AsyncClient, email: str, password: str = "secret123") -> None:
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Alex Rivera",
            "email": email,
            "password": password,
            "companyName": "Rivera Painting",
        },
    )
    assert reg.status_code == 201, reg.text
    token = parse_qs(urlparse(reg.json()["data"]["verificationUrl"]).query)["token"][0]
    verified = await client.post("/api/v1/auth/verify-email", json={"token": token})
    assert verified.status_code == 200, verified.text


@pytest.mark.asyncio
async def test_forgot_unknown_email_is_ok(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "nobody@example.com"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["resetUrl"] is None


@pytest.mark.asyncio
async def test_forgot_before_verify_does_not_issue_link(client: AsyncClient):
    email = unique_email("pending")
    created = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Alex Rivera",
            "email": email,
            "password": "secret123",
            "companyName": "Rivera Painting",
        },
    )
    assert created.status_code == 201
    resp = await client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert resp.status_code == 200
    assert resp.json()["data"]["resetUrl"] is None


@pytest.mark.asyncio
async def test_reset_password_then_login(client: AsyncClient):
    email = unique_email("reset")
    await _verified_user(client, email)
    forgot = await client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert forgot.status_code == 200, forgot.text
    reset_url = forgot.json()["data"]["resetUrl"]
    assert reset_url
    token = parse_qs(urlparse(reset_url).query)["token"][0]
    reset = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": token, "password": "newpass99"},
    )
    assert reset.status_code == 200, reset.text
    assert reset.json()["data"]["email"] == email

    old = await client.post("/api/v1/auth/login", json={"email": email, "password": "secret123"})
    assert old.status_code == 401
    new = await client.post("/api/v1/auth/login", json={"email": email, "password": "newpass99"})
    assert new.status_code == 200, new.text
    assert new.json()["data"]["accessToken"]


@pytest.mark.asyncio
async def test_reset_password_invalid_token(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": "not-a-real-token-value", "password": "newpass99"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_TOKEN"
