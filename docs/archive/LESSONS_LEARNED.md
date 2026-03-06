# LESSONS LEARNED - ADS CONTROL TOWER (A.C.T)

**Version:** 1.0  
**Created:** 2026-02-28  
**Total Lessons:** 50  
**Purpose:** Best practices from 300+ hours across 49 chats

**See Also:** MASTER_KNOWLEDGE_BASE.md, KNOWN_PITFALLS.md, COMPLETE_CHAT_HISTORY.md

---

## DATABASE & BACKEND

### 1. Always Extend base_bootstrap.html (Never base.html)
Bootstrap 5 migration created base_bootstrap.html. Old base.html lacks Bootstrap CSS. Extending wrong base = no styling.
- **Apply:** Always use `{% extends "base_bootstrap.html" %}`
- **Chat:** 21 (Bootstrap 5 migration)

### 2. Always Use ro.analytics.* Prefix for Read Queries
Dual database: warehouse.duckdb (write) + warehouse_readonly.duckdb (analytics). Without `ro.` prefix, queries fail.
- **Apply:** SELECT from `ro.analytics.table_name`, INSERT into `table_name`
- **Chat:** 29 (Radar monitoring)

### 3. Request Current File Before Editing — Never Cached
Files change between chats. Cached versions cause conflicts, lost work.
- **Apply:** Always request current version, never assume unchanged
- **Chat:** Multiple (recurring issue)

### 4. Route Decorator Quote Style Matters
str_replace must match exact quote style in decorators (`'` vs `"`).
- **Apply:** View file first, copy exact quote style
- **Chat:** Multiple

### 5. Shopping compute_campaign_metrics() Must Include total_clicks
CTR calculation requires clicks. Missing = division by zero.
- **Apply:** Always include SUM(clicks) in aggregation queries
- **Chat:** 23 (M2 Metrics Cards)

### 6. Session State > URL Params for Picker/Collapse
Session storage cleaner than URL params. Persists across pages, cleaner URLs.
- **Apply:** Use `flask.session['key']` for user preferences
- **Chat:** 22 (M1 Date Picker)

### 7. Jinja2 Macros: Pilot-Then-Rollout Pattern
Build macro once, reuse across pages. Saves 5-10 hours per feature.
- **Apply:** Pilot on 1 page, refine, rollout to all pages
- **Chat:** 23 (M2 Metrics Cards)

### 8. Mandatory Codebase Upload Saves Hours
Workers need context. Codebase ZIP provides complete picture, saves 50-75% spec time.
- **Apply:** Every worker chat starts with codebase ZIP upload
- **Chat:** 47 (Multi-Entity Recommendations)

### 9. Files in routes/ Are 3 Levels Deep
routes/ → act_dashboard/ → project root = 3 levels. Use `.parent.parent.parent`
- **Apply:** Count levels, use correct .parent depth
- **Chat:** Multiple

### 10. display:none + display:flex — Browser Uses Last
Both in inline style = flex wins. Drawer visible on load.
- **Apply:** HTML: `display:none`, JavaScript adds `display:flex`
- **Chat:** 26 (M5 Rules Tab)

### 11. Dual-Layer: JSON Config (UI) + Python (Execution)
rules_config.json = what to do. Python = how to do it. Keep separate.
- **Apply:** Never hard-code thresholds in Python, never put logic in JSON
- **Chat:** 12, 45 (Shopping)

---

## RECOMMENDATIONS SYSTEM

### 12. Campaign Picker Must Be Wired to Real Data
Empty picker = feature looks 90% complete but 0% functional.
- **Apply:** Wire `/api/campaigns-list` endpoint, test with real selection
- **Chat:** 26, 41

### 13. JSON Endpoints Enable SPA Behavior
`/recommendations/cards` endpoint = instant tab switching without reload.
- **Apply:** Use JSON for dynamic content, server-side for initial load
- **Chat:** 28 (M7 Accept/Decline)

### 14. Recommendations in Writable warehouse.duckdb
Analytics DB is read-only. Recommendations need INSERT/UPDATE.
- **Apply:** Write tables in warehouse.duckdb, read tables in ro.analytics.*
- **Chat:** 27 (M6 Recommendations Engine)

