"""phase4_generation_runs_content_variants

Revision ID: d4e6a0b3c925
Revises: c3d5f9a2b814
Create Date: 2026-07-20 16:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "d4e6a0b3c925"
down_revision: Union[str, Sequence[str], None] = "c3d5f9a2b814"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

generation_run_status = postgresql.ENUM(
    "pending",
    "processing",
    "completed",
    "failed",
    name="generation_run_status",
    create_type=False,
)
generation_type = postgresql.ENUM(
    "initial",
    "regenerate",
    name="generation_type",
    create_type=False,
)
content_type = postgresql.ENUM(
    "primary_social",
    "short_caption",
    "before_after",
    "directory_listing",
    "educational",
    name="content_type",
    create_type=False,
)
content_variant_status = postgresql.ENUM(
    "draft",
    "awaiting_review",
    "approved",
    "rejected",
    "superseded",
    name="content_variant_status",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    generation_run_status.create(bind, checkfirst=True)
    generation_type.create(bind, checkfirst=True)
    content_type.create(bind, checkfirst=True)
    content_variant_status.create(bind, checkfirst=True)

    op.create_table(
        "generation_runs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("job_id", sa.UUID(), nullable=False),
        sa.Column("requested_by", sa.UUID(), nullable=True),
        sa.Column(
            "status",
            generation_run_status,
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "generation_type",
            generation_type,
            nullable=False,
            server_default="initial",
        ),
        sa.Column("tone", sa.String(length=50), nullable=True),
        sa.Column("length_preference", sa.String(length=40), nullable=True),
        sa.Column("user_instruction", sa.Text(), nullable=True),
        sa.Column("model_provider", sa.String(length=40), nullable=True),
        sa.Column("model_name", sa.String(length=100), nullable=True),
        sa.Column("prompt_version", sa.String(length=40), nullable=True),
        sa.Column("input_snapshot_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("output_snapshot_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_generation_runs_job_id"), "generation_runs", ["job_id"], unique=False)
    op.create_index(
        op.f("ix_generation_runs_status"), "generation_runs", ["status"], unique=False
    )

    op.create_table(
        "content_variants",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("job_id", sa.UUID(), nullable=False),
        sa.Column("generation_run_id", sa.UUID(), nullable=False),
        sa.Column("content_type", content_type, nullable=False),
        sa.Column("platform_target", sa.String(length=40), nullable=True),
        sa.Column("title", sa.String(length=300), nullable=True),
        sa.Column("body_generated", sa.Text(), nullable=False),
        sa.Column("body_edited", sa.Text(), nullable=True),
        sa.Column("call_to_action", sa.String(length=300), nullable=True),
        sa.Column("hashtags_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "status",
            content_variant_status,
            nullable=False,
            server_default="awaiting_review",
        ),
        sa.Column("version_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("approved_by", sa.UUID(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["generation_run_id"], ["generation_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_content_variants_job_id"), "content_variants", ["job_id"], unique=False
    )
    op.create_index(
        op.f("ix_content_variants_generation_run_id"),
        "content_variants",
        ["generation_run_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_content_variants_content_type"),
        "content_variants",
        ["content_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_content_variants_status"), "content_variants", ["status"], unique=False
    )

    op.create_table(
        "job_structured_details",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("job_id", sa.UUID(), nullable=False),
        sa.Column("generation_run_id", sa.UUID(), nullable=True),
        sa.Column("customer_problem", sa.Text(), nullable=True),
        sa.Column("work_completed", sa.Text(), nullable=True),
        sa.Column("materials", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("equipment", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("techniques", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("challenges", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("duration_text", sa.String(length=100), nullable=True),
        sa.Column("customer_reaction", sa.Text(), nullable=True),
        sa.Column("homeowner_advice", sa.Text(), nullable=True),
        sa.Column("safety_notes", sa.Text(), nullable=True),
        sa.Column("location_context", sa.String(length=200), nullable=True),
        sa.Column("differentiators", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("confidence_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("source_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["generation_run_id"], ["generation_runs.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id", name="uq_job_structured_details_job_id"),
    )
    op.create_index(
        op.f("ix_job_structured_details_job_id"),
        "job_structured_details",
        ["job_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_job_structured_details_job_id"), table_name="job_structured_details")
    op.drop_table("job_structured_details")
    op.drop_index(op.f("ix_content_variants_status"), table_name="content_variants")
    op.drop_index(op.f("ix_content_variants_content_type"), table_name="content_variants")
    op.drop_index(op.f("ix_content_variants_generation_run_id"), table_name="content_variants")
    op.drop_index(op.f("ix_content_variants_job_id"), table_name="content_variants")
    op.drop_table("content_variants")
    op.drop_index(op.f("ix_generation_runs_status"), table_name="generation_runs")
    op.drop_index(op.f("ix_generation_runs_job_id"), table_name="generation_runs")
    op.drop_table("generation_runs")

    bind = op.get_bind()
    content_variant_status.drop(bind, checkfirst=True)
    content_type.drop(bind, checkfirst=True)
    generation_type.drop(bind, checkfirst=True)
    generation_run_status.drop(bind, checkfirst=True)
