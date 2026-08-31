"""Test fixtures for Phase 1 API tests."""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.db.base import Base
from app.db import models  # noqa: F401
from app.db.session import get_db
from app.main import app

settings = get_settings()


@pytest.fixture(autouse=True)
def _reset_rate_limiters():
    from app.core.rate_limit import reset_limiters

    reset_limiters()
    yield
    reset_limiters()


@pytest.fixture(autouse=True)
def _no_live_resend(monkeypatch):
    """Never hit Resend from pytest even if api/.env has a real key + domain from-address."""
    monkeypatch.setattr(settings, "resend_api_key", "")
    monkeypatch.setattr(settings, "email_from", "JobbPulse <noreply@localhost>")

TRUNCATE_SQL = """
TRUNCATE TABLE
  audit_events,
  notifications,
  publication_jobs,
  publishing_connections,
  directory_leads,
  directory_listing_media,
  directory_listings,
  contractor_profiles,
  content_variants,
  job_structured_details,
  generation_runs,
  job_submissions,
  voice_summaries,
  media_assets,
  jobs,
  company_services,
  company_service_areas,
  company_memberships,
  companies,
  users
RESTART IDENTITY CASCADE
"""


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    engine = create_async_engine(settings.database_url, poolclass=NullPool)
    async with engine.begin() as conn:
        # create_all adds missing tables; columns on existing tables come from alembic.
        # Run `make api-migrate` after pulling schema changes.
        await conn.run_sync(Base.metadata.create_all)
        for value in ("publishing", "publish_issue"):
            await conn.execute(text(f"ALTER TYPE job_status ADD VALUE IF NOT EXISTS '{value}'"))
        for value in ("facebook_group", "google_business"):
            await conn.execute(text(f"ALTER TYPE content_type ADD VALUE IF NOT EXISTS '{value}'"))
        for stmt in (
            "ALTER TABLE companies ADD COLUMN IF NOT EXISTS contact_name VARCHAR(200)",
            "ALTER TABLE companies ADD COLUMN IF NOT EXISTS email VARCHAR(320)",
            "ALTER TABLE companies ADD COLUMN IF NOT EXISTS service_area VARCHAR(300)",
            "ALTER TABLE companies ADD COLUMN IF NOT EXISTS photo_minimums_json JSONB",
            "ALTER TABLE companies ADD COLUMN IF NOT EXISTS photo_maximums_json JSONB",
            "ALTER TABLE companies ADD COLUMN IF NOT EXISTS notification_settings_json JSONB",
            "ALTER TABLE companies ADD COLUMN IF NOT EXISTS facebook_group_ids JSONB",
            "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS assigned_crew_member VARCHAR(200)",
            "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS featured_before_media_id UUID",
            "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS featured_after_media_id UUID",
            "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ",
            "ALTER TABLE media_assets ADD COLUMN IF NOT EXISTS is_favorite BOOLEAN DEFAULT false",
            "ALTER TABLE media_assets ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ",
        ):
            await conn.execute(text(stmt))
        await conn.execute(text(TRUNCATE_SQL))

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.execute(text(TRUNCATE_SQL))
    await engine.dispose()


def unique_email(prefix: str = "user") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}@example.com"


async def register_owner(client: AsyncClient, **overrides) -> dict:
    payload = {
        "email": unique_email("owner"),
        "password": "password123",
        "full_name": "Test Owner",
        "company_name": "Test Painting Co",
        "trade": "painting",
    }
    payload.update(overrides)
    res = await client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["error"] is None
    token_url = (body["data"] or {}).get("verificationUrl")
    assert token_url, body
    from urllib.parse import parse_qs, urlparse

    token = parse_qs(urlparse(token_url).query).get("token", [None])[0]
    verified = await client.post("/api/v1/auth/verify-email", json={"token": token})
    assert verified.status_code == 200, verified.text
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert login.status_code == 200, login.text
    data = login.json()["data"]
    data["user"] = data.get("user") or {
        "email": payload["email"],
        "full_name": payload["full_name"],
    }
    return data
