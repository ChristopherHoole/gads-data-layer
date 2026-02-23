# CHAT 29 BRIEF — M8: Changes Page + Radar Monitoring

**Date:** 2026-02-22
**Module:** M8
**Estimated time:** ~140 minutes
**Wireframe:** `C:\Users\User\Desktop\gads-data-layer\docs\M8_WIREFRAME.html`
**Previous chat:** Chat 28 (`C:\Users\User\Desktop\gads-data-layer\docs\CHAT_28_HANDOFF.md`)

---

## SECTION 1 — WORKER CHAT WORKFLOW (MANDATORY — DO NOT SKIP ANY STEP)

This section defines the exact process this worker chat must follow from start to finish. Every step is mandatory. Master Chat will not approve work from a worker that skipped any stage.

---

### STEP 1 — Christopher uploads 7 documents to start the worker chat

Before the worker does ANYTHING, Christopher uploads all of the following. Worker must confirm all 7 received before proceeding. If any are missing, ask Christopher to upload them before continuing.

```
1. Codebase ZIP
   C:\Users\User\Desktop\gads-data-layer  (full ZIP of entire folder)

2. CHAT_29_BRIEF.md  (this file)
   C:\Users\User\Desktop\gads-data-layer\docs\CHAT_29_BRIEF.md

3. PROJECT_ROADMAP.md
   C:\Users\User\Desktop\gads-data-layer\docs\PROJECT_ROADMAP.md

4. CHAT_WORKING_RULES.md
   C:\Users\User\Desktop\gads-data-layer\docs\CHAT_WORKING_RULES.md

5. MASTER_KNOWLEDGE_BASE.md
   C:\Users\User\Desktop\gads-data-layer\docs\MASTER_KNOWLEDGE_BASE.md

6. DASHBOARD_PROJECT_PLAN.md
   C:\Users\User\Desktop\gads-data-layer\docs\DASHBOARD_PROJECT_PLAN.md

7. WORKFLOW_GUIDE.md
   C:\Users\User\Desktop\gads-data-layer\docs\WORKFLOW_GUIDE.md
```

After all 7 confirmed:
- Extract ZIP, explore structure
- Read this brief in full
- Read PROJECT_ROADMAP.md
- Read CHAT_WORKING_RULES.md
- Read MASTER_KNOWLEDGE_BASE.md
- Then proceed to Step 2

---

### STEP 2 — Worker produces exactly 5 questions for Master Chat

After reading all documents, worker identifies gaps and ambiguities and produces **exactly 5 clarifying questions** — no more, no fewer. Questions must be specific, categorised, and not answerable by reading the uploaded docs carefully.

**Format:**
```
5 QUESTIONS FOR MASTER CHAT

Q1. [DATABASE] Question text?
Q2. [ROUTE] Question text?
Q3. [DESIGN] Question text?
Q4. [SCOPE] Question text?
Q5. [RULES] Question text?

Waiting for Master Chat answers before proceeding.
```

Worker **STOPS** completely after sending questions. Does not write any code or plan until Christopher pastes Master Chat answers back.

---

### STEP 3 — Worker produces a detailed build plan for Master Chat

After receiving answers to the 5 questions, worker produces a full build plan covering every file to create or edit (full Windows paths), the order of operations, dependencies, and estimated time per step.

**Format:**
```
DETAILED BUILD PLAN FOR MASTER CHAT REVIEW

Files to create/modify:
- C:\Users\User\Desktop\...\file.py — what changes

Step-by-step implementation:
STEP A: [Task] (~X min)
  - [Specific actions]
STEP B: [Task] (~X min)
  - [Specific actions]

Total estimated time: X minutes
Risks / unknowns: [Any remaining concerns]

Waiting for Master Chat approval before starting.
```

Worker **STOPS** after sending the build plan. Does not write any code until Christopher pastes Master Chat approval back.

---

### STEP 4 — Implementation rules (during build)

Once Master Chat approves the build plan, worker implements one file at a time:

- **Before editing ANY existing file** → ask Christopher to upload the current version first. Never use the ZIP version — it may be outdated. (CHAT_WORKING_RULES.md Rule 2)
- **Every file delivered** → complete, ready-to-use file only. Never code snippets. Full Windows path stated clearly above each file.
- **Full Windows paths always.** Example: `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\changes.py` — never `routes/changes.py`
- **After each file** → provide exact PowerShell commands to restart server and test. Wait for Christopher's confirmation before moving to the next file.

