"""Mock content generation provider for local dev and tests."""

from __future__ import annotations

from app.modules.ai_generation.schemas import (
    ContentPiece,
    GeneratedContentBundle,
    JobGenerationInput,
    StructuredJobDetails,
)

PROMPT_VERSION = "v1-mock"
MODEL_NAME = "mock-v1"


class MockContentGenerationProvider:
    name = "mock"

    async def extract_job_details(self, input_data: JobGenerationInput) -> StructuredJobDetails:
        return self._build_structured(input_data)

    async def generate_content(self, input_data: JobGenerationInput) -> GeneratedContentBundle:
        structured = self._build_structured(input_data)
        warnings = self._warnings(input_data)
        uncertain: list[str] = []
        if len((input_data.transcript or "").strip()) < 40:
            uncertain.append("Transcript is short; some details may be inferred.")

        place = self._place(input_data)
        service = self._service_label(input_data)
        company = (input_data.company_name or "our team").strip() or "our team"
        cta = (
            (input_data.default_call_to_action or "").strip()
            or f"Call {company} for a free estimate."
        )
        transcript_snip = self._transcript_snip(input_data.transcript)
        public_title = f"{service} in {place}" if place else f"Completed {service}"

        instruction_note = ""
        if input_data.user_instruction:
            instruction_note = f" ({input_data.user_instruction.strip()[:120]})"

        primary_body = (
            f"Another job wrapped up{f' in {place}' if place else ''}! "
            f"Our crew completed {service.lower()} for a local homeowner. "
            f"{transcript_snip} "
            f"Clean site, clear communication, solid result.{instruction_note}\n\n"
            f"{cta}"
        )
        short_body = (
            f"{service} done{f' in {place}' if place else ''}. "
            f"{transcript_snip} {cta}"
        )
        neighborhood = input_data.city or place or "the area"
        group_body = (
            f"Wrapped {service.lower()} in {neighborhood} this week. "
            f"{transcript_snip} "
            "If a neighbor needs similar work, we walk the house and send a written number."
        )
        gbp_body = (
            f"Finished {service.lower()}{f' in {place}' if place else ''}. "
            f"{transcript_snip} {cta}"
        )
        dir_summary = (
            f"{company} completed {service.lower()}"
            f"{f' for a homeowner in {place}' if place else ''}. "
            f"{structured.work_completed or transcript_snip}"
        )

        hashtags = self._hashtags(input_data, place, service)

        content = {
            "primary_social": ContentPiece(
                title=public_title,
                body=primary_body.strip(),
                hashtags=hashtags,
                call_to_action=cta,
            ),
            "short_caption": ContentPiece(
                body=short_body.strip()[:500],
                hashtags=hashtags[:3],
                call_to_action=cta,
            ),
            "facebook_group": ContentPiece(
                title="Neighborhood group",
                body=group_body.strip(),
                hashtags=[],
                call_to_action=cta,
            ),
            "google_business": ContentPiece(
                title=public_title,
                body=gbp_body.strip(),
                hashtags=[],
                call_to_action=cta,
            ),
            "directory_listing": ContentPiece(
                title=public_title,
                body=dir_summary.strip(),
                summary=dir_summary.strip()[:400],
                work_completed=structured.work_completed,
                call_to_action=cta,
                hashtags=[],
            ),
        }

        return GeneratedContentBundle(
            structured_details=structured,
            content=content,
            warnings=warnings,
            uncertain_claims=uncertain,
            model_name=MODEL_NAME,
            prompt_version=PROMPT_VERSION,
        )

    def _build_structured(self, input_data: JobGenerationInput) -> StructuredJobDetails:
        place = self._place(input_data)
        service = self._service_label(input_data)
        snip = self._transcript_snip(input_data.transcript)
        return StructuredJobDetails(
            customer_problem=f"Homeowner needed {service.lower()}{f' in {place}' if place else ''}.",
            work_completed=snip or f"Completed {service.lower()} as described by the crew.",
            materials=[],
            equipment=[],
            techniques=[],
            challenges=[],
            result="Work completed and site cleaned up.",
            duration_text=None,
            customer_reaction=None,
            homeowner_advice="Keep the area clear and reach out if anything looks off.",
            safety_notes=None,
            location_context=place or None,
            differentiators=["Local crew", "Clear communication"],
            confidence_json={"overall": 0.6, "source": "mock"},
        )

    def _warnings(self, input_data: JobGenerationInput) -> list[str]:
        out: list[str] = []
        if input_data.before_count == 0:
            out.append("No before photos — after-only story.")
        if input_data.total_photo_count < 3:
            out.append("Fewer than 3 photos — consider adding more for a stronger post.")
        return out

    def _place(self, input_data: JobGenerationInput) -> str:
        if input_data.location_display:
            return input_data.location_display.strip()
        parts = [p for p in [input_data.city, input_data.state] if p]
        return ", ".join(parts)

    def _service_label(self, input_data: JobGenerationInput) -> str:
        if input_data.service_key:
            return input_data.service_key.replace("_", " ").strip().title()
        if input_data.company_trade:
            return input_data.company_trade.replace("_", " ").strip().title() + " work"
        return "Home service project"

    def _transcript_snip(self, transcript: str, max_len: int = 180) -> str:
        t = (transcript or "").strip()
        if not t:
            return ""
        if len(t) <= max_len:
            return t
        return t[: max_len - 1].rstrip() + "…"

    def _hashtags(
        self, input_data: JobGenerationInput, place: str, service: str
    ) -> list[str]:
        tags = ["#LocalPros", "#BeforeAndAfter", "#HomeServices"]
        if input_data.city:
            tags.append("#" + "".join(c for c in input_data.city.title() if c.isalnum()))
        sk = (input_data.service_key or input_data.company_trade or "").replace("_", "")
        if sk:
            tags.append("#" + sk.title()[:24])
        return tags[:6]
