"""phase3_voice_summaries

Revision ID: c3d5f9a2b814
Revises: b2c4e8f1a903
Create Date: 2026-07-20 14:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c3d5f9a2b814"
down_revision: Union[str, Sequence[str], None] = "b2c4e8f1a903"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

transcription_status = postgresql.ENUM(
    "pending",
    "processing",
    "completed",
    "failed",
    name="transcription_status",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    transcription_status.create(bind, checkfirst=True)

    op.create_table(
        "voice_summaries",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("job_id", sa.UUID(), nullable=False),
        sa.Column("audio_asset_id", sa.UUID(), nullable=True),
        sa.Column("transcript_raw", sa.Text(), nullable=True),
        sa.Column("transcript_edited", sa.Text(), nullable=True),
        sa.Column("language", sa.String(length=16), nullable=False, server_default="en"),
        sa.Column(
            "transcription_status",
            transcription_status,
            nullable=False,
            server_default="pending",
        ),
        sa.Column("transcription_provider", sa.String(length=40), nullable=True),
        sa.Column("transcription_error", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["audio_asset_id"], ["media_assets.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id", name="uq_voice_summaries_job_id"),
    )
    op.create_index(op.f("ix_voice_summaries_job_id"), "voice_summaries", ["job_id"], unique=True)
    op.create_index(
        op.f("ix_voice_summaries_transcription_status"),
        "voice_summaries",
        ["transcription_status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_voice_summaries_transcription_status"), table_name="voice_summaries")
    op.drop_index(op.f("ix_voice_summaries_job_id"), table_name="voice_summaries")
    op.drop_table("voice_summaries")
    transcription_status.drop(op.get_bind(), checkfirst=True)
