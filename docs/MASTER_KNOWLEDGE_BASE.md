# MASTER KNOWLEDGE BASE - ADS CONTROL TOWER (A.C.T)

**Version:** 18.0
**Created:** 2026-02-19
**Updated:** 2026-03-12
**Purpose:** Complete project context for Master Chat coordination

---

## EXECUTIVE SUMMARY

### Current State (March 12, 2026)
- **Overall Completion:** ~99.9%
- **Phase:** Platform hardened — Rules & Recommendations overhaul next
- **Active Development:** Master Chat 11.0
- **Primary Website:** https://christopherhoole.com (always use this — never christopherhoole.online)
- **Email:** chris@christopherhoole.com (Google Workspace, live, DKIM/SPF authenticated)
- **Rules:** 41 total (13 campaign + 6 keyword + 4 ad_group + 4 ad + 14 shopping)
- **Recommendations:** 1,515 active (1,256 keywords + 126 shopping + 110 campaigns + 23 ads)
- **Outreach:** 6 pages complete, all 10 original functions live
- **Tests:** 620 tests, 80% coverage (Chat 89)
- **Background jobs:** Celery + Redis (replaces daemon threads, Chat 90)

### Tech Stack

**A.C.T Dashboard:**
- **Backend:** Python 3.11, Flask
- **Database:** DuckDB (warehouse.duckdb + warehouse_readonly.duckdb)
- **API:** Google Ads API (v15) — Test Access only, Basic Access pending
- **Frontend:** Bootstrap 5.3, Chart.js 4.4, Vanilla JS
- **Templating:** Jinja2 Macros (metrics_section M2 + performance_chart M3)
- **Date Picker:** Custom Google Ads-style dropdown (Chat 79, datepicker.css)
- **Email:** Gmail SMTP (chris@christopherhoole.com, port 587 TLS, App Password)
- **Background Jobs:** Celery 5.6.2 + Redis (Memurai on Windows) — see docs/CELERY_STARTUP.md
- **Tests:** pytest + pytest-cov, 620 tests, 80% coverage

**Marketing Website:**
- **Framework:** Next.js 14
- **Styling:** Tailwind CSS
- **Animation:** Framer Motion
- **Components:** shadcn/ui
- **Hero:** Three.js WebGL (r128)
- **Hosting:** Vercel
- **Domains:** christopherhoole.com (primary) + christopherhoole.online — both live on same Vercel project

### Development Architecture (2-Tier — Current)

```
Master Chat (Claude Desktop App / claude.ai)
 → Quick fixes done directly here (file download/replace)
 → Large builds: creates concise task briefs as downloadable files to /docs/

Claude Code (Code tab in Claude Desktop App)
 → Executes large builds autonomously
 → Reads codebase directly — no file uploads needed
```

**Brief delivery rule:** Always save briefs as downloadable files to `/docs/` — never inline in chat.

**Claude Code handles:** file editing, testing, documentation, checkpoint reporting.

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

### Chat 22 — M1: Date Range Picker ✅
Flatpickr, session persistence, 7d/30d/90d presets + custom range

### Chat 23 — M2: Metrics Cards ✅
Jinja2 macro system on all 6 pages — financial + actions rows, sparklines

### Chat 24 — M3: Chart Overhaul ✅
Reusable performance_chart.html macro, dual Y-axis, 4 toggleable metric slots

### Chat 25 — M4: Table Overhaul ✅
Full Google Ads column sets on all 5 entity pages, server-side sort, sticky first column

### Chat 26 — M5: Card-Based Rules Tab ✅
**Dual-layer architecture (critical — do not break):**
- `act_autopilot/rules_config.json` — UI config layer (CRUD via rules_api.py)
- `act_autopilot/rules/*.py` — execution layer (untouched, Python functions only)

