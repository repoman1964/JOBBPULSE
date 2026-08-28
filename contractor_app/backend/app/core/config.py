"""Application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.database_url import normalize_database_url


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
    auth_show_otp: bool = False
    auth_challenge_ttl_minutes: int = 10
    auth_fixed_dev_code: str = "123456"
    auth_verification_ttl_hours: int = 24
    resend_api_key: str | None = None
    auth_from_email: str = "JobbPulse <onboarding@resend.dev>"
    public_api_base_url: str = "http://localhost:8000"

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

    # CORS — demo site on Cloudflare Pages, contractor UI on Render
    cors_origins: str = (
        "http://localhost:3000,http://localhost:3002,http://127.0.0.1:3002,"
        "https://jobbpulse-app.onrender.com,https://red-clay-website.pages.dev"
    )

    # Frontend (deep links, Upload-Post redirect)
    frontend_base_url: str = "http://localhost:3000"

    # Providers
    provider_mode: Literal["fake", "live"] = "fake"
    # Simulated pipeline pacing so the contractor app can poll stages.
    # 0 disables pauses (tests). Demo and production use the same stages.
    pipeline_stage_delay_seconds: float = 2.5
    upload_post_api_key: str | None = None
    upload_post_base_url: str = "https://api.upload-post.com/api"
    upload_post_webhook_token: str | None = None

    conversion_site_api_url: str | None = None
    portfolio_site_api_url: str | None = None

    # Rate limits (simple defaults)
    auth_challenge_rate_per_minute: int = 10

    @property
    def cors_origin_list(self) -> list[str]:
        extras = (
            "https://jobbpulse-app.onrender.com",
            "https://red-clay-website.pages.dev",
        )
        seen: list[str] = []
        for origin in [*self.cors_origins.split(","), *extras]:
            value = origin.strip()
            if value and value not in seen:
                seen.append(value)
        return seen

    @property
    def return_otp_to_client(self) -> bool:
        """Show the one-time code in the API response. No email/SMS is sent."""
        if self.auth_show_otp:
            return True
        return self.auth_dev_codes and not self.is_production

    @property
    def return_verification_url_to_client(self) -> bool:
        """Expose the email-verify URL in API responses (local/dev only)."""
        return self.auth_dev_codes and not self.is_production

    @property
    def cors_origin_regex(self) -> str | None:
        """Allow any localhost / private-LAN origin in non-production (Nuxt QR, extra ports)."""
        if self.is_production:
            return None
        return (
            r"^https?://("
            r"localhost|127\.0\.0\.1|\[::1\]|"
            r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
            r"192\.168\.\d{1,3}\.\d{1,3}|"
            r"172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}"
            r")(:\d+)?$"
        )

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @field_validator("auth_dev_codes", "auth_show_otp", mode="before")
    @classmethod
    def _coerce_bool(cls, v: object) -> bool:
        if isinstance(v, str):
            return v.lower() in {"1", "true", "yes", "on"}
        return bool(v)

    @field_validator("resend_api_key", mode="before")
    @classmethod
    def _empty_secret_to_none(cls, v: object) -> object:
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @field_validator("database_url")
    @classmethod
    def _asyncpg_database_url(cls, v: str) -> str:
        return normalize_database_url(v)

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
