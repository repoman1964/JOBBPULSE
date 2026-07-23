"""directory_v2_leads_featured — directory_leads + featured flags

Revision ID: b9d1f6e2a470
Revises: a8c0e4f7b369
Create Date: 2026-07-22 21:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b9d1f6e2a470"
down_revision: Union[str, Sequence[str], None] = "a8c0e4f7b369"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

directory_lead_status = postgresql.ENUM(
    "new",
    "contacted",
    "booked",
    "won",
    "lost",
    "spam",
    name="directory_lead_status",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    directory_lead_status.create(bind, checkfirst=True)

    op.add_column(
        "contractor_profiles",
        sa.Column("featured", sa.Boolean(), server_default="false", nullable=False),
    )
    op.create_index("ix_contractor_profiles_featured", "contractor_profiles", ["featured"], unique=False)

    op.add_column(
        "directory_listings",
        sa.Column("featured", sa.Boolean(), server_default="false", nullable=False),
    )
    op.create_index("ix_directory_listings_featured", "directory_listings", ["featured"], unique=False)

    op.create_table(
        "directory_leads",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("contractor_profile_id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("source_project_id", sa.UUID(), nullable=True),
        sa.Column("source_page_type", sa.String(length=60), nullable=True),
        sa.Column("source_page_url", sa.String(length=1000), nullable=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("project_location", sa.String(length=200), nullable=True),
        sa.Column("service_requested", sa.String(length=100), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("preferred_contact_method", sa.String(length=40), nullable=True),
        sa.Column(
            "lead_status",
            directory_lead_status,
            server_default="new",
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["contractor_profile_id"], ["contractor_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_project_id"], ["directory_listings.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_directory_leads_contractor_profile_id", "directory_leads", ["contractor_profile_id"])
    op.create_index("ix_directory_leads_company_id", "directory_leads", ["company_id"])
    op.create_index("ix_directory_leads_source_project_id", "directory_leads", ["source_project_id"])
    op.create_index("ix_directory_leads_lead_status", "directory_leads", ["lead_status"])


def downgrade() -> None:
    op.drop_index("ix_directory_leads_lead_status", table_name="directory_leads")
    op.drop_index("ix_directory_leads_source_project_id", table_name="directory_leads")
    op.drop_index("ix_directory_leads_company_id", table_name="directory_leads")
    op.drop_index("ix_directory_leads_contractor_profile_id", table_name="directory_leads")
    op.drop_table("directory_leads")

    op.drop_index("ix_directory_listings_featured", table_name="directory_listings")
    op.drop_column("directory_listings", "featured")

    op.drop_index("ix_contractor_profiles_featured", table_name="contractor_profiles")
    op.drop_column("contractor_profiles", "featured")

    bind = op.get_bind()
    directory_lead_status.drop(bind, checkfirst=True)
