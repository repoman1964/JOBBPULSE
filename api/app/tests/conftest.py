"""Test fixtures for Phase 1 API tests."""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

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

TRUNCATE_SQL = """
TRUNCATE TABLE
  audit_events,
  notifications,
  publication_jobs,
  publishing_connections,
  directory_listing_media,
  directory_listings,
  contractor_profiles,
  content_variants,
  job_structured_details,
  generation_runs,
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
    return body["data"]
