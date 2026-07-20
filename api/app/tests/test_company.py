"""Company and membership permission tests."""

import pytest
from httpx import AsyncClient

from app.tests.conftest import register_owner, unique_email


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_company_get_and_patch(client: AsyncClient):
    data = await register_owner(client)
    token = data["access_token"]

    get_res = await client.get("/api/v1/company", headers=auth_header(token))
    assert get_res.status_code == 200
    company = get_res.json()["data"]
    assert company["name"] == "Test Painting Co"

    patch_res = await client.patch(
        "/api/v1/company",
        headers=auth_header(token),
        json={
            "phone": "555-0100",
            "default_tone": "straightforward",
            "default_call_to_action": "Call us for a free estimate",
            "onboarding_completed": True,
        },
    )
    assert patch_res.status_code == 200
    updated = patch_res.json()["data"]
    assert updated["phone"] == "555-0100"
    assert updated["onboarding_completed"] is True


@pytest.mark.asyncio
async def test_services_and_areas(client: AsyncClient):
    data = await register_owner(client)
    token = data["access_token"]
    headers = auth_header(token)

    svc = await client.post(
        "/api/v1/company/services",
        headers=headers,
        json={"service_key": "interior_painting", "display_name": "Interior Painting"},
    )
    assert svc.status_code == 201
    service_id = svc.json()["data"]["id"]

    listed = await client.get("/api/v1/company/services", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()["data"]) == 1

    area = await client.post(
        "/api/v1/company/service-areas",
        headers=headers,
        json={"display_name": "Austin, TX", "city": "Austin", "state": "TX", "is_primary": True},
    )
    assert area.status_code == 201

    areas = await client.get("/api/v1/company/service-areas", headers=headers)
    assert areas.status_code == 200
    assert areas.json()["data"][0]["city"] == "Austin"

    deleted = await client.delete(f"/api/v1/company/services/{service_id}", headers=headers)
    assert deleted.status_code == 200


@pytest.mark.asyncio
async def test_invite_crew_and_role_permissions(client: AsyncClient):
    owner = await register_owner(client)
    owner_token = owner["access_token"]
    owner_headers = auth_header(owner_token)

    crew_email = unique_email("crew")
    invite = await client.post(
        "/api/v1/company/members/invite",
        headers=owner_headers,
        json={
            "email": crew_email,
            "full_name": "Crew Member",
            "role": "crew",
            "password": "password123",
        },
    )
    assert invite.status_code == 201
    assert invite.json()["data"]["role"] == "crew"

    members = await client.get("/api/v1/company/members", headers=owner_headers)
    assert members.status_code == 200
    assert len(members.json()["data"]) == 2

    # Crew login
    crew_login = await client.post(
        "/api/v1/auth/login",
        json={"email": crew_email, "password": "password123"},
    )
    assert crew_login.status_code == 200
    crew_token = crew_login.json()["data"]["access_token"]
    crew_headers = auth_header(crew_token)

    me = await client.get("/api/v1/auth/me", headers=crew_headers)
    assert me.status_code == 200
    perms = me.json()["data"]["permissions"]
    assert perms["role"] == "crew"
    assert perms["can_create_jobs"] is True
    assert perms["can_manage_team"] is False
    assert perms["can_approve_and_publish"] is False

    # Crew cannot update company
    denied = await client.patch(
        "/api/v1/company",
        headers=crew_headers,
        json={"phone": "555-9999"},
    )
    assert denied.status_code == 403

    # Crew cannot invite
    invite_denied = await client.post(
        "/api/v1/company/members/invite",
        headers=crew_headers,
        json={
            "email": unique_email("other"),
            "full_name": "Other",
            "role": "crew",
            "password": "password123",
        },
    )
    assert invite_denied.status_code == 403
