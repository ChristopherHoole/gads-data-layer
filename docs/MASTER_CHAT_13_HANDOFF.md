# MASTER CHAT 13.0 HANDOFF

**From:** Master Chat 12.0
**To:** Master Chat 13.0
**Date:** 2026-03-19
**Status:** Ready for handoff

---

## ⚠️ FIRST THING TO DO

Read ALL of the following project files before doing anything else:
- `MASTER_KNOWLEDGE_BASE.md`
- `PROJECT_ROADMAP.md`
- `LESSONS_LEARNED.md`
- `KNOWN_PITFALLS.md`
- `WORKER_BRIEF_STRUCTURE.md`

These are in the Claude Project files panel. Read them all, confirm you've read them before proceeding.

---

## WHAT MASTER CHAT 12.0 COMPLETED

### Chat 101 — Flags System ✅
**Commits:** b8188fe (pre-build checkpoint) + final commit

**Built end-to-end:**
- `flags` DB table in warehouse.duckdb
- `_run_flag_engine()` in recommendations_engine.py — evaluates `rule_or_flag = 'flag'` rules after main engine runs, uses same CAMPAIGN_METRIC_MAP and `_evaluate_condition()`, correct MAX(snapshot_date) date query, duplicate prevention
- `/flags/cards` GET — returns `{active, snoozed, history}`, lazy snooze expiry check on every call
- `/flags/<id>/acknowledge` POST — sets status=snoozed, snooze_until = NOW() + cooldown_days from rules table
- `/flags/<id>/ignore` POST — sets status=snoozed, snooze_until = NOW() + days (7/14/30)
- All 3 routes CSRF exempted
- Flags tab on main Recommendations page — entity filter pills (All/Campaigns/Ad Groups/Keywords/Ads/Shopping), active table, collapsible Snoozed section (with Snoozed until column), collapsible History section (with Actioned column)
- Flags subtab on all 5 entity pages — active table + collapsible Snoozed + collapsible History
- Expand rows on ALL flag tables across all pages — Why triggered / Flag details / Rule details
- Actions dropdown on ALL flag rows (active, snoozed, history) across all pages

**Bugs found and fixed during testing (important for KNOWN_PITFALLS):**
1. All 15 `vs_prev_pct` flag conditions stored as whole numbers (e.g. -30) not decimals (-0.30) — fixed via `fix_all_flag_conditions.py` (already run, do not re-run)
2. 8 flags had `op=None` — fixed with correct operators (lt/gt) in same script
3. Bootstrap dropdowns on dynamically rendered rows — event delegation required, not bootstrap.Dropdown reinit
4. Functions inside IIFE inaccessible from inline onclick — exposed via `window.fnName`
5. `stopPropagation()` on snoozed/history TDs silently blocked event delegation — removed
6. Snoozed/History sections initially missing from entity page subtabs — added to all 5 pages

**Tested and verified:**
- ✅ Engine generates flags with lowered threshold (id=33 temporarily set to -0.05)
- ✅ Duplicate prevention — SkippedDuplicate=1 on second run
- ✅ Expand row on active, snoozed and history rows on all pages
- ✅ Actions dropdown on all rows on all pages
- ✅ Acknowledge moves flag to Snoozed with correct snooze_until date
- ✅ Snoozed section expands with correct columns
- ✅ Flask starts cleanly, no console errors

**Flag 33 threshold restored to -0.30 after testing.**

---

## CURRENT DB STATE

```
Rules:     19 (13 Budget, 6 Bid) — all enabled
Flags:     30 (16 Performance, 8 Anomaly, 6 Technical) — all enabled
Templates: 3
flags table: 0 rows (cleared after testing)
Recommendations: 0 (cleared)
Changes: 0 (cleared)
```

**Synthetic data:** Christopher Hoole client, customer_id `1254895944`, 4 campaigns
**Last valid snapshot date:** 2026-03-16

---

## IMMEDIATE PRIORITIES FOR MASTER CHAT 13

### 1. Fix Keywords search terms ← START HERE
**File:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\keywords.py` line 187
**Problem:** When using a custom date range from the date picker (e.g. "last 14 days", "this month"), the search terms table disappears. Preset buttons (7d, 30d, 90d) work correctly.
**Error:** `Binder Error: Cannot mix values of type DATE and VARCHAR in BETWEEN clause`
**Fix:** The `snapshot_date` column is type DATE but the custom date range passes a VARCHAR string. Cast the parameter: `CAST(? AS DATE)` in the BETWEEN clause, or cast the column.
**Scope:** Quick fix — 1 file, targeted change to `load_search_terms()` function.

### 2. Fix Shopping page query
**File:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\shopping.py` line 108
**Error:** `Binder Error: Referenced table "s" not found! Candidate tables: "shopping_campaign_daily"`
**Fix:** A table alias `s` is used in a WHERE clause but not defined in the FROM clause. Read the query, find where `s` should be aliased, add it.
**Scope:** Quick fix — 1 file, targeted change to the query in `load_shopping_campaigns()`.

