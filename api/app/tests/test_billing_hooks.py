"""Phase 8: billing status, soft enforce gate, webhook stub."""

from __future__ import annotations

import io

import pytest
from httpx import AsyncClient

from app.core.config import get_settings
from app.tests.conftest import register_owner

PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)
FAKE_AUDIO = b"\x1aE\xdf\xa3" + b"\x00" * 128


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _approved_job(client: AsyncClient, token: str) -> str:
    job = await client.post(
        "/api/v1/jobs",
        json={
            "title": "Billing Job",
            "city": "Austin",
            "state": "TX",
            "service_key": "exterior_paint",
        },
        headers=_auth(token),
    )
    assert job.status_code == 201, job.text
    job_id = job.json()["data"]["id"]
    r = await client.post(
        f"/api/v1/jobs/{job_id}/media/upload",
        headers=_auth(token),
        files={"file": ("after.png", io.BytesIO(PNG), "image/png")},
        data={"stage_label": "after"},
    )
    assert r.status_code == 201, r.text
    up = await client.post(
        f"/api/v1/jobs/{job_id}/voice/upload",
        headers=_auth(token),
        files={"file": ("note.webm", io.BytesIO(FAKE_AUDIO), "audio/webm")},
    )
    assert up.status_code == 201, up.text
    gen = await client.post(f"/api/v1/jobs/{job_id}/generate", headers=_auth(token))
    assert gen.status_code == 200, gen.text
    approve = await client.post(f"/api/v1/jobs/{job_id}/approve-all", headers=_auth(token))
    assert approve.status_code == 200, approve.text
    return job_id


@pytest.mark.asyncio
async def test_billing_status_and_enforce_off_allows_publish(client: AsyncClient):
    data = await register_owner(client)
    token = data["access_token"]

    status = await client.get("/api/v1/billing/status", headers=_auth(token))
    assert status.status_code == 200, status.text
    body = status.json()["data"]
    assert body["can_publish"] is True
    assert body["billing_enforce"] is False

    job_id = await _approved_job(client, token)
    pub = await client.post(
        f"/api/v1/jobs/{job_id}/publish",
        json={"publish_to_directory": True},
        headers=_auth(token),
    )
    assert pub.status_code == 200, pub.text


@pytest.mark.asyncio
async def test_billing_enforce_blocks_canceled(client: AsyncClient, monkeypatch):
    data = await register_owner(client)
    token = data["access_token"]
    company_id = data["company"]["id"]
    job_id = await _approved_job(client, token)

    # Mark company canceled via webhook stub
    wh = await client.post(
        "/api/v1/billing/webhooks/stripe",
        json={
            "type": "customer.subscription.updated",
            "company_id": company_id,
            "subscription_status": "canceled",
            "customer_id": "cus_test_123",
        },
    )
    assert wh.status_code == 200, wh.text
    assert wh.json()["data"]["matched"] is True

    settings = get_settings()
    monkeypatch.setattr(settings, "billing_enforce", True)

    blocked = await client.post(
        f"/api/v1/jobs/{job_id}/publish",
        json={"publish_to_directory": True},
        headers=_auth(token),
    )
    assert blocked.status_code == 402, blocked.text
    assert blocked.json()["error"]["code"] == "BILLING_REQUIRED"

    # Enforce off again — publish works
    monkeypatch.setattr(settings, "billing_enforce", False)
    ok = await client.post(
        f"/api/v1/jobs/{job_id}/publish",
        json={"publish_to_directory": True},
        headers=_auth(token),
    )
    assert ok.status_code == 200, ok.text


@pytest.mark.asyncio
async def test_request_id_on_errors_and_status(client: AsyncClient):
    res = await client.get("/api/v1/status")
    assert res.status_code == 200
    assert "X-Request-ID" in res.headers or "x-request-id" in {k.lower() for k in res.headers}
    assert res.json()["meta"].get("request_id")
    assert res.json()["data"].get("version")

    # Custom request id propagated
    res2 = await client.get("/api/v1/status", headers={"X-Request-ID": "test-rid-123"})
    assert res2.headers.get("X-Request-ID") == "test-rid-123"
    assert res2.json()["meta"]["request_id"] == "test-rid-123"

    # AppError still stable envelope
    bad = await client.get("/api/v1/jobs/00000000-0000-0000-0000-000000000001")
    # may be 401 without auth
    assert bad.status_code in (401, 404)
    assert "error" in bad.json()
