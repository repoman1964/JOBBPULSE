"""Application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["development", "staging", "production"] = "development"
    app_name: str = "JobbPulse Engine"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    # Auth
    jwt_secret: str = Field(default="dev-only-change-me-in-production-use-32b+")
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 30
    refresh_token_ttl_days: int = 30
    auth_dev_codes: bool = True
    auth_challenge_ttl_minutes: int = 10
    auth_fixed_dev_code: str = "123456"

    # Cookies
    refresh_cookie_name: str = "jp_refresh"
    cookie_secure: bool = False
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    cookie_domain: str | None = None

    # Database
    database_url: str = (
        "postgresql+asyncpg://jobbpulse:jobbpulse@localhost:5432/jobbpulse"
    )

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Object storage (S3 / MinIO)
    s3_endpoint_url: str = "http://localhost:9000"
    s3_public_endpoint_url: str | None = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "jobbpulse"
    s3_region: str = "us-east-1"
    upload_url_ttl_seconds: int = 900
    download_url_ttl_seconds: int = 3600

    # CORS
    cors_origins: str = "http://localhost:3000"

    # Frontend (deep links, Upload-Post redirect)
    frontend_base_url: str = "http://localhost:3000"

    # Providers
    provider_mode: Literal["fake", "live"] = "fake"
    upload_post_api_key: str | None = None
    upload_post_base_url: str = "https://api.upload-post.com/api"
    upload_post_webhook_token: str | None = None

    conversion_site_api_url: str | None = None
    portfolio_site_api_url: str | None = None

    # Rate limits (simple defaults)
    auth_challenge_rate_per_minute: int = 10

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @field_validator("auth_dev_codes")
    @classmethod
    def _coerce_bool(cls, v: object) -> bool:
        if isinstance(v, str):
            return v.lower() in {"1", "true", "yes", "on"}
        return bool(v)

    @model_validator(mode="after")
    def _guard_dev_auth(self) -> Settings:
        if self.is_production and self.auth_dev_codes:
            raise ValueError(
                "AUTH_DEV_CODES cannot be enabled when APP_ENV=production"
            )
        if self.is_production and self.jwt_secret.startswith("dev-only"):
            raise ValueError("JWT_SECRET must be set to a strong secret in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
