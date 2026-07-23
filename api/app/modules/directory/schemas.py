"""Pydantic schemas for directory admin and public APIs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProfileUpdate(BaseModel):
    headline: Optional[str] = Field(default=None, max_length=300)
    public_description: Optional[str] = None
    contact_phone: Optional[str] = Field(default=None, max_length=40)
    contact_email: Optional[str] = Field(default=None, max_length=320)
    website_url: Optional[str] = Field(default=None, max_length=500)
    lead_form_enabled: Optional[bool] = None
    published: Optional[bool] = None
    seo_title: Optional[str] = Field(default=None, max_length=300)
    seo_description: Optional[str] = Field(default=None, max_length=500)


class ListingUpdate(BaseModel):
    public_title: Optional[str] = Field(default=None, max_length=300)
    public_summary: Optional[str] = None
    seo_title: Optional[str] = Field(default=None, max_length=300)
    seo_description: Optional[str] = Field(default=None, max_length=500)
    location_display: Optional[str] = Field(default=None, max_length=200)


class JobPublishRequest(BaseModel):
    """Unified publish request (§10.10). Phase 6 implements directory only."""

    publish_to_directory: bool = True
    social_connection_ids: list[UUID] = Field(default_factory=list)
    scheduled_for: Optional[datetime] = None


class LeadCreate(BaseModel):
    contractor_slug: str = Field(min_length=1, max_length=220)
    name: str = Field(min_length=1, max_length=200)
    email: Optional[str] = Field(default=None, max_length=320)
    phone: Optional[str] = Field(default=None, max_length=40)
    message: Optional[str] = Field(default=None, max_length=2000)
    project_slug: Optional[str] = Field(default=None, max_length=220)
    project_location: Optional[str] = Field(default=None, max_length=200)
    service_requested: Optional[str] = Field(default=None, max_length=100)
    preferred_contact_method: Optional[str] = Field(default=None, max_length=40)
    source_page_type: Optional[str] = Field(default=None, max_length=60)
    source_page_url: Optional[str] = Field(default=None, max_length=1000)
