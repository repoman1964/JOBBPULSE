"""Company and team schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class CompanyOut(BaseModel):
    id: UUID
    name: str
    slug: str
    trade: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    website_url: Optional[str] = None
    default_tone: str
    default_call_to_action: Optional[str] = None
    subscription_status: str
    subscription_plan: str
    timezone: str
    is_active: bool
    onboarding_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    trade: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    phone: Optional[str] = Field(default=None, max_length=40)
    website_url: Optional[str] = Field(default=None, max_length=500)
    default_tone: Optional[str] = Field(default=None, max_length=50)
    default_call_to_action: Optional[str] = Field(default=None, max_length=300)
    timezone: Optional[str] = Field(default=None, max_length=64)
    onboarding_completed: Optional[bool] = None


class ServiceOut(BaseModel):
    id: UUID
    service_key: str
    display_name: str
    description: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}


class ServiceCreate(BaseModel):
    service_key: str = Field(min_length=1, max_length=100)
    display_name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None


class ServiceUpdate(BaseModel):
    display_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ServiceAreaOut(BaseModel):
    id: UUID
    country_code: str
    state: Optional[str] = None
    metro_area: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    display_name: str
    is_primary: bool

    model_config = {"from_attributes": True}


class ServiceAreaCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=200)
    country_code: str = Field(default="US", min_length=2, max_length=2)
    state: Optional[str] = Field(default=None, max_length=100)
    metro_area: Optional[str] = Field(default=None, max_length=150)
    city: Optional[str] = Field(default=None, max_length=150)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    is_primary: bool = False


class MemberOut(BaseModel):
    id: UUID
    user_id: UUID
    email: EmailStr
    full_name: str
    role: str
    status: str
    created_at: datetime


class MemberInvite(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=200)
    role: str = Field(pattern="^(manager|crew)$")
    password: str = Field(min_length=8, max_length=128)


class MemberUpdate(BaseModel):
    role: Optional[str] = Field(default=None, pattern="^(owner|manager|crew)$")
    status: Optional[str] = Field(default=None, pattern="^(active|invited|disabled)$")
