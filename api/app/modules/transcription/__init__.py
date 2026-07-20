"""Transcription providers (voice → text). Swap via TRANSCRIPTION_PROVIDER."""

from app.modules.transcription.provider import get_transcription_provider

__all__ = ["get_transcription_provider"]
