"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_env: str = "development"
    app_name: str = "JobPulse API"
    app_version: str = "0.1.0"
    app_secret_key: str = "dev-secret-change-me"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://jobpulse:jobpulse@localhost:5433/jobpulse"
    redis_url: str = "redis://localhost:6380/0"
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None

    s3_endpoint: str = Field(
        default="http://localhost:9000",
        validation_alias=AliasChoices("S3_ENDPOINT", "S3_ENDPOINT_URL"),
    )
    s3_bucket: str = "jobpulse"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_public_base_url: str = Field(
        default="http://localhost:9000/jobpulse",
        validation_alias=AliasChoices("S3_PUBLIC_BASE_URL", "S3_PUBLIC_ENDPOINT_URL"),
    )
    s3_region: str = "us-east-1"

    jwt_secret: str = "dev-jwt-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14
    auth_password_reset_ttl_hours: int = 1
    auth_challenge_rate_per_minute: int = 10

    frontend_url: str = Field(
        default="http://localhost:3000",
        validation_alias=AliasChoices("FRONTEND_URL", "FRONTEND_BASE_URL"),
    )
    directory_url: str = "http://localhost:3001"
    cors_origins: str = (
        "http://localhost:3000,http://localhost:3001,http://localhost:3002,"
        "http://localhost:3003,http://127.0.0.1:3000,http://127.0.0.1:3001,"
        "http://127.0.0.1:3002,http://127.0.0.1:3003"
    )

    ai_provider: str = "mock"
    publishing_provider: str = "mock"
    publishing_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("PUBLISHING_API_KEY", "UPLOAD_POST_API_KEY"),
    )
    upload_post_base_url: str = "https://api.upload-post.com/api"
    transcription_provider: str = "mock"

    # Phase 8 — pilot hardening
    sentry_dsn: str = ""
    billing_enforce: bool = False
    founder_admin_emails: str = ""  # comma-separated platform admin emails
    stripe_webhook_secret: str = ""  # optional; verify when set

    # Contractor-app compatibility
    return_verification_url_to_client: bool = True
    email_from: str = Field(
        default="JobbPulse <noreply@localhost>",
        validation_alias=AliasChoices("EMAIL_FROM", "AUTH_FROM_EMAIL"),
    )
    resend_api_key: str | None = None

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def founder_admin_email_set(self) -> set[str]:
        return {
            e.strip().lower()
            for e in self.founder_admin_emails.split(",")
            if e.strip()
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
