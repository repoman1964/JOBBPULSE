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


class TranscriptionStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class GenerationRunStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class GenerationType(str, enum.Enum):
    initial = "initial"
    regenerate = "regenerate"


class ContentType(str, enum.Enum):
    primary_social = "primary_social"
    short_caption = "short_caption"
    before_after = "before_after"
    directory_listing = "directory_listing"
    educational = "educational"


class ContentVariantStatus(str, enum.Enum):
    draft = "draft"
    awaiting_review = "awaiting_review"
    approved = "approved"
    rejected = "rejected"
    superseded = "superseded"


class DirectoryListingStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    unpublished = "unpublished"
    flagged = "flagged"
    removed = "removed"


class PublishingConnectionStatus(str, enum.Enum):
    active = "active"
    disconnected = "disconnected"
    error = "error"
    pending = "pending"


class PublicationDestinationType(str, enum.Enum):
    social = "social"
    directory = "directory"


class PublicationJobStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    published = "published"
    failed = "failed"
    cancelled = "cancelled"
    scheduled = "scheduled"


class NotificationChannel(str, enum.Enum):
    in_app = "in_app"
    email = "email"


class NotificationStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    read = "read"
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
    billing_customer_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    trial_ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
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
    contractor_profile: Mapped[Optional["ContractorProfile"]] = relationship(
        back_populates="company",
        uselist=False,
        cascade="all, delete-orphan",
    )
    publishing_connections: Mapped[list["PublishingConnection"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )


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
    voice_summary: Mapped[Optional["VoiceSummary"]] = relationship(
        back_populates="job",
        uselist=False,
        cascade="all, delete-orphan",
    )
    generation_runs: Mapped[list["GenerationRun"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
        foreign_keys="GenerationRun.job_id",
    )
    content_variants: Mapped[list["ContentVariant"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )
    structured_details: Mapped[Optional["JobStructuredDetails"]] = relationship(
        back_populates="job",
        uselist=False,
        cascade="all, delete-orphan",
    )
    directory_listing: Mapped[Optional["DirectoryListing"]] = relationship(
        back_populates="job",
        uselist=False,
        cascade="all, delete-orphan",
    )
    publication_jobs: Mapped[list["PublicationJob"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
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
    voice_summary: Mapped[Optional["VoiceSummary"]] = relationship(
        back_populates="audio_asset",
        uselist=False,
    )


class VoiceSummary(Base):
    """One current voice summary per job (MVP). Audio file lives in media_assets."""

    __tablename__ = "voice_summaries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    audio_asset_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("media_assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    transcript_raw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    transcript_edited: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(16), default="en", nullable=False)
    transcription_status: Mapped[TranscriptionStatus] = mapped_column(
        Enum(
            TranscriptionStatus,
            name="transcription_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=TranscriptionStatus.pending,
        index=True,
        nullable=False,
    )
    transcription_provider: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    transcription_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    job: Mapped[Job] = relationship(back_populates="voice_summary")
    audio_asset: Mapped[Optional[MediaAsset]] = relationship(
        back_populates="voice_summary",
        foreign_keys=[audio_asset_id],
    )


class GenerationRun(Base):
    """One AI generation attempt for a job (initial or regenerate)."""

    __tablename__ = "generation_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), index=True, nullable=False
    )
    requested_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[GenerationRunStatus] = mapped_column(
        Enum(
            GenerationRunStatus,
            name="generation_run_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=GenerationRunStatus.pending,
        index=True,
        nullable=False,
    )
    generation_type: Mapped[GenerationType] = mapped_column(
        Enum(
            GenerationType,
            name="generation_type",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=GenerationType.initial,
        nullable=False,
    )
    tone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    length_preference: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    user_instruction: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_provider: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    prompt_version: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    input_snapshot_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    output_snapshot_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    job: Mapped[Job] = relationship(
        back_populates="generation_runs",
        foreign_keys=[job_id],
    )
    variants: Mapped[list["ContentVariant"]] = relationship(
        back_populates="generation_run",
        cascade="all, delete-orphan",
    )


class ContentVariant(Base):
    """One draft marketing piece produced by a generation run."""

    __tablename__ = "content_variants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), index=True, nullable=False
    )
    generation_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("generation_runs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    content_type: Mapped[ContentType] = mapped_column(
        Enum(
            ContentType,
            name="content_type",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        index=True,
    )
    platform_target: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    body_generated: Mapped[str] = mapped_column(Text, nullable=False)
    body_edited: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    call_to_action: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    hashtags_json: Mapped[Optional[list[Any]]] = mapped_column(JSONB, nullable=True)
    status: Mapped[ContentVariantStatus] = mapped_column(
        Enum(
            ContentVariantStatus,
            name="content_variant_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=ContentVariantStatus.awaiting_review,
        index=True,
        nullable=False,
    )
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    job: Mapped[Job] = relationship(back_populates="content_variants")
    generation_run: Mapped[GenerationRun] = relationship(back_populates="variants")


class JobStructuredDetails(Base):
    """Latest structured extract for a job (upserted on each successful generation)."""

    __tablename__ = "job_structured_details"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    generation_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("generation_runs.id", ondelete="SET NULL"),
        nullable=True,
    )
    customer_problem: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    work_completed: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    materials: Mapped[Optional[list[Any]]] = mapped_column(JSONB, nullable=True)
    equipment: Mapped[Optional[list[Any]]] = mapped_column(JSONB, nullable=True)
    techniques: Mapped[Optional[list[Any]]] = mapped_column(JSONB, nullable=True)
    challenges: Mapped[Optional[list[Any]]] = mapped_column(JSONB, nullable=True)
    result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_text: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    customer_reaction: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    homeowner_advice: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    safety_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location_context: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    differentiators: Mapped[Optional[list[Any]]] = mapped_column(JSONB, nullable=True)
    confidence_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    source_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    job: Mapped[Job] = relationship(back_populates="structured_details")


class ContractorProfile(Base):
    """Public contractor profile for the JobPulse directory (one per company)."""

    __tablename__ = "contractor_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    public_slug: Mapped[str] = mapped_column(String(220), unique=True, index=True, nullable=False)
    headline: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    public_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    lead_form_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    featured: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    seo_title: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    seo_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    company: Mapped[Company] = relationship(back_populates="contractor_profile")
    listings: Mapped[list["DirectoryListing"]] = relationship(back_populates="contractor_profile")
    leads: Mapped[list["DirectoryLead"]] = relationship(back_populates="contractor_profile")


class DirectoryListing(Base):
    """Public project page derived from an approved Job."""

    __tablename__ = "directory_listings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    contractor_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contractor_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True, nullable=False)
    public_title: Mapped[str] = mapped_column(String(300), nullable=False)
    public_summary: Mapped[str] = mapped_column(Text, nullable=False)
    service_key: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    location_display: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(150), index=True, nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status: Mapped[DirectoryListingStatus] = mapped_column(
        Enum(
            DirectoryListingStatus,
            name="directory_listing_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=DirectoryListingStatus.draft,
        index=True,
        nullable=False,
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    unpublished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    featured: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    seo_title: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    seo_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    structured_data_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    job: Mapped[Job] = relationship(back_populates="directory_listing")
    contractor_profile: Mapped[ContractorProfile] = relationship(back_populates="listings")
    media_links: Mapped[list["DirectoryListingMedia"]] = relationship(
        back_populates="listing",
        cascade="all, delete-orphan",
        order_by="DirectoryListingMedia.display_order",
    )
    leads: Mapped[list["DirectoryLead"]] = relationship(back_populates="source_project")


class DirectoryListingMedia(Base):
    """Media assets linked to a public directory listing (before/after gallery)."""

    __tablename__ = "directory_listing_media"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    directory_listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("directory_listings.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    media_asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("media_assets.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    stage_label: Mapped[str] = mapped_column(String(40), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    listing: Mapped[DirectoryListing] = relationship(back_populates="media_links")
    media_asset: Mapped[MediaAsset] = relationship()


class DirectoryLeadStatus(str, enum.Enum):
    new = "new"
    contacted = "contacted"
    booked = "booked"
    won = "won"
    lost = "lost"
    spam = "spam"


class DirectoryLead(Base):
    """Homeowner inquiry routed to a contractor from a public portfolio page."""

    __tablename__ = "directory_leads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contractor_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contractor_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    source_project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("directory_listings.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    source_page_type: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    source_page_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    project_location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    service_requested: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preferred_contact_method: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    lead_status: Mapped[DirectoryLeadStatus] = mapped_column(
        Enum(
            DirectoryLeadStatus,
            name="directory_lead_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=DirectoryLeadStatus.new,
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    contractor_profile: Mapped[ContractorProfile] = relationship(back_populates="leads")
    source_project: Mapped[Optional[DirectoryListing]] = relationship(back_populates="leads")


class PublishingConnection(Base):
    """Connected social account for a company (via PUBLISHING_PROVIDER)."""

    __tablename__ = "publishing_connections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    provider: Mapped[str] = mapped_column(String(40), nullable=False, default="mock")
    platform: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    external_account_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    credentials_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[PublishingConnectionStatus] = mapped_column(
        Enum(
            PublishingConnectionStatus,
            name="publishing_connection_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=PublishingConnectionStatus.pending,
        index=True,
        nullable=False,
    )
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    company: Mapped[Company] = relationship(back_populates="publishing_connections")
    publication_jobs: Mapped[list["PublicationJob"]] = relationship(back_populates="connection")


class PublicationJob(Base):
    """One publication attempt to social or directory (audit + retry)."""

    __tablename__ = "publication_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), index=True, nullable=False
    )
    content_variant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("content_variants.id", ondelete="SET NULL"),
        nullable=True,
    )
    destination_type: Mapped[PublicationDestinationType] = mapped_column(
        Enum(
            PublicationDestinationType,
            name="publication_destination_type",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        index=True,
    )
    publishing_connection_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("publishing_connections.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    provider: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    scheduled_for: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[PublicationJobStatus] = mapped_column(
        Enum(
            PublicationJobStatus,
            name="publication_job_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=PublicationJobStatus.pending,
        index=True,
        nullable=False,
    )
    idempotency_key: Mapped[str] = mapped_column(String(300), unique=True, index=True, nullable=False)
    provider_request_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    provider_response_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    external_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    job: Mapped[Job] = relationship(back_populates="publication_jobs")
    connection: Mapped[Optional[PublishingConnection]] = relationship(back_populates="publication_jobs")
    content_variant: Mapped[Optional[ContentVariant]] = relationship()


class Notification(Base):
    """In-app (and stub email) notifications for contractors."""

    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[NotificationChannel] = mapped_column(
        Enum(
            NotificationChannel,
            name="notification_channel",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=NotificationChannel.in_app,
        nullable=False,
    )
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(
            NotificationStatus,
            name="notification_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=NotificationStatus.pending,
        index=True,
        nullable=False,
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class AuditEvent(Base):
    """Immutable-ish audit trail for sensitive contractor actions."""

    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    entity_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    before_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    after_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True, nullable=False
    )
