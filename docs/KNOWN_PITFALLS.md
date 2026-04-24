# KNOWN PITFALLS - ADS CONTROL TOWER (A.C.T)

**Version:** 10.0
**Created:** 2026-02-28
**Updated:** 2026-04-23
**Purpose:** Troubleshooting guide with solutions and prevention strategies

**See Also:** LESSONS_LEARNED.md (best practices), MASTER_KNOWLEDGE_BASE.md (current state)

---

## CATEGORIES

1. **Template & CSS Issues** (7 pitfalls)
2. **Database & Query Issues** (7 pitfalls)
3. **Blueprint & Route Issues** (4 pitfalls)
4. **Drawer & Modal Issues** (2 pitfalls)
5. **Campaign & Data Issues** (3 pitfalls)
6. **Radar & Monitoring Issues** (3 pitfalls)
7. **Website Deployment Issues** (6 pitfalls)
8. **Search Terms & API Issues** (4 pitfalls)
9. **Multi-Entity Issues** (4 pitfalls)
10. **Outreach System Issues** (5 pitfalls)
11. **Email Sending Issues** (4 pitfalls)
12. **Layout & CSS Issues** (4 pitfalls)
13. **Rules & Templates Issues** (6 pitfalls)
14. **Synthetic Data & Features Pipeline Issues** (6 pitfalls)
15. **Recommendations Engine Issues** (5 pitfalls)
16. **Flags System Issues** (5 pitfalls)
17. **Multi-Entity Rules & Flags Issues** (5 pitfalls)
18. **ACT v2 Negatives Module Issues** (10 pitfalls) ← NEW (N1–N4)

**Total:** 90 pitfalls with solutions

---

## TEMPLATE & CSS ISSUES

### 1. Template CSS Missing
**Problem:** Page loads with no styling, broken layout
**Solution:** `{% extends "base_bootstrap.html" %}`
**Prevention:** Always use base_bootstrap.html for Bootstrap 5 pages

### 2. Jinja Template 500 Error
**Problem:** 500 error on page load
**Cause:** Jinja2 syntax error (missing endif, endfor, unmatched tags)
**Solution:** Check all if/for blocks have matching close tags

### 3. Bootstrap Grid Not Working
**Problem:** Columns stacking vertically
**Solution:** Verify base_bootstrap.html extended; check col-md-6 syntax

### 4. display:none + display:flex Conflict
**Problem:** Drawer/panel visible on page load
**Solution:**
```html
<div id="drawer" style="display:none;">
```
```javascript
document.getElementById('drawer').style.display = 'flex';
```

### 5. Chart.js Canvas Not Rendering
**Problem:** Chart area blank
**Solution:** Ensure canvas has unique ID; wrap Chart init in DOMContentLoaded

### 6. Flatpickr Date Range Not Persisting
**Problem:** Date range resets on page navigation
**Solution:** Save dates to Flask session via AJAX on change

### 7. Jinja/JavaScript Brace Conflict
**Problem:** Jinja2 parses JavaScript `{{variable}}`
**Solution:** Split braces: `'{' + '{'` or use `{% raw %}...{% endraw %}`

---

## DATABASE & QUERY ISSUES

### 8. DB Query Fails — Wrong Table Prefix
**Problem:** Query returns error or empty results
**Solution:** `SELECT * FROM ro.analytics.campaign_daily`

### 9. Shopping Metrics Missing
**Problem:** CTR = 0 or NaN
**Solution:** Always include `SUM(clicks) as total_clicks` in aggregation queries

### 10. Recommendations Truncated
**Problem:** Fewer recommendations than expected
**Solution:** `limit = 5000` — was 200, caused truncation

### 11. Integer vs Timestamp Tracking Columns
**Problem:** open_count showing 0 despite emails sent
**Solution:** `WHERE open_count > 0` not `WHERE opened_at IS NOT NULL`

### 12. DuckDB: Can't Write After Read-Only Open
**Problem:** INSERT fails with "read-only" error
**Solution:**
```python
conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")
```

### 13. json_extract_string vs JSON_EXTRACT — Quotes Issue
**Problem:** `JSON_EXTRACT(conditions, '$[0].metric') = 'roas_7d'` returns no match
**Cause:** `JSON_EXTRACT` returns `"roas_7d"` with surrounding quotes. Equality check fails.
**Solution:** Use `json_extract_string(conditions, '$[0].metric') = 'roas_7d'` — returns clean value without quotes.
**Prevention:** Always use `json_extract_string` for WHERE clause string comparisons in DuckDB.
**Chat:** 93

