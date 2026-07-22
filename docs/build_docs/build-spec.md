# JobPulse Agent Build Specification

**Product:** JobPulse  
**Document type:** Agent Build Specification  
**Status:** Implementation-ready working specification  
**Version:** 1.0  
**Primary audience:** Coding agent, product engineer, technical founder  
**Frontend:** Nuxt 3  
**Backend:** FastAPI  
**Database:** PostgreSQL  
**Object storage:** S3-compatible storage  
**Primary architecture:** Modular monolith with asynchronous workers  
**Deployment target:** Containerized cloud deployment  

---

## 1. Purpose

This document defines how an engineering agent should build the first production-ready version of JobPulse.

JobPulse is a contractor-first job-to-marketing platform for visual home-service businesses.

The core workflow is:

**Create a Job → capture before photos → complete the work → capture after photos → record a voice summary → generate content → human review and revision → approve → publish to social media and the JobPulse-owned local directory**

The system must make this workflow extremely easy for a field contractor using a phone.

The MVP must support:

- Contractor accounts and company profiles
- Fast Job creation
- At least three photos per Job
- Before, progress and after photo labels
- Voice recording and transcription
- AI-generated social and directory content
- Human approval, rejection, editing and regeneration
- Social publishing through a third-party provider
- Publishing to a JobPulse-owned local directory
- Job and content status tracking
- Basic roles and permissions
- Durable data storage
- Background processing
- Error handling and auditability

---

## 2. Non-Negotiable Product Rules

The implementation must preserve the following rules.

### 2.1 The Job Is the Core Object

All generated content originates from a Job.

A Job is not simply a social post draft. It is the permanent source record containing the real work, photos, voice summary, structured data, generated content and publishing history.

### 2.2 Job Creation Must Be Extremely Easy

The user should be able to:

1. Tap **Create Job**
2. Capture before photos
3. Save
4. Return later
5. Capture after photos
6. Record a voice summary
7. Generate content

The system should minimize required typing.

### 2.3 At Least Three Photos Per Job

The system must support storing at least three photos for each Job.

The model should support more than three photos even if the launch UI emphasizes three primary assets.

The recommended minimum visual set is:

- One primary before photo
- One primary after photo
- One supporting photo

### 2.4 Human Approval Is Required

Generated content must never be distributed before a human approves it.

The user must be able to:

- Edit
- Reject
- Regenerate
- Change tone
- Change length
- Add missing context
- Remove incorrect details
- Approve social content
- Approve directory content

### 2.5 Two Primary Publication Destinations

Approved content must support publication to:

1. Connected social platforms through a third-party publisher
2. The JobPulse-owned and controlled local directory

### 2.6 No Facebook Group Automation

Do not implement automated posting to Facebook groups.

This is intentionally out of scope because it risks user accounts and creates platform dependency.

### 2.7 Owned Directory Is Core

The local directory must be treated as a primary product surface, not a later marketing page.

Each published Job should be able to create a permanent public project page connected to a contractor profile.

---

## 3. Recommended Architecture

Use a modular monolith for the MVP.

This keeps development fast while preserving clear boundaries between product areas.

### 3.1 Frontend

- Nuxt 3
- Vue 3 Composition API
- TypeScript
- Pinia
- Nuxt server routes only for frontend-specific proxy needs
- Tailwind CSS
- Nuxt UI or a comparable accessible component library
- PWA support
- Browser MediaRecorder API for voice capture
- Direct-to-object-storage uploads through signed URLs

### 3.2 Backend

- FastAPI
- Python 3.12+
- SQLAlchemy 2
- Alembic
- Pydantic 2
- PostgreSQL
- Redis
- Celery, Dramatiq or RQ for background work
- S3-compatible object storage
- FFmpeg for media processing when required
- AI provider abstraction
- Publishing provider abstraction

### 3.3 Infrastructure

- Docker
- Docker Compose for local development
- Managed PostgreSQL for production
- Managed Redis
- Managed S3-compatible storage
- Reverse proxy or cloud load balancer
- CI through GitHub Actions
- Structured logging
- Error monitoring
- Metrics and health checks

### 3.4 Initial Service Boundaries

Keep one backend application but separate code into modules:

- Authentication
- Companies
- Users
- Jobs
- Media
- Voice and transcription
- AI generation
- Content review
- Publishing
- Directory
- Notifications
- Billing
- Admin and moderation

---

## 4. Repository Structure

Recommended monorepo:

```text
jobpulse/
├── apps/
│   ├── web/
│   │   ├── app.vue
│   │   ├── nuxt.config.ts
│   │   ├── assets/
│   │   ├── components/
│   │   ├── composables/
│   │   ├── layouts/
│   │   ├── middleware/
│   │   ├── pages/
│   │   ├── plugins/
│   │   ├── public/
│   │   ├── stores/
│   │   ├── types/
│   │   └── utils/
│   └── api/
│       ├── app/
│       │   ├── main.py
│       │   ├── core/
│       │   ├── db/
│       │   ├── modules/
│       │   │   ├── auth/
│       │   │   ├── companies/
│       │   │   ├── users/
│       │   │   ├── jobs/
│       │   │   ├── media/
│       │   │   ├── transcription/
│       │   │   ├── ai_generation/
│       │   │   ├── content/
│       │   │   ├── publishing/
│       │   │   ├── directory/
│       │   │   ├── notifications/
│       │   │   ├── billing/
│       │   │   └── admin/
│       │   ├── schemas/
│       │   ├── services/
│       │   ├── tasks/
│       │   └── tests/
│       ├── alembic/
│       ├── pyproject.toml
│       └── Dockerfile
├── packages/
│   ├── shared-types/
│   └── config/
├── infra/
│   ├── docker-compose.yml
│   ├── nginx/
│   └── scripts/
├── docs/
│   ├── prd.md
│   ├── build-spec.md
│   └── api.md
└── .github/
    └── workflows/
```

