"""Phase 7 social publishing: connections, gate, privacy, idempotency, schedule."""

from __future__ import annotations

import io
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient

from app.modules.publishing.provider.mock import FAIL_MARKER, mock_idempotency_hits, reset_mock_store
from app.tests.conftest import register_owner, unique_email

PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)
FAKE_AUDIO = b"\x1aE\xdf\xa3" + b"\x00" * 128
PRIVATE_TITLE = "SECRET Private Job For Social 999"


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


async def _add_voice(client: AsyncClient, token: str, job_id: str):
    up = await client.post(
        f"/api/v1/jobs/{job_id}/voice/upload",
        headers=_auth(token),
        files={"file": ("site_note.webm", io.BytesIO(FAKE_AUDIO), "audio/webm")},
    )
    assert up.status_code == 201, up.text


async def _approved_job(client: AsyncClient, token: str) -> str:
    job = await _create_job(client, token)
    job_id = job["id"]
    await _add_photo(client, token, job_id, "after")
    await _add_voice(client, token, job_id)
    gen = await client.post(f"/api/v1/jobs/{job_id}/generate", headers=_auth(token))
    assert gen.status_code == 200, gen.text
    approve = await client.post(f"/api/v1/jobs/{job_id}/approve-all", headers=_auth(token))
    assert approve.status_code == 200, approve.text
    assert approve.json()["data"]["job"]["status"] == "approved"
    return job_id


async def _connect(client: AsyncClient, token: str, platform: str = "facebook") -> dict:
    res = await client.post(
        "/api/v1/publishing/connections/start",
        headers=_auth(token),
        json={"platform": platform, "display_name": f"Test {platform}"},
    )
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


@pytest.fixture(autouse=True)
def _reset_mock():
    reset_mock_store()
    yield
    reset_mock_store()


@pytest.mark.asyncio
async def test_connect_mock_account(client: AsyncClient):
    token = await _owner(client)
    conn = await _connect(client, token)
    assert conn["status"] == "active"
    assert conn["platform"] == "facebook"
    assert "credentials" not in conn
    assert "credentials_encrypted" not in conn


@pytest.mark.asyncio
async def test_unapproved_cannot_publish_social(client: AsyncClient):
    token = await _owner(client)
    conn = await _connect(client, token)
    job = await _create_job(client, token)
    job_id = job["id"]
    await _add_photo(client, token, job_id, "after")
    await _add_voice(client, token, job_id)
    await client.post(f"/api/v1/jobs/{job_id}/generate", headers=_auth(token))

    res = await client.post(
        f"/api/v1/jobs/{job_id}/publish",
        headers=_auth(token),
        json={
            "publish_to_directory": False,
            "social_connection_ids": [conn["id"]],
        },
    )
    assert res.status_code == 400, res.text
    assert res.json()["error"]["code"] == "PUBLISH_NOT_ALLOWED"


@pytest.mark.asyncio
async def test_publish_social_success_no_private_title(client: AsyncClient):
    token = await _owner(client)
    conn = await _connect(client, token)
    job_id = await _approved_job(client, token)

    res = await client.post(
        f"/api/v1/jobs/{job_id}/publish",
        headers=_auth(token),
        json={
            "publish_to_directory": False,
            "social_connection_ids": [conn["id"]],
        },
    )
    assert res.status_code == 200, res.text
    data = res.json()["data"]
    assert data["job"]["status"] == "published"
    pubs = data["publications"]
    social = [p for p in pubs if p["destination_type"] == "social"]
    assert len(social) == 1
    assert social[0]["status"] == "published"
    assert social[0]["external_url"]
    assert PRIVATE_TITLE not in (social[0].get("external_url") or "")
    # response listing may be null
    blob = str(data["publications"])
    assert PRIVATE_TITLE not in blob


@pytest.mark.asyncio
async def test_combined_directory_and_social(client: AsyncClient):
    token = await _owner(client)
    conn = await _connect(client, token)
    job_id = await _approved_job(client, token)

    res = await client.post(
        f"/api/v1/jobs/{job_id}/publish",
        headers=_auth(token),
        json={
            "publish_to_directory": True,
            "social_connection_ids": [conn["id"]],
        },
    )
    assert res.status_code == 200, res.text
    data = res.json()["data"]
    types = {p["destination_type"] for p in data["publications"]}
    assert "directory" in types
    assert "social" in types
    assert data["public_url"]
    assert data["listing"]["status"] == "published"


@pytest.mark.asyncio
async def test_directory_only_still_works(client: AsyncClient):
    token = await _owner(client)
    job_id = await _approved_job(client, token)
    res = await client.post(
        f"/api/v1/jobs/{job_id}/publish",
        headers=_auth(token),
        json={"publish_to_directory": True, "social_connection_ids": []},
    )
    assert res.status_code == 200, res.text
    assert res.json()["data"]["listing"]["status"] == "published"