### Chat 27 — M6: Recommendations Engine + UI ✅
- recommendations table in warehouse.duckdb
- recommendations_engine.py: evaluates campaign_features_daily → inserts pending recs
- `/recommendations/cards` JSON endpoint
- Global /recommendations page + Campaigns → Recommendations tab

### Chat 28 — M7: Accept/Decline/Modify + 4-Tab UI ✅
- Accept/Decline/Modify POST routes — fully wired
- `changes` audit table created in warehouse.duckdb

### Chat 29 — M8: Changes + Radar Monitoring ✅
- `act_autopilot/radar.py` — now a Celery task (Chat 90)
- `act_dashboard/routes/changes.py` — /changes route
- 5-tab UI (Pending/Monitoring/Successful/Declined/Reverted) — card grid layout confirmed working

### Chats 30a/30b — M9: Search Terms + Live Execution ✅
- Search Terms tab on Keywords page
- Negative keyword flagging + live Google Ads API execution
- Keyword expansion flagging

### Marketing Website ✅
**Deployed:** christopherhoole.com (primary) + christopherhoole.online | **Stack:** Next.js 14, Tailwind CSS, Framer Motion, Three.js

### Chats 84–87 — Website + CV Polish ✅
| Chat | Feature |
|------|---------|
| 84 | CV Download button in Hero + Navigation |
| 85 | Full SEO (metadata, sitemap, robots, og-image) — PageSpeed Desktop 83, Mobile 76, SEO 100/100 |
| 86 | WhatsApp floating button + 4 unique messages (WhatsApp: +447999500184) |
| 87 | LinkedIn URL fix + Insight Tag (partner ID: 9697497) |

### Rules Creation Phase ✅ (Chats 41-46 — 41 rules complete)
- Chat 42: 6 Keyword Rules
- Chat 43: 4 Ad Group Rules
- Chat 44: 4 Ad Rules
- Chat 45: 14 Shopping Rules
- Chat 46: Rules Tab UI Components

### Multi-Entity Recommendations (Chats 47-49) ✅
- 1,492 recommendations (pre-Chat 88): 1,256 keywords + 126 shopping + 110 campaigns
- Entity type filter, color-coded badges, entity-specific pages

### Module 4: Dashboard Design Upgrade (Chats 57-58) ✅
**Commits:** 6f9fafa, 0bcee06, ef93abc, 86e01ed, 72407bf
- Google Ads-style tables on all 5 entity pages
- Control bar, column selector modal, session-based persistence
- Status dots, ROAS color coding, actions menus, shared table-styles.css

### Cold Outreach System — UI (Chats 59-64) ✅
**Commits:** d524448, c0e0eb8, 194ef2c

6 pages under `/outreach/` blueprint:

**Database tables (warehouse.duckdb):**
- `outreach_leads` — prospect records
- `outreach_emails` — queue + sent log with open_count, click_count, cv_open_count integer columns
- `email_replies` — reply tracking
- `email_templates` — 4 steps × 4 tracks = 16 templates

**Track types:** Agency, Recruiter, Direct, Job

| Page | Route | Features |
|------|-------|----------|
| Leads | /outreach/leads | Lead list, status management, add/edit modal |
| Queue | /outreach/queue | Email queue, send/skip/discard, preview modal |
| Sent | /outreach/sent | Sent log, open/click tracking display |
| Replies | /outreach/replies | Reply cards, slide-out panel, unread count |
| Templates | /outreach/templates | 16 templates, edit modal, variable chips |
| Analytics | /outreach/analytics | 8 KPIs, funnel, 5 charts, performance tables |

### Chat 65 — Google Sheets → A.C.T Sync ✅
Contact form leads from christopherhoole.com sync to outreach_leads via `/outreach/sync-from-sheets`

### Chat 66 — Add Client Modal + Config Validator ✅
- Christopher Hoole account added: customer_id 1254895944, MCC 4434379827
- Config YAML validator fix

