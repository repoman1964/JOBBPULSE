.PHONY: help dev infra-up infra-down api-install api-dev api-test mobile-install mobile-dev directory-install directory-dev directory-seed lint

help:
	@echo "JobPulse development commands"
	@echo "  make infra-up          Start postgres, redis, minio, mailpit"
	@echo "  make infra-down        Stop infrastructure"
	@echo "  make api-install       Install API Python deps into api/.venv"
	@echo "  make api-dev           Run FastAPI with reload on :8000"
	@echo "  make api-migrate       Apply Alembic migrations"
	@echo "  make api-test          Run API tests"
	@echo "  make mobile-install    npm install for mobile_app"
	@echo "  make mobile-dev        Run contractor app on :3000"
	@echo "  make directory-install npm install for directory_v2"
	@echo "  make directory-dev     Run public portfolio (directory_v2) on :3001"
	@echo "  make directory-seed    Seed Georgia demo projects for directory_v2"
	@echo "  make dev               Start infra + print next steps"

infra-up:
	docker compose -f infra/docker-compose.yml up -d

infra-down:
	docker compose -f infra/docker-compose.yml down

api-install:
	cd api && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

api-dev:
	cd api && PYTHONPATH=. .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

api-test:
	cd api && PYTHONPATH=. .venv/bin/pytest -q

api-migrate:
	cd api && PYTHONPATH=. .venv/bin/alembic upgrade head

mobile-install:
	cd mobile_app && npm install

mobile-dev:
	cd mobile_app && npm run dev -- --port 3000 --host

directory-install:
	cd directory_v2 && npm install

directory-dev:
	cd directory_v2 && npm run dev -- --port 3001 --host

directory-seed:
	cd api && PYTHONPATH=. .venv/bin/python scripts/seed_directory_v2.py

dev: infra-up
	@echo ""
	@echo "Infrastructure is up."
	@echo "  API:        make api-dev        → http://localhost:8000/docs"
	@echo "  Mobile app: make mobile-dev     → http://localhost:3000"
	@echo "  Directory:  make directory-dev  → http://localhost:3001 (directory_v2)"
	@echo "  Seed demo:  make directory-seed"
	@echo "  Mailpit:    http://localhost:8025"
	@echo "  MinIO:      http://localhost:9001 (minioadmin / minioadmin)"
	@echo ""
