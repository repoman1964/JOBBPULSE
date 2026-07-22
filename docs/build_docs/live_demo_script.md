# JobPulse live demo — click by click

**Audience:** investor, pilot contractor, or yourself  
**Time:** ~12–15 minutes  
**Story:** *Finish a paint job → talk into the phone → approve AI drafts → one Publish → live on your directory + social.*

Use a **phone-width browser** (or Chrome DevTools → device toolbar) for the contractor app.

---

## 0. Setup (before the room)

Terminals:

```bash
cd "/path/to/JOBPULSE"
make infra-up
make api-migrate
make api-dev          # :8000
make mobile-dev       # :3000
make directory-dev    # :3001
```

Optional: open http://localhost:8000/docs in a second tab if you want to flash the API later.

**Demo data to invent aloud**

- Company: *Oak Street Painting*
- Job private name: *Johnson / Oak St* (say: “only we see this”)
- City will auto-detect or use whatever geo gives you

Have **1–2 photos** ready (any phone pics of a wall, deck, fence — “before/after” is fine even if imperfect). Mic permission OK.

---

## Act 1 — Sign up & company (2 min)

### 1. Open contractor app

- Go to **http://localhost:3000**
- If you land on login: click **Register** / go to **http://localhost:3000/register**

### 2. Create account

Fill:

| Field | Demo value |
|---|---|
| Your name | *Alex Rivera* |
| Company name | *Oak Street Painting* |
| Trade | *Painting* |
| Email | any unique email |
| Password | 8+ chars |

Click **Create account**

→ Lands on **Onboarding · step 1 of 3**

### 3. Onboarding (keep it snappy)

**Step 1 — Company basics**

- Phone: optional
- Tone: leave *Friendly and local*
- Click **Continue**

**Step 2 — Services**

- Service name: *Exterior painting*
- Click **Continue**  
  *(or **Skip for now** if short on time)*

**Step 3 — Service area**

- City: *Austin, TX*
- Click **Finish setup**

→ **Jobs home** (“No jobs yet” or empty list)

**Talk track:** “Under a minute. Company is multi-user later; owner can approve and publish.”

---

## Act 2 — Capture the job (4 min)

### 4. Create job

- Bottom nav: **Capture**, or **Create Job**, or big **+**
- Screen: **Create Job**

**Job name:** type `Johnson / Oak St`  
Point at the privacy note: *“Only you see this name… never shared in marketing.”*

Optional: Service type → *Exterior painting*

Click **Skip befores — go to after photos**  
*(Faster demo path. Or **Create & add before photos** if you want both.)*

→ Job detail opens

### 5. After photos (required)

- Stage should be **After (required)**
- Click **Add after photos (required)** / capture CTA
- Pick **1 photo** from the device (camera or library)
- Wait for upload success

**Talk track:** “Before is optional if they forget. After is the product gate.”

### 6. Voice summary (required)

Scroll to **Voice** card (`#voice`).

1. Click **Start recording** (or equivalent start CTA)
2. Speak ~10–15 seconds, e.g.  
   *“We painted the Johnson house exterior. Prepped and scraped the peeling side. Two coats of weatherproof white. Homeowner loves how clean the trim looks. Took about a day and a half.”*
3. **Stop**
4. Click **Upload & transcribe**
5. Wait for mock transcript (usually quick)
6. Optionally **edit** a word → **Save** transcript

**Talk track:** “Field reality: talk, don’t type. Mock STT today; real Whisper/Deepgram is a config swap.”

---

## Act 3 — AI drafts & human gate (3 min)

### 7. Generate

When next action is generate, click **Generate content** (primary CTA).

Wait for **Generating…** → job moves to **Needs review** / awaiting review.

### 8. Review workspace

You’ll see draft variants, typically:

- Primary social
- Short caption
- Before/after
- Directory listing

**Do one edit** (proves human control):

1. Open / focus **Primary social** (or any social piece)
2. Tweak a sentence in the body
3. **Save edit**

**Optional show reject path** (if time):

- **Reject** one piece → job can go revision
- Or **Regenerate drafts** with a short instruction (“more casual, mention curb appeal”)

**Skip reject for a clean happy path.**

### 9. Approve

Click **Approve all & mark ready**

→ Status becomes **Approved**  
Copy should say content is approved / ready to publish.

**Talk track:** “Hard rule: nothing ships without contractor approval. This is the product, not the model.”

---

## Act 4 — Connect social (1 min)

### 10. Account → mock social

- Bottom nav **Account** (or avatar)
- **Social accounts** section
- Click **Connect Facebook** (and/or **Connect Instagram**)
- Confirm status shows **active**

**Talk track:** “Mock provider. Real poster is `PUBLISHING_PROVIDER` — same button later.”

You should also see **Notifications** (generation ready, approved, etc.). Point at the badge/list briefly.

---

## Act 5 — One Publish (2 min)

### 11. Back to the job

- **Jobs** → open *Johnson / Oak St*

### 12. Publish panel

When approved:

- Check **JobPulse directory** (on)
- Check the **Facebook** (and/or Instagram) connection if shown
- Click the single primary button: **Publish**

Wait for **Publishing…** → success like *Published — directory + social.*

### 13. Open live page

- Click **Open live page** (or the public URL)

→ Public directory project page on **:3001**

**Show on purpose:**

- Public title/summary from **approved content**, not “Johnson / Oak St”
- Photos / service / city-level location
- **Private job name is gone**

Optional: open http://localhost:3001 home and browse projects/contractors.

**Talk track:** “Owned distribution + social in one action. Directory is first-party SEO surface; social is replaceable.”

---

## Act 6 — Pilot controls (optional, 2 min)

### 14. Unpublish (contractor control)

Back on job detail:

- **Unpublish from directory**
- Confirm
- Public URL should 404 / not show as live

### 15. Re-publish (optional)

- Approve state still OK → **Publish** again (idempotent-ish path)

### 16. Account notifications

- Account → **Notifications**
- Tap **Open job** on one item
- **Mark all read**

### 17. API flash (nerds only)

- http://localhost:8000/docs
- Or `GET /api/v1/status` — providers mock, version, etc.
- Mention audit: managers get `GET /api/v1/audit-events` after publish

---

## Closing line (15 seconds)

> “Contractor finishes the job, talks once, reviews once, hits **Publish** once. Private job name never leaves the truck app. Directory is ours; social is a plug. That’s the MVP loop — Phases 1–8.”

---

## If something breaks

| Symptom | Fix |
|---|---|
| Can’t register / 500 | `make infra-up`, `make api-migrate`, API running on :8000 |
| Mic blocked | Browser site settings → allow mic for localhost:3000 |
| Generate disabled | Need ≥1 after photo + usable transcript |
| Approve blocked | Approve at least one social variant + directory listing (Approve all does this) |
| Publish empty | Connect a social account **or** leave directory checked |
| No public page | Publish with directory on; use **Open live page** |
| CORS / blank API | `api/.env` CORS includes `http://localhost:3000` and `3001` |

---

## Ultra-short path (5 min)

If time is tight:

1. Register → Finish setup (skip services if needed)
2. Create job → **Skip befores**
3. 1 after photo → record voice → upload
4. Generate → **Approve all & mark ready**
5. Account → Connect Facebook
6. Job → **Publish** → **Open live page**

---

## Privacy beats to hit (say out loud)

1. Job name is **private** on create
2. Never appears on public project page
3. Approval is **always** human
4. **One** Publish button (don’t split destinations as primary CTAs)
