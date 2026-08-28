"""Job public status helpers and transition validation."""

from __future__ import annotations

from app.models.enums import InternalJobStatus, PublicJobStatus

TERMINAL_PUBLIC = {
    PublicJobStatus.processing.value,
    PublicJobStatus.ready_for_approval.value,
    PublicJobStatus.needs_revision.value,
    PublicJobStatus.publishing.value,
    PublicJobStatus.published.value,
    PublicJobStatus.publish_issue.value,
}

# Allowed public transitions
ALLOWED_PUBLIC: dict[str, set[str]] = {
    PublicJobStatus.active.value: {
        PublicJobStatus.ready_to_finish.value,
        PublicJobStatus.processing.value,  # rare: submit without ready if mins met
    },
    PublicJobStatus.ready_to_finish.value: {
        PublicJobStatus.active.value,
        PublicJobStatus.processing.value,
    },
    PublicJobStatus.processing.value: {
        PublicJobStatus.ready_for_approval.value,
        PublicJobStatus.publish_issue.value,  # pipeline failure surface
    },
    PublicJobStatus.ready_for_approval.value: {
        PublicJobStatus.needs_revision.value,
        PublicJobStatus.publishing.value,
    },
    PublicJobStatus.needs_revision.value: {
        PublicJobStatus.ready_for_approval.value,
        PublicJobStatus.publishing.value,
    },
    PublicJobStatus.publishing.value: {
        PublicJobStatus.published.value,
        PublicJobStatus.publish_issue.value,
    },
    PublicJobStatus.publish_issue.value: {
        PublicJobStatus.publishing.value,
        PublicJobStatus.published.value,
    },
    PublicJobStatus.published.value: set(),
}


def compute_active_public_status(
    *,
    counts: dict[str, int],
    minimums: dict[str, int],
    current: str,
) -> str:
    """Only recompute while job is still in active documentation phase."""
    if current in TERMINAL_PUBLIC:
        return current
    before_ok = counts.get("before", 0) >= int(minimums.get("before", 2))
    progress_ok = counts.get("progress", 0) >= int(minimums.get("progress", 0))
    after_ok = counts.get("after", 0) >= int(minimums.get("after", 2))
    if before_ok and progress_ok and after_ok:
        return PublicJobStatus.ready_to_finish.value
    return PublicJobStatus.active.value


def assert_public_transition(from_status: str, to_status: str) -> None:
    if from_status == to_status:
        return
    allowed = ALLOWED_PUBLIC.get(from_status, set())
    if to_status not in allowed:
        from app.core.errors import AppError

        raise AppError(
            "invalid_state_transition",
            f"Cannot move job from {from_status} to {to_status}.",
            status_code=409,
        )


def public_for_internal(internal: str) -> str:
    mapping = {
        InternalJobStatus.draft.value: PublicJobStatus.active.value,
        InternalJobStatus.submitted.value: PublicJobStatus.processing.value,
        InternalJobStatus.queued.value: PublicJobStatus.processing.value,
        InternalJobStatus.transcribing.value: PublicJobStatus.processing.value,
        InternalJobStatus.curating_media.value: PublicJobStatus.processing.value,
        InternalJobStatus.generating.value: PublicJobStatus.processing.value,
        InternalJobStatus.generating_description.value: PublicJobStatus.processing.value,
        InternalJobStatus.generating_destinations.value: PublicJobStatus.processing.value,
        InternalJobStatus.ready_for_approval.value: PublicJobStatus.ready_for_approval.value,
        InternalJobStatus.revision_requested.value: PublicJobStatus.needs_revision.value,
        InternalJobStatus.regenerating.value: PublicJobStatus.needs_revision.value,
        InternalJobStatus.approved.value: PublicJobStatus.publishing.value,
        InternalJobStatus.publishing.value: PublicJobStatus.publishing.value,
        InternalJobStatus.published.value: PublicJobStatus.published.value,
        InternalJobStatus.partially_failed.value: PublicJobStatus.publish_issue.value,
        InternalJobStatus.failed.value: PublicJobStatus.publish_issue.value,
    }
    return mapping.get(internal, PublicJobStatus.active.value)
