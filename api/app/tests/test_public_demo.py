"""Public demo project list used by Red Clay."""

import io
from uuid import UUID

import pytest
from httpx import AsyncClient

from types import SimpleNamespace

from app.core.slug import public_project_slug
from app.db.models import ContentType
from app.modules.directory.public_demo import ELIGIBLE_PUBLIC_STATUSES, _social_posts_for_job
from app.tests.conftest import unique_email

PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)
FAKE_AUDIO = b"\x1aE\xdf\xa3" + b"\x00" * 128


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _signup(client: AsyncClient, email: str | None = None) -> tuple[str, str]:
    email = email or unique_email("demo")
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Alex Rivera",
            "email": email,
            "password": "secret123",
            "companyName": "Rivera Painting",
        },
    )
    assert reg.status_code == 201, reg.text
    from urllib.parse import parse_qs, urlparse

    token = parse_qs(urlparse(reg.json()["data"]["verificationUrl"]).query)["token"][0]
    await client.post("/api/v1/auth/verify-email", json={"token": token})
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "secret123"},
    )
    assert login.status_code == 200, login.text
    return login.json()["data"]["accessToken"], email


async def _ready_job(client: AsyncClient, token: str, *, city: str = "Decatur") -> str:
    created = await client.post(
        "/api/v1/jobs",
        json={"name": "Private homeowner", "serviceType": "painting", "city": city, "region": "GA"},
        headers=_auth(token),
    )
    assert created.status_code == 201, created.text
    job_id = created.json()["data"]["id"]
    for stage in ("before", "after"):
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


async def _submit(client: AsyncClient, token: str, job_id: str, key: str) -> dict:
    res = await client.post(
        f"/api/v1/jobs/{job_id}/submit",
        json={"idempotencyKey": key},
        headers=_auth(token),
    )
    assert res.status_code == 200, res.text
    return res.json()["data"]


def test_public_project_slug_is_stable():
    job_id = UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    slug = public_project_slug("Exterior painting in Decatur", job_id)
    assert slug == "exterior-painting-in-decatur-a1b2"
    assert public_project_slug("Exterior painting in Decatur", job_id) == slug


def test_eligible_statuses_match_spec():
    assert ELIGIBLE_PUBLIC_STATUSES == {
        "processing",
        "ready_for_approval",
        "publishing",
        "published",
        "publish_issue",
    }


def test_social_posts_reuse_contractor_variants_without_inventing_titles():
    job = SimpleNamespace(city="Decatur")
    variants = [
        SimpleNamespace(
            content_type=ContentType.primary_social,
            platform_target=None,
            title="Exterior painting in Decatur",
            body_edited=None,
            body_generated="Prep, prime, two finish coats.",
        ),
        SimpleNamespace(
            content_type=ContentType.short_caption,
            platform_target=None,
            title=None,
            body_edited=None,
            body_generated="Prep you can see. Finish from the street.",
        ),
    ]
    posts = {p["destination"]: p for p in _social_posts_for_job(
        job,
        variants,
        title="Exterior painting in Decatur",
        summary="Directory summary",
        after_url="https://cdn.example/after.jpg",
    )}
    assert posts["facebook"]["body"] == "Prep, prime, two finish coats."
    assert posts["instagram"]["body"] == "Prep you can see. Finish from the street."
    assert posts["instagram"]["title"] == "Exterior painting in Decatur"
    assert posts["google_business"]["body"] == posts["facebook"]["body"]
    assert posts["facebook_group"]["groupName"] == "Decatur Neighbors"


@pytest.mark.asyncio
async def test_public_list_without_email_returns_422(client: AsyncClient):
    resp = await client.get("/api/v1/public/demo/projects")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_public_list_matches_email_case_insensitively(client: AsyncClient):
    token, email = await _signup(client)
    job_id = await _ready_job(client, token, city="Decatur")
    await _submit(client, token, job_id, "submit-case")
    mixed = email[0].upper() + email[1:]
    assert mixed != email
    resp = await client.get("/api/v1/public/demo/projects", params={"email": mixed})
    assert resp.status_code == 200, resp.text
    assert len(resp.json()["data"]["items"]) == 1


@pytest.mark.asyncio
async def test_public_list_unknown_email_returns_empty(client: AsyncClient):
    resp = await client.get(
        "/api/v1/public/demo/projects",
        params={"email": "nobody@example.com"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["items"] == []


@pytest.mark.asyncio
async def test_public_list_for_new_account_is_empty(client: AsyncClient):
    email = unique_email("demo")
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Alex Rivera",
            "email": email,
            "password": "secret123",
            "companyName": "Rivera Painting",
        },
    )
    assert reg.status_code == 201, reg.text
    resp = await client.get("/api/v1/public/demo/projects", params={"email": email})
    assert resp.status_code == 200
    assert resp.json()["data"]["items"] == []


@pytest.mark.asyncio
async def test_public_list_returns_submitted_job_and_hides_draft(client: AsyncClient):
    token, email = await _signup(client)
    draft = await client.post(
        "/api/v1/jobs",
        json={"name": "Still a draft", "city": "Atlanta"},
        headers=_auth(token),
    )
    assert draft.status_code == 201, draft.text
    job_id = await _ready_job(client, token, city="Decatur")
    submitted = await _submit(client, token, job_id, "submit-live")
    assert submitted["publicStatus"] == "ready_for_approval"

    resp = await client.get("/api/v1/public/demo/projects", params={"email": email})
    assert resp.status_code == 200, resp.text
    items = resp.json()["data"]["items"]
    assert len(items) == 1
    assert "Private homeowner" not in str(items[0])
    assert items[0]["city"] == "Decatur"
    assert items[0]["slug"]
    assert items[0]["publicTitle"]
    assert items[0]["hasAfter"] is True

    detail = await client.get(
        f"/api/v1/public/demo/projects/{items[0]['slug']}",
        params={"email": email},
    )
    assert detail.status_code == 200, detail.text
    body = detail.json()["data"]
    assert body["slug"] == items[0]["slug"]
    posts = {p["destination"]: p for p in body["socialPosts"]}
    assert set(posts) >= {"facebook", "facebook_group", "instagram", "google_business"}
    assert posts["instagram"]["body"]
    assert posts["google_business"]["body"]
    assert posts["facebook_group"]["groupName"]


@pytest.mark.asyncio
async def test_public_list_prepends_most_recent_submitted_job(client: AsyncClient):
    token, email = await _signup(client)
    first_id = await _ready_job(client, token, city="Atlanta")
    await _submit(client, token, first_id, "submit-old")
    pub = await client.post(
        f"/api/v1/jobs/{first_id}/approve-and-publish",
        json={"idempotencyKey": "publish-old"},
        headers=_auth(token),
    )
    assert pub.status_code == 200, pub.text

    newest_id = await _ready_job(client, token, city="Marietta")
    await _submit(client, token, newest_id, "submit-new")

    resp = await client.get("/api/v1/public/demo/projects", params={"email": email})
    assert resp.status_code == 200, resp.text
    items = resp.json()["data"]["items"]
    assert len(items) == 2
    assert items[0]["city"] == "Marietta"
    assert items[1]["city"] == "Atlanta"
