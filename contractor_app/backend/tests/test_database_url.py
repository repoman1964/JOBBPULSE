from app.core.database_url import (
    database_host_kind,
    database_requires_ssl,
    database_ssl_connect_args,
    normalize_database_url,
)


def test_render_internal_url_is_asyncpg_without_ssl() -> None:
    raw = "postgresql://jobbpulse:secret@dpg-abc123-a/jobbpulse"
    out = normalize_database_url(raw)
    assert out.startswith("postgresql+asyncpg://")
    assert "ssl=" not in out
    assert "jobbpulse:secret@dpg-abc123-a/jobbpulse" in out
    assert database_host_kind(raw) == "private"
    assert database_requires_ssl(raw) is False
    assert database_ssl_connect_args(raw) == {}


def test_render_external_url_uses_connect_args_ssl() -> None:
    raw = (
        "postgres://u:p@dpg-abc123-a.oregon-postgres.render.com:5432/app"
        "?sslmode=require"
    )
    out = normalize_database_url(raw)
    assert out.startswith("postgresql+asyncpg://")
    assert "sslmode" not in out
    assert "ssl=" not in out
    assert database_host_kind(raw) == "public"
    assert database_requires_ssl(raw) is True
    assert database_ssl_connect_args(raw) == {"ssl": True}


def test_local_urls_keep_asyncpg_without_ssl() -> None:
    raw = "postgresql+asyncpg://jobbpulse:jobbpulse@localhost:5433/jobbpulse"
    assert normalize_database_url(raw) == raw
    assert database_host_kind(raw) == "local"
    assert database_ssl_connect_args(raw) == {}

    compose = "postgresql://jobbpulse:jobbpulse@postgres:5432/jobbpulse"
    out = normalize_database_url(compose)
    assert out == "postgresql+asyncpg://jobbpulse:jobbpulse@postgres:5432/jobbpulse"
    assert "ssl=" not in out
    assert database_host_kind(compose) == "local"
    assert database_ssl_connect_args(compose) == {}
