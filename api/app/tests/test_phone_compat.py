"""Contractor phone-path compatibility tests against api/."""

from __future__ import annotations

import io
from urllib.parse import parse_qs, urlparse

import pytest
from httpx import AsyncClient

from app.tests.conftest import unique_email

PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)
FAKE_AUDIO = b"\x1aE\xdf\xa3" + b"\x00" * 128


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _signup(client: AsyncClient) -> tuple[str, dict]:
    email = unique_email("phone")
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Pat Contractor",
            "email": email,
            "password": "password123",
            "companyName": "Pat Paint",
        },
    )
    assert reg.status_code == 201, reg.text
    data = reg.json()["data"]
    token = parse_qs(urlparse(data["verificationUrl"]).query)["token"][0]
    await client.post("/api/v1/auth/verify-email", json={"token": token})
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    assert login.status_code == 200, login.text
    session = login.json()["data"]
    return session["accessToken"], session


async def _ready_job(client: AsyncClient, token: str, name: str = "SECRET Oak St") -> str:
    created = await client.post(
        "/api/v1/jobs",
        json={"name": name, "serviceType": "painting", "city": "Austin", "region": "TX"},
        headers=_auth(token),
    )
    assert created.status_code == 201, created.text
    job = created.json()["data"]
    assert job["name"] == name
    assert job["publicStatus"] == "active"
    job_id = job["id"]
    for stage in ("before", "progress", "after"):
        up = await client.post(
            f"/api/v1/jobs/{job_id}/media/upload",
            headers=_auth(token),
            files={"file": (f"{stage}.png", io.BytesIO(PNG), "image/png")},
            data={"stage_label": stage},
        )
        assert up.status_code == 201, up.text
    voice = await client.post(
        f"/api/v1/jobs/{job_id}/voice/upload",
        headers=_auth(token),
        files={"file": ("note.webm", io.BytesIO(FAKE_AUDIO), "audio/webm")},
    )
    assert voice.status_code == 201, voice.text
    return job_id


@pytest.mark.asyncio
async def test_phone_session_shape(client: AsyncClient):
    token, session = await _signup(client)
    assert session["contractor"]["name"] == "Pat Contractor"
    assert session["company"]["photoMinimums"]["after"] == 1
    me = await client.get("/api/v1/auth/me", headers=_auth(token))
    assert me.status_code == 200
    assert me.json()["data"]["accessToken"]


@pytest.mark.asyncio
async def test_submit_creates_package_without_job_name(client: AsyncClient):
    token, _ = await _signup(client)
    secret = "NEVER SEND THIS NAME"
    job_id = await _ready_job(client, token, name=secret)
    key = "submit-1"
    res = await client.post(
        f"/api/v1/jobs/{job_id}/submit",
        json={"idempotencyKey": key},
        headers=_auth(token),
    )
    assert res.status_code == 200, res.text
    job = res.json()["data"]
    assert job["publicStatus"] == "ready_for_approval"
    assert job["name"] == secret  # contractor-only; still on the job resource

    again = await client.post(
        f"/api/v1/jobs/{job_id}/submit",
        json={"idempotencyKey": key},
        headers=_auth(token),
    )
    assert again.status_code == 200
    assert again.json()["data"]["id"] == job_id

    pkg = await client.get(f"/api/v1/jobs/{job_id}/package", headers=_auth(token))
    assert pkg.status_code == 200, pkg.text
    data = pkg.json()["data"]
    assert data["assets"]
    assert secret not in str(data.get("projectDescription", ""))
    for asset in data["assets"]:
        assert secret not in (asset.get("title") or "")
        assert secret not in (asset.get("body") or "")

    runs = await client.get(f"/api/v1/jobs/{job_id}/generation-runs", headers=_auth(token))
    snapshot = runs.json()["data"][0]["input_snapshot_json"]
    assert secret not in str(snapshot)
    assert "title" not in (snapshot or {})