### 14. Silent Exception Swallowing — conn Not Open Before Query
**Problem:** Validation/duplicate check runs but never blocks anything
**Cause:** `conn = _get_warehouse()` placed AFTER the query that uses `conn`. NameError thrown, caught by `except Exception: pass`, save proceeds.
**Solution:** Always open `conn` before any code that uses it. Move connection open to top of function.
**Prevention:** Never use bare `except Exception: pass` on validation logic. Always log: `except Exception as e: print(f"check failed: {e}")`
**Chat:** 93

---

## BLUEPRINT & ROUTE ISSUES

### 15. Blueprint Not Registered
**Problem:** Route returns 404
**Solution:** Add to `__init__.py`: `app.register_blueprint(new_module_bp)`

### 16. Route Decorator Quote Style Mismatch
**Problem:** str_replace fails to find route decorator
**Solution:** View file first, copy exact quote style before any str_replace

### 17. rules_config.json Not Found
**Problem:** Rules API returns 500
**Solution:** `config_path = Path(__file__).parent.parent.parent / 'act_autopilot' / 'rules_config.json'`

### 18. CSRF 400 on Accept/Decline
**Problem:** JavaScript POST returns HTTP 400
**Solution:** `csrf.exempt(recommendations_bp)`

---

## DRAWER & MODAL ISSUES

### 19. Campaign Picker Empty
**Problem:** Scope card shows empty dropdown
**Solution:** Fetch on scope card click from `/api/campaigns-list`

### 20. "Budget Budget" Double Word in UI
**Problem:** Action labels show repeated words
**Solution:** `TYPE_LABELS = {'budget': 'Daily Budget', 'bid': 'Target ROAS', 'status': 'Campaign Status'}`

---

## CAMPAIGN & DATA ISSUES

### 21. Ad Group Table Empty
**Problem:** Ad groups table shows no data
**Solution:** Use `cpc_bid_micros` not `bid_micros`

### 22. Sort Not Working on Full Dataset
**Problem:** Sorting works on current page only
**Solution:** Sort must be SQL-side `ORDER BY` before pagination

### 23. New Sort Column Not Working
**Problem:** Clicking new column header doesn't sort
**Solution:** Add to `ALLOWED_*_SORT` whitelist in route

---

## RADAR & MONITORING ISSUES

### 24. Radar "ro Catalog Does Not Exist"
**Problem:** Radar crashes with catalog error
**Solution:**
```python
conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")
```

### 25. Radar Conflicts with Dashboard Connection
**Problem:** DuckDB "file is locked" error
**Solution:** Never open warehouse.duckdb with read_only=True anywhere if Radar is running

### 26. Changes JOIN to Recommendations Fails
**Problem:** Changes page shows no data
**Solution:** Join on compound key (campaign_id + rule_id) with QUALIFY ROW_NUMBER()

---

## WEBSITE DEPLOYMENT ISSUES

### 27. Three.js colorSpace Error
**Solution:** Remove `texture.colorSpace = THREE.SRGBColorSpace` for r128 compatibility

### 28. Next.js Build Fails
**Solution:** Always run `npm run build` locally before pushing to Vercel

### 29. Vercel Deployment 404
**Solution:** Add A record (76.76.21.21) + CNAME (cname.vercel-dns.com)

### 30. www Works But Root Doesn't
**Solution:** Wait 30-60 minutes for A record propagation

### 31. DNS Conflict
**Solution:** Delete ALL existing A records before adding Vercel records

### 32. Contact Form Doesn't Submit
**Status:** Planned work item — /api/leads endpoint not yet built

---

## SEARCH TERMS & API ISSUES

### 33. Dry-Run Still Loading Google Ads Client
**Solution:** Check `dry_run` flag before any external API calls

### 34. google_ads_config_path Attribute Error
**Solution:** Manually detect config with fallback paths

### 35. Expansion Flags in Wrong Column
**Solution:** Remove old Flag header, update colspan

### 36. Search Terms Client-Side Search Limitation
**Known limitation:** For cross-page search, server-side required

---

## MULTI-ENTITY ISSUES

### 37. Entity Type Contamination
**Solution:** Use exact strings: `'campaign'` / `'keyword'` / `'shopping_product'` / `'ad_group'` / `'ad'`

### 38. Empty State Wrong Alert Style
**Solution:** Info (blue) = temporary, Warning (yellow) = structural issue

### 39. Load More Missing on High-Volume Pages
**Solution:** Any dataset >100 items should use Load More

