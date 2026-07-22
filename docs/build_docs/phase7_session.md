# Phase 7 session handoff — Social Publishing

**Status:** Phase 7 is **complete** on `main` (`06ab053`). For the next session, use **[`docs/phase8_session.md`](phase8_session.md)**.

| Check | Detail |
|---|---|
| Phase 7 commit | `06ab053` — *Implement Phase 7 social publishing with mock provider and unified Publish.* |
| Tests | `make api-test` → **64 passed** |
| Migration | `f6a8c2d5e147` publishing_connections + publication_jobs |
| Greenfield only | `api/`, `mobile_app/`, `directory/` — **`legacy/` reference only** |

---

## What Phase 7 delivered

- `PublishingProvider` Protocol + mock + factory (`PUBLISHING_PROVIDER`)
- Connections APIs (start / list / callback / delete / verify)
- Unified orchestrator: `POST /jobs/{id}/publish` (directory + social)
- Schedule, publications list, retry, cancel; idempotency keys
- Mobile: Account connect mock FB/IG; job Publish with destination checkboxes
- Privacy: private job title never sent to social payloads

### UX rule (do not regress)

**One Publish button** — directory and social are destinations under the same action.

### Next

**[`docs/phase8_session.md`](phase8_session.md)** — Pilot hardening: notifications, audit, moderation, billing hooks, observability.
