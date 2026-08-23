.PHONY: help install dev build preview

help:
	@echo "Red Clay — painting website"
	@echo "  make install   npm install"
	@echo "  make dev       Dev server on :3002"
	@echo "  make build     Production build"
	@echo "  make preview   Preview production build"

install:
	npm install

dev:
	npm run dev -- --port 3002 --host

build:
	npm run build

preview:
	npm run preview -- --port 3002 --host
