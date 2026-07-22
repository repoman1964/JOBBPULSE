# Phase 5 session handoff — Human Review

**Status:** Phase 5 is **complete** on `main` (`137e95d`). Phase 6 is also complete (`a407d35`). For the next session, use **[`docs/phase7_session.md`](phase7_session.md)**.

| Check | Detail |
|---|---|
| Phase 5 commit | `137e95d` — *Implement Phase 5 human review: edit, approve, reject, publish gate.* |
| Tests | `make api-test` → **43 passed** (Phase 5 review suite included) |
| Greenfield only | Work in `api/`, `mobile_app/`, `directory/` — **`legacy/` is reference only** |

---

## Phase 4 complete — what exists

### Product workflow (locked)

```text
Create job (required private name)
  → Before photos OPTIONAL (recommended)
  → After photos REQUIRED (≥1)
  → Voice summary REQUIRED (transcript usable)
  → AI generate (drafts → awaiting_review)   ← Phase 4 done
  → Contractor review / edit / reject / regenerate until approve  ← Phase 5
  → Publish social + directory  (Phases 6–7)
```

**Approval is always the contractor’s decision** — not the founder/operator.  
**Nothing publishes without contractor approval.** Phase 5 enforces the gate; Phases 6–7 only act on approved content.

### Privacy (non-negotiable)

- Job **`title`** is a private contractor label. **Never** send to AI, social, or public directory.
- Use `api/app/modules/jobs/privacy.py` → `fields_for_generation` / `transcript_for_generation`.
- Prefer **edited transcript** over raw.
- Coarse location only (`city`, `state`, `location_display` — no street addresses).
- Public titles in content variants are AI-invented marketing hooks — not the private job name.

### Capture + generation rules (product)

- After photos required; before optional (soft warn, do not block generation or review).
- Generation readiness: **≥1 after + usable transcript**.
- Regenerated runs supersede prior variants (`content_variant_status = superseded`).

### API already in place (Phases 1–4)

| Area | Location |
|---|---|
| Auth + company | `api/app/modules/auth/`, `companies/` |
| Job + Media + Voice | `api/app/db/models.py`, `modules/jobs/` |
| AI generation | `api/app/modules/ai_generation/` (Protocol + **mock**) |
| Migrations | phase1 → phase2 → phase3 `c3d5f9a2b814` → **phase4** `d4e6a0b3c925` |
| Generation APIs | `POST …/generate`, `POST …/regenerate`, `GET …/generation-runs`, `GET …/generation-runs/{id}`, `GET …/content` |
| Permissions | `can_create_jobs` (crew+), **`can_approve_and_publish` (manager+)** already defined |
| Config | `AI_PROVIDER=mock`, `TRANSCRIPTION_PROVIDER=mock`, `PUBLISHING_PROVIDER=mock` |

**Content model fields ready for review:**

- `ContentVariant`: `body_generated`, `body_edited`, `status` (`draft` \| `awaiting_review` \| `approved` \| `rejected` \| `superseded`), `approved_by`, `approved_at`, `rejected_at`, `version_number`
- `GenerationRun`: snapshots, provider, prompt version, history
- `JobStructuredDetails`: latest structured extract (upserted per successful run)
- Job: `status` includes `awaiting_review`, `revision_requested`, `approved`; `generation_version`, `latest_generation_run_id`

### Mobile already in place

| Area | Location |
|---|---|
| Job detail + generate CTA | `mobile_app/app/pages/jobs/[id].vue` |
| Draft **preview only** | same page — cards for variants + regenerate |
| Generation client | `useGeneration.ts` |
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

## Phase 5 goal

Give the **contractor** a real **review workspace**: edit drafts, approve/reject variants, regenerate with instructions, see version history, and mark the job **approved** when rules are met — so Phases 6–7 can publish only approved content.

### Spec acceptance (from `jobpulse_agent_build_spec.md` §32 Phase 5)

- [x] Review workspace  
- [x] Inline editing  
- [x] Reject  
- [x] Regenerate  
- [x] Version history  
- [x] Approval  

**Acceptance lines:**

- User can loop until satisfied  
- **No unapproved content can publish** (enforce gate even if publish UI is Phase 6–7)

Also from §10.8 / §15:

- [x] `GET /jobs/{id}/content` (exists — extend as needed)  
- [x] `GET /content/{content_id}`  
- [x] `PATCH /content/{content_id}` (edit body / title / CTA / hashtags → `body_edited`)  
- [x] `POST /content/{content_id}/approve`  
- [x] `POST /content/{content_id}/reject`  
- [ ] `POST /content/{content_id}/duplicate` (optional MVP; skipped)  
- [x] `POST /jobs/{id}/approve-all` (or job-level approve when rules met)  
- [x] Regenerate already exists at job level; optional per-variant regenerate  
- [x] Permissions: approve/reject requires **manager or owner** (`can_approve_and_publish`); crew may edit drafts or only capture — product choice: recommend **crew can edit + regenerate, only manager+ approve**  
- [x] Job status: `awaiting_review` ↔ `revision_requested` → regenerate → `awaiting_review` → `approved`

---

## Phase 5 build checklist

### 1. Review API (module e.g. `api/app/modules/content/` or extend `ai_generation`)

Suggested package:

```text
api/app/modules/content/
  api.py
  service.py
  schemas.py
```

| Endpoint | Behavior |
|---|---|
| `GET /content/{id}` | Company-scoped variant detail |
| `PATCH /content/{id}` | Set `body_edited`, optional title/CTA/hashtags; keep `body_generated` immutable |
| `POST /content/{id}/approve` | `status=approved`, set `approved_by`/`approved_at`; clear reject |
| `POST /content/{id}/reject` | `status=rejected`, `rejected_at`; optional reason in body |
| `POST /jobs/{id}/approve-all` | Approve all current (non-superseded) variants that pass rules, or approve selected types |
| `POST /jobs/{id}/approve` (optional alias) | Mark job `approved` when approval rules satisfied |

**Effective body for display:** `body_edited or body_generated`.

**Regenerate (already Phase 4):** keep `POST /jobs/{id}/regenerate` with `user_instruction` / tone / length. On regenerate:

- Prior active variants → `superseded`  
- Job → `generating` briefly → `awaiting_review`  
- If user rejected some pieces, optional: set job `revision_requested` before regenerate (status already in enum)

### 2. Approval rules (MVP product overrides)

Build-spec §15.3 says before+after required for approve. **Product override:**

| Rule | MVP |
|---|---|
| ≥1 **after** photo still on job | **Required** |
| ≥1 **before** photo | Soft warn only — **do not block** job approval |
| ≥1 social-ish variant approved | Required: at least one of `primary_social` / `short_caption` / `before_after` |
| `directory_listing` approved | **Required** for job-level `approved` (directory is a primary destination) |
| Unresolved hard system errors | Block; soft generation warnings do **not** block |

Separate approval flags per variant are enough for MVP (no separate social/directory job sub-status tables unless needed).

When job becomes `approved`:

- Set `job.approved_at`  
- `next_action` → something like `publish_content` or `ready_to_publish` (Phases 6–7 will implement publish; label can say “Ready to publish (coming soon)”)

When any approved variant is later rejected or regenerated, clear job `approved` back to `awaiting_review` / `revision_requested` as appropriate.

### 3. Permissions

| Action | Role |
|---|---|
| View content / edit draft text | crew+ (`can_create_jobs`) — or manager+ if you want stricter |
| Regenerate | crew+ (same as generate) |
| Approve / reject / approve-all / job approve | **manager+** (`can_approve_and_publish`) |

Every query company-scoped.

### 4. State machine (`state.py`)

| Condition | next_action | job status |
|---|---|---|
| Drafts present, not all approved | `review_content` | `awaiting_review` |
| User requested changes / some rejected | `review_content` or `generate_content` | `revision_requested` |
| Regenerating | `wait_generation` | `generating` |
| Approval rules met + user approved | `ready_to_publish` (new) | `approved` |
| Failed generation | `generate_content` | `failed` |

Do **not** allow frontend to set `status` arbitrarily — only service transitions.

### 5. Mobile review workspace (Nuxt PWA)

Upgrade beyond Phase 4 preview on `jobs/[id].vue` **or** add:

```text
mobile_app/app/pages/jobs/[id]/review.vue
mobile_app/app/composables/useContentReview.ts
```

MVP UX (keep simple for contractors):

1. List current variants (not superseded) with type labels  
2. Inline edit textarea → Save (PATCH)  
3. Approve / Reject per card  
4. Job-level **Approve for publish** when rules met (disabled + reason until ready)  
5. Regenerate with optional instruction field  
6. Light version history: list generation runs + “view this version” (read-only older supersedes)  
7. Show soft tips (no befores) without blocking  

