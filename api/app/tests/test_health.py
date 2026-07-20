"""Smoke tests for health and root endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_envelope():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["error"] is None
    assert body["data"]["app"] == "JobPulse API"


def test_api_status():
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["ai_provider"] == "mock"
