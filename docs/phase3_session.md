# Phase 3 session handoff — Voice & Transcription

**Status of prior work:** Phase 2 is **complete**, tests green, committed and pushed.

| Check | Detail |
|---|---|
| Commit | `5141db3` — *Implement Phase 2 job capture with optional before photos.* |
| Remote | `origin/main` on https://github.com/repoman1964/JOBPULSE.git |
| Tests | `make api-test` → **23 passed** (as of handoff) |
| Greenfield only | Work in `api/`, `mobile_app/`, `directory/` — **`legacy/` is reference only** (untracked; do not extend) |

---

## Phase 2 complete — what exists

### Product workflow (locked)

```text
Create job (required private name)
  → Before photos OPTIONAL (recommended)
  → After photos REQUIRED (≥1)
  → Voice summary REQUIRED  ← Phase 3 builds this
  → AI generate → review → publish  (Phases 4–7)
```

- **Job name (`title`)** is required and **private** (contractor-only). Never send to AI/public (`api/app/modules/jobs/privacy.py` → `fields_for_generation`).
- **After + voice** complete a job; forgetting befores must not block.
- Soft tips when no befores; hard gate is after photos then voice.

### API already in place

| Area | Location |
|---|---|
| Job + MediaAsset models | `api/app/db/models.py` |
| Migration jobs/media | `api/alembic/versions/b2c4e8f1a903_phase2_jobs_media.py` |
| Jobs CRUD + media signed upload | `api/app/modules/jobs/` |
| Status / next_action / timeline | `api/app/modules/jobs/state.py` |
| S3/MinIO storage helpers | `api/app/core/storage.py` |
| Auth + company | `api/app/modules/auth/`, `companies/` |

**Next action after ≥1 after photo today:** `record_voice_summary` (UI points here; voice endpoints not built yet).

### Mobile already in place

| Area | Location |
|---|---|
| Jobs home (continue + timeline) | `mobile_app/app/pages/index.vue` |
| Create job | `mobile_app/app/pages/create.vue` |
| Job detail photos | `mobile_app/app/pages/jobs/[id].vue` |
| API client | `mobile_app/app/composables/useApi.ts` |
| Media upload | `mobile_app/app/composables/useJobMedia.ts` |

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

## Phase 3 goal

Let the contractor **record a short voice description** of the completed work, upload it to the job, get a **transcript**, **edit** it, and advance job status to ready for generation (Phase 4).

### Spec acceptance (from `jobpulse_agent_build_spec.md` §32 Phase 3)

- [ ] User can record  
- [ ] Transcript appears  
- [ ] Transcript can be corrected  

Also from §10.6 / §13:

- [ ] Audio upload (signed URL preferred, same pattern as photos)  
- [ ] Transcription task (mock provider OK for MVP; real provider pluggable)  
- [ ] Status polling until transcript ready  
- [ ] Edited transcript preferred over raw for later AI  

---

## Phase 3 build checklist

### 1. Data model + migration

New table **`voice_summaries`** (spec §6.8):

- `id`, `job_id` (unique per job or latest active — prefer one current summary per job for MVP)
- `audio_asset_id` → `media_assets` (asset_type `audio`)
- `transcript_raw`, `transcript_edited`
- `language`
- `transcription_status` (`pending` | `processing` | `completed` | `failed`)
- `transcription_provider`, `transcription_error`
- timestamps

Reuse `media_assets` for the audio file (stage can stay `unclassified` or add voice-specific handling; photos still before/after only).

### 2. API endpoints (spec §10.6)

```text
POST   /api/v1/jobs/{job_id}/voice/upload-url
POST   /api/v1/jobs/{job_id}/voice/complete
GET    /api/v1/jobs/{job_id}/voice
PATCH  /api/v1/jobs/{job_id}/voice/transcript
POST   /api/v1/jobs/{job_id}/voice/retranscribe
```

Optional: multipart fallback `POST .../voice/upload` (mirror photo path).

**Rules:**