No publish UI required in Phase 5 beyond “approved / ready to publish” messaging.

### 6. Publish gate (stub for later phases)

Even without social/directory publish endpoints:

- Add a clear helper e.g. `assert_job_publishable(job)` that raises unless `status == approved` and required variants still `approved`  
- Call it from any future publish path; unit-test the gate in Phase 5  

### 7. Tests

- Edit variant → `body_edited` returned; generated body unchanged  
- Approve variant; reject variant  
- Job approve blocked without directory_listing approved  
- Job approve blocked without after photos  
- Job approve succeeds with social + directory approved (no before OK)  
- Crew cannot approve (403); manager/owner can  
- Regenerate supersedes; job leaves `approved` if was approved  
- Version history / list runs still works  
- Privacy unchanged (title never in generation inputs)  
- `assert_job_publishable` rejects unapproved jobs  

### 8. Docs

- README try-it: review → approve steps  
- Keep PRD/build-spec as source of truth; this file is the agent session brief  

---

## Explicit non-goals for Phase 5

- Directory public pages / SEO publish — **Phase 6**  
- Social connections / Blotato-class poster — **Phase 7**  
- Real production LLM (mock remains fine)  
- Native Capacitor  
- Billing, team invites polish  
- Facebook group automation  
- Auto-publish on approve  

---

## Suggested session prompt (paste into next agent)

```text
Continue JobPulse Phase 5 (Human Review).

Greenfield: api/, mobile_app/, directory/. legacy/ is reference only.
Phases 1–4 done on main (commit bca5175+): auth/company, jobs, photos, voice,
AI generation (mock) → drafts in awaiting_review.

Follow jobpulse_prd.md + jobpulse_agent_build_spec.md §10.8, §15, §32 Phase 5.
Also read docs/phase5_session.md.

CRITICAL product rules:
- Contractor (not founder) reviews and approves; nothing publishes without approval.
- Job title is private — never send to AI/public.
- Before photos optional; after required. Do not block approval solely for missing befores.
- Prefer body_edited over body_generated for display/publish later.
- Approve requires manager+; use can_approve_and_publish.

Build:
- Content review APIs: GET/PATCH content, approve, reject, job approve-all
- Approval rules (social + directory variants; after photo; soft warn befores)
- State: awaiting_review / revision_requested / approved + next_action ready_to_publish
- Mobile review workspace: edit, approve/reject, regenerate+instruction, light history
- Publish gate helper + tests (no unapproved publish)
- Tests green

Acceptance: contractor can loop edit/reject/regenerate until satisfied; job can reach approved; unapproved content cannot publish.
Mobile is Nuxt PWA-first, not native.
```

---

## File map to create/touch (expected)

```text
api/app/modules/content/          # or extend ai_generation
  api.py, service.py, schemas.py
api/app/modules/jobs/state.py     # review / approved next_actions
api/app/core/permissions.py       # already has can_approve_and_publish
api/app/tests/test_content_review.py
mobile_app/app/composables/useContentReview.ts
mobile_app/app/pages/jobs/[id].vue          # upgrade drafts → review actions
# optional: mobile_app/app/pages/jobs/[id]/review.vue
```

---

## Done definition for Phase 5

1. Contractor can edit draft variant text and save (`body_edited`).  
2. Contractor (manager+) can approve/reject variants and see status.  
3. Job can reach `approved` only when MVP approval rules pass.  
4. Regenerate + optional instruction still works; history retained (superseded).  
5. Unapproved jobs fail a publish-gate helper/tests.  
6. Private job title still never in AI inputs.  
7. `make api-test` green; changes committed (push when asked).  

---

## Third-party vendors (context)

| Role | Env | Phase |
|---|---|---|
| Voice → text | `TRANSCRIPTION_PROVIDER` | 3 (done, mock) |
| AI generation | `AI_PROVIDER` | 4 (done, mock) |
| Social poster | `PUBLISHING_PROVIDER` | 7 |

Directory publishing is first-party (JobPulse-owned). Phase 5 only prepares **approved** content for later publish.

---

## Phase 5 in one line

Turn draft content (`awaiting_review`) into **contractor-controlled** approved content via edit / reject / regenerate loops — so nothing can publish until the contractor says so.
