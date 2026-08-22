"""Normalize Postgres URLs from hosts like Render into SQLAlchemy asyncpg form."""

from __future__ import annotations

_LOCAL_HOSTS = {"localhost", "127.0.0.1", "postgres"}


def normalize_database_url(url: str) -> str:
    """Turn a libpq/Render URL into postgresql+asyncpg:// with ssl for remote hosts."""
    if not url:
        return url

    if url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url.removeprefix("postgres://")
    elif url.startswith("postgresql://"):
        url = "postgresql+asyncpg://" + url.removeprefix("postgresql://")

    url = url.replace("sslmode=require", "ssl=require")
    url = url.replace("sslmode=prefer", "ssl=require")
    url = url.replace("sslmode=verify-full", "ssl=require")

    if "+asyncpg://" not in url:
        return url

    authority = url.split("@")[-1] if "@" in url else url
    hostname = authority.split("/")[0].split(":")[0].split("?")[0]
    if hostname not in _LOCAL_HOSTS and "ssl=" not in url:
        url = f"{url}{'&' if '?' in url else '?'}ssl=require"

    return url