### 40. Backward Compatibility Broken After Schema Change
**Solution:** Never remove columns — add new ones alongside existing

---

## OUTREACH SYSTEM ISSUES

### 41. Opened/Clicked Metrics Showing Zero
**Solution:** `WHERE open_count > 0` not `WHERE opened_at IS NOT NULL`

### 42. Client Selector Auto-Switching on Page Load
**Solution:** `session.get("current_client_config")` not `get_current_config()`

### 43. Jinja/JavaScript Double Brace Conflict
**Solution:** Split braces or use `{% raw %}`

### 44. Duplicate Flask Process / Port Already In Use
**Solution:** `taskkill /IM python.exe /F` before starting Flask

### 45. Worktrees Causing Git Issues
**Solution:** Add `.git/worktrees/` to `.gitignore`

---

## EMAIL SENDING ISSUES

### 46. Email Body Has No Formatting
**Solution:** `(body or "").replace("\n", "<br>")` in `queue_send()` before calling `send_email()`

### 47. Special Characters Garbled in Email
**Solution:** `MIMEText(body_html, "html", "utf-8")` — all three args required

### 48. Toast Not Showing After Successful Send
**Solution:** Add `showToast('Email sent successfully!', 'success')` inside `if (data.success)` block

### 49. Email Formatting Debug — Use Gmail "Show Original"
**Solution:** Gmail → ⋮ → Show original → decode base64 content block

---

## LAYOUT & CSS ISSUES

### 50. White Box Gap on All Entity Pages
**Cause:** `table-styles.css` had prototype `body { padding }` and `.container { background }` overrides
**Solution:** Remove `body` and `.container` blocks from table-styles.css
**Chat:** 81

### 51. Navbar Text Hidden on Outreach Pages
**Cause:** `outreach.css` had `.d-none { display: none !important }` overriding Bootstrap utilities
**Solution:** Remove `.d-none` override from outreach.css
**Chat:** 82

### 52. Client Name Blank on Specific Pages
**Cause:** Templates and Analytics routes missing `client_name=config.client_name` in render_template()
**Solution:** Add `config = get_current_config()` and `client_name=config.client_name` to all outreach routes
**Chat:** 82

### 53. Duplicate Client Selector on Outreach Pages
**Cause:** Each outreach template had its own `<select class="outreach-client-selector">`
**Solution:** Remove page-level selectors — navbar.html handles client switching globally
**Chat:** 82

---

## RULES & TEMPLATES ISSUES

### 54. JS Syntax Error — Apostrophe in Single-Quoted String
**Problem:** Page shows "Loading..." forever, console shows `Uncaught SyntaxError: Unexpected identifier`
**Cause:** Unescaped apostrophe in a JS string literal e.g. `'ROAS vs the campaign's baseline'`
**Solution:** Escape apostrophes as `\'` or switch to double-quoted strings
**Prevention:** Always check plain English label strings for apostrophes before saving
**Chat:** 91

### 55. Flag Condition Labels Show Wrong Direction
**Problem:** "ROAS Spike" shows "ROAS declined > 50%" in Condition column
**Cause:** `FLAG_COND_LABELS` had a single fixed string per metric, used for both spike and drop variants
**Solution:** Make labels direction-aware objects: `{pos: 'ROAS increased', neg: 'ROAS declined'}`. Pick based on operator in `rfFlagCondText()`.
**Chat:** 91

### 56. Duplicate Detection Not Blocking — Silent NameError
**Problem:** Duplicate rules created despite detection code existing
**Cause:** `conn = _get_warehouse()` was placed AFTER the duplicate check. Check threw NameError, caught silently, save proceeded.
**Solution:** Move `conn = _get_warehouse()` to before the duplicate check.
**Chat:** 93

### 57. Duplicate Detection Too Strict — campaign_type_lock Mismatch
**Problem:** tROAS variant (lock=troas) not blocked when creating All variant (lock=all)
**Cause:** Check included `AND campaign_type_lock = ?` which required exact match
**Solution:** Remove campaign_type_lock from check. Match on type + action_type + condition_1_metric only.
**Chat:** 93

### 58. JS State Variables Wiped by rfbResetForm
**Problem:** `_rfbIsTemplate` set to true but modal still shows "Save" not "Save template"
**Cause:** State variable set before `rfbResetForm()` call, which resets it to false
**Solution:** Set `_rfbEditId`, `_rfbHasPreload`, `_rfbIsTemplate` AFTER `rfbResetForm()` in `openRulesFlow()`
**Chat:** 93

