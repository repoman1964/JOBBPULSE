# Phase 6 session handoff — Directory Publishing

**Status of prior work:** Phases 1–5 are **complete**, tests green, committed and **pushed**.

| Check | Detail |
|---|---|
| Latest product commit | `137e95d` — *Implement Phase 5 human review: edit, approve, reject, publish gate.* |
| Remote | `origin/main` on https://github.com/repoman1964/JOBPULSE.git |
| Tests | `make api-test` → **43 passed** (as of handoff) |
| Greenfield only | Work in `api/`, `mobile_app/`, `directory/` — **`legacy/` is reference only** (untracked; do not extend) |

---

## Phases 1–5 complete — what exists

### Product workflow (locked)

```text
Create job (required private name)
  → Before photos OPTIONAL (recommended)
  → After photos REQUIRED (≥1)
  → Voice summary REQUIRED (transcript usable)
  → AI generate (drafts → awaiting_review)     ← Phase 4
  → Contractor review / edit / reject / regenerate until approve  ← Phase 5
  → Publish to JobPulse directory              ← Phase 6 (this session)
  → Publish to social networks                 ← Phase 7
```

**Approval is always the contractor’s decision** — not the founder/operator.  
**Nothing publishes without contractor approval.** Phase 5 already enforces the gate via:

- Job status `approved` + `next_action` = `ready_to_publish`
- Required variants: ≥1 social-ish approved + `directory_listing` approved
- After photos required; befores soft-warn only
- Helper: `api/app/modules/content/service.py` → **`assert_job_publishable(job, variants, counts)`**

Phase 6 **must call this gate** (or re-validate the same rules) before creating any public listing.

### Privacy (non-negotiable)

- Job **`title`** is a private contractor label. **Never** send to AI, social, **or public directory**.
- Public project title comes from approved **content variant** (`title` / body), not `jobs.title`.
- Prefer **`body_edited` over `body_generated`** for public summary text.
- Coarse location only (`city`, `state`, `location_display` — **no street addresses**, no precise GPS on public pages).
- Do **not** expose raw storage keys or private customer fields on public APIs.
- Strip EXIF / precise GPS from publicly served images when practical (MVP: serve via signed/public URLs that do not leak private metadata fields in JSON).

### Capture + generation + review rules (product)

| Rule | MVP |
|---|---|
| After photos | Required for approve + publish |
| Before photos | Optional; show in gallery if present |
| Voice / generation | Done in Phases 3–4 |
| Approve | manager+ (`can_approve_and_publish`) |
| Publish to directory | manager+ (same permission) |
| Directory is first-party | **Not** via `PUBLISHING_PROVIDER` / social adapter |

### API already in place (Phases 1–5)

| Area | Location |
|---|---|
| Auth + company | `api/app/modules/auth/`, `companies/` |
| Job + Media + Voice | `api/app/db/models.py`, `modules/jobs/` |
| AI generation | `api/app/modules/ai_generation/` (mock) |
| Content review | `api/app/modules/content/` (edit / approve / reject / approve-all / publish gate) |
| Migrations | phase1 → phase2 → phase3 `c3d5f9a2b814` → phase4 `d4e6a0b3c925` (**no phase5 migration** — reused existing columns) |
| Permissions | `can_create_jobs` (crew+), **`can_approve_and_publish` (manager+)** |
| Config | `AI_PROVIDER=mock`, `TRANSCRIPTION_PROVIDER=mock`, `PUBLISHING_PROVIDER=mock` |

**Job / content fields Phase 6 will use:**

- `Job.status` includes `approved`, `published` (and `scheduled` later)
- `Job.approved_at`, `Job.published_at`
- `ContentVariant` with `content_type=directory_listing`, `status=approved`, `body_edited` / `body_generated`, public `title`
- `MediaAsset` before/after images already on job
- `Company` has `name`, `slug`, `trade`, `description`, `phone`, `website_url`, services, service areas

**Not built yet (Phase 6 models):**

- `contractor_profiles`
- `directory_listings`
- `directory_listing_media`
- Optional: `publication_jobs` row with `destination_type=directory` for audit trail

### Mobile already in place

