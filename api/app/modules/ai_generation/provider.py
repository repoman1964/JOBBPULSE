"""Resolve content generation provider from settings."""

from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.modules.ai_generation.base import ContentGenerationProvider
from app.modules.ai_generation.mock import MockContentGenerationProvider


@lru_cache
def get_generation_provider() -> ContentGenerationProvider:
    settings = get_settings()
    name = (settings.ai_provider or "mock").strip().lower()
    if name == "mock":
        return MockContentGenerationProvider()
    # Real vendors (SpaceXAI, OpenAI, etc.) plug in here later.
    return MockContentGenerationProvider()
