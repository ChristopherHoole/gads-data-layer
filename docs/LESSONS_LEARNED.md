# LESSONS LEARNED - ADS CONTROL TOWER (A.C.T)

**Version:** 2.0
**Created:** 2026-02-28
**Updated:** 2026-03-06
**Total Lessons:** 56
**Purpose:** Best practices from 400+ hours across 64 chats

**See Also:** MASTER_KNOWLEDGE_BASE.md, KNOWN_PITFALLS.md

---

## DATABASE & BACKEND

### 1. Always Extend base_bootstrap.html (Never base.html)
Bootstrap 5 migration created base_bootstrap.html. Old base.html lacks Bootstrap CSS.
- **Apply:** `{% extends "base_bootstrap.html" %}`

### 2. Always Use ro.analytics.* Prefix for Read Queries
Dual database: warehouse.duckdb (write) + warehouse_readonly.duckdb (analytics).
- **Apply:** SELECT from `ro.analytics.table_name`, INSERT into `table_name`

### 3. Request Current File Before Editing — Never Cached
Files change between chats. Cached versions cause conflicts, lost work.
- **Apply:** Always request current version, never assume unchanged

### 4. Route Decorator Quote Style Matters
str_replace must match exact quote style in decorators.
- **Apply:** View file first, copy exact quote style

### 5. Shopping compute_campaign_metrics() Must Include total_clicks
CTR calculation requires clicks. Missing = division by zero.
- **Apply:** Always include SUM(clicks) in aggregation queries

### 6. Session State > URL Params for Picker/Collapse
Session storage cleaner than URL params. Persists across pages, cleaner URLs.
- **Apply:** Use `flask.session['key']` for user preferences

### 7. Jinja2 Macros: Pilot-Then-Rollout Pattern
Build macro once, reuse across pages. Saves 5-10 hours per feature.
- **Apply:** Pilot on 1 page, refine, rollout to all pages

### 8. Files in routes/ Are 3 Levels Deep
routes/ → act_dashboard/ → project root = 3 levels.
- **Apply:** Use `.parent.parent.parent` for config paths from route files

### 9. display:none + display:flex — Browser Uses Last
Both in inline style = flex wins. Drawer visible on load.
- **Apply:** HTML: `display:none`, JavaScript adds `display:flex`

### 10. Dual-Layer: JSON Config (UI) + Python (Execution)
rules_config.json = what to do. Python = how to do it. Keep separate.
- **Apply:** Never hard-code thresholds in Python, never put logic in JSON

### 11. Session Consistency: Always session.get(), Never Helper Objects
Helper functions like `get_current_config()` return objects. Template comparisons expect strings.
String vs object comparison always False → undefined browser state → spurious side effects.
- **Apply:** Always use `session.get("current_client_config")` directly. Never compare session strings to objects.
- **Chat:** 64 (client selector bug)

### 12. Integer Columns vs Timestamp Columns for Tracking
Seed scripts often only write integer tracking columns (open_count, click_count) but not timestamp columns (opened_at, clicked_at). Querying `IS NOT NULL` on unpopulated timestamps returns zero.
- **Apply:** Use `WHERE open_count > 0` not `WHERE opened_at IS NOT NULL`
- **Apply:** When building analytics, verify which column type the seed actually populates
- **Chat:** 64 (opened/clicked showing 0)

### 13. taskkill /IM python.exe /F for Stuck Flask Processes
Port 5000 already in use = previous Flask session still running.
- **Apply:** Run `taskkill /IM python.exe /F` before starting Flask in fresh PowerShell
- **Chat:** Throughout outreach build (Chats 59-64)

---

## RECOMMENDATIONS SYSTEM

### 14. JSON Endpoints Enable SPA Behavior
`/recommendations/cards` endpoint = instant tab switching without reload.
- **Apply:** Use JSON for dynamic content, server-side for initial load

### 15. Recommendations in Writable warehouse.duckdb
Analytics DB is read-only. Recommendations need INSERT/UPDATE.
- **Apply:** Write tables in warehouse.duckdb, read tables in ro.analytics.*

### 16. Duplicate Prevention: Check (campaign_id, rule_id)
Without check, engine creates duplicates every run.
- **Apply:** SELECT COUNT before INSERT, skip if exists

### 17. Verify DB Column Names Before Writing Routes
Brief says "bid", schema says "cpc_bid_micros". Verify actual names.
- **Apply:** View schema first, use actual column names

### 18. DuckDB Pattern: Open Writable + ATTACH Readonly
Radar needs reads (analytics) and writes (recommendations).
- **Apply:** `connect(warehouse.duckdb)` + `ATTACH warehouse_readonly AS ro`

### 19. Backend Limit Must Match Data Volume
limit=200 truncated Keywords to 162 of 1,256 recommendations.
- **Apply:** Development: 200, Production: 5000+ for high-volume entities

