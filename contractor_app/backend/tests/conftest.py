"""SQLite test client for contractor-app API."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.pool import StaticPool


@compiles(JSONB, "sqlite")
def _jsonb_sqlite(_type, compiler, **_kw) -> str:  # type: ignore[no-untyped-def]
    return "JSON"


@compiles(PGUUID, "sqlite")
def _uuid_sqlite(_type, compiler, **_kw) -> str:  # type: ignore[no-untyped-def]
    return "CHAR(36)"


@pytest.fixture
def client() -> Iterator[TestClient]:
    import app.models  # noqa: F401 — register metadata
    from app.db.base import Base
    from app.db.session import get_db
    from app.main import app as fastapi_app

    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )

    async def setup() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    import asyncio

    asyncio.run(setup())

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    fastapi_app.dependency_overrides[get_db] = override_get_db
    fastapi_app.state.test_session_factory = session_factory
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()

    async def teardown() -> None:
        await engine.dispose()

    asyncio.run(teardown())
