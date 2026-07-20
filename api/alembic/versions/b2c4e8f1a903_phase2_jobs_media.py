"""phase2_jobs_media

Revision ID: b2c4e8f1a903
Revises: 3579c479178b
Create Date: 2026-07-20 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b2c4e8f1a903"
down_revision: Union[str, Sequence[str], None] = "3579c479178b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

job_status = postgresql.ENUM(
    "draft",
    "before_photos_added",
    "work_in_progress",
    "ready_for_summary",
    "ready_to_generate",
    "generating",
    "awaiting_review",
    "revision_requested",
    "approved",
    "scheduled",
    "published",
    "failed",
    "archived",
    name="job_status",
    create_type=False,
)

media_asset_type = postgresql.ENUM(
    "image",
    "audio",
    "video",
    "document",
    name="media_asset_type",
    create_type=False,
)

media_stage_label = postgresql.ENUM(
    "before",
    "progress",
    "after",
    "unclassified",
    name="media_stage_label",
    create_type=False,
)

media_processing_status = postgresql.ENUM(
    "pending_upload",
    "uploaded",
    "processing",
    "ready",
    "failed",
    name="media_processing_status",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    job_status.create(bind, checkfirst=True)
    media_asset_type.create(bind, checkfirst=True)
    media_stage_label.create(bind, checkfirst=True)
    media_processing_status.create(bind, checkfirst=True)

    op.create_table(
        "jobs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("service_key", sa.String(length=100), nullable=True),
        sa.Column("location_display", sa.String(length=200), nullable=True),
        sa.Column("city", sa.String(length=150), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("postal_code", sa.String(length=20), nullable=True),
        sa.Column("customer_name_private", sa.String(length=200), nullable=True),
        sa.Column(
            "customer_consent_status",
            sa.String(length=40),
            nullable=False,
            server_default="unknown",
        ),
        sa.Column("status", job_status, nullable=False, server_default="draft"),
        sa.Column("job_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("job_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "privacy_mode",
            sa.String(length=40),
            nullable=False,
            server_default="city_only",
        ),
        sa.Column(
            "generation_version",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("latest_generation_run_id", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_jobs_city"), "jobs", ["city"], unique=False)
    op.create_index(op.f("ix_jobs_company_id"), "jobs", ["company_id"], unique=False)
    op.create_index(op.f("ix_jobs_created_by"), "jobs", ["created_by"], unique=False)
    op.create_index(op.f("ix_jobs_service_key"), "jobs", ["service_key"], unique=False)
    op.create_index(op.f("ix_jobs_state"), "jobs", ["state"], unique=False)
    op.create_index(op.f("ix_jobs_status"), "jobs", ["status"], unique=False)

    op.create_table(
        "media_assets",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("job_id", sa.UUID(), nullable=False),
        sa.Column("uploaded_by", sa.UUID(), nullable=True),
        sa.Column("storage_key", sa.String(length=500), nullable=False),
        sa.Column("original_filename", sa.String(length=300), nullable=True),
        sa.Column("mime_type", sa.String(length=100), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("asset_type", media_asset_type, nullable=False),
        sa.Column("stage_label", media_stage_label, nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "processing_status",
            media_processing_status,
            nullable=False,
            server_default="pending_upload",
        ),
        sa.Column(
            "moderation_status",
            sa.String(length=40),
            nullable=False,
            server_default="unreviewed",
        ),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_media_assets_company_id"), "media_assets", ["company_id"], unique=False)
    op.create_index(op.f("ix_media_assets_job_id"), "media_assets", ["job_id"], unique=False)
    op.create_index(op.f("ix_media_assets_stage_label"), "media_assets", ["stage_label"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_media_assets_stage_label"), table_name="media_assets")
    op.drop_index(op.f("ix_media_assets_job_id"), table_name="media_assets")
    op.drop_index(op.f("ix_media_assets_company_id"), table_name="media_assets")
    op.drop_table("media_assets")
    op.drop_index(op.f("ix_jobs_status"), table_name="jobs")
    op.drop_index(op.f("ix_jobs_state"), table_name="jobs")
    op.drop_index(op.f("ix_jobs_service_key"), table_name="jobs")
    op.drop_index(op.f("ix_jobs_created_by"), table_name="jobs")
    op.drop_index(op.f("ix_jobs_company_id"), table_name="jobs")
    op.drop_index(op.f("ix_jobs_city"), table_name="jobs")
    op.drop_table("jobs")

    media_processing_status.drop(op.get_bind(), checkfirst=True)
    media_stage_label.drop(op.get_bind(), checkfirst=True)
    media_asset_type.drop(op.get_bind(), checkfirst=True)
    job_status.drop(op.get_bind(), checkfirst=True)
