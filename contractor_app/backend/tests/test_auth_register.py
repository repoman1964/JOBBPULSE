"""Self-serve contractor registration."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_register_creates_company_and_contractor(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Alex Rivera",
            "email": "Alex@Example.com",
            "companyName": "Rivera Painting",
            "phone": "4045550100",
        },
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["email"] == "alex@example.com"
    assert body["companyId"]
    assert body["contractorId"]


def test_register_same_email_returns_409(client: TestClient) -> None:
    payload = {
        "name": "Alex Rivera",
        "email": "alex@example.com",
        "companyName": "Rivera Painting",
    }
    first = client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201
    second = client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409
    assert second.json()["code"] == "email_taken"
    assert "Sign in instead" in second.json()["message"]


def test_register_invalid_payload_returns_422(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/auth/register",
        json={"name": "Alex", "email": "not-an-email", "companyName": "X"},
    )
    assert resp.status_code == 422
    body = resp.json()
    assert body["code"] == "validation_error"
    assert "email" in body.get("fieldErrors", {}) or "email" in body["message"].lower()


def test_register_then_challenge_and_verify(client: TestClient) -> None:
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Alex Rivera",
            "email": "alex@example.com",
            "companyName": "Rivera Painting",
        },
    )
    assert reg.status_code == 201
    challenge = client.post(
        "/api/v1/auth/challenge",
        json={"identifier": "alex@example.com"},
    )
    assert challenge.status_code == 200
    data = challenge.json()
    verify = client.post(
        "/api/v1/auth/verify",
        json={"challengeId": data["challengeId"], "code": data["devCode"] or "123456"},
    )
    assert verify.status_code == 200, verify.text
    session = verify.json()
    assert session["accessToken"]
    assert session["contractor"]["email"] == "alex@example.com"
    assert session["company"]["name"] == "Rivera Painting"
