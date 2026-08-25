"""Normalize Postgres URLs from hosts like Render into SQLAlchemy asyncpg form."""

from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

_LOCAL_HOSTS = {"localhost", "127.0.0.1", "postgres", "::1"}
_SSL_QUERY_KEYS = {"ssl", "sslmode"}


def normalize_database_url(url: str) -> str:
    """Turn a libpq/Render URL into postgresql+asyncpg:// without driver SSL query params.

    SSL is applied via connect_args (see database_ssl_connect_args). asyncpg does not
    accept libpq values like ssl=require. Render's internal hostname (dpg-…-a, no
    dot) also does not speak TLS — forcing SSL there makes /health/ready 503.
    """
    if not url:
        return url

    if url.startswith("postgres://"):
        url = "postgresql://" + url.removeprefix("postgres://")

    parts = urlsplit(url)
    scheme = parts.scheme
    if scheme in {"postgres", "postgresql"}:
        scheme = "postgresql+asyncpg"

    query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key.lower() not in _SSL_QUERY_KEYS
    ]
    return urlunsplit((scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def database_hostname(url: str) -> str:
    if not url:
        return ""
    return (urlsplit(normalize_database_url(url)).hostname or "").lower()


def database_host_kind(url: str) -> str:
    """Classify the DB host without leaking the hostname (safe for health responses)."""
    host = database_hostname(url)
    if not host or host in _LOCAL_HOSTS:
        return "local"
    if "." not in host:
        return "private"
    return "public"


def database_requires_ssl(url: str) -> bool:
    """Use TLS only for public hostnames. Render private DNS and Compose hosts do not."""
    return database_host_kind(url) == "public"


def database_ssl_connect_args(url: str) -> dict[str, object]:
    if database_requires_ssl(url):
        return {"ssl": True}
    return {}
