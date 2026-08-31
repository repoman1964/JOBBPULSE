"""Phase 4 AI generation tests."""

from __future__ import annotations

import io

import pytest
from httpx import AsyncClient

from app.modules.jobs.privacy import PRIVATE_JOB_FIELDS
from app.tests.conftest import register_owner

PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)
FAKE_AUDIO = b"\x1aE\xdf\xa3" + b"\x00" * 128

REQUIRED_TYPES = {
    "primary_social",
    "short_caption",
    "facebook_group",
    "google_business",
    "directory_listing",
}


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _owner(client: AsyncClient) -> str:
    data = await register_owner(client, trade="painting")
    return data["access_token"]


async def _create_job(
    client: AsyncClient, token: str, title: str = "SECRET Customer / 123 Private St"
):
    res = await client.post(
        "/api/v1/jobs",
        json={
            "title": title,
            "city": "Austin",
            "state": "TX",
            "service_key": "exterior_paint",
        },
        headers=_auth(token),
    )
    assert res.status_code == 201, res.text
    return res.json()["data"]


async def _add_photo(client: AsyncClient, token: str, job_id: str, stage: str):
    r = await client.post(
        f"/api/v1/jobs/{job_id}/media/upload",
        headers=_auth(token),
        files={"file": (f"{stage}.png", io.BytesIO(PNG), "image/png")},
        data={"stage_label": stage},
    )
    assert r.status_code == 201, r.text
    return r.json()["data"]


async def _add_voice(client: AsyncClient, token: str, job_id: str):
    up = await client.post(
        f"/api/v1/jobs/{job_id}/voice/upload",
        headers=_auth(token),
        files={"file": ("site_note.webm", io.BytesIO(FAKE_AUDIO), "audio/webm")},
    )
    assert up.status_code == 201, up.text
    return up.json()["data"]


async def _ready_job(client: AsyncClient, token: str, *, with_before: bool = False):
    job = await _create_job(client, token)
    job_id = job["id"]
    if with_before:
        await _add_photo(client, token, job_id, "before")
    await _add_photo(client, token, job_id, "after")
    await _add_voice(client, token, job_id)
    return job_id, job["title"]


@pytest.mark.asyncio
async def test_generate_happy_path_variants_and_status(client: AsyncClient):
    token = await _owner(client)
    job_id, private_title = await _ready_job(client, token, with_before=False)

    res = await client.post(
        f"/api/v1/jobs/{job_id}/generate",
        json={"tone": "friendly_local", "length_preference": "standard"},
        headers=_auth(token),
    )
    assert res.status_code == 200, res.text
    body = res.json()["data"]
    run = body["run"]
    job = body["job"]
    variants = body["variants"]

    assert run["status"] == "completed"
    assert run["generation_type"] == "initial"
    assert run["model_provider"] == "mock"
    assert run["prompt_version"]
    assert run["input_snapshot_json"]
    assert run["output_snapshot_json"]

    # Privacy: no private fields in input snapshot
    snap = run["input_snapshot_json"]
    for key in PRIVATE_JOB_FIELDS:
        assert key not in snap
    assert private_title not in str(snap.values())
    assert "title" not in snap
    assert "transcript" in snap

    types = {v["content_type"] for v in variants}
    assert REQUIRED_TYPES.issubset(types)
    for v in variants:
        assert v["status"] == "awaiting_review"
        assert v["body_generated"]
        assert v["version_number"] == 1

    assert job["status"] == "awaiting_review"
    assert job["next_action"]["action"] == "review_content"
    assert body["warnings"]  # no before photos → soft warning

    # Content endpoint
    content = await client.get(f"/api/v1/jobs/{job_id}/content", headers=_auth(token))
    assert content.status_code == 200, content.text
    cdata = content.json()["data"]
    assert cdata["generation_version"] == 1
    assert cdata["structured_details"] is not None
    assert cdata["structured_details"]["work_completed"]
    assert len(cdata["variants"]) >= 4

    # List runs + get run
    runs = await client.get(
        f"/api/v1/jobs/{job_id}/generation-runs", headers=_auth(token)
    )
    assert runs.status_code == 200
    assert len(runs.json()["data"]) == 1
    got = await client.get(
        f"/api/v1/generation-runs/{run['id']}", headers=_auth(token)
    )
    assert got.status_code == 200
    assert got.json()["data"]["id"] == run["id"]
    assert len(got.json()["data"]["variants"]) >= 4


