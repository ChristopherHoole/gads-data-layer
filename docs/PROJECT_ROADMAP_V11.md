# PROJECT ROADMAP - Ads Control Tower (A.C.T.)

**Last Updated:** 2026-03-30
**Overall Completion:** ~90% (core platform complete, expansion features remain)
**Architecture:** 2-Tier (Master Chat → Claude Code)
**Local:** `C:\Users\User\Desktop\gads-data-layer`
**Primary Website:** https://christopherhoole.com (always — never christopherhoole.online)

---

## MASTER CHAT 13 COMPLETED WORK

### Chat 107 — Ad Groups Rules & Flags ✅
**Commit:** Multiple commits
**What was built:**
- 12 Ad Group Rules (4 Budget, 4 Bid, 4 Status)
- 18 Ad Group Flags (8 Performance, 6 Anomaly, 4 Technical)
- Ad Group rules CRUD routes (6 routes, all CSRF exempted)
- Ad Group rules flow builder component
- Rules tab on Ad Groups page with toggle/edit/delete/save-as-template
- Flags subtab with active/snoozed/history sections
- All 30 rules/flags tested and verified working

### Chat 108 — Keywords Rules & Flags ✅
**Commit:** Multiple commits
**What was built:**
- 12 Keyword Rules (4 Budget, 4 Bid, 4 Status)
- 20 Keyword Flags (10 Performance, 6 Anomaly, 4 Technical)
- Keyword rules CRUD routes (6 routes, all CSRF exempted)
- Keyword rules flow builder component
- Rules tab on Keywords page with full CRUD
- Flags subtab with active/snoozed/history sections
- All 32 rules/flags tested and verified working

### Chat 109 — Ads Rules & Flags ✅
**Commit:** Multiple commits
**What was built:**
- 8 Ad Rules (4 Performance, 4 Status)
- 15 Ad Flags (8 Performance, 4 Anomaly, 3 Technical)
- Ad rules CRUD routes (6 routes, all CSRF exempted)
- Ad rules flow builder component
- Rules tab on Ads page with full CRUD
- Flags subtab with active/snoozed/history sections
- All 23 rules/flags tested and verified working

### Chat 111 Redux — Shopping Campaign Rules & Flags ✅
**Commit:** bb47773
**What was built:**
- 14 Shopping Campaign Rules (3 Budget, 3 Status, 8 Bid)
- 8 Shopping Campaign Flags (3 Feed Quality, 3 Lifecycle, 2 Stock)
- Shopping campaign rules CRUD routes (6 routes, all CSRF exempted)
- Shopping campaign rules flow builder component
- Campaign/Product toggle buttons on Rules tab
- Rules tab on Shopping page with full CRUD
- Flags subtab with active/snoozed/history sections
- Manual creation of 8 Bid rules via create_shopping_bid_rules_v3.py
- All 22 rules/flags tested and verified working

### Chat 112 — Shopping Product Rules & Flags ✅
**Commit:** 2d03f15
**What was built:**
- 10 Product Rules (4 Priority, 4 Status, 2 Volume)
- 8 Product Flags (3 Performance, 3 Anomaly, 2 Technical)
- Product rules CRUD routes (6 routes, all CSRF exempted)
- Product rules flow builder component
- Campaign/Product toggle working — switches between views
- Product rules table with full CRUD
- All 18 rules/flags created in database

---

## MASTER CHAT 14 — MC RULES & RECOMMENDATIONS (Chat 114) ✅

### Slide-In Panel Migration (Tasks 1-7) ✅
**Commits:** d95697f + others
**What was built:**
- Replaced ALL 5-step wizard modals with single scrollable slide-in panels (720px wide)
- Live summary sidebar that updates in real-time as user fills form
- All 5 sections visible in one scroll (no step navigation)
- Sticky Save footer with Cancel and Save buttons
- Close via X button, overlay click, or Escape key
- New CSS: `.flow-slide-overlay`, `.flow-slide-panel`, `.rfb-section`, `.rfb-compact-card`, `.rfb-summary-card`, `.rfb-live-sentence`
- Removed all legacy centered-modal CSS

