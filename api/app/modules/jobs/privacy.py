"""
Privacy contract for Job fields.

The contractor-facing `title` is a private label (customer nickname, street, etc.).
It must never be sent to AI generation, social publishing, or the public directory.
AI will invent public titles/hooks later from photos + voice + coarse location.
"""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from app.db.models import Job, VoiceSummary
from app.modules.jobs.state import usable_transcript_text

# Never include these in AI, social, or public directory payloads.
PRIVATE_JOB_FIELDS = frozenset(
    {
        "title",
        "customer_name_private",
        "notes",  # may contain customer details; keep internal until scrubbed
        "postal_code",  # too precise for public pages
    }
)

# Coarse / safe for future generation and local SEO (not street-level).
GENERATION_SAFE_FIELDS = frozenset(
    {
        "service_key",
        "city",
        "state",
        "location_display",  # must stay general area only (e.g. "South Austin")
    }
)


def transcript_for_generation(voice: Optional[VoiceSummary]) -> Optional[str]:
    """Edited transcript preferred over raw for AI generation (Phase 4+)."""
    return usable_transcript_text(voice)


def fields_for_generation(job: Job, voice: Optional[VoiceSummary] = None) -> dict[str, Any]:
    """
    Build the safe subset of job metadata for AI generation (Phase 4+).

    Explicitly excludes private contractor labels and PII.
    Transcript text may be included; job title is never included.
    """
    if voice is None:
        voice = getattr(job, "voice_summary", None)
    out: dict[str, Any] = {
        "job_id": str(job.id),
        "company_id": str(job.company_id),
        "service_key": job.service_key,
        "city": job.city,
        "state": job.state,
        "location_display": job.location_display,
        # Intentionally omit: title, customer_name_private, notes, postal_code
    }
    transcript = transcript_for_generation(voice)
    if transcript:
        out["transcript"] = transcript
    return out


def assert_title_not_in_generation_payload(payload: dict[str, Any]) -> None:
    """Guard for tests and future generation code."""
    for key in PRIVATE_JOB_FIELDS:
        if key in payload and payload[key] is not None:
            raise ValueError(f"Private field {key!r} must not appear in generation payload.")


def is_private_field(name: str) -> bool:
    return name in PRIVATE_JOB_FIELDS
