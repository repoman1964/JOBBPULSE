"""Phase 6 directory publishing: gate, privacy, unpublish, roles, idempotency."""

from __future__ import annotations

import io
import json

import pytest
from httpx import AsyncClient

from app.tests.conftest import register_owner, unique_email

PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)
FAKE_AUDIO = b"\x1aE\xdf\xa3" + b"\x00" * 128

PRIVATE_TITLE = "SECRET Private Job Name 123"


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _owner(client: AsyncClient) -> str:
    data = await register_owner(client, trade="painting")
    return data["access_token"]


async def _create_job(client: AsyncClient, token: str, title: str = PRIVATE_TITLE):
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


async def _approve_all(client: AsyncClient, token: str, job_id: str):
    res = await client.post(f"/api/v1/jobs/{job_id}/approve-all", headers=_auth(token))
    assert res.status_code == 200, res.text
    return res.json()["data"]


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


async def _approved_job(client: AsyncClient, token: str, *, with_before: bool = False) -> str:
    job_id = await _ready_job(client, token, with_before=with_before)
    await _generate(client, token, job_id)
    data = await _approve_all(client, token, job_id)
    assert data["job"]["status"] == "approved"
    return job_id


@pytest.mark.asyncio
async def test_publish_blocked_when_not_approved(client: AsyncClient):
    token = await _owner(client)
    job_id = await _ready_job(client, token)
    await _generate(client, token, job_id)
    # Drafts exist but job not approved
    res = await client.post(f"/api/v1/jobs/{job_id}/publish", headers=_auth(token), json={})
    assert res.status_code == 400, res.text
    body = res.json()
    assert body["error"]["code"] == "PUBLISH_NOT_ALLOWED"


@pytest.mark.asyncio
async def test_publish_succeeds_without_before_photos(client: AsyncClient):
    token = await _owner(client)
    job_id = await _approved_job(client, token, with_before=False)
    res = await client.post(
        f"/api/v1/jobs/{job_id}/publish",
        headers=_auth(token),
        json={"publish_to_directory": True},
    )
    assert res.status_code == 200, res.text
    data = res.json()["data"]
    assert data["job"]["status"] == "published"
    assert data["listing"]["status"] == "published"
    assert data["public_url"]
    assert data["listing"]["slug"]
    # Public listing payload must not leak private job title (job admin object may keep it)
    listing_blob = json.dumps(data["listing"], default=str)
    assert PRIVATE_TITLE not in listing_blob
    assert PRIVATE_TITLE not in (data.get("public_url") or "")


@pytest.mark.asyncio
async def test_public_project_never_contains_private_title(client: AsyncClient):
    token = await _owner(client)
    job_id = await _approved_job(client, token, with_before=True)
    pub = await client.post(f"/api/v1/jobs/{job_id}/publish", headers=_auth(token), json={})
    assert pub.status_code == 200, pub.text
    slug = pub.json()["data"]["listing"]["slug"]

    res = await client.get(f"/api/v1/public/projects/{slug}")
    assert res.status_code == 200, res.text
    payload = res.json()["data"]
    blob = json.dumps(payload, default=str)
    assert PRIVATE_TITLE not in blob
    assert "customer_name_private" not in blob
    assert "storage_key" not in payload
    assert payload["public_title"]
    assert payload["public_summary"]
    assert payload["city"] == "Austin"
    assert payload["state"] == "TX"
    # After media present
    stages = {m["stage_label"] for m in payload["media"]}
    assert "after" in stages
    assert "before" in stages


@pytest.mark.asyncio
async def test_public_summary_prefers_body_edited(client: AsyncClient):
    token = await _owner(client)
    job_id = await _ready_job(client, token)
    gen = await _generate(client, token, job_id)
    variants = gen["variants"]
    directory = next(v for v in variants if v["content_type"] == "directory_listing")
    edited = "EDITED public summary for homeowners — unique string xyz."
    patch = await client.patch(
        f"/api/v1/content/{directory['id']}",
        headers=_auth(token),
        json={"body_edited": edited},
    )
    assert patch.status_code == 200, patch.text
    await _approve_all(client, token, job_id)

    pub = await client.post(f"/api/v1/jobs/{job_id}/publish", headers=_auth(token), json={})
    assert pub.status_code == 200, pub.text
    slug = pub.json()["data"]["listing"]["slug"]

    res = await client.get(f"/api/v1/public/projects/{slug}")
    assert res.status_code == 200, res.text
    assert res.json()["data"]["public_summary"] == edited