@pytest.mark.asyncio
async def test_idempotent_republish_same_connection(client: AsyncClient):
    token = await _owner(client)
    conn = await _connect(client, token)
    job_id = await _approved_job(client, token)
    payload = {
        "publish_to_directory": False,
        "social_connection_ids": [conn["id"]],
    }
    first = await client.post(
        f"/api/v1/jobs/{job_id}/publish", headers=_auth(token), json=payload
    )
    assert first.status_code == 200, first.text
    pub1 = first.json()["data"]["publications"][0]
    key = pub1["idempotency_key"]
    ext1 = pub1["provider_request_id"]

    second = await client.post(
        f"/api/v1/jobs/{job_id}/publish", headers=_auth(token), json=payload
    )
    assert second.status_code == 200, second.text
    pub2 = second.json()["data"]["publications"][0]
    assert pub2["id"] == pub1["id"]
    assert pub2["provider_request_id"] == ext1
    # Mock may be called again but replays same external id
    assert mock_idempotency_hits(key) >= 1

    pubs = await client.get(f"/api/v1/jobs/{job_id}/publications", headers=_auth(token))
    social = [p for p in pubs.json()["data"]["items"] if p["destination_type"] == "social"]
    assert len(social) == 1


@pytest.mark.asyncio
async def test_retry_failed_publication(client: AsyncClient):
    token = await _owner(client)
    conn = await _connect(client, token)
    job_id = await _approved_job(client, token)

    # Inject fail marker into primary social body
    content = await client.get(f"/api/v1/jobs/{job_id}/content", headers=_auth(token))
    assert content.status_code == 200, content.text
    payload = content.json()["data"]
    variants = payload["variants"] if isinstance(payload, dict) else payload
    primary = next(v for v in variants if v["content_type"] == "primary_social")
    await client.patch(
        f"/api/v1/content/{primary['id']}",
        headers=_auth(token),
        json={"body_edited": f"Nice work {FAIL_MARKER}"},
    )

    pub_res = await client.post(
        f"/api/v1/jobs/{job_id}/publish",
        headers=_auth(token),
        json={"publish_to_directory": False, "social_connection_ids": [conn["id"]]},
    )
    assert pub_res.status_code == 200, pub_res.text
    social = next(
        p for p in pub_res.json()["data"]["publications"] if p["destination_type"] == "social"
    )
    assert social["status"] == "failed"
    pub_id = social["id"]
    attempts = social["attempt_count"]

    # Fix body then retry
    await client.patch(
        f"/api/v1/content/{primary['id']}",
        headers=_auth(token),
        json={"body_edited": "Nice exterior paint job in Austin."},
    )
    retry = await client.post(
        f"/api/v1/publications/{pub_id}/retry",
        headers=_auth(token),
    )
    assert retry.status_code == 200, retry.text
    data = retry.json()["data"]
    assert data["status"] == "published"
    assert data["attempt_count"] > attempts
    assert data["id"] == pub_id


@pytest.mark.asyncio
async def test_schedule_and_cancel(client: AsyncClient):
    token = await _owner(client)
    conn = await _connect(client, token)
    job_id = await _approved_job(client, token)
    when = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

    res = await client.post(
        f"/api/v1/jobs/{job_id}/schedule",
        headers=_auth(token),
        json={
            "scheduled_for": when,
            "publish_to_directory": False,
            "social_connection_ids": [conn["id"]],
        },
    )
    assert res.status_code == 200, res.text
    social = next(
        p for p in res.json()["data"]["publications"] if p["destination_type"] == "social"
    )
    assert social["status"] == "scheduled"
    pub_id = social["id"]

    cancel = await client.post(
        f"/api/v1/publications/{pub_id}/cancel",
        headers=_auth(token),
    )
    assert cancel.status_code == 200, cancel.text
    assert cancel.json()["data"]["status"] == "cancelled"


@pytest.mark.asyncio
async def test_crew_cannot_connect_or_publish(client: AsyncClient):
    owner = await _owner(client)
    conn = await _connect(client, owner)
    job_id = await _approved_job(client, owner)
    crew = await _invite_crew(client, owner)

    bad_conn = await client.post(
        "/api/v1/publishing/connections/start",
        headers=_auth(crew),
        json={"platform": "instagram"},
    )
    assert bad_conn.status_code == 403, bad_conn.text

    bad_pub = await client.post(
        f"/api/v1/jobs/{job_id}/publish",
        headers=_auth(crew),
        json={"publish_to_directory": False, "social_connection_ids": [conn["id"]]},
    )
    assert bad_pub.status_code == 403, bad_pub.text


@pytest.mark.asyncio
async def test_list_publications(client: AsyncClient):
    token = await _owner(client)
    conn = await _connect(client, token, "instagram")
    job_id = await _approved_job(client, token)
    await client.post(
        f"/api/v1/jobs/{job_id}/publish",
        headers=_auth(token),
        json={"publish_to_directory": True, "social_connection_ids": [conn["id"]]},
    )
    res = await client.get(f"/api/v1/jobs/{job_id}/publications", headers=_auth(token))
    assert res.status_code == 200, res.text
    items = res.json()["data"]["items"]
    assert len(items) >= 2