### 59. Template "Use template" Button Defined But Never Called
**Problem:** Edit template button does nothing when clicked
**Cause:** HTML calls `rfEditTemplate(id)` but the function was never defined in rules_flags_tab.html
**Solution:** Always verify function definitions exist for every onclick handler
**Prevention:** Search for all `onclick="rfXxx"` patterns and confirm each function is defined
**Chat:** 93

---

## SYNTHETIC DATA & FEATURES PIPELINE ISSUES

### 60. customer_id YAML Integer Type Mismatch
**Problem:** Keywords/Ads/Ad Groups tables show no rows despite data existing in DB
**Cause:** YAML parses unquoted integers as Python int (e.g. `customer_id: 1254895944` → int). `DashboardConfig._get_customer_id()` returned int, but DB stores customer_id as VARCHAR. WHERE clause never matched.
**Solution:** Cast in `_get_customer_id()`: `return str(self.config["customer_id"])`
**Prevention:** Always quote customer_id in YAML: `customer_id: "1254895944"`. Always `str()` cast in config loader.
**Chat:** 97

### 61. campaign_id Type Mismatch — BIGINT vs VARCHAR
**Problem:** Keywords/Ads/Ad Groups tables empty despite data in DB
**Cause:** Synthetic data generation wrote campaign_id as BIGINT in keyword_daily, ad_daily, ad_group_daily — but campaign_daily stores it as VARCHAR. Route joins failed silently.
**Solution:** Run migration to cast campaign_id to VARCHAR: `CREATE TABLE t_new AS SELECT * REPLACE (CAST(campaign_id AS VARCHAR) AS campaign_id) FROM t`
**Prevention:** Always use VARCHAR for all ID columns in synthetic data generation scripts.
**Chat:** 97

### 62. DuckDB WAL Corruption — Script Exits With ro Attached
**Problem:** Flask crashes on startup with `os._exit()` — no traceback visible
**Cause:** A script (e.g. features pipeline) exits uncleanly while `warehouse_readonly.duckdb` is attached as `ro`. DuckDB leaves a `.wal` file. Next connection (Flask → outreach `_ensure_schema()`) tries to checkpoint the corrupt WAL and calls `os.abort()`.
**Solution:** `del warehouse.duckdb.wal` in PowerShell, then rebuild features.
**Prevention:** Always `DETACH ro` before closing any connection that had readonly attached. Use `try/finally` to guarantee detach even on crash.
**Chat:** 97

### 63. Features Pipeline Causes WAL Corruption — Use Direct SQL Instead
**Problem:** `build_keyword_features_daily()` pipeline inserts rows then crashes on close, leaving corrupt WAL every time
**Cause:** The pipeline attaches readonly DB, does heavy work, then fails to close cleanly — DuckDB WAL is never checkpointed.
**Solution:** Bypass the pipeline entirely. Build features tables directly via a single `CREATE TABLE AS SELECT` SQL query from `keyword_daily`/`ad_daily`. Same approach as `build_ad_features_direct.py`.
**Prevention:** For synthetic/test data, always use direct SQL builds rather than pipeline scripts. Pipeline scripts are designed for production API data flows, not local DB operations.
**Chat:** 97

### 64. DROP VIEW IF EXISTS on a TABLE Throws Error
**Problem:** `DROP VIEW IF EXISTS analytics.campaign_features_daily` throws `Catalog Error: Existing object is of type Table`
**Cause:** DuckDB does not allow DROP VIEW on a TABLE even with IF EXISTS.
**Solution:** Use `DROP TABLE IF EXISTS` for tables. Check `information_schema.tables.table_type` first if unknown.
**Chat:** 97

### 65. outreach_poller.py Imports celery_app at Module Level
**Problem:** Flask crashes on startup if celery_app fails to initialise
**Cause:** Bottom of `outreach_poller.py` has `from act_dashboard.celery_app import celery_app` at module level. If Celery/Redis is unavailable this line crashes the import silently via `os._exit()`.
**Prevention:** This import exists for the Celery task decorator. If Memurai is not installed, the WAL corruption issue is more likely the cause of crashes — fix WAL first before suspecting Celery.
**Chat:** 97

---

## RECOMMENDATIONS ENGINE ISSUES (Chats 97-100)

