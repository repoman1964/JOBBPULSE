# Red Clay painting demo site

**Date:** 2026-08-23  
**Status:** Draft for review  
**Surfaces:** `website/red_clay_website` (conversion site), `contractor_app` (signup + public project read)

## 1. Problem

JobbPulse needs a live sales demo that looks like a real metro-Atlanta painting company website. A prospect pretends Red Clay is their site: they create a contractor-app account, upload a job (photos + description), then enter the same email on Red Clay and see that job on the homepage carousel and a project page that also shows the Facebook, Instagram, and Google Business posts JobbPulse generated.

The current Red Clay site is a cabinet installer, uses the platform directory API (`api/`), and does not show social destination copy. The contractor app generates FB/IG/GBP assets but has no self-serve signup and no public read of those jobs. Conversion-site publish is a stub. Those pieces must connect for the walkthrough.

## 2. Goals

- Red Clay reads as a real exterior-led painting company. No “demo,” no JobbPulse branding on public chrome.
- Site meets Kai’s criteria for a good contractor website (see §9).
- Visual system is Premium Craft (Custom Roofing prompt structure) with Georgia clay as the accent, not brass and not navy/orange.
- Dummy paint jobs fill the site when nobody has identified themselves.
- After the prospect enters the contractor-app email, their generated jobs appear first; dummy jobs remain.
- Project pages show before/after plus Facebook, Instagram, and Google Business cards from generated assets.
- GHL is not wired. `/book` is an empty calendar mount for a later paste.

## 3. Non-goals

- Renaming the wordmark to the prospect’s company.
- A new company profile/site per prospect.
- Full OTP/session on the painting site (email-only identification).
- Production-grade auth for the email gate.
- Wiring GoHighLevel forms or calendars.
- Making `ConversionSitePublisher` push pages (Red Clay **pulls**).
- Changing social generation copy, Upload-Post, or the contractor job workspace beyond signup + the public read API.
- Platform `api/` directory seed (`red-clay-cabinet-installers`) as the live source of homepage jobs.

## 4. Demo walkthrough

1. Prospect browses Red Clay at `http://localhost:3002`. Dummy metro-Atlanta paint jobs fill Work and the homepage carousel.
2. Operator sends them to the contractor app (`http://localhost:3000`). They **create an account** (name, email, company) then sign in with the existing OTP flow.
3. They create a job, upload photos + description, submit, and wait until FB/IG/GBP assets exist (status `ready_for_approval` or later).
4. On Red Clay they open footer **See your project** → `/my-work`, enter **the same email**.
5. Cookie remembers the email. Homepage carousel prepends their job(s). `/work/{slug}` shows photos, write-up, and the three social cards.

Wordmark stays **Red Clay**. Tagline: Painting · Metro Atlanta.

## 5. Architecture

```
[Prospect browser]
    │
    ├─ Red Clay Nuxt (:3002)
    │     static dummy jobs + Premium Craft UI
    │     GET contractor_app /api/v1/public/demo/projects?email=
    │     GET contractor_app /api/v1/public/demo/projects/{slug}
    │     cookie: red_clay_demo_email
    │
    └─ Contractor app Nuxt (:3000)
          POST /api/v1/auth/register  (new)
          existing OTP + jobs + generation
          Engine DB (Postgres) + MinIO media
```

Red Clay’s `NUXT_PUBLIC_API_BASE_URL` (or a dedicated `NUXT_PUBLIC_CONTRACTOR_API_BASE_URL`) points at the **contractor-app engine** on `:8000`, not the platform directory API.

Estimate forms are UI-complete. Submit shows a finished success state without requiring the platform leads API. Operators may later replace the form with a GHL embed the same way as `/book`.

### 5.1 Units

| Unit | Does | Consumers | Depends on |
|---|---|---|---|
| Red Clay pages/CSS | Painting marketing site | Prospects | `siteContent` dummy data, public demo API, cookie |
| Email gate (`/my-work`) | Bind session to contractor email | Homepage carousel, `/work` | Public list endpoint |
| Public demo API | List/get jobs + social assets by email | Red Clay | Contractor, Job, Media, GeneratedAsset |
| Auth register | Create company + owner contractor | Contractor app sign-in | Company, Contractor |
| Dummy content | Always-on portfolio if API empty | Red Clay | Local images under `public/` |

## 6. Site map

Nav: Home · Services · Work · Areas · About · Contact. Primary button: **Book an estimate** → `/book`. Phone always `tel:404-555-0148` (display `404-555-0148`).

| Path | Role |
|---|---|
| `/` | Hero, click-to-call, lead form, recent-work carousel, services, process, reviews, areas |
| `/services` | Four offers |
| `/services/exterior-painting` | Primary |
| `/services/trim-and-siding` | Fascia, soffit, siding, exterior trim |
| `/services/decks-and-fences` | Stain/paint |
| `/services/interior-painting` | Second line, clearly secondary |
| `/service-area`, `/service-area/{city}`, `/service-area/{city}/{service}` | Atlanta, Decatur, Marietta, Roswell, Sandy Springs, Brookhaven |
| `/work` | Gallery hub (replaces `/portfolio` routes; old portfolio paths redirect) |
| `/work/{slug}` | Dummy or live project page |
| `/reviews` | On-site reviews |
| `/about` | Crew, licensed/insured, local |
| `/faq` | Real questions |
| `/book` | Empty GHL calendar mount + phone |
| `/contact` | Form + phone + areas |
| `/privacy`, `/terms` | Real legal pages |
| `/my-work` | Email gate. Footer link only, not main nav |