### 3. Fix trigger summary label — rule 19
**File:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\recommendations.py`
**Problem:** Rule 19 (Loosen tCPA Target) shows "ROAS" in the trigger summary label instead of "CPA"
**Fix:** Find where trigger summary labels are generated for rule 19 and correct the metric label.
**Scope:** Quick fix — targeted label correction.

### 4. After fixes — Rules strategic review
Design discussion in Master Chat 13 → review all 19 rules one by one → agree changes → Claude Code brief to implement.

---

## GOOGLE ADS (monitor only)

| Field | Value |
|-------|-------|
| Primary account | 487-268-1731 — suspended, appeal ID 6448619522 |
| Test account | 125-489-5944 — active |
| MCC | 152-796-4125 |
| Developer token | oDANZ-BXQprTm7_Sg4rjDg |
| API Case ID | 21767540705 — Basic Access pending |
| API Access Level | Explorer |

**Do NOT submit another appeal.** Monitor chris@christopherhoole.com for both.

---

## CRITICAL TECHNICAL CONTEXT

### Claude Code
Accessed via the **Code tab in the Claude Desktop App** — NOT PowerShell.

### Brief Delivery Rule
Always save Claude Code briefs as downloadable files to `/docs/` — never inline in chat.

### Quick Fix Rule
Fixes to 1–3 files with a clear, well-defined change → do in Master Chat directly (upload file → edit → return complete file). Only send to Claude Code when task requires 4+ files, new routes, or significant logic.

Items 1, 2 and 3 above are all quick fixes — do them in Master Chat directly, not Claude Code.

### Fresh PowerShell Start
```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python act_dashboard/app.py
```

### Clear All
```powershell
python -c "import duckdb; conn = duckdb.connect('warehouse.duckdb'); conn.execute('DELETE FROM recommendations'); conn.execute('DELETE FROM changes'); conn.execute('DELETE FROM flags'); print('Cleared'); conn.close()"
```

### Git Commit
```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
git add .
git commit -m "Chat XX: description"
git push origin main
```

### Roadmap Format
When asked for the full roadmap, ALWAYS use the format defined in WORKER_BRIEF_STRUCTURE.md — sections with own numbered lists starting from 1, one item per line.

### SMTP Credentials (email_config.yaml — gitignored)
```yaml
smtp_host: smtp.gmail.com
smtp_port: 587
smtp_username: chris@christopherhoole.com
smtp_password: iflslbdfppfoehqz
daily_limit: 100
```

---

## KEY FILE PATHS

| File | Purpose |
|------|---------|
| `act_dashboard/routes/keywords.py` line 187 | Search terms DATE/VARCHAR bug |
| `act_dashboard/routes/shopping.py` line 108 | Shopping query alias bug |
| `act_dashboard/routes/recommendations.py` | Accept/decline/monitoring, flags routes |
| `act_autopilot/recommendations_engine.py` | Engine + flag engine |
| `act_lighthouse/features.py` | Feature engineering |
| `act_dashboard/templates/recommendations.html` | Main recommendations + flags tab |
| `act_dashboard/templates/campaigns.html` | Campaigns + flags subtab |
| `act_dashboard/templates/ad_groups.html` | Ad Groups + flags subtab |
| `act_dashboard/templates/keywords.html` | Keywords + flags subtab |
| `act_dashboard/templates/ads.html` | Ads + flags subtab |
| `act_dashboard/templates/shopping.html` | Shopping + flags subtab |
| `act_dashboard/static/css/recommendations.css` | All recommendation + flag styles |
| `scripts/fix_all_flag_conditions.py` | Fixed flag conditions (already run — do not re-run) |
| `docs/MASTER_KNOWLEDGE_BASE.md` | Primary project context |
| `docs/PROJECT_ROADMAP.md` | Full roadmap |

---

## LATEST COMMITS

| Commit | Description |
|--------|-------------|
| b8188fe | Chat 101: Add flags wireframe and brief — pre-build checkpoint |
| 61002f3 | Chats 99-100: Engine fixes — micros, rules 19/20, impression share, valid date query |
| 30decda | Chat 97: Recommendations UI fixes |
| 342c8d8 | Chat 93: Templates tab |

*(Final Chat 101 flags system commit to be added after git commit at end of this session)*

---

**Handoff complete. Master Chat 13.0 is ready to start.**
**First task: Keywords search terms fix (quick fix in Master Chat — upload keywords.py and fix line 187).**