- Require company-scoped job access (same as jobs module).
- Prefer requiring **≥1 after photo** before accepting voice (product rule).
- On transcript `completed` (or mock instant complete): set job status toward `ready_to_generate` when after + transcript exist.
- Wire `next_action`: if afters and no usable transcript → `record_voice_summary`; if transcript ready → `generate_content` (Phase 4 can implement generate; next_action can say “Generate content” early).

### 3. Transcription provider

- Config already: `TRANSCRIPTION_PROVIDER=mock` in settings.
- Interface e.g. `transcribe(audio_bytes | storage_key) -> str`.
- **Mock:** return a fixed or filename-based fake transcript for tests/dev.
- Real: Whisper / SpaceXAI / etc. later — do not hardcode one vendor in the job service.

Processing options for MVP:

1. **Sync mock** on `voice/complete` (fastest to ship), or  
2. Celery task + poll `transcription_status` (closer to production).

Polling is fine; WebSockets not required.

### 4. Mobile (Nuxt PWA)

- Browser **`MediaRecorder`** (WebM Opus preferred; MP4/M4A fallback).
- Controls: start / pause / resume / stop / playback / delete / re-record / upload progress.
- Prefer surface on **job detail** when next_action is `record_voice_summary` (or small `/jobs/[id]/voice` page).
- Composables: `useVoiceRecorder.ts`, extend `useApi` with voice methods; optional `usePolling` for transcript status.
- After upload: show transcript; editable textarea → PATCH transcript; clear “Save & continue”.

### 5. State machine updates

Update `api/app/modules/jobs/state.py`:

| Condition | next_action / status |
|---|---|
| No after photos | `add_after_photos` (unchanged) |
| After, no transcript | `record_voice_summary` |
| After + transcript ready | `generate_content` (or `ready_to_generate`) |
| Timeline Voice step | `complete` when transcript usable |

Do **not** require before photos.

### 6. Tests

- Create job → after photo → voice upload/complete → mock transcript → GET voice → PATCH edited transcript.
- Reject or soft-fail voice without after photo if you enforce the product rule.
- Privacy: transcript/edited text may go to AI later; **title still excluded**.

### 7. Docs

- Short README Phase 3 try-it steps.
- Keep PRD/build spec as source of truth; this file is the agent session brief.

---

## Explicit non-goals for Phase 3

- AI content generation (Phase 4)  
- Review/approve UI (Phase 5)  
- Directory / social publish (Phases 6–7)  
- Native Capacitor packaging  
- Progress photos  
- Production R2 cutover (MinIO path stays)

---

## Suggested session prompt (paste into next agent)

```text
Continue JobPulse Phase 3 (Voice + Transcription).

Greenfield: api/, mobile_app/, directory/. legacy/ is reference only.
Phase 1–2 done on main (commit 5141db3+): auth/company, jobs, before/after photos,
required private job name, next_action/timeline. After photos required; before optional.

Follow jobpulse_prd.md + jobpulse_agent_build_spec.md §10.6, §13, §32 Phase 3.
Also read docs/phase3_session.md.

Build:
- voice_summaries model + migration
- signed audio upload + complete (media_assets audio)
- mock transcription provider + status
- GET/PATCH transcript, retranscribe
- update next_action/timeline when after + transcript ready
- Nuxt PWA MediaRecorder on job flow; edit transcript; poll status if async

Acceptance: record → transcript appears → transcript editable; tests green.
Mobile is Nuxt PWA-first, not native.
```

---

## File map to create (expected)

```text
api/app/modules/jobs/          # extend, or modules/voice/
  voice service + routes
api/app/modules/transcription/ # provider interface + mock
api/alembic/versions/*_phase3_voice.py
mobile_app/app/composables/useVoiceRecorder.ts
mobile_app/app/components/voice/*  (optional, keep thin)
mobile_app/app/pages/jobs/[id].vue  # integrate recorder + transcript
```

---

## Done definition for Phase 3

1. Contractor with after photos can record and save voice on the job.  
2. Mock (or real) transcript shows in the app.  
3. Contractor can edit and save transcript.  
4. Job next action advances past voice when transcript is ready.  
5. `make api-test` green; changes committed (push when asked).  