### 15. Log Proxy Columns When Used
Using cost_micros as budget proxy? Log it. Transparency builds trust.
- **Apply:** Log warnings, store in recommendations.notes field
- **Chat:** 27

### 16. Duplicate Prevention: Check (campaign_id, rule_id)
Without check, engine creates duplicates every run.
- **Apply:** SELECT COUNT before INSERT, skip if exists
- **Chat:** 27

### 17. Verify DB Column Names Before Writing Routes
Brief says "bid", schema says "cpc_bid_micros". Verify actual names.
- **Apply:** View schema first, use actual column names
- **Chat:** 25 (M4 Table Overhaul)

### 18. Tab Switching: Server-Side vs Client-Side
Global page: server-side Jinja. Entity pages: client-side fetch.
- **Apply:** Choose based on complexity and performance needs
- **Chat:** 28, 49

### 19. NULL Dates on Old Rows Are Expected
Old synthetic rows created before column added have NULLs. Document it.
- **Apply:** Accept NULLs on old rows, document in handoff
- **Chat:** 27

### 20. DuckDB Pattern: Open Writable + ATTACH Readonly
Radar needs reads (analytics) and writes (recommendations).
- **Apply:** `connect(warehouse.duckdb)` + `ATTACH warehouse_readonly AS ro`
- **Chat:** 29 (M8 Radar)

### 21. Changes Table: JOIN via campaign_id + rule_id
No recommendation_id FK. Use compound key + QUALIFY ROW_NUMBER().
- **Apply:** Latest rec per (campaign_id, rule_id) pair
- **Chat:** 29

### 22. System Changes Empty Until Autopilot Runs
Data from ro.analytics.change_log populated by Autopilot, not dashboard.
- **Apply:** Document expected empty state in testing
- **Chat:** 29

---

## MARKETING WEBSITE

### 23. Single-File Artifacts for Next.js
Combine HTML/CSS/JS in one .tsx file. Easier to edit, no import issues.
- **Apply:** Use Tailwind/CSS-in-JS, avoid separate .css files
- **Chat:** Master 4.0

### 24. Test npm run build Before Deploy
Development (npm run dev) forgives errors. Build catches them.
- **Apply:** Always run build locally before pushing
- **Chat:** Master 4.0

### 25. Three.js r128 Doesn't Support colorSpace
CDN version is r128. texture.colorSpace causes runtime error.
- **Apply:** Check CDN version, match docs to version
- **Chat:** Master 4.0

### 26. CNAME Propagates Faster Than A Record
CNAME (www): 5-15 min. A (root): 15-60 min. Normal behavior.
- **Apply:** Test www first, wait 30-60 min for root
- **Chat:** Master 4.0

### 27. GoDaddy: Remove Old A Records First
Old parking page records conflict with Vercel records.
- **Apply:** Delete all old records before adding new
- **Chat:** Master 4.0

### 28. Contact Form → A.C.T /api/leads
Unified lead tracking. Website POST to dashboard API.
- **Apply:** Central lead database, track source field
- **Chat:** Master 4.0 (pending integration)

---

## SEARCH TERMS & KEYWORDS

### 29. Client-Side Search: Instant > Comprehensive
Filters visible rows only but instant feedback. Good for Phase 1.
- **Apply:** Client-side for <1000 rows, server-side for >1000
- **Chat:** 30a (M9 Phase 1)

### 30. Industry-Standard Thresholds Work Well
10 clicks, £50 cost, 1% CTR work for 90% of cases.
- **Apply:** Start with standards, make configurable if clients request
- **Chat:** 30a

### 31. Bulk Selection: JavaScript Array Tracking
Persist selections across pages with in-memory array.
- **Apply:** JavaScript array for session, sessionStorage for persistence
- **Chat:** 30a

### 32. Dry-Run First: Check Flag BEFORE Loading Client
Check dry_run before loading Google Ads client. Saves 500-1000ms.
- **Apply:** Validate inputs in dry-run, load client only for live
- **Chat:** 30b (M9 Phase 2)

