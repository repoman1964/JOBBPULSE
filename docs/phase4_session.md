# Phase 4 session handoff — AI Generation

**Status of prior work:** Phase 3 is **complete**, tests green, committed and **pushed**.

| Check | Detail |
|---|---|
| Commit | `a8caa03` — *Implement Phase 3 voice capture with mock transcription.* |
| Remote | `origin/main` on https://github.com/repoman1964/JOBPULSE.git |
| Tests | `make api-test` → **28 passed** (as of handoff) |
| Greenfield only | Work in `api/`, `mobile_app/`, `directory/` — **`legacy/` is reference only** (untracked; do not extend) |

---

## Phase 3 complete — what exists

### Product workflow (locked)

```text
Create job (required private name)
  → Before photos OPTIONAL (recommended)
  → After photos REQUIRED (≥1)
  → Voice summary REQUIRED (transcript usable)
  → AI generate          ← Phase 4 builds this
  → Contractor review / revise until they approve  (Phase 5)
  → Publish social + directory  (Phases 6–7)
```

**Approval is always the contractor’s decision** — not the founder/operator. If they don’t like the output, they regenerate/edit until they approve. Nothing publishes without contractor approval (Phase 5 enforces the gate; Phase 4 only produces draft content).

### Privacy (non-negotiable)

- Job **`title`** is a private contractor label. **Never** send to AI, social, or public directory.
- Use `api/app/modules/jobs/privacy.py` → `fields_for_generation(job, voice)` and `transcript_for_generation(voice)`.
- Prefer **edited transcript** over raw.
- Coarse location only (`city`, `state`, `location_display` area-level — no street addresses).

### Capture rules (product)

- After photos required; before optional.
- Generation readiness for MVP: **≥1 after photo + usable voice transcript**. Do **not** hard-require before photos (build spec § generation readiness still mentions before/three photos — **override with product rule**: soft warn if no befores / fewer than 3 photos, do not block).

### API already in place (Phases 1–3)

| Area | Location |
|---|---|
| Auth + company | `api/app/modules/auth/`, `companies/` |
| Job + MediaAsset + VoiceSummary | `api/app/db/models.py` |
| Migrations | `api/alembic/versions/` … phase1, phase2, **phase3** `c3d5f9a2b814` |
| Jobs CRUD + media + **voice** | `api/app/modules/jobs/` (`voice.py`, `state.py`, `privacy.py`) |
| Transcription provider (mock) | `api/app/modules/transcription/` |
| Storage (S3/MinIO) | `api/app/core/storage.py` |
| Config | `AI_PROVIDER=mock`, `TRANSCRIPTION_PROVIDER=mock`, `PUBLISHING_PROVIDER=mock` |

**Next action when after + transcript ready:** `generate_content` (UI shows “Generate content (coming soon)” — Phase 4 wires the real action).

Job statuses already defined for this phase: `ready_to_generate` → `generating` → `awaiting_review` (and `failed`).

### Mobile already in place

| Area | Location |
|---|---|
| Jobs home | `mobile_app/app/pages/index.vue` |
| Create job | `mobile_app/app/pages/create.vue` |
| Job detail (photos + **voice + transcript**) | `mobile_app/app/pages/jobs/[id].vue` |
| Voice recorder / upload | `useVoiceRecorder.ts`, `useJobVoice.ts` |
| API client | `useApi.ts` |

Nuxt **PWA-first** (browser), not native Capacitor for MVP.

### Local run

```bash
make infra-up          # Postgres :5433, Redis :6380, MinIO :9000/:9001
make api-migrate
make api-dev           # :8000
make mobile-dev        # :3000
make api-test
```

---

## Phase 4 goal

Given a job that is **ready to generate** (after photos + usable transcript), the contractor taps **Generate content** and the system produces a **content bundle** (structured job details + social/directory draft variants) with status/polling, using a **replaceable AI provider** (mock OK for MVP).

### Spec acceptance (from `jobpulse_agent_build_spec.md` §32 Phase 4)

- [ ] AI abstraction (provider interface)
- [ ] Structured extraction
- [ ] Content bundle generation
- [ ] Generation status
- [ ] Warnings / uncertain claims  

**Acceptance line:** *Completed Job produces required content variants.*

Also from §10.7 / §14:

- [ ] `POST /jobs/{id}/generate`
- [ ] `GET /jobs/{id}/generation-runs`
- [ ] `GET /generation-runs/{run_id}`
- [ ] `POST /jobs/{id}/regenerate` (at least basic: new run with optional instruction)
- [ ] Record prompt version, provider, input/output snapshots on each run
- [ ] Never include private `title` in generation inputs
- [ ] Edited transcript preferred over raw

**Phase 4 is not full review UI.** After generation succeeds, set job to `awaiting_review` and next_action toward review. Minimal “show generated drafts” on mobile is OK; full approve/reject/edit loop is **Phase 5**.

---

## Phase 4 build checklist

### 1. Data model + migration

Per build spec §6.9–6.11 (and 6.12 if linking media to variants):

**`job_structured_details`** — one current structured extract per job (or latest by generation run — pick one; latest-by-run is fine).

**`generation_runs`**

- `id`, `job_id`, `requested_by`
- `status` (`pending` | `processing` | `completed` | `failed`)
- `generation_type` (e.g. `initial` | `regenerate`)
- `tone`, `length_preference`, `user_instruction`
- `model_provider`, `model_name`, `prompt_version`
- `input_snapshot_json`, `output_snapshot_json`
- `error_message`, `completed_at`, timestamps

**`content_variants`**

- Link to `job_id` + `generation_run_id`
- `content_type`: at minimum  
  `primary_social`, `short_caption`, `before_after`, `directory_listing`  
  (educational optional for MVP)
- `title`, `body_generated`, `body_edited` (null until Phase 5 edits)
- `call_to_action`, `hashtags_json`
- `status` (`draft` / `awaiting_review` for Phase 4)
- `version_number`

Update `Job.latest_generation_run_id` / `generation_version` when a run completes.

### 2. AI provider module

New package e.g. `api/app/modules/ai_generation/` or `modules/generation/`:

```text
base.py       # Protocol: extract_job_details + generate_content
mock.py       # Deterministic fake bundle from transcript + city/service
provider.py   # get_generation_provider() from settings.ai_provider
schemas.py    # JobGenerationInput, StructuredJobDetails, GeneratedContentBundle
service.py    # Orchestrate readiness, snapshots, persist run + variants
api.py        # Routes
```

**Mock provider:** invent plausible contractor-language copy from transcript + safe fields; invent a **public** title/hook (never use private job title). Return warnings list (e.g. soft: “No before photos”).

**Real provider later:** SpaceXAI / OpenAI / etc. — do not hardcode vendor in job service. Settings: `AI_PROVIDER=mock`.

Processing for MVP:

1. **Sync mock** on `POST /generate` (fastest; fine for tests), or  
2. Mark `processing` then complete in same request (status fields ready for Celery later).

Polling via `GET generation-runs/{id}` is enough; WebSockets not required.

### 3. API endpoints (spec §10.7)

```text
POST   /api/v1/jobs/{job_id}/generate
GET    /api/v1/jobs/{job_id}/generation-runs
GET    /api/v1/generation-runs/{run_id}
POST   /api/v1/jobs/{job_id}/regenerate
GET    /api/v1/jobs/{job_id}/content          # optional Phase 4: latest variants for job
```

Request body example:

```json
{
  "tone": "friendly_local",
  "length_preference": "standard",
  "user_instruction": "Focus on drainage and keep tone straightforward."
}
```

**Readiness rules (MVP product):**

- Company-scoped access + can_create_jobs (or generation permission)
- Job not archived
- ≥1 after photo (ready images)
- Usable transcript (`has_usable_transcript`)
- No run already `processing` (or allow supersede carefully)
- Soft warnings: zero befores, fewer than 3 photos — return in `warnings`, do not block

**On success:**

- Persist structured details + content variants  
- Job status: `generating` briefly → `awaiting_review` (or go straight to `awaiting_review` if sync)  
- `next_action` → `review_content`  
- Timeline Review step becomes current  

### 4. Guardrails (even for mock)

Input assembly must:

- Use `fields_for_generation` + transcript (edited preferred)
- Include photo stage labels / counts (and signed URLs only if provider needs them — mock can use counts only)
- Company tone / default CTA from company profile when available
- Never include `title`, `customer_name_private`, `notes`, exact address

