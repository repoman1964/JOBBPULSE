.PHONY: help install dev build generate preview deploy

help:
	@echo "JobbPulse marketing landing page"
	@echo "  make install    npm install"
	@echo "  make dev        Dev server on :3003"
	@echo "  make build      Production SSR build"
	@echo "  make generate   Static build for Cloudflare Workers"
	@echo "  make preview    Preview production build"
	@echo "  make deploy     Generate + wrangler deploy (jobbpulse-website)"

install:
	npm install

dev:
	npm run dev -- --port 3003 --host

build:
	npm run build

generate:
	npm run generate

preview:
	npm run preview -- --port 3003 --host

deploy:
	npm run deploy