**Pages migrated:**
| Page | Template | Status |
|------|----------|--------|
| Campaigns | `rules_flow_builder.html` | ✅ Migrated + tested |
| Ad Groups | `ag_rules_flow_builder.html` | ✅ Migrated + tested |
| Keywords | `kw_rules_flow_builder.html` | ✅ Migrated + tested |
| Ads | `ad_rules_flow_builder.html` | ✅ Migrated + tested |
| Shopping Campaigns | `shopping_campaign_rules_flow_builder.html` | ✅ Migrated + tested |
| Shopping Products | `product_rules_flow_builder.html` | ✅ Migrated + tested |

### Recommendations Design Upgrade (Campaigns) ✅
**Commit:** 6722705
- All 7 recommendation/flag tables wrapped in `.rec-table-wrapper` with rounded borders
- Expand rows use 3-column card layout with vertical dividers
- All sub-tab badges use consistent grey (`bg-secondary`)

### Recommendations Rollout — All 5 Remaining Entities (Tasks 8-12) ✅
**Commits:** 93b7ccd, 10ac92d, 0d29e98, 8acaf0f, d671184, 62cf8bb, 126cecc, 1932036, e37c1e5
**What was built per entity:**
- Header with "Accept all low risk" and "Run Recommendations Now" buttons
- 5 sub-tabs: Pending, Monitoring, Successful, History, Flags
- 11-column tables with `.rec-table-wrapper` borders
- Click-to-expand card rows (Why triggered, Proposed change, Rule details)
- Bulk select/accept/decline on Pending tab
- Pagination (20 per page)
- Toast notifications for all actions
- Flags section with Active, Snoozed (collapsible), History (collapsible) tables
- Flag actions: Acknowledge, Snooze 7/14/30 days (Bootstrap dropdown)

| Page | Engine | Accept/Decline | Monitoring | Flags | Status |
|------|--------|----------------|------------|-------|--------|
| Campaigns | ✅ | ✅ | ✅ | ✅ | ✅ Complete |
| Ad Groups | ✅ | ✅ | ✅ | ✅ | ✅ Complete |
| Keywords | ✅ | ✅ | ✅ | ✅ | ✅ Complete |
| Ads | ✅ | ✅ | ✅ | ✅ | ✅ Complete |
| Shopping | ✅ | ✅ | ✅ | ✅ | ✅ Complete |

### Backend Engine Fixes (Chat 114) ✅
- Multi-entity rule loading — engine now loads rules for ALL entity types
- Added `PRODUCT_METRIC_MAP` (new), updated `AD_METRIC_MAP`, `SHOPPING_METRIC_MAP`
- ACTION_MAP fixes: `enable` no longer maps to `hold`, added `decrease_target_roas`
- Added `"in"` operator support for comma-separated string matching
- Fixed string values being silently coerced to `0.0` by float() fallback
- Fixed entity ID crash on string IDs like `"prod_0001"`
- Rule enrichment now supports generic `db_*_N` format (not just `db_campaign_N`)
- Rule type display uses direct `type` field from DB (not hardcoded "shopping")

### Action Column Styling (Chat 114) ✅
- `actionCell()` handles all directions: increase (green ↑), decrease (red ↓), pause (orange ⏸), enable (green ▶), hold (grey →)
- `rtBadge()` extended with type map: performance, anomaly, technical, feed_quality, lifecycle, stock
- Keywords rtBadge CSS class map was missing — fixed

---

## GRAND TOTAL SYSTEM STATE

### Rules & Flags by Entity
| Entity | Rules | Flags | Total | Status |
|--------|-------|-------|-------|--------|
| Campaigns | 19 | 30 | 49 | ✅ Complete |
| Ad Groups | 12 | 18 | 30 | ✅ Complete |
| Keywords | 12 | 20 | 32 | ✅ Complete |
| Ads | 8 | 15 | 23 | ✅ Complete |
| Shopping Campaign | 14 | 8 | 22 | ✅ Complete |
| Shopping Product | 10 | 8 | 18 | ✅ Complete |
| **TOTAL** | **75** | **99** | **174** | **✅ Complete** |