### Chat 67 — Real Data Ingestion Pipeline ✅
**Commit:** e9bcb3f
- `src/gads_pipeline/v1_runner.py` — fixed DB write path
- `scripts/copy_all_to_readonly.py` — copies all 6 analytics tables to warehouse_readonly
- `tools/run_ingestion.py` — orchestration script
**Blocker:** Google Ads API Basic Access pending (Case 24460840136, applied March 4)

### Chat 68 — Live Email Sending ✅
**Commit:** fe4a0d7 + bug fixes
- Domain: christopherhoole.com | Email: chris@christopherhoole.com | DKIM/SPF authenticated
- Gmail App Password: `iflslbdfppfoehqz` (secrets/email_config.yaml — gitignored)
- Daily limit: 100 emails/day

### Chats 69–80 — Outreach Functions + UI Polish ✅
| Chat | Feature |
|------|---------|
| 69 | Email signature on all outgoing emails |
| 70 | CV upload & file storage (Templates page) |
| 71 | CV attachment on send (Queue page) |
| 72 | Open/click/CV tracking pixels + auto-inject on send |
| 73 | Reply inbox polling (Gmail IMAP, 120s — now Celery task) |
| 74 | Send reply from Replies page |
| 75 | Edit this email (Queue ✏ button) |
| 76 | Universal slidein design across all outreach pages |
| 77 | Switch template (Queue 📋 button) |
| 78 | Queue auto-scheduling (now Celery task) |
| 79 | Google Ads-style date picker (replaces Flatpickr) |
| 80 | Remove rules slidein from entity pages |

### Chat 81 — table-styles.css Layout Fix ✅
**Commit:** 8968d64 — removed prototype body/container CSS from table-styles.css

### Chat 82 — Remove Duplicate Client Selector from Outreach ✅
**Commit:** 9ee01fb — three bugs: duplicate selector, navbar text hidden, client_name blank

### Chat 83 — Remove Rules Card from Campaigns and Shopping ✅
**Commit:** f531bd8

### Chat 88 — ad_daily Table + Database Indexes ✅
**Commit:** 088317d
- `tools/seed_ad_daily.py` — created, populates ad_daily with 90 days synthetic data
- `scripts/copy_all_to_readonly.py` — updated to include ad_daily
- `scripts/add_indexes.py` — indexes on all 6 analytics tables in warehouse_readonly
- **Result:** 23 Ad recommendations now generating (was 0). 983 ads loaded, 12 rules active.

### Chat 89 — Unit Tests (pytest 80%+) ✅
**Commit:** 51e79c6
- `tests/` folder created with 19 test files
- 620 tests, 0 failures, 80% coverage
- Coverage: campaigns 85%, ads 85%, changes 94%, rule_helpers 94%, shared 86%, recommendations 80%
- ~30-40% of rule-specific tests will need updating after Rules & Recommendations overhaul

### Chat 90 — Celery + Redis Background Job Queue ✅
**Commit:** a932ee7
- `act_dashboard/celery_app.py` — Celery instance, Redis broker, 3 periodic tasks
- Daemon threads replaced: outreach_poller (120s), queue_scheduler (300s), radar (60s)
- Flask starts cleanly without Celery — background tasks simply don't fire until Celery worker started
- **Manual prerequisite:** Install Memurai (Windows Redis) from https://www.memurai.com/
- Startup instructions: `docs/CELERY_STARTUP.md`

### Google Ads Account Suspension ✅ (appeal submitted)
- Account 487-268-1731 (chris@christopherhoole.com) suspended — advertiser verification issue
- Root cause: UK passport submitted but payments profile registered in Brazil
- RNM document (V770566I, issued 25/02/2026) submitted as correct Brazilian ID
- **Appeal ID: 6448619522** — submitted 12 Mar 2026, status: "Your appeal is in review"
- Do NOT submit another appeal. Check chris@christopherhoole.com for Google's response.

---