---

### STEP 5 — Completion summary sent to Master Chat

Once all work is done and tested, worker writes a detailed completion summary:
- Every file created or modified (full Windows paths)
- What was built and how it works
- Test results per checklist item (pass/fail)
- Any known issues or deviations from brief

Christopher pastes this into Master Chat. Worker waits for Master Chat approval before proceeding.

---

### STEP 6 — Handoff documents created (after Master Chat approval)

After Master Chat approves the completion summary, worker creates exactly 2 handoff documents:

```
C:\Users\User\Desktop\gads-data-layer\docs\CHAT_29_DETAILED_SUMMARY.md
C:\Users\User\Desktop\gads-data-layer\docs\CHAT_29_HANDOFF.md
```

Christopher pastes both into Master Chat for final review.

---

### STEP 7 — Git commit (Master Chat instructs after approving handoff docs)

Master Chat reviews both handoff docs and instructs Christopher to run:

```powershell
cd C:\Users\User\Desktop\gads-data-layer
git add .
git commit -m "Chat 29 (M8): Changes page + Radar monitoring complete"
git push origin main
```

---

## SECTION 2 — Context

Chat 28 completed the full 4-tab Recommendations UI (Pending / Monitoring / Successful / Declined) and wired the Accept/Decline/Modify action buttons. It also created a `changes` table in `warehouse.duckdb` that records every user action as an audit trail.

Chat 29 builds on this in four areas:

1. **Changes page redesign** — Replace the existing Changes page with a 2-tab card-based UI: "My Actions" (user decisions from the `changes` table) and "System Changes" (automated changes from `analytics.change_log`). Both tabs use the same M6/M7 card format — consistent with the rest of the system.

2. **Radar background job** — Build `act_autopilot/radar.py`, a background thread that runs every 60 seconds, evaluates monitoring-period recommendations whose deadline has passed, and transitions them to `successful` or `reverted` based on KPI performance.

3. **Reverted card variant + 5th tab** — Surface the `reverted` status (already in the schema) as a 5th tab on both `/recommendations` and `/campaigns`, with its own card variant (red top bar, red outcome block).

4. **monitoring_minutes field** — Add `monitoring_minutes` to `rules_config.json` for fast testing (1–2 minute monitoring periods). Radar checks this first; if > 0 it uses minutes instead of days.

---

## SECTION 3 — Wireframe

**Read `C:\Users\User\Desktop\gads-data-layer\docs\M8_WIREFRAME.html` in full before writing any code.** It covers all 8 sections:

1. Summary strip (4 stat cards)
2. Tab bar (My Actions / System Changes)
3. My Actions tab — card grid, all card variants, filter bar
4. System Changes tab — card grid with source pill (Autopilot / Radar)
5. Reverted card variant + 5th tab on recommendations pages
6. Radar job — 4-step flow diagram
7. monitoring_minutes config — full table for all 13 rules + code snippet
8. Implementation reference table — every file and what changes

---

## SECTION 4 — Deliverables

### 4.1 `C:\Users\User\Desktop\gads-data-layer\act_autopilot\rules_config.json` — MODIFY

Add `monitoring_minutes` to all 13 rules. Update `monitoring_days` from 0 to values below. Request current file before editing (Rule 2).

| Rule | monitoring_days | monitoring_minutes |
|---|---|---|
| Budget 1 | 0 | 1 |
| Budget 2 | 0 | 2 |
| Budget 3 | 7 | 0 |
| Budget 4 | 7 | 0 |
| Budget 5 | 7 | 0 |
| Budget 6 | 7 | 0 |
| Bid 1 | 0 | 2 |
| Bid 2 | 14 | 0 |
| Bid 3 | 14 | 0 |
| Bid 4 | 7 | 0 |
| Bid 5 | 7 | 0 |
| Bid 6 | 7 | 0 |
| Status 1 | 3 | 0 |

**Logic:** If `monitoring_minutes > 0`, Radar uses minutes. If `monitoring_minutes = 0`, Radar uses `monitoring_days`.

---

### 4.2 `C:\Users\User\Desktop\gads-data-layer\act_autopilot\radar.py` — CREATE

New file. Three functions:

**`radar_loop()`** — Infinite loop, `time.sleep(60)`, opens `warehouse.duckdb`, calls `evaluate_all_monitoring_recs(conn)`, closes. Logs each cycle.