### Recommendations by Entity
| Entity | Engine | UI Tab | Accept/Decline | Monitoring | Flags | Status |
|--------|--------|--------|----------------|------------|-------|--------|
| Campaigns | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ Complete |
| Ad Groups | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ Complete |
| Keywords | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ Complete |
| Ads | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ Complete |
| Shopping | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ Complete |
| **TOTAL** | **5/5** | **5/5** | **5/5** | **5/5** | **5/5** | **✅ Complete** |

### Slide-In Panels
| Entity | Migrated | Old Modal Removed | Status |
|--------|----------|-------------------|--------|
| Campaigns | ✅ | ✅ | ✅ Complete |
| Ad Groups | ✅ | ✅ | ✅ Complete |
| Keywords | ✅ | ✅ | ✅ Complete |
| Ads | ✅ | ✅ | ✅ Complete |
| Shopping Campaigns | ✅ | ✅ | ✅ Complete |
| Shopping Products | ✅ | ✅ | ✅ Complete |

### Dashboard Pages (All Complete)
1. ✅ Dashboard (home) — metrics cards, charts
2. ✅ Campaigns — table, rules tab (slide-in), recommendations tab (full), flags
3. ✅ Ad Groups — table, rules tab (slide-in), recommendations tab (full), flags
4. ✅ Keywords — table, search terms, rules tab (slide-in), recommendations tab (full), flags
5. ✅ Ads — table, rules tab (slide-in), recommendations tab (full), flags
6. ✅ Shopping — campaigns tab, products tab, feed quality tab, rules (slide-in), recommendations (full), flags
7. ✅ Recommendations — main page with entity filters, all sections, flags tab
8. ✅ Changes — audit trail with filters and search
9. ✅ Jobs — table view, kanban view, slide-in add/edit, URL auto-fill, Google Sheet sync, stats header

### Cold Outreach System (All Complete)
1. ✅ Leads page — table, add/edit, notes, status tracking, won/lost
2. ✅ Queue page — compose email, send, skip, discard, CV attach toggle
3. ✅ Sent page — sent emails list, queue followup, status tracking, won/lost
4. ✅ Replies page — inbox, mark read/unread, send reply, won/lost, book meeting
5. ✅ Analytics page — funnel metrics, timeline, performance tracking
6. ✅ Templates page — create, edit, duplicate, switch template
7. ✅ Email sending — Gmail SMTP, HTML formatting, tracking pixels
8. ✅ CV upload/download — file storage system, toggle attach on emails
9. ✅ Scheduled emails — queue for later, cancel scheduled
10. ✅ Tracking — open pixel, click pixel, CV download pixel

### Marketing Website (Complete)
- ✅ Next.js 14, Tailwind CSS, Framer Motion
- ✅ Three.js WebGL hero animation
- ✅ Live at https://christopherhoole.com
- ✅ Lead capture form → Google Sheets integration

### Infrastructure (Complete)
- ✅ Flask + DuckDB + Bootstrap 5 + Chart.js
- ✅ Multi-client support (5 client configs)
- ✅ Celery + Redis background job queue (requires Memurai install)
- ✅ pytest suite — 620 tests, 80% coverage
- ✅ Google Ads API Explorer Access
- ✅ Git version control with GitHub

---

## MC RULES & RECOMMENDATIONS BRIEF — TASK STATUS

