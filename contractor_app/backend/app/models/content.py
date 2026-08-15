"""Content packages, generated assets, versions, and revision requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AssetStatus, PackageStatus, RevisionStatus

if TYPE_CHECKING:
    from app.models.job import Job


class ContentPackage(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "content_packages"
    __table_args__ = (
        UniqueConstraint("job_id", "version", name="uq_content_package_job_version"),
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
    submission_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("job_submissions.id", ondelete="SET NULL"),
        nullable=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=PackageStatus.generating.value
    )
    project_description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    featured_before_media_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("media_assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    featured_after_media_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("media_assets.id", ondelete="SET NULL"),
        nullable=True,
    )

    job: Mapped[Job] = relationship(back_populates="packages")
    assets: Mapped[list[GeneratedAsset]] = relationship(back_populates="package")


class GeneratedAsset(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "generated_assets"
    __table_args__ = (
        UniqueConstraint(
            "package_id", "destination_type", name="uq_generated_asset_package_dest"
        ),
    )

    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    package_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("content_packages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    destination_type: Mapped[str] = mapped_column(String(32), nullable=False)
    destination_account_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    preview_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=AssetStatus.ready.value
    )
    active_version_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "generated_asset_versions.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_generated_assets_active_version",
        ),
        nullable=True,
    )

    package: Mapped[ContentPackage] = relationship(back_populates="assets")
    versions: Mapped[list[GeneratedAssetVersion]] = relationship(
        back_populates="asset",
        foreign_keys="GeneratedAssetVersion.generated_asset_id",
    )


class GeneratedAssetVersion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "generated_asset_versions"
    __table_args__ = (
        UniqueConstraint(
            "generated_asset_id", "version", name="uq_generated_asset_version_num"
        ),
    )

    generated_asset_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("generated_assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    source_media_ids_json: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    title: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    preview_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    generation_metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )

    asset: Mapped[GeneratedAsset] = relationship(
        back_populates="versions",
        foreign_keys=[generated_asset_id],
    )


class RevisionRequest(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "revision_requests"

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
    generated_asset_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("generated_assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    change_type: Mapped[str] = mapped_column(String(32), nullable=False)
    instruction_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    instruction_audio_media_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("media_assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    selected_media_ids_json: Mapped[list[Any] | None] = mapped_column(JSONB, nullable=True)
    transcribed_instruction: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=RevisionStatus.pending.value
    )
    requested_by_contractor_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("contractors.id", ondelete="RESTRICT"),
        nullable=False,
    )
