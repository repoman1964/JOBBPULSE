# JobbPulse Backend (Engine)

FastAPI service for authentication, jobs, media, content generation orchestration, and publishing.

## Stack

- FastAPI + Pydantic v2
- PostgreSQL + SQLAlchemy 2 (async) + Alembic
- Redis + Celery workers
- S3-compatible storage (MinIO locally)
- Provider interfaces with **fake** adapters for local development

## Quick start (Docker)

From the repository root:

```bash
cp backend/.env.example backend/.env
make up
make migrate
make seed
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs  
Health: http://localhost:8000/health/live

Sign in with seed account `mike@johnsonoutdoor.example` and code **`123456`** (dev OTP).

## Local (without full Compose API)

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
# ensure Postgres, Redis, MinIO are running (make up-infra)
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload --port 8000
# worker
celery -A app.tasks.celery_app.celery_app worker -l info
```

## Environment

See [`.env.example`](./.env.example). Production must set a strong `JWT_SECRET` and `APP_ENV=production` (which disables `AUTH_DEV_CODES`).

## Tests

```bash
make test
# or
cd backend && pytest -q
```

## Architecture notes

- **Tenancy:** every query is scoped by `company_id` from the authenticated JWT.
- **Uploads:** presigned PUT to object storage, then `complete` to finalize.
- **Pipeline:** job submit enqueues Celery `process_job_submission` (not FastAPI BackgroundTasks).
- **Social:** Upload-Post keys stay server-side; webhooks update `social_connections`.
- **First-party sites:** Conversion Site and Portfolio publishers are separate from Upload-Post.
