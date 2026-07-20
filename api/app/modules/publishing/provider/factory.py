"""Resolve publishing provider from settings."""

from __future__ import annotations

import logging
from functools import lru_cache

from app.core.config import get_settings
from app.modules.publishing.provider.base import PublishingProvider
from app.modules.publishing.provider.mock import MockPublishingProvider

logger = logging.getLogger(__name__)


@lru_cache
def get_publishing_provider() -> PublishingProvider:
    settings = get_settings()
    name = (settings.publishing_provider or "mock").strip().lower()
    if name == "mock":
        return MockPublishingProvider()
    # Real vendors (Blotato-class, etc.) plug in here with publishing_api_key.
    logger.warning("Unknown PUBLISHING_PROVIDER=%s; using mock", name)
    return MockPublishingProvider()