---

## 5. Core Data Model

Use UUID primary keys.

Use UTC timestamps.

All tables should include:

- `id`
- `created_at`
- `updated_at`

Where appropriate, add:

- `deleted_at`
- `created_by`
- `updated_by`

---

## 6. Database Entities

### 6.1 companies

Fields:

- `id`
- `name`
- `slug`
- `trade`
- `description`
- `phone`
- `website_url`
- `logo_asset_id`
- `default_tone`
- `default_call_to_action`
- `subscription_status`
- `subscription_plan`
- `timezone`
- `is_active`
- `created_at`
- `updated_at`

Indexes:

- `slug`
- `subscription_status`
- `trade`

### 6.2 company_service_areas

Fields:

- `id`
- `company_id`
- `country_code`
- `state`
- `metro_area`
- `city`
- `postal_code`
- `display_name`
- `is_primary`

Indexes:

- `company_id`
- `state`
- `city`
- `postal_code`

### 6.3 company_services

Fields:

- `id`
- `company_id`
- `service_key`
- `display_name`
- `description`
- `is_active`

### 6.4 users

Fields:

- `id`
- `email`
- `phone`
- `full_name`
- `password_hash`
- `is_verified`
- `is_active`
- `last_login_at`

### 6.5 company_memberships

Fields:

- `id`
- `company_id`
- `user_id`
- `role`
- `status`

Roles:

- `owner`
- `manager`
- `crew`

### 6.6 jobs

Fields:

- `id`
- `company_id`
- `created_by`
- `title`
- `service_key`
- `location_display`
- `city`
- `state`
- `postal_code`
- `customer_name_private`
- `customer_consent_status`
- `status`
- `job_started_at`
- `job_completed_at`
- `submitted_at`
- `approved_at`
- `published_at`
- `notes`
- `privacy_mode`
- `generation_version`
- `latest_generation_run_id`

Suggested statuses:

- `draft`
- `before_photos_added`
- `work_in_progress`
- `ready_for_summary`
- `ready_to_generate`
- `generating`
- `awaiting_review`
- `revision_requested`
- `approved`
- `scheduled`
- `published`
- `failed`
- `archived`

### 6.7 media_assets

Fields:

- `id`
- `company_id`
- `job_id`
- `uploaded_by`
- `storage_key`
- `original_filename`
- `mime_type`
- `file_size_bytes`
- `width`
- `height`
- `duration_seconds`
- `asset_type`
- `stage_label`
- `display_order`
- `is_primary`
- `processing_status`
- `moderation_status`
- `metadata_json`

Asset types:

- `image`
- `audio`
- `video`
- `document`

Stage labels:

- `before`
- `progress`
- `after`
- `unclassified`

### 6.8 voice_summaries

Fields:

- `id`
- `job_id`
- `audio_asset_id`
- `transcript_raw`
- `transcript_edited`
- `language`
- `transcription_status`
- `transcription_provider`
- `transcription_error`

### 6.9 job_structured_details

Fields:

- `id`
- `job_id`
- `customer_problem`
- `work_completed`
- `materials`
- `equipment`
- `techniques`
- `challenges`
- `result`
- `duration_text`
- `customer_reaction`
- `homeowner_advice`
- `safety_notes`
- `location_context`
- `differentiators`
- `confidence_json`
- `source_version`

### 6.10 generation_runs

Fields:

- `id`
- `job_id`
- `requested_by`
- `status`
- `generation_type`
- `tone`
- `length_preference`
- `user_instruction`
- `model_provider`
- `model_name`
- `prompt_version`
- `input_snapshot_json`
- `output_snapshot_json`
- `error_message`
- `completed_at`

### 6.11 content_variants

Fields:

- `id`
- `job_id`
- `generation_run_id`
- `content_type`
- `platform_target`
- `title`
- `body_generated`
- `body_edited`
- `call_to_action`
- `hashtags_json`
- `status`
- `version_number`
- `approved_by`
- `approved_at`
- `rejected_at`

Content types:

- `primary_social`
- `short_caption`
- `before_after`
- `educational`
- `directory_listing`
- `ad_copy_future`

Statuses:

- `draft`
- `awaiting_review`
- `approved`
- `rejected`
- `superseded`

### 6.12 content_media_links

Fields:

- `id`
- `content_variant_id`
- `media_asset_id`
- `display_order`

### 6.13 publishing_connections

Fields:

- `id`
- `company_id`
- `provider`
- `external_account_id`
- `platform`
- `display_name`
- `credentials_encrypted`
- `status`
- `last_verified_at`
- `last_error`

### 6.14 publication_jobs

Fields:

- `id`
- `job_id`
- `content_variant_id`
- `destination_type`
- `publishing_connection_id`
- `provider`
- `scheduled_for`
- `status`
- `provider_request_id`
- `provider_response_json`
- `external_url`
- `attempt_count`
- `last_error`
- `published_at`

Destination types:

- `social`
- `directory`

### 6.15 contractor_profiles

Fields:

- `id`
- `company_id`
- `public_slug`
- `headline`
- `public_description`
- `contact_phone`
- `contact_email`
- `website_url`
- `lead_form_enabled`
- `published`
- `seo_title`
- `seo_description`

### 6.16 directory_listings

Fields:

- `id`
- `job_id`
- `company_id`
- `contractor_profile_id`
- `slug`
- `public_title`
- `public_summary`
- `service_key`
- `location_display`
- `city`
- `state`
- `postal_code`
- `status`
- `published_at`
- `unpublished_at`
- `seo_title`
- `seo_description`
- `structured_data_json`

### 6.17 directory_listing_media

Fields:

- `id`
- `directory_listing_id`
- `media_asset_id`
- `stage_label`
- `display_order`

### 6.18 notifications

Fields:

- `id`
- `user_id`
- `company_id`
- `type`
- `title`
- `body`
- `channel`
- `status`
- `read_at`
- `sent_at`
- `metadata_json`

### 6.19 audit_events

Fields:

- `id`
- `company_id`
- `user_id`
- `entity_type`
- `entity_id`
- `action`
- `before_json`
- `after_json`
- `ip_address`
- `user_agent`

---

## 7. FastAPI Backend Structure

Recommended module structure:

```text
app/modules/jobs/
├── api.py
├── models.py
├── schemas.py
├── repository.py
├── service.py
├── permissions.py
├── events.py
└── tests/
```

Use the same pattern for each major module.

### 7.1 Layer Responsibilities

#### API Layer

- Parse requests
- Apply authentication
- Apply authorization
- Call services
- Return response schemas
- Avoid direct ORM logic

#### Service Layer

- Enforce business rules
- Coordinate repositories
- Trigger background tasks
- Create audit events
- Handle state transitions

#### Repository Layer

- Database queries
- Persistence
- Pagination
- Filtering
- Row locking when necessary

#### Task Layer

- Transcription
- Image processing
- AI generation
- Publishing
- Notifications
- SEO metadata generation

---

## 8. Authentication and Authorization

### 8.1 Authentication

Use one of:

- Secure email and password authentication with JWT access and refresh tokens
- Passwordless magic links
- Managed auth provider

For an agent-built MVP, use:

- Short-lived JWT access token
- Rotating refresh token
- HttpOnly secure cookies
- CSRF protection
- Email verification
- Password reset

### 8.2 Authorization Rules

Owner:

- Full company access
- Billing
- Connections
- Team management
- Approval
- Publishing

Manager:

- Create and update Jobs
- Review and approve content
- Publish content
- View company reporting

Crew:

- Create Jobs
- Upload photos
- Record voice summaries
- Cannot approve or publish

Every backend query must be scoped to the authenticated user’s company.

---

## 9. API Conventions

Base path:

```text
/api/v1
```

Response format:

```json
{
  "data": {},
  "meta": {},
  "error": null
}
```

Error format:

```json
{
  "data": null,
  "meta": {},
  "error": {
    "code": "JOB_NOT_READY",
    "message": "Add at least one before photo and one after photo before generating content.",
    "details": {}
  }
}
```

Use cursor pagination for large collections.

Use idempotency keys for:

- Publishing
- Generation
- Direct upload completion
- Billing webhooks

---

## 10. Core API Endpoints

### 10.1 Auth

```text
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh
POST   /api/v1/auth/verify-email
POST   /api/v1/auth/request-password-reset
POST   /api/v1/auth/reset-password
GET    /api/v1/auth/me
```

### 10.2 Company

```text
GET    /api/v1/company
PATCH  /api/v1/company
GET    /api/v1/company/services
POST   /api/v1/company/services
PATCH  /api/v1/company/services/{service_id}
DELETE /api/v1/company/services/{service_id}
GET    /api/v1/company/service-areas
POST   /api/v1/company/service-areas
DELETE /api/v1/company/service-areas/{area_id}
```

### 10.3 Team

```text
GET    /api/v1/company/members
POST   /api/v1/company/members/invite
PATCH  /api/v1/company/members/{membership_id}
DELETE /api/v1/company/members/{membership_id}
```

### 10.4 Jobs

```text
GET    /api/v1/jobs
POST   /api/v1/jobs
GET    /api/v1/jobs/{job_id}
PATCH  /api/v1/jobs/{job_id}
DELETE /api/v1/jobs/{job_id}
POST   /api/v1/jobs/{job_id}/archive
POST   /api/v1/jobs/{job_id}/submit
POST   /api/v1/jobs/{job_id}/mark-complete
GET    /api/v1/jobs/{job_id}/timeline
```

### 10.5 Media

```text
POST   /api/v1/jobs/{job_id}/media/upload-url
POST   /api/v1/jobs/{job_id}/media/complete
GET    /api/v1/jobs/{job_id}/media
PATCH  /api/v1/media/{media_id}
DELETE /api/v1/media/{media_id}
POST   /api/v1/media/{media_id}/set-primary
POST   /api/v1/jobs/{job_id}/media/reorder
```