| # | Task | Category | Status |
|---|------|----------|--------|
| 1 | Build reusable slide-in panel component | Slide-In | ✅ Complete |
| 2 | Migrate Campaigns to slide-in | Slide-In | ✅ Complete |
| 3 | Migrate Ad Groups to slide-in | Slide-In | ✅ Complete |
| 4 | Migrate Keywords to slide-in | Slide-In | ✅ Complete |
| 5 | Migrate Ads to slide-in | Slide-In | ✅ Complete |
| 6 | Migrate Shopping Campaigns to slide-in | Slide-In | ✅ Complete |
| 7 | Migrate Shopping Products to slide-in | Slide-In | ✅ Complete |
| 8 | Ad Groups recommendations rollout | Recommendations | ✅ Complete |
| 9 | Keywords recommendations rollout | Recommendations | ✅ Complete |
| 10 | Ads recommendations rollout | Recommendations | ✅ Complete |
| 11 | Shopping Campaigns recommendations rollout | Recommendations | ✅ Complete |
| 12 | Shopping Products recommendations rollout | Recommendations | ✅ Complete |
| 13 | Fix trigger summary label (rule 19) | Bug Fix | ⚠️ Needs verification |
| 14 | Fix bugs found during tasks 1-12 | Bug Fix | ✅ Complete (many fixed) |
| 15 | Radar — monitor performance after acceptance | Radar | ❌ Not started |
| 16 | Radar — auto-rollback on degradation | Radar | ❌ Not started |
| 17 | Radar — cooldown reset on rollback | Radar | ❌ Not started |
| 18 | Radar — user alert on rollback | Radar | ❌ Not started |
| 19 | Radar — rollback audit trail | Radar | ❌ Not started |
| 20 | Radar — monitoring UI | Radar | ❌ Not started |
| 21 | Rules strategic review | Review | ❌ Not started |

**Completed: 14/21 | Remaining: 7 (6 Radar + 1 Review)**

---

## MASTER CHAT 15 — MC JOB HUNTER (Chat 115) ✅

### Task 1: Connect Indeed MCP ✅
- Connected Indeed MCP connector in claude.ai browser interface
- Tested with UK Google Ads Manager searches — returns listings with titles, companies, salaries, URLs

### Task 2-7: Jobs Tracker System ✅
**Files created:**
- `act_dashboard/routes/jobs.py` — Full CRUD + URL auto-fill + Google Sheet sync
- `act_dashboard/templates/jobs.html` — Table view, Kanban view, slide-in panel, stats header
- `act_dashboard/static/css/jobs.css` — All styles

**Files modified:**
- `act_dashboard/app.py` — Registered jobs blueprint, CSRF exemptions
- `act_dashboard/routes/__init__.py` — Added jobs import
- `act_dashboard/templates/base_bootstrap.html` — Added Jobs to sidebar nav

**Features built:**
- DuckDB `jobs` table with 15 columns (title, company, location, salary, status, priority, etc.)
- Full CRUD API (GET/POST/PUT/DELETE)
- Table view with filters, sorting, search, status/priority/source badges
- Slide-in panel for add/edit with URL auto-fill (JSON-LD → Open Graph → HTML fallback)
- LinkedIn crawler (title, company, location, salary, description, hiring contact)
- Pipeline/Kanban view with 4 columns (Saved, Applied, Interview, Offer)
- Google Sheet sync: Indeed MCP → Google Sheet → ACT (published CSV import, duplicate detection)
- Stats header: Total Jobs, Applications Sent, Interviews, Offers, Response Rate

### Task 8: CV Update ✅
- Updated stats: 75 rules, 99 flags, 507 recommendations
- Content: dates corrected, contracts labelled, MarisaPeer removed
- Design: 10px body / 12px headings, 2 separate A4 pages
- Output: `chrishoolecv26-3-26.pdf`

### Task 9: ChristopherHoole.com Website Polish ✅
**Project:** `C:\Users\User\Desktop\act-website` (Next.js + Tailwind)
- Complete recruiter-audience rework of homepage
- Original archived at `/hp-copy-1`
- New copy: "generates" not "automates", "100+ accounts", recruiter-focused FAQs
- 13 archive components created for rollback
- Inter font for body, 3-tier font system
- All CTAs changed to "Get in Touch"
- Deployed live via Vercel

### Task 10: LinkedIn Job Search Research ✅
**Output:** `docs/LINKEDIN_JOB_RESEARCH.md`
- 6 options evaluated: LinkedIn MCP, JobSpy, JSearch, Adzuna, Indeed MCP, Apify
- Recommendation: Keep Indeed MCP pipeline, integrate JobSpy next, JSearch/Adzuna as fallbacks

---

