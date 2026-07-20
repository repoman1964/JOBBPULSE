"""Phase 2 job capture and media tests."""

from __future__ import annotations

import io

import pytest
from httpx import AsyncClient

from app.modules.jobs.privacy import assert_title_not_in_generation_payload, fields_for_generation
from app.tests.conftest import register_owner


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)


async def _owner_client(client: AsyncClient) -> tuple[str, dict]:
    data = await register_owner(client, trade="painting")
    return data["access_token"], data


async def _create_job(client: AsyncClient, token: str, title: str = "Johnson / Oak St", **extra):
    payload = {"title": title, **extra}
    res = await client.post("/api/v1/jobs", json=payload, headers=_auth(token))
    assert res.status_code == 201, res.text
    return res.json()["data"]


@pytest.mark.asyncio
async def test_create_job_requires_title(client: AsyncClient):
    token, _ = await _owner_client(client)
    res = await client.post("/api/v1/jobs", json={}, headers=_auth(token))
    assert res.status_code == 422

    blank = await client.post(
        "/api/v1/jobs",
        json={"title": "   "},
        headers=_auth(token),
    )
    assert blank.status_code == 422


@pytest.mark.asyncio
async def test_create_job_with_required_private_name(client: AsyncClient):
    token, _ = await _owner_client(client)
    job = await _create_job(client, token, title="Johnson / Oak St")
    assert job["title"] == "Johnson / Oak St"
    assert job["status"] == "draft"
    assert job["photo_counts"]["total"] == 0
    # After is required; before is optional — empty job points at afters
    assert job["next_action"]["action"] == "add_after_photos"
    assert job["next_action"]["optional_tip"]
    assert job["timeline"][0]["key"] == "create"
    assert job["timeline"][0]["status"] == "complete"
    assert job["timeline"][1]["key"] == "before"
    assert job["timeline"][1]["status"] == "optional"
    assert job["timeline"][2]["key"] == "after"
    assert job["timeline"][2]["status"] == "current"


@pytest.mark.asyncio
async def test_create_job_with_fields(client: AsyncClient):
    token, _ = await _owner_client(client)
    job = await _create_job(
        client,
        token,
        title="Front porch refresh",
        service_key="interior_painting",
        city="Austin",
        state="TX",
        location_display="South Austin",
    )
    assert job["title"] == "Front porch refresh"
    assert job["service_key"] == "interior_painting"
    assert job["city"] == "Austin"


@pytest.mark.asyncio
async def test_list_and_get_job(client: AsyncClient):
    token, _ = await _owner_client(client)
    job = await _create_job(client, token, title="Deck stain")
    job_id = job["id"]

    listed = await client.get("/api/v1/jobs", headers=_auth(token))
    assert listed.status_code == 200
    items = listed.json()["data"]
    assert len(items) == 1
    assert items[0]["id"] == job_id
    assert items[0]["next_action"]["action"] == "add_after_photos"
    assert "timeline" in items[0]

    got = await client.get(f"/api/v1/jobs/{job_id}", headers=_auth(token))
    assert got.status_code == 200
    assert got.json()["data"]["title"] == "Deck stain"


@pytest.mark.asyncio
async def test_update_and_archive_job(client: AsyncClient):
    token, _ = await _owner_client(client)
    job = await _create_job(client, token)
    job_id = job["id"]

    patched = await client.patch(
        f"/api/v1/jobs/{job_id}",
        json={"title": "Kitchen cabinets", "notes": "Semi-gloss white"},
        headers=_auth(token),
    )
    assert patched.status_code == 200
    assert patched.json()["data"]["title"] == "Kitchen cabinets"
    assert patched.json()["data"]["notes"] == "Semi-gloss white"

    archived = await client.post(f"/api/v1/jobs/{job_id}/archive", headers=_auth(token))
    assert archived.status_code == 200
    assert archived.json()["data"]["status"] == "archived"
    assert archived.json()["data"]["next_action"]["action"] == "none"

    listed = await client.get("/api/v1/jobs", headers=_auth(token))
    assert listed.json()["data"] == []


