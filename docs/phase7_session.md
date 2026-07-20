# Phase 7 session handoff — Social Publishing

**Status of prior work:** Phases 1–6 are **complete**, tests green, committed and **pushed**.

| Check | Detail |
|---|---|
| Latest product commit | `a407d35` — *Implement Phase 6 directory publishing with unified Publish action.* |
| Remote | `origin/main` on https://github.com/repoman1964/JOBPULSE.git |
| Tests | `make api-test` → **54 passed** (as of handoff) |
| Greenfield only | Work in `api/`, `mobile_app/`, `directory/` — **`legacy/` is reference only** (untracked; do not extend) |

---

## Phases 1–6 complete — what exists

### Product workflow (locked)

```text
Create job (required private name)
  → Before photos OPTIONAL (recommended)
  → After photos REQUIRED (≥1)
  → Voice summary REQUIRED (transcript usable)
  → AI generate (drafts → awaiting_review)     ← Phase 4
  → Contractor review / edit / reject / regenerate until approve  ← Phase 5
  → Publish (single CTA) → directory live      ← Phase 6
  → Same Publish + social destinations         ← Phase 7 (this session)
```

**Approval is always the contractor’s decision** — not the founder/operator.  
**Nothing publishes without contractor approval.** Gate:

- Helper: `api/app/modules/content/service.py` → **`assert_job_publishable(job, variants, counts)`**
- Job status must be `approved` or `published` (re-publish)
- ≥1 social-ish approved variant + `directory_listing` approved
- After photos required; befores soft-warn only

### UX rule (Phase 6 product decision — do not regress)

**One Publish button** — never split into “Publish to directory” vs “Publish to social”.

- Endpoint already exists: `POST /api/v1/jobs/{job_id}/publish`
- Body shape (§10.10):

```json
{
  "social_connection_ids": ["uuid"],
  "publish_to_directory": true,
  "scheduled_for": null
}
```

- Phase 6: directory branch works; **non-empty `social_connection_ids` currently 400s** with `SOCIAL_NOT_AVAILABLE`
- Phase 6: `scheduled_for` currently 400s with `SCHEDULING_NOT_AVAILABLE`
- Phase 7: implement social (+ optional schedule) **on this same path**

Mobile: `mobile_app/app/composables/usePublish.ts` + Publish CTA on `jobs/[id].vue`.

### Privacy (non-negotiable)

- Job **`title`** is private — **never** send to AI, social APIs, or public directory
- Prefer **`body_edited` over `body_generated`** for social body text
- Prefer edited transcript for generation (already)
- Coarse location only on public surfaces
- Do not leak `storage_key`, customer private fields, or raw credentials in API responses
- Use `api/app/modules/jobs/privacy.py` patterns for generation-safe fields

### Directory is first-party (Phase 6) — social is adapter (Phase 7)

| Destination | Mechanism | Phase |
|---|---|---|
| JobPulse directory | Internal `directory` module | 6 done |
| Social networks | `PUBLISHING_PROVIDER` adapter | **7** |

Directory publication must **not** go through the social provider (spec §17).

### API already in place (Phases 1–6)

| Area | Location |
|---|---|
| Auth + company | `api/app/modules/auth/`, `companies/` |
| Job + Media + Voice | `api/app/db/models.py`, `modules/jobs/` |
| AI generation | `api/app/modules/ai_generation/` (mock) |
| Content review | `api/app/modules/content/` |
| Directory publish | `api/app/modules/directory/` |
| Unified publish | `POST /jobs/{id}/publish` in `directory/api.py` → `directory/service.publish_job` |
| Unpublish directory | `POST /jobs/{id}/unpublish-directory`, listing unpublish |
| Public directory | `/public/contractors`, `/public/projects` |
| Migrations | … → phase4 `d4e6a0b3c925` → **phase6** `e5f7b1c4d036` |
| Permissions | `can_create_jobs` (crew+), **`can_approve_and_publish` (manager+)** |
| Config | `AI_PROVIDER=mock`, `TRANSCRIPTION_PROVIDER=mock`, **`PUBLISHING_PROVIDER=mock`** (unused for real work yet) |

**Job / content fields Phase 7 will use:**

- Approved social variants: `primary_social`, `short_caption`, `before_after` (and optionally platform-specific later)
- `effective_body` from content service
- Media after/before images for provider media upload
- Job already becomes `published` when directory goes live; social can attach after or in same publish call

**Not built yet (Phase 7 models):**

- `publishing_connections` (or similar §6.13)
- `publication_jobs` (§6.14) with `destination_type=social` (and optionally record directory publishes too)
- Provider Protocol + mock + production stub
- OAuth / connect account flows (mock can fake connections without real OAuth)

### Mobile already in place

| Area | Location |
|---|---|
| Full capture + generate + review | `mobile_app/app/pages/jobs/[id].vue` |
| **Publish** CTA | same page via `usePublish.ts` |
| Directory URL open / unpublish | same |

Phase 7 should **extend** Publish UX (optional destination checkboxes / connected accounts list under the same Publish button), not add a second primary publish action.

### Directory app