@pytest.mark.asyncio
async def test_unpublish_hides_from_public(client: AsyncClient):
    token = await _owner(client)
    job_id = await _approved_job(client, token)
    pub = await client.post(f"/api/v1/jobs/{job_id}/publish", headers=_auth(token), json={})
    assert pub.status_code == 200, pub.text
    listing_id = pub.json()["data"]["listing"]["id"]
    slug = pub.json()["data"]["listing"]["slug"]

    assert (await client.get(f"/api/v1/public/projects/{slug}")).status_code == 200

    unpub = await client.post(
        f"/api/v1/directory/listings/{listing_id}/unpublish",
        headers=_auth(token),
    )
    assert unpub.status_code == 200, unpub.text
    assert unpub.json()["data"]["status"] == "unpublished"

    gone = await client.get(f"/api/v1/public/projects/{slug}")
    assert gone.status_code == 404, gone.text


@pytest.mark.asyncio
async def test_republish_idempotent_one_listing_per_job(client: AsyncClient):
    token = await _owner(client)
    job_id = await _approved_job(client, token)
    first = await client.post(f"/api/v1/jobs/{job_id}/publish", headers=_auth(token), json={})
    assert first.status_code == 200, first.text
    listing_id = first.json()["data"]["listing"]["id"]
    slug = first.json()["data"]["listing"]["slug"]

    second = await client.post(f"/api/v1/jobs/{job_id}/publish", headers=_auth(token), json={})
    assert second.status_code == 200, second.text
    assert second.json()["data"]["listing"]["id"] == listing_id
    assert second.json()["data"]["listing"]["slug"] == slug

    listings = await client.get("/api/v1/directory/listings", headers=_auth(token))
    assert listings.status_code == 200
    items = listings.json()["data"]["items"]
    job_listings = [i for i in items if i["job_id"] == job_id]
    assert len(job_listings) == 1


@pytest.mark.asyncio
async def test_crew_cannot_publish(client: AsyncClient):
    owner = await _owner(client)
    job_id = await _approved_job(client, owner)
    crew = await _invite_crew(client, owner)
    res = await client.post(f"/api/v1/jobs/{job_id}/publish", headers=_auth(crew), json={})
    assert res.status_code == 403, res.text


@pytest.mark.asyncio
async def test_profile_slug_stable(client: AsyncClient):
    token = await _owner(client)
    a = await client.get("/api/v1/directory/profile", headers=_auth(token))
    assert a.status_code == 200, a.text
    slug1 = a.json()["data"]["public_slug"]
    b = await client.get("/api/v1/directory/profile", headers=_auth(token))
    assert b.status_code == 200
    assert b.json()["data"]["public_slug"] == slug1


@pytest.mark.asyncio
async def test_public_contractor_lists_published_projects(client: AsyncClient):
    token = await _owner(client)
    job_id = await _approved_job(client, token)
    pub = await client.post(f"/api/v1/jobs/{job_id}/publish", headers=_auth(token), json={})
    assert pub.status_code == 200, pub.text

    profile = await client.get("/api/v1/directory/profile", headers=_auth(token))
    contractor_slug = profile.json()["data"]["public_slug"]

    res = await client.get(f"/api/v1/public/contractors/{contractor_slug}")
    assert res.status_code == 200, res.text
    data = res.json()["data"]
    assert data["slug"] == contractor_slug
    assert len(data["recent_projects"]) >= 1
    assert PRIVATE_TITLE not in json.dumps(data, default=str)


@pytest.mark.asyncio
async def test_unpublish_via_job_endpoint(client: AsyncClient):
    token = await _owner(client)
    job_id = await _approved_job(client, token)
    pub = await client.post(f"/api/v1/jobs/{job_id}/publish", headers=_auth(token), json={})
    slug = pub.json()["data"]["listing"]["slug"]
    unpub = await client.post(
        f"/api/v1/jobs/{job_id}/unpublish-directory",
        headers=_auth(token),
    )
    assert unpub.status_code == 200, unpub.text
    assert (await client.get(f"/api/v1/public/projects/{slug}")).status_code == 404