| Area | Location |
|---|---|
| Full capture + generate + **review workspace** | `mobile_app/app/pages/jobs/[id].vue` |
| Review client | `useContentReview.ts` |
| Generation client | `useGeneration.ts` |
| After approve | UI shows **Ready to publish (coming soon)** — Phase 6 wires real directory publish CTA |

Nuxt **PWA-first** (browser), not native Capacitor for MVP.

### Directory app scaffold (Phase 0)

`directory/` is a separate Nuxt app with **placeholder** routes only:

```text
/contractors/{state}/{city}/{slug}     → stub page
/projects/{state}/{city}/{service}/{slug}  → stub page
```

Phase 6 fills these with **SSR** public data from the API. Do **not** put public pages inside `mobile_app/`.

### Local run

```bash
make infra-up          # Postgres :5433, Redis :6380, MinIO :9000/:9001
make api-migrate
make api-dev           # :8000
make mobile-dev        # :3000 contractor app
# directory app — typically:
cd directory && npm run dev   # often :3001; check package scripts / nuxt config
make api-test
```

---

## Phase 6 goal

Turn an **approved Job** into a **public directory project page** (and ensure a **public contractor profile** exists), with SEO metadata, before/after gallery, and **unpublish** control — all first-party JobPulse, no social provider.

### Spec acceptance (from `jobpulse_agent_build_spec.md` §32 Phase 6 + §17 + §10.11–10.12 + §23)

- [ ] Contractor profile (public)
- [ ] Directory listing (from approved job)
- [ ] Public project page
- [ ] Before-after gallery
- [ ] SEO metadata
- [ ] Unpublish control

**Acceptance line:**

- **Approved Job can create a public directory page**

Also:

- Public URL patterns:
  - `/contractors/{state}/{city}/{contractor-slug}`
  - `/projects/{state}/{city}/{service-key}/{project-slug}`
- Directory publish does **not** use third-party social poster
- Unapproved jobs **cannot** publish (reuse `assert_job_publishable`)
- Private job title never on public pages/APIs

---

## Phase 6 build checklist

### 1. Data model + migration (`api/alembic/versions/` phase6)

Suggested tables (align with build-spec §6.15–6.17):

**`contractor_profiles`**

- `id`, `company_id` (unique)
- `public_slug` (unique, stable)
- `headline`, `public_description`
- `contact_phone`, `contact_email`, `website_url`
- `lead_form_enabled` (bool, default true for MVP form stub ok)
- `published` (bool)
- `seo_title`, `seo_description`
- timestamps

Seed/update profile from company onboarding data when first needed.

**`directory_listings`**

- `id`, `job_id` (unique), `company_id`, `contractor_profile_id`
- `slug` (unique per public path strategy — recommend unique globally or unique per company)
- `public_title`, `public_summary` (from approved directory variant; prefer `body_edited`)
- `service_key`, `location_display`, `city`, `state`, `postal_code` (coarse only)
- `status`: `draft` | `published` | `unpublished` | `flagged` | `removed` (MVP can use published/unpublished)
- `published_at`, `unpublished_at`
- `seo_title`, `seo_description`
- `structured_data_json` (optional JSON-LD payload)
- timestamps

**`directory_listing_media`**

- `id`, `directory_listing_id`, `media_asset_id`
- `stage_label` (`before` | `after`)
- `display_order`

Optional MVP: **`publication_jobs`** row when publishing to directory (`destination_type=directory`) for history; can defer full social-shaped table if a simpler `directory_publish_events` is cleaner — prefer matching §6.14 if time allows.

### 2. Directory module (API)

Suggested package:

```text
api/app/modules/directory/
  api.py          # authenticated admin routes
  public_api.py   # unauthenticated public routes
  service.py
  schemas.py
  privacy.py      # strip private fields from public serializers
```

#### Authenticated (spec §10.11) — manager+ for publish/unpublish

| Endpoint | Behavior |
|---|---|
| `GET /directory/profile` | Company contractor profile (create default if missing) |
| `PATCH /directory/profile` | Edit public headline, description, contact, SEO, published flag |
| `GET /directory/listings` | List company’s listings |
| `GET /directory/listings/{id}` | Detail |
| `PATCH /directory/listings/{id}` | Edit public title/summary/SEO before or after publish |
| `POST /jobs/{job_id}/publish-directory` | **Primary MVP action:** validate gate → create/update listing + media → publish → set job `published` (or keep `approved` if social still pending — see state note) |
| `POST /directory/listings/{id}/publish` | Publish / re-publish draft or unpublished listing |
| `POST /directory/listings/{id}/unpublish` | Unpublish; public page 404 or “unavailable” |

