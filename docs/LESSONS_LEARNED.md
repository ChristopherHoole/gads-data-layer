# LESSONS LEARNED - ADS CONTROL TOWER (A.C.T)

**Version:** 7.0
**Created:** 2026-02-28
**Updated:** 2026-03-19
**Total Lessons:** 92
**Purpose:** Best practices from 500+ hours across 101 chats

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
- **Apply:** Always use `session.get("current_client_config")` directly.
- **Chat:** 64

### 12. Integer Columns vs Timestamp Columns for Tracking
Seed scripts often only write integer tracking columns, not timestamp columns.
- **Apply:** Use `WHERE open_count > 0` not `WHERE opened_at IS NOT NULL`
- **Chat:** 64

### 13. taskkill /IM python.exe /F for Stuck Flask Processes
Port 5000 already in use = previous Flask session still running.
- **Apply:** Run `taskkill /IM python.exe /F` before starting Flask in fresh PowerShell

### 14. DuckDB: json_extract_string vs JSON_EXTRACT
`JSON_EXTRACT` returns values with surrounding quotes (e.g. `"roas_7d"`). Equality comparisons fail silently.
`json_extract_string` returns clean values without quotes (e.g. `roas_7d`).
- **Apply:** Always use `json_extract_string` for string comparisons in WHERE clauses.
- **Chat:** 93 (duplicate detection)

### 15. Open DB Connection BEFORE Using It in Queries
If `conn = _get_warehouse()` appears after a query that uses `conn`, the query throws a silent `NameError` swallowed by `except Exception: pass`. The save proceeds as if no check occurred.
- **Apply:** Always open `conn` before any query that uses it. Never place connection opening after validation logic that runs queries.
- **Chat:** 93 (duplicate detection silently failing)

---

## RECOMMENDATIONS SYSTEM

### 16. JSON Endpoints Enable SPA Behavior
`/recommendations/cards` endpoint = instant tab switching without reload.
- **Apply:** Use JSON for dynamic content, server-side for initial load

### 17. Recommendations in Writable warehouse.duckdb
Analytics DB is read-only. Recommendations need INSERT/UPDATE.
- **Apply:** Write tables in warehouse.duckdb, read tables in ro.analytics.*

### 18. Duplicate Prevention: Check (campaign_id, rule_id)
Without check, engine creates duplicates every run.
- **Apply:** SELECT COUNT before INSERT, skip if exists

### 19. Verify DB Column Names Before Writing Routes
Brief says "bid", schema says "cpc_bid_micros". Verify actual names.
- **Apply:** View schema first, use actual column names

### 20. DuckDB Pattern: Open Writable + ATTACH Readonly
Radar needs reads (analytics) and writes (recommendations).
- **Apply:** `connect(warehouse.duckdb)` + `ATTACH warehouse_readonly AS ro`

### 21. Backend Limit Must Match Data Volume
limit=200 truncated Keywords to 162 of 1,256 recommendations.
- **Apply:** Development: 200, Production: 5000+ for high-volume entities

### 22. CSRF Exemptions for JSON APIs
JavaScript fetch() doesn't send CSRF tokens automatically. Exempt JSON routes.
- **Apply:** `csrf.exempt()` for Accept/Decline routes in app.py

---

## MARKETING WEBSITE

### 23. Test npm run build Before Deploy
Development (npm run dev) forgives errors. Build catches them.
- **Apply:** Always run build locally before pushing

### 24. Three.js r128 Doesn't Support colorSpace
CDN version is r128. texture.colorSpace causes runtime error.
- **Apply:** Remove `texture.colorSpace` line; check CDN version

### 25. CNAME Propagates Faster Than A Record
CNAME (www): 5-15 min. A (root): 15-60 min. Normal behavior.
- **Apply:** Test www first, wait 30-60 min for root

### 26. GoDaddy: Remove Old A Records First
Old parking page records conflict with Vercel records.
- **Apply:** Delete all old records before adding new

---

## SEARCH TERMS & KEYWORDS

### 27. Dry-Run First: Check Flag BEFORE Loading Client
Check dry_run before loading Google Ads client. Saves 500-1000ms, enables credential-free testing.
- **Apply:** Validate inputs in dry-run, load client only for live

### 28. Conservative Expansion Criteria
CVR ≥5%, ROAS ≥4.0×, Conv. ≥10 = high quality. Fewer but better suggestions.
- **Apply:** Start conservative, track acceptance rate

### 29. Sequential < 10 Items, Batch > 50
Sequential simpler, acceptable for <10 items (2s total).
- **Apply:** Add batching only when proven necessary

---

## RULES & COMPONENTS

