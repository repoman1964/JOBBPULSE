# JobbPulse — Local spin-up (contractor UI + `api/`)

The contractor app is **frontend only**. All backend lives in `../api/` against the **one** Postgres in `infra/`.

## Ports

| Port | Service |
| --- | --- |
| **3000** | Contractor Nuxt UI |
| **8000** | `api/` FastAPI |
| **5433** | Postgres |
| **6380** | Redis |
| **9000** / **9001** | MinIO |

From the **repo root**:

```bash
make infra-up
make api-install          # first time
cp -n api/.env.example api/.env
make api-migrate
make api-dev              # http://localhost:8000
```

Then the UI:

```bash
cd contractor_app/frontend
NUXT_PUBLIC_API_MODE=http \
NUXT_PUBLIC_API_BASE_URL=http://localhost:8000 \
npm run dev -- --host 0.0.0.0 --port 3000
```

Open http://localhost:3000. Create an account (email + password), confirm the link, then sign in.

### Email (Resend)

Signup confirmation and forgot-password send through Resend when `api/.env` has a key **and** a from-address on the verified `jobbpulse.com` domain:

```
RESEND_API_KEY=re_...
EMAIL_FROM=JobbPulse <hello@jobbpulse.com>
```

Restart `make api-dev` after changing env. Links in those emails use `FRONTEND_URL` (default `http://localhost:3000`). API logs should show `Verification email sent … resend_id=…` (or `Password reset email sent`), not `skipped live send`.

`make api-test` never calls Resend.

Red Clay (optional, port 3002) also talks to `http://localhost:8000`.