@pytest.mark.asyncio
async def test_after_only_path_no_before_required(client: AsyncClient):
    """Forgetting befores must not block completing with afters + voice next."""
    token, _ = await _owner_client(client)
    job_id = (await _create_job(client, token))["id"]

    r = await client.post(
        f"/api/v1/jobs/{job_id}/media/upload",
        headers=_auth(token),
        files={"file": ("after1.png", io.BytesIO(PNG), "image/png")},
        data={"stage_label": "after"},
    )
    assert r.status_code == 201, r.text
    job = r.json()["data"]
    assert job["status"] == "ready_for_summary"
    assert job["photo_counts"]["after"] == 1
    assert job["photo_counts"]["before"] == 0
    assert job["photo_counts"]["has_before_after_pair"] is False
    assert job["next_action"]["action"] == "record_voice_summary"
    assert job["next_action"]["optional_tip"]
    assert job["timeline"][1]["status"] == "skipped"
    assert job["timeline"][2]["status"] == "complete"
    assert job["timeline"][3]["status"] == "current"


@pytest.mark.asyncio
async def test_upload_before_after_photos_and_next_action(client: AsyncClient):
    token, _ = await _owner_client(client)
    job_id = (await _create_job(client, token))["id"]

    r1 = await client.post(
        f"/api/v1/jobs/{job_id}/media/upload",
        headers=_auth(token),
        files={"file": ("before1.png", io.BytesIO(PNG), "image/png")},
        data={"stage_label": "before"},
    )
    assert r1.status_code == 201, r1.text
    job = r1.json()["data"]
    assert job["status"] == "before_photos_added"
    assert job["photo_counts"]["before"] == 1
    assert job["next_action"]["action"] == "add_after_photos"
    assert job["timeline"][1]["status"] == "complete"
    assert job["timeline"][2]["status"] == "current"

    r2 = await client.post(
        f"/api/v1/jobs/{job_id}/media/upload",
        headers=_auth(token),
        files={"file": ("before2.png", io.BytesIO(PNG), "image/png")},
        data={"stage_label": "before"},
    )
    assert r2.status_code == 201
    assert r2.json()["data"]["photo_counts"]["before"] == 2

    r3 = await client.post(
        f"/api/v1/jobs/{job_id}/media/upload",
        headers=_auth(token),
        files={"file": ("after1.png", io.BytesIO(PNG), "image/png")},
        data={"stage_label": "after"},
    )
    assert r3.status_code == 201, r3.text
    job = r3.json()["data"]
    assert job["status"] == "ready_for_summary"
    assert job["photo_counts"]["after"] == 1
    assert job["photo_counts"]["total"] == 3
    assert job["photo_counts"]["has_before_after_pair"] is True
    assert job["next_action"]["action"] == "record_voice_summary"
    assert job["next_action"].get("optional_tip") in (None, "")
    assert job["timeline"][3]["key"] == "voice"
    assert job["timeline"][3]["status"] == "current"
    assert len(job["media"]) == 3

    listed = await client.get("/api/v1/jobs", headers=_auth(token))
    assert listed.json()["data"][0]["next_action"]["action"] == "record_voice_summary"


@pytest.mark.asyncio
async def test_progress_stage_rejected(client: AsyncClient):
    token, _ = await _owner_client(client)
    job_id = (await _create_job(client, token))["id"]

    res = await client.post(
        f"/api/v1/jobs/{job_id}/media/upload",
        headers=_auth(token),
        files={"file": ("p.png", io.BytesIO(PNG), "image/png")},
        data={"stage_label": "progress"},
    )
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "INVALID_STAGE"

    url_res = await client.post(
        f"/api/v1/jobs/{job_id}/media/upload-url",
        json={
            "filename": "shot.jpg",
            "mime_type": "image/jpeg",
            "stage_label": "progress",
        },
        headers=_auth(token),
    )
    assert url_res.status_code == 422


