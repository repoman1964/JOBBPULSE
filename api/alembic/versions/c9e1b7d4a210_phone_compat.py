"""contractor phone compatibility columns

Revision ID: c9e1b7d4a210
Revises: b9d1f6e2a470
Create Date: 2026-08-29

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c9e1b7d4a210"
down_revision: Union[str, Sequence[str], None] = "b9d1f6e2a470"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    for value in ("publishing", "publish_issue"):
        bind.execute(sa.text(f"ALTER TYPE job_status ADD VALUE IF NOT EXISTS '{value}'"))

    op.add_column("companies", sa.Column("contact_name", sa.String(length=200), nullable=True))
    op.add_column("companies", sa.Column("email", sa.String(length=320), nullable=True))
    op.add_column("companies", sa.Column("service_area", sa.String(length=300), nullable=True))
    op.add_column("companies", sa.Column("photo_minimums_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("companies", sa.Column("photo_maximums_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column(
        "companies",
        sa.Column("notification_settings_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column("companies", sa.Column("facebook_group_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    op.add_column("jobs", sa.Column("assigned_crew_member", sa.String(length=200), nullable=True))
    op.add_column("jobs", sa.Column("featured_before_media_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("jobs", sa.Column("featured_after_media_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("jobs", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_jobs_deleted_at", "jobs", ["deleted_at"])

    op.add_column("media_assets", sa.Column("is_favorite", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("media_assets", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    op.create_table(
        "job_submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(length=40), nullable=False),
        sa.Column("idempotency_key", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="completed"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("job_id", "kind", "idempotency_key", name="uq_job_submission_idempotency"),
    )
    op.create_index("ix_job_submissions_job_id", "job_submissions", ["job_id"])
    op.create_index("ix_job_submissions_company_id", "job_submissions", ["company_id"])
    op.create_index("ix_job_submissions_kind", "job_submissions", ["kind"])


def downgrade() -> None:
    op.drop_table("job_submissions")
    op.drop_column("media_assets", "deleted_at")
    op.drop_column("media_assets", "is_favorite")
    op.drop_index("ix_jobs_deleted_at", table_name="jobs")
    op.drop_column("jobs", "deleted_at")
    op.drop_column("jobs", "featured_after_media_id")
    op.drop_column("jobs", "featured_before_media_id")
    op.drop_column("jobs", "assigned_crew_member")
    op.drop_column("companies", "facebook_group_ids")
    op.drop_column("companies", "notification_settings_json")
    op.drop_column("companies", "photo_maximums_json")
    op.drop_column("companies", "photo_minimums_json")
    op.drop_column("companies", "service_area")
    op.drop_column("companies", "email")
    op.drop_column("companies", "contact_name")