Public SSR pages live — Phase 7 should not require directory app changes unless linking external social posts on the project page (optional, non-goal for MVP).

### Local run

```bash
make infra-up          # Postgres :5433, Redis :6380, MinIO :9000/:9001
make api-migrate
make api-dev           # :8000
make mobile-dev        # :3000
make directory-dev     # :3001
make api-test
```

---

## Phase 7 goal

Publish **approved social content** through a **replaceable publishing provider** (mock first), with account connections, publish-now, basic scheduling, status, and safe retry — all behind the **existing single Publish action**.

### Spec acceptance (from `jobpulse_agent_build_spec.md` §32 Phase 7 + §10.9–10.10 + §16)

- [ ] Provider adapter (`PublishingProvider` Protocol)
- [ ] Account connections
- [ ] Publish now
- [ ] Scheduling
- [ ] Status
- [ ] Retry

**Acceptance line:**

- **Approved social content publishes through mock and production provider**

Also:

- Unapproved jobs still cannot publish (`assert_job_publishable`)
- Private job title never sent to provider payloads
- Idempotent publish / retry (no duplicate external posts)
- Directory remains independent (still first-party)
- Manager+ for publish/connect management

---

## Phase 7 build checklist

### 1. Data model + migration (`api/alembic/versions/` phase7)

Suggested tables (align with build-spec §6.13–6.14):

**`publishing_connections`**

- `id`, `company_id`
- `provider` (e.g. `mock`, later `blotato`)
- `platform` (`facebook`, `instagram`, `google_business`, … — start with a small set)
- `external_account_id`, `display_name`
- `credentials_encrypted` (or mock token blob)
- `status`: `active` | `disconnected` | `error` | `pending`
- `last_verified_at`, `last_error`
- timestamps

**`publication_jobs`**

- `id`, `job_id`, `content_variant_id` (nullable if multi-variant package)
- `destination_type`: `social` | `directory` (directory rows optional; social required)
- `publishing_connection_id` (null for directory)
- `provider`
- `scheduled_for`
- `status`: `pending` | `processing` | `published` | `failed` | `cancelled` | `scheduled`
- `idempotency_key` (unique) — **required** for safe retries
- `provider_request_id`, `provider_response_json`
- `external_url`
- `attempt_count`, `last_error`
- `published_at`
- timestamps

### 2. Publishing module (API)

Suggested package:

```text
api/app/modules/publishing/
  __init__.py
  api.py              # connections + publication status/retry/cancel
  service.py          # orchestrate publish with directory.service
  schemas.py
  privacy.py          # strip private fields from provider payloads
  provider/
    base.py           # Protocol
    mock.py
    factory.py        # PUBLISHING_PROVIDER env
```

#### Connections (§10.9) — manager+

| Endpoint | Behavior |
|---|---|
| `GET /publishing/connections` | List company connections |
| `POST /publishing/connections/start` | Start connect (mock: create fake pending/active connection) |
| `POST /publishing/connections/callback` | OAuth callback stub / mock complete |
| `DELETE /publishing/connections/{id}` | Disconnect |
| `POST /publishing/connections/{id}/verify` | Health check via provider |

#### Publishing (§10.10) — extend existing

| Endpoint | Behavior |
|---|---|
| `POST /jobs/{job_id}/publish` | **Already exists** — extend: if `social_connection_ids`, publish social; if `publish_to_directory`, keep directory path |
| `POST /jobs/{job_id}/schedule` | Same payload + required `scheduled_for` |
| `GET /jobs/{job_id}/publications` | List publication_jobs for job |
| `POST /publications/{id}/retry` | Retry failed with same idempotency rules |
| `POST /publications/{id}/cancel` | Cancel scheduled/pending |

**Orchestration recommendation:**

1. Move or thin-wrap `publish_job` so `publishing.service` owns the unified entry (call `directory.service` for directory branch; own social branch)
2. Or keep route in directory router but delegate social to publishing module — prefer **one orchestrator** to avoid split brains

### 3. Provider adapter (§16)

```python
class PublishingProvider(Protocol):
    async def connect_account(...): ...
    async def publish_post(request: PublishRequest) -> PublishResult: ...
    async def schedule_post(request: ScheduleRequest) -> PublishResult: ...
    async def get_status(external_id: str) -> PublishStatus: ...
```

**Mock provider:**

- Accept posts; return fake `external_id` + `external_url`
- Store in-memory or DB response JSON for status
- Fail deterministically when body contains a test marker (optional) for retry tests

**Production provider:** stub class or config-selected real vendor later (`PUBLISHING_API_KEY`). Do not hardcode one vendor deep in domain logic.

### 4. Publish flow (social)

```text
1. assert_job_publishable(...)
2. Load approved social variants (prefer primary_social; else any approved social-ish)
3. Build provider payload via privacy helper (no job.title, no customer PII)
4. For each connection_id (company-scoped, active):
   a. Create publication_jobs row with unique idempotency_key
   b. Call provider.publish_post (or schedule_post)
   c. Update status / external_url / errors
5. If publish_to_directory: existing directory path
6. Job status published + published_at (already set by directory; keep consistent if social-only publish)
```

