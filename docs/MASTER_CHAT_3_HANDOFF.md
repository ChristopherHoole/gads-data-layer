# MASTER CHAT 3.0 — FULL HANDOFF DOCUMENT

**Created:** 2026-02-22  
**Handed off from:** Master Chat 2.0  
**Reason for handoff:** Image attachment limit (100) reached in Master Chat 2.0  
**Git state:** Commit 025986a (Chat 26 complete, pushed to main)  
**Overall completion:** ~92%

---

## 🚨 CRITICAL: READ THIS BEFORE ANYTHING ELSE

This is the coordination chat for the Ads Control Tower (A.C.T) project. You are **Master Chat 3.0**. Your job is to:
- Coordinate worker chats (never build — always delegate)
- Review 5 diagnostic questions from workers and provide answers
- Review and approve worker build plans before implementation starts
- Review handoff documents and approve git commits
- Update project docs after each chat

You NEVER write code yourself. You assign tasks to worker chats and review their outputs.

---

## 📁 PROJECT IDENTITY

**Project Name:** Ads Control Tower (A.C.T)  
**Purpose:** Automated Google Ads optimisation platform — generates, approves, and executes bid/budget recommendations with safety guardrails  
**Codebase location:** `C:\Users\User\Desktop\gads-data-layer`  
**Git repo:** Pushed to GitHub, branch: main  
**Browser for testing:** Opera (fallback: Chrome)

**Customer IDs:**
- Real: 7372844356
- Test/Synthetic: 9999999999

---

## 💻 TECHNICAL STACK

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Flask |
| Database | DuckDB (warehouse.duckdb) |
| API | Google Ads API v15 |
| Frontend | Bootstrap 5.3 (NOT Tailwind), Chart.js 4.4, Vanilla JS, Flatpickr |
| Templating | Jinja2 Macros |
| Tools | PowerShell, Git, Virtual env (.venv) |

**Start the dashboard:**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python -m act_dashboard.app configs/client_synthetic.yaml
```

---

## 🏗️ SYSTEM ARCHITECTURE

```
gads-data-layer/
├── act_dashboard/
│   ├── app.py
│   ├── warehouse_duckdb.py
│   ├── routes/
│   │   ├── shared.py              ← get_metrics_collapsed, get_date_range
│   │   ├── dashboard.py
│   │   ├── campaigns.py           ← MODIFIED Chat 26 (Rules tab + Recommendations tab)
│   │   ├── ad_groups.py
│   │   ├── keywords.py
│   │   ├── ads.py
│   │   └── shopping.py
│   └── templates/
│       ├── base_bootstrap.html    ← ALWAYS USE THIS (never base.html)
│       ├── macros/
│       │   ├── metrics_cards.html ← M2 macro
│       │   └── performance_chart.html ← M3 macro
│       ├── components/
│       │   ├── rules_sidebar.html
│       │   ├── rules_tab.html     ← REPLACED Chat 26 with card-based UI
│       │   └── rules_card.html
│       └── campaigns.html         ← MODIFIED Chat 26 (3-tab layout)
├── rules_config.json              ← NEW Chat 26 (13 rules, UI config layer)
├── rules_api.py                   ← NEW Chat 26 (CRUD API + /api/campaigns-list)
├── src/act_autopilot/
│   ├── executor.py
│   └── constitution.py
├── warehouse.duckdb
├── warehouse_readonly.duckdb
├── tools/testing/
│   └── generate_synthetic_shopping_v2.py
└── docs/
    ├── PROJECT_ROADMAP.md
    ├── DASHBOARD_PROJECT_PLAN.md
    ├── MASTER_KNOWLEDGE_BASE.md
    ├── CHAT_WORKING_RULES.md
    └── [chat handoff docs]