Mock (and later real) should avoid inventing prices, exact addresses, fake licenses, guarantees.

### 5. State machine updates

Update `api/app/modules/jobs/state.py`:

| Condition | next_action / status |
|---|---|
| After + transcript, no completed generation | `generate_content` / `ready_to_generate` |
| Generation processing | `wait_generation` / `generating` |
| Generation completed | `review_content` / `awaiting_review` |
| Failed generation | allow retry `generate_content` + show error |

### 6. Mobile (Nuxt PWA)

- Enable **Generate content** button when `next_action.action === 'generate_content'`
- Call `POST /generate`; show progress / poll run status if needed
- After success: show simple results (list variants: primary social, short caption, before/after, directory) — **read-only or light preview** is enough
- Deep review/edit/approve UI = Phase 5
- Extend `useApi.ts`; optional `useGeneration.ts`

### 7. Tests

- Job with after + voice → generate → run completed → variants present → job `awaiting_review` → next_action `review_content`
- Reject generate without after / without transcript
- Privacy: input snapshot must not contain private job title
- Regenerate creates a new run (prior variants superseded or versioned)
- Mock returns required content types

### 8. Docs

- README Phase 4 try-it steps
- Keep PRD/build spec as source of truth; this file is the agent session brief
- Vendors: AI provider is separate from STT and social poster (PRD §14.1 + `AI_PROVIDER`)

---

## Explicit non-goals for Phase 4

- Full review workspace (approve / reject / inline edit loop) — **Phase 5**  
- Directory publish — **Phase 6**  
- Social publish — **Phase 7**  
- Real production LLM required (mock is fine; interface must be pluggable)  
- Native Capacitor  
- Facebook group automation  

---

## Suggested session prompt (paste into next agent)

```text
Continue JobPulse Phase 4 (AI Generation).

Greenfield: api/, mobile_app/, directory/. legacy/ is reference only.
Phases 1–3 done on main (commit a8caa03+): auth/company, jobs, before/after photos
(private required job name), voice + mock transcript, next_action/timeline.
After + usable transcript → next_action generate_content.

Follow jobpulse_prd.md + jobpulse_agent_build_spec.md §10.7, §14, §32 Phase 4.
Also read docs/phase4_session.md.

CRITICAL product rules:
- Contractor (not founder) will review later; Phase 4 only generates drafts → awaiting_review.
- Job title is private — never send to AI (privacy.fields_for_generation).
- Before photos optional; after + transcript required for generation.
- Prefer edited transcript over raw.

Build:
- generation_runs + content_variants (+ job_structured_details) models + migration
- AI provider interface + mock implementation
- POST generate / regenerate, GET runs, status
- Wire job status + next_action (ready_to_generate → generating → awaiting_review)
- Mobile: Generate content CTA + simple draft preview
- Tests green; privacy snapshot checks

Acceptance: completed job produces required content variants (mock OK).
Mobile is Nuxt PWA-first, not native.
```

---

## File map to create (expected)

```text
api/app/modules/ai_generation/   # or generation/
  base.py, mock.py, provider.py, service.py, schemas.py, api.py
api/alembic/versions/*_phase4_generation.py
api/app/db/models.py             # generation_runs, content_variants, structured_details
api/app/modules/jobs/state.py    # next_action after generation
mobile_app/app/composables/useGeneration.ts
mobile_app/app/pages/jobs/[id].vue   # enable Generate + preview
# optional: mobile_app/app/pages/jobs/[id]/review.vue (thin Phase 4; full Phase 5)
```

---

## Done definition for Phase 4

1. Contractor with after photos + transcript can trigger generation.  
2. Mock (or real) produces required content variants + structured details.  
3. Generation run is persisted with provider/prompt/snapshots.  
4. Job moves to `awaiting_review`; next_action is review (Phase 5 will flesh out).  
5. Private job title never appears in generation inputs.  
6. `make api-test` green; changes committed (push when asked).  

---

## Third-party vendors (context)

| Role | Env | Phase |
|---|---|---|
| Voice → text | `TRANSCRIPTION_PROVIDER` | 3 (done, mock) |
| **AI generation** | `AI_PROVIDER` | **4** |
| Social poster | `PUBLISHING_PROVIDER` | 7 |

Directory publishing is first-party (JobPulse-owned).