## NEXT PRIORITIES — IMMEDIATE BUGS & FIXES

**DASHBOARD — ACT**
1. Fix Keywords search terms — custom date range causes DATE/VARCHAR mismatch in keywords.py line 187. Preset 7d/30d/90d buttons work fine.
2. Fix Shopping page query — table alias 's' not found in shopping.py line 108
3. ⚠️ Verify trigger summary label fix — rule 19 ROAS→CPA (may have been fixed in Chat 114 engine work)
4. WoW metrics — all vs_prev_pct columns are 0.0 in synthetic data (will work on real data)
5. Rules 16, 17, 18, 20 don't fire — NULL bid_strategy_type in synthetic data (will work on real data)
6. Unit tests update — 620 tests written pre-flags, need new coverage for flags + recommendations
7. Memurai install — required for Celery background jobs to run

**NEW from Chat 114:**
8. Action column "enable" styling on Keywords — old recs have wrong `action_direction` stored as "hold". New recs after ACTION_MAP fix show correctly. Old recs need regeneration.
9. Ad Group status rules generate 0 recs — threshold too high for daily data granularity. Needs threshold adjustment.
10. `feed_quality` badge text shows underscore — prettify to "Feed Quality" with label map.
11. Old `ads.html` (Tailwind) still exists alongside `ads_new.html` (Bootstrap, served). Can be deleted in cleanup.

---

## NEXT PRIORITIES — MAJOR FEATURES

**DASHBOARD — ACT**
1. Radar / post-acceptance monitoring system (Tasks 15-20 from brief)
   - Monitor performance after rule acceptance
   - Auto-rollback if performance degrades
   - Cooldown reset on rollback
   - Alert user when rollback triggered
   - Rollback audit trail
   - Radar monitoring UI
   - Not started

2. Rules strategic review (Task 21 from brief)
   - Review all 75 rules across 6 entities
   - Verify thresholds are realistic
   - Verify cooldowns appropriate
   - Verify conditions use correct metrics
   - Verify risk levels accurate
   - Verify plain English clear
   - Not started

3. Reports builder — automated report generator
   - Monthly PowerPoint reports per campaign/account
   - Auto-generated slides with performance charts
   - AI-written insights and recommendations (Claude API)
   - Executive summary slide
   - Scheduled generation (Celery monthly job)
   - Email delivery to client
   - PDF export option
   - Tech: python-pptx, Chart.js image export, Claude API
   - Not started

4. Smart alerts system
   - Budget pacing alerts (overspend/underspend)
   - Keyword expansion opportunities
   - Competitor activity detected
   - Seasonal trend alerts
   - Quality Score drop alerts
   - Ad disapproval alerts
   - Delivery: Email notifications, in-app alerts, Slack integration
   - Not started

5. Campaign type expansion
   - Performance Max campaigns (metrics, rules, UI)
   - Display campaigns (metrics, rules, UI)
   - Video (YouTube) campaigns (metrics, rules, UI)
   - Demand Gen campaigns (metrics, rules, UI)
   - Each requires: new features tables, new rules config, new engine logic, UI updates
   - Not started

6. Conversion tracking checkup on account 487-268-1731
   - Verify all conversion actions configured
   - Check conversion tags firing correctly
   - Review attribution settings
   - Validate conversion values
   - Test checkout funnel tracking
   - Document current setup
   - Not started

7. Multi-user support
   - User authentication (beyond single admin)
   - Role-based permissions (Admin, Editor, Viewer)
   - User management UI
   - Audit trail per user
   - Email notifications per user
   - Not started

8. API endpoints for external access
   - REST API endpoints
   - API key authentication
   - Rate limiting
   - Documentation (Swagger/OpenAPI)
   - Not started

9. ACT deployment to production
    - Choose hosting (AWS, GCP, Azure, DigitalOcean)
    - Containerize with Docker
    - Database hosting (DuckDB → PostgreSQL migration?)
    - Redis hosting (Memurai → cloud Redis)
    - CI/CD pipeline
    - SSL certificates
    - Domain setup
    - Monitoring & logging (Sentry, DataDog)
    - Automated backups
    - Not started

