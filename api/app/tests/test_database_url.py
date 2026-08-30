from app.core.config import Settings, normalize_database_url


def test_normalize_render_postgres_url() -> None:
    assert (
        normalize_database_url("postgres://u:p@host:5432/db")
        == "postgresql+asyncpg://u:p@host:5432/db"
    )
    assert (
        normalize_database_url("postgresql://u:p@host/db")
        == "postgresql+asyncpg://u:p@host/db"
    )
    assert (
        normalize_database_url("postgresql+asyncpg://u:p@host/db")
        == "postgresql+asyncpg://u:p@host/db"
    )


def test_settings_rewrites_database_url() -> None:
    settings = Settings(database_url="postgres://jobbpulse:x@dpg-host/jobbpulse")
    assert settings.database_url.startswith("postgresql+asyncpg://")