@pytest.mark.asyncio
async def test_approved_next_action_is_publish(client: AsyncClient):
    token = await _owner(client)
    job_id = await _approved_job(client, token)
    res = await client.get(f"/api/v1/jobs/{job_id}", headers=_auth(token))
    assert res.status_code == 200
    na = res.json()["data"]["next_action"]
    assert na["action"] == "ready_to_publish"
    assert na["cta"] == "Publish"


@pytest.mark.asyncio
async def test_public_paths_use_v2_url_shape(client: AsyncClient):
    token = await _owner(client)
    job_id = await _approved_job(client, token)
    pub = await client.post(f"/api/v1/jobs/{job_id}/publish", headers=_auth(token), json={})
    assert pub.status_code == 200, pub.text
    listing = pub.json()["data"]["listing"]
    assert listing["public_path"] == f"/projects/{listing['slug']}"

    profile = await client.get("/api/v1/directory/profile", headers=_auth(token))
    contractor_slug = profile.json()["data"]["public_slug"]
    assert profile.json()["data"]["public_path"] == f"/contractors/{contractor_slug}"
    assert profile.json()["data"]["portfolio_path"] == f"/contractors/{contractor_slug}/portfolio"

    public = await client.get(f"/api/v1/public/projects/{listing['slug']}")
    assert public.status_code == 200
    data = public.json()["data"]
    assert data["public_path"] == f"/projects/{listing['slug']}"
    assert data["contractor"]["public_path"] == f"/contractors/{contractor_slug}"
    assert data["contractor"]["portfolio_path"] == f"/contractors/{contractor_slug}/portfolio"
    assert "primary_image_url" in data or data.get("media")


@pytest.mark.asyncio
async def test_create_lead_persists_with_project_attribution(client: AsyncClient):
    token = await _owner(client)
    job_id = await _approved_job(client, token)
    pub = await client.post(f"/api/v1/jobs/{job_id}/publish", headers=_auth(token), json={})
    slug = pub.json()["data"]["listing"]["slug"]
    profile = await client.get("/api/v1/directory/profile", headers=_auth(token))
    contractor_slug = profile.json()["data"]["public_slug"]

    res = await client.post(
        "/api/v1/public/leads",
        json={
            "contractor_slug": contractor_slug,
            "name": "Homeowner Pat",
            "email": "pat@example.com",
            "phone": "404-555-0100",
            "message": "Need similar exterior paint",
            "project_slug": slug,
            "source_page_type": "project",
            "source_page_url": f"/projects/{slug}",
            "preferred_contact_method": "phone",
        },
    )
    assert res.status_code == 200, res.text
    data = res.json()["data"]
    assert data["ok"] is True
    assert data["id"]
    assert data["contractor_slug"] == contractor_slug
    assert data["source_project_id"]


@pytest.mark.asyncio
async def test_public_home_and_catalog_endpoints(client: AsyncClient):
    token = await _owner(client)
    job_id = await _approved_job(client, token)
    await client.post(f"/api/v1/jobs/{job_id}/publish", headers=_auth(token), json={})

    home = await client.get("/api/v1/public/home")
    assert home.status_code == 200, home.text
    h = home.json()["data"]
    assert len(h["recent_projects"]) >= 1
    assert "popular_services" in h
    assert "popular_locations" in h

    services = await client.get("/api/v1/public/services")
    assert services.status_code == 200
    svc_items = services.json()["data"]["items"]
    assert len(svc_items) >= 1
    svc_slug = svc_items[0]["slug"]
    svc = await client.get(f"/api/v1/public/services/{svc_slug}")
    assert svc.status_code == 200
    assert len(svc.json()["data"]["projects"]) >= 1

    locations = await client.get("/api/v1/public/locations")
    assert locations.status_code == 200
    loc_items = locations.json()["data"]["items"]
    assert len(loc_items) >= 1
    loc = await client.get(f"/api/v1/public/locations/{loc_items[0]['slug']}")
    assert loc.status_code == 200
    assert len(loc.json()["data"]["projects"]) >= 1

    search = await client.get("/api/v1/public/search", params={"q": "paint"})
    assert search.status_code == 200
    assert "projects" in search.json()["data"]