### 30. Each Page Needs Specific Component Include
Generic rules_tab.html causes CSS/JS conflicts. Need entity-specific.
- **Apply:** keywords_rules_tab.html, ad_group_rules_tab.html, etc.

### 31. Document Schema Evolution
Keywords use old schema (condition_metric), new entities use new (condition_1_metric).
- **Apply:** Document divergence, plan future migration

### 32. Backward Compatibility via Column Retention
Add entity columns, keep campaign columns. Zero breaking changes.
- **Apply:** Add new columns, populate both, migrate code gradually

### 33. Database Migrations: Zero Data Loss
70 recs + 49 changes migrated successfully with scripts.
- **Apply:** Backup, migrate, verify zero NULLs, document

### 34. Backend Filter > Hardcoded Labels
get_action_label() filter = single source of truth, easy updates.
- **Apply:** Dynamic labels from backend functions, not database

### 35. Condition Schema: Always Handle Both op/ref AND operator/unit
Old seeded rules use `operator`/`unit` keys. New flow-builder rules use `op`/`ref` keys.
Both must be handled everywhere conditions are read — in rendering, in population, in plain English generation.
- **Apply:** Always use `cond.op || rfbNormOp(cond.operator)` and `cond.ref || rfbNormUnit(cond.unit)` pattern.
- **Chat:** 91-93 (flow builder population)

### 36. Duplicate Detection: Don't Include campaign_type_lock in Match
Including `campaign_type_lock` in duplicate check means tROAS and `all` variants aren't caught.
A budget rule increasing budget on roas_7d is a duplicate regardless of campaign type lock.
- **Apply:** Duplicate check = type + action_type + condition_1_metric only. No campaign_type_lock.
- **Chat:** 93

### 37. JS State Variables Reset by Form Reset — Set Them AFTER
If `_rfbIsTemplate`, `_rfbEditId`, `_rfbHasPreload` are set before `rfbResetForm()` is called,
they get wiped. The function resets all state variables to defaults.
- **Apply:** Always set state variables AFTER calling `rfbResetForm()`, never before.
- **Chat:** 93 (Save template button text leak)

---

## UI & UX

### 38. Empty State: Info vs Warning
Info (blue) = temporary. Warning (yellow) = structural.
- **Apply:** Match styling to cause and resolution path

### 39. Component Reuse: First Slow, Next Fast
Keywords: 7h. Shopping: 4h (43% faster). Ad Groups: 3h (57% faster). Ads: 2.5h (64% faster).
- **Apply:** First establishes pattern, subsequent apply it

### 40. Load More for >100 Items
1,256 recs at once = 8-10s. Load More (20 at time) = 200ms.
- **Apply:** >100 items always use Load More (page size 20-50)

### 41. Test AFTER Design Changes
Testing before redesign = wasted effort. Test final design.
- **Apply:** Test incrementally during dev, comprehensive after design done

### 42. Color-Coded Progress Bars for Performance Tables
N · X% format with inline colored progress bars instantly communicates performance tier.
- **Apply:** Use `an-` CSS prefix for analytics-specific classes to avoid conflicts
- **Chat:** 64

### 43. Unescaped Apostrophes in JS Single-Quoted Strings Cause SyntaxError
Strings like `'ROAS is declining vs the campaign's own baseline'` break JS parsing silently.
The entire script block fails to parse — all functions undefined, nothing works.
- **Symptom:** `Uncaught SyntaxError: Unexpected identifier` in console, page shows "Loading..."
- **Apply:** Escape apostrophes in JS strings as `\'` or switch to double-quoted strings.
- **Chat:** 91 (FLAG_PE_MAP labels)

---

## OUTREACH & EMAIL SYSTEM

### 44. Jinja/JavaScript Brace Conflict: Split the Braces
Jinja2 processes `{{ }}` before the browser sees JavaScript.
- **Apply:** `let template = "Hello " + '{' + '{' + "first_name}}";`
- **Chat:** 63

### 45. Pass Jinja Data to JavaScript via data Attributes
- **Apply:** `<div data-name="{{ lead.first_name }}">` → `document.getElementById('x').dataset.name`
- **Chat:** 63

### 46. Slide Panel Pattern for Detail Views
- **Apply:** Bootstrap offcanvas or custom fixed-position panel with CSS transition
- **Chat:** 62

### 47. Unread Counts: Decrement in JavaScript, Don't Reload
- **Apply:** Decrement badge textContent in JS immediately on mark-as-read.
- **Chat:** 62

### 48. Outreach Analytics: Integer Tracking Columns Are Truth
- **Apply:** Always query `open_count`, `click_count` — not timestamp columns.
- **Chat:** 64

