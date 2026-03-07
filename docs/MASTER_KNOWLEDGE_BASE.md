# MASTER KNOWLEDGE BASE - ADS CONTROL TOWER (A.C.T)

**Version:** 16.0
**Created:** 2026-02-19
**Updated:** 2026-03-07
**Purpose:** Complete project context for Master Chat coordination

---

## EXECUTIVE SUMMARY

### Current State (March 7, 2026)
- **Overall Completion:** ~99.9%
- **Phase:** Outreach system live email sending complete — 10 functions still not live
- **Active Development:** Master Chat 8.0 — complete remaining outreach functions
- **Marketing Websites:** https://christopherhoole.online | https://christopherhoole.com
- **Email:** chris@christopherhoole.com (Google Workspace, live, DKIM/SPF authenticated)
- **Rules:** 41 total (13 campaign + 6 keyword + 4 ad_group + 4 ad + 14 shopping)
- **Recommendations:** 1,492 active (1,256 keywords + 126 shopping + 110 campaigns)
- **Outreach:** 6 pages complete, live email sending working, 10 functions not yet live

### Tech Stack

**A.C.T Dashboard:**
- **Backend:** Python 3.11, Flask
- **Database:** DuckDB (warehouse.duckdb + warehouse_readonly.duckdb)
- **API:** Google Ads API (v15) — Test Access only, Basic Access pending
- **Frontend:** Bootstrap 5.3, Chart.js 4.4, Vanilla JS, Flatpickr
- **Templating:** Jinja2 Macros (metrics_section M2 + performance_chart M3)
- **Email:** Gmail SMTP (chris@christopherhoole.com, port 587 TLS, App Password)

**Marketing Website:**
- **Framework:** Next.js 14
- **Styling:** Tailwind CSS
- **Animation:** Framer Motion
- **Components:** shadcn/ui
- **Hero:** Three.js WebGL (r128)
- **Hosting:** Vercel
- **Domains:** christopherhoole.online (GoDaddy) + christopherhoole.com (Namecheap) — both live on same Vercel project

### Development Architecture (2-Tier — Current)

```
Master Chat (Claude Desktop App)
 → Creates concise task briefs (2 pages max)

Claude Code (PowerShell Terminal)
 → Executes entire task autonomously
 → npx @anthropic-ai/claude-code from C:\Users\User\Desktop\gads-data-layer
```

**Old 3-tier architecture (archived):** Master Chat → Worker Chat → Claude Code. Eliminated due to handoff overhead.

**Claude Code handles:** file editing, testing, documentation, checkpoint reporting. No file uploads needed — reads codebase directly.

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
- `act_autopilot/radar.py` — background daemon thread (60s cycle)
- `act_dashboard/routes/changes.py` — /changes route
- 5-tab UI (Pending/Monitoring/Successful/Declined/Reverted)

### Chats 30a/30b — M9: Search Terms + Live Execution ✅
- Search Terms tab on Keywords page
- Negative keyword flagging + live Google Ads API execution
- Keyword expansion flagging

### Marketing Website ✅
**Deployed:** christopherhoole.online + christopherhoole.com | **Stack:** Next.js 14, Tailwind CSS, Framer Motion, Three.js

### Rules Creation Phase ✅ (Chats 41-46 — 41 rules complete)
- Chat 42: 6 Keyword Rules
- Chat 43: 4 Ad Group Rules
- Chat 44: 4 Ad Rules
- Chat 45: 14 Shopping Rules
- Chat 46: Rules Tab UI Components

### Multi-Entity Recommendations (Chats 47-49) ✅
- 1,492 recommendations: 1,256 keywords + 126 shopping + 110 campaigns
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
Contact form leads from christopherhoole.online sync to outreach_leads via `/outreach/sync-from-sheets`

### Chat 66 — Add Client Modal + Config Validator ✅
- Christopher Hoole account added: customer_id 1254895944, MCC 4434379827
- Config YAML validator fix

### Chat 67 — Real Data Ingestion Pipeline ✅
**Commit:** e9bcb3f

- `src/gads_pipeline/v1_runner.py` — fixed DB write path (was writing to wrong DB)
- `scripts/copy_all_to_readonly.py` — copies all 5 analytics tables to warehouse_readonly
- `tools/run_ingestion.py` — orchestration script

**Blocker:** Google Ads API Basic Access pending (Case 24460840136, applied March 4). Currently Test Access only.

### Chat 68 — Live Email Sending ✅
**Commit:** fe4a0d7 + bug fixes

**Infrastructure setup:**
- Domain: `christopherhoole.com` purchased on Namecheap
- Google Workspace Business Starter activated
- `chris@christopherhoole.com` live with DKIM/SPF authentication
- Gmail App Password: `iflslbdfppfoehqz` (stored in secrets/email_config.yaml — gitignored)

