# Red Clay Cabinet Installers — website

Standalone demo **marketing site** for Red Clay Cabinet Installers (metro Atlanta).

This site lives under the JobbPulse project folder and can optionally load live “recent jobs” and submit estimate leads via the JobbPulse public API when that stack is running. It keeps its own git remote.

## Stack

- Nuxt 4 / Vue 3 (SSR)
- Georgia clay brand styling
- SEO silos: services, locations, and location × service pages

## Features

| Area | Routes |
|---|---|
| Home + above-the-fold recent jobs widget | `/` |
| Services hub + per-service pages | `/services`, `/services/{slug}` |
| Locations hub + city pages | `/service-area`, `/service-area/{city}` |
| Local money pages | `/service-area/{city}/{service}` |
| Portfolio (from API when available) | `/portfolio`, `/portfolio/{slug}` |
| About, reviews, FAQ, contact | `/about`, `/reviews`, `/faq`, `/contact` |

### JobbPulse integration (optional)

| Capability | API |
|---|---|
| Recent / portfolio jobs | `GET /api/v1/public/projects?contractor_slug=…` |
| Project detail | `GET /api/v1/public/projects/{slug}` |
| Estimate form leads | `POST /api/v1/public/leads` |

If the API is offline, the site still works with fallback demo job cards and local before/after photos under `public/portfolio/`.

Seed data for the Red Clay contractor lives in the JobbPulse repo:

```bash
cd ..
make red-clay-seed   # force-seed 6 projects + photos + mock FB/IG publications
# (cd .. && make portfolio-seed still seeds the broader Georgia portfolio inventory)
```

Contractor login after seed:

- Email: `owner+red-clay-cabinet-installers@demo.jobpulse.local`
- Password: `password123`

## Quick start

```bash
cd red_clay_website
cp .env.example .env   # optional
make install
make dev
# → http://localhost:3002
```

Or:

```bash
npm install
npm run dev -- --port 3002 --host
```

### Env

| Variable | Default |
|---|---|
| `NUXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` |
| `NUXT_PUBLIC_CONTRACTOR_SLUG` | `red-clay-cabinet-installers` |
| `NUXT_PUBLIC_DIRECTORY_URL` | `http://localhost:3001` |

## Cloudflare Pages (Connect to Git)

This app uses the Nitro **`cloudflare-pages`** preset (output: `dist/`).

| Setting | Value |
|---|---|
| Project name | `red-clay-website` |
| Custom domain | **`demo.jobbpulse.com`** |
| Production branch | `main` |
| Build command | `npm run build` |
| Build output directory | **`dist`** (not `.output` or `dist/public`) |
| Node version | **`22`** (set env `NODE_VERSION=22`) — Nuxt 4.5 needs ≥22.19 |

**Environment variables** (Pages → Settings → Environment variables):

| Name | Example |
|---|---|
| `NODE_VERSION` | `22` |
| `NUXT_PUBLIC_API_BASE_URL` | `https://api.jobbpulse.com` |
| `NUXT_PUBLIC_CONTRACTOR_SLUG` | `red-clay-cabinet-installers` |
| `NUXT_PUBLIC_DIRECTORY_URL` | Optional directory URL |

Repo includes `.npmrc` (`legacy-peer-deps=true`) so Cloudflare’s `npm ci` matches local installs. If install fails with lockfile/sync errors, ensure the latest `package-lock.json` is on `main`.

Manual direct upload (optional):

```bash
npm run deploy   # build + wrangler pages deploy dist
```

## Related

JobbPulse platform (API, contractor app, directory) is the parent folder:

```
../
```

Typical local ports when both run:

| App | Port |
|---|---|
| JobbPulse API | 8000 |
| Contractor app | 3000 |
| JobbPulse directory | 3001 |
| **This site** | **3002** |

## SEO siloing

```
/services  →  /services/kitchen-cabinets  →  /service-area/atlanta/kitchen-cabinets
/service-area  →  /service-area/atlanta  →  /service-area/atlanta/kitchen-cabinets
```

- Breadcrumbs on silo pages  
- Service pages link to every city leaf  
- Location pages link to every service leaf  
- Leaf pages link up to both parents and sideways to siblings  
- Footer lists full Services + Locations silos  

## License

Demo / internal use for JobbPulse product demos.