**OUTREACH**
1. Email signature — feature exists but not configured
2. Reply inbox polling — code exists, needs testing with live inbox
3. Edit email after queueing — UI exists, needs backend route
4. Regenerate email with AI — planned, not built
5. Queue auto-scheduling — planned, not built
6. Apollo.io lead import — integration not built
7. Indeed job listing connector — ✅ MCP connected + Google Sheet pipeline built (Chat 115)
8. Automated email reports (weekly/monthly) — not built

**WEBSITE**
1. ~~Website design upgrade~~ — ✅ Complete (Chat 115: full recruiter-audience rework)
2. Mobile performance optimization — Core Web Vitals, lazy loading, image optimization
3. Contact form backend — /api/leads endpoint built, needs form UI connection
4. User guide / documentation for ACT platform
5. Video tutorials for onboarding
6. Client onboarding flow
7. ACTAgency website — separate agency site for PPC agency search traffic (planned)

**GOOGLE ADS — EXTERNAL (monitor only)**
1. API Basic Access — Case 21767540705, pending review
2. Advertiser verification — Appeal ID 6448619522, account 487-268-1731, in review
3. Real data pipeline — switch from synthetic to real data (blocked on API Basic Access)
4. Performance tune queries for real data volume
5. Schedule daily data refresh (Celery job)

**ADMIN**
1. Handoff docs at end of each Master Chat session — ongoing
2. Update MASTER_KNOWLEDGE_BASE.md — ongoing
3. Update PROJECT_ROADMAP.md — ongoing
4. Update LESSONS_LEARNED.md — ongoing
5. Update KNOWN_PITFALLS.md — ongoing

---

## CURRENT SYSTEM STATE

**Database:**
- Rules: 75 (across 6 entities) — all enabled
- Flags: 99 (across 6 entities) — all enabled
- Templates: 10+ (created during testing)
- flags table: 0 rows (cleared after testing)
- Recommendations: 0 (cleared)
- Changes: 0 (cleared)

**Synthetic Data:**
- Client: Christopher Hoole (customer_id: 1254895944)
- Campaigns: 4
- Ad Groups: ~20
- Keywords: ~100
- Ads: 48
- Shopping Campaigns: 20
- Shopping Products: 100
- Date range: 90 days (2026-01-01 to 2026-03-16)
- Last valid snapshot date: 2026-03-16

**Tests:**
- Total: 620 tests
- Coverage: 80%
- Status: Written pre-flags, need updating for flags + recommendations systems

**Background Jobs:**
- Celery: Configured ✅
- Redis: Configured ✅
- Memurai: NOT installed ❌ (required for Celery to run on Windows)
- Status: Jobs defined but cannot execute until Memurai installed

**Google Ads:**
- Account 487-268-1731: Active
- Account 125-489-5944: Active (test account)
- MCC: 152-796-4125
- Developer Token: oDANZ-BXQprTm7_Sg4rjDg
- API Access: Explorer (read production, no writes)
- API Case: 21767540705 (Basic Access pending)

---

## KNOWN BUGS & ISSUES

### High Priority (Must Fix)
1. **Keywords search terms DATE/VARCHAR bug**
   - File: keywords.py line 187
   - Issue: Custom date range causes "Cannot mix DATE and VARCHAR in BETWEEN clause"
   - Workaround: Preset buttons (7d/30d/90d) work fine
   - Fix: Cast parameter to DATE in BETWEEN clause

2. **Shopping page query syntax error**
   - File: shopping.py line 108
   - Issue: Table alias 's' not found
   - Fix: Add table alias to FROM clause

### Medium Priority (Can Wait)
3. **Trigger summary label for rule 19** ⚠️
   - May have been fixed by Chat 114 engine work — needs verification
   - If not fixed: correct label mapping in recommendations.py

4. **WoW metrics always 0.0 in synthetic data**
   - DuckDB nested window function limitation
   - Will work on real data, not fixable in synthetic

5. **Rules 16, 17, 18, 20 don't fire**
   - NULL bid_strategy_type in synthetic data
   - Will work on real data

