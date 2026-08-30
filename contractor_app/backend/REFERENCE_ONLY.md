# Reference only

`contractor_app/backend` is **not** the production API.

The only JobbPulse API is `api/` (FastAPI + Postgres + Redis + object storage).
The contractor Nuxt app talks to `api/` via `HttpApiClient`.

Keep this tree as a reference for phone route shapes, Upload-Post, and pipeline behavior. Do not deploy it. Do not run it next to `make api-dev` — both bind `:8000`.
