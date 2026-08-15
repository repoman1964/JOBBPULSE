"""Company and contractor models."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AccountStatus, ContractorRole, ContractorStatus

if TYPE_CHECKING:
    from app.models.auth import AuthIdentity
    from app.models.job import Job


DEFAULT_PHOTO_MINIMUMS = {"before": 2, "progress": 0, "after": 2}
DEFAULT_PHOTO_MAXIMUMS = {"before": 15, "progress": 30, "after": 15}
DEFAULT_NOTIFICATION_SETTINGS = {
    "contentReadyForApproval": True,
    "publishingComplete": True,
}


class Company(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    account_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=AccountStatus.active.value
    )
    contact_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    phone: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    email: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    website: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    service_area: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    photo_minimums_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=lambda: dict(DEFAULT_PHOTO_MINIMUMS)
    )
    photo_maximums_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=lambda: dict(DEFAULT_PHOTO_MAXIMUMS)
    )
    notification_settings_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=lambda: dict(DEFAULT_NOTIFICATION_SETTINGS)
    )

    contractors: Mapped[list[Contractor]] = relationship(back_populates="company")
    jobs: Mapped[list[Job]] = relationship(back_populates="company")


class Contractor(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "contractors"
    __table_args__ = (
        UniqueConstraint("company_id", "email", name="uq_contractors_company_email"),
    )

    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    role: Mapped[str] = mapped_column(
        String(32), nullable=False, default=ContractorRole.owner.value
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=ContractorStatus.active.value
    )

    company: Mapped[Company] = relationship(back_populates="contractors")
    identities: Mapped[list[AuthIdentity]] = relationship(back_populates="contractor")