## CURRENT STATUS

### Overall: ~99.9% Complete

**What's Working:**
- All 6 dashboard pages with Google Ads-style tables
- Google Ads-style date picker on all entity pages
- 41 optimization rules across 5 entity types
- 1,515 active recommendations (including 23 Ad recs — Chat 88)
- Accept/Decline/Modify operations for all entity types
- Radar monitoring (Celery task)
- Changes audit trail (card grid layout confirmed working)
- Search Terms tab with live negative keyword blocking + keyword expansion
- Cold Outreach System — 6 pages, all 10 functions live
- Live email sending + signature + CV + tracking + scheduling (Celery)
- Reply inbox polling (Celery task)
- Marketing website live (christopherhoole.com primary)
- Google Sheets → outreach leads sync
- Real data ingestion pipeline (blocked on API access)
- 620 unit tests, 80% coverage
- Celery + Redis job queue (requires Memurai install)

**What's Blocked / Pending:**
- Google Ads API Basic Access (Case 24460840136)
- Advertiser verification appeal (ID 6448619522)
- Memurai install (for Celery to run)

**Next Priority:**
- Rules & Recommendations overhaul — deep design discussion in Master Chat 11

---

## KNOWN PITFALLS (Quick Reference)

| Problem | Fix |
|---------|-----|
| Template CSS missing | Must extend base_bootstrap.html, not base.html |
| DB query fails | Use ro.analytics.* not analytics.* |
| Route replacement fails | Match exact quote style of @bp.route decorator |
| Shopping metrics missing | Add total_clicks to compute_campaign_metrics() |
| Ad group table empty | Use cpc_bid_micros not bid_micros |
| Sort not working on full dataset | Must be SQL-side ORDER BY, not Python-side |
| New sort column not working | Add to ALLOWED_*_SORT whitelist in route |
| rules_config.json not found | Path needs `.parent.parent.parent` from route files |
| Drawer visible on page load | Remove flex from inline style, let JS add it |
| Blueprint not registered | New blueprints MUST be added to __init__.py |
| Radar "ro catalog does not exist" | Must ATTACH warehouse_readonly.duckdb |
| Radar read-write conflict | Never open warehouse.duckdb with read_only=True |
| **Recommendations:** limit=200 truncates | Increase to 5000+ for high-volume entities |
| **Recommendations:** CSRF 400 | Add csrf.exempt() to routes in app.py |
| **Outreach:** opened/clicked showing 0 | Use open_count > 0 (integer), not opened_at IS NOT NULL |
| **Outreach:** Client selector switching | Use session.get("current_client_config") not get_current_config() |
| **Outreach:** Jinja/JS brace conflict | Split: `'{' + '{'` instead of `{{` in JS |
| **Outreach:** Duplicate Flask process | Run `taskkill /IM python.exe /F` before starting |
| **Email:** No formatting in Gmail | body_html conversion missing from queue_send() — add \n→<br> wrap |
| **Email:** Garbled special chars | MIMEText needs all 3 args: `MIMEText(body_html, "html", "utf-8")` |
| **Email:** No toast on send | Add showToast to success branch of sendCard() |
| **Layout:** White box gap on entity pages | table-styles.css had prototype body/container CSS — remove both blocks |
| **Website:** Three.js colorSpace error | Remove t.colorSpace line for r128 compatibility |
| **Tests:** Rule tests need updating | After Rules & Recommendations overhaul, ~30-40% of test_rules_engine.py needs rewrite |
| **Celery:** Worker not running | Install Memurai first — see docs/CELERY_STARTUP.md |

**See KNOWN_PITFALLS.md for full detail with code examples.**

---

## LESSONS LEARNED (Key Points)

