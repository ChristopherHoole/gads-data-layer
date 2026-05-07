# ACT Backlog — captured 24 April 2026

Work to do on ACT, ordered shortest-term/smallest → longest-term/biggest.
Snapshot at end of Friday 24 April. Review/reprioritise whenever Chris picks it up.

---

## Tier 1 — Short-term fixes (hours, not days)

### 1.1 Scheduler pipeline truncation bug
**Symptom:** Overnight `python -m act_dashboard.scheduler.overnight_run` only runs ingestion + engine phases, silently skips `neg_stale_cleanup`, `neg_pass1`, `neg_pass2`, `neg_pass3`. Chris has to click Reclassify manually each morning.
**Impact:** Every day: ~10 min of manual triage the system should automate.
**Fix scope:** Brief Build 2. Probably a try/except swallowing phase errors, or a boolean flag tripping early. Error isolation is fine — just don't stop the loop.

### 1.2 CHECK constraint error on `act_v2_scheduler_runs.phase`
**Symptom:** End of each cycle logs `FATAL cycle error for dbd001: Constraint Error: CHECK constraint failed on table act_v2_scheduler_runs with expression CHECK((phase IN ('ingestion', 'engine', 'neg_stale_cleanup', 'neg_pass1', 'neg_pass2', 'neg_pass3')))`
**Impact:** Noise in logs; cycle status shows as `unknown` even when everything succeeded.
**Fix scope:** Add a missing enum value or widen the CHECK constraint. 10 min.

### 1.3 Flask rate limiter — proper IP exemption (not today's bump)
**Symptom:** Hit 429 on rapid search-term triage. Today bumped from 50/hour → 2000/hour as band-aid.
**Proper fix:** Exempt `127.0.0.1 / ::1` via `limiter.request_filter`. Keep production rate limits for external callers.
**File:** `act_dashboard/app.py` line ~133.
**Fix scope:** 15 min.

### 1.4 Row-number drift in Pass 1/2 Review UI
**Symptom:** After actioning 50 rows, row numbers on the remaining terms shift, making a mid-session table of decisions hard to map back to the UI.
**Impact:** Cognitive load during triage, especially when batching by reason.
**Fix scope:** Freeze row numbers at page load, or add a stable per-term ID that persists across actions.

### 1.5 Task Scheduler wiring (Windows Task Scheduler → overnight run)
**Pending from F1.** Wire up Windows Task Scheduler to run `python -m act_dashboard.scheduler.overnight_run` at 6:30 AM UK daily.
**Why it matters:** Without this, every morning is a manual scheduler trigger + Reclassify click. On a live server this becomes cron/systemd.
**Fix scope:** 10-min user task (Chris). Test end-to-end next weekday.

### 1.6 Auto-watch Downloads for PMax CSV
**Symptom:** Every morning Chris clicks the GAds scheduled-report email link, CSV saves to Downloads, then Chris has to remember to run the ingest CLI.
**Fix:** Python watchdog that monitors `~/Downloads` for `Search terms report*.csv`, moves to archive folder, runs `pmax_csv_ingest --client-id dbd001`, logs result.
**Fix scope:** 1–2 hours. Brief Build 2.

### 1.7 Post-deploy keyword coverage runner
**Current:** Manual invocation of the coverage-check Python script per LP.
**Fix:** Put it in ACT as a button: "Verify live page" → runs the check, logs result to `act_v2_recommendations` as a QA signal.
**Fix scope:** 2–3 hours.

