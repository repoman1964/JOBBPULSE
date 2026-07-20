# Phase 6 session handoff — Directory Publishing

**Status:** Phase 6 is **complete** on `main` (`a407d35`). For the next session, use **[`docs/phase7_session.md`](phase7_session.md)**.

| Check | Detail |
|---|---|
| Phase 6 commit | `a407d35` — *Implement Phase 6 directory publishing with unified Publish action.* |
| Tests | `make api-test` → **54 passed** (11 directory tests included) |
| Migration | `e5f7b1c4d036` phase6 directory tables |
| Greenfield only | Work in `api/`, `mobile_app/`, `directory/` — **`legacy/` is reference only** |

---

## What Phase 6 delivered

### Product workflow (locked)

```text
Create job (required private name)
  → Before photos OPTIONAL (recommended)
  → After photos REQUIRED (≥1)
  → Voice summary REQUIRED (transcript usable)
  → AI generate (drafts → awaiting_review)     ← Phase 4
  → Contractor review / edit / reject / regenerate until approve  ← Phase 5
  → Publish (single action) → JobPulse directory live  ← Phase 6 done
  → Same Publish button + social destinations           ← Phase 7
```

**UX rule:** One **Publish** button — not separate “directory” vs “social” CTAs.  
Phase 6 implements directory; Phase 7 extends the same `POST /jobs/{id}/publish` with social connections.

### Acceptance met

- [x] Contractor profile (public)
- [x] Directory listing from approved job
- [x] Public project page (SSR)
- [x] Before-after gallery
- [x] SEO metadata
- [x] Unpublish control
- [x] Unapproved jobs cannot publish
- [x] Private job title never on public APIs/pages

### Key implementation map

| Area | Location |
|---|---|
| Models | `contractor_profiles`, `directory_listings`, `directory_listing_media` in `api/app/db/models.py` |
| Migration | `api/alembic/versions/e5f7b1c4d036_phase6_directory.py` |
| Service | `api/app/modules/directory/service.py` — `publish_job`, profile, unpublish |
| Privacy | `api/app/modules/directory/privacy.py` |
| Admin APIs | `GET/PATCH /directory/profile`, listings, unpublish |
| Unified publish | `POST /jobs/{job_id}/publish` (`publish_to_directory`, empty social for now) |
| Public APIs | `/public/contractors`, `/public/projects`, `/public/leads` stub |
| Publish gate | `assert_job_publishable` — allows `approved` **or** `published` (re-publish) |
| Directory SSR | `directory/app/pages/...` |
| Mobile | `usePublish.ts` + **Publish** on `jobs/[id].vue` |

### Privacy (still non-negotiable)

- Job **`title`** never on public directory JSON/pages
- Prefer **`body_edited` over `body_generated`**
- Coarse location only; no `storage_key` in public payloads

### Local run

```bash
make infra-up
make api-migrate
make api-dev           # :8000
make mobile-dev        # :3000
make directory-dev     # :3001
make api-test
```

**Try it:** approve job → **Publish** → open live project URL on `:3001`.

---

## Phase 7 starts from here

See **[`docs/phase7_session.md`](phase7_session.md)** — social publishing via replaceable `PUBLISHING_PROVIDER`, still one Publish button.
