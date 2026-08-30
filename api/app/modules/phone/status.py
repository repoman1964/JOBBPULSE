"""Map api/ JobStatus onto contractor-app publicStatus values."""

from __future__ import annotations

from app.db.models import JobStatus

_TO_PUBLIC = {
    JobStatus.draft: "active",
    JobStatus.before_photos_added: "active",
    JobStatus.work_in_progress: "active",
    JobStatus.ready_for_summary: "ready_to_finish",
    JobStatus.ready_to_generate: "ready_to_finish",
    JobStatus.generating: "processing",
    JobStatus.awaiting_review: "ready_for_approval",
    JobStatus.approved: "ready_for_approval",
    JobStatus.revision_requested: "needs_revision",
    JobStatus.scheduled: "publishing",
    JobStatus.publishing: "publishing",
    JobStatus.published: "published",
    JobStatus.publish_issue: "publish_issue",
    JobStatus.failed: "publish_issue",
    JobStatus.archived: "active",
}

_FROM_PUBLIC = {
    "active": {
        JobStatus.draft,
        JobStatus.before_photos_added,
        JobStatus.work_in_progress,
    },
    "ready_to_finish": {JobStatus.ready_for_summary, JobStatus.ready_to_generate},
    "processing": {JobStatus.generating},
    "ready_for_approval": {JobStatus.awaiting_review, JobStatus.approved},
    "needs_revision": {JobStatus.revision_requested},
    "publishing": {JobStatus.publishing, JobStatus.scheduled},
    "published": {JobStatus.published},
    "publish_issue": {JobStatus.publish_issue, JobStatus.failed},
}


def to_public(status: JobStatus) -> str:
    return _TO_PUBLIC.get(status, "active")


def from_public(value: str) -> set[JobStatus]:
    return set(_FROM_PUBLIC.get(value, set()))
