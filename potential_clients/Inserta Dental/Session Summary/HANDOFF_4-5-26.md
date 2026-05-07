# HANDOFF — DBD GAds Rebuild Build State

**Date:** 4 May 2026
**Session:** PM 4 (current — about to compact)
**Purpose:** Full state of the DBD GAds rebuild so the post-compact session can continue without losing context.

---

## What just happened (today)

Full strategic rebuild of DBD's Google Ads campaign kicked off based on Giulio's brief: **one big Search campaign (Dental Implants Intent), exact-match-heavy, focus on single/double arch + closely-related high-ticket procedures, gradual phase-out of old phrase/exact ad groups**.

Two parents shipped end-to-end today (LPs + ad groups + RSAs live in production):

| Parent | Sub-groups built | Keywords | RSAs | Status |
|---|---:|---:|---:|---|
| **All on 4** | 4 (CORE / COST / LOCATION / INFO) | 47 | 12 (RSAs all pushed to Excellent) | LIVE |
| **Full Mouth Implants** | 3 (CORE / COST / LOCATION) | 54 | 9 (RSAs being pushed to Excellent) | LIVE |

8 LPs shipped to dentalbydesign.co.uk. 4 old PM-3 ad groups paused (or being paused — All on 4 done, Full Mouth in progress).

---

## Where to pick up