Also fine: `POST /jobs/{id}/publish` with `{ "publish_to_directory": true }` if you want closer to §10.10 — but **social half is Phase 7**. Prefer a clear directory-only path for Phase 6.

#### Public (spec §10.12) — no auth

| Endpoint | Behavior |
|---|---|
| `GET /public/contractors` | List published profiles (filter city/state/trade; paginate lightly) |
| `GET /public/contractors/{slug}` | Profile + recent published projects |
| `GET /public/projects` | List published projects (filters optional) |
| `GET /public/projects/{slug}` **or** by path segments | Project detail + media + contractor link |
| `POST /public/leads` | Optional MVP stub: accept name/email/message + contractor slug; store or log; do not require full CRM |

Public serializers must **never** include: private job title, customer_name_private, notes, raw transcripts, internal ids beyond what’s needed, storage_key secrets.

### 3. Publish flow (service)

```text
1. Load job (company-scoped) + variants + media
2. assert_job_publishable(...)
3. Require approved directory_listing variant still approved (not superseded)
4. Ensure contractor_profile exists + has public_slug; ensure profile.published or auto-publish profile with company defaults
5. Build public_title / public_summary from directory variant (body_edited or body_generated)
6. Generate project slug (lowercase, human, stable; no customer names / street addresses)
7. Upsert directory_listings + link before/after media (all ready afters; befores if any)
8. Generate SEO title/description + optional JSON-LD
9. status=published, published_at=now
10. Update job: published_at; status → published (see state note)
11. Return public_url paths for directory app
```

**Slug rules (§17.3):** lowercase, human readable, stable, unique; avoid customer names and precise addresses. Prefer service + city + short unique suffix from job id fragment.

**Idempotency:** Re-publishing the same job updates the existing listing (do not create duplicates).

### 4. Job state (`jobs/state.py`)

| Condition | next_action | job status |
|---|---|---|
| Approved, not yet directory-published | `ready_to_publish` or `publish_directory` | `approved` |
| Directory published (social still Phase 7) | `view_published` or `publish_social` (coming soon) | Prefer **`published`** once directory is live, **or** keep `approved` + flag on listing — pick one and document. Recommended MVP: set `Job.status=published` + `published_at` when directory goes live; Phase 7 adds social publications without blocking directory. |
| Unpublish listing | Public gone; job may return to `approved` **or** stay `published` with listing unpublished — recommended: job stays `published` historically; listing `unpublished` controls public visibility |

Do **not** allow frontend to set arbitrary status.

### 5. Privacy helpers

Extend or add:

```text
api/app/modules/directory/privacy.py
  public_project_payload(...)
  public_contractor_payload(...)
```

Assert private job `title` is never in public JSON. Reuse coarse location fields only.

### 6. Directory Nuxt app (`directory/`)

SSR (Nuxt) pages that fetch public API:

| Route | Content |
|---|---|
| `/` | Simple browse/search landing (city/trade optional MVP) |
| `/contractors/[state]/[city]/[slug]` | Profile, services, areas, recent projects, contact CTA |
| `/projects/[state]/[city]/[service]/[slug]` | Project title, summary, before/after gallery, contractor link, SEO |

Requirements:

- `useSeoMeta` / OG tags from API seo fields
- Before/after gallery (show after always; before if present)
- No private job name
- Graceful 404 for unpublished/missing

Wire `runtimeConfig.public.apiBase` like mobile app.

### 7. Mobile contractor UX (minimal)

On `jobs/[id].vue` when `ready_to_publish` / `approved`:

- **Publish to directory** button (manager+)
- Show public URL after success (open in new tab)
- **Unpublish** if listing exists and is published
- Soft message: social publish is Phase 7

Optional light screen: list company’s directory listings — can be a simple section on job or account page; not a full admin portal.

### 8. Tests

