.PHONY: up down up-infra logs migrate seed test lint api-shell

up:
	docker compose up -d --build

up-infra:
	docker compose up -d postgres redis minio minio-init

down:
	docker compose down

logs:
	docker compose logs -f api worker

migrate:
	docker compose exec api alembic upgrade head

seed:
	docker compose exec api python -m scripts.seed

test:
	docker compose exec api pytest -q /app/tests

lint:
	docker compose exec api ruff check app tests
	docker compose exec api ruff format --check app tests

api-shell:
	docker compose exec api bash