**Files:**
- `act_dashboard/email_sender.py` — SMTP sending, config loading, variable substitution, daily limit check
- `act_dashboard/routes/outreach.py` — `queue_send()` upgraded to live send

**Critical implementation details:**
- MIMEText: `MIMEText(body_html, "html", "utf-8")` — all three args required
- Body conversion in `queue_send()`:
```python
body_html = (
    "<div style='font-family:Arial,sans-serif;font-size:14px;line-height:1.6;color:#333;'>"
    + (body or "").replace("\n", "<br>")
    + "</div>"
)
```
- Toast: `showToast('Email sent successfully!', 'success')` fires before `removeCard()` in success branch

**Bugs fixed:**
1. MIMEText missing `"utf-8"` → special chars garbled
2. `body_html` conversion missing from `queue_send()` → emails sent as plain text
3. Toast missing from success branch of `sendCard()` → no visual feedback

**Confirmed working:** Emails deliver with correct formatting, em-dashes/£ signs render correctly, green toast on send.

**Reseed tool:** `tools/reseed_queue.py` — resets sent emails back to queued for testing

---

## OUTREACH SYSTEM — FUNCTIONS NOT YET LIVE

As of Chat 68, these 10 functions are confirmed not working:

| # | Function | Location | Status |
|---|----------|----------|--------|
| 1 | Email signature | All outgoing emails | ❌ Not built |
| 2 | CV upload & file storage | Templates page | ❌ Placeholder UI only |
| 3 | CV attachment on send | Queue page | ❌ Toggle exists, never attaches |
| 4 | Open/click tracking pixel | Analytics | ❌ Integer columns seeded only |
| 5 | Reply inbox polling | Replies page | ❌ No Gmail polling |
| 6 | Send reply | Replies page | ❌ "Coming soon" toast |
| 7 | Edit this email | Queue page ✏ | ❌ "Coming soon" toast |
| 8 | Regenerate with AI | Queue page 🔄 | ❌ "Coming soon" toast |
| 9 | Switch template | Queue page 📋 | ❌ "Coming soon" toast |
| 10 | Queue auto-scheduling | Queue page | ❌ All sends are manual |

---

## CURRENT STATUS

### Overall: ~99.9% Complete

**What's Working:**
- All 6 dashboard pages with Google Ads-style tables
- 41 optimization rules across 5 entity types
- 1,492 active recommendations
- Accept/Decline/Modify operations for all entity types
- Radar monitoring and automatic rollback
- Changes audit trail
- Search Terms tab with live negative keyword blocking + keyword expansion
- Rules Tab UI on all pages
- Cold Outreach System — 6 pages complete
- Live email sending via Gmail SMTP (chris@christopherhoole.com)
- Marketing websites live (christopherhoole.online + christopherhoole.com)
- Google Sheets → outreach leads sync
- Real data ingestion pipeline (blocked on API access)

**What's Partially Working / Not Yet Live:**
- Ad Groups: 4 rules enabled but 0 recommendations (conditions not met)
- Ads: 4 rules blocked (analytics.ad_daily table missing)
- Google Ads API: Test Access only — Basic Access pending
- Outreach: 10 functions not yet live (see table above)

**Next Priorities:**
1. Complete 10 outstanding outreach functions (Master Chat 8.0)
2. Apollo.io lead import
3. M9 Live Validation (pending API access)
4. Website Design Upgrade
5. Testing & Polish

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
| **Email:** No toast on send | Add showToast to success branch of sendCard(), not just error branch |
| **Website:** Three.js colorSpace error | Remove t.colorSpace line for r128 compatibility |

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

**See LESSONS_LEARNED.md for all 61 lessons with context.**

---

## KEY FILE PATHS

| File | Purpose |
|------|---------|
| `act_dashboard/email_sender.py` | SMTP sending module |
| `act_dashboard/routes/outreach.py` | All outreach routes (1,859 lines) |
| `act_dashboard/secrets/email_config.yaml` | SMTP credentials — local only, gitignored |
| `act_dashboard/templates/outreach/queue.html` | Queue page template |
| `tools/reseed_queue.py` | Reset sent emails to queued for testing |
| `tools/run_ingestion.py` | Data pipeline orchestration |
| `scripts/copy_all_to_readonly.py` | Copy analytics tables to warehouse_readonly |
| `src/gads_pipeline/v1_runner.py` | Google Ads API pull functions |
| `configs/client_christopher_hoole.yaml` | Christopher's account config |

---

**Version:** 16.0 | **Last Updated:** 2026-03-07
**Architecture:** 2-Tier (Master Chat → Claude Code)
**Next Step:** Master Chat 8.0 — Complete 10 outstanding outreach functions
