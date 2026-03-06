# MASTER KNOWLEDGE BASE - ADS CONTROL TOWER (A.C.T)

**Version:** 15.0
**Created:** 2026-02-19
**Updated:** 2026-03-06
**Purpose:** Complete project context for Master Chat coordination

---

## EXECUTIVE SUMMARY

### Current State (March 6, 2026)
- **Overall Completion:** ~99.9%
- **Phase:** Module 4 Dashboard Redesign ✅ COMPLETE | Cold Outreach System ✅ COMPLETE (6 pages) | Marketing Website ✅ COMPLETE
- **Active Development:** Ready for Website Design Upgrade + M9 Live Validation
- **Marketing Website:** Live at https://www.christopherhoole.online
- **Rules:** 41 total (13 campaign + 6 keyword + 4 ad_group + 4 ad + 14 shopping)
- **Recommendations:** 1,492 active (1,256 keywords + 126 shopping + 110 campaigns)
- **Outreach:** 6 pages complete (Leads, Queue, Sent, Replies, Templates, Analytics)

### Tech Stack

**A.C.T Dashboard:**
- **Backend:** Python 3.11, Flask
- **Database:** DuckDB (warehouse.duckdb + warehouse_readonly.duckdb)
- **API:** Google Ads API (v15)
- **Frontend:** Bootstrap 5.3, Chart.js 4.4, Vanilla JS, Flatpickr
- **Templating:** Jinja2 Macros (metrics_section M2 + performance_chart M3)

**Marketing Website:**
- **Framework:** Next.js 14
- **Styling:** Tailwind CSS
- **Animation:** Framer Motion
- **Components:** shadcn/ui
- **Hero:** Three.js WebGL (r128)
- **Hosting:** Vercel
- **Domain:** christopherhoole.online (GoDaddy DNS)

### Development Architecture (2-Tier — Current)

**As of March 3, 2026: Simplified from 3-tier to 2-tier.**

```
Master Chat (Claude Desktop App)
 → Creates simple task descriptions (2 pages max)

Claude Code (PowerShell Terminal)
 → Executes entire task autonomously
 → npx @anthropic-ai/claude-code from C:\Users\User\Desktop\gads-data-layer
```

**Old 3-tier architecture (archived):** Master Chat → Worker Chat → Claude Code. Eliminated due to handoff overhead.

**Claude Code handles:** file editing, testing, documentation, checkpoint reporting. No file uploads needed — reads codebase directly.

**Documentation:** CLAUDE_CODE_WORKFLOW.md is the authoritative workflow guide.

---

## COMPLETE CHAT HISTORY

### Phase 0: Foundation (Chats 1-17) ✅
- Chats 1-11: Flask app, DuckDB, auth, multi-client YAML
- Chat 12: Shopping module (14 rules, 4-tab UI, 3,800 lines)
- Chat 13.1: Constitution execution engine (safety guardrails, dry-run + live)
- Chat 14: Dashboard execution UI (buttons, toasts, change history)
- Chat 17: Architecture refactor — unified recommendation system

### Phase 1: Code Cleanup ✅
- 16/16 routes → 8 modular blueprints
- Input validation, rate limiting, logging, cache, error handling

### Phase 2: Polish ✅
- DRY helpers, type hints, config validation

### Chat 21: Dashboard UI Overhaul ✅
All 6 pages rebuilt with Bootstrap 5:
- 21a: Bootstrap foundation + base_bootstrap.html (commit 5789628)
- 21b: Main dashboard + Chart.js trend (commit 4976a29)
- 21c: Campaigns + Rule Visibility System (commit 3ab82a2)
- 21d: Keywords + QS distribution (commit f0fbd15)
- 21e: Ad Groups | 21f: Ads | 21g: Shopping (4 tabs) | 21h: Polish

Key outputs: base_bootstrap.html, rule_helpers.py, rules_sidebar/tab/card components

### Chat 22 — M1: Date Range Picker ✅
**Commits:** a644fdd + 25c7af5
- Flatpickr, session persistence, 7d/30d/90d presets + custom range

### Chat 23 — M2: Metrics Cards ✅
Jinja2 macro system on all 6 pages:
- Financial row (8 cards) + collapsible Actions row (8 cards)
- Sparklines + change % on date-range pages
- IS columns added: search_impression_share, search_top_impression_share, search_absolute_top_impression_share, click_share

