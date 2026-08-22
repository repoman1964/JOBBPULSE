from app.core.database_url import normalize_database_url


def test_render_postgres_url_becomes_asyncpg_with_ssl() -> None:
    raw = "postgresql://jobbpulse:secret@dpg-abc123-a/jobbpulse"
    out = normalize_database_url(raw)
    assert out.startswith("postgresql+asyncpg://")
    assert "ssl=require" in out
    assert "jobbpulse:secret@dpg-abc123-a/jobbpulse" in out


def test_postgres_scheme_and_sslmode_are_converted() -> None:
    raw = "postgres://u:p@db.example.com:5432/app?sslmode=require"
    out = normalize_database_url(raw)
    assert out.startswith("postgresql+asyncpg://")
    assert "ssl=require" in out
    assert "sslmode" not in out


def test_local_urls_keep_asyncpg_without_ssl() -> None:
    raw = "postgresql+asyncpg://jobbpulse:jobbpulse@localhost:5433/jobbpulse"
    assert normalize_database_url(raw) == raw

    compose = "postgresql://jobbpulse:jobbpulse@postgres:5432/jobbpulse"
    out = normalize_database_url(compose)
    assert out == "postgresql+asyncpg://jobbpulse:jobbpulse@postgres:5432/jobbpulse"
    assert "ssl=" not in out
