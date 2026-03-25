"""
JobPulse — Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── Job Models ────────────────────────────────────────────

class JobCreate(BaseModel):
    """Fields sent with the multipart job submission."""
    job_type: str
    title: Optional[str] = None
    customer_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    platforms: str = '["facebook","gbp","blog"]'


class JobResponse(BaseModel):
    id: str
    job_type: str
    title: Optional[str] = None
    customer_name: Optional[str] = None
    voice_transcript: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    platforms: str
    status: str
    created_at: str
    photos: list["PhotoResponse"] = []
    content: list["ContentResponse"] = []

    class Config:
        from_attributes = True


class JobListItem(BaseModel):
    id: str
    job_type: str
    title: Optional[str] = None
    customer_name: Optional[str] = None
    status: str
    photo_count: int = 0
    has_voice: bool = False
    city: Optional[str] = None
    created_at: str


class JobStats(BaseModel):
    total_jobs: int = 0
    jobs_this_month: int = 0
    published_count: int = 0
    total_impressions: int = 0  # Placeholder for v2 analytics


# ── Photo Models ──────────────────────────────────────────

class PhotoResponse(BaseModel):
    id: str
    file_path: str
    original_name: Optional[str] = None
    sort_order: int = 0


# ── Content Models ────────────────────────────────────────

class ContentResponse(BaseModel):
    id: str
    platform: str
    title: Optional[str] = None
    body: str
    hashtags: Optional[str] = None
    published: bool = False
    published_at: Optional[str] = None
    created_at: str


class ContentEdit(BaseModel):
    """For editing generated content before publishing."""
    title: Optional[str] = None
    body: Optional[str] = None
    hashtags: Optional[str] = None


class PublishRequest(BaseModel):
    """Publish specific platforms or all."""
    platforms: Optional[list[str]] = None  # None = publish all


class GenerateRequest(BaseModel):
    """Optional overrides for content generation."""
    tone: Optional[str] = None  # e.g. "professional", "casual"
    custom_instructions: Optional[str] = None
