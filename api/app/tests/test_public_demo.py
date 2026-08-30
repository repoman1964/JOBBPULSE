"""Public demo project list used by Red Clay."""

from uuid import UUID

import pytest
from httpx import AsyncClient

from app.core.slug import public_project_slug
from app.modules.directory.public_demo import ELIGIBLE_PUBLIC_STATUSES
from app.tests.conftest import unique_email


def test_public_project_slug_is_stable():
    job_id = UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    slug = public_project_slug("Exterior painting in Decatur", job_id)
    assert slug == "exterior-painting-in-decatur-a1b2"
    assert public_project_slug("Exterior painting in Decatur", job_id) == slug


def test_eligible_statuses_match_spec():
    assert ELIGIBLE_PUBLIC_STATUSES == {
        "ready_for_approval",
        "publishing",
        "published",
        "publish_issue",
    }


@pytest.mark.asyncio
async def test_public_list_without_email_returns_422(client: AsyncClient):
    resp = await client.get("/api/v1/public/demo/projects")
    assert resp.status_code == 422


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