1. Always extend base_bootstrap.html (never base.html)
2. Always use ro.analytics.* prefix for read queries
3. Request current file before editing — never cached
4. DuckDB Radar pattern: connect(warehouse.duckdb) + ATTACH warehouse_readonly as ro
5. Dual-layer architecture: JSON config (UI) and Python functions (execution) must stay separate
6. Dry-run first: check flag BEFORE loading Google Ads client
7. Backend query limits must match data volume
8. CSRF exemptions needed for JSON API routes called from JavaScript
9. Each entity page needs specific component include
10. Jinja/JS brace conflict: split `{{` as `'{' + '{'` in JavaScript
11. Session consistency: always use session.get("key") not helper functions returning objects
12. Integer columns (open_count) vs timestamp columns (opened_at) — seed may not populate timestamps
13. taskkill /IM python.exe /F to clear stuck Flask processes
14. MIMEText requires all 3 args: `MIMEText(body_html, "html", "utf-8")`
15. HTML body conversion belongs in the route (queue_send), not in email_sender.py
16. Toast success path is always missing — explicitly add showToast to if (data.success) branch
17. Never commit before Christopher confirms in Opera — Claude Code success ≠ visual confirmation
18. Diagnose email formatting via Gmail "Show original" → base64 decode
19. Prototype CSS (body padding, .container styles) must be stripped before using in Flask app
20. Never define `.d-none` in page-specific CSS — overrides Bootstrap responsive utilities
21. All render_template() calls must include `client_name=config.client_name`
22. Quick fixes (1-3 files, clear change) done directly in Master Chat — only large multi-file builds go to Claude Code
23. Brief delivery: always downloadable files to /docs/ — never inline in chat
24. Root folder files: always commit, no need to flag
25. Never send git commit or Flask start commands to Claude Code — Master Chat only

**See LESSONS_LEARNED.md for all lessons with context.**

---

## KEY FILE PATHS

| File | Purpose |
|------|---------|
| `act_dashboard/email_sender.py` | SMTP sending module |
| `act_dashboard/celery_app.py` | Celery instance + beat schedule (3 tasks) |
| `act_dashboard/outreach_poller.py` | IMAP reply polling — Celery task (120s) |
| `act_dashboard/queue_scheduler.py` | Email auto-send scheduler — Celery task (300s) |
| `act_autopilot/radar.py` | Post-change monitoring — Celery task (60s) |
| `act_dashboard/routes/outreach.py` | All outreach routes |
| `act_dashboard/secrets/email_config.yaml` | SMTP/IMAP credentials — local only, gitignored |
| `act_dashboard/static/css/table-styles.css` | Entity page table styles (no body/container overrides) |
| `act_dashboard/static/css/outreach.css` | Outreach CSS (no .d-none override) |
| `act_dashboard/static/css/datepicker.css` | Google Ads-style date picker CSS |
| `act_autopilot/rules_config.json` | Rules UI config layer (single source of truth) |
| `act_autopilot/rules/` | Rule execution layer (Python functions) |
| `act_autopilot/recommendations_engine.py` | Recommendation generation logic |
| `tests/` | pytest test suite — 620 tests, 80% coverage |
| `tools/reseed_queue.py` | Reset sent emails to queued for testing |
| `tools/seed_ad_daily.py` | Seed ad_daily table with synthetic data |
| `tools/run_ingestion.py` | Data pipeline orchestration |
| `scripts/copy_all_to_readonly.py` | Copy all 6 analytics tables to warehouse_readonly |
| `scripts/add_indexes.py` | Add indexes to warehouse_readonly analytics tables |
| `docs/CELERY_STARTUP.md` | Full startup instructions for Redis + Celery + Flask |
| `src/gads_pipeline/v1_runner.py` | Google Ads API pull functions |
| `configs/client_christopher_hoole.yaml` | Christopher's account config |

---

**Version:** 18.0 | **Last Updated:** 2026-03-12
**Architecture:** 2-Tier (Master Chat → Claude Code)
**Next Step:** Rules & Recommendations overhaul — design discussion in Master Chat 11