**`evaluate_all_monitoring_recs(conn)`** — Queries all `status = 'monitoring'` recs. For each: loads rule config to get `monitoring_minutes`/`monitoring_days`. Computes deadline. If `now() < deadline` → skip. If `now() >= deadline` → call `evaluate_monitoring_rec(conn, rec)`.

**`evaluate_monitoring_rec(conn, rec)`** — Loads KPI from `ro.analytics.campaign_features_daily ORDER BY date DESC LIMIT 1`. KPI check:
- Budget rules: `roas_w7` dropped ≥ 15% vs at `accepted_at` → revert
- Bid rules: `roas_w7` or `cvr_w7` dropped ≥ 15% → revert
- Status rules: no KPI check → always successful

On success: `UPDATE recommendations SET status='successful', resolved_at=NOW()`. Write `changes` row `executed_by='radar_resolved'`.
On revert: `UPDATE recommendations SET status='reverted', resolved_at=NOW(), revert_reason='...'`. Write `changes` row `executed_by='radar_revert'`.

**No Google Ads API call in Chat 29 — DB status update only.**
All DB operations in try/except — log errors, skip rec, never crash the loop.

---

### 4.3 `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — MODIFY

Add after app initialisation:
```python
from act_autopilot.radar import radar_loop
import threading
threading.Thread(target=radar_loop, daemon=True).start()
```
`daemon=True` is mandatory. Request current file before editing (Rule 2).

---

### 4.4 `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\recommendations.py` — MODIFY

- Update `_load_monitoring_days()` to also return `monitoring_minutes`
- Add `reverted_recs` query: `WHERE status = 'reverted' ORDER BY resolved_at DESC`
- Pass `reverted_recs` to template
- Extend `/recommendations/cards` endpoint to return `reverted` array
- Update `_get_summary()` to include `reverted` count

Request current file before editing (Rule 2).

---

### 4.5 `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\changes.py` — MODIFY

- Add query for `changes` table: `SELECT * FROM changes WHERE customer_id = ? ORDER BY executed_at DESC`
- Compute summary counts: total, accepted, declined, modified
- Keep existing `ro.analytics.change_log` query for System Changes tab
- Pass both datasets and summary counts to template

Verify exact column names in both tables before writing queries. Request current file before editing (Rule 2).

---

### 4.6 `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\changes.html` — FULL REWRITE

Must extend `base_bootstrap.html`. Follow wireframe Sections 3 and 4 exactly.

- Summary strip: 4 stat cards (Total / Accepted / Declined / Modified)
- Tab bar: My Actions (default active) / System Changes — pure JS switching, no page reload
- My Actions: `rec-grid-2` card grid, filter bar (All / Accepted / Declined / Modified / Reverted), card variant matches current recommendation status, Modified actions show amber "Modified" tag in change block, source pill shows "User", no action buttons
- System Changes: same `rec-grid-2` card grid, filter bar (All / Monitoring / Successful / Reverted), source pill shows "Autopilot" or "Radar" in footer meta
- Empty states per tab and per filter
- All read-only — no action buttons on any card

---

### 4.7 `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\recommendations.html` — MODIFY

Add 5th Reverted tab. Tab order: **Pending → Monitoring → Successful → Reverted → Declined**

- Red tab badge (`tab-badge-red`)
- Reverted card: `card-reverted` (red border), `rt-reverted` (red top bar), grey change block with "(then reverted)" note, `ob-reverted` outcome block — "Auto-reverted by Radar" + dates + `revert_reason`
- Footer meta only — no action buttons. "⟳ Reverted" readonly label
- Empty state
- Update summary strip to include Reverted count

Request current file before editing (Rule 2).

---

### 4.8 `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\campaigns.html` — MODIFY

Add 5th Reverted inner tab to Recommendations tab panel:
- `cam-btn-reverted` tab button
- `cam-tab-reverted` content div
- `renderRevertedCards(recs)` JS function
- Update `loadRecCards()` to populate reverted tab and badge

Request current file before editing (Rule 2).

---

## SECTION 5 — Technical Constraints