Card layouts:
| Page | Financial (8) | Actions (8) |
|------|---------------|-------------|
| Dashboard/Campaigns/Ad Groups/Keywords | Cost\|Revenue\|ROAS\|Wasted Spend\|Conv\|CPA\|CVR\|blank | Impr\|Clicks\|CPC\|CTR\|Search IS\|Top IS\|Abs Top IS\|Click Share |
| Ads | Cost\|Revenue\|ROAS\|blank\|Conv\|CPA\|CVR\|blank | Impr\|Clicks\|CPC\|CTR\|Ad Strength\|blank x3 |
| Shopping (Campaigns) | Cost\|Conv Value\|ROAS\|blank\|Conv\|Cost/Conv\|CVR\|blank | Impr\|Clicks\|CPC\|CTR\|blank x4 |
| Shopping (Products) | Cost\|ROAS\|blank\|Out of Stock\|Conv\|blank x3 | Products\|Feed Issues\|blank x6 |

Invert colours (red when rising): Cost, Cost/Conv, Wasted Spend

### Chat 24 — M3: Chart Overhaul ✅
- Reusable performance_chart.html macro on all 6 pages
- Dual Y-axis, 4 toggleable metric slots, session-persisted selection

### Chat 25 — M4: Table Overhaul ✅
Full Google Ads column sets on all 5 entity pages, server-side sort, sticky first column.

### Chat 26 — M5: Card-Based Rules Tab ✅
**Commit:** 025986a

**Architecture — dual-layer (critical — do not break):**
- `act_autopilot/rules_config.json` — UI config layer (CRUD via rules_api.py)
- `act_autopilot/rules/*.py` — execution layer (untouched, Python functions only)

**rules_config.json data model:**
```
rule_id, rule_type, rule_number, display_name, name
scope (blanket/specific), campaign_id
condition_metric, condition_operator, condition_value, condition_unit
condition_2_metric, condition_2_operator, condition_2_value, condition_2_unit
action_direction, action_magnitude, risk_level, cooldown_days, enabled
monitoring_days, monitoring_minutes, created_at, updated_at
```

**rules_api.py routes:**
| Route | Method | Purpose |
|---|---|---|
| `/api/rules` | GET | Return all rules (supports ?rule_type= filter) |
| `/api/rules/add` | POST | Add rule |
| `/api/rules/<id>/update` | PUT | Edit rule |
| `/api/rules/<id>/toggle` | PUT | Toggle enabled |
| `/api/rules/<id>` | DELETE | Delete rule |
| `/api/campaigns-list` | GET | Campaign names from warehouse |

### Chat 27 — M6: Recommendations Engine + UI ✅
- recommendations table in warehouse.duckdb (19 cols)
- recommendations_engine.py: reads rules_config.json → evaluates campaign_features_daily → inserts pending recs
- Duplicate prevention on (campaign_id, rule_id)
- /recommendations/cards JSON endpoint
- Global /recommendations page + Campaigns → Recommendations tab

**Card anatomy (locked):**
1. 4px coloured top bar (blue=budget, green=bid, red=status)
2. Header: rule tag + campaign name + status pill
3. Change block FIRST (gradient bg by type)
4. Trigger block SECOND (grey bg, "Why this triggered")
5. Footer: confidence badge + source pill + age
6. Action buttons: Modify / Decline / Accept

**Status pills:** Pending=blue / Monitoring=purple / Successful=green / Reverted=red / Declined=grey

### Chat 28 — M7: Accept/Decline/Modify + 4-Tab UI ✅
- Accept/Decline/Modify POST routes — fully wired
- `changes` audit table created in warehouse.duckdb
- `monitoring_days: 0` added to all 13 rules
- 4-tab UI: Pending / Monitoring / Successful / Declined

### Chat 29 — M8: Changes + Radar Monitoring ✅
- `act_autopilot/radar.py` — background daemon thread (60s cycle)
- `act_dashboard/routes/changes.py` — new blueprint, /changes route
- `monitoring_minutes` field added to all 13 rules
- 5-tab UI (added Reverted tab)
- Changes page: My Actions card grid + System Changes table

**DuckDB pattern (established):** `duckdb.connect('warehouse.duckdb')` + `ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)`

**executed_by values:**
| Value | Meaning |
|---|---|
| `user_accept` | User clicked Accept |
| `user_modify` | User modified then accepted |
| `user_decline` | User clicked Decline |
| `radar_resolved` | Monitoring complete, KPI held |
| `radar_revert` | KPI degraded, auto-reverted |

### Chats 30a/30b — M9: Search Terms + Live Execution ✅
- Search Terms tab on Keywords page (16-column table)
- Negative keyword flagging: 3 criteria (0% CVR + ≥10 clicks, ≥£50 + 0 conv, CTR <1% + ≥20 impr)
- Live Google Ads API execution for negative keyword blocking
- Keyword expansion flagging (CVR ≥5%, ROAS ≥4.0x, Conv. ≥10)
- Dry-run mode for safe testing
- Changes table audit logging

