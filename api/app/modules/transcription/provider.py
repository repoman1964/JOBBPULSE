"""Resolve transcription provider from settings."""

from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.modules.transcription.base import TranscriptionProvider
from app.modules.transcription.mock import MockTranscriptionProvider


@lru_cache
def get_transcription_provider() -> TranscriptionProvider:
    settings = get_settings()
    name = (settings.transcription_provider or "mock").strip().lower()
    if name == "mock":
        return MockTranscriptionProvider()
    # Real vendors (Whisper, Deepgram, etc.) plug in here later.
    return MockTranscriptionProvider()