```

---

## ✅ COMPLETED WORK (full history)

### Phase 0: Foundation (Chats 1-17) ✅
- Flask app, DuckDB, auth, multi-client YAML config
- Shopping module (14 rules), execution engine, change history
- Constitution safety framework, dry-run + live execution
- Architecture refactor — unified recommendation system

### Phase 1: Code Cleanup ✅
- 16/16 routes → 8 modular blueprints
- Input validation, rate limiting, logging, cache expiration, error handling

### Phase 2: Polish ✅
- DRY helpers, type hints, config validation

### Chat 21: Dashboard UI Overhaul ✅
All 6 pages rebuilt with Bootstrap 5. Key outputs:
- base_bootstrap.html (master template — ALWAYS extend this)
- rule_helpers.py — rule extraction engine
- rules_sidebar.html, rules_tab.html, rules_card.html — Rule Visibility System
- Dynamic category detection regex: `r'_\d{3}(?:_|$)'`

### Chat 22 — M1: Date Range Picker ✅
- Flatpickr replacing URL-parameter system
- Session-based persistence across all 6 pages
- Preset (7d/30d/90d) + custom date range
- Commits: a644fdd + 25c7af5

### Chat 23 — M2: Metrics Cards ✅
- Jinja2 macro system (metrics_section) on all 6 pages
- Financial row (8 cards) + collapsible Actions row (8 cards)
- Sparklines + change % vs prior period on date-range pages
- IS metrics added to schema (4 new columns)
- 17 files modified

### Chat 24 — M3: Chart Overhaul ✅
- Reusable performance_chart.html Jinja2 macro on all 6 pages
- Dual Y-axis, 4 toggleable metrics, session-persisted
- Default active: Cost + Clicks
- 10 files modified

### Chat 25 — M4: Table Overhaul ✅
- Full Google Ads UI column sets on all 5 pages (24/26/17/24/24 cols)
- Server-side sort (SQL ORDER BY) on all sortable columns
- CSS sticky first column on all pages
- ALLOWED_*_SORT whitelists prevent SQL injection
- Shopping migrated to ro.analytics.shopping_campaign_daily
- 16 files modified | Commit: pending (was pending at handoff)

### Chat 26 — M5: Rules Section Upgrade ✅
**Commit: 025986a (PUSHED)**

**Architecture — dual-layer design:**
- `rules_config.json` = UI configuration layer (13 rules, full CRUD via API)
- Python execution functions in act_autopilot = UNTOUCHED (safe)
- All rule changes via JSON config only — zero risk to execution engine

**What was built:**
- `rules_config.json` — 13 rules with 18 fields each (name, description, enabled, conditions, action, limits, cooldown, data_sufficiency, tags, priority, campaigns)
- `rules_api.py` — full CRUD API (GET/POST/PUT/DELETE rules, GET /api/campaigns-list)
- `act_dashboard/routes/campaigns.py` — extended with rules API endpoints + /api/campaigns-list
- `campaigns.html` — 3-tab layout (Campaigns | Rules | Recommendations placeholder)
- `rules_tab.html` — completely replaced with card-based UI

**Card design (Rules tab):**
- Grid layout, 4px coloured top bar (blue=budget, green=bid, red=status)
- Inline SVG icons (no CDN dependencies)
- "Budget 1", "Bid 1", "Status 1" naming convention
- Toggle switch (enabled/disabled)
- Edit drawer (slides in from right, full CRUD)
- Campaign picker in drawer (multi-select with search)
- Rules are named "Budget 1", "Budget 2" etc. (not "budget_001")

**CRUD tests passed (all 7):**
1. ✅ Create new rule
2. ✅ Edit existing rule
3. ✅ Toggle enable/disable
4. ✅ Delete rule
5. ✅ Campaign picker populates
6. ✅ Rules persist after page reload
7. ✅ API returns correct JSON

**Bugs fixed in Chat 26:**
- "budget budget" double word in card header (display name collision)
- Drawer visible on load (CSS z-index fix)
- Path resolution error (.parent.parent.parent — was .parent.parent)
- Campaign picker empty (wired to /api/campaigns-list endpoint)

**Known states (expected, not bugs):**
- Recommendations tab = placeholder only (Chat 27 scope)
- Python execution functions not yet connected to rules_config.json (Chat 28+ scope)

---

## 📊 DATABASE SCHEMA (current state post-Chat 25)

**CRITICAL: Always use `ro.analytics.*` prefix in dashboard queries**

| Table | Rows | Cols | Notes |
|-------|------|------|-------|
| analytics.campaign_daily | 7,300 | 21 | + IS cols (Chat 23) + opt_score/bid_strategy (Chat 25) |
| analytics.ad_group_daily | 23,725 | 30 | VIEW over snap_ad_group_daily |
| analytics.keyword_daily | 77,368 | 33 | Routes use keyword_features_daily (windowed) |
| analytics.ad_features_daily | 983 | 51 | ad_daily does NOT exist — use this |
| analytics.shopping_campaign_daily | 7,300 | 26 | Migrated Chat 25 |
| analytics.change_log | — | — | Audit trail |

**Known expected states (not bugs):**
- All Conv. columns show `—` — all_conversions pipeline not built yet
- Shopping IS/Opt. Score/Click Share show `—` — NULL, pending real data
- Ads Revenue $0.00 — ads-level revenue not aggregated yet

---

## 🔒 CONSTITUTION FRAMEWORK (safety guardrails)

All automated changes must pass:
- Min 10 conversions (30d) for bid changes
- Max 30% budget increase, 20% bid change per execution
- 7-day cooldown between changes on same entity
- Protected entities: brand campaigns immutable by default
- Data sufficiency thresholds before any rule fires

---

## 📋 DASHBOARD 3.0 MODULE STATUS

| Module | Chat | Status |
|--------|------|--------|
| M1: Date Range Picker | 22 | ✅ COMPLETE |
| M2: Metrics Cards | 23 | ✅ COMPLETE |
| M3: Chart Overhaul | 24 | ✅ COMPLETE |
| M4: Table Overhaul | 25 | ✅ COMPLETE |
| M5: Rules Section Upgrade | 26 | ✅ COMPLETE |
| M6: Recommendations | 27 | 🎯 NEXT |
| M7: Changes + Monitoring | 28 (TBD) | 📋 PLANNED |
| M8: Accept/Decline/Modify | 29 (TBD) | 📋 PLANNED |

---

## 🎯 IMMEDIATE NEXT TASK: Chat 27 — M6 Recommendations

### What M6 builds:
A full Recommendations system — the heart of A.C.T. Rules fire → recommendations are generated → user approves/declines → changes execute → outcomes are monitored → successful changes stay, failed ones auto-revert.

### Wireframe: M6_WIREFRAME_v5.html
The wireframe went through 5 iterations in Master Chat 2.0. v5 is the approved design. Christopher needs to visually confirm v5 looks correct before the brief is written (screenshot limit was hit before he could confirm v5).

**Action for Master Chat 3.0:** Ask Christopher to open `M6_WIREFRAME_v5.html` (in outputs from previous chat, or rebuild from the spec below) and confirm it looks right before writing Chat 27 brief.

### M6 Architecture (agreed in Master Chat 2.0):

**Storage:** DuckDB table (not JSON) — recommendations are timestamped data per campaign/rule

**Scope of Chat 27:** Campaign-level rules only (matching the 13 rules in rules_config.json)

**What Chat 27 builds:**
1. Recommendations engine — reads rules_config.json, evaluates against warehouse data, generates recommendations, stores in DuckDB
2. Per-page Recommendations tab on Campaigns page (replaces placeholder from Chat 26)
3. Global Recommendations page (replaces basic /recommendations page)
4. Manual "Run Recommendations Now" button
5. Recommendation cards — display only (Accept/Decline/Modify = placeholders, Chat 28 wires them)

### M6 Card Design (approved):

**Card anatomy (order matters):**
1. 4px coloured top bar (blue=budget, green=bid, red=status)
2. Header: rule tag + campaign name + status pill (Pending/Monitoring/etc.)
3. **Change block FIRST** (what will happen: e.g. "Increase daily budget by 10%, £450→£495, 7-day cooldown")
4. **Trigger block SECOND** (why it fired: e.g. "ROAS (7d) 6.2x > target × 1.15")
5. Footer row 1: confidence badge + source pill + age + "Buttons active in Chat 28" note
6. Footer row 2: Modify / Decline / Accept buttons (full width, Chat 28 placeholder)

**Status pill colours:**
- Pending: blue
- Monitoring: purple
- Successful: green
- Reverted: red
- Declined: grey

### M6 Page Structure (approved):

**Global Recommendations page (sidebar nav → Recommendations):**
- Summary strip: Pending count / Monitoring count / Success rate % / Last run time
- 3 tabs: Pending | Monitoring | History
- Pending tab: 2-col card grid + filter bar (All/Budget/Bid/Status) + "Run Recommendations Now" button
- Monitoring tab: 2-col card grid, each card shows progress bar (Day X of Y) + two outcome pills ("ROAS holds → kept in place" / "ROAS drops → auto-reverted")
- History tab: full table (Date / Rule / Campaign / Change Applied / Outcome / Result) + success rate banner + filter bar

**Per-page Recommendations tab (Campaigns → Recommendations tab):**
- Two labelled sections: Pending (blue left border) + Monitoring (purple left border)
- Same 2-col card grid as global
- "View full history →" link to global History tab
- "Run Recommendations Now" button

### M6 Lifecycle (fully agreed):

```
Rule fires → Recommendation generated (Pending)
     ↓