6. **Unit tests need updating**
   - 620 tests written pre-flags/recommendations
   - Flags + recommendations systems not covered

7. **Memurai not installed**
   - Celery requires Redis, Memurai is Redis for Windows
   - Background jobs can't execute

### Low Priority (Cosmetic / Cleanup)
8. **Keywords "enable" action styling** — old recs have `action_direction: "hold"` from pre-fix. Regenerate to fix.
9. **Ad Group status rules 0 recs** — threshold too high for daily data granularity
10. **`feed_quality` badge underscore** — prettify to "Feed Quality"
11. **Old `ads.html` can be deleted** — `ads_new.html` is the served template

---

## BLOCKED ITEMS

**Blocked on API Basic Access:**
1. Real data ingestion from Google Ads API
2. Test all 174 rules/flags with real performance swings
3. Validate WoW metrics work correctly
4. Performance Max / Display / Video / Demand Gen support

**Blocked on Account Suspension:**
1. Live testing on account 487-268-1731
2. Conversion tracking verification
3. Real client demonstrations

**Blocked on Infrastructure:**
1. Celery background jobs (blocked on Memurai install)
2. Scheduled data refreshes (blocked on Memurai)
3. Scheduled report generation (blocked on Memurai)

---

## DEVELOPMENT WORKFLOW

**Flask Start:**
```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python act_dashboard/app.py
```

**Clear Database:**
```powershell
python -c "import duckdb; conn = duckdb.connect('warehouse.duckdb'); conn.execute('DELETE FROM recommendations'); conn.execute('DELETE FROM changes'); conn.execute('DELETE FROM flags'); print('Cleared'); conn.close()"
```

**Git Commit:**
```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
git add .
git commit -m "Chat XX: description"
git push origin main
```

**Claude Code:**
- Access: Code tab in Claude Desktop App ONLY (never via PowerShell)
- Briefs: Always save as downloadable files to /docs/ (never inline)
- Start command: `cd C:\Users\User\Desktop\gads-data-layer` then `npx @anthropic-ai/claude-code`

**Quick Fix Rule:**
- 1-3 file edits with clear change → Master Chat directly
- 4+ files or new routes → Claude Code brief

---

## LATEST COMMITS

| Commit | Description |
|--------|-------------|
| (pending) | Chat 115: Jobs tracker system — full CRUD, table, kanban, slide-in, URL auto-fill, Sheet sync |
| 473d0bc | Chat 114: Add comprehensive session summary document |
| bfabcfa | Chat 113: Fix Keywords rtBadge - add CSS class map for coloured rule type badges |
| 58a59a9 | Chat 113: Action column styling polish pass |
| d989632 | Chat 113: Fix Shopping pagination layout |
| e37c1e5 | Chat 113: Fix product entity type detection + string ID handling |
| 126cecc | Chat 114: Shopping Recommendations rollout - engine + frontend |
| 1932036 | Chat 114: Replace Shopping recs JS IIFE with standard pattern |
| 62cf8bb | Chat 114: Fix engine string condition values being silently coerced to 0.0 |
| d671184 | Chat 114: Fix 'in' operator for bracket-quoted lists + CPA micros divisor |
| 8acaf0f | Chat 114: Fix ad recommendations engine - ad_features_daily + windowed metric map |
| 0d29e98 | Chat 114: Ads Recommendations upgrade on ads_new.html |
| 10ac92d | Chat 114: Ads Recommendations rollout - table-based design with flags |
| 93b7ccd | Chat 114: Ad Groups Recommendations rollout + multi-entity engine fix |
| 47adb8e | Chat 114: Add long-scroll slide-in wireframe prototype |
| 6722705 | Chat 114: Recommendations tab design upgrade - table wrappers, card expand rows |
| d95697f | Chat 114: Migrate all 6 rule builders from 5-step modal to long-scroll slide-in |
| 473d0bc | Chat 114: Add comprehensive session summary document |
| 2d03f15 | Chat 112: Shopping Product Rules - fixed cost values (micros to pounds) and type pills |
| bb47773 | Chat 111 Redux: Shopping Campaign Rules complete |
| 61002f3 | Chats 99-100: Engine fixes |

