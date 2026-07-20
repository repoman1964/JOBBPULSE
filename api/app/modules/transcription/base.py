"""Transcription provider interface."""

from __future__ import annotations

from typing import Optional, Protocol


class TranscriptionProvider(Protocol):
    """Replaceable voice-to-text vendor (mock, Whisper, Deepgram, etc.)."""

    name: str

    async def transcribe(
        self,
        audio_bytes: bytes,
        *,
        filename: str = "audio.webm",
        mime_type: str = "audio/webm",
        language: Optional[str] = "en",
    ) -> str:
        """Return plain-text transcript for the given audio."""
        ...