### 49. MIMEText Requires ALL THREE Arguments for HTML Email
- **Apply:** `MIMEText(body_html, "html", "utf-8")` — never omit the third arg.
- **Chat:** 68

### 50. HTML Body Conversion Belongs in the Route, Not email_sender.py
- **Apply:** `(body or "").replace("\n", "<br>")` in `queue_send()` before calling `send_email()`.
- **Chat:** 68

### 51. Toast Success Path Often Missing — Always Check Both Branches
- **Apply:** Always add `showToast('...', 'success')` inside `if (data.success) { ... }`.
- **Chat:** 68

### 52. Diagnose Email Formatting via Gmail "Show Original" → Base64 Decode
- **Apply:** Gmail → ⋮ → Show original → find base64 block → decode. Definitive debugging method.
- **Chat:** 68

---

## PROCESS & WORKFLOW

### 53. Fresh PowerShell for Each Operation
- **Apply:** Always start with `taskkill /IM python.exe /F` then `cd C:\Users\User\Desktop\gads-data-layer`

### 54. Complete Files > Code Snippets
Christopher prefers complete ready-to-use files, not snippets.
- **Apply:** Return entire file with save path, not just changed lines

### 55. File Size Limit: Split Files >2000 Lines
Claude project files don't index properly if >2000 lines or >45KB.
- **Apply:** Split large files into focused components

### 56. 2-Tier Workflow (Claude Code) Is 40-50% Faster
- **Apply:** Use Claude Code (`npx @anthropic-ai/claude-code`) for multi-file builds

### 57. Seed Scripts Must Cover All Referenced Columns
- **Apply:** Trace every queried column back to seed source before building routes.
- **Chat:** 64

### 58. Worktrees: Add to .gitignore Early
- **Apply:** Add `.git/worktrees/` to .gitignore at project setup

### 59. Never Commit Before Christopher Confirms in Opera
- **Apply:** Test in Opera → Christopher confirms → then commit via Master Chat PowerShell.
- **Chat:** 68

### 60. Run Diagnostic Scripts Before Each Major Test Session
Before testing new features, run `full_audit.py` and `check_state.py` to confirm DB is clean.
Testing on a dirty DB wastes time — junk rows from previous sessions cause false failures.
- **Apply:** Always run audit scripts before test sessions. Keep cleanup scripts in project root.
- **Chat:** 93

### 61. Don't Commit Diagnostic Scripts to Repo Root
Diagnostic/cleanup scripts (check_state.py, full_audit.py, cleanup_junk.py etc.) clutter the repo root.
- **Apply:** Keep in `tools/` or `scripts/` folder, or add to .gitignore if one-off.
- **Chat:** 93

---

## ARCHITECTURE PRINCIPLES

### 62. Dry-Run Mode Is Non-Negotiable for Live API Operations
- **Apply:** Check `dry_run` flag as first operation, before any external calls

### 63. Changes Audit Trail for Every State-Modifying Action
- **Apply:** Write to changes table before returning success response

### 64. Constitution Framework: Safety Guardrails Are Non-Negotiable
- **Apply:** Never bypass Constitution checks even for testing

### 65. Single Source of Truth for Business Rules
- **Apply:** Rule changes go through JSON only; Python execution layer reads JSON

### 66. Entity_type String Values Must Be Exact
- **Apply:** Exact values: `'campaign'`, `'keyword'`, `'shopping_product'`, `'ad_group'`, `'ad'`

### 67. Component CSS Prefix Isolation
- **Apply:** `an-` for analytics, `re-` for replies, `qu-` for queue, etc.
- **Chat:** 64

### 68. Prototype CSS Must Be Stripped Before Using in Flask App
- **Symptom:** White rounded box with gaps on all sides of main content area
- **Apply:** Remove all `body`, `html`, `.container` resets from prototype stylesheets before Flask use.
- **Chat:** 81

### 69. Never Define `.d-none` in Page-Specific CSS Files
- **Symptom:** Client name and user label hidden in navbar on affected pages only
- **Apply:** Never redefine Bootstrap utility classes in custom CSS files
- **Chat:** 82

### 70. All render_template() Calls Must Pass client_name
- **Apply:** Every outreach `render_template()` call must include `client_name=config.client_name`
- **Chat:** 82

### 71. Quick Fixes in Master Chat, Large Builds in Claude Code
- **Apply:** 1–3 file edits with a clear change → Master Chat. 4+ files or new routes → Claude Code brief.
- **Chat:** 81–83

