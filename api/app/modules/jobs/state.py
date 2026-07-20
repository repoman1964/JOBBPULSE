"""Job status transitions, next-action, and timeline helpers.

Contractor workflow (product rule):
- Before photos: optional (recommended)
- After photos: required to complete capture
- Voice summary: required (usable transcript) before generation

Forgetting befores must not block finishing a job with afters + voice.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from app.db.models import (
    Job,
    JobStatus,
    MediaAsset,
    MediaAssetType,
    MediaStageLabel,
    TranscriptionStatus,
    VoiceSummary,
)

CAPTURE_STATUSES = {
    JobStatus.draft,
    JobStatus.before_photos_added,
    JobStatus.work_in_progress,
    JobStatus.ready_for_summary,
}

# Statuses that recompute_capture_status must not rewrite downward.
LOCKED_STATUSES = {
    JobStatus.generating,
    JobStatus.awaiting_review,
    JobStatus.revision_requested,
    JobStatus.approved,
    JobStatus.scheduled,
    JobStatus.published,
    JobStatus.failed,
    JobStatus.archived,
}

OPTIONAL_BEFORE_TIP = "Before photos are optional but recommended for a stronger story."


@dataclass
class PhotoCounts:
    total: int = 0
    before: int = 0
    after: int = 0

    @property
    def has_before_after_pair(self) -> bool:
        return self.before >= 1 and self.after >= 1


@dataclass
class NextAction:
    action: str
    label: str
    cta: str
    reason: str
    optional_tip: Optional[str] = None

    def as_dict(self) -> dict:
        return {
            "action": self.action,
            "label": self.label,
            "cta": self.cta,
            "reason": self.reason,
            "optional_tip": self.optional_tip,
        }


def count_photos(media: Iterable[MediaAsset]) -> PhotoCounts:
    """Count ready images. Only before/after count toward the contractor workflow."""
    counts = PhotoCounts()
    for item in media:
        if item.asset_type != MediaAssetType.image:
            continue
        if item.processing_status.value == "pending_upload":
            continue
        if item.stage_label == MediaStageLabel.before:
            counts.before += 1
            counts.total += 1
        elif item.stage_label == MediaStageLabel.after:
            counts.after += 1
            counts.total += 1
    return counts


def usable_transcript_text(voice: Optional[VoiceSummary]) -> Optional[str]:
    """Prefer edited transcript over raw when transcription completed."""
    if voice is None:
        return None
    if voice.transcription_status != TranscriptionStatus.completed:
        return None
    edited = (voice.transcript_edited or "").strip()
    if edited:
        return edited
    raw = (voice.transcript_raw or "").strip()
    return raw or None


def has_usable_transcript(voice: Optional[VoiceSummary]) -> bool:
    return usable_transcript_text(voice) is not None


def recompute_capture_status(
    job: Job,
    counts: PhotoCounts,
    voice: Optional[VoiceSummary] = None,
) -> JobStatus:
    """
    Capture-phase status from media + voice.

    ≥1 after + usable transcript → ready_to_generate
    ≥1 after, no transcript → ready_for_summary
    """
    if job.status in LOCKED_STATUSES:
        return job.status

    # ready_to_generate is still recomputed so deleting voice can step back.
    if counts.after >= 1 and has_usable_transcript(voice):
        return JobStatus.ready_to_generate
    if counts.after >= 1:
        return JobStatus.ready_for_summary
    if counts.before >= 1:
        return JobStatus.before_photos_added
    return JobStatus.draft


def compute_next_action(
    job: Job,
    counts: PhotoCounts,
    voice: Optional[VoiceSummary] = None,
) -> NextAction:
    """
    Priority:
    1. After photos required
    2. Voice summary / usable transcript required
    3. Generate content (Phase 4 implements the action)
    Soft tip when no before photos — never a hard gate.
    """
    if job.status == JobStatus.archived:
        return NextAction(
            action="none",
            label="Archived",
            cta="View job",
            reason="This job is archived.",
        )

    if job.status == JobStatus.published:
        return NextAction(
            action="view_published",
            label="Published",
            cta="View results",
            reason="Content is published.",
        )

    if job.status in {
        JobStatus.awaiting_review,
        JobStatus.revision_requested,
        JobStatus.approved,
        JobStatus.scheduled,
    }:
        return NextAction(
            action="review_content",
            label="Review content",
            cta="Review",
            reason="Generated content needs your attention.",
        )

    if job.status == JobStatus.generating:
        return NextAction(
            action="wait_generation",
            label="Generating content",
            cta="Open job",
            reason="AI content is being prepared.",
        )

    # --- Capture phase ---

    if counts.after == 0:
        tip = OPTIONAL_BEFORE_TIP if counts.before == 0 else None
        if counts.before == 0 and counts.total == 0:
            return NextAction(
                action="add_after_photos",
                label="Add after photos",
                cta="Add after photos",
                reason=(
                    "After photos are required to finish this job. "
                    "Before photos are optional — add them if you still can."
                ),
                optional_tip=tip,
            )
        return NextAction(
            action="add_after_photos",
            label="Add after photos",
            cta="Add after photos",
            reason="Work done? Add after photos of the completed work.",
            optional_tip=tip,
        )

    tip = None
    if counts.before == 0:
        tip = "No before photos — you can still finish. " + OPTIONAL_BEFORE_TIP

    if not has_usable_transcript(voice):
        # In-progress transcription
        if voice is not None and voice.transcription_status in {
            TranscriptionStatus.pending,
            TranscriptionStatus.processing,
        }:
            return NextAction(
                action="record_voice_summary",
                label="Transcribing voice…",
                cta="Open job",
                reason="Your voice note is being transcribed. This usually takes a few seconds.",
                optional_tip=tip,
            )
        if voice is not None and voice.transcription_status == TranscriptionStatus.failed:
            return NextAction(
                action="record_voice_summary",
                label="Retry voice summary",
                cta="Record again",
                reason="Transcription failed. Re-record or try retranscribe.",
                optional_tip=tip,
            )
        return NextAction(
            action="record_voice_summary",
            label="Record work summary",
            cta="Record summary",
            reason="After photos are in. Record a short voice description to complete this job.",
            optional_tip=tip,
        )

    # After + usable transcript → ready for Phase 4 generation
    return NextAction(
        action="generate_content",
        label="Generate content",
        cta="Generate content",
        reason="Voice summary is ready. Generate marketing content from this job.",
        optional_tip=tip,
    )


def compute_timeline(
    job: Job,
    counts: PhotoCounts,
    voice: Optional[VoiceSummary] = None,
) -> list[dict]:
    """
    Visual steps: Created → Before (optional) → After (required) → Voice (required) → Review

    Before is never a blocking current step; empty jobs highlight After as required.
    """
    action = compute_next_action(job, counts, voice).action
    voice_done = has_usable_transcript(voice)

    def step(key: str, label: str, status: str) -> dict:
        return {"key": key, "label": label, "status": status}

    if action in {"review_content", "view_published"} or job.status in {
        JobStatus.awaiting_review,
        JobStatus.revision_requested,
        JobStatus.approved,
        JobStatus.scheduled,
        JobStatus.published,
    }:
        current = 4
    elif action == "generate_content" or job.status in {
        JobStatus.ready_to_generate,
        JobStatus.generating,
    }:
        # Voice complete; review/generation is next (Phase 4–5)
        current = 4 if action == "generate_content" else 3
    elif action == "record_voice_summary" or job.status == JobStatus.ready_for_summary:
        current = 3
    elif action == "add_after_photos" or counts.after == 0:
        current = 2
    else:
        current = 2

    if action == "record_voice_summary":
        current = 3
    elif action == "add_after_photos":
        current = 2
    elif action == "generate_content":
        # Stay on review step as "next"; voice is complete
        current = 4
    elif action == "wait_generation":
        current = 4
    elif action in {"review_content", "view_published"}:
        current = 4
    elif action == "none":
        current = 0

    keys = [
        ("create", "Created"),
        ("before", "Before"),
        ("after", "After"),
        ("voice", "Voice"),
        ("review", "Review"),
    ]
    out: list[dict] = []
    for i, (key, label) in enumerate(keys):
        if key == "create":
            status = "complete"
        elif key == "before":
            if counts.before >= 1:
                status = "complete"
            elif current > 2 or counts.after >= 1:
                status = "skipped"
            else:
                status = "optional"
        elif key == "after":
            if counts.after >= 1:
                status = "complete"
            elif current == 2:
                status = "current"
            else:
                status = "upcoming"
        elif key == "voice":
            if voice_done or job.status in {
                JobStatus.ready_to_generate,
                JobStatus.generating,
                JobStatus.awaiting_review,
                JobStatus.revision_requested,
                JobStatus.approved,
                JobStatus.scheduled,
                JobStatus.published,
            }:
                status = "complete"
            elif current == 3:
                status = "current"
            elif current < 3:
                status = "locked"
            else:
                status = "upcoming"
        else:  # review
            if action == "generate_content":
                # Phase 4 not built yet — show as current next step
                status = "current"
            elif current == 4 and action in {
                "wait_generation",
                "review_content",
                "view_published",
            }:
                status = "current"
            elif current > 4 or action in {"view_published"}:
                status = "complete"
            elif voice_done and action == "generate_content":
                status = "current"
            else:
                status = "locked"

        if job.status == JobStatus.archived:
            if key == "create":
                status = "complete"
            elif key == "before":
                status = "complete" if counts.before else "skipped"
            elif key == "after":
                status = "complete" if counts.after else "upcoming"
            elif key == "voice":
                status = "complete" if voice_done else "locked"
            else:
                status = "locked"

        out.append(step(key, label, status))
    return out