User accepts → Change executed → Monitoring starts (Day X of Y)
     ↓                               ↓
(Declined → logged)          Metric holds? → Successful (kept in place)
                             Metric drops? → Reverted (auto-reverted)
```

Monitoring periods: 7 days for budget rules, 14 days for bid rules

### M6 History view:
- Full table — every recommendation ever (pending/accepted/declined/successful/reverted)
- Success rate banner: "75% success rate (30d) — 9 of 12 accepted recommendations were successful"
- Filter: All / Successful / Reverted / Declined / Monitoring

---

## ⚠️ CRITICAL LESSONS LEARNED (NEVER REPEAT THESE)

| Problem | Fix |
|---------|-----|
| Wrong base template | ALWAYS extend `base_bootstrap.html` — NEVER `base.html` |
| DB prefix missing | ALWAYS use `ro.analytics.*` — never `analytics.*` alone |
| Flask routing broken silently | NEVER insert helper functions between `@bp.route` decorator and `def` — they must be adjacent |
| Cached file edits | ALWAYS request current file upload before editing — never use ZIP version |
| Partial file paths | ALWAYS use full Windows paths: `C:\Users\User\Desktop\gads-data-layer\...` |
| ad_daily table | Does NOT exist — use `ad_features_daily` |
| Sort not working | Must be SQL-side ORDER BY — not Python-side sort |
| New sort column missing | Must add to ALLOWED_*_SORT whitelist in route |
| Jinja 500 error | Validate before deploying: `python3 -c "from jinja2 import Environment, FileSystemLoader; env = Environment(loader=FileSystemLoader('.')); env.get_template('x.html'); print('OK')"` |
| Generator not found | They live in `tools/testing/` — not `scripts/` |
| sed replacing CSS definitions | Use Python string replace targeting `class="..."` attributes only |
| Rules drawer visible on load | CSS: drawer default z-index / transform must hide it |
| Path resolution error | rules_api.py needs `.parent.parent.parent` not `.parent.parent` |

---

## 📝 PROCESS RULES (MANDATORY — all worker chats)

### Rule 1: 3 Mandatory Uploads at Start of Every Worker Chat
Before ANY work, worker must request:
1. Codebase ZIP: `C:\Users\User\Desktop\gads-data-layer`
2. `C:\Users\User\Desktop\gads-data-layer\docs\PROJECT_ROADMAP.md`
3. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_WORKING_RULES.md`

