"""add facebook_group and google_business content types

Revision ID: b7c4e91a2d10
Revises: ce3e22caa18e
Create Date: 2026-08-31

"""
from typing import Sequence, Union

from alembic import op

revision: str = "b7c4e91a2d10"
down_revision: Union[str, Sequence[str], None] = "ce3e22caa18e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE content_type ADD VALUE IF NOT EXISTS 'facebook_group'")
    op.execute("ALTER TYPE content_type ADD VALUE IF NOT EXISTS 'google_business'")


def downgrade() -> None:
    # Postgres cannot drop enum values safely while rows may still use them.
    pass
