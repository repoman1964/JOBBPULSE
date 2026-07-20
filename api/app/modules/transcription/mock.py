"""Mock transcription provider for local dev and tests."""

from __future__ import annotations

from typing import Optional


class MockTranscriptionProvider:
    name = "mock"

    async def transcribe(
        self,
        audio_bytes: bytes,
        *,
        filename: str = "audio.webm",
        mime_type: str = "audio/webm",
        language: Optional[str] = "en",
    ) -> str:
        size = len(audio_bytes or b"")
        safe_name = (filename or "audio").strip() or "audio"
        return (
            "We finished the job as planned. Cleaned up the site and walked the homeowner "
            f"through the result. (mock transcript for {safe_name}, {size} bytes)"
        )
