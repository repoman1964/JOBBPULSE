"""Generated content destinations for each finished job."""

from __future__ import annotations

from app.integrations.content_gen.fake import FakeContentGenerator
from app.services.engine import content_destinations


def test_always_generates_google_business_when_nothing_is_connected() -> None:
    dests = content_destinations(connected=set())
    assert dests[0:4] == ["facebook", "facebook_group", "instagram", "google_business"]
    assert dests[-2:] == ["conversion_site", "portfolio_site"]


def test_always_generates_google_business_even_if_only_facebook_is_connected() -> None:
    dests = content_destinations(connected={"facebook"})
    assert "facebook" in dests
    assert "instagram" in dests
    assert "google_business" in dests
    assert dests.count("google_business") == 1


def test_does_not_add_removed_social_platforms() -> None:
    dests = content_destinations(connected={"tiktok", "youtube", "x", "linkedin"})
    assert dests == [
        "facebook",
        "facebook_group",
        "instagram",
        "google_business",
        "conversion_site",
        "portfolio_site",
    ]


async def test_google_business_copy_is_a_local_update_not_a_caption() -> None:
    content = await FakeContentGenerator().destination_content(
        destination="google_business",
        job_name="Thompson Exterior Painting",
        city="Decatur",
        description="We refreshed this Decatur home with a full exterior repaint.",
    )
    body = content["body"]
    assert content["title"] == "Google Business Profile"
    assert "Decatur" in body
    assert "#" not in body
    assert "documented with JobbPulse" not in body
    assert "Just finished" in body


async def test_facebook_group_copy_is_neighborly() -> None:
    content = await FakeContentGenerator().destination_content(
        destination="facebook_group",
        job_name="Exterior painting",
        city="Decatur",
        description="Full exterior.",
    )
    assert content["title"] == "Neighborhood group"
    assert "Decatur" in content["body"]
    assert "JobbPulse" not in content["body"]
    assert "#" not in content["body"]