- All templates MUST extend `base_bootstrap.html` — never `base.html`
- All read queries MUST use `ro.analytics.*` prefix
- All writes go to `warehouse.duckdb` — never to readonly analytics DB
- Radar thread MUST be `daemon=True`
- Never insert helper functions between a `@bp.route` decorator and its function
- Use existing M6/M7 CSS classes — verify against existing stylesheet before adding new ones
- New CSS classes needed: `rt-reverted`, `card-reverted`, `ob-reverted`, `ot-reverted`, `sp-reverted`, `tab-badge-red` — check if any already exist first
- Radar revert is DB-only in Chat 29 — no Google Ads API call
- DuckDB write locking: use `with conn:` context manager in Radar to keep transactions short

---

## SECTION 6 — Key Database Facts

### `changes` table (warehouse.duckdb — created Chat 28)
```
change_id, customer_id, campaign_id, campaign_name, rule_id,
action_type, old_value, new_value, justification,
executed_by  (user_accept / user_decline / user_modify / radar_resolved / radar_revert),
executed_at, dry_run, status
```
Run `SELECT DISTINCT executed_by FROM changes` to verify actual values written by Chat 28 before building filter/source pill logic.

### `recommendations` table (warehouse.duckdb)
- `status` supports: pending / monitoring / successful / declined / **reverted**
- `revert_reason` — verify column exists. If missing: `ALTER TABLE recommendations ADD COLUMN revert_reason VARCHAR`

### `ro.analytics.campaign_features_daily`
- `roas_w7`, `cvr_w7`, `campaign_id`, `date`
- Use `ORDER BY date DESC LIMIT 1` — never `WHERE date = today()`

---

## SECTION 7 — Implementation Order

1. `rules_config.json` — add `monitoring_minutes`, update `monitoring_days`
2. `radar.py` — create full file, test logic in isolation
3. `app.py` — add thread. **Test: Flask starts without errors**
4. `recommendations.py` — `monitoring_minutes` support, `reverted_recs`, extend `/cards`
5. `recommendations.html` — 5th Reverted tab. **Test both recommendation pages**
6. `campaigns.html` — 5th Reverted inner tab
7. `changes.py` — My Actions query, summary counts
8. `changes.html` — full rewrite. **Test all tabs and filters**

---

## SECTION 8 — Testing Checklist

### Radar
- [ ] Flask starts without errors after adding background thread
- [ ] Radar loop logs to console every 60 seconds
- [ ] Accept rec on rule with `monitoring_minutes: 1` → after 1 minute, card moves to Successful tab on page refresh
- [ ] Simulate KPI degradation → after monitoring period, card moves to Reverted tab
- [ ] `changes` table contains `radar_resolved` or `radar_revert` row after each resolution
- [ ] Radar loop does not crash on missing KPI data — skips and continues

### Reverted tab (both pages)
- [ ] 5th tab visible on `/recommendations` — correct order: Pending / Monitoring / Successful / Reverted / Declined
- [ ] Reverted cards: red top bar, red outcome block, `revert_reason` shown
- [ ] Red tab badge
- [ ] 5th inner tab visible on `/campaigns`
- [ ] No 500s, no JS console errors on either page

### Changes page
- [ ] `/changes` loads without errors
- [ ] Summary strip shows correct counts from `changes` table
- [ ] My Actions tab default active, `rec-grid-2` card grid renders correctly
- [ ] Card variants correct per status (monitoring / successful / reverted / declined)
- [ ] Modified actions show amber "Modified" tag in change block
- [ ] Filter buttons work client-side — no page reload
- [ ] System Changes tab shows cards with Autopilot / Radar source pill
- [ ] Tab switching — no page reload
- [ ] Empty states display correctly
- [ ] No 500s, no JS console errors

---

## SECTION 9 — Known Gotchas

- `revert_reason` column may not exist in `recommendations` — check before Radar writes to it, `ALTER TABLE` if missing
- DuckDB interval syntax: `accepted_at + INTERVAL '1 MINUTE'` — verify before using
- `campaign_features_daily` — use `ORDER BY date DESC LIMIT 1`, not `WHERE date = today()`
- Run `SELECT DISTINCT executed_by FROM changes` before building source pill logic — verify actual values
- Existing `changes.html` may be legacy Tailwind — full rewrite either way

---

## SECTION 10 — Handoff Requirements

After Master Chat approves the completion summary, worker creates:
```
C:\Users\User\Desktop\gads-data-layer\docs\CHAT_29_DETAILED_SUMMARY.md
C:\Users\User\Desktop\gads-data-layer\docs\CHAT_29_HANDOFF.md
```
Both sent to Master Chat for review before git commit.
