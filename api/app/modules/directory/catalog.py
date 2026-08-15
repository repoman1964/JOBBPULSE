"""Service and location catalog helpers for the public portfolio.

MVP derives catalog pages from published inventory rather than a CMS.
"""

from __future__ import annotations

from typing import Optional

from app.core.slug import slugify

# Canonical service catalog for display names + SEO copy.
# Keys match common job.service_key values (snake_case).
SERVICE_CATALOG: dict[str, dict[str, str]] = {
    "painting": {
        "name": "Painting",
        "description": "Interior and exterior painting projects completed by local contractors.",
    },
    "exterior_paint": {
        "name": "Exterior Painting",
        "description": "Exterior house painting and finish work documented in your area.",
    },
    "interior_painting": {
        "name": "Interior Painting",
        "description": "Interior repainting and finish projects completed for local homeowners.",
    },
    "tree_service": {
        "name": "Tree Service",
        "description": "Tree removal, pruning, and related outdoor work.",
    },
    "tree_removal": {
        "name": "Tree Removal",
        "description": "Large and small tree removal projects with visual proof of the work.",
    },
    "stump_removal": {
        "name": "Stump Removal",
        "description": "Stump grinding and removal after tree work.",
    },
    "hardscaping": {
        "name": "Hardscaping",
        "description": "Patios, retaining walls, and outdoor hardscape installations.",
    },
    "landscape_installation": {
        "name": "Landscape Installation",
        "description": "Landscape installation and yard improvement projects.",
    },
    "flooring": {
        "name": "Flooring",
        "description": "Flooring installation and refinishing projects.",
    },
    "fencing": {
        "name": "Fencing",
        "description": "Fence installation and repair projects.",
    },
    "deck_building": {
        "name": "Deck Building",
        "description": "Deck construction and outdoor living structures.",
    },
    "roofing": {
        "name": "Roofing",
        "description": "Roof repair and replacement projects.",
    },
    "paver_patio": {
        "name": "Paver Patio",
        "description": "Paver patio and hardscape patio installations.",
    },
    "cabinet_installation": {
        "name": "Cabinet Installation",
        "description": "Kitchen, bath, and custom cabinet installation projects.",
    },
    "kitchen_cabinets": {
        "name": "Kitchen Cabinets",
        "description": "Kitchen cabinet installation and refresh projects for local homes.",
    },
    "bathroom_vanity": {
        "name": "Bath Vanities",
        "description": "Bathroom vanity installation and upgrade projects.",
    },
    "pantry_built_ins": {
        "name": "Pantries & Built-ins",
        "description": "Custom pantry and built-in cabinet installations.",
    },
}


def service_slug(service_key: Optional[str]) -> str:
    if not service_key:
        return "project"
    return slugify(service_key.replace("_", "-")) or "project"


def service_display_name(service_key: Optional[str]) -> str:
    if not service_key:
        return "Home Service"
    meta = SERVICE_CATALOG.get(service_key)
    if meta:
        return meta["name"]
    return service_key.replace("_", " ").strip().title()


def service_description(service_key: Optional[str]) -> str:
    if not service_key:
        return "Completed home-service projects."
    meta = SERVICE_CATALOG.get(service_key)
    if meta:
        return meta["description"]
    name = service_display_name(service_key)
    return f"Recent {name.lower()} projects completed by local contractors."


def location_slug(city: Optional[str], state: Optional[str] = None) -> str:
    city_part = slugify(city or "local") or "local"
    state_part = slugify(state or "") if state else ""
    if state_part:
        return f"{city_part}-{state_part}"
    return city_part


def parse_location_slug(slug: str) -> tuple[Optional[str], Optional[str]]:
    """Best-effort parse of `city-st` style slugs (e.g. marietta-ga)."""
    raw = (slug or "").strip().lower()
    if not raw:
        return None, None
    parts = raw.split("-")
    if len(parts) >= 2 and len(parts[-1]) == 2:
        state = parts[-1].upper()
        city = " ".join(parts[:-1]).replace("-", " ").title()
        return city, state
    return raw.replace("-", " ").title(), None


def service_key_from_slug(slug: str) -> str:
    """Map URL service slug back toward service_key form."""
    cleaned = (slug or "").strip().lower().replace("-", "_")
    if cleaned in SERVICE_CATALOG:
        return cleaned
    # Try matching catalog by slugified key
    for key in SERVICE_CATALOG:
        if service_slug(key) == slugify(slug or ""):
            return key
    return cleaned
