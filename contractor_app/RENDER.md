# Deploy the Contractor App on Render

Render runs the Nuxt contractor UI, the FastAPI engine, and the Celery worker. Job photos and voice files go to **Cloudflare R2** (S3-compatible). The marketing site stays on Cloudflare.

Blueprint file: [`render.yaml`](../render.yaml) at the repo root.

## What the blueprint creates

| Resource | Render name | Role |
| --- | --- | --- |
| Static site | `jobbpulse-app` | Contractor UI (`nuxt generate`) |
| Web service | `jobbpulse-api` | FastAPI (`api/Dockerfile`) |
| Worker | `jobbpulse-worker` | Celery (`api/` worker) |
| Postgres | `jobbpulse-db` | Jobs, users, packages |
| Key Value | `jobbpulse-redis` | Celery broker |

Use **starter** (or larger) for the API. Do not use a free web service — it sleeps, which is painful on a phone at a job site.

Suggested custom domains (add in the dashboard after the first deploy):

- `app.jobbpulse.com` → `jobbpulse-app`
- `api.jobbpulse.com` → `jobbpulse-api`

## 1. Cloudflare R2 (photos)

Production object storage is **Cloudflare R2** on the Dimension Seven Systems account. The bucket **`jobbpulse`** already exists (WNAM). CORS for the Render app origin and `https://app.jobbpulse.com` is applied from [`api/r2-cors.json`](../api/r2-cors.json).

S3 API endpoint (use for both Render `S3_ENDPOINT_URL` and `S3_PUBLIC_ENDPOINT_URL`):

```text
https://b6120b2d531b6d97dfe538cc57780ea9.r2.cloudflarestorage.com
```

`S3_BUCKET=jobbpulse`  
`S3_REGION=auto`

Create an **R2 API token** (dashboard → R2 → Manage R2 API Tokens) with Object Read & Write on `jobbpulse`. Put the access key id and secret into Render as `S3_ACCESS_KEY` / `S3_SECRET_KEY`. Wrangler login cannot be used as S3 credentials.

Presigned PUT/GET go to the S3 API host above. They do **not** work on an R2 custom domain. Browsers upload directly to R2; the API never sees the file bytes.

To refresh CORS after adding origins:

```bash
npx wrangler r2 bucket cors set jobbpulse --file api/r2-cors.json
```

## 2. Apply the blueprint

`jobbpulse-api` and `jobbpulse-worker` must build from **`api/`**, not `contractor_app/backend` (that folder was removed). If a deploy fails with `lstat .../contractor_app/backend: no such file or directory`, open each service → **Settings → Build & Deploy** and set:

| Field | Value |
| --- | --- |
| Root Directory | `api` |
| Dockerfile Path | `./Dockerfile` |
| Docker Build Context Directory | `.` |

Then **Manual Deploy**.

1. Push this repo to GitHub (`main`).
2. Render dashboard → **New** → **Blueprint**.
3. Select `repoman1964/JOBBPULSE` and `render.yaml`.
4. When prompted, set:

| Variable | Service | Value |
| --- | --- | --- |
| `NUXT_PUBLIC_API_BASE_URL` | `jobbpulse-app` | `https://api.jobbpulse.com` |
| `FRONTEND_BASE_URL` | engine group | `https://app.jobbpulse.com` |
| `CORS_ORIGINS` | engine group | `https://app.jobbpulse.com,https://jobbpulse-app.onrender.com,https://red-clay-website.pages.dev` |
| `S3_ENDPOINT_URL` | engine group | `https://b6120b2d531b6d97dfe538cc57780ea9.r2.cloudflarestorage.com` |
| `S3_PUBLIC_ENDPOINT_URL` | engine group | Same as `S3_ENDPOINT_URL` |
| `S3_ACCESS_KEY` | engine group | R2 API token access key id |
| `S3_SECRET_KEY` | engine group | R2 API token secret |

`JWT_SECRET` is generated. `APP_ENV=production` turns off the `123456` dev sign-in code. `AUTH_SHOW_OTP=true` still returns OTP codes in the API for the legacy phone/email code flow (that path does not send mail). **Signup confirmation is different:** register creates a pending contractor and Resend must deliver the verify link or the account stays inactive.

Set these on the `jobbpulse-engine` env group or signup emails will not arrive:

| Variable | Service | Value |
| --- | --- | --- |
| `RESEND_API_KEY` | engine group | Resend API key (`re_…`) |
| `AUTH_FROM_EMAIL` | engine group | `JobbPulse <hello@jobbpulse.com>` **after** `jobbpulse.com` is verified in Resend. Leave `onboarding@resend.dev` only for sending to the Resend account owner's inbox. |
| `PUBLIC_API_BASE_URL` | engine group | `https://api.jobbpulse.com` |

`onboarding@resend.dev` is Resend's test sender. It **rejects** any recipient other than the email on the Resend account (HTTP 403: “You can only send testing emails to your own email address”). To activate real contractors:

1. Resend dashboard → **Domains** → add and verify `jobbpulse.com` (SPF/DKIM DNS).
2. Set `AUTH_FROM_EMAIL` to an address on that domain (`JobbPulse <hello@jobbpulse.com>`).
3. Restart `jobbpulse-api` (and the worker if it ever sends mail).
4. Confirm API logs show `Verification email sent … resend_id=…` on signup, not `Resend send failed` / `RESEND_API_KEY is not set`.

The static site bakes `NUXT_PUBLIC_API_BASE_URL` in at **build** time. If the API URL is wrong on the first pass, set it and **Manual Deploy** the static site.

Custom domains (`app.jobbpulse.com` → `jobbpulse-app`, `api.jobbpulse.com` → `jobbpulse-api`):

1. Point DNS at Render and wait until both hosts resolve over HTTPS.
2. Set `CORS_ORIGINS`, `FRONTEND_BASE_URL`, and `NUXT_PUBLIC_API_BASE_URL` as in the table above.
3. Optionally set `COOKIE_DOMAIN=.jobbpulse.com` on the engine group.
4. Manual Deploy **jobbpulse-api** (CORS / email links) and **jobbpulse-app** (API URL is baked at build).

## 3. Smoke check

```bash
curl -sS https://api.jobbpulse.com/health/live
curl -sS https://api.jobbpulse.com/health/ready
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