### 10.6 Voice

```text
POST   /api/v1/jobs/{job_id}/voice/upload-url
POST   /api/v1/jobs/{job_id}/voice/complete
GET    /api/v1/jobs/{job_id}/voice
PATCH  /api/v1/jobs/{job_id}/voice/transcript
POST   /api/v1/jobs/{job_id}/voice/retranscribe
```

### 10.7 Generation

```text
POST   /api/v1/jobs/{job_id}/generate
GET    /api/v1/jobs/{job_id}/generation-runs
GET    /api/v1/generation-runs/{run_id}
POST   /api/v1/jobs/{job_id}/regenerate
```

Request body example:

```json
{
  "tone": "friendly_local",
  "length_preference": "standard",
  "user_instruction": "Focus more on the drainage problem and keep the tone straightforward."
}
```

### 10.8 Content Review

```text
GET    /api/v1/jobs/{job_id}/content
GET    /api/v1/content/{content_id}
PATCH  /api/v1/content/{content_id}
POST   /api/v1/content/{content_id}/approve
POST   /api/v1/content/{content_id}/reject
POST   /api/v1/content/{content_id}/duplicate
POST   /api/v1/jobs/{job_id}/approve-all
```

### 10.9 Publishing Connections

```text
GET    /api/v1/publishing/connections
POST   /api/v1/publishing/connections/start
POST   /api/v1/publishing/connections/callback
DELETE /api/v1/publishing/connections/{connection_id}
POST   /api/v1/publishing/connections/{connection_id}/verify
```

### 10.10 Publishing

```text
POST   /api/v1/jobs/{job_id}/publish
POST   /api/v1/jobs/{job_id}/schedule
GET    /api/v1/jobs/{job_id}/publications
POST   /api/v1/publications/{publication_id}/retry
POST   /api/v1/publications/{publication_id}/cancel
```

Example publish request:

```json
{
  "social_connection_ids": [
    "uuid"
  ],
  "publish_to_directory": true,
  "scheduled_for": null
}
```

### 10.11 Directory Admin

```text
GET    /api/v1/directory/profile
PATCH  /api/v1/directory/profile
GET    /api/v1/directory/listings
GET    /api/v1/directory/listings/{listing_id}
PATCH  /api/v1/directory/listings/{listing_id}
POST   /api/v1/directory/listings/{listing_id}/publish
POST   /api/v1/directory/listings/{listing_id}/unpublish
```

### 10.12 Public Directory API

```text
GET    /api/v1/public/contractors
GET    /api/v1/public/contractors/{slug}
GET    /api/v1/public/projects
GET    /api/v1/public/projects/{slug}
POST   /api/v1/public/leads
```

---

## 11. Job State Machine

Implement Job status changes through one state transition service.

Do not allow arbitrary status updates from the frontend.

Example transition rules:

```text
draft
  -> before_photos_added
  -> work_in_progress
  -> ready_for_summary
  -> ready_to_generate
  -> generating
  -> awaiting_review
  -> revision_requested
  -> awaiting_review
  -> approved
  -> scheduled
  -> published
```

Allowed fallback transitions:

```text
generating -> failed
scheduled -> failed
published -> archived
awaiting_review -> revision_requested
revision_requested -> generating
```

Generation readiness checks:

- Job exists
- User has permission
- At least one before photo
- At least one after photo
- At least three total photos are recommended
- Voice transcript exists
- No generation already running

For MVP flexibility, allow generation with fewer than three photos only if an authorized user explicitly confirms.

---

## 12. Media Upload Flow

Use direct-to-object-storage uploads.

### 12.1 Flow

1. Frontend requests a signed upload URL
2. Backend validates company and Job access
3. Backend returns storage key and signed URL
4. Frontend uploads directly to object storage
5. Frontend calls upload completion endpoint
6. Backend creates or finalizes `media_asset`
7. Background worker generates thumbnail and extracts metadata
8. Frontend receives live or polled status update

### 12.2 Accepted Image Formats

- JPEG
- PNG
- HEIC, if server-side conversion is supported
- WebP

### 12.3 Image Processing

Generate:

- Original preserved
- Large web version
- Medium card version
- Thumbnail

Perform:

- EXIF rotation normalization
- Metadata extraction
- Optional EXIF stripping for privacy
- Compression
- Basic corruption detection

### 12.4 Privacy

Strip precise GPS metadata from publicly served images.

Do not expose raw object storage keys in public responses.

Use signed delivery URLs or CDN paths.

---

## 13. Voice Recording and Transcription

### 13.1 Frontend Recording

Use the browser `MediaRecorder` API.

Preferred formats:

- WebM Opus
- MP4 or M4A fallback when supported

The UI must support:

- Start
- Pause
- Resume
- Stop
- Playback
- Delete
- Re-record
- Upload progress

### 13.2 Backend Processing

The transcription task should:

1. Validate audio
2. Normalize format if required
3. Send to transcription provider
4. Save raw transcript
5. Mark status
6. Trigger structured extraction
7. Notify frontend

### 13.3 Transcript Editing

The user must be able to edit the transcript before generation.

Store:

- Original transcript
- Edited transcript

