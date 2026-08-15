"""Social profiles, connections, publications, and webhooks."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import PublicationStatus, SocialConnectionStatus, WebhookProcessingStatus


class SocialProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "social_profiles"
    __table_args__ = (
        UniqueConstraint("company_id", "provider", name="uq_social_profile_company_provider"),
    )

    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(64), nullable=False, default="upload_post")
    provider_username: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")

    connections: Mapped[list[SocialConnection]] = relationship(back_populates="profile")


class SocialConnection(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "social_connections"
    __table_args__ = (
        UniqueConstraint(
            "company_id", "platform", name="uq_social_connection_company_platform"
        ),
    )

    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    social_profile_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("social_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform: Mapped[str] = mapped_column(String(32), nullable=False)
    provider_account_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider_account_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=SocialConnectionStatus.not_connected.value,
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_event_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    profile: Mapped[SocialProfile] = relationship(back_populates="connections")


class PublicationAttempt(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "publication_attempts"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_publication_idempotency"),
    )

    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    generated_asset_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("generated_assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    destination_type: Mapped[str] = mapped_column(String(32), nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    provider_request_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider_job_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=PublicationStatus.pending.value
    )
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    request_snapshot_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    response_snapshot_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    last_error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class WebhookEvent(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "webhook_events"
    __table_args__ = (
        UniqueConstraint(
            "provider", "provider_event_id", name="uq_webhook_provider_event"
        ),
    )

    provider: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    provider_event_id: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=WebhookProcessingStatus.received.value,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
