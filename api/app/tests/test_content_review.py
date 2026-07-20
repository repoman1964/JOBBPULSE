"""Phase 5 human review: edit, approve, reject, job approval, publish gate."""

from __future__ import annotations

import io

import pytest
from httpx import AsyncClient

from app.db.models import (
    ContentType,
    ContentVariant,
    ContentVariantStatus,
    Job,
    JobStatus,
)
from app.modules.content.service import (
    assert_job_publishable,
    evaluate_job_approval,
)
from app.modules.jobs.state import PhotoCounts
from app.tests.conftest import register_owner, unique_email

PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)
FAKE_AUDIO = b"\x1aE\xdf\xa3" + b"\x00" * 128


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _owner(client: AsyncClient) -> str:
    data = await register_owner(client, trade="painting")
    return data["access_token"]


async def _create_job(client: AsyncClient, token: str, title: str = "SECRET Private Job"):
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
    return job_id


async def _generate(client: AsyncClient, token: str, job_id: str):
    res = await client.post(f"/api/v1/jobs/{job_id}/generate", headers=_auth(token))
    assert res.status_code == 200, res.text
    return res.json()["data"]


def _by_type(variants: list) -> dict:
    return {v["content_type"]: v for v in variants}


async def _invite_crew(client: AsyncClient, owner_token: str) -> str:
    crew_email = unique_email("crew")
    invite = await client.post(
        "/api/v1/company/members/invite",
        headers=_auth(owner_token),
        json={
            "email": crew_email,
            "full_name": "Crew Member",
            "password": "password123",
            "role": "crew",
        },
    )
    assert invite.status_code == 201, invite.text
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": crew_email, "password": "password123"},
    )
    assert login.status_code == 200, login.text
    return login.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_edit_variant_sets_body_edited(client: AsyncClient):
    token = await _owner(client)
    job_id = await _ready_job(client, token)
    data = await _generate(client, token, job_id)
    v = data["variants"][0]
    original = v["body_generated"]

    res = await client.patch(
        f"/api/v1/content/{v['id']}",
        json={"body_edited": "Contractor-edited social copy."},
        headers=_auth(token),
    )
    assert res.status_code == 200, res.text
    out = res.json()["data"]
    assert out["body_edited"] == "Contractor-edited social copy."
    assert out["body_generated"] == original
    assert out["body_effective"] == "Contractor-edited social copy."

    got = await client.get(f"/api/v1/content/{v['id']}", headers=_auth(token))
    assert got.status_code == 200
    assert got.json()["data"]["body_effective"] == "Contractor-edited social copy."


@pytest.mark.asyncio
async def test_approve_and_reject_variant(client: AsyncClient):
    token = await _owner(client)
    job_id = await _ready_job(client, token)
    data = await _generate(client, token, job_id)
    by = _by_type(data["variants"])
    social = by["primary_social"]
    directory = by["directory_listing"]

    ap = await client.post(
        f"/api/v1/content/{social['id']}/approve", headers=_auth(token)
    )
    assert ap.status_code == 200, ap.text
    assert ap.json()["data"]["status"] == "approved"
    assert ap.json()["data"]["approved_at"] is not None

    rj = await client.post(
        f"/api/v1/content/{directory['id']}/reject",
        json={"reason": "Too salesy"},
        headers=_auth(token),
    )
    assert rj.status_code == 200, rj.text
    assert rj.json()["data"]["status"] == "rejected"
    assert rj.json()["data"]["rejected_at"] is not None

    job = await client.get(f"/api/v1/jobs/{job_id}", headers=_auth(token))
    assert job.json()["data"]["status"] == "revision_requested"
    assert job.json()["data"]["next_action"]["action"] == "review_content"


