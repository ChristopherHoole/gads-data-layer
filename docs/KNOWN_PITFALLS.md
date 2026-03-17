# KNOWN PITFALLS - ADS CONTROL TOWER (A.C.T)

**Version:** 6.0
**Created:** 2026-02-28
**Updated:** 2026-03-17
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
14. **Synthetic Data & Features Pipeline Issues** (6 pitfalls) ← NEW

**Total:** 65 pitfalls with solutions

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

**Version:** 5.0 | **Last Updated:** 2026-03-15
**Total Pitfalls:** 59
**See Also:** LESSONS_LEARNED.md | MASTER_KNOWLEDGE_BASE.md

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

**Version:** 6.0 | **Last Updated:** 2026-03-17
**Total Pitfalls:** 65
**See Also:** LESSONS_LEARNED.md | MASTER_KNOWLEDGE_BASE.md
