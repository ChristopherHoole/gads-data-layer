# MASTER KNOWLEDGE BASE - ADS CONTROL TOWER (A.C.T)

**Version:** 2.0  
**Created:** 2026-02-19  
**Purpose:** Complete project context for Master Chat 2.0  
**Audience:** Master Chat (coordination & diagnosis), not workers

---

## ðŸ“‹ TABLE OF CONTENTS

1. [Executive Summary](#executive-summary)
2. [Project Vision & Goals](#project-vision--goals)
3. [Complete Chat History](#complete-chat-history)
4. [System Architecture](#system-architecture)
5. [Database Schema](#database-schema)
6. [Key Files & Purposes](#key-files--purposes)
7. [How Things Work](#how-things-work)
8. [Rules Engine](#rules-engine)
9. [Dashboard UI (Chat 21)](#dashboard-ui-chat-21)
10. [Common Problems & Solutions](#common-problems--solutions)
11. [Important Documents](#important-documents)
12. [Current Status](#current-status)
13. [Future Roadmap](#future-roadmap)

---

## ðŸŽ¯ EXECUTIVE SUMMARY

### What is A.C.T?
**Ads Control Tower (A.C.T)** is a production-ready, automated Google Ads management platform that:
- Analyzes campaign performance using DuckDB analytics
- Generates optimization recommendations via rules engine
- Executes changes through Google Ads API
- Provides web dashboard for approval/monitoring
- Supports multi-client agency operations

### Current State (Feb 19, 2026)
- **Overall Completion:** ~82%
- **Phase:** Chat 21 COMPLETE ✅ — Next: Big Dashboard Overhaul (scope TBD)
- **Production Status:** Foundation + Polish + Full Dashboard UI complete
- **Active Development:** Planning next phase

### Tech Stack
- **Backend:** Python 3.11, Flask
- **Database:** DuckDB (analytics + readonly)
- **API:** Google Ads API (v15)
- **Frontend:** Bootstrap 5, Chart.js, Vanilla JS
- **Rules:** Python dataclasses, Constitution framework
- **Execution:** Dry-run + Live modes with rollback

---

## ðŸš€ PROJECT VISION & GOALS

### Mission Statement
Build a production-ready, automated Google Ads management dashboard that generates, approves, and executes bid/budget recommendations across Keywords, Ads, and Shopping campaigns.

### Core Features
1. **Multi-Client Support:** Agency-ready with per-client configs
2. **Real-Time Recommendations:** Rules engine generates optimization suggestions
3. **Approval Workflows:** Human-in-the-loop with risk tiering
4. **Automated Execution:** Dry-run testing, then live execution
5. **Change Tracking:** Full audit trail in DuckDB
6. **Rollback Capability:** Automatic rollback on performance degradation
7. **Email Reports:** (Planned) Daily/weekly performance summaries
8. **Smart Alerts:** (Planned) Anomaly detection + notifications
9. **Google Ads-Inspired UI:** Familiar interface for millions of users

### Success Criteria
- âœ… Generates accurate recommendations (100% test pass rate achieved)
- âœ… Executes changes safely (Constitution guardrails implemented)
- âœ… Tracks performance (change_log table operational)
- âœ… Multi-client capable (4 clients configured)
- â³ Professional UI (87.5% complete - 7/8 pages done, Chat 21h remaining)
- ðŸ“‹ Email reports (planned)
- ðŸ“‹ Smart alerts (planned)

---

## ðŸ“š COMPLETE CHAT HISTORY

### **Phase 0: Foundation (Chats 1-17)** âœ…

#### **Chats 1-11: Initial Dashboard Development**
**Time:** ~15-20 hours  
**Status:** Complete

**Deliverables:**
- Basic Flask web application with routes
- Multi-client YAML configuration system
- DuckDB integration for analytics
- Authentication system (admin/admin123)
- Dashboard home page with account stats
- Client switching functionality
- Session management (24-hour sessions)

**Key Files Created:**
- `act_dashboard/app.py` - Flask application
- `act_dashboard/config.py` - YAML config loader
- `act_dashboard/auth.py` - Login/logout logic
- `act_dashboard/routes.py` - Initial monolithic routes (later refactored)
- `act_dashboard/templates/` - Jinja2 templates

**Architecture:**
- Single-client initially
- Monolithic routes.py (1,731 lines)
- Direct DuckDB queries in routes
- No input validation
- No rate limiting
- No comprehensive logging

---

#### **Chats 12-16: Shopping & Execution Infrastructure**
**Time:** ~10-12 hours  
**Status:** Complete

**Chat 12: Shopping Module** â­
**Key Achievement:** Complete Shopping campaign optimization

**Deliverables:**
- 76 product-level features across 4 time windows (7d/14d/30d/90d)
- 14 Shopping-specific optimization rules
- 4-tab interactive dashboard (Campaigns, Products, Feed Quality, Recs)
- Shopping campaign data pipeline (Google Ads API â†’ DuckDB)
- Product performance analytics
- Feed quality monitoring
- ~3,800 lines of production code

**Files Created:**
- `src/shopping/features.py` - Feature engineering
- `src/shopping/diagnostics.py` - Performance diagnosis
- `act_autopilot/rules/shopping_rules.py` - 14 Shopping rules
- `act_dashboard/routes_shopping.py` - Dashboard routes
- `act_dashboard/templates/shopping.html` - 4-tab UI

**Database Tables:**
- `analytics.shopping_campaign_daily`
- `analytics.product_features_daily`
- `analytics.feed_quality_daily`

---

**Chat 13.1: Execution Engine** â­
**Key Achievement:** Constitution-based execution framework

**Deliverables:**
- Complete execution engine with Google Ads API integration
- Constitution framework (safety guardrails)
- Risk tiering (Low/Medium/High)
- Confidence scoring system
- Cooldown periods (7 days post-change)
- Data sufficiency gates
- Change logging to DuckDB
- Dry-run vs Live execution modes
- Rollback capability (manual + automatic triggers)

**Files Created:**
- `act_autopilot/executor.py` - Main execution engine
- `act_autopilot/constitution.py` - Safety constraints
- `act_autopilot/risk_tier.py` - Risk assessment
- `docs/GAds_Project_Constitution_v0.2.md` - Governance document

**Constitution Highlights:**
- Data gates: Min 10 conversions (30d) for bid changes
- Change limits: Max 30% budget increase, 20% bid change
- Cooldowns: 7 days between changes on same entity
- Spend caps: Enforced daily + monthly limits
- Protected entities: Brand campaigns immutable by default
- Kill switch: Emergency stop on critical KPI regression

---

**Chat 14: Dashboard Execution UI**
**Time:** 5-6 hours  
**Status:** Complete (UI), backend integration deferred

**Deliverables:**
- Execute buttons (individual + batch)
- Toast notification system
- Confirmation modals (live execution only)
- Results display with error handling
- Change history page with filters
- Status indicators
- 9-step implementation complete

**Files Modified:**
- `act_dashboard/templates/base.html` - Toast + modal system
- `act_dashboard/routes.py` - API endpoints for execution
- All page templates - Execute buttons added

**Known Issues:**
- Recommendations from JSON files vs live generation mismatch
- Executor dict/object compatibility needs fixing
- Backend integration deferred to Chat 15

---

**Chat 17: Architecture Refactor (Master Chat)** â­
**Time:** 3-4 hours  
**Status:** Complete

**Key Achievement:** Unified recommendation system

**Problem:**
- Dual recommendation systems (shopping vs keywords/ads)
- Schema mismatches causing execution failures
- Inconsistent data structures across modules

**Solution:**
- Created standardized `shopping_rules.py`
- Unified recommendation schema across all campaign types
- Fixed format mismatches
- Comprehensive codebase analysis (21 issues identified)
- Created 3-phase cleanup roadmap

**Deliverables:**
- `act_autopilot/rules/shopping_rules.py` - Shopping rules (14 rules, fully implemented)
- Codebase analysis document (21 issues)
- Phase 1-3 cleanup plan
- Foundation hardening strategy

---

### **Phase 1: Code Cleanup & Foundation Hardening** âœ…

**Time:** ~4 hours  
**Commits:** 5 major commits  
**Status:** Complete

#### **Phase 1a-1d: Routes Split into Blueprints**
**Commits:** e291e70, 2e28da6, 10fa943, 4b372d3

**Problem:** Monolithic routes.py (1,731 lines) was unmaintainable

**Solution:** Split into 8 modular blueprints

**Blueprints Created:**
1. **auth.py** - Login, logout, client switching
2. **api.py** - Execute, batch, status, approve, reject
3. **keywords.py** - Keywords page + search terms
4. **ads.py** - Ads page + asset performance
5. **shopping.py** - 4-tab Shopping interface
6. **dashboard.py** - Home page with stats
7. **recommendations.py** - Recommendations page
8. **settings.py** - Settings + config editor

**Supporting Files:**
- `routes/shared.py` - Helper functions
- `routes/__init__.py` - Blueprint registration

**Metrics:**
- Routes migrated: 16/16 (100%)
- Lines removed: 1,745
- Lines added: 350+ (cleaner, modular code)
- Modules created: 8 blueprint files

---

#### **Phase 1e: Input Validation**
**Commit:** ed73d3d  
**Time:** 45 minutes

**Deliverables:**
- `act_dashboard/validation.py` - Comprehensive validation
- Action type whitelist (KEYWORD_BID, KEYWORD_PAUSE, etc.)
- Batch size limits (max 100 recommendations)
- Type safety for all inputs
- Clear error messages

---

#### **Phase 1f: Rate Limiting**
**Commit:** (included in Phase 1 work)  
**Time:** 45 minutes

**Deliverables:**
- Flask-Limiter integration
- 10 requests/minute on `/api/execute-recommendation`
- 5 requests/minute on `/api/execute-batch`
- Sliding window algorithm
- 429 error handling

---

#### **Phase 1g: Logging**
**Time:** 45 minutes

**Deliverables:**
- RotatingFileHandler (10MB per file, 10 backups)
- Logs to `logs/dashboard.log`
- Execution tracking with user IP addresses
- Error logging with stack traces
- Request/response logging for API endpoints

---

#### **Phase 1h: Cache Expiration**
**Time:** 1 hour

**Deliverables:**
- `act_dashboard/cache.py` - ExpiringCache class (170 lines)
- 1-hour TTL (time-to-live)
- Dict-like syntax support
- Prevents memory leaks
- Thread-safe implementation

---

#### **Phase 1i: Error Handling**
**Commit:** 01bd80e  
**Time:** 35 minutes

**Deliverables:**
- Centralized 404/500/429 error handlers
- Consistent error format (JSON for API, HTML for pages)
- Enhanced logging on errors
- User-friendly error messages

---

### **Phase 2: Polish & Refactoring** âœ…

**Time:** ~2.5 hours  
**Commits:** 3 major commits  
**Status:** Complete

#### **Phase 2a: Extract Duplicate Code**
**Time:** 1 hour

**Deliverables:**
- Created 5 helper functions in `routes/shared.py`
- Eliminated 5 duplicate patterns:
  1. Database connection
  2. Config loading
  3. Date parameter parsing
  4. Pagination logic
  5. Error response formatting
- DRY principle applied across all routes

---

#### **Phase 2b: Refactor Long Functions**
**Time:** 1 hour

**Deliverables:**
- Created 17 helper functions across 3 files
- Main route functions: 269 lines â†’ 76 lines (72% reduction)
- Single Responsibility Principle enforced
- Improved readability and testability

---

#### **Phase 2c: Add Type Hints**
**Time:** 30 minutes

**Deliverables:**
- Added type hints to 4 route files
- Better IDE support (autocomplete, error detection)
- Self-documenting code
- Foundation for future static type checking

---

#### **Phase 2d: Config Validation**
**Time:** 1 hour  
**Status:** TESTED âœ…

**Deliverables:**
- `act_dashboard/config_validator.py` (263 lines)
- Validates all YAML configs on startup
- Checks required fields (client_id, customer_id, db_path, etc.)
- Validates enum values (automation_mode, risk_tolerance)
- Clear, actionable error messages
- Warnings vs blocking errors

**Validation Rules:**
- Required fields: client_id, customer_id, db_path
- Valid automation_modes: ['auto_approve', 'full_auto', 'suggest']
- Valid risk_tolerances: ['aggressive', 'conservative', 'moderate']
- Catches typos and missing configs before runtime

---

### **Chat 21: Dashboard UI Overhaul** â³ (IN PROGRESS - 62.5%)

**Framework:** Bootstrap 5.3  
**Icons:** Bootstrap Icons 1.11  
**Timeline:** 20 hours / 3 days  
**Status:** 5/8 pages complete

#### **Chat 21a: Bootstrap Setup** âœ…
**Time:** 50 minutes (vs 2 hrs estimated)  
**Commit:** 5789628

**Deliverables:**
- Created `templates/base_bootstrap.html` - New base template
- Integrated Bootstrap 5.3.0 via CDN
- Integrated Bootstrap Icons 1.11
- Dark sidebar navigation with collapsible sections
- Top navbar (client selector, date picker, user menu)
- Responsive design (mobile + desktop)
- Custom CSS overrides in `static/css/custom.css`

**Components Created:**
- Reusable sidebar navigation
- Metrics bar layout structure
- Modal and toast foundations

---

#### **Chat 21b: Main Dashboard Redesign** âœ…
**Time:** 53 minutes (vs 3 hrs estimated)  
**Commit:** 4976a29

**Deliverables:**
- Redesigned home page with Bootstrap 5
- 6 metrics cards (campaigns, spend, conversions, ROAS, CPA, CTR)
- Performance trend chart (Chart.js)
- Recent recommendations table (last 5)
- Quick actions panel
- Account health indicators
- Responsive layout (stacks on mobile)

**Files Modified:**
- `templates/dashboard.html` â†’ Bootstrap 5 version
- `routes/dashboard.py` â†’ Updated data loading

---

#### **Chat 21c: Campaigns View + Rule Visibility System** âœ…
**Time:** 100 minutes (vs 2 hrs estimated)  
**Commit:** 3ab82a2

**Key Achievement:** Built reusable rules visibility system

**Deliverables:**
- Complete Campaigns page from scratch (NEW)
- `routes/campaigns.py` - New blueprint (250 lines)
- `templates/campaigns.html` - Bootstrap 5 template (450 lines)
- 6 metrics cards (campaigns, budget, spend, clicks, conversions, CTR)
- 12-column responsive table
- Status badges (ENABLED=green, PAUSED=gray, REMOVED=red)
- Campaign type badges
- Budget utilization bars
- Pagination (10/25/50/100 rows)
- **Rules visibility system** (sidebar, tab, card)

**Rules Integration:** â­
- Dynamic category detection from rule IDs
- Regex pattern matching (CAMP-, KW-, AD-, SHOP-)
- Sidebar shows active rules count
- Tab shows rule breakdown
- Card shows "no rules" empty state
- Reusable across all entity pages

**Campaign Rules Working:**
- 8 campaign rules displaying correctly
- CAMP-BUDGET-001, CAMP-BID-002, CAMP-PAUSE-003, etc.
- Grouped by category (budget, bid, status)
- Color-coded by risk tier

---

#### **Chat 21d: Keywords View + Full Rule Integration** âœ…
**Time:** 125 minutes (vs 70 min estimated)  
**Commit:** f0fbd15

**Deliverables:**
- Complete Keywords page redesign
- `templates/keywords_new.html` (536 lines)
- 7 metrics cards (keywords, clicks, cost, conv., CPA, CTR, avg bid)
- 11-column table with Quality Score expansion UI
- Match type pills (Exact=blue, Phrase=green, Broad=yellow)
- QS color coding (8-10=green, 5-7=yellow, 1-4=red)
- Chevron icons for QS sub-columns (LP Exp, Ad Rel, Exp CTR)
- **14 keyword rules working correctly** â­
- Rules displayed in sidebar, tab, and card
- Search terms section (collapsible, not separate page)

**Rules Achievement:**
- KW-PAUSE-001 through KW-REVIEW-014 all displaying
- Sidebar title fix ("Keyword Rules" not "Campaign Rules")
- Category detection working perfectly
- Risk tier badges showing correctly

**Known Issues (Minor):**
- QS chevron click functionality pending (Chat 21e or later)
- Some duplicate columns in table (to clean up)

---

#### **Chat 21e: Ad Groups View** âœ…
**Time:** 120 minutes (vs 70 min estimated)  
**Commit:** [PENDING - completed overnight]

**Deliverables:**
- Complete Ad Groups page from scratch (NEW)
- `routes/ad_groups.py` - New blueprint (264 lines)
- `templates/ad_groups.html` - Bootstrap 5 template (368 lines)
- 7 metrics cards (Total, Clicks, Cost, Conv., CPA, CTR, Avg Bid)
- 12-column responsive table with 400 ad groups
- Color-coded CPA (green <$25, yellow $25-50, red >$50)
- Status badges (green=Active, gray=Paused, red=Removed)
- Filters: Date (7/30/90d), Status (all/active/paused), Per-page (10/25/50/100)
- Python-based pagination
- Rules integration (empty state - 0 rules correct)

**Database Pattern:**
- Uses `ro.analytics.ad_group_daily` table
- SQL date filtering (same as campaigns.py)
- Aggregations: SUM(clicks, impressions, cost, conversions)
- Calculated fields: ctr, cpa, avg_bid

**Issues Encountered & Resolved:**
1. **Database table name:** `analytics.ad_group_daily` â†’ `ro.analytics.ad_group_daily` (5 min fix)
2. **Template inheritance:** `base.html` â†’ `base_bootstrap.html` (45 min diagnosis, 2 min fix)
3. **Unknown page_type warning:** Expected until ad_group_rules.py created (harmless)

**Testing:** All 8 success criteria passing âœ…

---

#### **Chat 21f: Ads View** ðŸ“‹ NEXT
**Estimated:** 70 minutes

**Plan:**
- Redesign existing ads.py page
- Bootstrap 5 template
- Ad strength progress bars
- Asset performance expandable rows
- Ad type badges (RSA/ETA)
- Preview modal
- Rules integration (11 ad rules)

---

#### **Chat 21g: Shopping View** ðŸ“‹ PLANNED
**Estimated:** 90 minutes

**Plan:**
- Redesign existing 4-tab Shopping page
- Bootstrap 5 tabs component
- Product images in table
- Feed quality issue badges
- ROAS color coding
- Rules integration (14 Shopping rules)

---

#### **Chat 21h: Charts & Polish** ðŸ“‹ PLANNED
**Estimated:** 60 minutes

**Plan:**
- Standardize Chart.js colors
- Add loading spinners
- Fix responsive issues
- Cross-browser testing
- Bug fixes

---

## ðŸ—ï¸ SYSTEM ARCHITECTURE

### **High-Level Overview**

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                      USER (WEB BROWSER)                      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                    â”‚ HTTP (port 5000)
                    â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                   FLASK WEB APPLICATION                      â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚  ROUTES (Blueprints)                                  â”‚   â”‚
â”‚  â”‚  â€¢ auth.py - Login/logout/client switching           â”‚   â”‚
â”‚  â”‚  â€¢ dashboard.py - Home page with metrics             â”‚   â”‚
â”‚  â”‚  â€¢ campaigns.py - Campaigns table (Chat 21c)         â”‚   â”‚
â”‚  â”‚  â€¢ ad_groups.py - Ad Groups table (Chat 21e)         â”‚   â”‚
â”‚  â”‚  â€¢ keywords.py - Keywords + search terms             â”‚   â”‚
â”‚  â”‚  â€¢ ads.py - Ads + asset performance                  â”‚   â”‚
â”‚  â”‚  â€¢ shopping.py - 4-tab Shopping interface            â”‚   â”‚
â”‚  â”‚  â€¢ recommendations.py - Recommendations page         â”‚   â”‚
â”‚  â”‚  â€¢ api.py - Execution API endpoints                  â”‚   â”‚
â”‚  â”‚  â€¢ settings.py - Settings editor                     â”‚   â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â”‚                                                               â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚  UTILITIES                                            â”‚   â”‚
â”‚  â”‚  â€¢ config.py - YAML config loader                    â”‚   â”‚
â”‚  â”‚  â€¢ config_validator.py - Startup validation          â”‚   â”‚
â”‚  â”‚  â€¢ validation.py - Input validation                  â”‚   â”‚
â”‚  â”‚  â€¢ cache.py - ExpiringCache (1hr TTL)                â”‚   â”‚
â”‚  â”‚  â€¢ auth.py - @login_required decorator               â”‚   â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                    â”‚
        â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
        â”‚                       â”‚
        â†“                       â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚    DUCKDB        â”‚    â”‚  GOOGLE ADS API  â”‚
â”‚  (Analytics)     â”‚    â”‚    (v15)         â”‚
â”‚                  â”‚    â”‚                  â”‚
â”‚ â€¢ campaign_daily â”‚    â”‚ â€¢ Campaign data  â”‚
â”‚ â€¢ keyword_daily  â”‚    â”‚ â€¢ Ad group data  â”‚
â”‚ â€¢ ad_daily       â”‚    â”‚ â€¢ Keyword data   â”‚
â”‚ â€¢ shopping_daily â”‚    â”‚ â€¢ Ad data        â”‚
â”‚ â€¢ change_log     â”‚    â”‚ â€¢ Execute changesâ”‚
â”‚ â€¢ ad_group_daily â”‚    â”‚                  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
        â†‘                       â†‘
        â”‚                       â”‚
        â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                    â”‚
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚              ACT OPTIMIZATION ENGINE                         â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚  DATA PIPELINE                                        â”‚   â”‚
â”‚  â”‚  src/gads_pipeline/v1_runner.py                       â”‚   â”‚
â”‚  â”‚  â€¢ pull_campaign_data()                               â”‚   â”‚
â”‚  â”‚  â€¢ pull_ad_group_data()                               â”‚   â”‚
â”‚  â”‚  â€¢ pull_keyword_data()                                â”‚   â”‚
â”‚  â”‚  â€¢ pull_ad_data()                                     â”‚   â”‚
â”‚  â”‚  â€¢ pull_shopping_data()                               â”‚   â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â”‚                                                               â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚  ANALYTICS (Feature Engineering)                      â”‚   â”‚
â”‚  â”‚  src/lighthouse/                                      â”‚   â”‚
â”‚  â”‚  â€¢ campaign_features.py                               â”‚   â”‚
â”‚  â”‚  â€¢ keyword_features.py                                â”‚   â”‚
â”‚  â”‚  â€¢ ad_features.py                                     â”‚   â”‚
â”‚  â”‚  src/shopping/features.py                             â”‚   â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â”‚                                                               â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚  DIAGNOSTICS                                          â”‚   â”‚
â”‚  â”‚  src/lighthouse/                                      â”‚   â”‚
â”‚  â”‚  â€¢ campaign_diagnostics.py                            â”‚   â”‚
â”‚  â”‚  â€¢ keyword_diagnostics.py                             â”‚   â”‚
â”‚  â”‚  â€¢ ad_diagnostics.py                                  â”‚   â”‚
â”‚  â”‚  src/shopping/diagnostics.py                          â”‚   â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â”‚                                                               â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚  RULES ENGINE (Autopilot)                             â”‚   â”‚
â”‚  â”‚  act_autopilot/rules/                                       â”‚   â”‚
â”‚  â”‚  â€¢ campaign_rules.py (8 rules)                        â”‚   â”‚
â”‚  â”‚  â€¢ keyword_rules.py (14 rules)                        â”‚   â”‚
â”‚  â”‚  â€¢ ad_rules.py (11 rules)                             â”‚   â”‚
â”‚  â”‚  act_autopilot/rules/shopping_rules.py (14 rules)            â”‚   â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â”‚                                                               â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚  EXECUTION ENGINE                                     â”‚   â”‚
â”‚  â”‚  act_autopilot/rules/                                       â”‚   â”‚
â”‚  â”‚  â€¢ executor.py - Main execution logic                 â”‚   â”‚
â”‚  â”‚  â€¢ constitution.py - Safety guardrails                â”‚   â”‚
â”‚  â”‚  â€¢ risk_tier.py - Risk assessment                     â”‚   â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### **Data Flow: Recommendation â†’ Execution**

```
1. USER REQUEST
   â†“
2. FLASK ROUTE (dashboard, campaigns, keywords, etc.)
   â†“
3. LOAD CONFIG (DashboardConfig from YAML)
   â†“
4. QUERY DUCKDB (analytics tables)
   â†“
5. APPLY DIAGNOSTICS (identify issues)
   â†“
6. RUN RULES ENGINE (generate recommendations)
   â†“
7. DISPLAY IN UI (Bootstrap 5 templates)
   â†“
8. USER CLICKS "EXECUTE" (individual or batch)
   â†“
9. API ENDPOINT (/api/execute-recommendation)
   â†“
10. VALIDATION (input validation, rate limiting)
    â†“
11. CONSTITUTION CHECK (safety guardrails)
    â†“
12. RISK TIER ASSESSMENT (low/medium/high)
    â†“
13. EXECUTOR.execute()
    â”œâ”€ DRY RUN: Simulate change, log, return success
    â””â”€ LIVE: Call Google Ads API, log to change_log
    â†“
14. RETURN RESULT TO UI (toast notification)
    â†“
15. MONITOR PERFORMANCE (change_log tracking)
    â†“
16. ROLLBACK IF NEEDED (manual or automatic)
```

---

## ðŸ’¾ DATABASE SCHEMA

### **Primary Database: warehouse.duckdb**

**Location:** Root directory (created by data pipeline)

#### **Table: analytics.campaign_daily**
**Purpose:** Daily campaign performance snapshots

```sql
CREATE TABLE analytics.campaign_daily (
    snapshot_date DATE,
    customer_id TEXT,
    campaign_id TEXT,
    campaign_name TEXT,
    campaign_type TEXT,  -- SEARCH, SHOPPING, PERFORMANCE_MAX
    status TEXT,  -- ENABLED, PAUSED, REMOVED
    budget_micros BIGINT,
    target_cpa_micros BIGINT,
    target_roas REAL,
    clicks INTEGER,
    impressions INTEGER,
    cost_micros BIGINT,
    conversions REAL,
    conversions_value REAL,
    -- Rolling window metrics
    clicks_w7_sum INTEGER,
    impressions_w7_sum INTEGER,
    cost_w7_sum BIGINT,
    conversions_w7_sum REAL,
    -- ... w14, w30, w90 windows
    PRIMARY KEY (snapshot_date, customer_id, campaign_id)
);
```

---

#### **Table: analytics.keyword_daily**
**Purpose:** Keyword performance with Quality Score

```sql
CREATE TABLE analytics.keyword_daily (
    snapshot_date DATE,
    customer_id TEXT,
    campaign_id TEXT,
    ad_group_id TEXT,
    keyword_id TEXT,
    keyword_text TEXT,
    match_type TEXT,  -- EXACT, PHRASE, BROAD
    status TEXT,
    max_cpc_micros BIGINT,
    quality_score INTEGER,  -- 1-10
    quality_score_landing_page INTEGER,
    quality_score_ad_relevance INTEGER,
    quality_score_expected_ctr INTEGER,
    clicks INTEGER,
    impressions INTEGER,
    cost_micros BIGINT,
    conversions REAL,
    conversions_value REAL,
    search_impression_share REAL,
    search_rank_lost_impression_share REAL,
    search_budget_lost_impression_share REAL,
    -- Rolling windows
    clicks_w7_sum INTEGER,
    -- ... etc
    PRIMARY KEY (snapshot_date, customer_id, keyword_id)
);
```

---

#### **Table: analytics.ad_daily**
**Purpose:** Ad performance and ad strength

```sql
CREATE TABLE analytics.ad_daily (
    snapshot_date DATE,
    customer_id TEXT,
    campaign_id TEXT,
    ad_group_id TEXT,
    ad_id TEXT,
    ad_type TEXT,  -- RESPONSIVE_SEARCH_AD, EXPANDED_TEXT_AD
    status TEXT,
    ad_strength TEXT,  -- POOR, AVERAGE, GOOD, EXCELLENT
    headlines_count INTEGER,
    descriptions_count INTEGER,
    final_url TEXT,
    clicks INTEGER,
    impressions INTEGER,
    cost_micros BIGINT,
    conversions REAL,
    conversions_value REAL,
    -- Rolling windows
    clicks_w7_sum INTEGER,
    -- ... etc
    PRIMARY KEY (snapshot_date, customer_id, ad_id)
);
```

---

#### **Table: analytics.ad_group_daily**
**Purpose:** Ad group performance (NEW - Chat 21e)

```sql
CREATE TABLE analytics.ad_group_daily (
    snapshot_date DATE,
    customer_id TEXT,
    campaign_id TEXT,
    campaign_name TEXT,
    ad_group_id TEXT,
    ad_group_name TEXT,
    ad_group_type TEXT,  -- SEARCH_STANDARD, SHOPPING_PRODUCT_ADS
    status TEXT,  -- ENABLED, PAUSED, REMOVED
    cpc_bid_micros BIGINT,
    target_cpa_micros BIGINT,  -- Can be NULL
    target_roas REAL,
    clicks INTEGER,
    impressions INTEGER,
    cost_micros BIGINT,
    conversions REAL,
    conversions_value REAL,
    -- Calculated fields (computed in query)
    ctr REAL,  -- clicks / impressions
    cpa REAL,  -- cost / conversions
    PRIMARY KEY (snapshot_date, customer_id, ad_group_id)
);
```

---

#### **Table: analytics.shopping_campaign_daily**
**Purpose:** Shopping campaign metrics

```sql
CREATE TABLE analytics.shopping_campaign_daily (
    snapshot_date DATE,
    customer_id TEXT,
    campaign_id TEXT,
    campaign_name TEXT,
    status TEXT,
    budget_micros BIGINT,
    target_roas REAL,
    clicks INTEGER,
    impressions INTEGER,
    cost_micros BIGINT,
    conversions REAL,
    conversions_value REAL,
    roas REAL,  -- conversions_value / cost
    -- Rolling windows
    clicks_w7_sum INTEGER,
    -- ... etc
    PRIMARY KEY (snapshot_date, customer_id, campaign_id)
);
```

---

#### **Table: analytics.product_features_daily**
**Purpose:** Product-level Shopping performance

```sql
CREATE TABLE analytics.product_features_daily (
    snapshot_date DATE,
    customer_id TEXT,
    campaign_id TEXT,
    product_id TEXT,
    product_title TEXT,
    product_brand TEXT,
    max_cpc_micros BIGINT,
    clicks INTEGER,
    impressions INTEGER,
    cost_micros BIGINT,
    conversions REAL,
    conversions_value REAL,
    roas REAL,
    -- 76 engineered features across 4 time windows
    clicks_w7_sum INTEGER,
    clicks_w14_sum INTEGER,
    clicks_w30_sum INTEGER,
    clicks_w90_sum INTEGER,
    -- ... cost, conversions, value for each window
    -- ... trend features, volatility, efficiency metrics
    PRIMARY KEY (snapshot_date, customer_id, product_id)
);
```

---

#### **Table: analytics.feed_quality_daily**
**Purpose:** Merchant Center feed issues

```sql
CREATE TABLE analytics.feed_quality_daily (
    snapshot_date DATE,
    customer_id TEXT,
    product_id TEXT,
    approval_status TEXT,  -- APPROVED, DISAPPROVED, PENDING
    disapproval_reasons TEXT,  -- JSON array of reasons
    missing_attributes TEXT,  -- JSON array of missing fields
    price_mismatch BOOLEAN,
    availability_mismatch BOOLEAN,
    image_quality_issues BOOLEAN,
    PRIMARY KEY (snapshot_date, customer_id, product_id)
);
```

---

#### **Table: analytics.change_log**
**Purpose:** Audit trail of all executed changes

```sql
CREATE TABLE analytics.change_log (
    change_id TEXT PRIMARY KEY,  -- UUID
    timestamp TIMESTAMP,
    customer_id TEXT,
    campaign_id TEXT,
    campaign_name TEXT,
    entity_type TEXT,  -- CAMPAIGN, AD_GROUP, KEYWORD, AD, PRODUCT
    entity_id TEXT,
    entity_name TEXT,
    action_type TEXT,  -- BUDGET_CHANGE, BID_CHANGE, STATUS_CHANGE
    lever TEXT,  -- budget, bid, status, creative
    before_value TEXT,
    after_value TEXT,
    change_amount REAL,
    change_percent REAL,
    rule_id TEXT,
    confidence_score REAL,
    risk_tier TEXT,  -- LOW, MEDIUM, HIGH
    dry_run BOOLEAN,
    approved_by TEXT,
    executed_by TEXT,
    execution_mode TEXT,  -- DRY_RUN, LIVE
    status TEXT,  -- PENDING, SUCCESS, FAILED, ROLLED_BACK
    error_message TEXT,
    rollback_trigger TEXT,  -- CPA_DEGRADATION, CONV_DROP, MANUAL
    monitoring_end_date DATE,
    expected_impact TEXT,  -- JSON
    actual_impact TEXT  -- JSON (populated after monitoring period)
);
```

---

### **Readonly Database: warehouse_readonly.duckdb**

**Purpose:** Backup/snapshot for reporting  
**Contents:** Same tables as warehouse.duckdb  
**Access:** Read-only views in some queries (e.g., `ro.analytics.ad_group_daily`)

---

### **Indexes (Recommended but not yet implemented)**

**Performance optimization for common queries:**

```sql
-- Campaign queries (used in dashboard, campaigns page)
CREATE INDEX idx_campaign_daily_date ON analytics.campaign_daily(snapshot_date, customer_id);
CREATE INDEX idx_campaign_daily_id ON analytics.campaign_daily(customer_id, campaign_id);

-- Keyword queries (used in keywords page)
CREATE INDEX idx_keyword_daily_date ON analytics.keyword_daily(snapshot_date, customer_id);
CREATE INDEX idx_keyword_daily_qs ON analytics.keyword_daily(quality_score);
CREATE INDEX idx_keyword_daily_match ON analytics.keyword_daily(match_type);

-- Ad queries (used in ads page)
CREATE INDEX idx_ad_daily_date ON analytics.ad_daily(snapshot_date, customer_id);
CREATE INDEX idx_ad_daily_strength ON analytics.ad_daily(ad_strength);

-- Ad Group queries (used in ad groups page)
CREATE INDEX idx_ad_group_daily_date ON analytics.ad_group_daily(snapshot_date, customer_id);
CREATE INDEX idx_ad_group_daily_campaign ON analytics.ad_group_daily(campaign_id);

-- Change log queries (used in changes page, recommendations)
CREATE INDEX idx_change_log_date ON analytics.change_log(timestamp);
CREATE INDEX idx_change_log_entity ON analytics.change_log(entity_type, entity_id);
CREATE INDEX idx_change_log_status ON analytics.change_log(status);
```

---

## ðŸ“ KEY FILES & PURPOSES

### **Core Application Files**

```
act_dashboard/
â”œâ”€â”€ app.py                        # Flask application entry point
â”‚   â€¢ create_app(config_path)     # App factory
â”‚   â€¢ Blueprint registration
â”‚   â€¢ Error handler setup
â”‚   â€¢ Session config (24hr lifetime)
â”‚
â”œâ”€â”€ config.py                     # YAML config loader
â”‚   â€¢ DashboardConfig class
â”‚   â€¢ get_customer_id() - handles nested YAML
â”‚   â€¢ save() - writes config changes back
â”‚
â”œâ”€â”€ config_validator.py           # Startup validation (Phase 2d)
â”‚   â€¢ validate_config(yaml_path)
â”‚   â€¢ Check required fields
â”‚   â€¢ Validate enums
â”‚   â€¢ Clear error messages
â”‚
â”œâ”€â”€ auth.py                       # Authentication
â”‚   â€¢ check_credentials(user, pass)
â”‚   â€¢ @login_required decorator
â”‚   â€¢ Session management
â”‚
â”œâ”€â”€ validation.py                 # Input validation (Phase 1e)
â”‚   â€¢ validate_recommendation_id()
â”‚   â€¢ validate_action_type()
â”‚   â€¢ validate_batch_size()
â”‚
â”œâ”€â”€ cache.py                      # Expiring cache (Phase 1h)
â”‚   â€¢ ExpiringCache class
â”‚   â€¢ 1-hour TTL
â”‚   â€¢ Thread-safe
â”‚
â””â”€â”€ routes/                       # Blueprint modules
    â”œâ”€â”€ __init__.py               # Blueprint registration
    â”œâ”€â”€ shared.py                 # Helper functions (Phase 2a)
    â”œâ”€â”€ auth.py                   # Login/logout/client switch
    â”œâ”€â”€ dashboard.py              # Home page
    â”œâ”€â”€ campaigns.py              # Campaigns page (Chat 21c)
    â”œâ”€â”€ ad_groups.py              # Ad Groups page (Chat 21e)
    â”œâ”€â”€ keywords.py               # Keywords + search terms
    â”œâ”€â”€ ads.py                    # Ads + assets
    â”œâ”€â”€ shopping.py               # 4-tab Shopping UI
    â”œâ”€â”€ recommendations.py        # Recommendations page
    â”œâ”€â”€ api.py                    # Execution API endpoints
    â””â”€â”€ settings.py               # Settings editor
```

---

### **Templates (Jinja2)**

```
act_dashboard/templates/
â”œâ”€â”€ base_bootstrap.html           # NEW Bootstrap 5 base (Chat 21a)
â”‚   â€¢ Dark sidebar nav
â”‚   â€¢ Top navbar
â”‚   â€¢ Toast notification system
â”‚   â€¢ Confirmation modal
â”‚   â€¢ Chart.js integration
â”‚
â”œâ”€â”€ base.html                     # OLD base (pre-Bootstrap)
â”‚   â€¢ Simple HTML layout
â”‚   â€¢ No framework
â”‚   â€¢ Being phased out
â”‚
â”œâ”€â”€ components/                   # Reusable components
â”‚   â”œâ”€â”€ sidebar.html              # Navigation sidebar
â”‚   â”œâ”€â”€ navbar.html               # Top navbar
â”‚   â”œâ”€â”€ metrics_bar.html          # Metrics cards
â”‚   â”œâ”€â”€ rules_sidebar.html        # Rules panel (Chat 21c)
â”‚   â”œâ”€â”€ rules_tab.html            # Rules tab content
â”‚   â””â”€â”€ rules_card.html           # Rules summary card
â”‚
â”œâ”€â”€ dashboard.html                # Home page (Chat 21b)
â”œâ”€â”€ campaigns.html                # Campaigns page (Chat 21c)
â”œâ”€â”€ ad_groups.html                # Ad Groups page (Chat 21e)
â”œâ”€â”€ keywords_new.html             # Keywords page (Chat 21d)
â”œâ”€â”€ ads.html                      # Ads page (needs redesign)
â”œâ”€â”€ shopping.html                 # Shopping 4-tab (needs redesign)
â”œâ”€â”€ recommendations.html          # Recommendations page
â”œâ”€â”€ changes.html                  # Change history
â”œâ”€â”€ settings.html                 # Settings editor
â””â”€â”€ login.html                    # Login form
```

---

### **Static Assets**

```
act_dashboard/static/
â”œâ”€â”€ css/
â”‚   â””â”€â”€ custom.css                # Bootstrap 5 overrides
â”‚       â€¢ Sidebar styling
â”‚       â€¢ Metrics cards
â”‚       â€¢ Badge colors
â”‚       â€¢ Table hover effects
â”‚
â””â”€â”€ js/
    â”œâ”€â”€ tables.js                 # Table interactions
    â”‚   â€¢ Sorting
    â”‚   â€¢ Filtering
    â”‚   â€¢ Checkbox selection
    â”‚
    â””â”€â”€ charts.js                 # Chart.js configs
        â€¢ Performance trends
        â€¢ Distribution charts
        â€¢ Color schemes
```

---

### **Configuration Files**

```
configs/
â”œâ”€â”€ client_001.yaml               # Real client config
â”‚   â€¢ customer_id: "7372844356"
â”‚   â€¢ client_type: ecom
â”‚   â€¢ automation_mode: suggest
â”‚
â”œâ”€â”€ client_001_mcc.yaml           # MCC account config
â”‚   â€¢ Multiple sub-accounts
â”‚
â”œâ”€â”€ client_002.yaml               # Another client
â”‚   â€¢ customer_id: different
â”‚   â€¢ risk_tolerance: moderate
â”‚
â””â”€â”€ client_synthetic.yaml         # Test client
    â€¢ customer_id: "9999999999"
    â€¢ Used for development/testing
```

**Config Structure:**
```yaml
# Required fields
client_name: "Example Client"
client_id: "client_001"
customer_id: "1234567890"
db_path: "warehouse.duckdb"

# Optional but recommended
client_type: "ecom"  # ecom, lead_gen, mixed
primary_kpi: "roas"  # roas, cpa, conversions
automation_mode: "suggest"  # insights, suggest, auto_low_risk, auto_expanded
risk_tolerance: "moderate"  # conservative, moderate, aggressive

# Targets
target_roas: 3.0
target_cpa: 50.0

# Spend caps
daily_cap: 1000.0
monthly_cap: 30000.0

# Protected entities
brand_protected: true
protected_campaigns: ["Brand - Exact", "Brand - Phrase"]
```

---

### **Optimization Engine Files**

```
src/
â”œâ”€â”€ gads_pipeline/
â”‚   â””â”€â”€ v1_runner.py              # Data ingestion from Google Ads API
â”‚       â€¢ pull_campaign_data()
â”‚       â€¢ pull_ad_group_data()    # Added Chat 12
â”‚       â€¢ pull_keyword_data()
â”‚       â€¢ pull_ad_data()          # Added Chat 11
â”‚       â€¢ pull_shopping_data()    # Added Chat 12
â”‚
â”œâ”€â”€ lighthouse/                   # Analytics & Diagnostics
â”‚   â”œâ”€â”€ campaign_features.py      # Campaign feature engineering
â”‚   â”œâ”€â”€ campaign_diagnostics.py   # Campaign issue detection
â”‚   â”œâ”€â”€ keyword_features.py       # Keyword metrics
â”‚   â”œâ”€â”€ keyword_diagnostics.py    # Keyword issue detection
â”‚   â”œâ”€â”€ ad_features.py            # Ad metrics
â”‚   â””â”€â”€ ad_diagnostics.py         # Ad issue detection
â”‚
â”œâ”€â”€ autopilot/                    # Rules Engine & Execution
â”‚   â”œâ”€â”€ engine.py                 # Main autopilot orchestrator
â”‚   â”œâ”€â”€ campaign_rules.py         # 8 campaign optimization rules
â”‚   â”œâ”€â”€ keyword_rules.py          # 14 keyword optimization rules
â”‚   â”œâ”€â”€ ad_rules.py               # 11 ad optimization rules
â”‚   â”œâ”€â”€ executor.py               # Execution engine (Chat 13.1)
â”‚   â”œâ”€â”€ constitution.py           # Safety guardrails
â”‚   â””â”€â”€ risk_tier.py              # Risk assessment
â”‚
â””â”€â”€ shopping/                     # Shopping-specific (Chat 12)
    â”œâ”€â”€ features.py               # 76 product features
    â”œâ”€â”€ diagnostics.py            # Product issue detection
    â””â”€â”€ shopping_rules.py         # 14 Shopping rules (Chat 17)
```

---

### **Documentation Files**

```
docs/
â”œâ”€â”€ PROJECT_ROADMAP.md            # Overall project status
â”‚   â€¢ Phase tracking
â”‚   â€¢ Completion metrics
â”‚   â€¢ Future plans
â”‚
â”œâ”€â”€ DASHBOARD_PROJECT_PLAN.md     # Chat 21 detailed plan
â”‚   â€¢ 8-chat breakdown
â”‚   â€¢ UI specifications
â”‚   â€¢ Component details
â”‚
â”œâ”€â”€ CHAT_WORKING_RULES.md         # Mandatory rules for all chats
â”‚   â€¢ Rule 1: Upload codebase first
â”‚   â€¢ Rule 2: Request current file versions
â”‚   â€¢ Rule 3: Use full file paths
â”‚
â”œâ”€â”€ GAds_Project_Constitution_v0.2.md  # Governance document
â”‚   â€¢ Safety constraints
â”‚   â€¢ Data sufficiency gates
â”‚   â€¢ Change limits
â”‚   â€¢ Rollback policies
â”‚
â””â”€â”€ handoffs/                     # Chat handoff documents
    â”œâ”€â”€ CHAT_7_HANDOFF.md         # Dashboard initial build
    â”œâ”€â”€ CHAT_11_HANDOFF.md        # Ad optimization module
    â”œâ”€â”€ CHAT_12_HANDOFF.md        # Shopping module
    â”œâ”€â”€ CHAT_13.1_HANDOFF.md      # Execution engine
    â”œâ”€â”€ CHAT_14_HANDOFF.md        # Execution UI
    â”œâ”€â”€ CHAT_21C_HANDOFF.md       # Campaigns page
    â””â”€â”€ CHAT_21E_HANDOFF.md       # Ad Groups page (just created)
```

---

## âš™ï¸ HOW THINGS WORK

### **1. Application Startup**

```python
# Command: python -m act_dashboard.app configs/client_synthetic.yaml

1. Load config from YAML (config.py)
2. Validate config (config_validator.py) - Phase 2d
3. Create Flask app (app.py)
4. Register blueprints (__init__.py)
5. Initialize auth (auth.py)
6. Set up error handlers (Phase 1i)
7. Set up rate limiting (Phase 1f) - NOT YET IMPLEMENTED
8. Set up logging (Phase 1g)
9. Start server (host=0.0.0.0, port=5000, debug=True)
```

**Flask runs at:** http://localhost:5000

---

### **2. Authentication Flow**

```
1. User visits http://localhost:5000
2. @login_required decorator checks session['logged_in']
3. If not logged in: Redirect to /login
4. User enters credentials (admin / admin123)
5. auth.check_credentials(username, password)
6. If valid: session['logged_in'] = True, redirect to dashboard
7. If invalid: Flash error, show login form again
8. Session expires after 24 hours
9. User clicks Logout: Clear session, redirect to login
```

**Security Note:** Credentials stored in plaintext (environment variables or defaults). NOT production-ready. Needs bcrypt hashing + database storage.

---

### **3. Client Switching**

```
1. User selects client from navbar dropdown
2. GET /switch-client/<index>
3. Load new config path from app.config['AVAILABLE_CLIENTS']
4. Store in session['current_client_config']
5. Redirect to dashboard
6. All subsequent requests use get_current_config() helper
7. Helper loads config from session path
8. Each route gets isolated data for that client
```

**Multi-Client Isolation:**
- Each client has separate YAML config
- Each client has separate database (different customer_id)
- Session tracks currently selected client
- No cross-client data leakage

---

### **4. Dashboard Page Loading**

```
User visits: http://localhost:5000/

1. Route: dashboard.py â†’ dashboard_page()
2. @login_required checks session
3. get_current_config() loads client YAML
4. Open DuckDB connection (config.db_path)
5. Query campaign_daily for last 7 days:
   â€¢ COUNT(DISTINCT campaign_id) â†’ campaign_count
   â€¢ SUM(cost_micros) / 1M â†’ total_spend
   â€¢ SUM(conversions) â†’ total_conversions
   â€¢ SUM(conversions_value) / SUM(cost_micros) â†’ avg_roas
6. Query change_log for recent changes (last 7 days, limit 5)
7. Query campaign_daily grouped by date (last 30 days) â†’ trend_data
8. Count pending recommendations (load today's suggestions JSON)
9. Close DuckDB connection
10. Render dashboard.html with data
11. Chart.js renders performance trend chart
12. Bootstrap 5 styles metrics cards
```

**Query Example (Campaign Count):**
```sql
SELECT COUNT(DISTINCT campaign_id) as campaign_count
FROM analytics.campaign_daily
WHERE customer_id = '9999999999'
  AND snapshot_date >= CURRENT_DATE - INTERVAL '7 days'
```

---

### **5. Campaigns Page Loading (Chat 21c)**

```
User visits: http://localhost:5000/campaigns

1. Route: campaigns.py â†’ campaigns_page()
2. @login_required checks session
3. get_current_config() loads client YAML
4. Extract URL parameters:
   â€¢ days (default 7, options: 7/30/90)
   â€¢ page (default 1)
   â€¢ per_page (default 25, options: 10/25/50/100)
   â€¢ status (default 'all', options: all/active/paused)
5. Open DuckDB connection
6. Query ro.analytics.campaign_daily:
   â€¢ Filter: customer_id + date range (last N days)
   â€¢ GROUP BY campaign_id, campaign_name, status, type, budget
   â€¢ SUM(clicks, impressions, cost_micros, conversions, conversions_value)
   â€¢ Calculate: spend, ctr, cpa, roas
7. Apply status filter (if not 'all')
8. Calculate metrics bar (6 cards):
   â€¢ Total campaigns (count)
   â€¢ Total budget (sum)
   â€¢ Total spend (sum cost)
   â€¢ Total clicks (sum)
   â€¢ Total conversions (sum)
   â€¢ Average CTR (clicks / impressions)
9. Apply pagination (Python slice):
   â€¢ start_idx = (page - 1) * per_page
   â€¢ end_idx = start_idx + per_page
   â€¢ paginated = campaigns[start_idx:end_idx]
10. Load campaign rules using get_rules_for_page('campaign', customer_id)
11. Close DuckDB connection
12. Render campaigns.html with:
    â€¢ campaigns (paginated list)
    â€¢ metrics (6-card data)
    â€¢ rules (sidebar, tab, card data)
    â€¢ pagination (total_pages, current_page)
    â€¢ filters (days, status, per_page)
```

**Rules Loading:**
```python
from act_dashboard.routes.shared import get_rules_for_page

rules_data = get_rules_for_page('campaign', customer_id)
# Returns: {
#   'total_rules': 8,
#   'active_rules': ['CAMP-BUDGET-001', 'CAMP-BID-002', ...],
#   'grouped_rules': {
#     'budget': [...],
#     'bid': [...],
#     'status': [...]
#   }
# }
```

---

### **6. Ad Groups Page Loading (Chat 21e)**

```
User visits: http://localhost:5000/ad-groups

1. Route: ad_groups.py â†’ ad_groups()
2. @login_required checks session
3. get_current_config() loads client YAML
4. Extract URL parameters (same as campaigns)
5. Open DuckDB connection
6. Query ro.analytics.ad_group_daily:
   â€¢ Filter: customer_id + date range
   â€¢ GROUP BY ad_group_id, ad_group_name, campaign_id, status, bids
   â€¢ SUM(clicks, impressions, cost_micros, conversions)
   â€¢ Calculate: ctr, cpa, avg_bid
7. Apply status filter
8. Calculate metrics bar (7 cards):
   â€¢ Total ad groups
   â€¢ Total clicks
   â€¢ Total cost
   â€¢ Total conversions
   â€¢ Overall CPA
   â€¢ Overall CTR
   â€¢ Average bid
9. Apply pagination (Python slice)
10. Load rules using get_rules_for_page('ad_group', customer_id)
    â€¢ Returns empty (ad_group_rules.py doesn't exist yet)
    â€¢ Displays "0 rules" empty state âœ…
11. Close DuckDB connection
12. Render ad_groups.html
```

**Key Difference from Campaigns:**
- Uses `ro.analytics.ad_group_daily` (readonly database)
- NULL handling for target_cpa_micros (many ad groups don't have this)
- CPA color coding: green <$25, yellow $25-50, red >$50

---

### **7. Keywords Page Loading (Chat 21d)**

```
User visits: http://localhost:5000/keywords

1. Route: keywords.py â†’ keywords_page()
2. Load config, extract URL params
3. Query keyword_daily:
   â€¢ Join with ad_group and campaign tables for names
   â€¢ Filter by customer_id + date
   â€¢ Include quality_score and sub-metrics
4. Calculate metrics bar (7 cards)
5. Apply match type filter (if selected)
6. Apply pagination
7. Load keyword rules (14 rules display correctly) âœ…
8. Render keywords_new.html
```

**Quality Score Handling:**
```python
# Color coding in template
if qs >= 8: color = 'success' (green)
elif qs >= 5: color = 'warning' (yellow)
else: color = 'danger' (red)

# Sub-metrics (LP Experience, Ad Relevance, Expected CTR)
# Expandable UI (chevrons) - click functionality pending
```

---

### **8. Recommendation Generation**

**Two Modes:**

**Mode A: File-Based (Recommendations Page)**
```
1. User visits /recommendations or /recommendations/2026-02-19
2. Load suggestions JSON:
   â€¢ Path: reports/suggestions/{client_name}/{date}.json
   â€¢ Contains: List of recommendations with metadata
3. Load approvals JSON (if exists):
   â€¢ Path: reports/suggestions/{client_name}/approvals/{date}_approvals.json
   â€¢ Contains: User decisions (approved/rejected)
4. Group by risk tier (low/medium/high)
5. Mark each as approved/rejected/pending
6. Display in 3 risk tier sections
```

**Mode B: Live Generation (Keywords/Ads/Shopping)**
```
1. User clicks "Recommendations" tab on entity page
2. Route queries DuckDB for entity data
3. Route calls rules engine directly:
   â€¢ keyword_rules.apply_rules(keywords_data, config)
   â€¢ ad_rules.apply_rules(ads_data, config)
   â€¢ shopping_rules.apply_rules(products_data, config)
4. Rules engine returns recommendations list
5. Display immediately (no JSON file)
```

**Issue:** File-based vs Live mismatch causes execution problems (noted in Chat 14, deferred to Chat 15)

---

### **9. Recommendation Execution**

**Flow:**
```
1. User clicks "Execute" button (individual or batch)
2. JavaScript calls /api/execute-recommendation (POST)
3. Request body:
   {
     "date": "2026-02-19",
     "recommendation_id": 0,
     "dry_run": false
   }
4. API route: api.py â†’ execute_recommendation()
5. Load suggestions JSON
6. Extract recommendation by ID
7. Validate input (validation.py - Phase 1e)
8. Check rate limit (Flask-Limiter - Phase 1f)
9. Load config
10. Constitution check (constitution.py):
    â€¢ Data sufficiency gate
    â€¢ Change magnitude limit
    â€¢ Cooldown period check
    â€¢ Spend cap validation
11. Risk tier assessment (risk_tier.py)
12. Call executor.execute():
    â€¢ If dry_run: Simulate + log
    â€¢ If live: Call Google Ads API + log to change_log
13. Return JSON response:
    {
      "success": true,
      "change_id": "uuid-here",
      "message": "Change executed successfully"
    }
14. JavaScript shows toast notification
15. Update UI (mark as executed)
```

**Constitution Gates:**
```python
# Data sufficiency
if conversions_30d < 10:
    return {"blocked": True, "reason": "Insufficient conversions"}

# Change magnitude
if budget_increase_pct > 30:
    return {"blocked": True, "reason": "Exceeds 30% change limit"}

# Cooldown
if last_change_date >= today - 7 days:
    return {"blocked": True, "reason": "Cooldown period active"}
```

---

### **10. Rules Engine Architecture**

**Rule Structure (Standard):**
```python
@dataclass
class Recommendation:
    entity_type: str  # CAMPAIGN, KEYWORD, AD, PRODUCT
    entity_id: str
    entity_name: str
    campaign_id: str
    campaign_name: str
    rule_id: str  # CAMP-BUDGET-001, KW-PAUSE-003, etc.
    action_type: str  # BUDGET_CHANGE, BID_CHANGE, STATUS_CHANGE
    current_value: Any
    recommended_value: Any
    reasoning: str
    confidence: float  # 0.0 to 1.0
    risk_tier: str  # LOW, MEDIUM, HIGH
    expected_impact: dict  # {"metric": "CPA", "change": "-15%"}
    data_window: str  # "Last 30 days"
    priority: int  # 1-10
```

**Rule Categories:**

**Campaign Rules (8 total):**
- `CAMP-BUDGET-001`: Increase budget (lost IS > 20%)
- `CAMP-BUDGET-002`: Decrease budget (wasted spend)
- `CAMP-BID-003`: Increase target CPA (underperforming)
- `CAMP-BID-004`: Decrease target CPA (exceeding target)
- `CAMP-PAUSE-005`: Pause campaign (critical underperformance)
- `CAMP-ENABLE-006`: Enable paused campaign (recovered)
- `CAMP-ROAS-007`: Adjust target ROAS
- `CAMP-STATUS-008`: Monitor status changes

**Keyword Rules (14 total):**
- `KW-PAUSE-001`: Pause keyword (high cost, low conversions)
- `KW-PAUSE-002`: Pause keyword (low Quality Score)
- `KW-BID-003`: Increase bid (lost IS)
- `KW-BID-004`: Decrease bid (overpaying)
- `KW-REVIEW-005` through `KW-REVIEW-014`: Various review triggers

**Ad Rules (11 total):**
- `AD-PAUSE-001`: Pause ad (poor performance)
- `AD-PAUSE-002`: Pause ad (low CTR)
- `AD-PAUSE-003`: Pause ad (POOR RSA strength)
- `AD-REVIEW-001`: Review ad (AVERAGE RSA strength)
- `AD-REVIEW-002` through `AD-REVIEW-009`: Various review triggers

**Shopping Rules (14 total)** — `act_autopilot/rules/shopping_rules.py`:
- `SHOP-BID-001` through `SHOP-BID-005`: Product bid adjustments
- `SHOP-PAUSE-006` through `SHOP-PAUSE-008`: Product pausing
- `SHOP-FEED-009` through `SHOP-FEED-012`: Feed quality fixes
- `SHOP-REVIEW-013` through `SHOP-REVIEW-014`: Product reviews

---

### **11. Rules Display System (Chat 21c Innovation)** â­

**Dynamic Category Detection:**
```python
def get_rules_for_page(page_type, customer_id):
    """
    Detect rules for any page type using rule ID patterns.
    
    Patterns:
    - CAMP-* â†’ campaign rules
    - KW-* â†’ keyword rules
    - AD-* â†’ ad rules
    - SHOP-* â†’ shopping rules
    """
    # Load all rules from appropriate rules.py file
    if page_type == 'campaign':
        from act_autopilot import campaign_rules
        rules = campaign_rules.RULES
    elif page_type == 'keyword':
        from act_autopilot import keyword_rules
        rules = keyword_rules.RULES
    # ... etc
    
    # Extract rule IDs using regex
    pattern = get_pattern_for_page(page_type)  # e.g., r'^CAMP-'
    matching_rules = [r for r in rules if re.match(pattern, r.id)]
    
    # Group by category (extracted from rule ID)
    grouped = {}
    for rule in matching_rules:
        category = extract_category(rule.id)  # CAMP-BUDGET-001 â†’ budget
        grouped.setdefault(category, []).append(rule)
    
    return {
        'total_rules': len(matching_rules),
        'active_rules': [r.id for r in matching_rules],
        'grouped_rules': grouped
    }
```

**Display Components:**

**1. Sidebar (rules_sidebar.html):**
```html
<div class="rules-sidebar">
  <h5>Campaign Rules <span class="badge">8</span></h5>
  <button>View All Rules</button>
</div>
```

**2. Tab (rules_tab.html):**
```html
<ul class="nav nav-tabs">
  <li><a href="#campaigns">Campaigns (400)</a></li>
  <li><a href="#rules">Rules (8)</a></li>
</ul>
```

**3. Card (rules_card.html):**
```html
<div class="card">
  <div class="card-header">
    <i class="bi bi-lightning"></i> Active Optimization Rules
    <span class="badge">8 rules</span>
  </div>
  <div class="card-body">
    <h6>Budget Rules (3)</h6>
    <ul>
      <li>CAMP-BUDGET-001: Increase budget...</li>
      <li>CAMP-BUDGET-002: Decrease budget...</li>
    </ul>
    <h6>Bid Rules (2)</h6>
    ...
  </div>
</div>
```

**Empty State (when 0 rules):**
```html
<div class="empty-state">
  <i class="bi bi-inbox"></i>
  <p>No rules configured yet</p>
  <small>Optimization rules will appear here once configured</small>
</div>
```

---

## ðŸ”§ RULES ENGINE

### **Rule Execution Flow**

```
1. Data Loading
   â†“
2. Feature Engineering (lighthouse/)
   â€¢ Rolling window metrics (7d, 14d, 30d, 90d)
   â€¢ Trend calculations
   â€¢ Efficiency metrics
   â†“
3. Diagnostics (lighthouse/)
   â€¢ Issue detection (LOW_QS, WASTED_SPEND, etc.)
   â€¢ Performance classification (POOR, AVERAGE, GOOD)
   â†“
4. Rules Application (autopilot/)
   â€¢ Loop through all rules
   â€¢ Check applicability conditions
   â€¢ Generate recommendations
   â†“
5. Risk Assessment (risk_tier.py)
   â€¢ Calculate confidence score
   â€¢ Assign risk tier (LOW/MEDIUM/HIGH)
   â†“
6. Recommendation Delivery
   â€¢ Sort by priority
   â€¢ Group by risk tier
   â€¢ Display in UI
```

---

### **Rule Application Pattern**

**Example: CAMP-BUDGET-001 (Increase Budget)**

```python
def rule_camp_budget_001(campaign, config):
    """
    Increase budget when losing impression share due to budget.
    
    Conditions:
    - Search budget lost IS > 20%
    - Campaign is ENABLED
    - Spend is near daily budget (>90%)
    - ROI is positive (ROAS > target or CPA < target)
    
    Action:
    - Increase budget by 20-30% (depending on lost IS)
    
    Risk: LOW (budget increases are relatively safe)
    """
    # Check conditions
    if campaign.status != 'ENABLED':
        return None  # Skip disabled campaigns
    
    if campaign.search_budget_lost_is_30d < 0.20:
        return None  # Not losing enough impression share
    
    if campaign.spend_30d / campaign.budget < 0.90:
        return None  # Not constrained by budget
    
    # Check ROI is positive
    if config.primary_kpi == 'roas':
        if campaign.roas_30d < config.target_roas:
            return None  # ROI too low
    elif config.primary_kpi == 'cpa':
        if campaign.cpa_30d > config.target_cpa:
            return None  # CPA too high
    
    # Calculate recommendation
    lost_is = campaign.search_budget_lost_is_30d
    increase_pct = 0.20 if lost_is < 0.30 else 0.30
    
    current_budget = campaign.budget
    recommended_budget = current_budget * (1 + increase_pct)
    
    # Build recommendation
    return Recommendation(
        entity_type='CAMPAIGN',
        entity_id=campaign.campaign_id,
        entity_name=campaign.campaign_name,
        campaign_id=campaign.campaign_id,
        campaign_name=campaign.campaign_name,
        rule_id='CAMP-BUDGET-001',
        action_type='BUDGET_CHANGE',
        current_value=current_budget,
        recommended_value=recommended_budget,
        reasoning=f"Campaign losing {lost_is:.1%} impression share due to budget. "
                  f"Current spend is {campaign.spend_30d / current_budget:.1%} of budget. "
                  f"Increasing budget by {increase_pct:.0%} to capture more traffic.",
        confidence=0.85,  # High confidence (clear signal)
        risk_tier='LOW',  # Budget increases are safe
        expected_impact={
            'metric': 'Impressions',
            'change': f"+{lost_is * 100:.0f}%",
            'timeframe': '7-14 days'
        },
        data_window='Last 30 days',
        priority=8  # High priority (losing traffic)
    )
```

---

### **Constitution Enforcement**

**At Execution Time:**

```python
def check_constitution(recommendation, entity_data, config):
    """
    Apply Constitution guardrails before execution.
    
    Gates:
    1. Data sufficiency
    2. Change magnitude limits
    3. Cooldown periods
    4. Spend caps
    5. Protected entities
    """
    # Gate 1: Data sufficiency
    if recommendation.action_type == 'BID_CHANGE':
        if entity_data.conversions_30d < 10:
            return {
                'allowed': False,
                'reason': 'Insufficient data (need 10+ conversions in 30 days)'
            }
    
    # Gate 2: Change magnitude
    if recommendation.action_type == 'BUDGET_CHANGE':
        change_pct = abs(recommendation.recommended_value - recommendation.current_value) / recommendation.current_value
        if change_pct > 0.30:  # 30% limit
            return {
                'allowed': False,
                'reason': f'Change exceeds 30% limit ({change_pct:.1%})'
            }
    
    # Gate 3: Cooldown period
    last_change = get_last_change(recommendation.entity_id, recommendation.action_type)
    if last_change and (datetime.now() - last_change.timestamp).days < 7:
        return {
            'allowed': False,
            'reason': 'Cooldown period active (7 days required)'
        }
    
    # Gate 4: Spend caps
    if recommendation.action_type == 'BUDGET_CHANGE':
        projected_spend = calculate_projected_spend(recommendation.recommended_value)
        if projected_spend > config.monthly_cap:
            return {
                'allowed': False,
                'reason': f'Would exceed monthly cap ({config.monthly_cap})'
            }
    
    # Gate 5: Protected entities
    if is_protected(recommendation.entity_id, config):
        return {
            'allowed': False,
            'reason': 'Entity is protected (brand campaign or manually protected)'
        }
    
    # All gates passed
    return {
        'allowed': True,
        'reason': 'All Constitution checks passed'
    }
```

---

## ðŸŽ¨ DASHBOARD UI (CHAT 21)

### **Design Philosophy**

**Google Ads-Inspired (Not Clone):**
- Familiar layout patterns (sidebar, top metrics, tables)
- Similar UX flows (filtering, sorting, pagination)
- Recognizable color schemes (but not exact Google colors)
- **ACT branding** (not Google branding)

**Bootstrap 5 Advantages:**
- No build pipeline complexity (CDN)
- Battle-tested components
- Excellent documentation
- Responsive by default
- Easy maintenance

---

### **Layout Structure**

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ TOP NAVBAR                                                  â”‚
â”‚ [ACT Logo] [Client: Synthetic â–¼] [Date: Last 7d â–¼] [User â–¼]â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚          â”‚ METRICS BAR                                      â”‚
â”‚ LEFT     â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚ SIDEBAR  â”‚ â”‚Clicksâ”‚ Impr.â”‚ Cost â”‚ Conv.â”‚ ROAS â”‚ CPA  â”‚   â”‚
â”‚          â”‚ â”‚1,234 â”‚45.6K â”‚$1,234â”‚  56  â”‚ 3.2x â”‚  $22 â”‚   â”‚
â”‚ ðŸ  Dash  â”‚ â”‚+12%â†‘ â”‚ +5%â†‘ â”‚ +8%â†‘ â”‚ -3%â†“ â”‚+15%â†‘ â”‚ -5%â†“ â”‚   â”‚
â”‚ ðŸ“Š Camps â”‚ â””â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”˜   â”‚
â”‚ ðŸ“ AdGrp â”‚                                                  â”‚
â”‚ ðŸ”‘ KWs   â”‚ DATE RANGE & FILTERS                            â”‚
â”‚ ðŸ“ Ads   â”‚ [Last 7 days â–¼] [Search...] [Filters â–¼]        â”‚
â”‚ ðŸ›’ Shop  â”‚                                                  â”‚
â”‚ â”€â”€â”€â”€     â”‚                                                  â”‚
â”‚ ðŸ’¡ Recs  â”‚ MAIN CONTENT AREA                               â”‚
â”‚ ðŸ“œ Chgs  â”‚ (Tables, Charts, Cards)                         â”‚
â”‚ â”€â”€â”€â”€     â”‚                                                  â”‚
â”‚ âš™ï¸ Set   â”‚                                                  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

### **Component Inventory**

**Navigation:**
- **Dark Sidebar** - Fixed left, collapsible on mobile
- **Top Navbar** - Client selector, date picker, user menu
- **Breadcrumbs** - Current page location
- **Tabs** - Entity data vs Rules

**Metrics:**
- **Metrics Cards** - 6-7 cards per page (campaigns, clicks, cost, etc.)
- **Trend Indicators** - Green â†‘ (positive), Red â†“ (negative)
- **Progress Bars** - Budget utilization, Quality Score
- **Badges** - Status (ENABLED/PAUSED), Risk tier (LOW/MEDIUM/HIGH)

**Tables:**
- **Sortable Headers** - Click to sort ASC/DESC
- **Responsive** - Horizontal scroll on mobile
- **Pagination** - 10/25/50/100 rows per page
- **Checkbox Selection** - Bulk actions
- **Actions Dropdown** - Per-row actions (Edit/Pause/Remove)
- **Expandable Rows** - Quality Score sub-metrics, Asset performance

**Forms:**
- **Filters** - Date range, Status, Match type
- **Search Bar** - Entity name/ID search
- **Settings Editor** - YAML config UI

**Modals:**
- **Confirmation Modal** - "Are you sure?" for live execution
- **Preview Modal** - Ad preview, Asset details
- **Rules Modal** - Full rule details

**Notifications:**
- **Toast Notifications** - Success (green), Error (red)
- **Inline Alerts** - Info, Warning, Danger banners

**Charts:**
- **Line Charts** - Performance trends over time
- **Bar Charts** - Campaign comparison, Budget utilization
- **Pie Charts** - Ad type distribution, Match type breakdown
- **Histogram** - Quality Score distribution

---

### **Color Palette**

**Primary Colors:**
- **Blue** - `#0d6efd` (primary actions, links)
- **Green** - `#198754` (success, positive metrics)
- **Yellow** - `#ffc107` (warnings, medium metrics)
- **Red** - `#dc3545` (danger, negative metrics)

**Sidebar:**
- **Background** - `#212529` (dark gray)
- **Text** - `#f8f9fa` (light gray)
- **Active Item** - `#0d6efd` (blue highlight)

**Tables:**
- **Header Background** - `#f8f9fa` (light gray)
- **Row Hover** - `#f1f3f5` (lighter gray)
- **Borders** - `#dee2e6` (medium gray)

**Badges:**
- **Status ENABLED** - Green
- **Status PAUSED** - Gray
- **Status REMOVED** - Red
- **Match Type EXACT** - Blue
- **Match Type PHRASE** - Green
- **Match Type BROAD** - Yellow

---

### **Pages Completed (5/8)**

1. âœ… **Main Dashboard** (Chat 21b)
   - 6 metrics cards
   - Performance trend chart
   - Recent recommendations
   - Quick actions

2. âœ… **Campaigns** (Chat 21c)
   - 6 metrics cards
   - 12-column table
   - 8 campaign rules
   - Pagination

3. âœ… **Ad Groups** (Chat 21e)
   - 7 metrics cards
   - 12-column table
   - 0 rules (correct empty state)
   - Pagination

4. âœ… **Keywords** (Chat 21d)
   - 7 metrics cards
   - 11-column table
   - 14 keyword rules
   - QS expansion UI
   - Search terms section

5. âœ… **Bootstrap Foundation** (Chat 21a)
   - base_bootstrap.html
   - Dark sidebar
   - Top navbar
   - Custom CSS

---

### **Pages Remaining (3/8)**

6. ðŸ“‹ **Ads** (Chat 21f) - Next
   - Redesign existing ads.py
   - Ad strength bars
   - Asset performance
   - Preview modal

7. ðŸ“‹ **Shopping** (Chat 21g)
   - Redesign 4-tab UI
   - Product images
   - Feed quality
   - ROAS color coding

8. ðŸ“‹ **Polish** (Chat 21h)
   - Standardize charts
   - Loading spinners
   - Bug fixes
   - Cross-browser testing

---

## ðŸ› COMMON PROBLEMS & SOLUTIONS

### **Problem 1: Browser UI Lag**

**Symptoms:**
- Slow typing in text fields
- Delayed copy/paste
- Upload button unresponsive
- Page scrolling stutters

**Root Cause:**
- Large chat history = massive DOM tree
- Browser struggles to render thousands of elements
- Opera browser particularly affected

**Solution:**
```
Start fresh chat in the project!

This is NOT an AI context problem - it's a browser rendering problem.

1. Keep old chat open for reference (in separate tab)
2. Start new Master Chat in ACT project
3. Initialize with context (from knowledge base)
4. Instant UI responsiveness restored âœ…
```

**Prevention:**
- Roll to new Master every 5-8 worker chats
- Monitor for typing lag as early warning
- Try Chrome/Edge if Opera continues to struggle

---

### **Problem 2: Database Table Not Found**

**Error:**
```
Catalog Error: Table with name campaign_daily does not exist!
Did you mean "ro.analytics.campaign_daily"?
```

**Root Cause:**
- Query using wrong table name
- Missing `ro.` prefix for readonly database
- Schema mismatch between databases

**Solution:**
```python
# WRONG:
FROM analytics.campaign_daily

# CORRECT:
FROM ro.analytics.campaign_daily
```

**Pattern:**
- `analytics.*` â†’ Standard warehouse.duckdb
- `ro.analytics.*` â†’ Readonly warehouse_readonly.duckdb

---

### **Problem 3: Template Rendering Broken**

**Symptoms:**
- Table columns stacking vertically
- All content displaying as plain text
- No Bootstrap styling applied

**Root Cause:**
- Template extending wrong base
- Using `base.html` instead of `base_bootstrap.html`
- Bootstrap 5 CSS not loading

**Solution:**
```html
<!-- WRONG: -->
{% extends "base.html" %}

<!-- CORRECT: -->
{% extends "base_bootstrap.html" %}
```

**Diagnosis Time:** ~45 minutes (Chat 21e)

---

### **Problem 4: Config Validation Errors**

**Error:**
```
âŒ Missing required field: 'client_id'
âŒ Invalid automation_mode: 'insights'
```

**Root Cause:**
- YAML config missing required fields
- Typo in enum value
- Wrong field names

**Solution:**
```yaml
# Fix missing fields:
client_id: "client_001"  # Add this

# Fix enum typos:
automation_mode: "suggest"  # NOT "insights"
risk_tolerance: "moderate"  # NOT "balanced"
```

**Validation Tool:** `config_validator.py` (Phase 2d)

---

### **Problem 5: Duplicate Recommendation Systems**

**Symptoms:**
- Shopping recommendations don't execute
- Schema mismatch errors
- Dict vs object attribute errors

**Root Cause:**
- Two different recommendation schemas
- Shopping used custom format
- Keywords/Ads used standard format

**Solution:**
- Chat 17 standardized everything
- Created `shopping_rules.py` with unified schema
- All recommendation types now use same `Recommendation` dataclass

**Status:** Fixed in Chat 17 âœ…

---

### **Problem 6: File vs Live Recommendations**

**Symptoms:**
- "Recommendations file not found" error
- Execution fails for Keywords/Ads/Shopping tabs

**Root Cause:**
- Main Recommendations page loads from JSON file
- Keywords/Ads/Shopping generate recommendations live
- API routes expect JSON files to exist

**Solution:**
- Deferred to Chat 15
- Options:
  1. Modify API to accept recommendations as payload
  2. Store live recommendations to temp JSON
  3. Create separate execution endpoints

**Status:** Known issue, deferred â³

---

### **Problem 7: Rules Not Displaying**

**Symptoms:**
- "0 rules" showing when rules should exist
- Empty rules card
- Rules sidebar blank

**Root Cause:**
- Rules file doesn't exist (e.g., ad_group_rules.py)
- Wrong page_type in get_rules_for_page() call
- Regex pattern not matching rule IDs

**Solution:**
```python
# Check if rules file exists:
from act_autopilot import campaign_rules  # âœ… Exists
from act_autopilot import ad_group_rules  # âŒ Doesn't exist

# If doesn't exist: Show empty state (correct behavior)
# If exists but not displaying: Check regex pattern

# Common patterns:
'campaign' â†’ r'^CAMP-'
'keyword' â†’ r'^KW-'
'ad' â†’ r'^AD-'
'shopping' â†’ r'^SHOP-'
```

---

### **Problem 8: Cooldown Blocking Valid Changes**

**Symptoms:**
- Change blocked with "Cooldown period active"
- But it's been more than 7 days
- No recent changes in change_log

**Root Cause:**
- Cooldown logic checking wrong date field
- Timezone mismatch
- change_log not queried correctly

**Solution:**
```python
# Check last change:
SELECT * FROM analytics.change_log
WHERE entity_id = '{entity_id}'
  AND action_type = '{action_type}'
  AND status = 'SUCCESS'
ORDER BY timestamp DESC
LIMIT 1;

# Calculate days since:
days_since = (datetime.now() - last_change.timestamp).days

# Cooldown should be:
if days_since < 7:
    return "Cooldown active"
```

**Debug:** Add logging to executor.py to see cooldown calculations

---

## ðŸ“š IMPORTANT DOCUMENTS

### **Must-Read for Master Chat**

1. **CHAT_WORKING_RULES.md** â­â­â­
   - Mandatory rules for ALL chats
   - Rule 1: Upload codebase first
   - Rule 2: Request current file versions
   - Rule 3: Use full file paths
   - **Violation = wasted time + bugs**

2. **PROJECT_ROADMAP.md** â­â­
   - Overall project status (77% complete)
   - Phase tracking (0-2 complete, 3+ planned)
   - Chat 21 progress (62.5% complete)
   - Future roadmap

3. **DASHBOARD_PROJECT_PLAN.md** â­â­
   - Chat 21 detailed breakdown
   - 8-chat specifications
   - UI component details
   - Testing checklists

4. **GAds_Project_Constitution_v0.2.md** â­
   - Governance framework
   - Safety constraints
   - Data sufficiency gates
   - Change magnitude limits
   - Rollback policies
   - Risk tiers

5. **Handoff Documents**
   - `CHAT_12_HANDOFF.md` - Shopping module
   - `CHAT_13.1_HANDOFF.md` - Execution engine
   - `CHAT_14_HANDOFF.md` - Execution UI
   - `CHAT_21C_HANDOFF.md` - Campaigns page
   - `CHAT_21E_HANDOFF.md` - Ad Groups page

---

### **Quick Reference**

**Where Things Are:**
- **Code:** `act_dashboard/`, `src/`
- **Templates:** `act_dashboard/templates/`
- **Configs:** `configs/`
- **Database:** `warehouse.duckdb` (root)
- **Logs:** `logs/dashboard.log`
- **Docs:** `docs/`

**Common Commands:**
```bash
# Start dashboard
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python -m act_dashboard.app configs/client_synthetic.yaml

# Run data pipeline (if needed)
python -m src.gads_pipeline.v1_runner

# Git workflow
git add <files>
git commit -m "message"
git push origin main
```

**Database Queries:**
```python
import duckdb

conn = duckdb.connect('warehouse.duckdb')

# Check table structure:
conn.execute("DESCRIBE analytics.campaign_daily")

# Quick query:
result = conn.execute("""
    SELECT campaign_id, campaign_name, SUM(cost_micros)/1000000 as spend
    FROM analytics.campaign_daily
    WHERE customer_id = '9999999999'
      AND snapshot_date >= CURRENT_DATE - 7
    GROUP BY campaign_id, campaign_name
    ORDER BY spend DESC
""").fetchall()

conn.close()
```

---

## ðŸ“Š CURRENT STATUS

### **Overall Project: ~84% Complete**

**Completed Phases:**
- âœ… Phase 0: Foundation (Chats 1-17)
- âœ… Phase 1: Code Cleanup (9 tasks)
- âœ… Phase 2: Polish & Refactoring (4 tasks)

**In Progress:**
- â³ Chat 21: Dashboard UI Overhaul (62.5% complete)
  - âœ… Chat 21a: Bootstrap Setup
  - âœ… Chat 21b: Main Dashboard
  - âœ… Chat 21c: Campaigns View
  - âœ… Chat 21d: Keywords View
  - âœ… Chat 21e: Ad Groups View
  - ðŸ“‹ Chat 21f: Ads View (next)
  - ðŸ“‹ Chat 21g: Shopping View
  - ðŸ“‹ Chat 21h: Polish

**Planned:**
- ðŸ“‹ Phase 3: Future-Proofing (tests, optimization)
- ðŸ“‹ Chat 22: Email Reports
- ðŸ“‹ Chat 23: Smart Alerts
- ðŸ“‹ Chats 24-28: Additional features

---

### **Code Metrics**

**Lines of Code:**
- **Dashboard:** ~3,000 lines (routes + templates)
- **Optimization Engine:** ~5,000 lines (rules + diagnostics)
- **Shopping Module:** ~3,800 lines (Chat 12)
- **Execution Engine:** ~1,500 lines (Chat 13.1)
- **Tests:** ~1,000 lines (100% pass rate)
- **Total:** ~14,300 lines of production code

**Files:**
- **Python modules:** 45+
- **Templates:** 20+
- **Config files:** 4 clients
- **Documentation:** 15+ handoff docs

---

### **Test Results**

**Module Tests:**
- Shopping: 29/29 tests passing (100%) âœ…
- Keywords: 100% pass rate âœ…
- Ads: 100% pass rate âœ…
- Execution: Integration tests passing âœ…

**Manual Testing:**
- All 5 completed dashboard pages working âœ…
- Authentication working âœ…
- Client switching working âœ…
- Database queries working âœ…
- Rules display working (campaigns, keywords) âœ…

---

### **Known Issues**

1. **File vs Live Recommendations** â³
   - Deferred to Chat 15
   - API expects JSON files
   - Keywords/Ads generate live

2. **Executor Dict/Object Compatibility** â³
   - Deferred to Chat 15
   - Executor expects objects
   - Dashboard passes dicts

3. **Rate Limiting Not Implemented** ðŸ“‹
   - Phase 1f defined it
   - Flask-Limiter not yet integrated
   - TODO: Add to app.py

4. **QS Chevron Click Functionality** ðŸ“‹
   - Chevrons display (Chat 21d)
   - Click to expand sub-metrics pending
   - Low priority

5. **Ad Group Rules File Missing** âœ… Expected
   - ad_group_rules.py doesn't exist
   - Empty state displays correctly
   - Future enhancement

---

## ðŸ—ºï¸ FUTURE ROADMAP

### **Immediate (Next 2-3 Days)**

**Chat 21f: Ads View** (~70 min)
- Redesign ads.py with Bootstrap 5
- Ad strength progress bars
- Asset performance expandable rows
- Ad preview modal
- Rules integration (11 ad rules)

**Chat 21g: Shopping View** (~90 min)
- Redesign 4-tab Shopping UI
- Product images in table
- Feed quality issue badges
- ROAS color coding
- Rules integration (14 Shopping rules)

**Chat 21h: Charts & Polish** (~60 min)
- Standardize Chart.js colors (Bootstrap palette)
- Add loading spinners for tables
- Fix responsive issues
- Cross-browser testing (Chrome, Firefox, Edge)
- Bug fixes

**Result:** Dashboard UI 100% complete âœ…

---

### **Short-Term (After Dashboard)**

**Chat 15: Backend Integration** (2-3 hrs)
- Fix file vs live recommendations mismatch
- Fix executor dict/object compatibility
- Test end-to-end execution flow
- Validate rollback functionality

**Phase 3: Future-Proofing** (10-14 hrs)
- 3a: Unit Tests (4-6 hrs) - pytest, 60%+ coverage
- 3b: Background Job Queue (3-4 hrs) - Celery/RQ
- 3c: Database Optimization (2-3 hrs) - Add indexes
- 3d: CSRF Protection (1 hr) - Flask-WTF

**Chat 22: Email Reports** (2-3 hrs)
- Daily/weekly summary emails
- Performance highlights
- Pending recommendations
- Change notifications
- SMTP integration

**Chat 23: Smart Alerts** (2-3 hrs)
- Anomaly detection (sudden CPA spike, conversion drop)
- Threshold-based alerts (budget caps, KPI targets)
- Email + SMS notifications
- Alert configuration UI

---

### **Medium-Term (Next 1-2 Weeks)**

**Chat 24: Advanced Analytics** (3-4 hrs)
- Cohort analysis
- Attribution modeling
- Incrementality testing
- Forecasting models

**Chat 25: Data Quality Monitoring** (2-3 hrs)
- Tracking health checks
- Data freshness monitoring
- Anomaly detection in API data
- Data quality dashboards

**Chat 26: Onboarding Wizard** (3-4 hrs)
- New client setup flow
- Google Ads connection wizard
- Step-by-step configuration
- Validation and testing

**Chat 27: Documentation & Training** (3-4 hrs)
- User guide (how to use dashboard)
- Setup guide (installation & config)
- FAQ section
- Video tutorials (optional)

**Chat 28: Marketing Website** (varies)
- A.C.T product page
- Case studies
- Pricing information
- Demo request form

---

### **Long-Term (Backlog)**

**Performance Max Support**
- Full PMax campaign optimization
- Asset group recommendations
- Audience signal suggestions
- Currently insights-only

**Video Campaigns**
- YouTube campaign support
- Video ad performance
- View-through conversions
- Creative testing

**Display Campaigns**
- Display network optimization
- Responsive display ads
- Placement recommendations
- Audience targeting

**Multi-Account Dashboard**
- MCC-level aggregation
- Cross-account insights
- Consolidated reporting
- Budget allocation across accounts

**Machine Learning Enhancements**
- Custom ML models for predictions
- Automated A/B testing
- Dynamic bid optimization
- Seasonality adjustments

**API for Third-Party Integrations**
- REST API for external tools
- Webhook notifications
- CRM integrations (Salesforce, HubSpot)
- Data exports (BigQuery, Snowflake)

---

## ðŸŽ“ LESSONS LEARNED

### **Architecture Decisions**

**What Worked Well:**
1. âœ… **Blueprint Pattern** - Modular routes make maintenance easy
2. âœ… **DuckDB** - Fast analytics without database server overhead
3. âœ… **Constitution Framework** - Safety guardrails prevent harmful changes
4. âœ… **Bootstrap 5** - Professional UI without build complexity
5. âœ… **Rules Engine Modularity** - Easy to add new rules per campaign type
6. âœ… **Dynamic Category Detection** - Regex patterns make rules display future-proof

**What Could Be Improved:**
1. âš ï¸ **Dual Recommendation Systems** - Took Chat 17 to unify
2. âš ï¸ **File vs Live Generation** - Should have designed this upfront
3. âš ï¸ **Rate Limiting** - Defined in Phase 1f but not implemented
4. âš ï¸ **Type Hints** - Should have been from start, not retrofitted (Phase 2c)

---

### **Development Process**

**Effective Practices:**
1. âœ… **Comprehensive Testing** - 100% test pass rate before moving on
2. âœ… **Handoff Documents** - Essential for context continuity
3. âœ… **Working Rules** - MANDATORY codebase upload saves hours
4. âœ… **Git Commits** - Frequent commits with clear messages
5. âœ… **Multi-Chat Pattern** - Specialized chats with Master coordination

**Pain Points:**
1. âš ï¸ **Browser UI Lag** - Large chat history breaks UI responsiveness
2. âš ï¸ **Context Bleeding** - Old information sometimes persists incorrectly
3. âš ï¸ **File Version Confusion** - Must request current versions explicitly
4. âš ï¸ **Template Inheritance** - Easy to miss (Chat 21e took 45 min to diagnose)

---

### **Key Insights**

1. **Always verify template inheritance first** when CSS/styling issues occur
   - Check line 1 of template
   - Confirm correct base template (base_bootstrap.html vs base.html)

2. **Database table names matter**
   - `analytics.*` vs `ro.analytics.*`
   - Document which database queries use which prefix

3. **Rules display system is reusable**
   - Dynamic category detection works for any entity type
   - Regex patterns make it future-proof
   - Empty states are correct when rules files don't exist

4. **Browser performance matters**
   - Large DOM trees cause UI lag
   - Roll to new Master chat when typing slows down
   - Not an AI problem - it's a browser rendering problem

5. **Constitution framework is essential**
   - Prevents harmful changes
   - Builds trust with clients
   - Enables automated execution with safety

---

## ðŸŽ¯ SUCCESS CRITERIA (FOR MASTER CHAT 2.0)

**You'll know Master Chat 2.0 is working well when:**

1. âœ… **Worker chats are productive**
   - Clear briefs
   - Minimal back-and-forth
   - Complete deliverables
   - Proper testing

2. âœ… **Problems are diagnosed quickly**
   - Root cause identified in <30 minutes
   - Clear solution provided
   - No circular debugging

3. âœ… **Documentation stays updated**
   - Handoffs created after each chat
   - Roadmap updated with progress
   - Lessons learned captured

4. âœ… **Coordination is smooth**
   - Master knows what's been done
   - Master knows what's next
   - Master can answer "where are we?" questions
   - No duplicate work

5. âœ… **Project momentum maintained**
   - Steady progress (not blocked)
   - Clear next steps always defined
   - Technical debt addressed promptly
   - Quality remains high

---

## ðŸ“ NOTES FOR MASTER CHAT 2.0

**When coordinating workers:**
- Always reference this knowledge base first
- Check PROJECT_ROADMAP.md for current status
- Review recent handoff docs for context
- Verify file versions before editing
- Test thoroughly before marking complete

**When diagnosing problems:**
- Check "Common Problems & Solutions" section first
- Look for similar issues in past handoffs
- Verify database table names (analytics vs ro.analytics)
- Check template inheritance (line 1)
- Review Constitution gates if execution blocked

**When planning next steps:**
- Consult DASHBOARD_PROJECT_PLAN.md for Chat 21 sequence
- Reference PROJECT_ROADMAP.md for overall priorities
- Estimate time realistically (actual times often 2X estimates)
- Define clear success criteria before starting
- Plan for testing and documentation time

**When things go wrong:**
- Don't waste time on circular debugging
- Escalate to user if stuck >1 hour
- Document the issue for future reference
- Update troubleshooting guide with new solutions

---

**END OF MASTER KNOWLEDGE BASE**

**This document version:** 2.0  
**Created for:** Master Chat 2.0  
**Last updated:** 2026-02-19  
**Total length:** ~8,000 lines

**Next step:** Use this knowledge base to coordinate worker chats and maintain project momentum! ðŸš€