AI generation should use the edited transcript when available.

---

## 14. AI Generation Pipeline

Create an AI provider interface.

```python
class ContentGenerationProvider(Protocol):
    async def extract_job_details(self, input_data: JobGenerationInput) -> StructuredJobDetails:
        ...

    async def generate_content(self, input_data: JobGenerationInput) -> GeneratedContentBundle:
        ...
```

### 14.1 Generation Inputs

- Job title
- Service type
- General location
- Before photos
- After photos
- Optional progress photos
- Voice transcript
- Contractor profile
- Services
- Tone
- Default CTA
- User instruction
- Previous rejected version, when regenerating

### 14.2 Generation Output Schema

```json
{
  "structured_details": {
    "customer_problem": "",
    "work_completed": "",
    "materials": [],
    "challenges": [],
    "result": "",
    "homeowner_advice": ""
  },
  "content": {
    "primary_social": {
      "title": "",
      "body": "",
      "hashtags": []
    },
    "short_caption": {
      "body": ""
    },
    "before_after": {
      "body": ""
    },
    "directory_listing": {
      "title": "",
      "summary": "",
      "work_completed": "",
      "call_to_action": ""
    }
  },
  "warnings": [],
  "uncertain_claims": []
}
```

### 14.3 AI Guardrails

The generation service must instruct the model to:

- Use only supplied facts
- Avoid exact residential addresses
- Avoid inventing prices
- Avoid inventing durations
- Avoid invented customer reactions
- Avoid invented certifications
- Avoid guarantees
- Avoid identifying the customer without consent
- Flag uncertainty
- Prefer plain contractor language
- Avoid repetitive marketing clichés
- Avoid excessive emojis
- Avoid excessive hashtags

### 14.4 Prompt Versioning

Store prompt versions.

Every generation run should record:

- Prompt version
- Model
- Provider
- Input snapshot
- Output snapshot

This is required for debugging and quality improvement.

---

## 15. Content Review Loop

The review loop is a central product feature.

### 15.1 Review Actions

Users can:

- Edit text inline
- Approve a variant
- Reject a variant
- Regenerate all variants
- Regenerate one variant
- Add a custom instruction
- Change tone
- Change length
- Select different images
- Remove a generated claim
- Restore a previous version

### 15.2 Versioning

Do not overwrite generated versions.

Each regeneration creates:

- New generation run
- New content variant versions
- Prior content marked `superseded` or retained as history

### 15.3 Approval Rules

A Job can be marked approved when:

- At least one social variant is approved
- Directory listing content is approved
- At least one before image and one after image are selected
- No unresolved system warnings block publication

Allow separate approval status for:

- Social content
- Directory content

---

## 16. Third-Party Publishing Adapter

Define a provider interface.

```python
class PublishingProvider(Protocol):
    async def connect_account(self, ...):
        ...

    async def publish_post(self, request: PublishRequest) -> PublishResult:
        ...

    async def schedule_post(self, request: ScheduleRequest) -> PublishResult:
        ...

    async def get_status(self, external_id: str) -> PublishStatus:
        ...
```

### 16.1 Provider Responsibilities

- Account connection
- Token handling
- Media upload
- Text publishing
- Scheduling
- Status retrieval
- Error mapping
- Retry support

### 16.2 Internal Responsibilities

JobPulse must:

- Encrypt credentials
- Track connection health
- Map provider errors
- Retry safely
- Prevent duplicate posts
- Preserve publication history
- Support provider replacement

### 16.3 Idempotency

Every publication attempt must include an internal idempotency key.

Never create duplicate social posts when a worker retries.

---

## 17. Directory Publishing

Directory publication should not depend on the third-party social publishing provider.

It is an internal JobPulse operation.

### 17.1 Directory Publication Flow

1. Validate approved directory content
2. Validate contractor profile
3. Generate slug
4. Create or update directory listing
5. Link selected media
6. Strip private metadata
7. Generate SEO metadata
8. Publish
9. Return public URL
10. Record publication event

### 17.2 Public URL Patterns

```text
/contractors/{state}/{city}/{contractor-slug}
/projects/{state}/{city}/{service-key}/{project-slug}
```

### 17.3 Slug Requirements

- Lowercase
- Human readable
- Stable
- Unique
- Avoid customer names
- Avoid precise addresses

### 17.4 Directory Moderation

Support:

- Draft
- Published
- Unpublished
- Flagged
- Removed

Admin must be able to unpublish any listing.

---

## 18. Nuxt Frontend Architecture

Use Nuxt 3 with TypeScript.

### 18.1 Layouts

```text
layouts/
├── default.vue
├── auth.vue
├── app.vue
└── directory.vue
```

### 18.2 Page Structure

```text
pages/
├── index.vue
├── login.vue
├── register.vue
├── onboarding/
│   ├── index.vue
│   ├── company.vue
│   ├── services.vue
│   ├── service-areas.vue
│   ├── brand.vue
│   └── connections.vue
├── app/
│   ├── index.vue
│   ├── jobs/
│   │   ├── index.vue
│   │   ├── new.vue
│   │   └── [id]/
│   │       ├── index.vue
│   │       ├── photos.vue
│   │       ├── voice.vue
│   │       ├── generate.vue
│   │       ├── review.vue
│   │       └── publish.vue
│   ├── content/
│   │   └── index.vue
│   ├── directory/
│   │   ├── index.vue
│   │   ├── profile.vue
│   │   └── listings/[id].vue
│   ├── connections.vue
│   ├── team.vue
│   ├── settings.vue
│   └── billing.vue
├── contractors/
│   └── [state]/[city]/[slug].vue
└── projects/
    └── [state]/[city]/[service]/[slug].vue
```

