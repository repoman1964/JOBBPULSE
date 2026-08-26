# JobbPulse Contractor App (Frontend)

Mobile-first Nuxt app for contractors to document jobs, review generated content packages, and approve publishing.

A typed `ApiClient` talks to a **mock adapter** by default. The FastAPI engine in `../backend` plugs in via `HttpApiClient` (`NUXT_PUBLIC_API_MODE=http`).

## Quick start

```bash
cd frontend
npm install
npm run dev
```

Open the URL Nuxt prints (usually `http://localhost:3000`).

### Mock sign-in

1. Go to `/sign-in`
2. Seed account: `mike@johnsonoutdoor.example` / **`devpassword`**
3. New accounts: create account, then open the confirmation URL printed in the browser console (`[JobbPulse mock auth]`), then sign in with your password.

### Demo data

- Company: **Johnson Outdoor Living** / Mike Johnson
- Jobs: deck rebuild (active), kitchen (active), exterior painting (**ready for approval**)
- Photo minima: Before **2** / Progress **0** / After **2**

Reset mock data from the browser console:

```js
__jobbpulseReset()
```

## Scripts

| Command | Purpose |
| --- | --- |
| `npm run dev` | Dev server |
| `npm run build` | Production build |
| `npm run preview` | Preview production build |
| `npm test` | Unit tests (Vitest) |

## Environment

Copy `.env.example`:

```bash
# mock | http
NUXT_PUBLIC_API_MODE=mock
NUXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

| Mode | Behavior |
| --- | --- |
| `mock` | In-memory + `localStorage` seed data; simulates Engine + publishers |
| `http` | Uses `HttpApiClient` skeleton against `API_BASE_URL` (not implemented yet) |

## Architecture (backend-ready)

```
app/
  pages/                 # routes matching mockups
  components/            # UI primitives
  composables/           # useApi, useAuthSession
  services/api/
    client.ts            # ApiClient interface (port)
    mock/mockClient.ts   # MockApiClient
    httpClient.ts        # future HTTP implementation
  types/domain.ts        # shared domain types
  utils/jobStatus.ts     # status/action helpers
```

Screens and composables **must** use `useApi()` only. Do not call `fetch` from pages.

When a real backend exists:

1. Implement methods on `HttpApiClient` against `/api/v1` (prefer OpenAPI-generated types).
2. Set `NUXT_PUBLIC_API_MODE=http` and `NUXT_PUBLIC_API_BASE_URL`.
3. Keep domain types aligned with the server; avoid provider-specific payloads in UI.

## Routes

| Path | Screen |
| --- | --- |
| `/sign-in` | Auth |
| `/jobs` | My Jobs |
| `/jobs/new` | Create Job |
| `/jobs/:jobId` | Workspace |
| `/jobs/:jobId/photos/:category` | Photo gallery |
| `/jobs/:jobId/finish` | Finish + voice + submit |
| `/jobs/:jobId/approval` | Review & approve package |
| `/jobs/:jobId/approval/:assetId` | Content review |
| `/settings` | Settings + social |
| `/settings/social` | Connect / disconnect social accounts |
| `/settings/business-profile` | Business profile |
| `/settings/social-return` | Upload-Post OAuth return |

## Product notes

- Progress photos are optional for submit (minimum **0**); Before/After require **2** each.
- Google Business Profile row is visible but **gated** (not connectable via mock manage flow as fully available).
- Approve & publish and content generation are **simulated** only.

## Mockups

Visual authority lives in `../mockups/`.
