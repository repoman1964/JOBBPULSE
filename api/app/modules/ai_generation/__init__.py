"""AI content generation providers (job → marketing drafts). Swap via AI_PROVIDER."""

from app.modules.ai_generation.provider import get_generation_provider

__all__ = ["get_generation_provider"]