Footer lists all four services, all cities, phone, Book, Privacy, Terms, See your project.

## 7. Visual system

Premium Craft structure. One accent: Georgia clay.

| Token | Hex |
|---|---|
| Charcoal | `#2B2825` |
| Clay | `#B54A2A` |
| Clay hover | `#8B3A20` |
| Page | `#F7F4EE` |
| Card | `#FFFFFF` |
| Footer/dark | `#1C1A18` |
| Text | `#211F1D` |
| Text muted | `#6B655C` |
| Border | `#E3DCCF` |

- Headlines: Fraunces (or Lora), H1 68→42px, H2 44→32px, weight 500–600, serif.  
- Body: Inter, 17→16px.  
- Small-caps labels: 13px, letter-spacing 0.1em, clay.  
- One solid clay CTA per viewport. Phone color is clay.  
- Before/after side by side, never a slider.  
- Section padding ≥ 96px desktop. Tap targets ≥ 44px.

Forbidden: stock thumbs-up painters, multi-color gradients, countdown/urgency, chatbot popup, “demo”/JobbPulse on public chrome, more than one primary clay button in a viewport.

## 8. Components

**Global:** header, trust bar (Licensed & insured · Written estimates · Metro Atlanta · On-site reviews), CTA band (“Ready for a quote?” + phone + Book), footer.

**Homepage carousel:** dummy jobs from `siteContent`; if the demo cookie is set and the API returns jobs, those cards are **prepended**. Click → `/work/{slug}`.

**`/my-work`:** email + Continue. Cookie `red_clay_demo_email` (path `/`, 7-day max-age, not httpOnly so the SPA can read it; this is demo-grade). Unknown email or no eligible jobs: dummy portfolio remains; copy: “No published project for that email yet. Finish the job in the contractor app, then try again.” Clear-email control on the same page.

**`/work/{slug}`:**  
1. Resolve live project from public GET if slug is not a dummy slug.  
2. Else dummy from `siteContent`.  
3. Layout: before | after, public write-up, estimate CTA, **Shared from this job** (Facebook, Instagram, Google Business — image + title/body). Dummy jobs include mock social copy so the layout is never empty.

**`/book`:** heading, phone, `<div id="ghl-calendar" data-ghl-embed></div>` with short operator comment in source. No fake calendar UI.

**Forms:** name, phone, email, service, message. Client-side validation (name + phone or email). Success state without a required backend.

## 9. Kai criteria mapping

| Criterion | Where |
|---|---|
| Click-to-call | Header, hero, CTA band, footer, contact, book |
| Homepage lead capture | Hero form |
| Not a one-pager | Site map §6 |
| Service pages | Four detail routes |
| Service areas | Existing silo, painting copy |
| On-site reviews | `/reviews` + homepage quotes |
| Booking calendar | `/book` GHL mount |
| Privacy / terms | Real pages |
| Recent projects carousel → dedicated page | Homepage + `/work/{slug}` (dummy and live) |

## 10. Contractor-app: create account

Today `POST /auth/verify` returns 404 if no contractor exists. Add:

`POST /api/v1/auth/register`

Body (JSON):

```json
{
  "name": "Alex Rivera",
  "email": "alex@example.com",
  "companyName": "Rivera Painting",
  "phone": "4045550100"
}
```

`phone` is optional. Email is required, stored lowercased. `companyName` required.

Behavior:

- If a contractor already exists with that email: **409** `{ "error": { "code": "email_taken", "message": "An account with that email already exists. Sign in instead." } }`.
- Else create `Company` (name from `companyName`, slug unique from slugified name + short suffix if collision) and `Contractor` (role owner, status active).
- Return **201** with `{ "email": "...", "companyId": "...", "contractorId": "..." }`. Client then calls existing `POST /auth/challenge` and `POST /auth/verify`.

Frontend: sign-in page gains **Create account** (name, email, company, optional phone) then continues into the OTP step.

This is the only contractor-app auth change in this spec.

## 11. Contractor-app: public demo API

Unauthenticated. Demo-grade. Rate-limit by IP (same order as auth challenge).

CORS must include Red Clay origins: `http://localhost:3002` and `http://127.0.0.1:3002`.

### 11.1 Eligible jobs

A job is eligible when:

- `deleted_at` is null
- `public_status` is one of: `ready_for_approval`, `publishing`, `published`, `publish_issue`
- Latest content package has generated assets for `facebook`, `instagram`, and `google_business` (missing one still returns the job; that card is omitted)

Private fields never appear: `job.name`, `internal_note`, `assigned_crew_member`, storage keys.

### 11.2 List

`GET /api/v1/public/demo/projects?email=`

