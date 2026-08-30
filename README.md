# JobbPulse

Contractor-first **job-to-marketing** platform for visual home-service businesses.

> Finish the job. Show JobbPulse what you did. JobbPulse turns it into marketing.

Core loop:

**Create Job → before photos → after photos → voice summary → AI content → human approve → publish to social + owned local directory**

## Repository layout

| Path | Purpose |
|---|---|
| `api/` | FastAPI modular monolith (PostgreSQL, Redis, S3) |
| `infra/` | Docker Compose for local dependencies |
| `contractor_app/` | Contractor phone UI (`frontend/`). `backend/` is reference-only. |
| `website/portfolio_website/` | Public local project portfolio (Nuxt SSR) |
| `website/red_clay_website/` | Red Clay Cabinet Installers demo marketing site |
| `website/marketing_website/` | One-page JobbPulse sales landing page |
| `website/abc_painters_website/` | ABC Painters demo marketing site |
| `legacy/` | **Frozen prototype** — reference only, not production |
| `docs/` | Product docs (PRD + build spec) |
| `docs/biz_docs/usp.md` | **Canonical offer / USP** (what one job publishes, evergreen cadence) |
| `jobbpulse_prd.md` | Product requirements |
| `jobbpulse_agent_build_spec.md` | Implementation specification |

`contractor_app/` and the sites under `website/` all live in this repo.

## Prerequisites

- Node.js 20+
- Python 3.11+ (3.12 preferred)
- Docker + Docker Compose

## Quick start

```bash
# 1. Infrastructure (Postgres, Redis, MinIO, Mailpit)
make infra-up

# 2. API
make api-install
cp api/.env.example api/.env   # if you don't already have api/.env
make api-migrate
make api-dev
# → http://localhost:8000/docs

# 3. Seed public portfolio demo data (optional)
make portfolio-seed   # Georgia demo inventory (includes Red Clay contractor)
```

The **contractor phone app** is `contractor_app/frontend`. Point it at `api/`:

```bash
cd contractor_app/frontend
NUXT_PUBLIC_API_MODE=http NUXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
# → http://localhost:3000
```

Frontend-only mock (no API): omit `NUXT_PUBLIC_API_MODE` or set it to `mock`.

`contractor_app/backend` is a **reference implementation** only — see `contractor_app/backend/REFERENCE_ONLY.md`. Do not run it next to `make api-dev`.

Production hosting is **Render** (static UI + FastAPI + worker + Postgres + Redis, photos on Cloudflare R2). Blueprint: [`render.yaml`](./render.yaml). The API image should be `api/` (cut over from `contractor_app/backend`).

The **public project portfolio** is `website/portfolio_website/`. From there: `make install && make dev` → http://localhost:3001

The **Red Clay Cabinet Installers** demo marketing site is `website/red_clay_website/`. It consumes JobbPulse’s public API when both are running.

The **JobbPulse sales landing page** is `website/marketing_website/`. From there: `make install && make dev` → http://localhost:3003. Production deploys as Cloudflare Worker **`jobbpulse-website`** (`make -C website/marketing_website deploy`).


### Local infra ports

Compose uses host ports that avoid common local conflicts:

| Service | Host port |
|---|---|
| Postgres | **5433** → container 5432 |
| Redis | **6380** → container 6379 |
| MinIO API / console | 9000 / 9001 |
| Mailpit SMTP / UI | 1025 / 8025 |

`api/.env` is preconfigured for these ports.

## Mobile strategy (MVP)

The contractor product is a **mobile-first Nuxt web app** used in Safari/Chrome on the phone. Camera, photo library, and microphone work via browser APIs. Photos and voice upload to cloud storage and attach to a server-side Job so closing the browser does not lose work.

A store-installed app (Capacitor) is optional later packaging of the same code—not required for before/after photos or voice capture.

## Product rules (non-negotiable)

Offer destinations: [`docs/biz_docs/usp.md`](docs/biz_docs/usp.md).

