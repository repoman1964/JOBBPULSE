# Phase 8 session handoff — Pilot Hardening

**Status of prior work:** Phases 1–7 are **complete**, tests green, committed and **pushed**.

| Check | Detail |
|---|---|
| Latest product commit | `06ab053` — *Implement Phase 7 social publishing with mock provider and unified Publish.* |
| Remote | `origin/main` on https://github.com/repoman1964/JOBPULSE.git |
| Tests | `make api-test` → **64 passed** (as of handoff) |
| Greenfield only | Work in `api/`, `mobile_app/`, `directory/` — **`legacy/` is reference only** (untracked; do not extend) |

---

## Phases 1–7 complete — what exists

### Product workflow (locked)

```text
Create job (required private name)
  → Before photos OPTIONAL (recommended)
  → After photos REQUIRED (≥1)
  → Voice summary REQUIRED (transcript usable)
  → AI generate (drafts → awaiting_review)     ← Phase 4
  → Contractor review / edit / reject / regenerate until approve  ← Phase 5
  → Publish (single CTA)
       → JobPulse directory (first-party)      ← Phase 6
       → Social via PUBLISHING_PROVIDER        ← Phase 7
  → Pilot hardening / ops readiness            ← Phase 8 (this session)
```

**Approval is always the contractor’s decision.**  
**Nothing publishes without contractor approval** (`assert_job_publishable`).  
**One Publish button** — directory + social under the same action (never split primary CTAs).

### Privacy (non-negotiable — do not regress)

- Job **`title`** is private — never AI, social, public directory, notifications bodies that leak to third parties, or audit payloads shown publicly
- Prefer **`body_edited` over `body_generated`**; edited transcript for generation
- Coarse location only on public surfaces
- No `storage_key` / raw credentials / customer PII on public APIs
- Helpers: `jobs/privacy.py`, `directory/privacy.py`, `publishing/privacy.py`

### What is already production-shaped

| Area | Location |
|---|---|
| Auth + company + roles | `api/app/modules/auth/`, `companies/`, `core/permissions.py` |
| Jobs, media, voice | `modules/jobs/` |
| AI generation (mock) | `modules/ai_generation/` |
| Content review + gate | `modules/content/` → **`assert_job_publishable`** |
| Directory (first-party) | `modules/directory/` + `directory/` Nuxt SSR |
| Social publish (mock) | `modules/publishing/` + `PUBLISHING_PROVIDER` |
| Unified publish | `POST /api/v1/jobs/{id}/publish` |
| Mobile contractor app | `mobile_app/` — capture → review → Publish + Account connections |
| Migrations | phase1…phase6 `e5f7b1c4d036` → **phase7** `f6a8c2d5e147` |
| Config providers | `AI_PROVIDER`, `TRANSCRIPTION_PROVIDER`, `PUBLISHING_PROVIDER` (all mock OK) |

### Spec MVP Definition of Done (§33) — product path status

| # | Criterion | Status |
|---|---|---|
| 1–3 | Register, company, create job fast | Done |
| 4–8 | Before/after photos, ≥3 supported | Done (before optional product rule) |
| 9–10 | Voice + transcript | Done (mock STT) |
| 11–14 | Generate, edit, regenerate, approve | Done (mock AI) |
| 15 | Publish via third-party provider | Done (mock provider) |
| 16–18 | Directory publish + public page + status | Done |

Phase 8 is **not** a new marketing destination. It makes the pilot **operable, observable, and safe** for real contractors.

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

## Phase 8 goal

Harden JobPulse for **pilot use**: in-app (and stub email) notifications, audit trail for sensitive actions, light admin/moderation controls for public directory content, billing **hooks** (not full Stripe product), structured error monitoring, and a few high-ROI reliability/performance fixes.

### Spec acceptance (from `jobpulse_agent_build_spec.md` §32 Phase 8 + §25–27 + §6.18–6.19)

Build:

- [ ] Notifications
- [ ] Audit logs
- [ ] Admin moderation
- [ ] Billing hooks
- [ ] Error monitoring
- [ ] Performance improvements

**Acceptance line (practical pilot):**

- A contractor can complete the full loop **and** the system records audits, surfaces key notifications, allows unpublish/flag of public content, exposes health/metrics for ops, and does not leave silent failures on publish/generation.

Also:

- Do **not** weaken publish gate or privacy rules  
- Do **not** add a second Publish CTA  
- Directory stays first-party; social stays behind provider adapter  
- Prefer vertical slices that stay runnable after each sub-step  

---

## Phase 8 build checklist (prioritized MVP slices)

Work **top to bottom**. Later items can shrink if time is tight; first three are the pilot core.

### 1. Audit events (foundation for everything else)

**Model** (spec §6.19) — `audit_events`:

- `id`, `company_id`, `user_id` (nullable for system)
- `entity_type`, `entity_id`
- `action` (string enum-ish: `job.approved`, `job.published`, `content.rejected`, `listing.unpublished`, `connection.connected`, …)
- `before_json`, `after_json` (redact private fields / never store credentials)
- `ip_address`, `user_agent` (optional from request)
- `created_at`

**Service helper:**

```text
api/app/modules/audit/
  service.py   # record_event(...)
  privacy.py   # scrub payloads
```

**Emit on (minimum):**

- Job approve / publish / unpublish directory  
- Content approve / reject  
- Social connection connect / disconnect  
- Publication success / fail / retry  
- Company profile / directory profile updates that affect public pages  

**API (manager+ or owner):**

- `GET /api/v1/audit-events?entity_type=&entity_id=&limit=` company-scoped list  

**Tests:** publish creates audit row; credentials never in `after_json`; crew cannot list (or read-only owner-only — pick manager+).

---

### 2. Notifications (in-app first; email stub)

**Model** (spec §6.18) — `notifications`:

- `id`, `user_id`, `company_id`
- `type`, `title`, `body`
- `channel` (`in_app` | `email`)
- `status` (`pending` | `sent` | `read` | `failed`)
- `read_at`, `sent_at`
- `metadata_json` (job_id, publication_id, links — no private job title required; use public titles or generic copy)

**Events to implement first** (spec §25 — pick highest value for pilot):

| Event | When |
|---|---|
| Generation complete | generation run completed |
| Generation failed | generation failed |
| Content ready to review | job → `awaiting_review` |
| Job approved / ready to publish | job → `approved` |
| Directory published | listing published |
| Social published / failed | publication_jobs terminal states |
| Connection error | verify/disconnect error paths (nice-to-have) |

**API:**

- `GET /notifications` (current user)  
- `POST /notifications/{id}/read`  
- `POST /notifications/read-all`  

**Delivery:**

- In-app: write row + return in list (mobile badge/list on Account or home)  
- Email: **stub** logger / optional Mailpit if easy — do not block on real ESP  

**Mobile (minimal):**

- Account or home: unread count + simple list  
- Deep-link metadata `job_id` → open job  

**Tests:** generation complete creates notification for job creator / managers; mark read works; no private title in body if job title would leak.

---

### 3. Admin moderation (directory-focused, thin)

**Not** a full founder CMS. Goal: pilot can remove bad public content.

Already have contractor unpublish. Phase 8 adds:

| Capability | MVP approach |
|---|---|
| Flag listing | `directory_listings.status = flagged` (enum already exists) |
| Remove listing | `status = removed` (hard hide from public) |
| List flagged | Authenticated **owner** (or env `FOUNDER_ADMIN_EMAILS`) endpoint |

**APIs (suggest):**

- `POST /directory/listings/{id}/flag` — manager+ of owning company **or** platform admin  
- `POST /admin/directory/listings/{id}/remove` — platform admin only  
- `GET /admin/directory/listings?status=flagged` — platform admin  

**Platform admin MVP:** config list of emails or `is_platform_admin` on user (simple flag). Avoid multi-tenant admin product scope.

**Public behavior:** `flagged` / `removed` / `unpublished` all 404 on public GET (same as unpublish).

**Tests:** remove hides public project; non-admin 403.

---

### 4. Billing hooks (not full billing product)

**Do not** build a complete Stripe portal unless asked. Spec wants **hooks**:

- Company fields already exist-ish: `subscription_status`, `subscription_plan`  
- Add optional: `billing_customer_id`, `trial_ends_at` if missing  
- Module stub:

```text
api/app/modules/billing/
  service.py   # assert_company_can_publish(company) → allow all in trial/dev
  api.py       # GET /billing/status
```

**Gate (soft for pilot):**

- Config `BILLING_ENFORCE=false` by default  
- When true: block publish if `subscription_status` in `canceled` / `past_due`  
- Webhook stub endpoint `POST /billing/webhooks/stripe` that logs + updates status (signature verify optional behind flag)

**Tests:** with enforce off, publish works; with enforce on + canceled company, publish 402/403.

---

### 5. Error monitoring & observability (§27)

**Minimum viable ops:**

| Item | Implementation |
|---|---|
| Request ID | Middleware: `X-Request-ID` generate/propagate; include in error JSON `meta` |
| Structured logs | JSON-ish log lines for publish, generation, provider errors (stdlib logging OK) |
| Sentry (optional) | `SENTRY_DSN` env; init if set — no-op if empty |
| Health | Existing `/health/*` — extend ready with optional redis/s3 checks (soft fail) |
| Status | `GET /api/v1/status` already exposes providers — add app version + request id sample |

**Do not** require Datadog/New Relic for MVP.