@pytest.mark.asyncio
async def test_generate_requires_after_and_transcript(client: AsyncClient):
    token = await _owner(client)
    job = await _create_job(client, token)
    job_id = job["id"]

    res = await client.post(f"/api/v1/jobs/{job_id}/generate", headers=_auth(token))
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "AFTER_PHOTOS_REQUIRED"

    await _add_photo(client, token, job_id, "after")
    res2 = await client.post(f"/api/v1/jobs/{job_id}/generate", headers=_auth(token))
    assert res2.status_code == 400
    assert res2.json()["error"]["code"] == "TRANSCRIPT_REQUIRED"


@pytest.mark.asyncio
async def test_generate_prefers_edited_transcript(client: AsyncClient):
    token = await _owner(client)
    job_id, _ = await _ready_job(client, token)

    edited = "We painted the front porch semi-gloss white and cleaned thoroughly."
    patch = await client.patch(
        f"/api/v1/jobs/{job_id}/voice/transcript",
        json={"transcript_edited": edited},
        headers=_auth(token),
    )
    assert patch.status_code == 200, patch.text

    res = await client.post(f"/api/v1/jobs/{job_id}/generate", headers=_auth(token))
    assert res.status_code == 200, res.text
    snap = res.json()["data"]["run"]["input_snapshot_json"]
    assert snap["transcript"] == edited


@pytest.mark.asyncio
async def test_regenerate_supersedes_and_versions(client: AsyncClient):
    token = await _owner(client)
    job_id, _ = await _ready_job(client, token, with_before=True)

    first = await client.post(f"/api/v1/jobs/{job_id}/generate", headers=_auth(token))
    assert first.status_code == 200, first.text
    v1_ids = {v["id"] for v in first.json()["data"]["variants"]}

    second = await client.post(
        f"/api/v1/jobs/{job_id}/regenerate",
        json={"user_instruction": "Focus on curb appeal."},
        headers=_auth(token),
    )
    assert second.status_code == 200, second.text
    data = second.json()["data"]
    assert data["run"]["generation_type"] == "regenerate"
    assert data["run"]["status"] == "completed"
    for v in data["variants"]:
        assert v["version_number"] == 2
        assert v["status"] == "awaiting_review"

    content = await client.get(f"/api/v1/jobs/{job_id}/content", headers=_auth(token))
    active = content.json()["data"]["variants"]
    active_ids = {v["id"] for v in active}
    assert active_ids.isdisjoint(v1_ids)
    assert content.json()["data"]["generation_version"] == 2

    runs = await client.get(
        f"/api/v1/jobs/{job_id}/generation-runs", headers=_auth(token)
    )
    assert len(runs.json()["data"]) == 2

    # Old variants superseded (visible on first run detail)
    run1_id = first.json()["data"]["run"]["id"]
    old = await client.get(f"/api/v1/generation-runs/{run1_id}", headers=_auth(token))
    for v in old.json()["data"]["variants"]:
        assert v["status"] == "superseded"


@pytest.mark.asyncio
async def test_soft_warnings_without_befores(client: AsyncClient):
    token = await _owner(client)
    job_id, _ = await _ready_job(client, token, with_before=False)
    res = await client.post(f"/api/v1/jobs/{job_id}/generate", headers=_auth(token))
    assert res.status_code == 200
    warnings = res.json()["data"]["warnings"]
    assert any("before" in w.lower() for w in warnings)
