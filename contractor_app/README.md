# JobbPulse Contractor App

Mobile-first contractor UI for documenting jobs and approving JobbPulse-generated marketing.

This folder is **frontend only**. The API is `../api/` (one FastAPI app, one Postgres).

## Local

From the repo root: `make infra-up && make api-dev`

Then:

```bash
cd frontend
NUXT_PUBLIC_API_MODE=http NUXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

→ http://localhost:3000

Mock-only (no API): omit `NUXT_PUBLIC_API_MODE` or set it to `mock`.

See [`LOCAL_SETUP.md`](./LOCAL_SETUP.md).
