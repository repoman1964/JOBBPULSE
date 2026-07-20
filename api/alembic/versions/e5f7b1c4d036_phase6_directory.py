"""phase6_directory_profiles_listings

Revision ID: e5f7b1c4d036
Revises: d4e6a0b3c925
Create Date: 2026-07-20 18:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e5f7b1c4d036"
down_revision: Union[str, Sequence[str], None] = "d4e6a0b3c925"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

directory_listing_status = postgresql.ENUM(
    "draft",
    "published",
    "unpublished",
    "flagged",
    "removed",
    name="directory_listing_status",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    directory_listing_status.create(bind, checkfirst=True)

    op.create_table(
        "contractor_profiles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("public_slug", sa.String(length=220), nullable=False),
        sa.Column("headline", sa.String(length=300), nullable=True),
        sa.Column("public_description", sa.Text(), nullable=True),
        sa.Column("contact_phone", sa.String(length=40), nullable=True),
        sa.Column("contact_email", sa.String(length=320), nullable=True),
        sa.Column("website_url", sa.String(length=500), nullable=True),
        sa.Column("lead_form_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("published", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("seo_title", sa.String(length=300), nullable=True),
        sa.Column("seo_description", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_id"),
    )
    op.create_index("ix_contractor_profiles_public_slug", "contractor_profiles", ["public_slug"], unique=True)
    op.create_index("ix_contractor_profiles_published", "contractor_profiles", ["published"], unique=False)
    op.create_index("ix_contractor_profiles_company_id", "contractor_profiles", ["company_id"], unique=False)

    op.create_table(
        "directory_listings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("job_id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("contractor_profile_id", sa.UUID(), nullable=False),
        sa.Column("slug", sa.String(length=220), nullable=False),
        sa.Column("public_title", sa.String(length=300), nullable=False),
        sa.Column("public_summary", sa.Text(), nullable=False),
        sa.Column("service_key", sa.String(length=100), nullable=True),
        sa.Column("location_display", sa.String(length=200), nullable=True),
        sa.Column("city", sa.String(length=150), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("postal_code", sa.String(length=20), nullable=True),
        sa.Column(
            "status",
            directory_listing_status,
            server_default="draft",
            nullable=False,
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("unpublished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("seo_title", sa.String(length=300), nullable=True),
        sa.Column("seo_description", sa.String(length=500), nullable=True),
        sa.Column("structured_data_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["contractor_profile_id"], ["contractor_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id"),
    )
    op.create_index("ix_directory_listings_slug", "directory_listings", ["slug"], unique=True)
    op.create_index("ix_directory_listings_status", "directory_listings", ["status"], unique=False)
    op.create_index("ix_directory_listings_city", "directory_listings", ["city"], unique=False)
    op.create_index("ix_directory_listings_state", "directory_listings", ["state"], unique=False)
    op.create_index("ix_directory_listings_service_key", "directory_listings", ["service_key"], unique=False)
    op.create_index("ix_directory_listings_company_id", "directory_listings", ["company_id"], unique=False)
    op.create_index(
        "ix_directory_listings_contractor_profile_id",
        "directory_listings",
        ["contractor_profile_id"],
        unique=False,
    )
    op.create_index("ix_directory_listings_job_id", "directory_listings", ["job_id"], unique=False)

    op.create_table(
        "directory_listing_media",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("directory_listing_id", sa.UUID(), nullable=False),
        sa.Column("media_asset_id", sa.UUID(), nullable=False),
        sa.Column("stage_label", sa.String(length=40), nullable=False),
        sa.Column("display_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["directory_listing_id"], ["directory_listings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["media_asset_id"], ["media_assets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_directory_listing_media_directory_listing_id",
        "directory_listing_media",
        ["directory_listing_id"],
        unique=False,
    )
    op.create_index(
        "ix_directory_listing_media_media_asset_id",
        "directory_listing_media",
        ["media_asset_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("directory_listing_media")
    op.drop_table("directory_listings")
    op.drop_table("contractor_profiles")
    directory_listing_status.drop(op.get_bind(), checkfirst=True)
