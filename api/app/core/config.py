"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    app_name: str = "JobPulse API"
    app_version: str = "0.1.0"
    app_secret_key: str = "dev-secret-change-me"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://jobpulse:jobpulse@localhost:5433/jobpulse"
    redis_url: str = "redis://localhost:6380/0"

    s3_endpoint: str = "http://localhost:9000"
    s3_bucket: str = "jobpulse"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_public_base_url: str = "http://localhost:9000/jobpulse"
    s3_region: str = "us-east-1"

    jwt_secret: str = "dev-jwt-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14

    frontend_url: str = "http://localhost:3000"
    directory_url: str = "http://localhost:3001"
    cors_origins: str = "http://localhost:3000,http://localhost:3001"

    ai_provider: str = "mock"
    publishing_provider: str = "mock"
    publishing_api_key: str = ""
    transcription_provider: str = "mock"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