**NEXT PARENT TO BUILD: General Implants** (Day 2's biggest universe — 8 planned sub-groups: CORE / COST / LOCATION / FINANCE / COMPARISON / INFO / BRAND / NHS).

Apply the same workflow (below). Expect 4-7 sub-groups to survive the filter — General Implants has 5,000+ historical variants so should keep most.

After General Implants, remaining parents in build order (per `_PLAN_subgroups.md`):
- New Teeth (6 sub-groups planned)
- Screwless Implants (3)
- Vivo Bridge (1, branded)
- Permanent Teeth 48h (2)
- Same Day Teeth (3)
- Smile in a Day (3)
- All on 6 (4)
- Single Arch (1, no historical, build because Chris insisted)
- Double Arch (1, same)
- Full Arch (2)
- Upper Jaw (2)
- Lower Jaw (1)
- Implants for Elderly (4)
- Hybrid Bridge (2)
- Implant Clinic (3)
- Bone Graft (2)
- Failed Implants (1)
- Nobel Biocare (1)
- Fixed Teeth (1)
- Comparison Shoppers (4) — these are competitor-brand searches that convert at £243 CPB
- **PENDING Tommaso/Giulio approvals (Day 5):** Implant Denture / Zygomatic / Straumann / NHS Implants

---

## Locked rules / conventions

### Ad group naming
**`[ex] {Parent} - {SUBGROUP}`** — single dash, `[ex]` prefix groups them visually in Ads Editor + identifies as exact-match.
- Examples: `[ex] All on 4 - CORE`, `[ex] Full Mouth - LOCATION`, `[ex] General Implants - COST`

### Filter rules per sub-group keywords
- **Min 30 impressions** (10 for low-vol sub-groups: INFO, COMPARISON, BRAND, NHS)
- **Min 1 click**
- **Max 6 words per keyword** (longer triggers Low Search Volume)
- **Sort: clicks desc, then impressions desc**
- **Cap 25 keywords per ad group** — no force-fill (if 8 qualify, ship 8)
- **Drop self-blocking tokens**: invisalign, clear aligner/aligners, braces, ortho/orthodontic, veneer/s, whitening, composite bonding, flipper/s, dentures/denture, crowns/crown, fillings/filling, root canal, failed, problems, horror stories, gone wrong, dentaprime
- **Drop tourism / foreign**: lithuania, latvia, estonia, hungary, poland, etc.
- **Drop COMPARISON sub-groups** if 0 keywords qualify (LP can stay live for SEO, just no paid traffic)
- **Roll FINANCE keyword(s) into COST** if FINANCE has only 1-2 qualifiers

### CSV character limits
- **Headlines: ≤30 chars, target 12-13 of 15 with parent keyword anchor** for high Quality Score
- **Descriptions: 75-87 chars** (Google hard limit 90, our soft target 75-87 — validator hard-enforces)
- **Path 1 + Path 2: ≤15 chars each**, unique combo per RSA in same ad group

### Banned phrases (any RSA copy)
- `£25 booking deposit` / `£25 deposit` (per Chris — not a positive)
- `60% off` / `99.12%` / `Top 10 Europe` / `Best Clinic 2024` (per Giulio — only `2024 Implant Clinic Finalist` allowed; `99.12%` allowed in disclaimer only)

### CSV encoding
**UTF-8 with BOM (`utf-8-sig` in Python).** Without BOM, Ads Editor reads as Windows-1252 → `£` becomes `Â£`, em-dash becomes `â€"`. **All `csv.writer` opens use `encoding="utf-8-sig"`.**

### Negatives
**Deferred to buffer day** per Chris's call. Existing shared lists provide baseline protection:
- `Off Not Adv "ph"` (PM 3 maintained, applies to DII campaign)
- `Loc 1 WRD "ph"` (Chris added 19 country/abroad-seeker tokens today)
- `All Foreign Language "ph"` (Chris created today, 11 tokens — Polish/Czech/Hungarian)
- `All Foreign Language [ex]` (created today, empty for now)

**Cross-sub-group negs (cost / london / vs etc.) ALSO deferred** — Chris said don't predict the problem, see if it actually happens in real search terms data. Buffer day = audit search terms across all live ad groups, then add negs at appropriate level.

### LP URL pattern
**`https://dentalbydesign.co.uk/google/{slug}`** with `dental-implants` in slug for keyword density:
- CORE: `/google/{base}-dental-implants` (e.g. `/google/all-on-4-dental-implants`)
- COST: `/google/{base}-dental-implants-cost`
- LOCATION: `/google/{base}-dental-implants-london` OR `-near-me` (use whichever is highest-volume keyword)
- COMPARISON: `/google/{base}-dental-implants-vs-{other}`
- INFO: `/google/{base}-dental-implants-explained`
- NHS: `/google/{base}-dental-implants-nhs`
- BRAND: `/google/{brand-name}-dental-implants`

Coexist alongside PM 3's old LPs (e.g. `/google/all-on-4-implants` stays live until old ad group pauses).

---

## Build workflow (per parent)

### 1. Sub-group analysis
```
.venv/Scripts/python.exe potential_clients/Inserta\ Dental/data/search_terms_audit_2026/dump_parent.py {parent_name}
```
Outputs `{parent_name}_keywords.json` + console summary showing qualified keywords per sub-group. Use this to decide which sub-groups to build.

### 2. Build LPs (one at a time, ngrok preview, push to main)
**DBD repo:** `C:\Users\User\Desktop\dentalbydesign-repo`
**Dev server:** `bun dev` (assumes 4321 or starts on 4322 if 4321 in use). Per CLAUDE.md don't auto-start unless port not in use.
**Ngrok:** `/c/ngrok/ngrok http 4321 --host-header=rewrite` (already running in background — URL: `https://intervalvular-rainily-shawna.ngrok-free.dev`)
**LP file path:** `apps/web/src/pages/google/{slug}.astro`
**Template to clone:** Use existing similar LP (e.g. `all-on-4-dental-implants.astro`) — same component structure
**Required components:** Hero, Quiz, Featured, RecapSection, BeforeAfterMinimal, FreeConsultationVideo, LifetimeWarranty, Comparison, SuccessRate, PriceChart, PatientTestimonials, Doctors, Spacer, Safety, DelayCosts, custom FAQ accordion, custom 0% finance Quiz section, VideoCta, Reviews, disclaimer
**Custom per LP:** SEO (title/description/keywords), Hero (title + description), 7 FAQs (tailored to sub-group intent), FreeConsultationVideo subtitle + consultationIncludes, VideoCta title/description/ctaText, Reviews title/subtitle, custom inline sections if needed (e.g. comparison table for COMPARISON LP, step-by-step for INFO LP)

**Per-LP QA:**
- `noIndex: true` always (paid LP, prevents duplicate-content SEO issue)
- All 7 FAQs render (`<details>` count = 7)
- No template errors / unresolved placeholders
- Title + meta description unique per LP
- Reasonable keyword coverage on rendered page (curl + grep -c)
- No banned phrases in copy
- No keyword stuffing / synonym dumps (per memory `feedback_token_economy.md`)

**Ngrok preview workflow:**
1. Build LP → `curl -sI http://localhost:4321/google/{slug}` returns 200
2. Share `https://intervalvular-rainily-shawna.ngrok-free.dev/google/{slug}` with Chris for visual review
3. Iterate on copy if Chris flags
4. After Chris approves: `bun run build` (catch Cloudflare-breaking errors), then commit + push

**Commit format (PM 3 convention):**
```
Add LP: {Parent} — {Sub-group} → /google/{slug}

{Brief description of intent + key copy decisions}

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
Push to `main` → Cloudflare auto-deploys (~3-5 min) → verify live with curl.

### 3. Generate Ads Editor CSVs
**Helper script (copy + customise per parent):** `potential_clients/Inserta Dental/data/search_terms_audit_2026/generate_full_mouth_uploads.py` is the latest template. Per parent:
1. Copy script → `generate_{parent}_uploads.py`
2. Update SUBGROUPS list (sub-group names + LP URLs)
3. Update FILTER_RULES per sub-group (standard 30/1/6 unless small bucket needs relax)
4. Replace RSAS dict (3 RSAs per ad group, themes per sub-group: procedure / speed / trust for CORE; cost-clarity / finance / value for COST; London / Hammersmith / UK-trust for LOCATION; etc.)
5. Run → outputs to `Campaigns/{Parent}/`:
   - `01_core.md` ... markdown specs (human-readable)
   - `_csv_ad_groups.csv`
   - `_csv_keywords.csv`
   - `_csv_rsas.csv`
   - (skip `_csv_negatives.csv` — deferred)

**Validation (script-enforced):**
- Headlines ≤30, descriptions 75-87
- Path1/Path2 ≤15
- Each RSA in same ad group has unique path1+path2 combo
- No banned phrases anywhere
- No self-blocking keyword tokens
- No cross-group keyword duplicates
- ≥1 keyword per ad group (else flag ZERO KEYWORDS)

### 4. Chris uploads to Ads Editor + posts to GAds
Workflow:
1. Import `_csv_ad_groups.csv` first
2. Import `_csv_keywords.csv` second
3. Import `_csv_rsas.csv` third
4. Post all
5. Pause the equivalent old PM-3 ad groups in same campaign

### 5. Iterate ads to Excellent (post-launch QA)
After 24-48h, Chris pulls **Ad report** CSV showing each RSA's strength.

For each RSA scored Poor / Average / Good:
- I generate **15 NEW headlines + 4 NEW descriptions per RSA** (no duplicates with current 15+4)
- Show **current side-by-side with new candidates** (per project rule)
- Chris swaps one at a time until score = Excellent
- Auto-advance to next ad group when current is done (don't ask permission)

Skip RSAs already scored Excellent.

---

## Key files / scripts

### Audit DB
**`potential_clients/Inserta Dental/data/search_terms_audit_2026/audit.duckdb`** — 175,241 search-term rows from Jan 2025 - May 2026 (includes 16 months of historical data + booking-conversion segmentation).

### Helper scripts
- **`dump_parent.py {parent_name}`** — generic parent dumper: pulls keywords from DB, sub-classifies, applies filter, reports survivors. Run first per new parent.
- **`generate_full_mouth_uploads.py`** — latest CSV generator template. Copy + customise per parent.
- **`shrink_for_inspection.py`** in `potential_clients/Inserta Dental/Screenshots/` — shrinks screenshots to ≤1500px before Read.

### Output folders
- **`Campaigns/{Parent}/`** — markdown specs + Ads Editor CSVs
- **`Campaigns/_LP_URLS.md`** — master 70-LP URL plan
- **`Campaigns/_PLAN_subgroups.md`** + **`Campaigns/_PLAN_subgroup_data.csv`** — full sub-group breakdown for 26 parents
- **`Campaigns/_TOURISM_NEGS.md`** — 55 phrase-match neg tokens (already added to shared lists by Chris)
- **`Campaigns/_MORNING_REVIEW.md`** — earlier strategy doc (mostly superseded)

### DBD website repo
**`C:\Users\User\Desktop\dentalbydesign-repo`** (separate from gads-data-layer)
- `apps/web/src/pages/google/*.astro` — paid LP pages
- `bun dev` for dev server (port 4321 by convention)
- `bun run build` for production build (run before push to catch Cloudflare errors)
- `bun deploy` and `bun build` — DO NOT auto-run per CLAUDE.md
- Push to `main` → Cloudflare Pages auto-deploys ~3-5 min

### Ngrok
**`/c/ngrok/ngrok`** — for sharing dev server with Chris during LP review.
Active tunnel URL: `https://intervalvular-rainily-shawna.ngrok-free.dev` (still up at compact time per the bx17hlhnc background process).

---

## What's currently live in dbd-google-ads

**Campaign:** `Dental Implants Intent`

**Ad groups (live, fully built):**
- `[ex] All on 4 - CORE` — 24 keywords, 3 RSAs Excellent
- `[ex] All on 4 - COST` — 7 keywords, 3 RSAs (improved to Excellent today)
- `[ex] All on 4 - LOCATION` — 10 keywords, 3 RSAs (improved to Excellent today)
- `[ex] All on 4 - INFO` — 6 keywords, 3 RSAs (improved to Excellent today)
- `[ex] Full Mouth - CORE` — 20 keywords, 3 RSAs (3 Good, being pushed to Excellent today)
- `[ex] Full Mouth - COST` — 19 keywords, 3 RSAs (1 Poor + 2 Good, being pushed to Excellent today)
- `[ex] Full Mouth - LOCATION` — 14 keywords, 3 RSAs (1 Poor + 1 Average + 1 Good, being pushed to Excellent today)

**Old PM-3 ad groups status:**
- `*All on 4 Implants` — paused after new All on 4 ad groups went live + verified
- `*Full Mouth Implants`, `*Full Mouth Implants Cost`, `*Full Mouth Implants Near Me` — pause in progress

---

## What's currently live on dentalbydesign.co.uk

**8 NEW LPs (Chris-approved, deployed via Cloudflare):**

| LP | URL |
|---|---|
| All on 4 — CORE | `/google/all-on-4-dental-implants` |
| All on 4 — COST | `/google/all-on-4-dental-implants-cost` |
| All on 4 — LOCATION | `/google/all-on-4-dental-implants-london` |
| All on 4 — COMPARISON | `/google/all-on-4-dental-implants-vs-all-on-6` (LP live but no paid traffic — sub-group dropped per filter) |
| All on 4 — INFO | `/google/all-on-4-dental-implants-explained` |
| Full Mouth — CORE | `/google/full-mouth-dental-implants` |
| Full Mouth — COST | `/google/full-mouth-dental-implants-cost` |
| Full Mouth — LOCATION | `/google/full-mouth-dental-implants-near-me` |

Plus PM 3's existing 25-30 LPs at `/google/{slug}` (those stay live until their old ad groups are paused).

---

## Key decisions Chris locked today

1. **Defer all negatives to buffer day** — universal, defensive, AND cross-sub-group. Real data > theoretical predictions.
2. **No pinning headlines** — never seems to help.
3. **75-87 char descriptions** — hard-enforce in validator.
4. **`[ex] {Parent} - {SUBGROUP}` ad group naming** — single dash, `[ex]` prefix.
5. **UTF-8 BOM on all CSVs** — fixes £/em-dash encoding.
6. **Drop self-blocking keyword tokens** at filter time (lithuania, denture, etc.).
7. **Tourism keywords** added to existing `Loc 1 WRD "ph"` shared list (countries + abroad-seeker phrases) + new `All Foreign Language "ph"` for foreign-language tokens.
8. **Drop sub-groups with 0 qualifying keywords** (e.g. All on 4 COMPARISON dropped).
9. **One LP at a time, ngrok preview, then push** — never batch-build LPs without checkpoints.
10. **One ad group at a time for ad strength iteration** — auto-advance only between ad groups, never asking permission.
11. **Skip Excellent-strength RSAs** — only generate replacements for Poor/Average/Good.

---

## Pending Giulio/Tommaso decisions (Day 5 work)

- **NHS Implants** ad group + LP — **30 historical bookings at £148 CPB** (best in dataset). Needs sign-off before building.
- **Implant Denture / Overdenture** ad group — does DBD offer implant-supported dentures? Affects this whole parent build + ~12 negs.
- **Zygomatic / Pterygoid Implants** ad group — does DBD offer? Severe-bone-loss arch cases.
- **Straumann Implants** ad group — does DBD use Straumann (Nobel Biocare confirmed; Straumann TBC).

---

## Action items as soon as session resumes post-compact

1. **Confirm All on 4 + Full Mouth ads all hit Excellent** (Chris was iterating during this session).
2. **Run `dump_parent.py general_implants`** to see sub-group survivors. Likely 4-7 will qualify (CORE / COST / LOCATION / FINANCE / INFO are biggest).
3. **Build General Implants LPs one at a time** — clone from existing template (e.g. `all-on-4-dental-implants.astro`), adapt copy.
4. **Generate Ads Editor CSVs** using `generate_full_mouth_uploads.py` as template.
5. **Chris uploads + iterates ads to Excellent** (then auto-advance to next parent).

---

## Safety notes

- **Never archive existing LPs or ad groups** — coexist alongside new ones until Chris explicitly pauses.
- **Always validate descriptions 75-87 chars + headlines ≤30** before generating CSVs (validator does this — don't bypass).
- **Always check banned phrases** before shipping copy (`£25 deposit`, `60% off`, `99.12%` outside disclaimer, `Top 10 Europe`, `Best Clinic 2024`).
- **Never run `bun build` or `bun deploy` automatically** per DBD CLAUDE.md — Chris handles deploy steps manually OR via approved push-to-main flow.
- **CSV files always saved with `encoding="utf-8-sig"`** — UTF-8 BOM is mandatory.
- **Cross-parent contamination check** — when comparing existing ad groups vs new structure, check against ALL new ad groups (not just the corresponding parent), since old structure mixed parents.
