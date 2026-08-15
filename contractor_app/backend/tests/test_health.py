"""Basic health and app import tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_live_health() -> None:
    client = TestClient(app)
    resp = client.get("/health/live")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_openapi_available() -> None:
    client = TestClient(app)
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert "/api/v1/jobs" in resp.text
