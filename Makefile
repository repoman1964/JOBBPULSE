.PHONY: help dev infra-up infra-down api-install api-dev api-test api-migrate portfolio-seed red-clay-seed lint

help:
	@echo "JobbPulse development commands"
	@echo "  make infra-up            Start postgres, redis, minio, mailpit"
	@echo "  make infra-down          Stop infrastructure"
	@echo "  make api-install         Install API Python deps into api/.venv"
	@echo "  make api-dev             Run FastAPI with reload on :8000"
	@echo "  make api-migrate         Apply Alembic migrations"
	@echo "  make api-test            Run API tests"
	@echo "  make portfolio-seed      Seed Georgia demo projects (public portfolio API)"
	@echo "  make red-clay-seed       Force-seed Red Clay (photos + mock social)"
	@echo "  make dev                 Start infra + print next steps"
	@echo ""
	@echo "Apps:"
	@echo "  contractor_app/frontend  Contractor phone UI (HTTP mode talks to api/)"
	@echo "                            → cd contractor_app/frontend && NUXT_PUBLIC_API_MODE=http npm run dev"
	@echo "  website/portfolio_website   Public portfolio site → make -C website/portfolio_website dev"
	@echo "  website/red_clay_website    Red Clay marketing site → make -C website/red_clay_website dev"
	@echo "  website/marketing_website   JobbPulse landing page → make -C website/marketing_website dev"

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

portfolio-seed:
	cd api && PYTHONPATH=. .venv/bin/python scripts/seed_portfolio.py

red-clay-seed:
	cd api && PYTHONPATH=. .venv/bin/python scripts/seed_red_clay_demo.py

dev: infra-up
	@echo ""
	@echo "Infrastructure is up."
	@echo "  API:            make api-dev          → http://localhost:8000/docs"
	@echo "  Seed demo:      make portfolio-seed"
	@echo "  Red Clay seed:  make red-clay-seed    (photos + mock FB/IG pubs)"
	@echo "  Mailpit:        http://localhost:8025"
	@echo "  MinIO:          http://localhost:9001 (minioadmin / minioadmin)"
	@echo "  Contractor app: NUXT_PUBLIC_API_MODE=http NUXT_PUBLIC_API_BASE_URL=http://localhost:8000"
	@echo "                  cd contractor_app/frontend && npm run dev  → :3000 (talks to api/)"
	@echo "  Portfolio site: make -C website/portfolio_website dev  → http://localhost:3001"
	@echo "  Red Clay site:  make -C website/red_clay_website dev   → http://localhost:3002"
	@echo "  Landing page:   make -C website/marketing_website dev  → http://localhost:3003"
	@echo ""
