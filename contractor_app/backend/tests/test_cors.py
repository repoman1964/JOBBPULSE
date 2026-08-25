"""Local-dev CORS allows LAN / extra Nuxt ports."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_preflight_allows_unlisted_lan_origin() -> None:
    client = TestClient(app)
    resp = client.options(
        "/api/v1/auth/register",
        headers={
            "Origin": "http://10.9.8.7:3012",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "http://10.9.8.7:3012"
    assert resp.headers.get("access-control-allow-credentials") == "true"


def test_preflight_allows_cloudflare_demo_origin() -> None:
    client = TestClient(app)
    resp = client.options(
        "/api/v1/public/demo/projects",
        headers={
            "Origin": "https://red-clay-website.pages.dev",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "https://red-clay-website.pages.dev"
