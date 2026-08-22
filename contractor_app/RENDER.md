# Deploy the Contractor App on Render

Render runs the Nuxt contractor UI, the FastAPI engine, and the Celery worker. Job photos and voice files go to **Cloudflare R2** (S3-compatible). The marketing site stays on Cloudflare.

Blueprint file: [`render.yaml`](../render.yaml) at the repo root.

## What the blueprint creates

| Resource | Render name | Role |
| --- | --- | --- |
| Static site | `jobbpulse-app` | Contractor UI (`nuxt generate`) |
| Web service | `jobbpulse-api` | FastAPI (`Dockerfile.prod`) |
| Worker | `jobbpulse-worker` | Celery (`process_job_submission`) |
| Postgres | `jobbpulse-db` | Jobs, users, packages |
| Key Value | `jobbpulse-redis` | Celery broker |

Use **starter** (or larger) for the API. Do not use a free web service — it sleeps, which is painful on a phone at a job site.

Suggested custom domains (add in the dashboard after the first deploy):

- `app.jobbpulse.com` → `jobbpulse-app`
- `api.jobbpulse.com` → `jobbpulse-api`

## 1. Cloudflare R2 (photos)

1. In Cloudflare: **R2** → create a bucket named `jobbpulse` (or match `S3_BUCKET`).
2. Create an R2 API token with Object Read & Write on that bucket.
3. Note the S3 API URL: `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`
4. Bucket **Settings → CORS policy** — allow PUT/GET from the app origin:

```json
[
  {
    "AllowedOrigins": [
      "https://jobbpulse-app.onrender.com",
      "https://app.jobbpulse.com"
    ],
    "AllowedMethods": ["GET", "PUT", "HEAD"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": ["ETag", "Content-Type"],
    "MaxAgeSeconds": 3600
  }
]
```

Replace the onrender.com origin with the real static-site URL after the first deploy. Browsers upload **directly to R2** with a presigned PUT; the API never sees the file bytes.

## 2. Apply the blueprint

1. Push this repo to GitHub (`main`).
2. Render dashboard → **New** → **Blueprint**.
3. Select `repoman1964/JOBBPULSE` and `render.yaml`.
4. When prompted, set:

| Variable | Service | Value |
| --- | --- | --- |
| `NUXT_PUBLIC_API_BASE_URL` | `jobbpulse-app` | `https://jobbpulse-api.onrender.com` (or `https://api.jobbpulse.com`) |
| `FRONTEND_BASE_URL` | engine group | `https://jobbpulse-app.onrender.com` (or `https://app.jobbpulse.com`) |
| `CORS_ORIGINS` | engine group | Same as the app origin (comma-separated if both onrender + custom domain) |
| `S3_ENDPOINT_URL` | engine group | `https://<ACCOUNT_ID>.r2.cloudflarestorage.com` |
| `S3_PUBLIC_ENDPOINT_URL` | engine group | Same as `S3_ENDPOINT_URL` |
| `S3_ACCESS_KEY` | engine group | R2 access key id |
| `S3_SECRET_KEY` | engine group | R2 secret access key |

`JWT_SECRET` is generated. `APP_ENV=production` turns off the `123456` dev sign-in code.

The static site bakes `NUXT_PUBLIC_API_BASE_URL` in at **build** time. If the API URL is wrong on the first pass, set it and **Manual Deploy** the static site.

If you add `app.jobbpulse.com` / `api.jobbpulse.com` later:

1. Point DNS at Render.
2. Update `CORS_ORIGINS`, `FRONTEND_BASE_URL`, R2 CORS, and `NUXT_PUBLIC_API_BASE_URL`.
3. Optionally set `COOKIE_DOMAIN=.jobbpulse.com` on the engine group.
4. Redeploy API + app.

## 3. Smoke check

```bash
curl -sS https://jobbpulse-api.onrender.com/health/live
curl -sS https://jobbpulse-api.onrender.com/health/ready
```

Open the static site, request a sign-in code for a real contractor email (dev codes are off). Seed data is **not** loaded in production; run seed only against a throwaway database if you need demo jobs.

## Local vs production

| | Local | Render |
| --- | --- | --- |
| Frontend | `npm run dev` | static `nuxt generate` |
| API image | `backend/Dockerfile` (includes test extras) | `backend/Dockerfile.prod` |
| Object store | MinIO | R2 |
| Auth codes | `AUTH_DEV_CODES=true` | forbidden |

## Render dashboard notes

- API health check: `/health/live`
- Migrations: `preDeployCommand` on `jobbpulse-api` (`alembic upgrade head`)
- Worker uses the same image and env group; it does not run migrations
