"""SQLAlchemy ORM models for JobPulse foundation + job capture."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MembershipRole(str, enum.Enum):
    owner = "owner"
    manager = "manager"
    crew = "crew"


class MembershipStatus(str, enum.Enum):
    active = "active"
    invited = "invited"
    disabled = "disabled"


class JobStatus(str, enum.Enum):
    draft = "draft"
    before_photos_added = "before_photos_added"
    work_in_progress = "work_in_progress"
    ready_for_summary = "ready_for_summary"
    ready_to_generate = "ready_to_generate"
    generating = "generating"
    awaiting_review = "awaiting_review"
    revision_requested = "revision_requested"
    approved = "approved"
    scheduled = "scheduled"
    published = "published"
    failed = "failed"
    archived = "archived"


class MediaAssetType(str, enum.Enum):
    image = "image"
    audio = "audio"
    video = "video"
    document = "document"


class MediaStageLabel(str, enum.Enum):
    before = "before"
    progress = "progress"
    after = "after"
    unclassified = "unclassified"


class MediaProcessingStatus(str, enum.Enum):
    pending_upload = "pending_upload"
    uploaded = "uploaded"
    processing = "processing"
    ready = "ready"
    failed = "failed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    memberships: Mapped[list[CompanyMembership]] = relationship(back_populates="user")


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True, nullable=False)
    trade: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    default_tone: Mapped[str] = mapped_column(String(50), default="friendly_local", nullable=False)
    default_call_to_action: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    subscription_status: Mapped[str] = mapped_column(
        String(40), default="trial", index=True, nullable=False
    )
    subscription_plan: Mapped[str] = mapped_column(String(40), default="core", nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="America/New_York", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    memberships: Mapped[list[CompanyMembership]] = relationship(back_populates="company")
    services: Mapped[list[CompanyService]] = relationship(back_populates="company")
    service_areas: Mapped[list[CompanyServiceArea]] = relationship(back_populates="company")
    jobs: Mapped[list["Job"]] = relationship(back_populates="company")


class CompanyMembership(Base):
    __tablename__ = "company_memberships"
    __table_args__ = (UniqueConstraint("company_id", "user_id", name="uq_company_user"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role: Mapped[MembershipRole] = mapped_column(
        Enum(MembershipRole, name="membership_role", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    status: Mapped[MembershipStatus] = mapped_column(
        Enum(
            MembershipStatus,
            name="membership_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=MembershipStatus.active,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    company: Mapped[Company] = relationship(back_populates="memberships")
    user: Mapped[User] = relationship(back_populates="memberships")


class CompanyService(Base):
    __tablename__ = "company_services"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    service_key: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    company: Mapped[Company] = relationship(back_populates="services")


class CompanyServiceArea(Base):
    __tablename__ = "company_service_areas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    country_code: Mapped[str] = mapped_column(String(2), default="US", nullable=False)
    state: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    metro_area: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(150), index=True, nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), index=True, nullable=True)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    company: Mapped[Company] = relationship(back_populates="service_areas")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, default="Untitled Job")
    service_key: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    location_display: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(150), index=True, nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    customer_name_private: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    customer_consent_status: Mapped[str] = mapped_column(
        String(40), default="unknown", nullable=False
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status", values_callable=lambda x: [e.value for e in x]),
        default=JobStatus.draft,
        index=True,
        nullable=False,
    )
    job_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    job_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    privacy_mode: Mapped[str] = mapped_column(String(40), default="city_only", nullable=False)
    generation_version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    latest_generation_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    company: Mapped[Company] = relationship(back_populates="jobs")
    creator: Mapped[Optional[User]] = relationship(foreign_keys=[created_by])
    media_assets: Mapped[list["MediaAsset"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class MediaAsset(Base):
    __tablename__ = "media_assets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), index=True, nullable=False
    )
    uploaded_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    asset_type: Mapped[MediaAssetType] = mapped_column(
        Enum(MediaAssetType, name="media_asset_type", values_callable=lambda x: [e.value for e in x]),
        default=MediaAssetType.image,
        nullable=False,
    )
    stage_label: Mapped[MediaStageLabel] = mapped_column(
        Enum(
            MediaStageLabel,
            name="media_stage_label",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=MediaStageLabel.unclassified,
        index=True,
        nullable=False,
    )
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    processing_status: Mapped[MediaProcessingStatus] = mapped_column(
        Enum(
            MediaProcessingStatus,
            name="media_processing_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=MediaProcessingStatus.pending_upload,
        nullable=False,
    )
    moderation_status: Mapped[str] = mapped_column(String(40), default="unreviewed", nullable=False)
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    job: Mapped[Job] = relationship(back_populates="media_assets")