- Email missing or invalid: **422**.
- No contractor for that email: **200** `{ "items": [] }` (do not 404; avoids email enumeration messaging on the site — the site already says “no project yet”).
- Multiple contractors with the same email: use the most recently created contractor’s company.

Response item:

```json
{
  "slug": "exterior-painting-in-decatur-a1b2",
  "publicTitle": "Exterior painting in Decatur",
  "publicSummary": "Two-story colonial, full body and trim…",
  "serviceType": "Exterior painting",
  "city": "Decatur",
  "publishedAt": "2026-08-23T15:00:00Z",
  "primaryImageUrl": "https://…",
  "hasBefore": true,
  "hasAfter": true
}
```

`publicTitle` / `publicSummary`: from `conversion_site` asset title/body when present; else `"{service_type} in {city}"` and the package description/body.

`slug`: stable, kebab-case from public title plus the first 4 hex chars of job id so collisions cannot happen. Stored nowhere extra — computed as `slugify(publicTitle) + "-" + job_id.hex[:4]`. GET by slug finds the job by matching that rule for jobs in the company.

### 11.3 Detail

`GET /api/v1/public/demo/projects/{slug}?email=`

Email required (same as list) so a slug from another company cannot be fetched without that email.

**200** body:

```json
{
  "slug": "exterior-painting-in-decatur-a1b2",
  "publicTitle": "Exterior painting in Decatur",
  "publicSummary": "…",
  "serviceType": "Exterior painting",
  "city": "Decatur",
  "publishedAt": "2026-08-23T15:00:00Z",
  "media": [
    { "stageLabel": "before", "url": "https://…" },
    { "stageLabel": "after", "url": "https://…" }
  ],
  "socialPosts": [
    { "destination": "facebook", "title": "…", "body": "…", "imageUrl": "https://…" },
    { "destination": "instagram", "title": "…", "body": "…", "imageUrl": "https://…" },
    { "destination": "google_business", "title": "…", "body": "…", "imageUrl": "https://…" }
  ]
}
```

`imageUrl` for social cards: after-photo signed URL (same as primary). `title`/`body` from the active generated-asset version.

**404** if slug does not match an eligible job for that email.

Media URLs are the existing short-lived signed GET URLs from object storage.

## 12. Red Clay data flow

- `useDemoProjects()`: if cookie email set, fetch list; on network error, keep dummy only (no error banner on the homepage).
- Carousel: `[...liveItems, ...dummyJobs]` with live first. Deduplicate by slug.
- `/work/{slug}`: try live detail if cookie present; on 404 fall back to dummy; if neither, “Project not found” + link to `/work`.
- Dummy slugs are reserved prefixes such as `demo-` so they never collide with live slugs.

Fallback dummy jobs: at least four painting projects (exterior Atlanta, interior Decatur, deck Marietta, trim Roswell) with local JPEGs under `public/work/`. Replace cabinet photos.

## 13. Error handling

| Case | Behavior |
|---|---|
| Contractor API down | Dummy site only. `/my-work` submit shows “Could not reach the project service. Try again.” |
| Email not found / empty list | 200 empty; site copy in §8 |
| Register email taken | 409; UI: sign in instead |
| Invalid register payload | 422 field errors |
| Live project media URL expired | Card still renders; broken image alt text; page remains usable |
| Job without all three social assets | Show the cards that exist |
| `/book` with no GHL embed | Page still has phone + empty mount, not a dead end |

## 14. Testing

**Contractor app API**

- Register creates company + contractor; second register same email → 409.
- Register then challenge + verify (dev code) yields a session.
- Public list without email → 422; unknown email → 200 empty list.
- After a job has FB/IG/GBP assets and eligible status, list returns it; detail includes `socialPosts`.
- Private `job.name` does not appear in public JSON.
- Ineligible (draft / deleted) jobs omitted.

**Red Clay**

- Unauthenticated homepage has dummy carousel, `tel:` links, hero form, no “demo” string in rendered chrome.
- Routes in §6 return 200 (or redirect from `/portfolio` → `/work`).
- `/privacy` and `/terms` are not stubs.
- `/book` contains `#ghl-calendar`.
- Cookie set → live cards prepend when API mocked with a job.

Browser check after implementation: homepage desktop + mobile, service page, work hub, dummy project page (social cards), `/my-work`, `/book`, `/privacy`.

## 15. Copy and brand facts

- Company: **Red Clay**
- Trade: Exterior painting first; interior as a second line
- Area: Metro Atlanta (six cities in §6)
- Phone: `404-555-0148` / `+14045550148`
- Email: `hello@redclaypainting.com`
- Tone: Direct, practical, warm, not cute; neighbor who happens to be a professional. No “passionate about painting since…”

## 16. Implementation order (for the later plan)

1. Contractor-app register + public demo API + tests.  
2. Red Clay visual/content rebuild (dummy only, Kai pages).  
3. Email gate + live carousel/project page.  
4. Browser verification of the walkthrough.

Do not start (2) until (1) has a green test for empty-list and one eligible job, or Red Clay cannot be verified end-to-end.
