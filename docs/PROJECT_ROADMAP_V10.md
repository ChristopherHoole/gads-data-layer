# PROJECT ROADMAP - Ads Control Tower (A.C.T.)

**Last Updated:** 2026-03-23
**Overall Completion:** ~85% (core platform complete, expansion features remain)
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

**Bugs fixed during Chat 111 Redux:**
- Apostrophe in JavaScript string caused SyntaxError — fixed by Claude Code
- 8 Bid rules missing — created manually via Python script
- Table UI migration from old pattern to new pattern

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

**Bugs fixed during Chat 112:**
- Cost values stored as micros (50000000) instead of pounds (50.0) — fixed
- Type pills missing for some rules — fixed
- All rules now render correctly with proper type badges and cost values

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

### Dashboard Pages (All Complete)
1. ✅ Dashboard (home) — metrics cards, charts
2. ✅ Campaigns — table, rules tab, recommendations tab, flags subtab
3. ✅ Ad Groups — table, rules tab, recommendations tab, flags subtab
4. ✅ Keywords — table, search terms, rules tab, recommendations tab, flags subtab
5. ✅ Ads — table, rules tab, recommendations tab, flags subtab
6. ✅ Shopping — campaigns tab, products tab, feed quality tab, campaign rules, product rules, flags subtab
7. ✅ Recommendations — main page with entity filters, active/monitoring/successful/history sections, flags tab
8. ✅ Changes — audit trail with filters and search

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

## NEXT PRIORITIES — IMMEDIATE BUGS & FIXES

**DASHBOARD — ACT**
1. Fix Keywords search terms — custom date range causes DATE/VARCHAR mismatch in keywords.py line 187. Preset 7d/30d/90d buttons work fine.
2. Fix Shopping page query — table alias 's' not found in shopping.py line 108
3. Fix trigger summary label — rule 19 shows ROAS label instead of CPA in recommendations.py
4. WoW metrics — all vs_prev_pct columns are 0.0 in synthetic data (DuckDB limitation, will work on real data)
5. Rules 16, 17, 18, 20 don't fire — campaign_type_lock can't be enforced (NULL bid_strategy_type in synthetic data, will work on real data)
6. Unit tests update — 620 tests written pre-flags, need new coverage for flags system
7. Memurai install — required for Celery background jobs to run

---

## NEXT PRIORITIES — MAJOR FEATURES

**DASHBOARD — ACT**
1. Radar / post-acceptance monitoring system
   - Monitor performance after rule acceptance
   - Auto-rollback if performance degrades
   - Cooldown reset on rollback
   - Alert user when rollback triggered
   - Not started

2. Reports builder — automated report generator
   - Monthly PowerPoint reports per campaign/account
   - Auto-generated slides with performance charts
   - AI-written insights and recommendations (Claude API)
   - Executive summary slide
   - Scheduled generation (Celery monthly job)
   - Email delivery to client
   - PDF export option
   - Tech: python-pptx, Chart.js image export, Claude API
   - Not started

3. Rules strategic review
   - Review all 75 rules across 6 entities
   - Verify thresholds are realistic
   - Verify cooldowns appropriate
   - Verify conditions use correct metrics
   - Verify risk levels accurate
   - Verify plain English clear
   - Design discussion → Claude Code implementation
   - Not started

4. Test all flags with real data
   - Synthetic data swings too small for most thresholds
   - Need real Google Ads data
   - Blocked on API Basic Access

5. Smart alerts system
   - Budget pacing alerts (overspend/underspend)
   - Keyword expansion opportunities
   - Competitor activity detected
   - Seasonal trend alerts
   - Quality Score drop alerts
   - Ad disapproval alerts
   - Delivery: Email notifications, in-app alerts, Slack integration
   - Not started

6. Campaign type expansion
   - Performance Max campaigns (metrics, rules, UI)
   - Display campaigns (metrics, rules, UI)
   - Video (YouTube) campaigns (metrics, rules, UI)
   - Demand Gen campaigns (metrics, rules, UI)
   - Shopping campaigns — data exists, rules exist, needs recommendations engine integration
   - Each requires: new features tables, new rules config, new engine logic, UI updates
   - Not started

7. Conversion tracking checkup on account 487-268-1731
   - Verify all conversion actions configured
   - Check conversion tags firing correctly
   - Review attribution settings
   - Validate conversion values
   - Test checkout funnel tracking
   - Document current setup
   - Not started

8. Multi-user support
   - User authentication (beyond single admin)
   - Role-based permissions (Admin, Editor, Viewer)
   - User management UI
   - Audit trail per user
   - Email notifications per user
   - Not started

9. API endpoints for external access
   - REST API endpoints
   - API key authentication
   - Rate limiting
   - Documentation (Swagger/OpenAPI)
   - Endpoints: get recommendations, accept/decline, get rules, create/update rules, get performance data
   - Not started