### 1.8 Date picker convention doc
**Already agreed (MEMORY.md):** Picker = analysis_date. Picker 24/4 = data for 23/4. This is intentional and correct.
**Action:** Surface this in UI — a small "?" tooltip on the date picker explaining what the date means. Prevents repeated confusion (including Claude's today).
**Fix scope:** 20 min.

---

## Tier 2 — Medium-term features (days)

### 2.1 AI analysis inside ACT ⭐ [major initiative]
**Replaces:** The manual "paste term list to Claude chat, get verdicts back" loop Chris runs.
**Components:**
- **2.1a** AI classification endpoint — takes a batch of terms, returns `block / review / keep` + reasoning for each
- **2.1b** AI-generated reasoning shown per row in Search Review UI (hover tooltip or column)
- **2.1c** AI confidence scoring (high/med/low) per verdict
- **2.1d** "Bulk AI triage" button → AI pre-sorts all Review terms into Approve/Reject buckets; user just rubber-stamps
- **2.1e** AI-driven target-list assignment for Pass 3 (route by intent — location/competitor/service — not word count). Fixes today's observed bug where location phrases landed in `1_word_phrase` list.
- **2.1f** AI intent tagging (researcher / price-shopper / ready-to-book / competitor)
- **2.1g** Feedback loop — system learns from Approve/Reject history to tune future recommendations
- **2.1h** Cross-client learning — OE blocks → surface for DBD review (with gate)
- **2.1i** AI brand-term auto-detection — flag potential brand/competitor/location terms for review queue

**Why it matters:** Biggest unlock for scaling ACT to N clients. Manual triage at 100 terms/day × N clients doesn't scale; AI pre-sort makes it feasible. Also removes the need to leave ACT to use Claude separately.

**Fix scope:** 1–2 weeks. Needs its own design doc. First MVP = 2.1a + 2.1b + 2.1d in one sprint.

### 2.2 Monthly neg-list audit workflow
**Why:** Pass 3 currently assigns targets by word count, not intent. Over time, wrong terms land in wrong lists. Needs periodic clean-up until AI fix (2.1e) ships.
**Workflow:**
1. Export all negative-list keywords per list to a table
2. Flag rows where keyword intent ≠ list intent (location token in non-location list, etc.)
3. Show a one-click "Move to correct list" action
4. Log the move in `act_v2_executed_actions`
**Fix scope:** 1 day.

### 2.3 R1 — Weekly Reports module
**Status in build plan:** Inserted after F2, before C1 (per MEMORY.md).
**Why:** Manual weekly reports burned ~500k tokens + hours for DBD Week 1. Doesn't scale past 1 client.
**Components:**
- Master `.pptx` template with `{{PLACEHOLDERS}}` (derived from Week 1 v8)
- Data aggregator (week totals, 8-week trend, daily breakdown, campaign breakdown)
- Session-summary ingester (reads client's `/Session Summary/*.md` for the week)
- Narrative generator (Claude API call → Key Findings, Recommendations, Core Insight)
- Template filler (python-pptx)
- ACT UI button: "Generate Week N Report" on Morning Review / client page
- Multi-client support

**Week 2 note:** Reverted from Friday to Monday delivery so reports use full Sun–Sat data window. Week 2 report due **Mon 28 April** (hand-edit v8 template while R1 is built).

**Fix scope:** 8–10 hours MVP. Lean on Week 1 v8 layout.

### 2.4 Pass 3 stopword audit automation
Today extended `neg_pass3_stopwords` with 13 tokens via direct SQL. Should be a UI — `/v2/config` page for `dbd001` shows stopwords list, user can add/remove. Each client has different noise words.
**Fix scope:** 2 hours.

### 2.5 Search Terms system backlog already captured
Full list in today's earlier chat exchange — includes finish-today's-triage items now done, and the AI list under 2.1 above. Nothing additional to flag here.

---

## Tier 3 — Engine + UI build-out (weeks)

Per MEMORY.md, the A→G build plan. Progress so far: A1-A3, B1-B2, Onboarding/F1/F2 COMPLETE. Morning Review live for both clients. First real ACT recommendation produced (DBD budget shift £65/day DII → Brand).

### 3.1 C1 — Campaign Level engine
7 strategy-specific checks: Manual CPC, tCPA, tROAS, Max Conversions, Max Clicks, PMax, Standard Shopping.
DBD has PMax so will immediately produce Campaign-level recs after C1 ships.

### 3.2 C2 — Campaign Level UI
Same pattern as B2 Account Level UI but scoped per campaign.

### 3.3 C3 — Campaign slide-in / deep-dive
Per MEMORY.md `project_act_v2_slidein.md`. Shared slide-in components exist. Build on that foundation.

### 3.4 D1-D4 — Ad Group / Keyword / Ad engines + UIs
Granular level. Based on prototype pages 5–7 (all signed off).

### 3.5 E1-E2 — Shopping engines
For OE which has Shopping campaigns (and future shopping clients).

### 3.6 G1-G3 — Execution layer
Actual pushes to Google Ads (current neg pushes are via the legacy path; G ports all actions to one clean execution layer).

---

## Tier 4 — Long-term / strategic (months)

### 4.1 Multi-client scaling
ACT already stores by `client_id` so data model scales. What doesn't scale yet:
- Weekly reports (need R1 first)
- Onboarding (still partly manual — seed scripts + level state setup)
- Daily triage (needs AI 2.1a–d for N-client workloads)

### 4.2 Onboarding automation
One CLI command: `act onboard --customer-id XXX --persona lead_gen_cpa --target-cpa 75`. Backfills, seeds, level-states, ready for Morning Review next day.

### 4.3 Proper A/B experiment tracking
Today's "full switch + extra caution" is a speed choice. Long-term ACT should integrate GAds Experiments for proper 50/50 randomised splits on LP tests, with stats significance shown in-UI.

### 4.4 ACTAgency website
Separate agency site for PPC agency search traffic (per MEMORY.md priority #3). Not the ACT tool itself — the marketing site for the agency selling ACT as a service.

### 4.5 Notification / alerts system
Morning Review already catches day-to-day. Missing: push notifications on CPA spikes, budget overruns, ad disapprovals, conversion stall — anything that doesn't wait until tomorrow morning. Email + WhatsApp integration.

### 4.6 Multi-account / MCC views
Some clients have multiple GAds accounts (franchise/multi-location). ACT currently one-account-per-client. Future: link multiple `google_ads_customer_id` per client with roll-up views.

### 4.7 Budget optimiser
Beyond current budget-allocation recommendations — a proper optimiser that proposes weekly budget reallocations across the full account given a target CPA/ROAS.

### 4.8 Creative / ad copy generator
Today's LP copy work is human-in-loop. Next: ACT generates ad copy variants from the LP + landing page brief, pushes to GAds, tracks performance per variant. (Longer horizon than LP generation.)

---

## Suggested weekend-work priorities for Chris

If doing 2–4 hours on ACT this weekend:
1. **1.2** (CHECK constraint) — 10 min, removes daily error noise
2. **1.3** (proper rate-limit IP exemption) — 15 min, undoes today's band-aid properly
3. **1.8** (date picker tooltip) — 20 min, user-facing clarity
4. **1.4** (row-number drift UX) — 1–2 hours, quality-of-life improvement for daily triage
5. **2.4** (Pass 3 stopwords UI) — 2 hours, moves config out of SQL and into the app

If doing 6+ hours:
6. **2.1a** (AI classification endpoint MVP) — lay the foundation for the major AI initiative. Hook a single `/v2/api/ai/classify-terms` endpoint, wire to Claude API, test on today's PMax Review backlog.

---

**End of backlog snapshot.** Review + reprioritise at next PM session.
