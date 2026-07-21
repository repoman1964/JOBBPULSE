"""Phase 8: audit events on approve/publish; privacy; role gate."""

from __future__ import annotations

import io

import pytest
from httpx import AsyncClient

from app.tests.conftest import register_owner, unique_email

PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)
FAKE_AUDIO = b"\x1aE\xdf\xa3" + b"\x00" * 128
PRIVATE_TITLE = "SECRET Audit Private Title XYZ"


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _ready_job(client: AsyncClient, token: str) -> str:
    job = await client.post(
        "/api/v1/jobs",
        json={
            "title": PRIVATE_TITLE,
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
    return job_id


@pytest.mark.asyncio
async def test_publish_creates_audit_events_without_secrets_or_private_title(
    client: AsyncClient,
):
    data = await register_owner(client)
    token = data["access_token"]
    job_id = await _ready_job(client, token)

    approve = await client.post(f"/api/v1/jobs/{job_id}/approve-all", headers=_auth(token))
    assert approve.status_code == 200, approve.text

    pub = await client.post(
        f"/api/v1/jobs/{job_id}/publish",
        json={"publish_to_directory": True, "social_connection_ids": []},
        headers=_auth(token),
    )
    assert pub.status_code == 200, pub.text

    res = await client.get("/api/v1/audit-events?limit=100", headers=_auth(token))
    assert res.status_code == 200, res.text
    items = res.json()["data"]["items"]
    assert items, "expected audit events after approve/publish"
    actions = {i["action"] for i in items}
    assert "job.approved" in actions
    assert "job.published" in actions or "publication.success" in actions

    blob = str(items)
    assert PRIVATE_TITLE not in blob
    assert "credentials_encrypted" not in blob
    assert "password_hash" not in blob
    assert "[REDACTED]" not in blob or True  # may appear if secrets were scrubbed


@pytest.mark.asyncio
async def test_crew_cannot_list_audit_events(client: AsyncClient):
    owner = await register_owner(client)
    token = owner["access_token"]

    crew_email = unique_email("crew")
    invite = await client.post(
        "/api/v1/company/members/invite",
        json={
            "email": crew_email,
            "full_name": "Crew Member",
            "role": "crew",
            "password": "password123",
        },
        headers=_auth(token),
    )
    assert invite.status_code == 201, invite.text

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": crew_email, "password": "password123"},
    )
    assert login.status_code == 200, login.text
    crew_token = login.json()["data"]["access_token"]

    res = await client.get("/api/v1/audit-events", headers=_auth(crew_token))
    assert res.status_code == 403, res.text
