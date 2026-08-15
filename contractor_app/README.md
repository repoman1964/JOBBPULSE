# JobbPulse Contractor App

Mobile-first contractor experience for documenting jobs and approving JobbPulse-generated marketing content.

Lives at `JOBBPULSE/contractor_app/` (this is the current contractor app).

## Projects

| Folder | Stack | Role |
| --- | --- | --- |
| [`frontend/`](./frontend/) | Nuxt 3 + Vue 3 + TypeScript | Contractor App UI |
| [`backend/`](./backend/) | FastAPI + PostgreSQL + Celery + MinIO | JobbPulse Engine API & workers |

## Full local stack

**Step-by-step (recommended):** see **[`LOCAL_SETUP.md`](./LOCAL_SETUP.md)** — backend, frontend, phone QR, ports, shutdown, troubleshooting.

Short version:

```bash
# Infra + API + worker
cp backend/.env.example backend/.env
make up
make migrate   # already runs on API start; safe to re-run
make seed

# Frontend (separate terminal)
cd frontend
npm install
NUXT_PUBLIC_API_MODE=http NUXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

- API: http://localhost:8000  
- OpenAPI: http://localhost:8000/docs  
- App: http://localhost:3000 (or :3001 if 3000 is busy)  

**Seed sign-in:** `mike@johnsonoutdoor.example` · code **`123456`**

### Frontend-only (mock API)

```bash
cd frontend
npm install
npm run dev
```

Any email + code `123456` (mock client).

## Specs

- Local spin-up guide: [`LOCAL_SETUP.md`](./LOCAL_SETUP.md)
- Master build document: [`contractor_app_build_instructions.md`](./contractor_app_build_instructions.md)
- Approved mockups: [`mockups/`](./mockups/)
- Backend details: [`backend/README.md`](./backend/README.md)

## Make targets

| Target | Description |
| --- | --- |
| `make up` | Build and start Compose stack |
| `make up-infra` | Postgres, Redis, MinIO only |
| `make down` | Stop stack |
| `make migrate` | Alembic upgrade head |
| `make seed` | Johnson Outdoor Living demo data |
| `make test` | Backend pytest |
| `make logs` | Follow API + worker logs |