1. The **Job** is the core object.
2. Job creation must be extremely easy (photos first, minimal typing).
3. **Human approval** before any job-package distribution. Evergreen cadence is engine-scheduled.
4. Locked destinations for an approved job: Facebook Page, Instagram, Google Business Profile, 3–5 local homeowners groups, contractor website (home carousel + job page), JobbPulse directory page.
5. Facebook homeowners / neighborhood group posting **is in the offer** (capped at 3–5 groups; contractor’s connected account; neighbor-native copy).
6. Privacy: city/neighborhood-level location; no exact residential addresses on public pages.

## Development phases

See `jobpulse_agent_build_spec.md` §32 and the session plan. High level:

0. Bootstrap — **done**  
1. Auth + company — **done**  
2. Job capture + photos — **done**  
3. Voice + transcription — **done** (mock STT; real vendor is a config swap)  
4. AI generation (drafts) — **done** (mock provider)  
5. Human review (contractor approves) — **done**  
6. Directory publish — **done** (single **Publish** CTA → first-party directory)  
7. Social publish — **done** (mock `PUBLISHING_PROVIDER`; same Publish button)  
8. Pilot hardening — **done** (audit, notifications, moderation, billing hooks, request IDs)

### Third-party vendors (replaceable)

See PRD **§14.1**. MVP uses mocks; production plugs in:

| Role | Env | Notes |
|---|---|---|
| Voice → text | `TRANSCRIPTION_PROVIDER` | Mock now; Whisper/Deepgram/etc. later |
| AI generation | `AI_PROVIDER` | Mock now; pluggable LLM later |
| Social poster | `PUBLISHING_PROVIDER` | Mock now; real vendor is a config swap |
| Error monitoring | `SENTRY_DSN` | Optional; no-op when empty |
| Billing | `BILLING_ENFORCE` | Hooks only; enforce off by default |

## Phase 1–6 (try it)

Contractor app (current):

```bash
cd contractor_app
cp -n backend/.env.example backend/.env
make up
make seed
# other terminal
cd contractor_app/frontend
npm install
NUXT_PUBLIC_API_MODE=http NUXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

Or frontend-only with the mock API: `cd contractor_app/frontend && npm run dev`. Sign-in: `mike@johnsonoutdoor.example` / code `123456`. Full steps: `contractor_app/LOCAL_SETUP.md`.

Platform API + public sites (separate from the contractor engine):

```bash
make infra-up
make api-migrate
make api-dev                              # terminal 1 — http://localhost:8000/docs
make -C portfolio_website dev              # terminal 2 — http://localhost:3001
```

The current contractor UI is OTP sign-in → jobs → photo categories → finish with voice → asset approval. It is **not** wired to this repo’s `api/` yet (own engine on :8000).

The older capture → generate → approve → publish loop against `api/` + `portfolio_website` is still valid for the platform API; that client is no longer in this folder.

**Privacy:** Job name is contractor-only. It is never sent to AI, social, public directory, notification bodies, or audit payloads. AI invents public titles/hooks from photos + voice + coarse location. Edited transcript / body is preferred for public summary.

**Pilot ops (Phase 8):**
- `X-Request-ID` on every response; included in error `meta`
- `GET /health/ready` checks DB (required) + soft Redis/S3
- Flag listing: `POST /api/v1/directory/listings/{id}/flag` (manager+). Platform remove: set `FOUNDER_ADMIN_EMAILS` and `POST /api/v1/admin/directory/listings/{id}/remove`
- Billing: `GET /api/v1/billing/status`; set `BILLING_ENFORCE=true` to block canceled companies at publish (402)

**Apps:** Contractor app (`contractor_app/`) = jobs + capture + publish. Public portfolio (`portfolio_website/`) = SSR local SEO pages.

## Tests

```bash
make api-test
```

## Legacy

`legacy/` contains an earlier FastAPI + SQLite + Nuxt/Capacitor prototype. It is useful for UX patterns and prompt ideas. Do **not** extend it for production—new work goes in `api/` and the apps (`contractor_app/`, `portfolio_website/`).
