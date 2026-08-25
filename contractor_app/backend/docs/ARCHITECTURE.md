# JobbPulse Engine — Architecture Notes

## Responsibilities

The backend owns multi-tenant persistence, media upload orchestration, the content generation pipeline, revision versioning, social connection management (Upload-Post), and first-party website publishing.

The Nuxt Contractor App never calls Upload-Post or AI providers directly.

## Request path

1. Contractor authenticates via OTP challenge → JWT access token (+ refresh cookie).
2. All `/api/v1/*` business routes require `Authorization: Bearer <access>`.
3. `company_id` is taken from the token, never from client-supplied tenant fields.
4. Repositories/services filter every query by that `company_id`.

## Media

1. `POST .../upload-sessions` creates a `media_assets` row and a presigned S3/MinIO PUT URL.
2. Browser uploads bytes directly to object storage.
3. `POST .../complete` verifies the object exists and marks upload complete.
4. API responses return short-lived signed GET URLs.

## Pipeline (submit → ready for approval)

`POST /jobs/{id}/submit` is idempotent on `idempotencyKey`. It snapshots media, transitions the job to `processing`, and enqueues Celery task `process_job_submission`.

Worker steps (fake providers by default):

1. Transcribe voice
2. Curate photos (prefer favorites)
3. Generate project description
4. Generate destination assets (Facebook / Instagram / GBP / 3–5 homeowners groups + Conversion Site carousel and job page + directory)
5. Persist package + immutable asset versions
6. Set public status `ready_for_approval`

If the broker is unavailable during local development, the API falls back to running the same engine code inline so the happy path remains usable.

## Revisions

- Package description revision or asset-scoped revision creates a `revision_requests` row.
- Only affected outputs get a new **immutable** `generated_asset_versions` row.
- Active version is selected via `select-version` or set by the engine.

## Publishing

`approve-and-publish` is idempotent. Celery creates one `publication_attempts` row per asset with a unique idempotency key.

Offer lock: `docs/biz_docs/usp.md`. One approve must fan out to the locked set (Facebook Page, Instagram, Google Business Profile, 3–5 local homeowners groups, conversion-site carousel + job page, directory project page). Evergreen cadence is a separate scheduled pipeline, not part of the job package.

| Destination | Adapter |
| --- | --- |
| Facebook Page, Instagram, Google Business Profile | `FakeSocialPublisher` / Upload-Post client |
| Local Facebook homeowners groups (3–5) | Same social adapter, group destinations from company onboarding |
| Conversion Site (home carousel + job page) | `ConversionSitePublisher` (first-party) |
| Portfolio / directory Site | `PortfolioSitePublisher` (first-party) |

Partial failures set public status `publish_issue` without re-posting successful destinations.

## Upload-Post / Google Business Profile

- One Upload-Post profile per company (`social_profiles.provider_username` derived from company id).
- Create-user treats HTTP 409 as idempotent.
- Google Business Profile connection is an **integration gate**: keep the platform in the model/UI; do not send invalid provider enums until confirmed against live Upload-Post docs.

## Local vs production providers

| Setting | Local default | Production |
| --- | --- | --- |
| `PROVIDER_MODE` | `fake` | `live` |
| `AUTH_DEV_CODES` | `true` | **forbidden** |
| Transcription / content gen | Fake deterministic | Configured STT + LLM |
| Social publish | Fake success | Upload-Post API |

## Key modules

```
app/api/v1/       HTTP routers
app/models/       SQLAlchemy models
app/services/     Domain logic + engine pipeline
app/integrations/ Storage, Upload-Post, fake AI
app/publishers/   Social + first-party destinations
app/tasks/        Celery workers
```
