"""Job status transitions, next-action, and timeline helpers.

Contractor workflow (product rule):
- Before photos: optional (recommended)
- After photos: required to complete capture
- Voice summary: required to complete job (Phase 3 implements recording)

Forgetting befores must not block finishing a job with afters + voice.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from app.db.models import Job, JobStatus, MediaAsset, MediaAssetType, MediaStageLabel

CAPTURE_STATUSES = {
    JobStatus.draft,
    JobStatus.before_photos_added,
    JobStatus.work_in_progress,
    JobStatus.ready_for_summary,
}

LOCKED_STATUSES = {
    JobStatus.ready_to_generate,
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


def recompute_capture_status(job: Job, counts: PhotoCounts) -> JobStatus:
    """
    Capture-phase status from media.

    ≥1 after photo → ready_for_summary (voice next), even with zero befores.
    """
    if job.status in LOCKED_STATUSES:
        return job.status

    if counts.after >= 1:
        return JobStatus.ready_for_summary
    if counts.before >= 1:
        return JobStatus.before_photos_added
    return JobStatus.draft


def compute_next_action(job: Job, counts: PhotoCounts) -> NextAction:
    """
    Priority:
    1. After photos required
    2. Voice summary required (Phase 3)
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

    if job.status in {JobStatus.generating, JobStatus.ready_to_generate}:
        return NextAction(
            action="wait_generation",
            label="Generating content",
            cta="Open job",
            reason="AI content is being prepared.",
        )

    # --- Capture phase ---

    # After photos are required to complete the job story.
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

    # After present → voice is required (Phase 3). Soft tip if no before.
    tip = None
    if counts.before == 0:
        tip = "No before photos — you can still finish. " + OPTIONAL_BEFORE_TIP

    return NextAction(
        action="record_voice_summary",
        label="Record work summary",
        cta="Record summary",
        reason="After photos are in. Record a short voice description to complete this job.",
        optional_tip=tip,
    )


def compute_timeline(job: Job, counts: PhotoCounts) -> list[dict]:
    """
    Visual steps: Created → Before (optional) → After (required) → Voice (required) → Review

    Before is never a blocking current step; empty jobs highlight After as required.
    """
    action = compute_next_action(job, counts).action

    def step(key: str, label: str, status: str) -> dict:
        return {"key": key, "label": label, "status": status}

    # Current step index: 0 create, 1 before (optional), 2 after, 3 voice, 4 review
    if action in {"review_content", "view_published"} or job.status in {
        JobStatus.awaiting_review,
        JobStatus.revision_requested,
        JobStatus.approved,
        JobStatus.scheduled,
        JobStatus.published,
    }:
        current = 4
    elif action in {"record_voice_summary", "wait_generation"} or job.status in {
        JobStatus.ready_to_generate,
        JobStatus.generating,
    }:
        current = 3
    elif action == "add_after_photos" or counts.after == 0:
        current = 2
    else:
        current = 2

    if action == "record_voice_summary":
        current = 3
    elif action == "add_after_photos":
        current = 2
    elif action in {"wait_generation"}:
        current = 3
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
            if action == "wait_generation":
                status = "current"
            elif action in {"review_content", "view_published"} or job.status in {
                JobStatus.ready_to_generate,
                JobStatus.generating,
                JobStatus.awaiting_review,
                JobStatus.approved,
                JobStatus.published,
            }:
                # Voice done once past ready_for_summary into generation/review
                if job.status in {
                    JobStatus.ready_to_generate,
                    JobStatus.generating,
                    JobStatus.awaiting_review,
                    JobStatus.revision_requested,
                    JobStatus.approved,
                    JobStatus.scheduled,
                    JobStatus.published,
                }:
                    status = "complete" if action != "wait_generation" else "current"
                else:
                    status = "complete"
            elif current == 3:
                status = "current"
            elif current < 3:
                status = "locked"
            else:
                status = "upcoming"
        else:  # review
            if current == 4:
                status = "current"
            elif current > 4:
                status = "complete"
            else:
                status = "locked"

        if job.status == JobStatus.archived:
            if key == "create":
                status = "complete"
            elif key == "before":
                status = "complete" if counts.before else "skipped"
            elif key == "after":
                status = "complete" if counts.after else "upcoming"
            else:
                status = "locked"

        out.append(step(key, label, status))
    return out