### Marketing Website ✅
**Deployed:** https://www.christopherhoole.online | **Stack:** Next.js 14, Tailwind CSS, Framer Motion, Three.js
**11 sections:** Hero, About Me, The Problem, The Difference, Work History, Skills & Platforms, What A.C.T Does, Why I'm Different (16 USP cards), FAQ (10 questions), Contact Form, Footer

### Rules Creation Phase ✅ (Chats 41-46 — 41 rules complete)

#### Chat 41: Rules Tab Rollout (ead441b)
- Rules tab structure on Keywords, Ad Groups, Ads, Shopping pages
- rules_api.py extended with rule_type filtering

#### Chat 42: 6 Keyword Rules (d9d0b33 + 65b6986)
keyword_1–6: Pause High Cost, Increase Bid ROAS, Decrease Bid ROAS, Pause Low QS (2 conditions), Flag Low CTR, Flag High Impr Low Click

#### Chat 43: 4 Ad Group Rules (4a9cdbe)
ad_group_1–4: Pause High Cost, Increase/Decrease Bid ROAS, Flag Low CTR

#### Chat 44: 4 Ad Rules (52b042e)
ad_1–4: Pause High Cost, Flag Low CTR, Flag Poor Ad Strength, Flag Average Ad Strength
String comparison pattern: `condition_operator: "eq"` + `condition_value: "POOR"`

#### Chat 45: 14 Shopping Rules (86fc939)
shopping_1–14: Budget (3), ROAS Performance (3), Feed Errors (3), Out-of-Stock + IS (3), IS Budget + Opt Score (2)

**Master-Approved Thresholds:**
- ROAS: 4.5x (increase), 2.0x (decrease), 1.5x/1.0x (pause)
- Feed errors: 20 (flag), 50 (pause)
- IS: 30% (flag), 40% (budget increase)
- Out-of-stock: 5 products | Opt score: 60%

#### Chat 46: Rules Tab UI Components (0299845)
- ad_group_rules_tab.html, ad_rules_tab.html, shopping_rules_tab.html created
- Schema fix: new entities use condition_1_metric (not condition_metric like keywords)

### Multi-Entity Recommendations (Chats 47-49) ✅

#### Chat 47 (75becfb): Engine Extension
- Extended from campaign-only to 4 entity types
- +3 columns to recommendations table (entity_type, entity_id, entity_name)
- +2 columns to changes table
- 1,492 recommendations: 1,256 keywords + 126 shopping + 110 campaigns
- 26/26 tests passed

#### Chat 48 (c7a4017): Global Page Entity Filtering
- Entity type filter dropdown (All/Campaigns/Keywords/Shopping/Ad Groups)
- Color-coded badges: Campaign=blue, Keyword=green, Shopping=cyan, Ad Group=orange
- get_action_label() Jinja2 filter for entity-aware action labels

#### Chat 49 (85dc3aa): Entity-Specific Pages
- Recommendations tabs on Keywords, Shopping, Ad Groups, Ads pages
- Keywords: 1,256 recs, Load More (20/load), purple badges
- Shopping: 126 recs, cyan badges
- Ad Groups: Empty state + Run button, orange badges
- Ads: Warning empty state (table missing), no Run button
- Critical fixes: limit=200→5000, CSRF exemptions for Accept/Decline

### Module 4: Dashboard Design Upgrade (Chats 57-58) ✅
**Date:** 2026-03-03 | **Commits:** 6f9fafa, 0bcee06, ef93abc, 86e01ed, 72407bf

Google Ads-style table redesign across all 5 entity pages.

**Features across all pages:**
- Control bar: All/Enabled/Paused filter tabs, rows per page selector, Create/Columns buttons
- Column selector modal: 3 sections (Default always visible, Performance toggleable, Additional hidden)
- Session-based column persistence via /[entity]/save-columns endpoints
- Status dots: Green (enabled) / Grey (paused) — no more badges
- ROAS color coding: Green ≥4.0x / Yellow 2.0–4.0x / Red <2.0x
- Opt. score progress bars: Green ≥80% / Yellow 60–80% / Red <60%
- Actions menus: entity-specific dropdown options
- Pagination: Previous / page numbers / Next
- Shared CSS: table-styles.css

**Column specs (visible / hidden):**
| Page | Visible | Hidden |
|---|---|---|
| Campaigns | 15 | 11 |
| Ad Groups | 15 (incl. Opt. score) | 11 |
| Ads | 17 | 6 |
| Keywords | 16 | 15 |
| Shopping | 14 | 11 |

