# JobbPulse — Local spin-up (frontend + backend)

Step-by-step guide to run the **Contractor App** (Nuxt) against the **JobbPulse Engine** (FastAPI) on your machine.

---

## Prerequisites

| Tool | Notes |
| --- | --- |
| **Docker** + Docker Compose | Backend stack (API, worker, Postgres, Redis, MinIO) |
| **Node.js** (v20 recommended) + npm | Frontend |
| **Make** | Optional convenience; you can use `docker compose` directly |

### Ports used by this project

| Port | Service |
| --- | --- |
| **3000** (or **3001** / **3002** if busy) | Nuxt frontend |
| **8000** | FastAPI API |
| **5433** | Postgres (host → container 5432) |
| **6380** | Redis (host → container 6379) |
| **9000** | MinIO (S3) |
| **9001** | MinIO console |

**Note:** Host ports **5433** / **6380** avoid clashes with local Postgres/Redis on 5432/6379.

Check free ports before starting:

```bash
ss -tln | grep -E ':(3000|3001|8000|5433|6380|9000)\s' || echo "none of those ports listening"
```

---

## Project root

All backend commands assume:

```bash
cd contractor_app
```

From the JobbPulse project root that is:

```bash
cd "/home/jose/Documents/DIMENSION SEVEN SYSTEMS/PROJECTS/JOBBPULSE/contractor_app"
```

---

## Part A — Backend

### A1. Create backend env file (first time only)

```bash
cp -n backend/.env.example backend/.env
```

You usually do **not** need to edit this for local Docker; Compose injects the main service URLs.

### A2. Start the backend stack

```bash
make up
```

Equivalent:

```bash
docker compose up -d --build
```

This starts:

- Postgres  
- Redis  
- MinIO (+ bucket init)  
- FastAPI API (runs migrations on start)  
- Celery worker  

### A3. Wait until healthy

```bash
docker compose ps
curl -s http://localhost:8000/health/live
curl -s http://localhost:8000/health/ready
```

Expected live/ready:

```json
{"status":"ok"}
```

Optional API docs: http://localhost:8000/docs  

### A4. Seed demo data (first time, or after wiping the DB)

```bash
make seed
```

Creates **Johnson Outdoor Living** and demo jobs.

If you see *“Seed company already exists — skipping”*, that is fine.

### A5. (Optional) Re-run migrations manually

Migrations already run when the API container starts. To re-run:

```bash
make migrate
```

---

## Part B — Frontend (desktop browser + real API)

Use a **second terminal**.

### B1. Install dependencies (first time, or after package changes)

```bash
cd frontend
npm install
```

### B2. Start Nuxt against the real backend

```bash
NUXT_PUBLIC_API_MODE=http \
NUXT_PUBLIC_API_BASE_URL=http://localhost:8000 \
npm run dev -- --host 0.0.0.0 --port 3000
```

| Variable | Meaning |
| --- | --- |
| `NUXT_PUBLIC_API_MODE=http` | Use the HTTP client (not the mock) |
| `NUXT_PUBLIC_API_BASE_URL=http://localhost:8000` | API URL (desktop) |

If port **3000** is busy, Nuxt may pick **3001** or **3002** automatically. That is OK — CORS allows 3000–3003 on localhost and your LAN IP.

### B3. Open the app

- Desktop: http://localhost:3000 (or http://localhost:3001)  
- Sign in:

| Field | Value |
| --- | --- |
| Email | `mike@johnsonoutdoor.example` |
| Code | `123456` |

---

## Part C — Frontend on a phone (Nuxt QR / Network URL)

Phone and PC must be on the **same Wi‑Fi**.

On the phone, `localhost` means the phone itself — so the API base URL must be your **PC’s LAN IP**.

### C1. Find your LAN IP

```bash
ip -4 route get 1.1.1.1 | awk '{for(i=1;i<=NF;i++) if($i=="src"){print $(i+1); exit}}'
```

Example: `10.0.0.156`

### C2. Ensure CORS allows that origin

Backend defaults already include common LAN URLs for `10.0.0.156` and `10.0.0.180`.  
If your IP is different, set CORS before starting the API:

```bash
export CORS_ORIGINS="http://localhost:3000,http://localhost:3001,http://localhost:3002,http://YOUR_LAN_IP:3000,http://YOUR_LAN_IP:3001,http://YOUR_LAN_IP:3002"
export S3_PUBLIC_ENDPOINT_URL="http://YOUR_LAN_IP:9000"
make up
```

Or edit `CORS_ORIGINS` in `backend/.env` and recreate the API container.

### C3. Start frontend for mobile

From `frontend/`:

```bash
./scripts/dev-mobile.sh
```

Or manually (replace the IP):

```bash
NUXT_PUBLIC_API_MODE=http \
NUXT_PUBLIC_API_BASE_URL=http://10.0.0.156:8000 \
npm run dev -- --host 0.0.0.0 --port 3000
```

### C4. On the phone

1. Scan the **QR code** Nuxt prints, or open the **Network** URL (e.g. `http://10.0.0.156:3000`).  
2. Sign in with the same seed credentials.  
3. Optional check: open `http://YOUR_LAN_IP:8000/health/live` on the phone — should return `{"status":"ok"}`.

---

## Quick reference — URLs

| What | URL |
| --- | --- |
| App (desktop) | http://localhost:3000 or :3001 |
| API | http://localhost:8000 |
| OpenAPI docs | http://localhost:8000/docs |
| MinIO console | http://localhost:9001 (`minioadmin` / `minioadmin`) |

---

## Make targets

| Command | Action |
| --- | --- |
| `make up` | Build/start full backend stack |
| `make down` | Stop backend stack |
| `make seed` | Load demo company/jobs |
| `make migrate` | Alembic upgrade |
| `make logs` | Follow API + worker logs |
| `make test` | Backend pytest |

---

## Shut everything down

### Backend

```bash
cd contractor_app
make down
```

### Frontend

Stop the terminal running Nuxt (`Ctrl+C`), or free the ports:

```bash
# if something is still listening
fuser -k 3000/tcp 2>/dev/null
fuser -k 3001/tcp 2>/dev/null
```

---

## Frontend-only mode (no backend)

Uses the **mock** API in the browser (no Docker):

```bash
cd frontend
npm install
npm run dev
```

Any email + code **`123456`**. Do **not** set `NUXT_PUBLIC_API_MODE=http`.

---

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| **Failed to fetch** on desktop | API down? `curl http://localhost:8000/health/live`. CORS: origin must match Nuxt port (`3000`–`3003`). Confirm `NUXT_PUBLIC_API_MODE=http`. |
| **Failed to fetch** on phone | API base must be LAN IP, not `localhost`. CORS must include `http://YOUR_LAN_IP:PORT` (e.g. `:3002` if QR shows 3002). Same Wi‑Fi. |
| Port **3000** in use | Nuxt picks 3001/3002 — fine if CORS includes that port. Or free lower ports. |
| Port **8000** / **5433** in use | Stop the other process or change mappings in `docker-compose.yml`. |
| Seed already exists | Safe to ignore; or wipe volumes: `docker compose down -v` then `make up && make seed`. |
| Worker not processing jobs | `docker compose logs worker`. Submit may fall back to inline processing if broker is down. |

---

## Checklist (happy path)

1. [ ] `cp -n backend/.env.example backend/.env`  
2. [ ] `make up`  
3. [ ] `curl http://localhost:8000/health/ready` → ok  
4. [ ] `make seed` (first time)  
5. [ ] `cd frontend && npm install`  
6. [ ] Start Nuxt with `NUXT_PUBLIC_API_MODE=http` and `NUXT_PUBLIC_API_BASE_URL=http://localhost:8000`  
7. [ ] Open app → sign in as Mike / `123456`  
8. [ ] (Optional) Phone: `./scripts/dev-mobile.sh` + QR  

---

## Related docs

- Master product/build spec: [`contractor_app_build_instructions.md`](./contractor_app_build_instructions.md)  
- Backend details: [`backend/README.md`](./backend/README.md)  
- Architecture notes: [`backend/docs/ARCHITECTURE.md`](./backend/docs/ARCHITECTURE.md)  
- Root overview: [`README.md`](./README.md)  
