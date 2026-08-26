"""password_email_verification

Revision ID: d9f2b6c8e013
Revises: c8e1a4b7d902
Create Date: 2026-08-25

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d9f2b6c8e013"
down_revision: Union[str, None] = "c8e1a4b7d902"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "contractors",
        sa.Column("password_hash", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "contractors",
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("contractors", "email_verified_at")
    op.drop_column("contractors", "password_hash")
