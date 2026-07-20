"""phase7_publishing_connections_publication_jobs

Revision ID: f6a8c2d5e147
Revises: e5f7b1c4d036
Create Date: 2026-07-20 20:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f6a8c2d5e147"
down_revision: Union[str, Sequence[str], None] = "e5f7b1c4d036"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

publishing_connection_status = postgresql.ENUM(
    "active",
    "disconnected",
    "error",
    "pending",
    name="publishing_connection_status",
    create_type=False,
)
publication_destination_type = postgresql.ENUM(
    "social",
    "directory",
    name="publication_destination_type",
    create_type=False,
)
publication_job_status = postgresql.ENUM(
    "pending",
    "processing",
    "published",
    "failed",
    "cancelled",
    "scheduled",
    name="publication_job_status",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    publishing_connection_status.create(bind, checkfirst=True)
    publication_destination_type.create(bind, checkfirst=True)
    publication_job_status.create(bind, checkfirst=True)

    op.create_table(
        "publishing_connections",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("provider", sa.String(length=40), server_default="mock", nullable=False),
        sa.Column("platform", sa.String(length=40), nullable=False),
        sa.Column("external_account_id", sa.String(length=200), nullable=True),
        sa.Column("display_name", sa.String(length=200), nullable=False),
        sa.Column("credentials_encrypted", sa.Text(), nullable=True),
        sa.Column(
            "status",
            publishing_connection_status,
            server_default="pending",
            nullable=False,
        ),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_publishing_connections_company_id", "publishing_connections", ["company_id"])
    op.create_index("ix_publishing_connections_platform", "publishing_connections", ["platform"])
    op.create_index("ix_publishing_connections_status", "publishing_connections", ["status"])

    op.create_table(
        "publication_jobs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("job_id", sa.UUID(), nullable=False),
        sa.Column("content_variant_id", sa.UUID(), nullable=True),
        sa.Column("destination_type", publication_destination_type, nullable=False),
        sa.Column("publishing_connection_id", sa.UUID(), nullable=True),
        sa.Column("provider", sa.String(length=40), nullable=True),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            publication_job_status,
            server_default="pending",
            nullable=False,
        ),
        sa.Column("idempotency_key", sa.String(length=300), nullable=False),
        sa.Column("provider_request_id", sa.String(length=200), nullable=True),
        sa.Column("provider_response_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("external_url", sa.String(length=500), nullable=True),
        sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["content_variant_id"], ["content_variants.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["publishing_connection_id"], ["publishing_connections.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_index("ix_publication_jobs_job_id", "publication_jobs", ["job_id"])
    op.create_index("ix_publication_jobs_destination_type", "publication_jobs", ["destination_type"])
    op.create_index(
        "ix_publication_jobs_publishing_connection_id",
        "publication_jobs",
        ["publishing_connection_id"],
    )
    op.create_index("ix_publication_jobs_status", "publication_jobs", ["status"])
    op.create_index("ix_publication_jobs_idempotency_key", "publication_jobs", ["idempotency_key"], unique=True)


def downgrade() -> None:
    op.drop_table("publication_jobs")
    op.drop_table("publishing_connections")
    publication_job_status.drop(op.get_bind(), checkfirst=True)
    publication_destination_type.drop(op.get_bind(), checkfirst=True)
    publishing_connection_status.drop(op.get_bind(), checkfirst=True)