### 72. Templates Use is_template Boolean Flag, Not Separate Table
Templates are rules/flags rows with `is_template = TRUE`. Keeps the schema simple and reuses all existing CRUD routes.
- **Apply:** Filter templates with `WHERE is_template = TRUE`. Exclude from rules engine with `WHERE is_template = FALSE`.
- **Chat:** 93

### 73. except Exception: pass Silently Hides Critical Bugs
Using bare `except Exception: pass` to "safely" skip validation means real errors (missing conn, wrong syntax) go completely unnoticed and the code proceeds as if validation passed.
- **Apply:** Always log exceptions: `except Exception as e: print(f"[Warning] check failed: {e}")`. Never use bare pass on validation logic.
- **Chat:** 93 (duplicate detection)

---

## GOOGLE ADS API APPLICATION

### 74. API Application: Attach Design Document PDF
Google's compliance team asks for tool design documentation. A professional PDF showing architecture, API usage table, safety guardrails, and rules engine significantly strengthens the application.
- **Apply:** Always attach a design doc PDF when responding to Google API compliance requests.
- **Chat:** Master Chat 11 (March 2026)

### 75. API Application: Company URL Must Match Primary Domain
API centre Company URL should match the primary website. Using `.online` variant instead of `.com` looks less credible.
- **Apply:** Keep API centre Company URL updated to `christopherhoole.com` at all times.
- **Chat:** Master Chat 11

### 76. Google Ads API Access Levels: Test → Explorer → Basic → Standard
Explorer access = read production data, no writes. Basic = full read + write.
Upgrade from Test to Explorer can happen before full Basic Access is granted.
- **Apply:** Explorer access is a positive signal during the application review process. Keep monitoring email for Basic Access decision.
- **Chat:** Master Chat 11

---

## SYNTHETIC DATA & FEATURES PIPELINE (Chat 97)

### 77. YAML Unquoted Integers Parse as int, Not str
YAML parses `customer_id: 1254895944` as Python int. `DashboardConfig._get_customer_id()` must cast to str or all DB queries silently return 0 rows.
- **Apply:** Always `return str(self.config["customer_id"])` in config loaders. Always quote IDs in YAML: `customer_id: "1254895944"`.
- **Chat:** 97

### 78. Synthetic Data: Use VARCHAR for All ID Columns
When generating synthetic data, ID columns (campaign_id, ad_group_id, keyword_id) must match the type used in the primary tables. campaign_daily uses VARCHAR for campaign_id — all other tables must match.
- **Apply:** In generation scripts, always explicitly cast IDs to VARCHAR. Run type verification after generation.
- **Chat:** 97

### 79. DuckDB WAL Corruption: Always DETACH ro Before Closing
If a script attaches `warehouse_readonly.duckdb` as `ro` and exits uncleanly (crash, exception, or incomplete run), DuckDB leaves a `.wal` file. The next connection that tries to open `warehouse.duckdb` will attempt to checkpoint the corrupt WAL and call `os.abort()`, crashing Flask with no traceback.
- **Apply:** Always `DETACH ro` in a `try/finally` block before closing any connection. If Flask crashes silently after startup log, check for `warehouse.duckdb.wal` and delete it.
- **Chat:** 97

### 80. Bypass Pipeline Scripts for Local Feature Builds — Use Direct SQL
Pipeline scripts like `build_keyword_features_daily()` are designed for production API flows and can cause WAL corruption in local dev when they crash mid-run. For synthetic/test data, always build features tables directly with a single `CREATE TABLE AS SELECT` SQL query.
- **Apply:** Use `build_ad_features_direct.py` and `build_keyword_features.py` as the pattern. One SQL query, `DETACH ro` before close, done. Never use the pipeline for local builds.
- **Chat:** 97

---

## RECOMMENDATIONS ENGINE (Chats 97-100)

### 81. _load_monitoring_days Must Query DB Rules Table for DB Rule IDs
`_load_monitoring_days(rule_id)` originally only searched `rules_config.json`. Rule IDs like `db_campaign_7` dont exist in the JSON — returns 0 days — accepted recs go straight to Successful.
- **Apply:** When `rule_id` starts with `db_campaign_`, extract integer, query `cooldown_days` from DB rules table.
- **Chat:** 97

### 82. Enrichment Order Matters — Re-calculate Labels After action_type Is Set
`_enrich_rec()` sets `action_label` and `value_label` before `_enrich_with_rule_data()` adds `action_type`. Result: wrong labels every time.
- **Apply:** In `recommendations_cards()`, add a second loop AFTER `_enrich_with_rule_data()` that re-runs `get_action_label()` and re-calculates `value_label`/`value_suffix`.
- **Chat:** 97-100

