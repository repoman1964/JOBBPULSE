"""job_soft_delete

Revision ID: c8e1a4b7d902
Revises: e304f5555716
Create Date: 2026-08-23

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c8e1a4b7d902"
down_revision: Union[str, None] = "e304f5555716"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_jobs_deleted_at", "jobs", ["deleted_at"])


def downgrade() -> None:
    op.drop_index("ix_jobs_deleted_at", table_name="jobs")
    op.drop_column("jobs", "deleted_at")