---

## 19. Required Nuxt Components

### 19.1 App Shell

```text
components/app/
├── AppHeader.vue
├── AppSidebar.vue
├── AppBottomNav.vue
├── MobileActionBar.vue
├── PageTitle.vue
├── EmptyState.vue
├── LoadingState.vue
├── ErrorState.vue
└── ConfirmDialog.vue
```

### 19.2 Job Components

```text
components/jobs/
├── JobCard.vue
├── JobList.vue
├── JobStatusBadge.vue
├── JobCreateButton.vue
├── JobQuickCreate.vue
├── JobHeader.vue
├── JobTimeline.vue
├── JobProgressStepper.vue
├── JobSummaryPanel.vue
├── JobLocationField.vue
├── JobServiceSelector.vue
├── JobActionsMenu.vue
├── JobResumeCard.vue
└── JobCompletionChecklist.vue
```

### 19.3 Photo Components

```text
components/media/
├── PhotoCapture.vue
├── PhotoUploader.vue
├── PhotoGrid.vue
├── PhotoCard.vue
├── PhotoStageSelector.vue
├── PhotoPairSelector.vue
├── PhotoReorderList.vue
├── PhotoPreviewModal.vue
├── PhotoUploadProgress.vue
├── PhotoQualityWarning.vue
└── PrimaryPhotoBadge.vue
```

### 19.4 Voice Components

```text
components/voice/
├── VoiceRecorder.vue
├── VoiceRecorderControls.vue
├── VoiceWaveform.vue
├── VoicePlayback.vue
├── VoiceUploadProgress.vue
├── TranscriptEditor.vue
├── TranscriptStatus.vue
└── VoicePromptCards.vue
```

### 19.5 Generation Components

```text
components/generation/
├── GenerateContentButton.vue
├── GenerationProgress.vue
├── GenerationWarnings.vue
├── ToneSelector.vue
├── LengthSelector.vue
├── CustomInstructionField.vue
└── GenerationHistory.vue
```

### 19.6 Review Components

```text
components/content/
├── ContentReviewWorkspace.vue
├── ContentVariantTabs.vue
├── ContentEditor.vue
├── ContentPreview.vue
├── ContentVersionSelector.vue
├── ApproveButton.vue
├── RejectButton.vue
├── RegenerateButton.vue
├── RegenerateDialog.vue
├── PlatformPreview.vue
├── HashtagEditor.vue
├── CallToActionEditor.vue
├── SelectedMediaStrip.vue
└── ApprovalStatusBanner.vue
```

### 19.7 Publishing Components

```text
components/publishing/
├── PublishingDestinationSelector.vue
├── SocialConnectionCard.vue
├── SocialConnectionStatus.vue
├── PublishNowButton.vue
├── SchedulePostForm.vue
├── PublicationStatusList.vue
├── PublicationStatusCard.vue
├── RetryPublicationButton.vue
└── PublishConfirmation.vue
```

### 19.8 Directory Components

```text
components/directory/
├── ContractorProfileEditor.vue
├── ContractorProfilePreview.vue
├── DirectoryListingEditor.vue
├── DirectoryListingPreview.vue
├── DirectoryListingCard.vue
├── DirectoryStatusBadge.vue
├── BeforeAfterGallery.vue
├── ProjectHero.vue
├── ProjectDetails.vue
├── ContractorContactCard.vue
├── LeadForm.vue
├── LocalDirectoryFilters.vue
└── DirectorySearchResults.vue
```

### 19.9 Onboarding Components

```text
components/onboarding/
├── OnboardingStepper.vue
├── CompanyDetailsForm.vue
├── ServicesForm.vue
├── ServiceAreasForm.vue
├── BrandToneForm.vue
├── SocialConnectionsForm.vue
└── OnboardingComplete.vue
```

---

## 20. Nuxt Composables

```text
composables/
├── useApi.ts
├── useAuth.ts
├── useCompany.ts
├── useJobs.ts
├── useJob.ts
├── useJobMedia.ts
├── useVoiceRecorder.ts
├── useTranscription.ts
├── useGeneration.ts
├── useContentReview.ts
├── usePublishing.ts
├── useDirectory.ts
├── useNotifications.ts
├── useUpload.ts
├── usePolling.ts
└── usePermissions.ts
```

### 20.1 useApi

Responsibilities:

- Base URL
- Auth headers or cookie mode
- Error normalization
- Request cancellation
- Idempotency header support
- Retry only for safe requests

### 20.2 useJob

Responsibilities:

- Fetch Job
- Update Job
- Track dirty state
- Resume workflow
- Compute next recommended action
- Expose permissions

### 20.3 useVoiceRecorder

Responsibilities:

- Media permission
- Recorder lifecycle
- Elapsed time
- Blob creation
- Playback URL
- Cleanup
- Upload trigger

### 20.4 usePolling

Use for:

- Transcription status
- Generation status
- Media processing
- Publication status

Allow future replacement with WebSockets or server-sent events.

---

## 21. Pinia Stores

```text
stores/
├── auth.ts
├── company.ts
├── jobs.ts
├── activeJob.ts
├── notifications.ts
└── ui.ts
```

Avoid storing large media blobs in Pinia.

Use local component state for recording blobs and temporary uploads.

---

## 22. Primary Frontend User Flows

### 22.1 Quick Create Job

Screen behavior:

- Large **Create Job** button
- Immediately open camera or photo chooser
- Require no title initially
- Save automatically after first upload
- Assign default title such as `Untitled Painting Job`
- Display clear **Finish Later** option

### 22.2 Resume Incomplete Job

Dashboard should show:

- Most recent incomplete Job
- Current stage
- Next action
- Large **Continue Job** button

Examples:

- Add after photos
- Record work summary
- Review generated content
- Publish approved content

### 22.3 Review Loop

Review workspace should show:

- Before-and-after images
- Generated copy
- Edit mode
- Approve
- Reject
- Regenerate
- Version history

Keep the primary actions visible on mobile.

### 22.4 Publish Flow

The publish screen should show:

- Approved social content
- Selected platforms
- Directory publish toggle
- Publish now or schedule
- Final confirmation

Default directory publication to enabled, but allow the user to disable it before publishing.

---

## 23. Public Directory Frontend

Use Nuxt server-side rendering for directory pages.

### 23.1 Public Contractor Page

Must include:

- Company name
- Logo
- Services
- Service areas
- Contact actions
- Recent projects
- Before-and-after gallery
- Website link
- Lead form

### 23.2 Public Project Page

Must include:

- Project title
- Contractor
- City or local area
- Service type
- Before-and-after media
- Project summary
- Work completed
- Optional homeowner advice
- Contact CTA
- Related projects
- Contractor profile link

### 23.3 SEO Requirements

Use Nuxt SEO metadata for:

- Title
- Description
- Canonical URL
- Open Graph
- Twitter card
- Local business structured data
- Project structured data where appropriate

Generate server-rendered pages.

---

## 24. Background Tasks

Create workers for:

- Image processing
- Audio normalization
- Transcription
- Structured extraction
- Content generation
- Social publishing
- Publication status checks
- Directory publishing
- Notification delivery
- SEO metadata generation
- Cleanup of abandoned uploads

### 24.1 Retry Policy

Use exponential backoff.

Do not retry:

- Permanent validation failures
- Permission failures
- Unsupported media
- Rejected provider credentials

Retry:

- Network failures
- Provider timeouts
- Rate limits
- Temporary storage failures

---

## 25. Notifications

Initial notification events:

- Job created
- Before photos saved
- After photos missing
- Voice summary missing
- Transcription complete
- Generation complete
- Generation failed
- Content approved
- Social post published
- Social publication failed
- Directory listing published
- Directory listing failed
- Connection expired

Initial channels:

- In-app
- Email

SMS can be added later.

---

## 26. Security Requirements

### 26.1 Credentials

- Encrypt third-party tokens at rest
- Never expose tokens to frontend
- Rotate encryption keys
- Use environment secret management

### 26.2 Upload Security

- Signed upload URLs
- File type validation
- File size limits
- Malware scanning where practical
- Random storage keys
- No public bucket access

### 26.3 Authorization

- Company scoping on every protected entity
- Role checks
- Audit approval and publication
- No insecure direct object references

### 26.4 Public Privacy

- Strip EXIF GPS data
- Do not expose precise addresses
- Do not expose private customer fields
- Public listing schema should be separate from internal Job schema

---

## 27. Observability

Implement:

- Structured JSON logs
- Request IDs
- User and company IDs in logs when safe
- Background task IDs
- Generation run IDs
- Publication IDs
- Error monitoring
- API latency metrics
- Task success rates
- Provider error rates
- Health endpoints

Endpoints:

```text
GET /health/live
GET /health/ready
```

---

## 28. Testing Requirements

### 28.1 Backend

Use:

- Pytest
- Async test client
- Test database
- Factory fixtures
- Mock AI provider
- Mock publishing provider
- Mock object storage

Test:

- Auth
- Company scoping
- Role permissions
- Job state transitions
- Photo minimum rules
- Transcript editing
- Generation idempotency
- Approval rules
- Publication idempotency
- Directory privacy
- Public endpoint filtering

### 28.2 Frontend

Use:

- Vitest
- Vue Test Utils
- Playwright

Test:

- Quick Job creation
- Upload progress
- Resume Job
- Voice recording state
- Review loop
- Approval
- Publish flow
- Directory rendering
- Mobile layouts

### 28.3 End-to-End Golden Flow

The primary E2E test must:

1. Register user
2. Create company
3. Create Job
4. Upload before photo
5. Save and leave
6. Return to Job
7. Upload after photos
8. Record or upload voice summary
9. Complete transcription
10. Generate content
11. Edit content
12. Reject and regenerate
13. Approve content
14. Publish to mock social provider
15. Publish to directory
16. Verify public project page

---

## 29. Local Development

Provide:

```text
make dev
make test
make lint
make migrate
make seed
```

Docker Compose services:

- web
- api
- worker
- postgres
- redis
- minio
- mailpit