@pytest.mark.asyncio
async def test_job_approve_blocked_without_directory(client: AsyncClient):
    token = await _owner(client)
    job_id = await _ready_job(client, token)
    data = await _generate(client, token, job_id)
    by = _by_type(data["variants"])

    # Approve only social
    await client.post(
        f"/api/v1/content/{by['primary_social']['id']}/approve", headers=_auth(token)
    )

    res = await client.post(f"/api/v1/jobs/{job_id}/approve", headers=_auth(token))
    assert res.status_code == 400, res.text
    assert res.json()["error"]["code"] == "APPROVAL_RULES_NOT_MET"
    blockers = res.json()["error"]["details"]["blockers"]
    assert any("directory" in b.lower() for b in blockers)


@pytest.mark.asyncio
async def test_job_approve_blocked_without_after_photos(client: AsyncClient):
    token = await _owner(client)
    job_id = await _ready_job(client, token)
    data = await _generate(client, token, job_id)
    by = _by_type(data["variants"])

    for key in ("primary_social", "directory_listing"):
        r = await client.post(
            f"/api/v1/content/{by[key]['id']}/approve", headers=_auth(token)
        )
        assert r.status_code == 200, r.text

    # Delete the after photo
    job = await client.get(f"/api/v1/jobs/{job_id}", headers=_auth(token))
    media = job.json()["data"]["media"]
    afters = [m for m in media if m["stage_label"] == "after"]
    assert afters
    for m in afters:
        d = await client.delete(f"/api/v1/media/{m['id']}", headers=_auth(token))
        assert d.status_code == 200, d.text

    res = await client.post(f"/api/v1/jobs/{job_id}/approve", headers=_auth(token))
    assert res.status_code == 400, res.text
    assert res.json()["error"]["code"] == "APPROVAL_RULES_NOT_MET"
    blockers = res.json()["error"]["details"]["blockers"]
    assert any("after" in b.lower() for b in blockers)


@pytest.mark.asyncio
async def test_job_approve_succeeds_without_befores(client: AsyncClient):
    token = await _owner(client)
    job_id = await _ready_job(client, token, with_before=False)
    data = await _generate(client, token, job_id)
    by = _by_type(data["variants"])

    for key in ("primary_social", "directory_listing"):
        r = await client.post(
            f"/api/v1/content/{by[key]['id']}/approve", headers=_auth(token)
        )
        assert r.status_code == 200, r.text

    readiness = await client.get(
        f"/api/v1/jobs/{job_id}/approval-readiness", headers=_auth(token)
    )
    assert readiness.status_code == 200
    rdata = readiness.json()["data"]
    assert rdata["can_approve_job"] is True
    assert rdata["before_count"] == 0
    assert any("before" in w.lower() for w in rdata["soft_warnings"])

    res = await client.post(f"/api/v1/jobs/{job_id}/approve", headers=_auth(token))
    assert res.status_code == 200, res.text
    payload = res.json()["data"]
    assert payload["job"]["status"] == "approved"
    assert payload["job"]["next_action"]["action"] == "ready_to_publish"
    assert payload["readiness"]["can_approve_job"] is True


@pytest.mark.asyncio
async def test_approve_all_approves_and_marks_job(client: AsyncClient):
    token = await _owner(client)
    job_id = await _ready_job(client, token, with_before=True)
    await _generate(client, token, job_id)

    res = await client.post(f"/api/v1/jobs/{job_id}/approve-all", headers=_auth(token))
    assert res.status_code == 200, res.text
    payload = res.json()["data"]
    assert payload["job"]["status"] == "approved"
    assert payload["job"]["next_action"]["action"] == "ready_to_publish"
    for v in payload["variants"]:
        assert v["status"] == "approved"


