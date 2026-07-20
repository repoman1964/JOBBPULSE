"""Content generation provider interface."""

from __future__ import annotations

from typing import Protocol

from app.modules.ai_generation.schemas import (
    GeneratedContentBundle,
    JobGenerationInput,
    StructuredJobDetails,
)


class ContentGenerationProvider(Protocol):
    """Replaceable AI vendor (mock, SpaceXAI, OpenAI, etc.)."""

    name: str

    async def extract_job_details(self, input_data: JobGenerationInput) -> StructuredJobDetails:
        """Extract structured work details from safe job inputs."""
        ...

    async def generate_content(self, input_data: JobGenerationInput) -> GeneratedContentBundle:
        """Produce a full content bundle (structured + variants + warnings)."""
        ...