### 83. CPC/CPA/Cost Metrics in Features Table Are in Micros
`cpc_w7_mean`, `cpa_w14_mean`, `cost_micros_w7_sum` store values in micros. Rule conditions are in pounds. Engine compared 5 against 5390056 — always true.
- **Apply:** Add 4th tuple element (divisor) to metric map: `"cpc_avg_7d": ("cpc_w7_mean", None, None, 1_000_000)`. Apply in `_get_metric_value()`.
- **Chat:** 99

### 84. Engine Should Load Only Most Recent Valid Snapshot Date
Engine loaded all 360 rows. Most recent dates had NULL names (no source data). Engine fell back to ID names.
- **Apply:** `WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM table WHERE customer_id = ? AND name_col IS NOT NULL)`. Pass customer_id twice.
- **Chat:** 100

### 85. Never Make Assumptions in Diagnosis — Always Test First
Multiple loops wasted when assumptions were made before running diagnostic scripts.
- **Apply:** Write diagnostic script, run it, read output before stating a diagnosis.
- **Chat:** 97-100

### 86. Never Update Cached Doc Versions — Always Request Current File First
Updating a doc from memory instead of current file creates version conflicts.
- **Apply:** Always request current file upload before editing any doc.
- **Chat:** Master Chat 12

---

## FLAGS SYSTEM (Master Chat 12 / Chat 101)

### 87. Flag vs_prev_pct Conditions Must Use Decimal Ratios, Not Whole Numbers
The features table stores `vs_prev_pct` metrics as decimal ratios (e.g. -0.1045 = -10.45% drop). Flag conditions authored in the flow builder were saved as whole-number percentages (e.g. -30). Engine compared -0.1045 < -30 — always false, flags never fired.
- **Apply:** Always store `vs_prev_pct` thresholds as decimals: -0.30 not -30, 0.50 not 50.
- **Diagnostic:** Run `check_flag_data.py` to see actual feature values vs thresholds before debugging engine.
- **Chat:** Master Chat 12

### 88. Functions Inside IIFE Are Not Accessible From Inline onclick Handlers
Inline `onclick="fnName()"` handlers run in global scope. If `fnName` is declared inside an IIFE `(function() { ... })()`, it is not accessible and the click silently does nothing — no error, just nothing happens.
- **Apply:** Always expose functions called from inline onclick to global scope: `window.fnName = function(...) {...}`
- **Symptom:** Clicking a row/button does nothing, no console error.
- **Chat:** Master Chat 12

### 89. stopPropagation on TD Silently Kills Event Delegation
If a `<td>` has `onclick="event.stopPropagation()"` and you rely on `document.addEventListener('click', ...)` event delegation for a child element (e.g. a dropdown toggle), the stop fires before the delegation listener ever sees the click. The dropdown never opens, no error.
- **Apply:** Only add `stopPropagation` when there is a genuine parent handler to suppress. Never add it defensively.
- **Symptom:** Dropdown works on some rows but not others — the broken rows have stopPropagation on a parent element.
- **Chat:** Master Chat 12

### 90. Bootstrap Dropdowns in Dynamically Rendered Rows Require Event Delegation
`new bootstrap.Dropdown(el)` called after `innerHTML` is set does not reliably work for dynamically rendered dropdown toggles. Bootstrap's own initialisation on `data-bs-toggle="dropdown"` only fires on page load.
- **Apply:** Use `document.addEventListener('click', ...)` event delegation scoped to `document` for all dropdown toggles in dynamically rendered tables. Do not use `bootstrap.Dropdown` reinit loops.
- **Chat:** Master Chat 12

### 91. Synthetic Data Swings Too Small for Flag Thresholds
All 30 flags use thresholds designed for real Google Ads accounts (e.g. -30% conversion drop). Synthetic data has much smaller swings (max ~10%). Most flags will never fire on synthetic data regardless of conditions being correct.
- **Apply:** To test flag UI with synthetic data, temporarily lower one threshold (e.g. flag 33 Conversion Drop from -0.30 to -0.05), test fully, then restore. Never commit a lowered threshold.
- **Chat:** Master Chat 12

### 92. Always Add Snoozed and History Sections to Entity Page Flag Subtabs
Entity pages (Campaigns, Ad Groups, Keywords, Ads, Shopping) need Snoozed and History collapsible sections on their Flags subtabs — not just active flags. Without them, users have no visibility of actioned flags on the entity they are viewing.
- **Apply:** All entity page Flags subtabs must include: Active table + collapsible Snoozed section + collapsible History section.
- **Chat:** Master Chat 12

---

**Total:** 92 lessons
**Version:** 7.0 | **Updated:** 2026-03-19
