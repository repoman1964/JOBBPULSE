"""Phase 8: in-app notifications + mark read; no private title leaks."""

from __future__ import annotations

import io

import pytest
from httpx import AsyncClient

from app.tests.conftest import register_owner

PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)
FAKE_AUDIO = b"\x1aE\xdf\xa3" + b"\x00" * 128
PRIVATE_TITLE = "SECRET Notify Private Title 777"


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _generate(client: AsyncClient, token: str) -> str:
    job = await client.post(
        "/api/v1/jobs",
        json={
            "title": PRIVATE_TITLE,
            "city": "Dallas",
            "state": "TX",
            "service_key": "interior_paint",
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
async def test_generation_creates_notifications_and_mark_read(client: AsyncClient):
    data = await register_owner(client)
    token = data["access_token"]
    job_id = await _generate(client, token)

    res = await client.get("/api/v1/notifications", headers=_auth(token))
    assert res.status_code == 200, res.text
    body = res.json()["data"]
    assert body["unread_count"] >= 1
    items = body["items"]
    types = {i["type"] for i in items}
    assert "generation.completed" in types or "content.ready_for_review" in types
    for i in items:
        assert PRIVATE_TITLE not in i["title"]
        assert PRIVATE_TITLE not in i["body"]
        assert PRIVATE_TITLE not in str(i.get("metadata_json") or {})

    nid = items[0]["id"]
    read = await client.post(f"/api/v1/notifications/{nid}/read", headers=_auth(token))
    assert read.status_code == 200, read.text
    assert read.json()["data"]["status"] == "read"

    all_read = await client.post("/api/v1/notifications/read-all", headers=_auth(token))
    assert all_read.status_code == 200, all_read.text

    res2 = await client.get("/api/v1/notifications", headers=_auth(token))
    assert res2.json()["data"]["unread_count"] == 0
    _ = job_id


@pytest.mark.asyncio
async def test_approve_and_publish_notifications(client: AsyncClient):
    data = await register_owner(client)
    token = data["access_token"]
    job_id = await _generate(client, token)

    approve = await client.post(f"/api/v1/jobs/{job_id}/approve-all", headers=_auth(token))
    assert approve.status_code == 200, approve.text

    pub = await client.post(
        f"/api/v1/jobs/{job_id}/publish",
        json={"publish_to_directory": True},
        headers=_auth(token),
    )
    assert pub.status_code == 200, pub.text

    res = await client.get("/api/v1/notifications", headers=_auth(token))
    types = {i["type"] for i in res.json()["data"]["items"]}
    assert "job.approved" in types
    assert "directory.published" in types