**Files modified:** 5 templates, 5 routes, 1 shared CSS (~2,500 lines total)

### Cold Outreach System (Chats 59-64) ✅
**Date:** 2026-03-03 to 2026-03-06 | **Commits:** d524448, c0e0eb8, 194ef2c

Full cold outreach platform built into A.C.T dashboard. 6 pages under `/outreach/` blueprint.

**Database tables (warehouse.duckdb):**
- `leads` — prospect records (name, company, role, email, track, status, source)
- `email_queue` — scheduled emails with send_at, template_step, status
- `sent_emails` — sent email log with open_count, click_count, cv_open_count integer columns
- `email_replies` — reply tracking with unread flag, read_at timestamp
- `email_templates` — template content per step (Step 1–4) per track

**Track types:** Agency, Recruiter, Direct, Job

**6 Pages:**

**Leads** (`/outreach/leads`): Lead list with status management, add/edit modal, track assignment, status pills (New/Contacted/Replied/Meeting/Won/Lost)

**Queue** (`/outreach/queue`): Email queue management, scheduled sends, preview modal, send/cancel actions

**Sent** (`/outreach/sent`): Sent email log, open/click tracking display, CV open tracking

**Replies** (`/outreach/replies`):
- 5-stat header (Total/Unread/Replied/Meeting/Won)
- Reply cards with unread styling (blue left border)
- Slide-out panel for full reply view + status management
- Real-time unread count decrement
- Commit: d524448

**Templates** (`/outreach/templates`):
- Attachments card with CV placeholders
- Sequence flow diagram (4-step visual)
- 2×2 template grid per track
- Edit modal with variable chips ({{first_name}}, {{company}}, etc.)
- Jinja/JS brace conflict resolved: use `'{' + '{'` splitting in JS
- Commit: c0e0eb8

**Analytics** (`/outreach/analytics`):
- 8 KPI cards: sent, opened, clicked, CV opens, replies, meetings, warm leads, avg reply days (with prev-period deltas)
- Engagement funnel (6 steps: leads → sent → opened → clicked → replied → meeting)
- Daily activity chart (4 series), reply rate by day-of-week chart
- Performance by track table (Agency/Recruiter/Direct/Job) with N · X% + colored progress bars
- Performance by template step table with reply% color-coded by tier
- 3 bottom charts: emails by DOW, status distribution donut, link clicks donut
- ?days= filter (7/14/30/90, default 30)
- Commit: 194ef2c

**Key bugs fixed during outreach build:**
1. opened/clicked showing 0 — root cause: route used `opened_at IS NOT NULL` (timestamp column never written by seed). Fix: use `open_count > 0` / `click_count > 0` (integer columns). Seed: tools/seed_outreach_clicks.py
2. Client selector auto-switching — root cause: `current_client_path = get_current_config()` returns DashboardConfig object, string comparison always False. Fix: `session.get("current_client_config")` to match all other routes.
3. Duplicate Flask processes causing port conflicts — fix: `taskkill /IM python.exe /F` before starting
4. Worktrees causing git issues — fix: added to .gitignore

**CSS:** 175 lines added to outreach.css with `an-` prefix classes for analytics page

---

## CURRENT STATUS

### Overall: ~99.9% Complete

**What's Working:**
- All 6 dashboard pages (Dashboard, Campaigns, Ad Groups, Keywords, Ads, Shopping)
- Module 4 Google Ads-style tables on all 5 entity pages
- 41 optimization rules across 5 entity types
- 1,492 active recommendations (1,256 keywords + 126 shopping + 110 campaigns)
- Multi-entity recommendations system (campaigns, keywords, shopping)
- Entity-specific recommendations tabs on all 4 pages
- Global recommendations page with entity filtering
- Accept/Decline/Modify operations for all entity types
- Radar monitoring and automatic rollback
- Changes audit trail (My Actions + System Changes)
- Search Terms tab with live negative keyword blocking + keyword expansion
- Rules Tab UI on all pages
- Cold Outreach System — 6 pages complete (Leads/Queue/Sent/Replies/Templates/Analytics)
- Marketing website live (christopherhoole.online)
- M1–M9 Dashboard 3.0 features complete

**What's Partially Working:**
- Ad Groups: 4 rules enabled but 0 recommendations (conditions not met with current data)
- Ads: 4 rules blocked (analytics.ad_daily table missing)
- Outreach email sending: DB-only (no live SMTP/SendGrid yet)
- Outreach open/click tracking: integer columns populated but no tracking pixel yet
- Outreach CV attachment: placeholder toasts, no real file management yet

