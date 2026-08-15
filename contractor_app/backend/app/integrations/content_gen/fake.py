"""Deterministic fake content generation."""

from __future__ import annotations

from typing import Any


class FakeContentGenerator:
    async def project_description(
        self,
        *,
        job_name: str,
        service_type: str,
        city: str,
        region: str,
        transcript: str,
    ) -> str:
        location = ", ".join(p for p in [city, region] if p)
        base = (
            f"We completed {job_name} ({service_type}) in {location or city}. "
            "The crew documented the full transformation from start to finish."
        )
        if transcript:
            # Ground only — do not invent warranties/pricing
            snippet = transcript.strip()[:280]
            return f"{base} {snippet}"
        return base

    async def destination_content(
        self,
        *,
        destination: str,
        job_name: str,
        city: str,
        description: str,
    ) -> dict[str, Any]:
        titles = {
            "facebook": "Facebook",
            "instagram": "Instagram",
            "google_business": "Google Business Profile",
            "tiktok": "TikTok",
            "x": "X",
            "linkedin": "LinkedIn",
            "conversion_site": "Project Page",
            "portfolio_site": "JobbPulse Portfolio",
        }
        if destination == "instagram":
            body = f"{job_name} complete in {city}. #JobbPulse"
        elif destination == "facebook":
            body = f"{job_name}: another transformation ready to share."
        elif destination in {"conversion_site", "portfolio_site"}:
            body = description
        else:
            body = f"{job_name} in {city} — documented with JobbPulse."

        return {
            "title": titles.get(destination, destination),
            "body": body,
            "payload": {"destination": destination},
            "preview": {},
        }
