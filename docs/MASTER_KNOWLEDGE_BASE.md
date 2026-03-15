# MASTER KNOWLEDGE BASE - ADS CONTROL TOWER (A.C.T)

**Version:** 19.0
**Created:** 2026-02-19
**Updated:** 2026-03-15
**Purpose:** Complete project context for Master Chat coordination

---

## EXECUTIVE SUMMARY

### Current State (March 15, 2026)
- **Overall Completion:** ~99.9%
- **Phase:** Rules & Templates complete — Rules strategic review next
- **Active Development:** Master Chat 12
- **Primary Website:** https://christopherhoole.com (always use this — never christopherhoole.online)
- **Email:** chris@christopherhoole.com (Google Workspace, live, DKIM/SPF authenticated)
- **Rules:** 24 campaign rules (18 Budget, 6 Bid) — all enabled
- **Flags:** 30 campaign flags (16 Performance, 8 Anomaly, 6 Technical) — all enabled
- **Templates:** 0 (clean slate — create via bookmark button on any rule/flag row)
- **Total DB rows:** 54
- **Recommendations:** 1,515 active (1,256 keywords + 126 shopping + 110 campaigns + 23 ads)
- **Tests:** 620 tests, 80% coverage
- **Background jobs:** Celery + Redis (Chat 90)

### Tech Stack

**A.C.T Dashboard:**
- **Backend:** Python 3.11, Flask
- **Database:** DuckDB (warehouse.duckdb + warehouse_readonly.duckdb)
- **API:** Google Ads API (v15) — Explorer Access (upgraded March 2026), Basic Access pending
- **Frontend:** Bootstrap 5.3, Chart.js 4.4, Vanilla JS
- **Templating:** Jinja2 Macros (metrics_section M2 + performance_chart M3)
- **Date Picker:** Custom Google Ads-style dropdown (Chat 79, datepicker.css)
- **Email:** Gmail SMTP (chris@christopherhoole.com, port 587 TLS, App Password)
- **Background Jobs:** Celery 5.6.2 + Redis (Memurai on Windows) — see docs/CELERY_STARTUP.md
- **Tests:** pytest + pytest-cov, 620 tests, 80% coverage

**Marketing Website:**
- **Framework:** Next.js 14, Tailwind CSS, Framer Motion, shadcn/ui
- **Hero:** Three.js WebGL (r128)
- **Hosting:** Vercel
- **Domain:** christopherhoole.com (primary)

### Development Architecture (2-Tier — Current)

```
Master Chat (claude.ai)
 → Quick fixes done directly here (file upload → edit → download)
 → Large builds: creates concise task briefs as downloadable files to /docs/

Claude Code (Code tab in Claude Desktop App)
 → Executes large builds autonomously
 → Reads codebase directly — no file uploads needed
```

**Brief delivery rule:** Always save briefs as downloadable files to `/docs/` — never inline in chat.

---

## COMPLETE CHAT HISTORY

### Phase 0: Foundation (Chats 1-17) ✅
- Chats 1-11: Flask app, DuckDB, auth, multi-client YAML
- Chat 12: Shopping module
- Chat 13.1: Constitution execution engine
- Chat 14: Dashboard execution UI
- Chat 17: Architecture refactor

### Phase 1-2: Code Cleanup + Polish ✅
- 16/16 routes → 8 modular blueprints, DRY helpers, type hints

### Chat 21: Dashboard UI Overhaul ✅
All 6 pages rebuilt with Bootstrap 5

### Chats 22-30b: Dashboard M1-M9 ✅
Date picker, metrics cards, charts, tables, rules, recommendations, accept/decline, changes, search terms

### Marketing Website ✅
christopherhoole.com — Next.js 14, Tailwind, Framer Motion, Three.js

### Chats 84-87: Website + CV Polish ✅
CV download, SEO (PageSpeed 83/76), WhatsApp button, LinkedIn URL fix, Insight Tag

### Chats 41-49: Rules + Recommendations ✅
57 rules/flags seeded, multi-entity recommendations (1,515 active)

### Chats 57-58: Dashboard Design Upgrade ✅
Google Ads-style tables, column selector, table-styles.css

### Chats 59-64: Cold Outreach System — UI ✅
6 pages: Leads, Queue, Sent, Replies, Templates, Analytics

### Chat 65: Google Sheets → A.C.T Sync ✅
### Chat 66: Add Client Modal + Config Validator ✅
### Chat 67: Real Data Ingestion Pipeline ✅ (blocked on API)
### Chat 68: Live Email Sending ✅