### Rule 2: Always Request Current File Before Editing
Never use cached/ZIP versions. Always request upload of current file first.

### Rule 3: Full Windows Paths Only
CORRECT: `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\campaigns.py`
WRONG: `routes/campaigns.py`

### Rule 4: 5 Questions → Build Plan → Implement (in that order)
Worker sends exactly 5 diagnostic questions → Master answers → Worker writes build plan → Master approves → Worker implements. No exceptions.

### Rule 5: Complete files only (no code snippets)
All deliverables as downloadable files. Never paste code in chat.

### Rule 6: Test before reporting complete
All work must be tested and confirmed working before the worker declares it done.

### Rule 7: Handoff docs required
Every chat must produce a handoff document and detailed summary before git commit.

---

## 📦 PROJECT DOCS TO KEEP UPDATED

After every chat completion, Master Chat must update these 4 files and upload to project:

| File | Location |
|------|----------|
| PROJECT_ROADMAP.md | `C:\Users\User\Desktop\gads-data-layer\docs\PROJECT_ROADMAP.md` |
| DASHBOARD_PROJECT_PLAN.md | `C:\Users\User\Desktop\gads-data-layer\docs\DASHBOARD_PROJECT_PLAN.md` |
| MASTER_KNOWLEDGE_BASE.md | `C:\Users\User\Desktop\gads-data-layer\docs\MASTER_KNOWLEDGE_BASE.md` |
| CHAT_WORKING_RULES.md | `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_WORKING_RULES.md` |