**Next Priorities:**
1. Website Design Upgrade (christopherhoole.online — scope TBD)
2. M9 Live Validation (real Google Ads account testing)
3. Website contact form backend (Google Sheets integration)
4. Outreach: Live email sending (SMTP/SendGrid)
5. Outreach: CV upload/replace (real file management)
6. Outreach: Open/click tracking (pixel + redirect endpoints)
7. Outreach: Apollo.io data partner integration
8. Testing & Polish (comprehensive post-redesign)

---

## KNOWN PITFALLS (Quick Reference)

| Problem | Fix |
|---------|-----|
| Template CSS missing | Must extend base_bootstrap.html, not base.html |
| DB query fails | Use ro.analytics.* not analytics.* |
| Route replacement fails | Match exact quote style of @bp.route decorator |
| Shopping metrics missing | Add total_clicks to compute_campaign_metrics() |
| Collapse state lost | POST to /set-metrics-collapse |
| Rules showing 0 | Use r'_\d{3}(?:_|$)' regex |
| Ad group table empty | Use cpc_bid_micros not bid_micros |
| Sort not working on full dataset | Must be SQL-side ORDER BY, not Python-side |
| New sort column not working | Add to ALLOWED_*_SORT whitelist in route |
| Jinja template 500 error | Validate with jinja2 Environment before deploying |
| rules_config.json not found | Path needs `.parent.parent.parent` — routes/ is 3 levels from project root |
| Drawer visible on page load | Remove flex from inline style, let JS add it |
| Blueprint not registered | New blueprints MUST be added to __init__.py |
| Radar "ro catalog does not exist" | Must ATTACH warehouse_readonly.duckdb in radar connection |
| Radar read-write conflict | Never open warehouse.duckdb with read_only=True if writes needed |
| changes JOIN to recommendations | No recommendation_id — use campaign_id + rule_id + QUALIFY |
| **Website:** Three.js colorSpace error | Remove t.colorSpace line for r128 compatibility |
| **Website:** www works but root doesn't | Root A record takes longer to propagate (5-60 min) |
| **Recommendations:** Backend limit=200 truncates | Increase to 5000+ for high-volume entities |
| **Recommendations:** CSRF 400 on Accept/Decline | Add csrf.exempt() to routes in app.py |
| **Rules Tab UI:** Generic component include | Each page needs specific component (ad_group_rules_tab.html etc.) |
| **Rules Tab UI:** Schema field mismatch | Keywords use condition_metric, others use condition_1_metric |
| **Outreach:** opened/clicked showing 0 | Use open_count > 0 (integer), not opened_at IS NOT NULL (timestamp never written) |
| **Outreach:** Client selector switching on load | Use session.get("current_client_config") not get_current_config() (returns object) |
| **Outreach:** Jinja/JS brace conflict | In JS inside Jinja template, split: `'{' + '{'` instead of `{{` |
| **Outreach:** Duplicate Flask process | Run `taskkill /IM python.exe /F` before starting Flask |
| **Flask:** Port already in use | Kill all python.exe processes, fresh PowerShell |

**See KNOWN_PITFALLS.md for full detail with code examples.**

---

## LESSONS LEARNED (Key Points)

1. Always extend base_bootstrap.html (never base.html)
2. Always use ro.analytics.* prefix for read queries
3. Request current file before editing — never cached
4. DuckDB Radar pattern: connect(warehouse.duckdb) + ATTACH warehouse_readonly as ro
5. Dual-layer architecture: JSON config (UI) and Python functions (execution) must stay separate
6. Dry-run first: check flag BEFORE loading Google Ads client
7. Backend query limits must match data volume (limit=200 truncated Keywords recs)
8. CSRF exemptions needed for JSON API routes called from JavaScript
9. Each entity page needs specific component include (not generic rules_tab.html)
10. Schema divergence: Keywords use condition_metric, newer entities use condition_1_metric
11. Jinja/JS brace conflict: split `{{` as `'{' + '{'` in JavaScript inside Jinja templates
12. Session consistency: always use session.get("key") not helper functions returning objects
13. Integer columns (open_count) vs timestamp columns (opened_at) — seed scripts may not populate timestamps
14. taskkill /IM python.exe /F to clear stuck Flask processes
15. Load More pattern for >100 items prevents UI overload

**See LESSONS_LEARNED.md for all 56 lessons with context.**

---

**Version:** 15.0 | **Last Updated:** 2026-03-06
**Architecture:** 2-Tier (Master Chat → Claude Code)
**Next Step:** Website Design Upgrade + M9 Live Validation