### Chats 69-80: Outreach Functions + UI Polish ✅
Email signature, CV upload/attach, tracking pixels, reply polling, send reply, edit email, switch template, queue scheduler, Google Ads date picker, remove rules slidein

### Chats 81-83: UI Cleanup ✅
table-styles.css layout fix, duplicate client selector, navbar text, rules card removed

### Chat 88: ad_daily Table + Database Indexes ✅
**Commit:** 088317d — 23 Ad recs now generating (was 0)

### Chat 89: Unit Tests (pytest 80%+) ✅
**Commit:** 51e79c6 — 620 tests, 0 failures, 80% coverage

### Chat 90: Celery + Redis Background Job Queue ✅
**Commit:** a932ee7 — daemon threads replaced with Celery tasks

### Chat 91: Rules & Flags UI Overhaul ✅
**Commits:** 86d0eb6, 4bae83d
- `rules_flow_builder.html` — 5-step modal, full condition/action dropdowns, sidebar, all 38 metrics
- `rules_flags_tab.html` — Rules table, Flags table with direction labels, plain English, condition text, badge colours
- `rules.css` — complete styling
- Fixed: unescaped apostrophes in JS strings, schema dual-handling (op/ref + operator/unit)

### Chat 92: Impression Share Pipeline + Metric Map ✅
**Commit:** 060fe2a
- `act_lighthouse/features.py` — `impression_share_lost_rank` column added
- `scripts/add_impression_share_col.py` — migration
- `act_autopilot/recommendations_engine.py` — CAMPAIGN_METRIC_MAP 9 → 38 entries

### Chat 93: Templates Tab ✅
**Commit:** 342c8d8
- `scripts/add_is_template_col.py` — `is_template BOOLEAN DEFAULT FALSE` column
- `act_dashboard/routes/campaigns.py` — save-as-template route, duplicate detection
- `rules_flags_tab.html` — Templates table, bookmark buttons, Edit template button
- `rules_flow_builder.html` — Edit/Use template flow, Save template button, template name label
- **DB cleaned:** 54 total rows (removed test duplicates)
- **Key fixes:** conn open order, json_extract_string, state var reset order, rfEditTemplate function

### Google Ads API Application (March 2026)
- Replied to compliance team with detailed response + ACT Design Document PDF
- Company URL updated to christopherhoole.com in API centre
- Access upgraded: Test Account → **Explorer Access** (read production, no writes)
- Basic Access Case: 21767540705 — pending

### Google Ads Account Suspension
- Account 487-268-1731 suspended — advertiser verification issue
- RNM document (V770566I) submitted as Brazilian ID
- **Appeal ID: 6448619522** — "Your appeal is in review"
- Do NOT submit another appeal. Monitor chris@christopherhoole.com.

---

## CURRENT STATUS

### What's Working
- All 6 dashboard pages with Google Ads-style tables
- Google Ads-style date picker on all entity pages
- 24 campaign rules + 30 flags (all enabled)
- Templates sub-tab — save as template, edit template, use template, duplicate detection
- 1,515 active recommendations
- Accept/Decline/Modify operations for all entity types
- Radar monitoring (Celery task)
- Changes audit trail (card grid)
- Search Terms tab with live negative keyword blocking
- Cold Outreach System — 6 pages, all 10 functions live
- Live email sending + signature + CV + tracking + scheduling (Celery)
- Reply inbox polling (Celery task)
- Marketing website live (christopherhoole.com)
- Google Sheets → outreach leads sync
- Real data ingestion pipeline (blocked on API)
- 620 unit tests, 80% coverage
- Celery + Redis job queue (requires Memurai install)

### What's Blocked / Pending
- Google Ads API Basic Access (Case 21767540705)
- Advertiser verification appeal (ID 6448619522)
- Memurai install (for Celery to run)

---

## DB STATE

| Table | Count |
|-------|-------|
| Rules (campaign, is_template=FALSE) | 24 |
| Flags (campaign, is_template=FALSE) | 30 |
| Templates (is_template=TRUE) | 0 |
| **Total rows** | **54** |

**Diagnostic scripts (project root):**
- `full_audit.py` — full breakdown of all rules/flags/templates
- `check_state.py` — recent rows + template state
- `check_pacing.py` — Pacing Reduction rows
- `cleanup_junk.py` — delete specific IDs
- `cleanup_all_templates.py` — delete all (template) named rows
- `test_duplicate_query.py` — test duplicate detection in isolation

