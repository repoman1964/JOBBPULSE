# JobPulse

Contractor-first **job-to-marketing** platform for visual home-service businesses.

> Finish the job. Show JobPulse what you did. JobPulse turns it into marketing.

Core loop:

**Create Job → before photos → after photos → voice summary → AI content → human approve → publish to social + owned local directory**

## Repository layout

| Path | Purpose |
|---|---|
| `api/` | FastAPI modular monolith (PostgreSQL, Redis, S3) |
| `mobile_app/` | Contractor phone-first Nuxt app (browser / PWA for MVP) |
| `directory/` | Public local directory (Nuxt SSR) |
| `infra/` | Docker Compose for local dependencies |
| `legacy/` | **Frozen prototype** — reference only, not production |
| `docs/` | Product docs (PRD + build spec) |
| `jobpulse_prd.md` | Product requirements |
| `jobpulse_agent_build_spec.md` | Implementation specification |

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

# 3. Contractor app (phone-first)
make mobile-install
make mobile-dev
# → http://localhost:3000

# 4. Public directory
make directory-install
make directory-dev
# → http://localhost:3001
```

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

1. The **Job** is the core object.
2. Job creation must be extremely easy (photos first, minimal typing).
3. **Human approval** before any distribution.
4. Two destinations: social (via replaceable provider) + **owned directory**.
5. No Facebook group automation.
6. Privacy: city/neighborhood-level location; no exact residential addresses on public pages.

## Development phases

See `jobpulse_agent_build_spec.md` §32 and the session plan. High level:

0. Bootstrap — **done**  
1. Auth + company — **done**  
2. Job capture + photos — **done**  
3. Voice + transcription — **done** (mock STT; real vendor is a config swap)  
4. AI generation — **next**  
5. Human review  
6. Directory publish  
7. Social publish (third-party poster vendor)  
8. Pilot hardening  

### Third-party vendors (replaceable)

See PRD **§14.1**. MVP uses mocks; production plugs in:

| Role | Env | Notes |
|---|---|---|
| Voice → text | `TRANSCRIPTION_PROVIDER` | Mock now; Whisper/Deepgram/etc. later |
| Social poster | `PUBLISHING_PROVIDER` | Phase 7; e.g. Blotato-class distributor |

## Phase 1–3 (try it)

```bash
make infra-up
make api-migrate
make api-dev          # terminal 1 — http://localhost:8000/docs
make mobile-dev       # terminal 2 — http://localhost:3000
```

1. Open http://localhost:3000/register  
2. Create account (user + company + owner role)  
3. Complete short onboarding  
4. Tap **Create Job** → **required private job name** (e.g. “Johnson / Oak St” — only you see it)  
5. **Before photos optional** (recommended). **After photos required.**  
6. **Record voice summary** on the job (mic → upload → mock transcript appears).  
7. **Edit the transcript** if needed → Save. Next action becomes **Generate content** (Phase 4).  
8. Forgot befores? Still finish with afters + voice. Leave and return → **Your jobs** shows Continue + timeline.  

**Workflow:** Create job → (optional befores) → work → **afters (required)** → **voice (required)** → AI → review → publish.

**Privacy:** Job name is contractor-only. It is never sent to AI, social, or the public directory. AI will invent public titles later. Edited transcript is preferred for generation.

**Apps:** Contractor app (`mobile_app`) = jobs + capture. Public directory (`directory`) = local SEO pages; contractor analytics/admin on the directory side comes later (not a third product).

## Tests

```bash
make api-test
```

## Legacy

`legacy/` contains an earlier FastAPI + SQLite + Nuxt/Capacitor prototype. It is useful for UX patterns and prompt ideas. Do **not** extend it for production—new work goes in `api/`, `mobile_app/`, and `directory/`.