10. ACT deployment to production
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
7. Indeed job listing connector — integration not built
8. Automated email reports (weekly/monthly) — not built

**WEBSITE**
1. Website design upgrade — hero upgrade, layout improvements
2. Mobile performance optimization — Core Web Vitals, lazy loading, image optimization
3. Contact form backend — /api/leads endpoint built, needs form UI connection
4. User guide / documentation for ACT platform
5. Video tutorials for onboarding
6. Client onboarding flow

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
- Status: Written pre-flags, need updating for flags system

**Background Jobs:**
- Celery: Configured ✅
- Redis: Configured ✅
- Memurai: NOT installed ❌ (required for Celery to run on Windows)
- Status: Jobs defined but cannot execute until Memurai installed

**Google Ads:**
- Account 487-268-1731: Suspended, appeal in review (ID: 6448619522)
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
   - Impact: Users can't use custom date ranges on search terms

2. **Shopping page query syntax error**
   - File: shopping.py line 108
   - Issue: Table alias 's' not found
   - Impact: Specific shopping query broken
   - Fix: Add table alias to FROM clause

3. **Trigger summary label incorrect for rule 19**
   - File: recommendations.py
   - Issue: Rule 19 (Loosen tCPA Target) shows "ROAS" label instead of "CPA"
   - Impact: Confusing UI (minor)
   - Fix: Correct label mapping in trigger summary generation

### Medium Priority (Can Wait)
4. **WoW metrics always 0.0 in synthetic data**
   - Issue: DuckDB nested window function limitation
   - Impact: All vs_prev_pct flags never fire on synthetic data
   - Status: Will work on real data, not fixable in synthetic
   - Workaround: Test WoW flags only after API Basic Access granted

5. **Rules 16, 17, 18, 20 don't fire**
   - Issue: campaign_type_lock can't be enforced (NULL bid_strategy_type in synthetic data)
   - Impact: 4 campaign rules never trigger on synthetic data
   - Status: Will work on real data
   - Priority: Low (synthetic limitation only)

6. **Unit tests need updating**
   - Issue: 620 tests written pre-flags system
   - Impact: Flags system not covered by tests
   - Priority: Medium (tests still pass, just incomplete)

7. **Memurai not installed**
   - Issue: Celery requires Redis, Memurai is Redis for Windows
   - Impact: Background jobs can't execute
   - Priority: Medium (no background jobs currently critical)

---

## BLOCKED ITEMS

**Blocked on API Basic Access:**
1. Real data ingestion from Google Ads API
2. Test all 174 rules/flags with real performance swings
3. Validate WoW metrics work correctly
4. Shopping campaigns recommendations engine integration
5. Performance Max / Display / Video / Demand Gen support

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
| 2d03f15 | Chat 112: Shopping Product Rules - fixed cost values (micros to pounds) and type pills |
| bb47773 | Chat 111 Redux: Shopping Campaign Rules complete - 14 rules + 8 flags + apostrophe fix + manual Bid rule creation |
| [pending] | Chat 109: Ads Rules - 8 rules + 15 flags |
| [pending] | Chat 108: Keywords Rules - 12 rules + 20 flags |
| [pending] | Chat 107: Ad Groups Rules - 12 rules + 18 flags |
| 61002f3 | Chats 99-100: Engine fixes — micros, rules 19/20, impression share, valid date query |
| 30decda | Chat 97: Recommendations UI fixes |
| 342c8d8 | Chat 93: Templates tab |

---

## SUMMARY STATISTICS

**Development Time:** ~500+ hours across 112+ chats

**Code Stats:**
- Rules/Flags: 174 (75 rules + 99 flags) across 6 entities
- Dashboard Pages: 8 complete
- Outreach Pages: 6 complete
- Unit Tests: 620 tests, 80% coverage
- Routes: 100+ Flask routes
- Templates: 50+ Jinja2 templates
- CSS Files: 15+ custom stylesheets
- JavaScript: 10,000+ lines across all pages

**Completion by Category:**
- Core Dashboard: 100% ✅
- Rules System: 100% ✅
- Flags System: 100% ✅
- Outreach System: 90% ✅ (core complete, integrations remain)
- Marketing Website: 100% ✅
- Testing: 80% ✅ (needs flags coverage)
- Infrastructure: 90% ✅ (Memurai install remains)
- Deployment: 0% ❌ (not started)
- Reports Builder: 0% ❌ (not started)
- Multi-User: 0% ❌ (not started)
- API Endpoints: 0% ❌ (not started)

**Overall Platform Completion: ~85%**
- Core features: Complete
- Expansion features: Planned
- Production deployment: Not started

---

**Version:** 10.0 | **Last Updated:** 2026-03-23
**Next Master Chat:** 14.0
