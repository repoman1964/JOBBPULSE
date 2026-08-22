# JobbPulse Portfolio Website

Public-facing **local project portfolio** (Nuxt SSR). Presents JobbPulse as a living gallery of completed contractor projects—not a traditional company directory.

This site lives under the JobbPulse project folder and talks to the JobbPulse public API over HTTP when that stack is running. It keeps its own git remote.

## Stack

- Nuxt 4 / Vue 3 (SSR)
- JobbPulse FastAPI (`/api/v1/public/*`)
- PostgreSQL via the shared JobbPulse API

## Features

| Area | Routes |
|---|---|
| Home (featured projects + contractors) | `/` |
| Projects hub + detail | `/projects`, `/projects/{slug}` |
| Contractors hub + portfolio / about | `/contractors`, `/contractors/{slug}`, `…/portfolio`, `…/about` |
| Services × locations SEO pages | `/services`, `/locations`, `/locations/{slug}/{service}` |
| Search, how it works, for contractors | `/search`, `/how-it-works`, `/for-contractors` |

### JobbPulse API (required for live data)

The app expects the JobbPulse API at `NUXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`).

Run the platform from the JobbPulse project root:

```bash
cd ..
make infra-up
make api-migrate
make api-dev          # → http://localhost:8000/docs
make portfolio-seed   # optional Georgia demo inventory
```

## Quick start

```bash
cd portfolio_website
cp .env.example .env   # optional; defaults work for localhost
make install
make dev
# → http://localhost:3001
```

Or:

```bash
npm install
npm run dev -- --port 3001 --host
```

### Env

| Variable | Default |
|---|---|
| `NUXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` |
| `NUXT_PUBLIC_APP_URL` | `http://localhost:3000` |
| `NUXT_PUBLIC_DIRECTORY_URL` | `http://localhost:3001` |

For phone-on-LAN demos, set all three to your machine’s LAN IP (and allow CORS on the API if needed). Restart `make dev` after changing `.env`.

## Product rules

- Primary object is the **project**
- No private job titles or exact residential addresses
- Service × location pages only when inventory exists
- Lead forms persist attribution to the contractor (and source project when present)

## Related projects

| Path | Purpose |
|---|---|
| `../` (JobbPulse root) | API, infra, seed scripts |
| `../contractor_app` | Contractor phone app (capture → publish) |
| `../red_clay_website` | Red Clay marketing demo site |