### 66. Accept Goes Straight to Successful — Monitoring Skipped
**Problem:** Accepted recommendations skip Monitoring and go directly to Successful
**Cause:** `_load_monitoring_days()` only searched `rules_config.json`. DB rules have IDs like `db_campaign_7` which dont exist in JSON — returns monitoring_days=0 — else branch sets status=successful.
**Solution:** When rule_id starts with `db_campaign_`, extract integer ID, query `cooldown_days` from DB rules table.
**Chat:** 97

### 67. Action Label Shows Wrong Rule Type — tROAS Instead of CPC Cap
**Problem:** "Decrease Max CPC Cap" rule shows "Decrease tROAS target by 10%" in Action column
**Cause:** `_enrich_rec()` calls `get_action_label()` before `action_type` is set. `action_type` is only added later by `_enrich_with_rule_data()`. `get_action_label()` gets empty string, falls through to tROAS label.
**Solution:** Add second loop in `recommendations_cards()` AFTER `_enrich_with_rule_data()` that re-runs `get_action_label()` and re-calculates `value_label`/`value_suffix`.
**Chat:** 97-100

### 68. CPC/CPA Rule Fires on All Campaigns — Micros vs Pounds
**Problem:** Rule fires on all campaigns when only some should qualify
**Cause:** `cpc_w7_mean` in features table stores value in micros (e.g. 5390056 = £5.39). Rule condition `value=5` is in pounds. Engine compares 5390056 > 5 — always true.
**Solution:** Add 4th tuple element (divisor=1_000_000) to CPC/CPA/cost entries in CAMPAIGN_METRIC_MAP. Apply divisor in `_get_metric_value()`.
**Chat:** 99

### 69. Engine Loads 360 Rows — Campaign Names Show as IDs
**Problem:** Engine processes all historical rows; most recent rows have NULL campaign_name
**Cause:** Synthetic data not updated daily. Features rebuild creates rows for today/yesterday with NULL names. Engine query was `SELECT * ORDER BY snapshot_date DESC` — iterates all rows including NULL-name ones.
**Solution:** `WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM table WHERE customer_id=? AND name_col IS NOT NULL)`. Two customer_id params needed.
**Chat:** 100

### 70. Rules 19/20 Never Fire — op=None in DB Conditions
**Problem:** Rules 19 and 20 never generate recommendations despite being enabled
**Cause:** Flow builder saved conditions with op=None and ref=None. Engine calls `_evaluate(value, None, threshold)` which returns False.
**Solution:** Run `scripts/fix_rules_19_20_conditions.py` to set correct op and ref values.
**Prevention:** When creating rules via flow builder, always verify conditions with check_bid_rules.py after saving.
**Chat:** 99

---

## FLAGS SYSTEM ISSUES (Master Chat 12)

### 71. Flag vs_prev_pct Thresholds Stored as Whole Numbers — Engine Never Fires
**Problem:** All percentage-based flags generate 0 results despite correct conditions
**Cause:** Flow builder saved thresholds as whole-number percentages (e.g. -30) but features table stores decimal ratios (e.g. -0.1045). Engine compares -0.1045 < -30 — always false.
**Solution:** Run `fix_all_flag_conditions.py` — divides all vs_prev_pct values by 100 and sets missing op/ref values. Already run — do NOT re-run.
**Prevention:** Always store vs_prev_pct thresholds as decimals. Check with `check_flag_data.py` before debugging engine.
**Chat:** Master Chat 12

### 72. Flag Conditions with op=None Never Evaluate — Always False
**Problem:** Specific flags (e.g. CPA Spike, CTR Drop) never fire even with correct thresholds
**Cause:** Flow builder saved conditions with `op=None` and `ref=None`. Engine calls `_evaluate(value, None, threshold)` which returns False.
**Solution:** Set correct op values: Drop flags use `lt`, Spike flags use `gt`. Run `fix_all_flag_conditions.py`.
**Prevention:** After creating flags via flow builder, always verify conditions with a check script before testing.
**Chat:** Master Chat 12

### 73. Bootstrap Dropdown Reinit Doesn't Work on Dynamically Rendered Rows
**Problem:** `new bootstrap.Dropdown(el)` called after innerHTML set — dropdown still doesn't open
**Cause:** Bootstrap dropdown initialisation via JS reinit is unreliable for dynamically injected HTML.
**Solution:** Use `document.addEventListener('click', ...)` event delegation on `document` instead. Catches all toggles regardless of when they were rendered.
**Chat:** Master Chat 12