Seed data should include:

- One painting company
- One owner
- One manager
- One crew member
- Several Jobs at different statuses
- One published directory project

---

## 30. Environment Variables

Backend:

```text
APP_ENV
APP_SECRET_KEY
DATABASE_URL
REDIS_URL
S3_ENDPOINT
S3_BUCKET
S3_ACCESS_KEY
S3_SECRET_KEY
S3_PUBLIC_BASE_URL
JWT_SECRET
TOKEN_ENCRYPTION_KEY
AI_PROVIDER
AI_API_KEY
TRANSCRIPTION_PROVIDER
TRANSCRIPTION_API_KEY
PUBLISHING_PROVIDER
PUBLISHING_API_KEY
FRONTEND_URL
EMAIL_PROVIDER
EMAIL_API_KEY
```

Frontend:

```text
NUXT_PUBLIC_API_BASE_URL
NUXT_PUBLIC_APP_URL
NUXT_PUBLIC_DIRECTORY_URL
```

---

## 31. Deployment

Recommended MVP deployment:

- Nuxt app on container platform
- FastAPI app on container platform
- Separate worker container
- Managed PostgreSQL
- Managed Redis
- S3-compatible storage
- CDN for public media
- HTTPS only

Deployment must support:

- Zero-downtime API rollout
- Database migration job
- Worker restart
- Health checks
- Rollback

---

## 32. Phased Build Plan

### Phase 1: Foundation

Build:

- Repository
- CI
- Auth
- Companies
- Users
- Roles
- PostgreSQL
- Object storage
- Basic Nuxt shell

Acceptance:

- User can register
- Company can be created
- Protected app loads
- Roles work

### Phase 2: Job Capture

Build:

- Job model
- Job state machine
- Quick create
- Photo upload
- Before and after labels
- Resume workflow
- Mobile dashboard

Acceptance:

- User can create Job
- Upload at least three photos
- Leave and return
- See next action

### Phase 3: Voice and Transcription

Build:

- Voice recorder
- Audio upload
- Transcription task
- Transcript editor
- Status polling

Acceptance:

- User can record
- Transcript appears
- Transcript can be corrected

### Phase 4: AI Generation

Build:

- AI abstraction
- Structured extraction
- Content bundle generation
- Generation status
- Warnings

Acceptance:

- Completed Job produces required content variants

### Phase 5: Human Review

Build:

- Review workspace
- Inline editing
- Reject
- Regenerate
- Version history
- Approval

Acceptance:

- User can loop until satisfied
- No unapproved content can publish

### Phase 6: Directory

Build:

- Contractor profile
- Directory listing
- Public project page
- Before-after gallery
- SEO metadata
- Unpublish control

Acceptance:

- Approved Job can create a public directory page

### Phase 7: Social Publishing

Build:

- Provider adapter
- Account connections
- Publish now
- Scheduling
- Status
- Retry

Acceptance:

- Approved social content publishes through mock and production provider

### Phase 8: Hardening

Build:

- Notifications
- Audit logs
- Admin moderation
- Billing hooks
- Error monitoring
- Performance improvements

---

## 33. Definition of Done for MVP

The MVP is done when a real contractor can:

1. Register
2. Create a company profile
3. Create a Job in under one minute
4. Upload before photos
5. Save and leave
6. Return after completing the work
7. Upload after photos
8. Store at least three photos total
9. Record a voice summary
10. Receive a transcript
11. Generate social and directory content
12. Reject or edit the generated content
13. Regenerate content
14. Approve the final version
15. Publish through a third-party provider
16. Publish to the JobPulse-owned local directory
17. View publication status
18. Open the public directory project page

---

## 34. Agent Implementation Rules

The coding agent must:

- Build vertical slices
- Keep the application runnable after each phase
- Add tests with every feature
- Avoid placeholder logic in core flows
- Use provider interfaces for AI and publishing
- Preserve content and generation history
- Use explicit state transitions
- Keep mobile UX primary
- Minimize required Job fields
- Never auto-publish unapproved content
- Never implement Facebook group automation
- Treat the owned directory as a first-class product
- Document setup and migration steps
- Keep API contracts typed
- Keep frontend types synchronized with backend schemas

The coding agent should prefer a clean, boring implementation over premature microservices.

---

## 35. First Vertical Slice

The first complete vertical slice should include:

1. User registration
2. Company creation
3. Create Job
4. Upload three photos
5. Label before and after
6. Save and resume
7. Record or upload voice
8. Mock transcription
9. Mock generation
10. Review content
11. Approve
12. Publish to a local development directory page

Social publishing may remain mocked in the first slice, but the provider interface must already exist.

This slice validates the core JobPulse loop before deeper integrations are added.

---

## 36. Final Technical Definition

JobPulse should be built as a mobile-first Nuxt 3 application backed by a FastAPI modular monolith.

The system should center every workflow around a persistent Job containing before-and-after photos and a voice description. AI generates social and directory content from that Job. The contractor remains in control through an explicit review loop. Approved content is then distributed through a replaceable third-party publishing provider and published to the JobPulse-owned local directory.

The technical design must preserve three strategic advantages:

1. Extremely easy Job capture
2. Human-controlled AI generation
3. Ownership of the local directory and its long-term data