---

## 🔄 GIT STATE

**Last commit:** 025986a  
**Message:** Chat 26 (M5): Card-based Rules Tab + Rules API  
**Status:** Pushed to main ✅  
**Files in commit (32 changed):**
- CREATE: rules_config.json, rules_api.py, CHAT_26_BRIEF.md, CHAT_26_DETAILED_SUMMARY.md, CHAT_26_HANDOFF.md, M5_WIREFRAME_v3.html
- MODIFY: __init__.py, campaigns.py, campaigns.html, rules_tab.html, ad_groups.py, ads.py, keywords.py, shopping.py + 4 generator files + 3 doc files
- DELETE: act_dashboard.zip (cleanup)

**Git workflow for future commits:**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
git add .
git commit -m "Chat XX (MX): [Description]"
git push origin main
```

---

## 🎯 MASTER CHAT 3.0 FIRST ACTIONS

1. Acknowledge you are Master Chat 3.0 and have read this document
2. Ask Christopher to confirm M6_WIREFRAME_v5.html looks correct (screenshot it)
3. If v5 is approved → write Chat 27 brief
4. If v5 needs changes → iterate wireframe first, then write brief

### Chat 27 Brief scope (when ready to write):
- Engine: reads rules_config.json → evaluates campaigns → generates recommendations → stores in DuckDB
- UI: Global Recommendations page (3 tabs) + Campaigns Recommendations tab
- Cards: display only — Accept/Decline/Modify wired in Chat 28
- Button label: "Run Recommendations Now" (not "Run Rules Now")
- Monitoring lifecycle must be visible on cards
- History table with success rate tracking

---

## 📊 FUTURE ROADMAP (after M6)

| Chat | Module | Description |
|------|--------|-------------|
| 27 | M6 | Recommendations engine + UI (display only) |
| 28 | M7 | Accept/Decline/Modify wiring + execution |
| 29 | M8 | Changes log + Monitoring page |
| 30 | M9 | Search Terms / Keywords recommendations |
| TBD | Phase 5 | Unit tests, job queue, DB indexes, CSRF |
| TBD | — | Email Reports, Smart Alerts |
| TBD | — | Onboarding Wizard, Documentation |

---

**End of Master Chat 3.0 Handoff Document**  
**Created by:** Master Chat 2.0  
**Date:** 2026-02-22  
**Git state:** 025986a — M5 complete, M6 next