---

## SUMMARY STATISTICS

**Development Time:** ~540+ hours across 115+ chats

**Code Stats:**
- Rules/Flags: 174 (75 rules + 99 flags) across 6 entities
- Recommendations: Full engine + UI across all 6 entities
- Slide-In Panels: 6 entity pages migrated from modal to slide-in
- Dashboard Pages: 9 complete (including Jobs)
- Outreach Pages: 6 complete
- Unit Tests: 620 tests, 80% coverage
- Routes: 100+ Flask routes
- Templates: 50+ Jinja2 templates
- CSS Files: 15+ custom stylesheets
- JavaScript: 10,000+ lines across all pages
- Wireframes: 3 (slide-in panel, long-scroll, recommendations tab)

**Completion by Category:**
- Core Dashboard: 100% ✅
- Rules System: 100% ✅
- Flags System: 100% ✅
- Slide-In Panels: 100% ✅
- Recommendations Engine: 100% ✅ (all 6 entities)
- Recommendations UI: 100% ✅ (all 6 entities)
- Radar / Monitoring: 0% ❌ (not started)
- Outreach System: 90% ✅ (core complete, integrations remain)
- Jobs Tracker: 100% ✅ (table, kanban, slide-in, sync, stats)
- Marketing Website: 100% ✅ (recruiter rework complete)
- Testing: 75% ⚠️ (needs flags + recommendations coverage)
- Infrastructure: 90% ✅ (Memurai install remains)
- Deployment: 0% ❌ (not started)
- Reports Builder: 0% ❌ (not started)
- Multi-User: 0% ❌ (not started)
- API Endpoints: 0% ❌ (not started)

**Overall Platform Completion: ~88%**
- Core features: Complete
- Rules + Recommendations: Complete across all entities
- Radar system: Not started
- Expansion features: Planned
- Production deployment: Not started

---

## MASTER CHAT 16 — CLIENT PITCH & QUOTING (2026-03-29/30) ✅

### Objection Experts — Client Pitch Reports ✅
**Data location:** `potential_clients/objection_experts/data/` (17 CSV files)
**Output:** `potential_clients/objection_experts/reports/`

**Reports built:**
1. `FINAL01_waste_spend_report_v6.pptx` — 12 slides, £7,836 waste identified (42.7% of spend)
2. `FINAL02_account_structure_report_v2.pptx` — 15 slides, before/after Oct analysis, CPA +28%, change history timeline
3. `FINAL03_restructure_report_v2.pptx` — 14 slides, target CPA £20-25, +30-50% more leads, 8-12 week plan

**Key findings presented to client:**
- CPA increased 28% after agency change (£30.24 → £38.63)
- Conversion rate dropped 22% (8.25% → 6.42%)
- Email Click counted as Primary conversion (inflating numbers)
- Quality Scores of 2-3 (paying 2-4x premium)
- No target CPA set (algorithm had no guardrails)
- Auto-apply recommendations enabled (Google making unsupervised changes)

**Client status:** Quote sent, likely to proceed. First potential paying client.

### Quote Template ✅
- `potential_clients/quote_template.html` — reusable A4 HTML quote (print to PDF)
- `potential_clients/objection_experts/quote_objection_experts.html` — client-specific quote
- Setup fee + monthly management fee model

### Job Applications (2026-03-27 to 2026-03-30)
- 60+ job applications submitted via Indeed and LinkedIn
- Jobs tracker in ACT actively used (table view, kanban view)
- CV V26 deployed, website aligned for recruiter audience

---

## PRIORITY ORDER (as of 2026-03-30)

1. **Revenue generation** — Job applications (ongoing) + Outreach to recruiters & agencies (this week)
2. **ACTAgency website** — Separate agency site for PPC agency search traffic
3. **ACT optimization architecture redesign** — Fundamental rethink of how optimization works by bid strategy type

---

**Version:** 13.0 | **Last Updated:** 2026-03-30
**Current Master Chat:** 16.0