### 74. stopPropagation on TD Silently Blocks Event Delegation Dropdowns
**Problem:** Dropdown works on active flag rows but not on snoozed/history rows
**Cause:** `onclick="event.stopPropagation()"` on the Actions `<td>` in snoozed/history rows fires before the document-level delegation listener sees the click. Dropdown never opens, no error.
**Solution:** Remove `stopPropagation` from any `<td>` that has no parent `<tr onclick>` to suppress. Only needed on active rows where row-expand must be prevented.
**Chat:** Master Chat 12

### 75. window.fnName Required for onclick Handlers in Dynamically Rendered HTML
**Problem:** Clicking a flag row or button does nothing — no console error
**Cause:** Function declared inside IIFE is not accessible from inline `onclick` which runs in global scope.
**Solution:** Expose all functions called from inline onclick: `window.toggleFlagExpand = function(id) {...}`
**Prevention:** Any function called from dynamically rendered HTML must be on `window`.
**Chat:** Master Chat 12

---

## MULTI-ENTITY RULES & FLAGS ISSUES (Chat 107)

### 76. Wrong Entity Rules Showing on Page — Missing entity_type Filter
**Problem:** Ad group rules appear on Campaigns page, or vice versa
**Cause:** Rules query missing `WHERE entity_type = 'campaign'` filter. Database has rows with different entity_type values, route loads them all.
**Solution:** Add `WHERE entity_type = '{entity}'` to ALL rules/flags queries in entity-specific routes (campaigns.py, ad_groups.py, keywords.py, etc.)
**Prevention:** ALWAYS filter by entity_type in ALL rules queries. Never rely on seeded data to enforce separation.
**Example:**
```python
# WRONG - loads all rules regardless of entity
rules = conn.execute("SELECT * FROM rules WHERE enabled = true").fetchall()

# CORRECT - filters by entity type
rules = conn.execute("""
    SELECT * FROM rules 
    WHERE entity_type = 'campaign' AND enabled = true
""").fetchall()
```
**Chat:** 107

### 77. Modal Visible at Bottom of Page on Load
**Problem:** Rules flow builder modal visible at bottom of page when page loads, instead of hidden
**Cause:** Modal overlay div missing `display:none` in inline style attribute
**Solution:** Add `style="display:none;"` to modal overlay div:
```html
<div id="ag-rules-flow-overlay" style="display:none;">
```
**Prevention:** Always verify modal overlay has `display:none` by default. Modal visibility is controlled by adding/removing `.show` class which sets `display: flex`.
**Chat:** 107

### 78. Modal Appearing at Bottom Instead of Centered Popup
**Problem:** Modal appears as a box at bottom of page instead of centered overlay popup
**Cause:** CSS positioning rules missing or incorrect on modal overlay div
**Solution:** Verify modal overlay CSS has ALL required positioning properties:
```css
#ag-rules-flow-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1050;
    background-color: rgba(0, 0, 0, 0.5);
    display: none;  /* hidden by default */
    align-items: center;
    justify-content: center;
}
#ag-rules-flow-overlay.show {
    display: flex;  /* centered popup when shown */
}
```
**Prevention:** Always verify CSS selector matches div ID exactly. Copy working modal CSS from campaigns modal (rules.css) and adapt ID prefix.
**Chat:** 107

### 79. Toast Appearing at Bottom of Page Instead of Sliding In
**Problem:** Success/error toast appears at bottom of page content instead of sliding in from corner
**Cause:** Entity-specific toast container ID (e.g. `#ag-rules-toast-wrap`) has no CSS styling. Only the base toast container (e.g. `#rules-toast-wrap`) has `position: fixed` rules.
**Solution:** Combine all toast container IDs into one CSS rule:
```css
#rules-toast-wrap,
#ag-rules-toast-wrap,
#kw-rules-toast-wrap {
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 1060;
    max-width: 400px;
}
```
**Prevention:** When adding new entity modal, add its toast container ID to the combined CSS rule. Never create separate toast containers with different positioning.
**Chat:** 107

### 80. Risk Level Always Changes to "High" When Editing
**Problem:** Editing any rule always changes risk level to "High", regardless of current value (Low/Medium/High)
**Cause:** Auto-risk calculation function (`agRfbAutoRisk()`) runs AFTER dropdown is populated, overwriting the value even when editing an existing rule
**Solution:** Add edit-mode guard to auto-risk function:
```javascript
function agRfbAutoRisk() {
    if (_agRfbEditId) return;  // Skip auto-risk when editing
    // ... auto-risk logic for new rules only
}
```
**Prevention:** Auto-risk logic should ONLY run for new rules, never when editing. Check `_editId` state variable at start of all auto-calculation functions.
**Alternative:** Move auto-risk call to BEFORE dropdown population in edit flow, then re-set dropdown value after.
**Chat:** 107

