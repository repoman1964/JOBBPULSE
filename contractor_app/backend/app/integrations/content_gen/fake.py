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
            "facebook_group": "Neighborhood group",
            "instagram": "Instagram",
            "google_business": "Google Business Profile",
            "tiktok": "TikTok",
            "youtube": "YouTube Shorts",
            "x": "X",
            "linkedin": "LinkedIn",
            "conversion_site": "Project Page",
            "portfolio_site": "Portfolio",
        }
        if destination == "instagram":
            tag = f"#{city.replace(' ', '')}" if city else ""
            body = f"{job_name} complete in {city}. {tag}".strip()
        elif destination == "facebook":
            body = f"{job_name}: another transformation ready to share."
        elif destination == "facebook_group":
            body = (
                f"Wrapped a {job_name.lower()} in {city} this week. "
                "Prep first, then the finish. If a neighbor needs similar work, "
                "we walk the house and send a written number."
            )
        elif destination == "google_business":
            body = (
                f"Just finished {job_name} in {city}. "
                "Solid prep, a clean finish, and a crew that shows up ready to work. "
                "Call us if you have a similar project."
            )
        elif destination in {"conversion_site", "portfolio_site"}:
            body = description
        else:
            body = f"{job_name} in {city}."

        return {
            "title": titles.get(destination, destination),
            "body": body,
            "payload": {"destination": destination},
            "preview": {},
        }
