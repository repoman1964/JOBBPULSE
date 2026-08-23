"""Jobs, submissions, and job audit events."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import InternalJobStatus, PublicJobStatus

if TYPE_CHECKING:
    from app.models.company import Company, Contractor
    from app.models.content import ContentPackage
    from app.models.media import MediaAsset


class Job(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "jobs"

    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by_contractor_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("contractors.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    service_type: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(128), nullable=False)
    region: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    location_text: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    internal_note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    assigned_crew_member: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    public_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=PublicJobStatus.active.value, index=True
    )
    internal_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=InternalJobStatus.draft.value
    )
    submission_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cover_object_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    company: Mapped[Company] = relationship(back_populates="jobs")
    media_assets: Mapped[list[MediaAsset]] = relationship(back_populates="job")
    packages: Mapped[list[ContentPackage]] = relationship(back_populates="job")
    events: Mapped[list[JobEvent]] = relationship(back_populates="job")
    submissions: Mapped[list[JobSubmission]] = relationship(back_populates="job")


class JobSubmission(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "job_submissions"
    __table_args__ = (
        UniqueConstraint("job_id", "idempotency_key", name="uq_job_submission_idempotency"),
        UniqueConstraint("job_id", "version", name="uq_job_submission_version"),
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
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    voice_media_asset_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("media_assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    snapshot_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    submitted_by_contractor_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("contractors.id", ondelete="RESTRICT"),
        nullable=False,
    )

    job: Mapped[Job] = relationship(back_populates="submissions")


class JobEvent(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "job_events"

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
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    actor_type: Mapped[str] = mapped_column(String(32), nullable=False)  # contractor|system|worker
    actor_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    job: Mapped[Job] = relationship(back_populates="events")