---

## ACT v2 NEGATIVES MODULE ISSUES (N1–N4, Apr 2026)

### 81. DuckDB 1.1.0 UPDATE-on-UNIQUE False-Positive PK
**Problem:** `UPDATE act_v2_phrase_suggestions SET target_list_role = ? WHERE id = ?` throws `ConstraintException: Duplicate key violates primary key` even when no real duplicate exists and the new value is unique.
**Cause:** DuckDB 1.1.0's index layer treats UPDATEs on UNIQUE-constrained columns as insert-then-delete; the pre-image key is briefly "still present" in the index view and the new value looks like a dupe.
**Solution (no real change):** Read the current value first. Only issue the UPDATE if the value is actually changing. See N1q in `bulk_update_phrase_suggestions`.
**Solution (real change):** DELETE by id, then INSERT with the same id + new values. See N4d.
**Prevention:** Any UPDATE touching a UNIQUE column needs this pattern. Affected tables in this project: `act_v2_phrase_suggestions`, anything with a composite UNIQUE where the mutable column participates.
**Ticket:** N1q / N4d

### 82. DuckDB 1.1.0 DELETE+INSERT-Same-ID Inside BEGIN/COMMIT Fails
**Problem:** Followed the "wrap DELETE + INSERT in a single transaction for atomicity" pattern and hit the same false-positive PK error on the INSERT.
**Cause:** Within an explicit transaction, DuckDB 1.1.0 retains the DELETE'd row's primary-key slot in the in-transaction index view. An INSERT with the same id trips as a duplicate.
**Solution:** Autocommit each statement (no explicit `BEGIN`/`COMMIT`). DELETE commits, the index releases the key, INSERT succeeds. For atomicity, pre-read the full row and add a compensating re-INSERT in the `except` branch that restores the original state, then re-raise. Log the compensation failure with `logger.exception` so a worst-case row loss is at least visible.
**Verified:** Both `:memory:` and file-backed DuckDB 1.1.0 connections.
**Prevention:** Do not reach for `BEGIN/COMMIT` to make this safe — it makes it worse. Autocommit + compensation is the working pattern.
**Ticket:** N4d

### 83. Stale Negative-List Matches — Missing snapshot_date Filter
**Problem:** ACT kept flagging search terms as "already blocked in GAds" days after the user had removed the neg keyword. Evidence: DBD removed `over 60s` from the 2026-04-21 snapshot, but Pass 1 on 2026-04-22 still showed `pass1_reason_detail = 'over 60s|2_word_phrase'`.
**Cause:** `_load_client_config` in pass1/pass3 UNIONed across every historical `snapshot_date` in `act_v2_negative_list_keywords`. Once a keyword ever existed in any snapshot, it stayed "in the neg list" forever.
**Solution:** Resolve `MAX(snapshot_date)` once per run. Add `AND kw.snapshot_date = ?` to every neg-list query. Fall back to empty sets when no snapshot exists, log a warning, let downstream rules still run.
**Prevention:** Any query against a snapshot-archived table must filter by the latest `snapshot_date` for the client. Grep for `act_v2_negative_list_keywords` before touching the neg engine.
**Ticket:** N2 Part 1

### 84. PMax API `campaign_search_term_insight` Returns NULL Cost
**Problem:** PMax rows in `act_v2_search_terms` had `cost=NULL`, so no cost-based signals worked for PMax.
**Cause:** The `campaign_search_term_insight` resource prohibits `metrics.cost_micros`. Google Ads API doesn't expose per-term PMax cost via any API surface; only the UI's scheduled "Search terms report" CSV has it.
**Solution:** Manual CLI ingestion from the CSV export — `pmax_csv_ingest.py` upserts into `raw_pmax_search_term_csv`, `act_v2_search_terms` (PMax slice only), and `act_v2_pmax_other_bucket`. Engine reads `act_v2_search_terms` unchanged.
**Prevention:** If an ACT feature needs PMax cost, assume API won't have it and plan for the CSV path.
**Ticket:** N4

### 85. GAds CSV Export: UTF-16+Tab vs UTF-8+Comma
**Problem:** Parser broke on the scheduled-email-link CSV despite working on the manual download.
**Cause:** Google sends two different shapes — manual download is UTF-8 + comma, scheduled-email link is UTF-16 + tab.
**Solution:** Detect encoding via BOM (`\xff\xfe` / `\xfe\xff` → UTF-16, else UTF-8-sig). Detect delimiter by counting tabs vs commas in the header row. See `pmax_csv_ingest._detect_encoding` / `_detect_delimiter`.
**Prevention:** Never hardcode encoding or delimiter on Google CSVs. Test both shapes.
**Ticket:** N4b

