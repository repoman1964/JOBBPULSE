"""Resend send vs skip for verification and password-reset mail."""

from types import SimpleNamespace

import pytest

from app.modules.auth import email as email_mod


def _settings(**overrides) -> SimpleNamespace:
    values = {
        "resend_api_key": "re_test",
        "email_from": "JobbPulse <hello@jobbpulse.com>",
        "is_production": False,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class _FakeResponse:
    def __init__(self, status: int = 200, body: str = '{"id":"email_1"}'):
        self.status_code = status
        self.text = body
        self.is_success = 200 <= status < 300

    def json(self):
        return {"id": "email_1"}


class _FakeClient:
    calls: list

    def __init__(self, **_kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_exc):
        return False

    async def post(self, url, headers=None, json=None):
        _FakeClient.calls.append({"url": url, "headers": headers, "json": json})
        return _FakeResponse()


@pytest.fixture
def resend_client(monkeypatch):
    _FakeClient.calls = []
    monkeypatch.setattr(email_mod.httpx, "AsyncClient", _FakeClient)
    return _FakeClient


@pytest.mark.asyncio
async def test_verification_sends_when_key_and_domain_from(resend_client):
    await email_mod.send_verification_email(
        settings=_settings(),
        to_email="owner@example.com",
        verify_url="http://localhost:3000/sign-in?token=abc",
    )
    assert len(resend_client.calls) == 1
    call = resend_client.calls[0]
    assert call["url"] == email_mod.RESEND_URL
    assert call["json"]["from"] == "JobbPulse <hello@jobbpulse.com>"
    assert call["json"]["to"] == ["owner@example.com"]
    assert "Confirm your JobbPulse account" == call["json"]["subject"]
    assert "token=abc" in call["json"]["text"]


@pytest.mark.asyncio
async def test_password_reset_sends_when_key_and_domain_from(resend_client):
    await email_mod.send_password_reset_email(
        settings=_settings(),
        to_email="owner@example.com",
        reset_url="http://localhost:3000/reset-password?token=xyz",
    )
    assert len(resend_client.calls) == 1
    call = resend_client.calls[0]
    assert call["json"]["subject"] == "Reset your JobbPulse password"
    assert "token=xyz" in call["json"]["text"]


@pytest.mark.asyncio
async def test_localhost_from_skips_live_send(resend_client):
    await email_mod.send_verification_email(
        settings=_settings(email_from="JobbPulse <noreply@localhost>"),
        to_email="owner@example.com",
        verify_url="http://localhost:3000/sign-in?token=abc",
    )
    assert resend_client.calls == []


@pytest.mark.asyncio
async def test_missing_key_skips_live_send(resend_client):
    await email_mod.send_password_reset_email(
        settings=_settings(resend_api_key=""),
        to_email="owner@example.com",
        reset_url="http://localhost:3000/reset-password?token=xyz",
    )
    assert resend_client.calls == []
