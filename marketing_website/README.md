# JobbPulse marketing landing page

One-page sales site. Not a full marketing website.

Warm paper, ink type, and clay accents on the page. Dark charcoal and electric lime stay on the Contractor App screenshots.

Deploy target: Cloudflare Workers (static assets) — Worker name `jobbpulse-website`.

## Quick start

```bash
cp .env.example .env   # optional
make install
make dev
# → http://localhost:3003
```

## Scope

This page is meant to stay short until JobbPulse is selling. Do not add pricing, blog, FAQ, or a Portfolio nav item unless that changes.

| Env | Default |
|---|---|
| `NUXT_PUBLIC_APP_URL` | `http://localhost:3000` |
| `NUXT_PUBLIC_CONTACT_EMAIL` | `hello@jobbpulse.com` |

## Cloudflare deploy (monorepo)

This site lives in the **`marketing_website/`** folder of the [JOBBPULSE](https://github.com/repoman1964/JOBBPULSE) repo.

### One-time: connect Workers Builds to the monorepo

In the [Cloudflare dashboard](https://dash.cloudflare.com) → **Workers & Pages** → **`jobbpulse-website`** → **Settings** → **Builds**:

1. **Connect** GitHub repo **`repoman1964/JOBBPULSE`**.
   - If the repo does not appear, open [GitHub → Settings → Applications → Cloudflare Workers](https://github.com/settings/installations) and grant the Cloudflare Workers app access to **`JOBBPULSE`** (or all repos).
2. Use these build settings:

| Setting | Value |
|---|---|
| **Git repository** | `repoman1964/JOBBPULSE` |
| **Production branch** | `main` |
| **Root directory** | `marketing_website` |
| **Build command** | `npm run generate` |
| **Deploy command** | `npx wrangler deploy --config wrangler.jsonc` |
| **Non-production deploy** (optional) | `npx wrangler versions upload` |
| **Build watch paths (include)** | `marketing_website/**` |

**Critical:** The Worker name in the dashboard must stay **`jobbpulse-website`** — it must match `"name"` in `marketing_website/wrangler.jsonc`.

Optional build variables:

| Variable | Value |
|---|---|
| `NODE_VERSION` | `22` (also set via `.nvmrc`) |
| `NUXT_PUBLIC_APP_URL` | production Contractor App URL |
| `NUXT_PUBLIC_CONTACT_EMAIL` | `hello@jobbpulse.com` |

After saving, push a commit that touches `marketing_website/` (or trigger a manual build) to verify.

### Manual deploy from this machine

```bash
cd marketing_website
npm ci
npm run deploy
```

`npm run deploy` prerenders the site with `nuxt generate` (output: `.output/public`) and runs `wrangler deploy`.

## Requirements

- Node.js **22.19+**

```bash
# if you use nvm
nvm use 22
```

## Commands

```bash
npm install
npm run dev        # local dev server
npm run generate   # static production build → .output/public
npm run preview    # preview production build
npm run deploy     # generate + wrangler deploy
```