### 86. CSS `nth-child` Column Widths Shift When Prepending a Column
**Problem:** Adding a 44px `#` column to a wide table broke wrapping on Search term / Reason / Keyword — wide columns stretched, narrow columns shrank.
**Cause:** The existing widths were pinned via `.st-table--wide th:nth-child(N)` selectors. Prepending a column shifted every downstream nth-child by +1 — the "Status" rule was now sizing Reason, Reason was sizing Target list, etc.
**Solution:** Shift every nth-child selector +1 when a column is prepended. Also hard-lock the new column (`width` + `min-width` + `max-width`) so the browser can't redistribute it.
**Prevention:** Prefer semantic class selectors (`.col-num`, `.col-search-term`, etc.) over positional `nth-child` for column widths. When you inherit an `nth-child`-driven table and need to add a column, remember every downstream index needs to shift.
**Ticket:** N3-hotfix-1

### 87. Jinja Template Key Mismatch Renders Empty String Silently
**Problem:** `<div id="negLists" data-client-id="{{ client.client_id }}">` rendered as `data-client-id=""`. JS read an empty string, API returned 400 "client_id required".
**Cause:** Route builds the `client` dict with key `id`, not `client_id`. Jinja renders an undefined attribute as empty, no error.
**Solution:** One-char fix (`client.id`). Add a defensive early-return in the consuming JS: if `dataset.clientId` is empty, render a human-readable error and `console.error` rather than firing the API call.
**Prevention:** Grep for `client.client_id` in templates before committing (in this project, every correct usage is `client.id`). Defensive null-checks at the JS-to-API boundary are cheap insurance against template regressions.
**Ticket:** N2-hotfix-1

### 88. Wrong Column Name: `customer_id` vs `google_ads_customer_id`
**Problem:** `/v2/api/negatives/refresh-snapshot` threw `Binder Error: Referenced column "customer_id" not found`.
**Cause:** `act_v2_clients` stores the Google Ads customer id as `google_ads_customer_id`, not `customer_id`. The endpoint's lookup SQL used the wrong column name.
**Solution:** Query `SELECT google_ads_customer_id FROM act_v2_clients`. Keep the local variable named `customer_id` since `GoogleAdsDataPipeline`'s kwarg is `customer_id`.
**Prevention:** Run `DESCRIBE act_v2_clients` before writing new SQL against it. Every entity id column uses the `google_ads_<entity>_id` pattern.
**Ticket:** N2-hotfix-2

### 89. Missing CSRF Exemptions on New v2 JSON Endpoints
**Problem:** New `POST /v2/api/...` endpoints returned 400 on the first client call.
**Cause:** Every new endpoint in a `/v2/api/*` blueprint must be added to the CSRF-exempt list in `app.py` next to the existing v2 entries. The global CSRF protection catches unlisted JSON POSTs.
**Solution:** For every new endpoint, add `'blueprint.route_function'` to the `v2_negatives_api_routes` list (or a new list alongside it for new blueprints). `app.py` already loops over the list and runs `csrf.exempt(app.view_functions[name])`.
**Prevention:** When registering a new v2 blueprint / POST route, grep `csrf.exempt` in `app.py` and append. Missing this produces a 400, not a 500, so it's easy to miss locally.
**Ticket:** N2 / N3e

### 90. `btn-act--ghost` Doesn't Exist; Use `btn-act--decline`
**Problem:** Confirm-modal Cancel button was unstyled — invisible text on white.
**Cause:** `btn-act--ghost` is not defined in `v2_base.css`. Only `btn-act--approve`, `btn-act--decline`, `btn-act--details` exist in the v2 design system.
**Solution:** Use `btn-act--decline` for Cancel, `btn-act--approve` for primary confirm, `btn-act--details` for neutral / secondary actions.
**Prevention:** Grep `btn-act--` in `act_dashboard/static/css/v2_base.css` before reaching for a new variant. If you need a "ghost" button, define the class in v2_base.css first rather than inlining a style.
**Ticket:** N2-polish-1

---

**Version:** 10.0 | **Last Updated:** 2026-04-23
**Total Pitfalls:** 90
**See Also:** LESSONS_LEARNED.md | MASTER_KNOWLEDGE_BASE.md
