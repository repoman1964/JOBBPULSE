"""Self-serve contractor registration, email verify, and password login."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, urlparse
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.errors import AppError
from app.core.security import hash_password, verify_password
from app.integrations.email.resend import send_verification_email
from app.models.auth import AuthChallenge
from app.models.company import Contractor
from app.models.enums import ContractorStatus


def _token(url: str) -> str:
    return parse_qs(urlparse(url).query)["token"][0]


def _register(
    client: TestClient,
    *,
    email: str = "Alex@Example.com",
    password: str = "secret123",
) -> object:
    return client.post(
        "/api/v1/auth/register",
        json={
            "name": "Alex Rivera",
            "email": email,
            "password": password,
            "companyName": "Rivera Painting",
            "phone": "4045550100",
        },
    )


def test_production_can_show_otp_without_email() -> None:
    settings = Settings(
        app_env="production",
        jwt_secret="not-a-dev-secret-use-this-in-tests-32b",
        auth_dev_codes=False,
        auth_show_otp=True,
    )
    assert settings.return_otp_to_client is True


def test_production_hides_otp_by_default() -> None:
    settings = Settings(
        app_env="production",
        jwt_secret="not-a-dev-secret-use-this-in-tests-32b",
        auth_dev_codes=False,
        auth_show_otp=False,
    )
    assert settings.return_otp_to_client is False
    assert settings.return_verification_url_to_client is False


def test_password_hash_round_trip() -> None:
    stored = hash_password("secret123")
    assert stored.startswith("pbkdf2_sha256$")
    assert verify_password("secret123", stored)
    assert not verify_password("wrong", stored)
    assert not verify_password("secret123", None)


def test_register_requires_password(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Alex Rivera",
            "email": "alex@example.com",
            "companyName": "Rivera Painting",
        },
    )
    assert resp.status_code == 422
    assert resp.json()["code"] == "validation_error"


def test_register_persists_pending_account(client: TestClient) -> None:
    resp = _register(client)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["email"] == "alex@example.com"
    assert body["companyId"]
    assert body["contractorId"]
    assert body["verificationUrl"]
    assert "token=" in body["verificationUrl"]
    assert "accessToken" not in body

    async def load() -> Contractor:
        async with client.app.state.test_session_factory() as session:
            result = await session.get(Contractor, UUID(body["contractorId"]))
            return result

    contractor = asyncio.run(load())
    assert contractor is not None
    assert contractor.status == ContractorStatus.pending.value
    assert contractor.email_verified_at is None
    assert contractor.password_hash
    assert verify_password("secret123", contractor.password_hash)
    assert contractor.phone == "4045550100"
    assert contractor.company_id


def test_register_keeps_pending_account_if_email_send_fails(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def fail_send(**_kwargs: object) -> None:
        raise AppError(
            "email_send_failed",
            "We could not send the confirmation email. Try again in a moment.",
            status_code=503,
        )

    monkeypatch.setattr("app.services.auth_email.send_verification_email", fail_send)
    resp = _register(client)
    assert resp.status_code == 503, resp.text
    assert resp.json()["code"] == "email_send_failed"

    async def load() -> Contractor | None:
        from sqlalchemy import select

        async with client.app.state.test_session_factory() as session:
            result = await session.execute(
                select(Contractor).where(Contractor.email == "alex@example.com")
            )
            return result.scalar_one_or_none()

    contractor = asyncio.run(load())
    assert contractor is not None
    assert contractor.status == ContractorStatus.pending.value
    assert contractor.email_verified_at is None


def test_register_same_email_returns_409(client: TestClient) -> None:
    payload = {
        "name": "Alex Rivera",
        "email": "alex@example.com",
        "password": "secret123",
        "companyName": "Rivera Painting",
    }
    first = client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201
    second = client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409
    assert second.json()["code"] == "email_taken"
    assert "Sign in instead" in second.json()["message"]


def test_register_invalid_payload_returns_422(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Alex",
            "email": "not-an-email",
            "password": "secret123",
            "companyName": "X",
        },
    )
    assert resp.status_code == 422
    body = resp.json()
    assert body["code"] == "validation_error"
    assert "email" in body.get("fieldErrors", {}) or "email" in body["message"].lower()


def test_login_before_verify_returns_403(client: TestClient) -> None:
    assert _register(client).status_code == 201
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "alex@example.com", "password": "secret123"},
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "email_not_verified"


def test_login_wrong_password_returns_401(client: TestClient) -> None:
    reg = _register(client)
    token = _token(reg.json()["verificationUrl"])
    assert client.post("/api/v1/auth/verify-email", json={"token": token}).status_code == 200
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "alex@example.com", "password": "nope-nope"},
    )
    assert resp.status_code == 401
    assert resp.json()["code"] == "invalid_credentials"


def test_verify_email_then_password_login(client: TestClient) -> None:
    reg = _register(client)
    assert reg.status_code == 201
    token = _token(reg.json()["verificationUrl"])

    verified = client.post("/api/v1/auth/verify-email", json={"token": token})
    assert verified.status_code == 200, verified.text
    assert verified.json() == {"email": "alex@example.com", "verified": True}

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "Alex@Example.com", "password": "secret123"},
    )
    assert login.status_code == 200, login.text
    session = login.json()
    assert session["accessToken"]
    assert session["contractor"]["email"] == "alex@example.com"
    assert session["company"]["name"] == "Rivera Painting"
    assert session["company"]["email"] == "alex@example.com"

    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {session['accessToken']}"},
    )
    assert me.status_code == 200
    assert me.json()["contractor"]["email"] == "alex@example.com"


def test_verify_email_link_is_single_use(client: TestClient) -> None:
    reg = _register(client)
    token = _token(reg.json()["verificationUrl"])
    assert client.post("/api/v1/auth/verify-email", json={"token": token}).status_code == 200
    again = client.post("/api/v1/auth/verify-email", json={"token": token})
    assert again.status_code == 200
    assert again.json()["verified"] is True


def test_verify_email_get_redirects_to_sign_in(client: TestClient) -> None:
    reg = _register(client)
    token = _token(reg.json()["verificationUrl"])
    resp = client.get(
        "/api/v1/auth/verify-email",
        params={"token": token},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert resp.headers["location"].endswith("/sign-in?verified=1")

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "alex@example.com", "password": "secret123"},
    )
    assert login.status_code == 200


def test_verify_email_get_invalid_token_redirects_failure(client: TestClient) -> None:
    resp = client.get(
        "/api/v1/auth/verify-email",
        params={"token": "not-a-real-token-value"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert resp.headers["location"].endswith("/sign-in?verified=0")


def test_expired_verification_token_is_rejected(client: TestClient) -> None:
    reg = _register(client)
    token = _token(reg.json()["verificationUrl"])

    async def expire() -> None:
        async with client.app.state.test_session_factory() as session:
            from sqlalchemy import select

            result = await session.execute(
                select(AuthChallenge).where(AuthChallenge.identifier_type == "email_verify")
            )
            challenge = result.scalar_one()
            challenge.expires_at = datetime.now(UTC) - timedelta(hours=1)
            await session.commit()

    asyncio.run(expire())
    resp = client.post("/api/v1/auth/verify-email", json={"token": token})
    assert resp.status_code == 400
    assert resp.json()["code"] == "token_expired"


def test_resend_verification_unknown_email_is_204(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/auth/resend-verification",
        json={"email": "nobody@example.com"},
    )
    assert resp.status_code == 204


def test_resend_verification_issues_new_link(client: TestClient) -> None:
    first = _register(client)
    old_token = _token(first.json()["verificationUrl"])
    resp = client.post(
        "/api/v1/auth/resend-verification",
        json={"email": "alex@example.com"},
    )
    assert resp.status_code == 204

    async def assert_old_token_consumed() -> None:
        from sqlalchemy import select

        from app.core.security import hash_token

        async with client.app.state.test_session_factory() as session:
            result = await session.execute(
                select(AuthChallenge).where(
                    AuthChallenge.identifier_type == "email_verify",
                    AuthChallenge.consumed_at.is_(None),
                )
            )
            challenge = result.scalar_one()
            assert challenge.code_hash != hash_token(old_token)

    asyncio.run(assert_old_token_consumed())
    reused = client.post("/api/v1/auth/verify-email", json={"token": old_token})
    assert reused.status_code == 400


async def test_resend_http_payload() -> None:
    settings = Settings(
        jwt_secret="not-a-dev-secret-use-this-in-tests-32b",
        resend_api_key="re_test_key",
        auth_from_email="login@jobbpulse.com",
    )
    captured: dict = {}

    class FakeResp:
        is_success = True
        status_code = 200
        text = '{"id":"re_test_id"}'

        def json(self) -> dict[str, str]:
            return {"id": "re_test_id"}

    class FakeClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        async def __aenter__(self) -> FakeClient:
            return self

        async def __aexit__(self, *args) -> None:
            return None

        async def post(self, url, headers=None, json=None):
            captured["url"] = url
            captured["headers"] = headers
            captured["json"] = json
            return FakeResp()

    import app.integrations.email.resend as resend_mod

    original = resend_mod.httpx.AsyncClient
    resend_mod.httpx.AsyncClient = FakeClient  # type: ignore[misc]
    try:
        await send_verification_email(
            settings=settings,
            to_email="alex@example.com",
            verify_url="http://localhost:8000/api/v1/auth/verify-email?token=abc",
        )
    finally:
        resend_mod.httpx.AsyncClient = original  # type: ignore[misc]

    assert captured["url"] == "https://api.resend.com/emails"
    assert captured["headers"]["Authorization"] == "Bearer re_test_key"
    assert captured["json"]["to"] == ["alex@example.com"]
    assert "Confirm your JobbPulse account" == captured["json"]["subject"]
    assert "token=abc" in captured["json"]["text"]
    assert captured["json"]["from"] == "JobbPulse <login@jobbpulse.com>"


async def test_resend_test_domain_403_raises_email_send_failed() -> None:
    settings = Settings(
        jwt_secret="not-a-dev-secret-use-this-in-tests-32b",
        resend_api_key="re_test_key",
        auth_from_email="JobbPulse <onboarding@resend.dev>",
    )

    class FakeResp:
        is_success = False
        status_code = 403
        text = (
            "You can only send testing emails to your own email address "
            "(owner@example.com). To send emails to other recipients, please "
            "verify a domain at resend.com/domains."
        )

        def json(self) -> dict[str, str]:
            return {"message": self.text}

    class FakeClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        async def __aenter__(self) -> FakeClient:
            return self

        async def __aexit__(self, *args) -> None:
            return None

        async def post(self, url, headers=None, json=None):
            return FakeResp()

    import app.integrations.email.resend as resend_mod

    original = resend_mod.httpx.AsyncClient
    resend_mod.httpx.AsyncClient = FakeClient  # type: ignore[misc]
    try:
        with pytest.raises(AppError) as caught:
            await send_verification_email(
                settings=settings,
                to_email="contractor@example.com",
                verify_url="https://api.example/verify-email?token=abc",
            )
    finally:
        resend_mod.httpx.AsyncClient = original  # type: ignore[misc]

    assert caught.value.code == "email_send_failed"
    assert caught.value.status_code == 503