### 33. Conservative Expansion Criteria
CVR ≥5%, ROAS ≥4.0×, Conv. ≥10 = high quality. Fewer but better suggestions.
- **Apply:** Start conservative, track acceptance rate
- **Chat:** 30b

### 34. Sequential < 10 Items, Batch > 50
Sequential simpler, acceptable for <10 items (2s total).
- **Apply:** Add batching only when proven necessary
- **Chat:** 30b

---

## GOOGLE ADS API

### 35. Config Path: Try Multiple Fallbacks
Root, configs/, secrets/. Different environments use different locations.
- **Apply:** Try 3 paths, clear error listing all attempted
- **Chat:** 30b

---

## RULES & COMPONENTS

### 36. Each Page Needs Specific Component
Generic rules_tab.html causes CSS/JS conflicts. Need entity-specific.
- **Apply:** keywords_rules_tab.html, ad_group_rules_tab.html, etc.
- **Chat:** 46 (Rules Tab UI)

### 37. Document Schema Evolution
Keywords use old schema (condition_metric), new entities use new (condition_1_metric).
- **Apply:** Document divergence, plan future migration
- **Chat:** 46

### 38. Backward Compatibility via Column Retention
Add entity columns, keep campaign columns. Zero breaking changes.
- **Apply:** Add new columns, populate both, migrate code gradually
- **Chat:** 47 (Multi-Entity)

### 39. Database Migrations: Zero Data Loss
70 recs + 49 changes migrated successfully with scripts.
- **Apply:** Backup, migrate, verify zero NULLs, document
- **Chat:** 47

### 40. Backend Filter > Hardcoded Labels
get_action_label() filter = single source of truth, easy updates.
- **Apply:** Dynamic labels from backend functions, not database
- **Chat:** 48 (Global Filtering)

### 41. Testing Efficiency: 600% on Refactoring
Chat 47: 2h actual vs 11-14h estimated. Extending existing patterns = fast.
- **Apply:** Build solid foundation, establish patterns, extend confidently
- **Chat:** 47

---

## BACKEND & CSRF

### 42. Verify Limits Match Data Volume
limit=200 truncated Keywords to 162 of 1,256 recs.
- **Apply:** Development: 100-200, Production: max × 2
- **Chat:** 49

### 43. CSRF Exemptions for JSON APIs
JavaScript fetch() doesn't send CSRF tokens. Exempt JSON routes.
- **Apply:** csrf.exempt() for Accept/Decline routes
- **Chat:** 49

---

## UI & UX

### 44. Empty State: Info vs Warning
Info (blue) = temporary. Warning (yellow) = structural.
- **Apply:** Match styling to cause and resolution path
- **Chat:** 49

### 45. Component Reuse: First Slow, Next Fast
Keywords: 7h. Shopping: 4h (43% faster). Ad Groups: 3h (57% faster). Ads: 2.5h (64% faster).
- **Apply:** First establishes pattern, subsequent apply it
- **Chat:** 49

### 46. Load More for >100 Items
1,256 recs at once = 8-10s. Load More (20 at time) = 200ms.
- **Apply:** >100 items always use Load More (page size 20-50)
- **Chat:** 49

### 47. Test AFTER Design Changes
Testing before redesign = wasted effort. Test final design.
- **Apply:** Test incrementally during dev, comprehensive after design done
- **Chat:** 50 moved to after dashboard redesign

---

## ADDITIONAL LESSONS

### 48. File Size Limit: Split Files >2000 Lines
Claude project files don't index properly if >2000 lines or >45KB.
- **Apply:** Split large files into focused components
- **Discovery:** Master Chat 5.0

### 49. Fresh PowerShell for Each Operation
Reusing PowerShell commands causes state issues.
- **Apply:** New PowerShell window or clear command for each test
- **Pattern:** Throughout project

### 50. Complete Files > Code Snippets
Christopher prefers complete ready-to-use files, not snippets.
- **Apply:** Return entire file with save path, not just changed lines
- **Pattern:** Throughout project

---

**Total:** 50 lessons  
**Coverage:** Database, recommendations, website, search, API, components, UI  
**Purpose:** Prevent recurring mistakes, accelerate development  
**Application:** Read before new chats, reference during work

**Version:** 1.0 | **Updated:** 2026-02-28
