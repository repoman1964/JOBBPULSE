# JobbPulse single-engine merge spec

**Status:** Canonical engineering decision  
**Date:** 2026-08-29  
**Repo:** `repoman1964/JOBBPULSE`  
**Audience:** The agent that executes the merge after the 5:30 reset

When this file disagrees with older stack notes, **this file wins** for architecture.  
When this file disagrees with `docs/biz_docs/usp.md` on *what an approved job publishes*, **USP wins**.

---

## 1. Decision

There is one backend: **`api/`**.

`contractor_app/` is a **frontend-only** contractor tool.

`contractor_app/backend/` is not a product. It is a reference implementation of phone-shaped routes, Upload-Post, R2 presign, package/revision, and submit/approve pipelines. Port the missing behavior into `api/`, then stop running that service.

Do not create a third API, a BFF, or a sync job between two Postgres databases.

```
Contractor Nuxt  ──HTTP──►  api/ (FastAPI + Postgres + Redis + R2)
                                │
                                ├─► JobbPulse Engine (generation, revisions)
                                ├─► Directory / portfolio_website
                                ├─► Conversion site job pages (Red Clay pattern)
                                └─► Upload-Post (FB / IG / GBP / groups)
```

---

## 2. Why this merge exists

Today:

- `website/portfolio_website` and public directory talk to **`api/`**.
- The live contractor phone app talks to **`contractor_app/backend`**.
- `render.yaml` deploys the contractor engine, not `api/`.
- A finished job in the app cannot appear on the owned portfolio without a second write path.

That split is the whole problem. One job record must be the record the directory publishes.

---

## 3. Non-negotiable product rules

From README + `docs/biz_docs/usp.md`. Do not reopen during the merge.

1. The **Job** is the core object.
2. Capture stays photos + ~30s voice. No extra contractor dashboard work.
3. Human approval before first distribution of a job package.
4. One approve publishes the locked set:
   - Facebook Page
   - Instagram
   - Google Business Profile
   - 3–5 local homeowners groups
   - Contractor website home carousel
   - Contractor website job page
   - JobbPulse directory project page
5. Evergreen cadence is engine/ops, not an app calendar.
6. Public location is city / neighborhood only. No exact address, no GPS on public pages.
7. **Job name is contractor-only.** Never send it to AI, social, directory, notifications, or audit payloads.
8. Contractor app must not become CRM, dispatch, invoicing, or a per-group composer.

---

## 4. Source of truth vs reference

### Keep and extend

| Path | Role after merge |
|---|---|
| `api/` | Only FastAPI app, only Alembic history going forward, only production Docker API |
| `api/app/db/models.py` | Canonical schema. Add columns/tables here. |
| `website/portfolio_website/` | Public portfolio. Keep reading `api/` public directory routes. |
| `website/red_clay_website/` | Conversion-site demo. Keep reading public job payloads from `api/`. |
| `contractor_app/frontend/` | Only contractor UI. Talks to `api/` via `HttpApiClient`. |
| `infra/docker-compose.yml` | Postgres / Redis / MinIO / Mailpit for `api/` |
| `docs/biz_docs/usp.md` | Offer destinations |

### Reference only (port, then freeze)

| Path | Port from here |
|---|---|
| `contractor_app/backend/app/api/v1/*` | Phone route shapes the frontend already calls |
| `contractor_app/backend/app/services/engine.py` | Submit → generate package pipeline |
| `contractor_app/backend/app/integrations/upload_post/` | Real social connect/publish client |
| `contractor_app/backend/app/integrations/storage/s3.py` | R2/S3 presign PUT + GET |
| `contractor_app/backend/app/integrations/email/resend.py` | Signup verification email |
| `contractor_app/backend/app/services/job_delete.py` | Soft-delete semantics |
| `contractor_app/frontend/app/services/api/client.ts` | **Contract the API must satisfy** |
| `contractor_app/frontend/app/types/domain.ts` | Field names the UI already uses |

### Do not port as-is

- Duplicate SQLAlchemy models in `contractor_app/backend/app/models/`
- Fake content-gen that cannot write directory listings
- Second Celery app as the long-term worker (one worker process against `api/`)
- OTP-as-primary-auth (keep password + email verify; OTP may remain as a later add-on)
- Per-destination toggles in the finish-job flow

---

## 5. Frontend contract (do not redesign screens)

`contractor_app/frontend/app/services/api/client.ts` is the interface.

`HttpApiClient` already calls these paths. After merge, **`api/` must implement them** (canonical or alias). The UI does not change page flow.

### Auth

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/verify-email`
- `POST /api/v1/auth/resend-verification`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me` → session with `accessToken`

