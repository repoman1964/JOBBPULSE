"""Auth request/response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import AliasChoices, BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    model_config = {"populate_by_name": True}

    email: EmailStr
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
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=8, max_length=2000)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
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