- Publish blocked when job not approved (`assert_job_publishable` / API 400)
- Publish blocked without approved directory variant
- Publish succeeds without before photos (afters present)
- Public project JSON never contains private job title
- Public project shows effective body (`body_edited` preferred)
- Unpublish removes from public GET (404)
- Re-publish is idempotent (one listing per job)
- Crew cannot publish (403); manager/owner can
- Profile slug stable / unique

### 9. Docs

- README try-it: approve → publish to directory → open public project URL
- Keep PRD/build-spec as source of truth; this file is the agent session brief

---

## Explicit non-goals for Phase 6

- Social connections / Blotato-class poster — **Phase 7**
- Scheduling social posts  
- Real production LLM / transcription (mocks remain fine)  
- Native Capacitor  
- Full lead CRM / email delivery (stub form OK)  
- Advanced directory search/map/filters (basic list is enough)  
- Admin moderation console for founder (unpublish by contractor is enough; flagged/removed enums can exist unused)  
- Billing  

---

## Suggested session prompt (paste into next agent)

```text
Continue JobPulse Phase 6 (Directory Publishing).

Greenfield: api/, mobile_app/, directory/. legacy/ is reference only.
Phases 1–5 done on main (commit 137e95d+): auth/company, jobs, photos, voice,
AI generation (mock), human review → job can reach approved / ready_to_publish.
Publish gate: assert_job_publishable in api/app/modules/content/service.py.

Follow jobpulse_prd.md + jobpulse_agent_build_spec.md §10.11, §10.12, §17, §23, §32 Phase 6.
Also read docs/phase6_session.md.

CRITICAL product rules:
- Contractor approval required; call assert_job_publishable before any public listing.
- Job title is private — never on public directory pages/APIs.
- Prefer body_edited over body_generated for public summary.
- Before photos optional in gallery; after required.
- Directory is first-party JobPulse — not the social PUBLISHING_PROVIDER.
- Publish/unpublish requires manager+ (can_approve_and_publish).

Build:
- Models + migration: contractor_profiles, directory_listings, directory_listing_media
- Admin APIs: profile, listings, publish/unpublish, job publish-directory
- Public APIs: contractors, projects (SSR-friendly)
- Directory Nuxt SSR pages for contractor + project URLs
- Mobile: publish to directory CTA when approved + show public URL
- Tests green (privacy + gate + unpublish)

Acceptance: approved Job can create a public directory project page; unapproved cannot.
```

---

## File map to create/touch (expected)

```text
api/alembic/versions/*_phase6_directory.py
api/app/db/models.py                    # contractor_profiles, directory_listings, media links
api/app/modules/directory/
  __init__.py, api.py, public_api.py, service.py, schemas.py, privacy.py
api/app/main.py                         # register routers
api/app/modules/jobs/state.py           # published / publish_directory next_actions
api/app/modules/content/service.py      # reuse assert_job_publishable (do not weaken)
api/app/tests/test_directory.py
directory/app/pages/...                 # real SSR pages + API fetch
directory/nuxt.config.ts                # apiBase
mobile_app/app/pages/jobs/[id].vue      # publish CTA
mobile_app/app/composables/useDirectory.ts   # optional
README.md
```

---

## Done definition for Phase 6

1. Manager+ can publish an **approved** job to the JobPulse directory.  
2. Public project page renders with title, summary, city, service, before/after gallery, contractor link.  
3. Public contractor profile page lists published projects.  
4. SEO meta present on public pages.  
5. Unpublish hides the project from public API/pages.  
6. Unapproved jobs fail publish (gate).  
7. Private job title never appears on public responses or pages.  
8. `make api-test` green; changes committed (push when asked).  

---

## Third-party vendors (context)

| Role | Env | Phase |
|---|---|---|
| Voice → text | `TRANSCRIPTION_PROVIDER` | 3 (mock) |
| AI generation | `AI_PROVIDER` | 4 (mock) |
| Social poster | `PUBLISHING_PROVIDER` | **7** — not used for directory |
| Directory | first-party JobPulse | **6** |

---

## Phase 6 in one line

**Take contractor-approved content and put it on a real public JobPulse local directory page — with privacy, SEO, gallery, and unpublish — without touching social networks yet.**