### Company

- `GET /api/v1/company`
- `PATCH /api/v1/company`
- `PATCH /api/v1/company/settings`

### Jobs

- `GET /api/v1/jobs?status&cursor`
- `POST /api/v1/jobs`
- `GET /api/v1/jobs/{jobId}`
- `PATCH /api/v1/jobs/{jobId}`
- `DELETE /api/v1/jobs/{jobId}`  (soft-delete; hide from list; keep media + published pages)
- `POST /api/v1/jobs/{jobId}/submit`  `{ idempotencyKey }`

### Media / voice

- `POST /api/v1/jobs/{jobId}/media/upload-sessions`
- `POST /api/v1/jobs/{jobId}/media/{mediaId}/complete`
- `GET /api/v1/jobs/{jobId}/media?category`
- `PATCH /api/v1/jobs/{jobId}/media/{mediaId}`
- `DELETE /api/v1/jobs/{jobId}/media/{mediaId}`
- `POST /api/v1/jobs/{jobId}/voice/upload-sessions`
- `POST /api/v1/jobs/{jobId}/voice/{mediaId}/complete`
- `GET /api/v1/jobs/{jobId}/voice`

### Package / publish

- `GET /api/v1/jobs/{jobId}/package`
- `PATCH /api/v1/jobs/{jobId}/package/featured-media`
- `POST /api/v1/jobs/{jobId}/package/description-revision`
- `GET /api/v1/generated-assets/{assetId}`
- `POST /api/v1/generated-assets/{assetId}/revisions`
- `POST /api/v1/generated-assets/{assetId}/select-version`
- `POST /api/v1/jobs/{jobId}/approve-and-publish`  `{ idempotencyKey }`

### Social

- `GET /api/v1/social/connections`
- `PUT /api/v1/social/connections/{platform}`
- `POST /api/v1/social/connections/{platform}/disconnect`
- `POST /api/v1/social/connect-url`

Existing `api/` routes that already do similar work (`/jobs/{id}/media/upload-url`, `/content/{id}`, `/jobs/{id}/publish`, `/publishing/connections`) stay. Add **thin aliases** that match the phone client. Do not force a screen rewrite in the same PR as the data merge.

---

## 6. Response envelope

`api/` returns:

```json
{ "data": { ... }, "meta": { "request_id": "..." }, "error": null }
```

Errors:

```json
{ "data": null, "meta": {}, "error": { "code": "...", "message": "...", "details": {} } }
```

`HttpApiClient` today treats the JSON body as the resource and reads `code` / `message` at the top level.

**Required frontend change (small, mandatory):**

1. On success, unwrap `body.data` (and map snake_case → camelCase if the payload is still snake).
2. On error, read `body.error.code` and `body.error.message`.
3. Keep `Authorization: Bearer` + `jp.accessToken`.
4. Keep loopback proxy behavior in `resolveEngineApiBase` so phones on LAN still work.

Do not drop the envelope on `api/`. Portfolio and tests already depend on it.

---

## 7. Auth model

### Target

- Email + password register / login on `api/` (already exists).
- Email verification before login (port Resend flow from contractor engine).
- JWT access token. Refresh token may stay body-based (`api/` already has `/auth/refresh`) plus optional cookie later.
- Company membership on `api/` User + Membership is the identity. Map UI `contractor` to that user.

### Mapping

| Phone field | `api/` field |
|---|---|
| `accessToken` | `data.access_token` |
| `contractor.id` | `data.user.id` |
| `contractor.email` | `data.user.email` |
| `contractor.name` | `data.user` display name (add if missing) |
| `company.id` | `data.company.id` |
| `company.name` | `data.company.name` |

### Port

- `register` creates User + Company + owner Membership, sends verify email, does **not** return a usable session until verified (match current contractor UX).
- `verify-email` + `resend-verification`.
- Dev-only: return `verificationUrl` when `RETURN_VERIFICATION_URL_TO_CLIENT=true`.

### Do not block merge on

- Phone OTP challenge (`/auth/challenge`, `/auth/verify`). Leave unimplemented on `api/` unless signup already depends on it in production. Password path is enough for merge.

---

## 8. Job and media model gaps to close on `api/`

`api/` already has jobs, media upload-url/complete, voice upload-url/complete, list/delete/archive.

Add or confirm:

| Need | Notes |
|---|---|
| Soft-delete | `deleted_at`. List excludes deleted. Published directory pages stay unless unpublished. |
| Photo categories | `before`, `progress`/`during`, `after`. Phone uses `progress`. Map `during` ↔ `progress`. |
| Photo minimums | Company JSON minimums; submit rejects if unmet. |
| Voice required on submit | Same as contractor engine. |
| Idempotent submit | `JobSubmission.idempotency_key`. Replay returns current job. |
| Public vs internal status | Phone statuses: `active`, `ready_to_finish`, `processing`, `ready_for_approval`, `needs_revision`, `publishing`, `published`, `publish_issue`. Map onto existing `api/` job state machine; do not invent a second status field if one can be extended. |
| Job name privacy | Keep name off public serializers and AI inputs. |
| Coarse location | city, region, neighborhood. No street on public payloads. |
| Featured before/after media ids | Needed for package + directory hero. |
| Cursor pagination | Phone sends `cursor`. `api/` today uses `limit/offset`. Support `cursor` on the alias list route. |

---

## 9. Content package vs content variants

Two vocabularies, one job.

| Phone (`ContentPackage` / `GeneratedAsset`) | `api/` today |
|---|---|
| Package per submission version | Content variants per destination |
| Asset versions + select-version | Variant edit + regenerate |
| `approve-and-publish` | `approve` / `approve-all` then `publish` |

### Target behavior

Keep the phone mental model. Implement package endpoints as a facade over `api/` generation + content + publishing.

On submit:

1. Snapshot media + voice (no job name in AI payload).
2. Transcribe voice (provider flag; mock allowed).
3. Generate destination assets for the locked USP set.
4. Persist as a package (new table) **or** as a labeled set of content variants with `destination` + `version`.
5. Job status → `ready_for_approval`.

Preferred schema (add to `api/` if missing):

- `content_packages` (job_id, version, status, featured_before_id, featured_after_id)
- `generated_assets` (package_id, destination, status, active_version_id)
- `generated_asset_versions` (asset_id, title, body, preview_json, payload_json)
- `revision_requests` (job_id, asset_id nullable, change_type, instruction, status)

If `api/` content variants already store version history, map rather than duplicate. Do not keep two generation pipelines.

Destinations for generated assets (minimum):

- `facebook_page`
- `instagram`
- `google_business`
- `facebook_group` (one asset, engine fans out to 3–5 groups)
- `website_carousel`
- `website_job_page`
- `directory_page`

TikTok / Shorts / X / LinkedIn stay out of the paid set.

---

## 10. Publish path

`POST /jobs/{id}/approve-and-publish` must:

1. Require status in `{ ready_for_approval, needs_revision, publish_issue }`.
2. Be idempotent on `idempotencyKey`.
3. Set job → `publishing`.
4. Write **directory project page** through existing `api/` directory module (this is the point of the merge).
5. Upsert conversion-site recent-job payload (same public job record Red Clay already consumes).
6. Fan out social via Upload-Post for connected accounts. Missing connection = skip that destination, do not fail the whole job; surface `publish_issue` only if directory write fails or every social target fails.
7. Job → `published` when directory write succeeds. Social retries use existing `/publications/{id}/retry`.

Port Upload-Post client into `api/app/modules/publishing/provider/upload_post.py`. Keep `PUBLISHING_PROVIDER=mock|upload_post`.

Do not expose destination checkboxes on the finish-job screen.

---

## 11. Social connections

Phone uses `/social/*`. `api/` uses `/publishing/connections`.

Implement `/social/*` as aliases:

- list → publishing connections, shaped as `SocialConnection[]`
- connect-url → `publishing/connections/start` (Upload-Post OAuth URL)
- disconnect → publishing disconnect

Group selection (3–5 groups) is onboarding/ops data on the company, not a composer in the job flow. Store `facebook_group_ids` on company. Engine reads it at publish time.

---

## 12. Storage

Keep S3-compatible storage (`api/app/core/storage.py`).

Phone flow:

1. `upload-sessions` returns `{ mediaId, uploadUrl, headers, objectKey }`.
2. Browser **PUT**s the file to R2/MinIO.
3. `complete` verifies object exists and marks media complete.

`api/` already has `media/upload-url` + `media/complete`. Alias the phone paths. Confirm CORS on the bucket (`contractor_app/backend/r2-cors.json` is the reference).

Multipart `/media/upload` stays as test/fallback only.

---

## 13. Workers

One worker, owned by `api/`.

Tasks:

- transcribe voice
- generate package
- apply revision
- approve-and-publish fan-out
- evergreen cadence (later; do not build calendar UI now)

Local: if broker is down, run the task in-process (contractor engine already does this). Tests must not require Redis.

Point Render worker `dockerContext` at `api/`, not `contractor_app/backend`.

---

## 14. Render / local wiring

### After merge, `render.yaml` must

