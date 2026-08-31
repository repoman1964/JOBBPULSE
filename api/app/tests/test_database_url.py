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


def test_cors_always_includes_custom_app_domain() -> None:
    settings = Settings(cors_origins="https://jobbpulse-app.onrender.com")
    assert "https://app.jobbpulse.com" in settings.cors_origin_list
    assert "https://jobbpulse-app.onrender.com" in settings.cors_origin_list
    assert "https://demo.jobbpulse.com" in settings.cors_origin_list
    assert "https://red-clay-website.pages.dev" in settings.cors_origin_list
    assert "http://localhost:3002" in settings.cors_origin_list
