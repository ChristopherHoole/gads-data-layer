# Handoff → MC - Project Manager 3

**From:** PM session 22 April 2026 (both AM + PM sessions)
**To:** Next PM session picking up 23 April 2026 onward
**User:** Christopher Hoole (`chrishoole101@gmail.com`)
**Working directory:** `C:\Users\User\Desktop\gads-data-layer`

This doc is your cold-start briefing. Read it all before the user types anything. The companion Prompt (end of doc) is what the user will paste to open the new session.

---

## 1. Who you are and how you work with Chris

You are the **PM** session — Chris's planning, drafting, and decision-making partner. A separate **ACT Build 2** session does all Flask/Python/JS implementation work for the ACT app. You produce briefs, Chris pastes them to ACT Build 2. Do NOT write ACT code yourself unless ACT Build 2 is unavailable (API overload, etc.) and the change is small and urgent.

Chris is the sole decision-maker. He wants:
- **Short, concise replies.** No waffle. Bullet lists preferred over prose paragraphs. He's not a great reader and will call out verbose answers.
- **Pure colours only.** Never off-white, off-black, grey body text. Pure black (#000000), pure white (#FFFFFF), or a real colour.
- **Verify before claiming.** He has called out at least two wrong claims I made today by asking "are you sure?" — validate claims from CSVs, code, or logs before stating them as fact.
- **Never push to remote git unless asked.** Do push to origin/main after Build 2 merges (he asked for that on 22 April).
- **Read everything in the CLAUDE.md / memory folder** at session start.

He will NOT read git. Git is always your job.

---

## 2. What's in memory already (read first)

Before doing anything, read everything in:
`C:\Users\User\.claude\projects\C--Users-User-Desktop-gads-data-layer\memory\MEMORY.md` and its referenced files.

Key things memory already tells you:
- Project = ADS Control Tower (ACT) — Flask app + DuckDB warehouse
- Two paying clients: Objection Experts (signed 02/04), Dental by Design (signed 14/04)
- ACT v2 build status, file paths, engine pipeline (Pass 1/2/3 for negatives)
- DBD data ingested since Oct 2025, OE ingested earlier
- Nightly scheduler runs via Windows Task Scheduler (user set up)
- Standard workflow: PM brief → Build 2 implements → Chris tests → PM iterates

---

## 3. Client context — Dental by Design (active focus)

**Who:** Dental by Design / Prodent Group (Tommaso + Giulio)
**Signed:** 14 April 2026
**Account:** Google Ads customer_id `5380281688`, MCC `152-796-4125`
**Spend:** ~£52k/mo (target £45k)
**Campaigns:** 3 active — Brand, Performance Max (main converter), Dental Implants Intent
**Scope:** Implants only (single + double arches), plus cosmetic dentistry added 21 Apr
**Funnel:** Lead → 13% → Booking → 35% → Treatment
**Free consultation + £25 booking deposit.**

**Site stack:**
- Domain: `dentalbydesign.co.uk` — Astro monorepo
- GitHub repo: `dentalbydesignuk/dentalbydesign` — cloned locally at `C:\Users\User\Desktop\dentalbydesign-repo` (read-only reference; Giulio owns deployment; NEVER push)
- Forms → **Dengro** CRM (awaiting login)
- Automation → **Zapier** account 23529592 (awaiting access)
- Analytics → **GA4** property 306680549, stream `G-TX9XP8RLZ7`
- Tag Manager → **GTM-KBPKCLKB**
- Call tracking → **CallTrackingMetrics** (awaiting login)
- Meta Pixel: `1229401092401938` (hardcoded in BaseLayout)
- Microsoft UET (via GTM, Bing not in scope yet)

---

## 4. What was shipped today (22 April 2026)

### AM session — ACT Build 2 completed N2 + N3

All commits on `main`, all pushed to `origin/main`. See git log for full history.

**N2 — Negatives sync repair (7 commits):**
- `40b88de` Engine fix: neg-list queries now filter by latest snapshot_date (both pass1 + pass3)
- `1b37ff2` 3 new API endpoints: refresh-snapshot, lists (for viewer), reclassify-now
- `a106f07` Negative Lists viewer UI — new tab in Client Config
- `1871002` Last-synced pill + Refresh + Reclassify buttons on Search Terms page
- `5b59824` Hotfix: column name `customer_id` → `google_ads_customer_id`
- `b233770` Hotfix: button label standardised to "Refresh Neg Lists from GAds"
- `7985e49` Hotfix: Neg Lists viewer client_id template typo

**N2-polish-1 — modal + in-place refresh:**
- `dd90a0f` ACT-styled confirm modal replaces browser `confirm()`; reclassify no longer full-page reloads

**N3 — Sticky Rejections + Mixed Intent + Row numbers (7 commits):**
- `b96058c` Migration: `act_v2_sticky_rejections` table
- `96a52a7` Engine Rule 0: sticky check short-circuits classification
- `0c5a8c2` API: bulk-update inserts sticky row on reject
- `672d8ff` Scheduler: `neg_sticky_expiry` phase
- `40a5ed3` Rejected Terms page + 3 API endpoints + sidebar link
- `8636680` Rule 5 mixed-intent downgrade (block → review when query has both adv + not-adv)
- `f4cc788` Row # column on Pass 1/2, Pass 3, Rejected Terms tables
- `e2065de` N3-hotfix-1: column widths after row# addition

**Total: 16 commits, all merged to main and pushed.**

### Search terms triage for 22/4
- **168 negatives pushed** to DBD's GAds (running 2-day total: 388)
- 1 sticky rejection recorded
- Pass 3: approved `composite` (1-word phrase), rejected `care`, `centre`, `clinic` (too broad)

### PM session — DBD Tracking Audit (opened, NOT complete)

Deliverables in `potential_clients/Inserta Dental/Tracking Audit/`:
- `DBD - Tracking Audit v2.pptx` — 16 slides (9 main + 7 appendix). **Needs visual polish — see §7.**
- `email_to_giulio_DRAFT.md` — 8 questions ready to send (Chris reviewing)
- `_resize.py` — image resize util for Opera screenshots (max 1500px)
- All supporting screenshots from GAds, GTM, GA4

---

## 5. In-flight work — tomorrow's priorities

### IMMEDIATE (do first thing)

**A. Polish the Tracking Audit deck to v3.** User flagged multiple issues with v2:
- Footer: match v8 exactly (ACT logo + `Christopher Hoole | christopherhoole.com | Confidential` + slide number)
- Colours: navy `#1A237E` (not `#1A2B4D`), red `#EA4335`, pure black `#000000`, pure white `#FFFFFF`. Light border `#E2E8F0`. Blue pill bg `#E8F0FE`.
- **NO GREYS ANYWHERE.** No `#5F6B7C` muted text, no `#1F2937`, nothing off-black/off-white. Pure black for body, pure colour for accents.
- Top-right corner: **Blue rounded box** (bg `#E8F0FE`, text dark) — not the thin grey pill I used. Reference v8 slide 2 for exact style.
- Subtitle beneath title: **pure black, not red, not bold**.
- Fonts: **Arial** for body, **Calibri** for headings. Minimum 11pt (no 9pt small text).
- Use **proper bullet points** where appropriate, not text blobs.
- **Real tables**: header row with actual fill, bordered cells, no awkward rectangle overlays over text. Use pptxgenjs table row options properly — I was faking headers with rectangles.

Reference deck to copy from exactly: `potential_clients/Inserta Dental/End-of-week reports/DentalByDesign.co.uk - Week 1 Report 13-17 April 2026-v8.pptx`

The build script is at `potential_clients/Inserta Dental/Tracking Audit/build_deck.js`. Edit + rerun with `node build_deck.js`.

**B. Send Giulio email.** Once deck is polished, Chris will review both + send. Email draft is in `email_to_giulio_DRAFT.md`.

**C. Morning search-terms triage for 23/4.** Standard daily review. See §6.

### AFTER IMMEDIATE — when Giulio replies / access arrives

- **Dengro login audit:** query leads to measure what % have `attribution.gclid` populated. This VALIDATES the first-touch-attribution theory from the deck.
- **Zapier account 23529592 audit:** check 3 zap run histories. The `u9v9qg1/` Booking zap has not fired since 5 Jan 2026 — find out why (likely mapping or auth issue).
- **CallTrackingMetrics audit:** DNI config, call routing, how calls become GAds conversions.
- **Cloudflare logs** (optional): webhook delivery logs.
- **Live page testing:** 5 PPC landing pages × desktop/mobile × with/without gclid = 20 test leads, each checked in Dengro for attribution preservation.

---

## 6. Daily rhythm (morning ritual)

Every morning Chris does search-terms triage. Standard flow:

1. Chris opens `/v2/search-terms` in ACT for today's date
2. Filters: Search/PMax → Block → Not advertised / Leak-exact / Leak-phrase
3. Chris screenshots the filtered list, you analyse every row, flag false-positives
4. Chris unchecks flagged rows, approves + pushes rest to Google Ads
5. Move through Search → PMax → Review → Pass 3 suggestions

Before deep analysis, always check:
- Topbar negatives pill is green (< 24h) — if not, prompt Chris to click Refresh
- If config has been edited or negs removed from GAds, prompt Refresh + Reclassify first

Common patterns to flag:
- Query contains "dental implant" + not-advertised term (crown, bridge, veneers) — this is now `review/mixed_intent` not `block`, so should be rare
- Phrase negs that look too broad (single-word like `care`, `clinic`, `centre` — reject in Pass 3)
- Implant-comparison queries ("implants vs X") — these are high intent, often false-blocks
- Over-60s queries — DBD's primary demographic

---

## 7. Backlog — ACT negatives module (prioritised)

Ordered by value. When Chris asks "what's next?" after triage, lead with these:

### 🔥 Top 5 (do soonest)

1. **Claude integration for search-terms analysis** — instead of Chris pasting screenshots for me to analyse, build a server-side endpoint on ACT that calls Claude API with filtered rows → inline annotations appear in the UI. Huge UX win, scales to multi-client. ~4-6hr Build 2 task. (Chris confirmed interest on 22 Apr.)

2. **Manual "Pull today's search-term data" button** — separate from Refresh Neg Lists. User wants to manually trigger today's search-term ingestion (currently only runs overnight).

3. **Pass 3 stopword filter** — Pass 3 keeps surfacing generic 1-word fragments like `care`, `clinic`, `centre`. Add a stopword list to exclude these during mining.

4. **Pass 3 location AI** — use spaCy NER or Claude API to detect dental-tourism countries (Turkey, Hungary, Poland, Spain etc.) automatically.

5. **"Reclassify on config change" auto-trigger** — currently Chris has to click Reclassify after editing Client Config. Auto-trigger on save would be cleaner.

### 🛠 Nice to have (batch together)

6. Rule precedence fix for Rule 5/Rule 7 edge cases (further refinement of mixed-intent)
7. Bulk "approve all on filter" button
8. Keyboard shortcuts for triage (j/k to navigate, a to approve, r to reject)
9. Saved filters / views
10. Visually deprioritise signal-less ambiguous rows
11. PMax Added/Excluded cross-reference in Search Terms UI
12. Duplicate-negative detector (flag GAds negs that already cover a proposed new neg)
13. "Review filter UX" reconsideration (Chris parked this on 21/4)

### 🏗 Architecture / ops

14. Proper relational migration of Client Config (currently textarea-backed)
15. Per-client Pass 3 threshold customisation
16. Fuzzy brand match (Option C, deferred from N1)
17. Pass 3 protected-words widening (does, clinic, care, front, treatment noise)

### 🔧 Small bugs

18. Pill cross-filtering edge cases
19. Pushed-row dual pill revisit
20. Flask error observability improvement

### 📊 Monitoring / reports

21. Per-client Pass 3 dashboard
22. Daily "cleanup impact" metric (negs pushed, terms classified, etc.)
23. Change log on Client Config edits

### 🔮 Future

24. Multi-client parallel triage
25. ML suggestions from historical decisions
26. Automated Pass 3 push for low-risk consolidations
27. Phrase-match vs exact-match optimisation advisor

---

## 8. ACT v2 build roadmap (beyond negatives)

Current status per memory:
- **A1-B2:** Complete (account-level engine + UI)
- **F1 (scheduler), F2 (morning review UI):** Complete
- **R1 (Weekly Reports module):** INSERTED before C1 — see memory. Auto-generate .pptx from DB + session summaries + Claude narrative. ~8-10hr build.
- **C1 Campaign Level Engine:** NEXT after tracking audit dust settles. 7 strategy-specific checks (Manual CPC, tCPA, tROAS, Max Conversions, Max Clicks, PMax, Standard Shopping).
- Then: C2 → C3 → D1-D4 (Ad Group/Keyword/Ad engines + UIs) → E1-E2 (Shopping) → G1-G3 (execution engine)

Rule: do NOT start C1 while tracking audit is unresolved — DBD's Week 2 report depends on having reliable conversion data, which depends on the audit fixes shipping.

---

## 9. Other DBD project work queued

### Week 2 report (Friday 24 April 2026)
- Chris will produce manually (existing v8-style template), automated R1 not yet built
- Depends partly on tracking audit fixes — likely still "All conv" for Week 2 unless Dengro/Zapier fixes ship fast
- Include: Week 1 vs Week 2 comparison, Impact of negatives work (388 neg terms pushed), Week 3 plan

### Cosmetic dentistry campaign build
- Scope expanded 21 Apr to include cosmetic dentistry (Chris added `cosmetic dentistry`, `cosmetic dentist` to services_advertised)
- Campaign not yet built — backlog

### Landing page optimisation
- Waiting on tracking audit to show which LPs are losing leads
- Chris already has PPC LPs at `/promo/google/*` (5 pages), plus a dedicated PMax LP

### PMax rebuild
- Mentioned in Week 1 call deck for Week 2 delivery
- Waiting on tracking fixes

### Other
- Vivo bridges config scope change (confirmed on client call 21 Apr — Chris needs to update services_advertised to include "Vivo bridge")
- Long-tail keyword expansion

---

## 10. Other clients

### Objection Experts (oe001)
- Signed 02/04/2026, first paying client. Manually managed while ACT is refined.
- `google_ads_customer_id: 8530211223`
- Account Level state: monitor_only
- 3 pitch reports delivered previously
- Negatives module working (tested against OE in parallel with DBD during N2/N3)
- Not actively being worked on — just daily triage

---

## 11. Critical files to know

### ACT codebase (active development)
- `act_dashboard/routes/v2_negatives_api.py` — search terms API (bulk-update, lists, refresh, reclassify, sticky)
- `act_dashboard/engine/negatives/pass1.py` — classification engine (rules 1-8 + sticky)
- `act_dashboard/engine/negatives/pass2.py` — target list routing
- `act_dashboard/engine/negatives/pass3.py` — phrase fragment consolidation
- `act_dashboard/scheduler/overnight_run.py` — scheduler phases (ingestion, engine, neg_stale_cleanup, neg_sticky_expiry, neg_pass1, neg_pass2)
- `act_dashboard/templates/v2/search_term_review.html` — main triage page
- `act_dashboard/templates/v2/rejected_terms.html` — sticky rejection management
- `act_dashboard/templates/v2/client_config.html` — settings + Negative Lists viewer tab
- `warehouse.duckdb` — the DB

### DBD site repo (READ ONLY — Giulio owns)
- `C:\Users\User\Desktop\dentalbydesign-repo\` — full clone
- `apps/web/src/scripts/utm-tracker.ts` — first-touch attribution (needs fix)
- `apps/web/src/scripts/track-conversion.ts` — 6 client-side conv types + Meta + MS UET
- `apps/web/src/layouts/BaseLayout.astro` — includes GTM (most pages)
- `apps/web/src/layouts/InvisalignLayout.astro` — NO GTM (bug)
- `apps/api/src/routes/api/v1/dengro-webhook-leads.ts` — Lead webhook handler
- `apps/api/src/routes/api/v1/dengro-webhook-journeys.ts` — Booking + Purchase handler
- `apps/api/src/lib/dengro-utils.ts` — Zapier + Meta Conversions API callers

### Client files
- `potential_clients/Inserta Dental/` — all DBD materials
- `potential_clients/Inserta Dental/Tracking Audit/` — audit work (this session)
- `potential_clients/Inserta Dental/Session Summary/` — daily session summaries
- `potential_clients/Inserta Dental/End-of-week reports/` — weekly pptx reports

---

## 12. How to run common commands

### Start Flask (Chris does this himself, don't auto-start)
```
cd C:\Users\User\Desktop\gads-data-layer
python act_dashboard/app.py
```

### Build the tracking audit deck
```
cd "C:/Users/User/Desktop/gads-data-layer/potential_clients/Inserta Dental/Tracking Audit/"
node build_deck.js
```

### Resize screenshots (Chris runs after taking screenshots)
```
python "C:\Users\User\Desktop\gads-data-layer\potential_clients\Inserta Dental\Tracking Audit\_resize.py"
```

### Inspect DBD repo
```
cd C:\Users\User\Desktop\dentalbydesign-repo
# grep, read — NEVER git add / commit / push
```

### Git after Build 2 merge
```
git push origin main
```

---

## 13. Known quirks / things that will trip you up

1. **Image token limit** — images across a single Claude Code session accumulate against an image-token limit separate from text context. Late-afternoon of 22 Apr, image reads started failing even on small new images. If it happens mid-session, hand off to a fresh one.

2. **Opera screenshots are retina** — a "1920px" Opera screenshot is often 3840px actual. Use `_resize.py` before asking Claude to read.

3. **PostToolUse hook "preview server" reminders** — ignore them when the file is not browser-observable (pptx scripts, markdown, etc.). Only relevant when editing Flask templates/CSS/JS that a dev server is serving.

4. **TodoWrite auto-reminders** — these appear as system-reminders at the end of tool results. They are not errors. Keep the todo list current and they stop nagging.

5. **DuckDB 1.1.0 UPDATE-on-UNIQUE bug** — when updating rows with a UNIQUE constraint on a changing column, DuckDB throws a false positive PK error. Workaround: read current value first, only UPDATE if changed. See `pass3.py` and `v2_negatives_api.py` history.

6. **Chris will NEVER check git** — you own it. Always push to origin/main after Build 2 merges.

7. **Briefs to Build 2** — Chris pastes them in a separate session. He expects:
   - Context (1 paragraph)
   - Exact files + line numbers to change
   - Specific code / SQL / config
   - Acceptance criteria (numbered list)
   - Commit messages (one per logical change)
   Build 2 will ship in 15min–4hr depending on scope.

8. **Chris is PM, not developer.** He will test UX, verify numbers, screenshot issues — but will NOT read code. Frame responses accordingly.

---

## 14. The Giulio relationship

Giulio Zanchetta is DBD's developer. He owns the Astro/Hono site and the Cloudflare API. He's responsive and technical. Chris has a friendly working relationship with him.

Rules:
- We audit, Giulio implements site-code changes (`utm-tracker.ts`, landing page forms, etc.)
- Briefs to Giulio are drafted by us, Chris sends
- We never touch the DBD repo beyond reading
- Logins come from Giulio when he gets round to it — don't push

---

## 15. Open questions Chris wants tracked

- Does Dengro store gclid capture-date AND form-submission-date separately? Would let us count leads where gclid was captured ≥1 day before form submit (validates first-touch theory).
- When user switches devices (phone → desktop) between click and form submit, what happens to the `__attr` cookie? Probably lost — need Enhanced Conversions data to bridge.
- Is CTM firing GAds conversions directly, or are phone calls only counted via Call Extensions? (Multiple Call Extension | X conversion actions in GAds suggests the latter, but CTM_Activity event in GA4 is mysterious.)
- What Meta Pixel ID is in the site vs what's in Meta Business Manager — cross-check when Meta access arrives.

---

# Prompt for Chris to paste into new MC - Project Manager 3 session

Copy everything below this line into the first message of the new session.

---

```
I'm starting a fresh PM session after handing off from yesterday's session (22 April 2026). The previous session ran out of image-token budget mid-afternoon and was getting unreliable.

Your role: PM / planning partner. A separate session (ACT Build 2) does all Flask/Python/JS code for the ACT app. You write briefs, I paste them there.

Working directory: C:\Users\User\Desktop\gads-data-layer

**First thing — read these two docs before I ask anything:**
1. potential_clients/Inserta Dental/HANDOFF_TO_MC_PM3.md  (full context + everything in flight)
2. C:\Users\User\.claude\projects\C--Users-User-Desktop-gads-data-layer\memory\MEMORY.md  (auto-memory from prior sessions)

Also read the most recent session summary:
3. potential_clients/Inserta Dental/Session Summary/SESSION_SUMMARY_22-4-26.md

**Today's priorities** (in order):
1. Polish the Tracking Audit deck (v2 → v3) — fix colours, footer, top-right pill, subtitle styling, tables, fonts. See handoff §5-A for exact specs. Reference: DentalByDesign.co.uk - Week 1 Report 13-17 April 2026-v8.pptx.
2. When deck is polished, I'll review + send the Giulio email (email_to_giulio_DRAFT.md).
3. Daily search-terms triage for 23/4 (morning ritual, see handoff §6).

**Then waiting on:**
- Giulio replies to the email
- Dengro, Zapier, CallTrackingMetrics logins

Confirm you've read everything and tell me the top 3 things you understand about what's in flight. Then we start.
```