**Social-only publish:** If directory already published, allow social without re-failing. If directory never published and `publish_to_directory=false`, still allow social-only for approved jobs (product-flexible). Default mobile payload can keep `publish_to_directory: true`.

**Idempotency:** same job + connection + content version → same idempotency key; retries update the same row / do not double-post.

### 5. Mobile UX (still one button)

On `jobs/[id].vue` when ready to publish:

- **Publish** remains the primary CTA
- Optional: list connected accounts with checkboxes (default: all active, or “post to all”)
- Optional: “also update directory” toggle default **on**
- After success: show directory URL (existing) + social publication statuses / external links
- Soft empty state: “Connect a social account” → link to simple account/connections section (can live on Account page for MVP)

Do **not** add a second full-page “Social publish” wizard unless absolutely necessary.

### 6. Tests

- Gate still blocks unapproved publish (social and directory)
- Mock provider receives payload **without** private job title
- Publish creates `publication_jobs` rows; status published
- Retry failed publication does not create duplicate provider posts (idempotency)
- Crew cannot publish / manage connections (403)
- Manager can connect mock account + publish
- Schedule creates scheduled row (mock)
- Cancel scheduled works
- Directory-only publish still works when social_connection_ids empty
- Combined publish: directory + social in one request

### 7. Docs

- README try-it: connect mock account → approve → Publish → see publication status
- Keep PRD/build-spec as source of truth; this file is the agent session brief

---

## Explicit non-goals for Phase 7

- Real multi-platform OAuth with production secrets in CI (mock + interface is enough for MVP green)
- Facebook group automation (product ban)
- Directory feature work (already Phase 6)
- Billing
- Native Capacitor
- Full analytics dashboards
- Real production LLM / transcription (mocks remain fine)

---

## Suggested session prompt (paste into next agent)

```text
Continue JobPulse Phase 7 (Social Publishing).

Greenfield: api/, mobile_app/, directory/. legacy/ is reference only.
Phases 1–6 done on main (commit a407d35+): auth/company, jobs, photos, voice,
AI generation (mock), human review, directory publish with unified Publish CTA.
Publish gate: assert_job_publishable in api/app/modules/content/service.py.
Unified endpoint: POST /jobs/{id}/publish (directory works; social currently 400).

Follow jobpulse_prd.md + jobpulse_agent_build_spec.md §10.9, §10.10, §16, §32 Phase 7.
Also read docs/phase7_session.md.

CRITICAL product rules:
- Contractor approval required; call assert_job_publishable before any publish.
- Job title is private — never send to social provider payloads.
- Prefer body_edited over body_generated for social text.
- ONE Publish button — extend existing publish, do not add a second primary CTA.
- Directory stays first-party (directory module); social uses PUBLISHING_PROVIDER adapter.
- Publish/connect requires manager+ (can_approve_and_publish).
- Idempotent publication_jobs + safe retry (no duplicate external posts).

Build:
- Models + migration: publishing_connections, publication_jobs
- PublishingProvider Protocol + mock + factory (PUBLISHING_PROVIDER)
- Connections APIs + extend publish/schedule/publications/retry/cancel
- Mobile: account connections + Publish still single CTA with optional destinations
- Tests green (privacy + gate + idempotent retry + roles)

Acceptance: approved social content publishes through mock provider; unapproved cannot.
```

---

## File map to create/touch (expected)

```text
api/alembic/versions/*_phase7_publishing.py
api/app/db/models.py
api/app/modules/publishing/
  __init__.py, api.py, service.py, schemas.py, privacy.py
  provider/base.py, mock.py, factory.py
api/app/modules/directory/service.py   # share/orchestrate with publishing; do not weaken gate
api/app/main.py
api/app/core/config.py                 # PUBLISHING_API_KEY if needed
api/app/tests/test_publishing.py
mobile_app/app/composables/usePublish.ts
mobile_app/app/composables/usePublishingConnections.ts
mobile_app/app/pages/jobs/[id].vue
mobile_app/app/pages/account.vue       # optional connections UI
README.md
```

---

## Done definition for Phase 7

1. Manager+ can connect a mock social account.  
2. Approved job **Publish** can post to mock social (with or without directory).  
3. Publication history/status visible per job.  
4. Failed publish can retry safely (no duplicates).  
5. Schedule + cancel work for mock.  
6. Unapproved jobs fail publish (gate).  
7. Private job title never in provider request payloads.  
8. Still one primary Publish action in the contractor app.  
9. `make api-test` green; changes committed (push when asked).  

---

## Third-party vendors (context)

| Role | Env | Phase |
|---|---|---|
| Voice → text | `TRANSCRIPTION_PROVIDER` | 3 (mock) |
| AI generation | `AI_PROVIDER` | 4 (mock) |
| Social poster | **`PUBLISHING_PROVIDER`** | **7** |
| Directory | first-party JobPulse | 6 done |

---

## Phase 7 in one line

**Extend the existing single Publish action so approved social content goes out through a replaceable mock/production provider — with connections, status, schedule, and safe retry — without reintroducing destination-split UX or leaking private job titles.**
