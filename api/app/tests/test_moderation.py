"""Phase 8: directory flag/remove moderation; public 404."""

from __future__ import annotations

import io

import pytest
from httpx import AsyncClient

from app.core.config import get_settings
from app.tests.conftest import register_owner, unique_email

PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)
FAKE_AUDIO = b"\x1aE\xdf\xa3" + b"\x00" * 128


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _publish_listing(client: AsyncClient, token: str) -> tuple[str, str]:
    job = await client.post(
        "/api/v1/jobs",
        json={
            "title": "Moderation Job",
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
    pub = await client.post(
        f"/api/v1/jobs/{job_id}/publish",
        json={"publish_to_directory": True},
        headers=_auth(token),
    )
    assert pub.status_code == 200, pub.text
    listing = pub.json()["data"]["listing"]
    return listing["id"], listing["slug"]


@pytest.mark.asyncio
async def test_flag_hides_from_public_and_owner_can_flag(client: AsyncClient):
    data = await register_owner(client)
    token = data["access_token"]
    listing_id, slug = await _publish_listing(client, token)

    public = await client.get(f"/api/v1/public/projects/{slug}")
    assert public.status_code == 200, public.text

    flag = await client.post(
        f"/api/v1/directory/listings/{listing_id}/flag",
        json={"reason": "spam"},
        headers=_auth(token),
    )
    assert flag.status_code == 200, flag.text
    assert flag.json()["data"]["status"] == "flagged"

    public2 = await client.get(f"/api/v1/public/projects/{slug}")
    assert public2.status_code == 404, public2.text


@pytest.mark.asyncio
async def test_platform_admin_remove_and_non_admin_403(client: AsyncClient, monkeypatch):
    admin_email = unique_email("admin")
    data = await register_owner(client, email=admin_email)
    token = data["access_token"]
    listing_id, slug = await _publish_listing(client, token)

    # Non-admin cannot remove
    bad = await client.post(
        f"/api/v1/admin/directory/listings/{listing_id}/remove",
        headers=_auth(token),
    )
    assert bad.status_code == 403, bad.text

    settings = get_settings()
    monkeypatch.setattr(settings, "founder_admin_emails", admin_email)

    ok = await client.post(
        f"/api/v1/admin/directory/listings/{listing_id}/remove",
        json={"reason": "policy"},
        headers=_auth(token),
    )
    assert ok.status_code == 200, ok.text
    assert ok.json()["data"]["status"] == "removed"

    public = await client.get(f"/api/v1/public/projects/{slug}")
    assert public.status_code == 404, public.text

    listed = await client.get(
        "/api/v1/admin/directory/listings?status=removed",
        headers=_auth(token),
    )
    assert listed.status_code == 200, listed.text
    ids = {i["id"] for i in listed.json()["data"]["items"]}
    assert listing_id in ids or str(listing_id) in ids
