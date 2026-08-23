# Red Clay painting demo site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn Red Clay into a Premium Craft painting conversion site that pulls a prospect’s generated jobs from the contractor app after they identify by email, and add self-serve contractor signup so the sales walkthrough works.

**Architecture:** Contractor-app FastAPI on `:8000` gains `POST /api/v1/auth/register` plus unauthenticated `GET /api/v1/public/demo/projects`. Red Clay Nuxt on `:3002` is rebuilt as an exterior-led painting company using Premium Craft layout (Custom Roofing prompt) with Georgia clay accent. Dummy jobs always fill the portfolio; a `red_clay_demo_email` cookie prepends live jobs from the engine.

**Tech Stack:** FastAPI, SQLAlchemy async, pytest, Nuxt 4 / Vue 3, Vitest for Red Clay utils.

**Spec:** `docs/superpowers/specs/2026-08-23-red-clay-painting-demo-site-design.md`

## Global Constraints

- Wordmark stays **Red Clay**. Tagline: Painting · Metro Atlanta. No “demo” / JobbPulse on public chrome.
- Phone `404-555-0148` / `tel:+14045550148`. Email `hello@redclaypainting.com`.
- Visual tokens: charcoal `#2B2825`, clay `#B54A2A`, clay hover `#8B3A20`, page `#F7F4EE`, card `#FFFFFF`, footer `#1C1A18`, text `#211F1D`, muted `#6B655C`, border `#E3DCCF`.
- Headlines: Fraunces (or Lora) 68→42 / 44→32, weight 500–600. Body: Inter 17→16. Small-caps 13px, letter-spacing 0.1em, clay.
- One solid clay CTA per viewport. Before/after side by side, never a slider. Section padding ≥ 96px desktop. Tap targets ≥ 44px.
- Dummy job slugs reserved with `demo-` prefix.
- Cookie `red_clay_demo_email`, path `/`, 7-day max-age, not httpOnly.
- Error envelope stays the existing contractor-app shape `{ code, message, fieldErrors? }` (not `{ error: { ... } }`) so clients keep working; codes match the spec (`email_taken`, `validation_error`).
- CORS must include `http://localhost:3002` and `http://127.0.0.1:3002`.
- GHL is not wired. `/book` is an empty `#ghl-calendar` mount.
- Estimate forms succeed client-side without the platform leads API.
- Red Clay `NUXT_PUBLIC_API_BASE_URL` points at the contractor-app engine (`:8000`), not platform `api/`.
- Do not start Red Clay live-API wiring until empty-list and one eligible-job tests are green.

## File map

**Create**
- `contractor_app/backend/app/core/slug.py` — kebab-case slugify
- `contractor_app/backend/app/core/rate_limit.py` — IP sliding window
- `contractor_app/backend/app/services/auth_register.py` — create company + owner
- `contractor_app/backend/app/services/public_demo.py` — eligibility, slug, serialize
- `contractor_app/backend/app/api/v1/public_demo.py` — list/detail routes
- `contractor_app/backend/tests/conftest.py` — sqlite TestClient
- `contractor_app/backend/tests/test_auth_register.py`
- `contractor_app/backend/tests/test_public_demo.py`
- `website/red_clay_website/app/utils/demoEmail.ts`
- `website/red_clay_website/app/utils/demoProjects.ts`
- `website/red_clay_website/app/composables/useDemoProjects.ts`
- `website/red_clay_website/app/components/{TrustBar,CtaBand,ProjectCarousel,BeforeAfter,SocialCards,FaqAccordion}.vue`
- `website/red_clay_website/app/pages/{book,privacy,terms,my-work}.vue`
- `website/red_clay_website/app/pages/work/index.vue`, `work/[slug].vue`
- `website/red_clay_website/tests/demoProjects.test.ts`
- Dummy JPEGs under `website/red_clay_website/public/work/` and `public/images/`

**Modify**
- `contractor_app/backend/app/api/v1/auth.py` — register
- `contractor_app/backend/app/api/v1/router.py` — include public_demo
- `contractor_app/backend/app/schemas/requests.py` — RegisterRequest
- `contractor_app/backend/app/core/config.py` — CORS defaults
- `contractor_app/backend/pyproject.toml` — aiosqlite dev dep
- `contractor_app/frontend` — register on API client + sign-in Create account
- `website/red_clay_website` — visual system, siteContent, pages, nuxt.config, Makefile

---

### Task 1: Contractor-app register + public demo API

**Files:** listed above under backend.

**Interfaces:**
- Produces: `POST /api/v1/auth/register` → 201 `{ email, companyId, contractorId }`; 409 `email_taken`; 422 field errors.
- Produces: `GET /api/v1/public/demo/projects?email=` and `GET /api/v1/public/demo/projects/{slug}?email=` as specified.
- Produces: `public_project_slug(public_title, job_id) -> str`

- [ ] **Step 1: Write failing tests** for slug, register, public list/detail (see spec §14).
- [ ] **Step 2: Run tests, confirm fail** (`pytest contractor_app/backend/tests/test_auth_register.py contractor_app/backend/tests/test_public_demo.py -v`).
- [ ] **Step 3: Implement slug, register, public demo, CORS, rate limit.**
- [ ] **Step 4: Run tests, confirm pass.**
- [ ] **Step 5: Commit.**

### Task 2: Red Clay Premium Craft rebuild (dummy only)

Rebuild chrome, tokens, copy, site map, dummy jobs, Kai pages. No live API yet.

- [ ] **Step 1: Write failing util tests** (merge live+dummy, dummy slugs start with `demo-`, public chrome strings must not include `JobbPulse` / `demo` as a word except reserved slugs).
- [ ] **Step 2: Implement visual system + pages + dummy content + images.**
- [ ] **Step 3: Verify routes exist and forms succeed without backend.**
- [ ] **Step 4: Commit.**

### Task 3: Email gate + live project pages + contractor signup UI

- [ ] **Step 1: `useDemoProjects` fetches list when cookie set; prepend live cards; `/work/{slug}` live then dummy.**
- [ ] **Step 2: `/my-work` email + clear; unknown email copy from spec.**
- [ ] **Step 3: Contractor app Create account → OTP.**
- [ ] **Step 4: Tests + commit.**

### Task 4: Browser verification

Homepage desktop+mobile, service page, work hub, dummy project (social cards), `/my-work`, `/book` (`#ghl-calendar`), `/privacy`. Confirm no JobbPulse on public chrome.