@pytest.mark.asyncio
async def test_approve_and_publish_writes_directory(client: AsyncClient):
    token, _ = await _signup(client)
    job_id = await _ready_job(client, token, name="Private label only")
    sub = await client.post(
        f"/api/v1/jobs/{job_id}/submit",
        json={"idempotencyKey": "s1"},
        headers=_auth(token),
    )
    assert sub.status_code == 200, sub.text
    pub = await client.post(
        f"/api/v1/jobs/{job_id}/approve-and-publish",
        json={"idempotencyKey": "p1"},
        headers=_auth(token),
    )
    assert pub.status_code == 200, pub.text
    assert pub.json()["data"]["publicStatus"] in {"published", "publish_issue"}
    listings = await client.get("/api/v1/directory/listings", headers=_auth(token))
    assert listings.status_code == 200, listings.text
    items = listings.json()["data"]["items"]
    assert items, listings.text
    listing = items[0]
    blob = str(listing)
    assert "Private label only" not in blob


@pytest.mark.asyncio
async def test_soft_delete_hides_job(client: AsyncClient):
    token, _ = await _signup(client)
    created = await client.post(
        "/api/v1/jobs",
        json={"name": "To delete", "serviceType": "painting", "city": "Austin"},
        headers=_auth(token),
    )
    job_id = created.json()["data"]["id"]
    deleted = await client.delete(f"/api/v1/jobs/{job_id}", headers=_auth(token))
    assert deleted.status_code == 200, deleted.text
    listed = await client.get("/api/v1/jobs", headers=_auth(token))
    assert listed.json()["data"]["items"] == []


@pytest.mark.asyncio
async def test_phone_voice_session_strips_codec_and_completes(client: AsyncClient):
    """Chrome MediaRecorder sends audio/webm;codecs=opus; signed PUT must use audio/webm."""
    token, _ = await _signup(client)
    created = await client.post(
        "/api/v1/jobs",
        json={"name": "Voice capture", "serviceType": "painting", "city": "Austin"},
        headers=_auth(token),
    )
    job_id = created.json()["data"]["id"]
    after = await client.post(
        f"/api/v1/jobs/{job_id}/media/upload",
        headers=_auth(token),
        files={"file": ("after.png", io.BytesIO(PNG), "image/png")},
        data={"stage_label": "after"},
    )
    assert after.status_code == 201, after.text

    session = await client.post(
        f"/api/v1/jobs/{job_id}/voice/upload-sessions",
        json={
            "mimeType": "audio/webm;codecs=opus",
            "byteSize": len(FAKE_AUDIO),
            "durationMs": 2500,
        },
        headers=_auth(token),
    )
    assert session.status_code == 201, session.text
    payload = session.json()["data"]
    assert payload["mediaId"]
    assert payload["uploadUrl"]
    assert payload["headers"]["Content-Type"] == "audio/webm"

    import httpx

    put = httpx.put(
        payload["uploadUrl"],
        content=FAKE_AUDIO,
        headers=payload["headers"],
        timeout=30.0,
    )
    assert put.status_code in {200, 204}, put.text

    complete = await client.post(
        f"/api/v1/jobs/{job_id}/voice/{payload['mediaId']}/complete",
        headers=_auth(token),
    )
    assert complete.status_code == 200, complete.text
    media = complete.json()["data"]
    assert media["kind"] == "audio"
    assert media["uploadStatus"] == "complete"

    got = await client.get(f"/api/v1/jobs/{job_id}/voice", headers=_auth(token))
    assert got.status_code == 200, got.text
    voice = got.json()["data"]
    assert voice["audio_asset_id"] == media["id"]
    assert voice["transcription_status"] == "completed"

    job = await client.get(f"/api/v1/jobs/{job_id}", headers=_auth(token))
    assert job.json()["data"]["hasVoice"] is True


@pytest.mark.asyncio
async def test_list_jobs_cursor_envelope(client: AsyncClient):
    token, _ = await _signup(client)
    await client.post(
        "/api/v1/jobs",
        json={"name": "One", "serviceType": "painting", "city": "Austin"},
        headers=_auth(token),
    )
    listed = await client.get("/api/v1/jobs", headers=_auth(token))
    body = listed.json()["data"]
    assert "items" in body
    assert "nextCursor" in body
    assert body["items"][0]["name"] == "One"
