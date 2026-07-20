"""Phase 3 voice summary and mock transcription tests."""

from __future__ import annotations

import io

import pytest
from httpx import AsyncClient

from app.modules.jobs.privacy import assert_title_not_in_generation_payload, fields_for_generation
from app.tests.conftest import register_owner

PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)

# Tiny fake webm-ish payload for mock STT
FAKE_AUDIO = b"\x1aE\xdf\xa3" + b"\x00" * 128


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _owner(client: AsyncClient) -> str:
    data = await register_owner(client, trade="painting")
    return data["access_token"]


async def _create_job(client: AsyncClient, token: str, title: str = "Johnson / Oak St"):
    res = await client.post(
        "/api/v1/jobs",
        json={"title": title, "city": "Austin", "state": "TX"},
        headers=_auth(token),
    )
    assert res.status_code == 201, res.text
    return res.json()["data"]


async def _add_after(client: AsyncClient, token: str, job_id: str):
    r = await client.post(
        f"/api/v1/jobs/{job_id}/media/upload",
        headers=_auth(token),
        files={"file": ("after1.png", io.BytesIO(PNG), "image/png")},
        data={"stage_label": "after"},
    )
    assert r.status_code == 201, r.text
    return r.json()["data"]


@pytest.mark.asyncio
async def test_voice_requires_after_photo(client: AsyncClient):
    token = await _owner(client)
    job_id = (await _create_job(client, token))["id"]

    res = await client.post(
        f"/api/v1/jobs/{job_id}/voice/upload",
        headers=_auth(token),
        files={"file": ("voice.webm", io.BytesIO(FAKE_AUDIO), "audio/webm")},
    )
    assert res.status_code == 400, res.text
    assert res.json()["error"]["code"] == "AFTER_PHOTOS_REQUIRED"


@pytest.mark.asyncio
async def test_voice_upload_mock_transcript_edit_and_advance(client: AsyncClient):
    token = await _owner(client)
    job = await _create_job(client, token, title="SECRET Customer / 123 Private St")
    job_id = job["id"]
    await _add_after(client, token, job_id)

    # Multipart voice path (tests + CORS fallback)
    up = await client.post(
        f"/api/v1/jobs/{job_id}/voice/upload",
        headers=_auth(token),
        files={"file": ("site_note.webm", io.BytesIO(FAKE_AUDIO), "audio/webm")},
    )
    assert up.status_code == 201, up.text
    body = up.json()["data"]
    voice = body["voice"]
    job_out = body["job"]

    assert voice["transcription_status"] == "completed"
    assert voice["transcription_provider"] == "mock"
    assert voice["transcript_raw"]
    assert "mock transcript" in voice["transcript_raw"]
    assert voice["transcript"] == voice["transcript_raw"]
    assert voice["transcript_edited"] is None

    assert job_out["status"] == "ready_to_generate"
    assert job_out["next_action"]["action"] == "generate_content"
    voice_step = next(s for s in job_out["timeline"] if s["key"] == "voice")
    assert voice_step["status"] == "complete"
    assert job_out["voice"]["id"] == voice["id"]

    got = await client.get(f"/api/v1/jobs/{job_id}/voice", headers=_auth(token))
    assert got.status_code == 200
    assert got.json()["data"]["transcript_raw"]

    edited = "We painted the front porch semi-gloss white and cleaned thoroughly."
    patch = await client.patch(
        f"/api/v1/jobs/{job_id}/voice/transcript",
        json={"transcript_edited": edited},
        headers=_auth(token),
    )
    assert patch.status_code == 200, patch.text
    v2 = patch.json()["data"]["voice"]
    assert v2["transcript_edited"] == edited
    assert v2["transcript"] == edited
    assert patch.json()["data"]["job"]["next_action"]["action"] == "generate_content"

    # Privacy: title never in generation payload; edited transcript preferred
    from uuid import UUID

    from app.db.models import Job, TranscriptionStatus, VoiceSummary

    orm_job = Job(
        id=UUID(job_id),
        company_id=UUID(job_out["company_id"]),
        title=job["title"],
        city="Austin",
        state="TX",
        location_display=None,
        service_key=None,
    )
    orm_voice = VoiceSummary(
        job_id=UUID(job_id),
        transcript_raw=voice["transcript_raw"],
        transcript_edited=edited,
        transcription_status=TranscriptionStatus.completed,
        language="en",
    )
    payload = fields_for_generation(orm_job, orm_voice)
    assert "title" not in payload
    assert payload["transcript"] == edited
    assert_title_not_in_generation_payload(payload)


@pytest.mark.asyncio
async def test_voice_signed_url_and_complete(client: AsyncClient):
    token = await _owner(client)
    job_id = (await _create_job(client, token))["id"]
    await _add_after(client, token, job_id)

    url_res = await client.post(
        f"/api/v1/jobs/{job_id}/voice/upload-url",
        json={
            "filename": "note.webm",
            "mime_type": "audio/webm",
            "file_size_bytes": len(FAKE_AUDIO),
        },
        headers=_auth(token),
    )
    assert url_res.status_code == 201, url_res.text
    payload = url_res.json()["data"]
    assert payload["media_id"]
    assert payload["upload_url"]

    import httpx

    put = httpx.put(
        payload["upload_url"],
        content=FAKE_AUDIO,
        headers=payload["headers"],
        timeout=30.0,
    )
    assert put.status_code in {200, 204}, put.text

    complete = await client.post(
        f"/api/v1/jobs/{job_id}/voice/complete",
        json={"media_id": payload["media_id"], "file_size_bytes": len(FAKE_AUDIO)},
        headers=_auth(token),
    )
    assert complete.status_code == 200, complete.text
    data = complete.json()["data"]
    assert data["voice"]["transcription_status"] == "completed"
    assert data["job"]["status"] == "ready_to_generate"
    assert data["job"]["next_action"]["action"] == "generate_content"


@pytest.mark.asyncio
async def test_retranscribe(client: AsyncClient):
    token = await _owner(client)
    job_id = (await _create_job(client, token))["id"]
    await _add_after(client, token, job_id)

    up = await client.post(
        f"/api/v1/jobs/{job_id}/voice/upload",
        headers=_auth(token),
        files={"file": ("v.webm", io.BytesIO(FAKE_AUDIO), "audio/webm")},
    )
    assert up.status_code == 201
    raw1 = up.json()["data"]["voice"]["transcript_raw"]

    # Edit then retranscribe clears edit and refreshes raw
    await client.patch(
        f"/api/v1/jobs/{job_id}/voice/transcript",
        json={"transcript_edited": "Custom edit for this job."},
        headers=_auth(token),
    )

    re = await client.post(
        f"/api/v1/jobs/{job_id}/voice/retranscribe",
        headers=_auth(token),
    )
    assert re.status_code == 200, re.text
    v = re.json()["data"]["voice"]
    assert v["transcription_status"] == "completed"
    assert v["transcription_provider"] == "mock"
    assert v["transcript_raw"]
    assert v["transcript_edited"] is None
    assert v["transcript_raw"]  # mock still produces text
    assert raw1  # prior raw existed


@pytest.mark.asyncio
async def test_voice_requires_auth(client: AsyncClient):
    res = await client.get("/api/v1/jobs/00000000-0000-0000-0000-000000000001/voice")
    assert res.status_code == 401
