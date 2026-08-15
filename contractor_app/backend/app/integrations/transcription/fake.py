"""Deterministic fake transcription for local development."""

from __future__ import annotations


class FakeTranscriptionProvider:
    async def transcribe(self, *, object_key: str, mime_type: str) -> str:
        return (
            "Customer needed the work done carefully. "
            "We completed the project as planned and the result looks great."
        )