@pytest.mark.asyncio
async def test_signed_upload_url_and_complete(client: AsyncClient):
    token, _ = await _owner_client(client)
    job_id = (await _create_job(client, token))["id"]

    url_res = await client.post(
        f"/api/v1/jobs/{job_id}/media/upload-url",
        json={
            "filename": "shot.jpg",
            "mime_type": "image/jpeg",
            "stage_label": "before",
            "file_size_bytes": 128,
        },
        headers=_auth(token),
    )
    assert url_res.status_code == 201, url_res.text
    payload = url_res.json()["data"]
    assert payload["media_id"]
    assert payload["upload_url"]
    assert payload["upload_method"] == "PUT"

    import httpx

    jpegish = b"\xff\xd8\xff\xd9" + b"\x00" * 64
    put = httpx.put(
        payload["upload_url"],
        content=jpegish,
        headers=payload["headers"],
        timeout=30.0,
    )
    assert put.status_code in {200, 204}, put.text

    complete = await client.post(
        f"/api/v1/jobs/{job_id}/media/complete",
        json={"media_id": payload["media_id"], "file_size_bytes": len(jpegish)},
        headers=_auth(token),
    )
    assert complete.status_code == 200, complete.text
    job = complete.json()["data"]
    assert job["photo_counts"]["before"] == 1
    assert job["status"] == "before_photos_added"


@pytest.mark.asyncio
async def test_label_primary_delete_and_reorder(client: AsyncClient):
    token, _ = await _owner_client(client)
    job_id = (await _create_job(client, token))["id"]

    ids = []
    for name in ("a.png", "b.png", "c.png"):
        up = await client.post(
            f"/api/v1/jobs/{job_id}/media/upload",
            headers=_auth(token),
            files={"file": (name, io.BytesIO(PNG), "image/png")},
            data={"stage_label": "before"},
        )
        assert up.status_code == 201, up.text
        ids.append(up.json()["data"]["media"][-1]["id"])

    # Reverse order: c, b, a
    reordered = await client.post(
        f"/api/v1/jobs/{job_id}/media/reorder",
        json={"media_ids": list(reversed(ids))},
        headers=_auth(token),
    )
    assert reordered.status_code == 200, reordered.text
    media = reordered.json()["data"]["media"]
    assert [m["id"] for m in media] == list(reversed(ids))

    media_id = ids[0]
    patched = await client.patch(
        f"/api/v1/media/{media_id}",
        json={"stage_label": "after"},
        headers=_auth(token),
    )
    assert patched.status_code == 200
    assert patched.json()["data"]["stage_label"] == "after"

    primary = await client.post(
        f"/api/v1/media/{media_id}/set-primary",
        headers=_auth(token),
    )
    assert primary.status_code == 200
    assert primary.json()["data"]["is_primary"] is True

    deleted = await client.delete(f"/api/v1/media/{media_id}", headers=_auth(token))
    assert deleted.status_code == 200


@pytest.mark.asyncio
async def test_generation_payload_excludes_private_title(client: AsyncClient):
    token, _ = await _owner_client(client)
    job_data = await _create_job(
        client,
        token,
        title="SECRET Customer / 123 Private St",
        city="Austin",
        state="TX",
        location_display="South Austin",
    )
    # Load ORM via get would need DB; instead verify privacy helper contract
    from uuid import UUID

    from app.db.models import Job

    job = Job(
        id=UUID(job_data["id"]),
        company_id=UUID(job_data["company_id"]),
        title=job_data["title"],
        city=job_data["city"],
        state=job_data["state"],
        location_display=job_data["location_display"],
        service_key=None,
        customer_name_private="Should Not Leak",
        notes="private",
    )
    payload = fields_for_generation(job)
    assert "title" not in payload
    assert "customer_name_private" not in payload
    assert "notes" not in payload
    assert payload["city"] == "Austin"
    assert_title_not_in_generation_payload(payload)

    with pytest.raises(ValueError):
        assert_title_not_in_generation_payload({"title": "leak"})


@pytest.mark.asyncio
async def test_jobs_require_auth(client: AsyncClient):
    res = await client.get("/api/v1/jobs")
    assert res.status_code == 401