- Build `jobbpulse-api` from `api/Dockerfile` (or `api/` prod Dockerfile if added).
- Run `alembic upgrade head` from `api/`.
- Worker from `api/` task runner.
- Static `jobbpulse-app` still `contractor_app/frontend`.
- `NUXT_PUBLIC_API_BASE_URL` = public `api/` URL.
- Stop deploying `contractor_app/backend`.

### Local

```bash
make infra-up
make api-install && make api-migrate && make api-dev   # :8000
# frontend
cd contractor_app/frontend
NUXT_PUBLIC_API_MODE=http NUXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

Update `contractor_app/LOCAL_SETUP.md`, root `README.md`, and `Makefile` so `make up` does **not** start a second API on :8000.

`portfolio_website` on :3001 against the same `api/`.

---

## 15. Execution sequence (agent order)

Do these in order. Do not skip to Render until step 7 is green.

### Step 1 — Compatibility layer on `api/`

Add alias routers that match §5 paths. Internally call existing jobs/media/voice/auth/company services. Unwrap not needed server-side.

Add tests that hit the **phone paths**.

### Step 2 — HttpApiClient adapter

Unwrap `{ data }`, map errors, map camelCase session/job/media. Point `NUXT_PUBLIC_API_BASE_URL` at `api/`. Keep mock mode working.

### Step 3 — Auth parity

Email verify + register/login/me shaped for the phone. Seed a demo user that can sign in without mail in development.

### Step 4 — Submit pipeline on `api/`

Port `submit` + generation into `api/` modules (`jobs` + `ai_generation` + new package facade). Job becomes `ready_for_approval` with a package the approval screens can render.

### Step 5 — Approve-and-publish on `api/`

Directory write first, then social mock, then Upload-Post provider behind flag.

### Step 6 — Soft-delete, progress photos, featured media, revisions

Port remaining phone behaviors. Soft-delete must not wipe published directory rows.

### Step 7 — Dual-run proof

Same `api/` process:

- Create job in contractor UI
- Upload before/progress/after + voice
- Submit, approve
- Project appears on `portfolio_website`
- Red Clay recent-jobs can see it when pointed at the same API

### Step 8 — Cut over infra

Update `render.yaml`, Compose, READMEs. Mark `contractor_app/backend` as `REFERENCE_ONLY.md`. Do not delete in the same PR as the first green cutover unless tests are fully moved.

### Step 9 — Move tests

Port contractor backend tests that still encode product rules (submit minimums, privacy, approve idempotency, soft-delete) into `api/app/tests/`. Then freeze the old engine.

---

## 16. Explicitly out of scope for this merge

- GHL / Lead Desk work
- Evergreen cadence scheduler UI
- Capacitor wrapper
- New trades, new destinations
- Rebrand / visual polish
- Migrating production contractor-engine Postgres data (call out as a follow-up if Render already has live rows). If pilot data exists on the contractor-engine DB, write a one-shot copy script; do not dual-write going forward.
- Building a new frontend API client interface — extend `ApiClient`, do not replace it

---

## 17. Acceptance criteria

Merge is done when all of the following are true:

1. Only one API process is required for contractor app + portfolio + Red Clay.
2. `contractor_app/frontend` in HTTP mode talks only to `api/`.
3. `POST /jobs/{id}/submit` then `POST /jobs/{id}/approve-and-publish` creates a public directory project.
4. Job name never appears in generation inputs, social payloads, directory JSON, or audit bodies.
5. Public pages show city/neighborhood only.
6. Soft-deleted jobs disappear from the contractor list and remain absent from new homepage galleries; already-published pages are unpublished or remain until an explicit unpublish (pick one, document it, test it). **Recommended:** unpublish directory listing on soft-delete.
7. `make api-test` passes. Frontend unit tests for `HttpApiClient` unwrap still pass.
8. README no longer says “contractor UI is not wired to `api/`.”
9. `render.yaml` does not reference `contractor_app/backend` as the API image.

---

## 18. Suggested first PR titles

1. `api: phone-compatible auth/job/media aliases + envelope docs`
2. `contractor-app: HttpApiClient unwraps api/ envelope`
3. `api: submit + package facade + approve-and-publish writes directory`
4. `infra: Render and Compose serve api/ only; freeze contractor_app/backend`

---

## 19. Command the executing agent should follow

> Implement this spec against `repoman1964/JOBBPULSE`. Do not start a new backend. Do not redesign the contractor screens. Make `api/` satisfy `contractor_app/frontend/app/services/api/client.ts`, then point the frontend at it, then prove one approved job appears on `website/portfolio_website`.