**Tests:** AppError responses still stable; middleware does not break clients.

---

### 6. Performance / reliability improvements (pick 2–4)

High ROI only:

1. **DB indexes** already partly present — verify hot paths: jobs by company+status, publication_jobs by job_id, notifications by user_id+read_at  
2. **N+1** on job list / publications list — `selectinload` where missing  
3. **Publish path** — ensure single commit; avoid repeated job reloads  
4. **Public directory list** — limit default page size; avoid loading full media on list endpoints (summaries only)  
5. **Idempotency** — already on social; ensure directory publish remains idempotent under double-tap  

Optional: simple Redis cache for public project by slug (skip if timeboxed).

**Tests:** list endpoints still correct; no behavior regressions on publish double-call.

---

## Explicit non-goals for Phase 8

- Real production LLM / STT / Blotato OAuth (keep mocks; interfaces stay)  
- Full Stripe subscription UX / pricing pages  
- SMS notifications  
- Facebook group automation (product ban)  
- Native Capacitor  
- Multi-region, complex RBAC matrix, founder analytics dashboards  
- Reworking the contractor capture UX  
- Splitting Publish into destination-specific primary buttons  

---

## Suggested session prompt (paste into next agent)

```text
Continue JobPulse Phase 8 (Pilot Hardening).

Greenfield: api/, mobile_app/, directory/. legacy/ is reference only.
Phases 1–7 done on main (commit 06ab053+): auth/company, jobs, photos, voice,
AI (mock), human review, directory publish, social publish (mock provider).
Unified Publish: POST /jobs/{id}/publish. Gate: assert_job_publishable.
One Publish button — do not regress.

Follow jobpulse_prd.md + jobpulse_agent_build_spec.md §25–27, §6.18–6.19, §32 Phase 8, §33.
Also read docs/phase8_session.md.

CRITICAL product rules:
- Contractor approval required before any publish.
- Job title private — never on public/social/notification leak surfaces.
- Prefer body_edited over body_generated.
- Directory first-party; social via PUBLISHING_PROVIDER.
- Manager+ for publish; careful platform-admin for moderation.

Build (priority order):
1. audit_events + emit on approve/publish/connection
2. notifications (in-app) for generation/publish outcomes + mobile list
3. Thin admin moderation (flag/remove directory listings; public 404)
4. Billing hooks (status fields + optional enforce flag; webhook stub)
5. Request IDs + structured error logging (+ optional SENTRY_DSN)
6. A few performance fixes (N+1, list pagination, indexes)

Tests green. Keep app runnable after each slice.
Acceptance: pilot-ready observability + audit + notifications + moderation path;
full job→publish loop still green.
```

---

## File map to create/touch (expected)

```text
api/alembic/versions/*_phase8_hardening.py
api/app/db/models.py                    # notifications, audit_events; optional billing cols
api/app/modules/audit/
api/app/modules/notifications/
api/app/modules/billing/                # hooks only
api/app/modules/admin/                  # thin moderation (or under directory)
api/app/core/middleware.py              # request id
api/app/core/config.py                  # SENTRY_DSN, BILLING_ENFORCE, admin emails
api/app/main.py
api/app/tests/test_audit.py
api/app/tests/test_notifications.py
api/app/tests/test_moderation.py
api/app/tests/test_billing_hooks.py
mobile_app/app/pages/account.vue        # notifications list / badge
mobile_app/app/composables/useNotifications.ts
README.md                               # pilot ops notes
docs/phase8_session.md                  # this file
```

---

## Done definition for Phase 8

1. Sensitive actions write **audit_events** (no secrets/private title leaks).  
2. Key lifecycle events create **in-app notifications**; user can mark read.  
3. Public listings can be **flagged/removed** and disappear from public API/pages.  
4. **Billing hooks** exist; enforcement off by default for pilot.  
5. **Request IDs** + useful error logs; optional Sentry if DSN set.  
6. At least one measurable **list/publish performance** improvement without regressions.  
7. Full path still works: approve → Publish (directory + mock social).  
8. `make api-test` green; commit and push when asked.  

---

## Third-party vendors (context)

| Role | Env | Status |
|---|---|---|
| Voice → text | `TRANSCRIPTION_PROVIDER` | Mock (Phase 3) |
| AI generation | `AI_PROVIDER` | Mock (Phase 4) |
| Social poster | `PUBLISHING_PROVIDER` | Mock (Phase 7) |
| Directory | first-party | Phase 6 |
| Error monitoring | `SENTRY_DSN` (optional) | **Phase 8** |
| Billing | Stripe later; hooks only now | **Phase 8** |

---

## Phase 8 in one line

**Make the completed job→approve→publish loop pilot-safe: auditable, notifiable, moderatable, observable, and lightly gated for billing — without new destinations or mock-provider rewrites.**
