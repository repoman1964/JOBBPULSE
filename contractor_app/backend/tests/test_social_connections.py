"""Connect and disconnect contractor social accounts."""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient


def _token(url: str) -> str:
    return parse_qs(urlparse(url).query)["token"][0]


def _auth_headers(client: TestClient) -> dict[str, str]:
    registered = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Alex Rivera",
            "email": "alex@example.com",
            "password": "secret123",
            "companyName": "Rivera Painting",
        },
    )
    assert registered.status_code == 201, registered.text
    token = _token(registered.json()["verificationUrl"])
    assert client.post("/api/v1/auth/verify-email", json={"token": token}).status_code == 200
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "alex@example.com", "password": "secret123"},
    )
    assert login.status_code == 200, login.text
    return {"Authorization": f"Bearer {login.json()['accessToken']}"}


def test_list_connections_includes_instagram_facebook_google(client: TestClient) -> None:
    headers = _auth_headers(client)
    resp = client.get("/api/v1/social/connections", headers=headers)
    assert resp.status_code == 200, resp.text
    platforms = [row["platform"] for row in resp.json()]
    assert platforms == ["facebook", "instagram", "google_business"]
    assert all(row["status"] == "not_connected" for row in resp.json())


def test_connect_instagram_and_disconnect(client: TestClient) -> None:
    headers = _auth_headers(client)
    connected = client.put(
        "/api/v1/social/connections/instagram",
        headers=headers,
        json={"accountName": "riverapainting"},
    )
    assert connected.status_code == 200, connected.text
    body = connected.json()
    assert body["platform"] == "instagram"
    assert body["status"] == "connected"
    assert body["accountName"] == "@riverapainting"

    listed = client.get("/api/v1/social/connections", headers=headers)
    ig = next(row for row in listed.json() if row["platform"] == "instagram")
    assert ig["status"] == "connected"
    assert ig["accountName"] == "@riverapainting"

    gone = client.post(
        "/api/v1/social/connections/instagram/disconnect",
        headers=headers,
    )
    assert gone.status_code == 200, gone.text
    assert gone.json()["status"] == "not_connected"
    assert gone.json()["accountName"] is None


def test_unknown_platform_returns_404(client: TestClient) -> None:
    headers = _auth_headers(client)
    resp = client.put(
        "/api/v1/social/connections/tiktok",
        headers=headers,
        json={"accountName": "nope"},
    )
    assert resp.status_code == 404
    assert resp.json()["code"] == "unknown_platform"