---

## KNOWN PITFALLS (Quick Reference)

| Problem | Fix |
|---------|-----|
| Template CSS missing | Must extend base_bootstrap.html |
| DB query fails | Use ro.analytics.* not analytics.* |
| Route replacement fails | Match exact quote style |
| json_extract returns quoted value | Use json_extract_string not JSON_EXTRACT |
| Duplicate check silently failing | conn must be open BEFORE the check query |
| JS state vars wiped | Set _rfbEditId/_rfbIsTemplate AFTER rfbResetForm() |
| onclick function does nothing | Verify function is actually defined in JS |
| Apostrophe breaks JS | Escape as \'  in single-quoted strings |
| Flag condition shows wrong direction | Use direction-aware label objects {pos, neg} |
| Recommendations limit=200 truncates | Increase to 5000+ |
| CSRF 400 | Add csrf.exempt() to routes |
| Opened/clicked showing 0 | Use open_count > 0 not opened_at IS NOT NULL |
| Client selector switching | Use session.get() not get_current_config() |
| Email no formatting | Add \n→<br> wrap in queue_send() |
| Email garbled chars | MIMEText needs all 3 args including "utf-8" |
| White box gap on entity pages | table-styles.css had prototype body/container CSS |
| Navbar text hidden | Never define .d-none in custom CSS |
| Celery worker not running | Install Memurai first — see docs/CELERY_STARTUP.md |

**See KNOWN_PITFALLS.md for full detail with code examples.**

---

## KEY FILE PATHS

| File | Purpose |
|------|---------|
| `act_dashboard/email_sender.py` | SMTP sending module |
| `act_dashboard/celery_app.py` | Celery instance + beat schedule |
| `act_dashboard/routes/campaigns.py` | Campaign rules CRUD + save-as-template + duplicate detection |
| `act_dashboard/templates/components/rules_flags_tab.html` | Rules/Flags/Templates tables + JS |
| `act_dashboard/templates/components/rules_flow_builder.html` | 5-step modal flow builder |
| `act_dashboard/static/css/rules.css` | All rules/flags/templates styling |
| `act_autopilot/recommendations_engine.py` | CAMPAIGN_METRIC_MAP 38 entries |
| `act_lighthouse/features.py` | Feature engineering incl. impression_share_lost_rank |
| `act_autopilot/rules_config.json` | Rules UI config layer (single source of truth) |
| `act_autopilot/rules/` | Rule execution layer (Python functions) |
| `scripts/add_is_template_col.py` | Migration: adds is_template column |
| `scripts/add_impression_share_col.py` | Migration: adds impression_share_lost_rank |
| `tests/` | pytest test suite — 620 tests, 80% coverage |
| `docs/CELERY_STARTUP.md` | Celery + Redis startup instructions |
| `docs/CHAT_93_BRIEF.md` | Templates tab build brief |
| `full_audit.py` | Full DB audit script (project root) |
| `check_state.py` | Quick DB state check (project root) |

---

## GOOGLE ADS ACCOUNT DETAILS

| Field | Value |
|-------|-------|
| Primary account | 487-268-1731 (chris@christopherhoole.com) — active |
| Test account | 125-489-5944 (joicemoura1001@gmail.com) — active |
| MCC | 152-796-4125 |
| Developer token | oDANZ-BXQprTm7_Sg4rjDg |
| API Case ID | 21767540705 |
| Appeal ID | 6448619522 |
| API Access Level | Explorer (upgraded from Test Account, March 2026) |

---

## LATEST COMMITS

| Commit | Description |
|--------|-------------|
| 342c8d8 | Chat 93: Templates tab — table view, save/edit/use template, duplicate detection |
| 4bae83d | Chat 91: Flags sub-tab UI overhaul — direction labels, plain English, condition text |
| 060fe2a | Chat 92: impression_share_lost_rank pipeline + CAMPAIGN_METRIC_MAP 38 entries |
| a932ee7 | Chat 90: Replace daemon threads with Celery + Redis job queue |
| 51e79c6 | Chat 89: Add pytest test suite — 620 tests, 80% coverage |
| 088317d | Chat 88: Add ad_daily table + seed data + database indexes |

---

**Version:** 19.0 | **Last Updated:** 2026-03-15
**Architecture:** 2-Tier (Master Chat → Claude Code)
**Next Step:** Rules strategic review — design discussion in Master Chat 12