### 20. CSRF Exemptions for JSON APIs
JavaScript fetch() doesn't send CSRF tokens automatically. Exempt JSON routes.
- **Apply:** `csrf.exempt()` for Accept/Decline routes in app.py

---

## MARKETING WEBSITE

### 21. Test npm run build Before Deploy
Development (npm run dev) forgives errors. Build catches them.
- **Apply:** Always run build locally before pushing

### 22. Three.js r128 Doesn't Support colorSpace
CDN version is r128. texture.colorSpace causes runtime error.
- **Apply:** Remove `texture.colorSpace` line; check CDN version

### 23. CNAME Propagates Faster Than A Record
CNAME (www): 5-15 min. A (root): 15-60 min. Normal behavior.
- **Apply:** Test www first, wait 30-60 min for root

### 24. GoDaddy: Remove Old A Records First
Old parking page records conflict with Vercel records.
- **Apply:** Delete all old records before adding new

---

## SEARCH TERMS & KEYWORDS

### 25. Dry-Run First: Check Flag BEFORE Loading Client
Check dry_run before loading Google Ads client. Saves 500-1000ms, enables credential-free testing.
- **Apply:** Validate inputs in dry-run, load client only for live

### 26. Conservative Expansion Criteria
CVR ≥5%, ROAS ≥4.0×, Conv. ≥10 = high quality. Fewer but better suggestions.
- **Apply:** Start conservative, track acceptance rate

### 27. Sequential < 10 Items, Batch > 50
Sequential simpler, acceptable for <10 items (2s total).
- **Apply:** Add batching only when proven necessary

---

## RULES & COMPONENTS

### 28. Each Page Needs Specific Component Include
Generic rules_tab.html causes CSS/JS conflicts. Need entity-specific.
- **Apply:** keywords_rules_tab.html, ad_group_rules_tab.html, etc.

### 29. Document Schema Evolution
Keywords use old schema (condition_metric), new entities use new (condition_1_metric).
- **Apply:** Document divergence, plan future migration

### 30. Backward Compatibility via Column Retention
Add entity columns, keep campaign columns. Zero breaking changes.
- **Apply:** Add new columns, populate both, migrate code gradually

### 31. Database Migrations: Zero Data Loss
70 recs + 49 changes migrated successfully with scripts.
- **Apply:** Backup, migrate, verify zero NULLs, document

### 32. Backend Filter > Hardcoded Labels
get_action_label() filter = single source of truth, easy updates.
- **Apply:** Dynamic labels from backend functions, not database

---

## UI & UX

### 33. Empty State: Info vs Warning
Info (blue) = temporary. Warning (yellow) = structural.
- **Apply:** Match styling to cause and resolution path

### 34. Component Reuse: First Slow, Next Fast
Keywords: 7h. Shopping: 4h (43% faster). Ad Groups: 3h (57% faster). Ads: 2.5h (64% faster).
- **Apply:** First establishes pattern, subsequent apply it

### 35. Load More for >100 Items
1,256 recs at once = 8-10s. Load More (20 at time) = 200ms.
- **Apply:** >100 items always use Load More (page size 20-50)

### 36. Test AFTER Design Changes
Testing before redesign = wasted effort. Test final design.
- **Apply:** Test incrementally during dev, comprehensive after design done

### 37. Color-Coded Progress Bars for Performance Tables
N · X% format with inline colored progress bars instantly communicates performance tier.
More scannable than plain percentages, especially for funnel/performance tables.
- **Apply:** Use `an-` CSS prefix for analytics-specific classes to avoid conflicts
- **Chat:** 64 (Outreach Analytics)

---

## OUTREACH SYSTEM

### 38. Jinja/JavaScript Brace Conflict: Split the Braces
Jinja2 processes `{{ }}` before the browser sees JavaScript. Template literals with `{{variable}}` will cause Jinja errors.
- **Apply:**
```javascript
// WRONG:
let template = "Hello {{first_name}}";

// CORRECT:
let template = "Hello " + '{' + '{' + "first_name}}";
```
- **Alternative:** Use data attributes to pass Jinja vars to JS, avoiding inline `{{ }}`
- **Chat:** 63 (Templates page)

### 39. Outreach: Pass Jinja Data to JavaScript via data Attributes
Instead of embedding Jinja variables in JavaScript strings, pass them through HTML data attributes. Cleaner, avoids brace conflicts.
- **Apply:**
```html
<!-- HTML: -->
<div id="lead-card" data-name="{{ lead.first_name }}" data-company="{{ lead.company }}">

<!-- JavaScript: -->
let name = document.getElementById('lead-card').dataset.name;
```
- **Chat:** 63 (Templates page)