@pytest.mark.asyncio
async def test_crew_cannot_approve_owner_can(client: AsyncClient):
    owner_token = await _owner(client)
    crew_token = await _invite_crew(client, owner_token)
    job_id = await _ready_job(client, owner_token)
    data = await _generate(client, owner_token, job_id)
    v = data["variants"][0]

    # Crew can edit
    edit = await client.patch(
        f"/api/v1/content/{v['id']}",
        json={"body_edited": "Crew edit ok"},
        headers=_auth(crew_token),
    )
    assert edit.status_code == 200, edit.text

    # Crew cannot approve
    ap = await client.post(
        f"/api/v1/content/{v['id']}/approve", headers=_auth(crew_token)
    )
    assert ap.status_code == 403, ap.text

    # Crew cannot reject
    rj = await client.post(
        f"/api/v1/content/{v['id']}/reject", headers=_auth(crew_token)
    )
    assert rj.status_code == 403, rj.text

    # Crew cannot approve-all
    aa = await client.post(
        f"/api/v1/jobs/{job_id}/approve-all", headers=_auth(crew_token)
    )
    assert aa.status_code == 403, aa.text

    # Owner can approve
    ok = await client.post(
        f"/api/v1/content/{v['id']}/approve", headers=_auth(owner_token)
    )
    assert ok.status_code == 200, ok.text
    assert ok.json()["data"]["status"] == "approved"


@pytest.mark.asyncio
async def test_regenerate_clears_approval_and_supersedes(client: AsyncClient):
    token = await _owner(client)
    job_id = await _ready_job(client, token)
    data = await _generate(client, token, job_id)
    v1_ids = {v["id"] for v in data["variants"]}

    aa = await client.post(f"/api/v1/jobs/{job_id}/approve-all", headers=_auth(token))
    assert aa.status_code == 200
    assert aa.json()["data"]["job"]["status"] == "approved"

    regen = await client.post(
        f"/api/v1/jobs/{job_id}/regenerate",
        json={"user_instruction": "Make it shorter."},
        headers=_auth(token),
    )
    assert regen.status_code == 200, regen.text
    out = regen.json()["data"]
    assert out["job"]["status"] == "awaiting_review"
    assert out["job"]["next_action"]["action"] == "review_content"
    for v in out["variants"]:
        assert v["status"] == "awaiting_review"
        assert v["version_number"] == 2

    # Old approved variants are superseded
    run1_id = data["run"]["id"]
    old = await client.get(f"/api/v1/generation-runs/{run1_id}", headers=_auth(token))
    for v in old.json()["data"]["variants"]:
        assert v["id"] in v1_ids
        assert v["status"] == "superseded"


@pytest.mark.asyncio
async def test_assert_job_publishable_gate():
    """Unit-level publish gate — no unapproved content can publish."""
    job = Job(status=JobStatus.awaiting_review)
    counts = PhotoCounts(total=1, before=0, after=1)
    variants: list[ContentVariant] = []

    with pytest.raises(Exception) as exc_info:
        assert_job_publishable(job, variants, counts)
    assert exc_info.value.code == "PUBLISH_NOT_ALLOWED"

    job.status = JobStatus.approved
    social = ContentVariant(
        content_type=ContentType.primary_social,
        body_generated="hi",
        status=ContentVariantStatus.approved,
        version_number=1,
    )
    directory = ContentVariant(
        content_type=ContentType.directory_listing,
        body_generated="dir",
        status=ContentVariantStatus.approved,
        version_number=1,
    )
    # Should pass with approved social + directory + after photos
    assert_job_publishable(job, [social, directory], counts)

    # Fail without directory
    with pytest.raises(Exception) as exc2:
        assert_job_publishable(job, [social], counts)
    assert exc2.value.code == "PUBLISH_NOT_ALLOWED"

    # Fail without after photos
    with pytest.raises(Exception) as exc3:
        assert_job_publishable(job, [social, directory], PhotoCounts(after=0))
    assert exc3.value.code == "PUBLISH_NOT_ALLOWED"


def test_evaluate_approval_soft_warn_no_befores():
    job = Job(status=JobStatus.awaiting_review)
    social = ContentVariant(
        content_type=ContentType.primary_social,
        body_generated="s",
        status=ContentVariantStatus.approved,
        version_number=1,
    )
    directory = ContentVariant(
        content_type=ContentType.directory_listing,
        body_generated="d",
        status=ContentVariantStatus.approved,
        version_number=1,
    )
    readiness = evaluate_job_approval(
        job, [social, directory], PhotoCounts(total=1, before=0, after=1)
    )
    assert readiness.can_approve_job is True
    assert readiness.before_count == 0
    assert readiness.soft_warnings
