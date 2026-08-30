"""Auth request/response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from email_validator import EmailNotValidError, validate_email
from pydantic import AfterValidator, AliasChoices, BaseModel, Field


_LOCAL_DEMO_TLDS = (".local", ".test", ".example", ".invalid", ".localhost")


def _normalize_email(value: str) -> str:
    """Accept real emails and reserved demo domains used by local seed users."""
    text = (value or "").strip()
    domain = text.rsplit("@", 1)[-1].lower() if "@" in text else ""
    if any(domain == tld[1:] or domain.endswith(tld) for tld in _LOCAL_DEMO_TLDS):
        # email-validator rejects .local even with test_environment=True.
        if text.count("@") == 1 and " " not in text:
            local_part, host = text.split("@", 1)
            if local_part and host:
                return f"{local_part}@{host.lower()}"
        raise ValueError("value is not a valid email address")
    try:
        info = validate_email(text, check_deliverability=False)
    except EmailNotValidError as exc:
        raise ValueError(str(exc)) from exc
    return info.normalized


AppEmail = Annotated[str, AfterValidator(_normalize_email)]


class RegisterRequest(BaseModel):
    model_config = {"populate_by_name": True}

    email: AppEmail
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(
        min_length=1,
        max_length=200,
        validation_alias=AliasChoices("full_name", "name"),
    )
    company_name: str = Field(
        min_length=1,
        max_length=200,
        validation_alias=AliasChoices("company_name", "companyName"),
    )
    trade: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=40)


class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=8, max_length=2000)


class ResendVerificationRequest(BaseModel):
    email: AppEmail


class ForgotPasswordRequest(BaseModel):
    email: AppEmail


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=8, max_length=2000)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: AppEmail
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: UUID
    email: AppEmail
    full_name: str
    phone: Optional[str] = None
    is_verified: bool
    is_active: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MembershipOut(BaseModel):
    id: UUID
    company_id: UUID
    role: str
    status: str

    model_config = {"from_attributes": True}


class CompanySummaryOut(BaseModel):
    id: UUID
    name: str
    slug: str
    trade: Optional[str] = None
    onboarding_completed: bool

    model_config = {"from_attributes": True}


class MeOut(BaseModel):
    user: UserOut
    company: Optional[CompanySummaryOut] = None
    membership: Optional[MembershipOut] = None
    permissions: dict


class TokenPairOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut
    company: Optional[CompanySummaryOut] = None
    membership: Optional[MembershipOut] = None