### 40. Slide Panel Pattern for Detail Views
For reply/lead detail views, a slide-in panel (right side, fixed position) is better UX than a modal. Keeps context visible while viewing detail.
- **Apply:** Use Bootstrap offcanvas or custom fixed-position panel with CSS transition
- **Pattern:** Click row → panel slides in from right → real-time state updates (unread decrement) without full page reload
- **Chat:** 62 (Replies page)

### 41. Unread Counts: Decrement in JavaScript, Don't Reload
When marking items as read, update the count badge in JavaScript immediately. Don't wait for page reload.
Better UX, faster, no flicker.
- **Apply:**
```javascript
let count = parseInt(badge.textContent);
if (count > 0) badge.textContent = count - 1;
if (count <= 1) badge.style.display = 'none';
```
- **Chat:** 62 (Replies page)

### 42. Outreach Analytics: Integer Tracking Columns Are Truth
The `sent_emails` table has both integer columns (open_count, click_count, cv_open_count) and timestamp columns (opened_at, clicked_at, cv_opened_at). The seed script only populates integers. The tracking pixel system (planned) will write timestamps.
- **Apply:** Always query integer columns for current analytics. When live tracking is added, both will be populated.
- **Chat:** 64 (Analytics page)

### 43. Colored Analytics Progress Bars: CSS Prefix Isolation
Adding analytics-specific CSS to a shared CSS file (outreach.css) risks conflicts with existing classes.
- **Apply:** Use component-specific CSS prefix: `an-` for analytics, `re-` for replies, etc.
- **Chat:** 64 (Analytics page)

### 44. Performance Tables: N · X% Format
Display raw numbers alongside percentages: "95 · 95%" is more informative than "95%" alone.
Reader sees both volume and rate without needing to hover or calculate.
- **Apply:** Format: `{{ count }} · {{ pct }}%` in performance breakdown tables
- **Chat:** 64 (Analytics page)

---

## PROCESS & WORKFLOW

### 45. Fresh PowerShell for Each Operation
Reusing PowerShell commands causes state issues.
- **Apply:** New PowerShell window or clear command for each test

### 46. Complete Files > Code Snippets
Christopher prefers complete ready-to-use files, not snippets.
- **Apply:** Return entire file with save path, not just changed lines

### 47. File Size Limit: Split Files >2000 Lines
Claude project files don't index properly if >2000 lines or >45KB.
- **Apply:** Split large files into focused components

### 48. 2-Tier Workflow (Claude Code) Is 40-50% Faster
Old: Master Chat → Worker Chat → execution (3-tier).
New: Master Chat → Claude Code (2-tier). Worker Chats eliminated.
- **Apply:** Use Claude Code (`npx @anthropic-ai/claude-code`) for all implementation work
- **Reference:** CLAUDE_CODE_WORKFLOW.md

### 49. Seed Scripts Must Cover All Referenced Columns
If analytics routes query `open_count`, the seed script must populate `open_count`. If it only populates `opened_at`, analytics shows zeros.
- **Apply:** When building analytics, trace every queried column back to its seed source. If missing, write a patch seed script.
- **Chat:** 64 (tools/seed_outreach_clicks.py)

### 50. Worktrees: Add to .gitignore Early
Git worktrees can cause unexpected git behavior if not excluded.
- **Apply:** Add `.git/worktrees/` to .gitignore at project setup

---

## ARCHITECTURE PRINCIPLES

### 51. Dry-Run Mode Is Non-Negotiable for Live API Operations
Any feature that writes to Google Ads must have a dry-run mode. Validates logic without API credentials. Enables demo mode for clients.
- **Apply:** Check `dry_run` flag as first operation after parsing request, before any external calls

### 52. Changes Audit Trail for Every State-Modifying Action
Every Accept/Decline/Execute operation writes to the `changes` table. Never modify state without logging.
- **Apply:** Write to changes table before returning success response

### 53. Constitution Framework: Safety Guardrails Are Non-Negotiable
All automated changes must pass Constitution checks: daily limits, 7-day cooldown periods, magnitude restrictions, data sufficiency.
- **Apply:** Never bypass Constitution checks even for testing

### 54. Single Source of Truth for Business Rules
rules_config.json is the single source for all rule definitions. Python execution files are untouched by UI operations.
- **Apply:** Rule changes go through JSON only; Python execution layer reads JSON

### 55. Entity_type String Values Must Be Exact
Database stores exact strings. Any mismatch returns zero results with no error.
- **Apply:** Exact values: `'campaign'`, `'keyword'`, `'shopping_product'`, `'ad_group'`, `'ad'`

### 56. Component CSS Prefix Isolation
When adding styles for a new section/feature to a shared CSS file, use a unique prefix to prevent conflicts with existing classes.
- **Apply:** `an-` for analytics, `re-` for replies, `qu-` for queue, etc.
- **Chat:** 64 (outreach.css)

---

**Total:** 56 lessons
**Coverage:** Database, recommendations, website, search, API, components, UI, outreach, process
**Version:** 2.0 | **Updated:** 2026-03-06
