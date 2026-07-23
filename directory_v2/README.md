# JobPulse Directory v2 — Local Project Portfolio

Public-facing Nuxt SSR app that presents JobPulse as a **living portfolio of completed projects**, not a traditional company directory.

## Stack

- Nuxt 4 (SSR)
- JobPulse FastAPI (`/api/v1/public/*`)
- PostgreSQL via the shared monorepo API

## Local development

```bash
# From repo root
make infra-up
make api-migrate
make api-dev                 # :8000

# Seed Georgia demo inventory (optional but recommended)
cd api && PYTHONPATH=. .venv/bin/python scripts/seed_directory_v2.py

make directory-install
make directory-dev           # :3001 → directory_v2
```

Environment (optional):

- `NUXT_PUBLIC_API_BASE_URL` — default `http://localhost:8000`
- `NUXT_PUBLIC_APP_URL` — contractor app, default `http://localhost:3000`
- `NUXT_PUBLIC_DIRECTORY_URL` — this site, default `http://localhost:3001`

## Product rules

- Primary object is the **project**
- No private job titles or exact residential addresses
- Service × location pages only when inventory exists
- Lead forms persist attribution to the contractor (and source project when present)

## Note

This app is greenfield. Do not copy from `directory_v1/`.
