# KNOWN PITFALLS - ADS CONTROL TOWER (A.C.T)

**Version:** 2.0
**Created:** 2026-02-28
**Updated:** 2026-03-06
**Purpose:** Troubleshooting guide with solutions and prevention strategies

**See Also:** LESSONS_LEARNED.md (best practices), MASTER_KNOWLEDGE_BASE.md (current state)

---

## 🗂️ CATEGORIES

1. **Template & CSS Issues** (7 pitfalls)
2. **Database & Query Issues** (5 pitfalls)
3. **Blueprint & Route Issues** (4 pitfalls)
4. **Drawer & Modal Issues** (2 pitfalls)
5. **Campaign & Data Issues** (3 pitfalls)
6. **Radar & Monitoring Issues** (3 pitfalls)
7. **Website Deployment Issues** (6 pitfalls)
8. **Search Terms & API Issues** (4 pitfalls)
9. **Multi-Entity Issues** (4 pitfalls)
10. **Outreach System Issues** (5 pitfalls) ← NEW

**Total:** 43 pitfalls with solutions

---

## TEMPLATE & CSS ISSUES

### 1. Template CSS Missing
**Problem:** Page loads with no styling, broken layout
**Cause:** Template extends base.html instead of base_bootstrap.html
**Solution:**
```html
<!-- Change this: -->
{% extends "base.html" %}
<!-- To this: -->
{% extends "base_bootstrap.html" %}
```
**Prevention:** Always use base_bootstrap.html for Bootstrap 5 pages

### 2. Jinja Template 500 Error
**Problem:** 500 error on page load, no specific error message
**Cause:** Jinja2 syntax error (missing {% endif %}, {% endfor %}, unmatched tags)
**Solution:**
- Check all {% if %} have matching {% endif %}
- Check all {% for %} have matching {% endfor %}
- Validate template with jinja2 Environment before deploying
**Prevention:** Test template rendering in isolation before full deployment

### 3. Bootstrap Grid Not Working
**Problem:** Columns stacking vertically instead of side-by-side
**Cause:** Missing Bootstrap CSS (wrong base template) or incorrect col classes
**Solution:** Verify base_bootstrap.html extended; check col-md-6 syntax
**Prevention:** Test responsive layout immediately after page creation

### 4. display:none + display:flex Conflict
**Problem:** Drawer/panel visible on page load
**Cause:** Both `display:none` and `display:flex` in same inline style — browser uses last one
**Solution:**
```html
<!-- WRONG: -->
<div style="display:none; display:flex;">

<!-- CORRECT: HTML has display:none, JS adds display:flex -->
<div id="drawer" style="display:none;">
```
```javascript
document.getElementById('drawer').style.display = 'flex';
```
**Prevention:** Never put both in inline style

### 5. Chart.js Canvas Not Rendering
**Problem:** Chart area blank, no error
**Cause:** Canvas element missing ID, or Chart.js loaded before DOM ready
**Solution:** Ensure canvas has unique ID; wrap Chart initialization in DOMContentLoaded
**Prevention:** Always initialize charts after DOM ready

### 6. Flatpickr Date Range Not Persisting
**Problem:** Date range resets on page navigation
**Cause:** Not using session-based persistence
**Solution:** Save dates to Flask session via AJAX on change; read from session on page load
**Prevention:** Always use session for user preferences, not URL params

### 7. Jinja/JavaScript Brace Conflict
**Problem:** Jinja2 tries to parse JavaScript template literals containing `{{variable}}`
**Cause:** Jinja2 processes `{{ }}` before browser sees JavaScript
**Solution:**
```javascript
// WRONG — Jinja processes this:
let template = `Hello {{first_name}}`;

// CORRECT — split the braces:
let template = `Hello ${ '{' + '{' }first_name}}`;

// OR use a data attribute to pass Jinja variables to JS:
// <div data-name="{{ lead.first_name }}">
// let name = el.dataset.name;
```
**Prevention:** Never use `{{ }}` inside JavaScript strings in Jinja templates

---

## DATABASE & QUERY ISSUES

### 8. DB Query Fails — Wrong Table Prefix
**Problem:** Query returns error or empty results unexpectedly
**Cause:** Using `analytics.table_name` instead of `ro.analytics.table_name`
**Solution:**
```sql
-- WRONG:
SELECT * FROM analytics.campaign_daily

-- CORRECT:
SELECT * FROM ro.analytics.campaign_daily
```
**Prevention:** Always use ro.analytics.* for read-only queries

### 9. Shopping Metrics Missing
**Problem:** CTR = 0 or NaN on Shopping page
**Cause:** `compute_campaign_metrics()` missing total_clicks
**Solution:** Always include `SUM(clicks) as total_clicks` in aggregation queries
**Prevention:** Include clicks in every metrics aggregation

### 10. Recommendations Truncated
**Problem:** Fewer recommendations showing than expected
**Cause:** Backend query limit=200 caps results
**Solution:** Increase limit for high-volume entities:
```python
# In recommendations.py — increase limit:
limit = 5000  # was 200, caused Keywords to show 162 of 1,256
```
**Prevention:** Set limit to 2× expected maximum data volume

### 11. Integer vs Timestamp Tracking Columns
**Problem:** open_count, click_count showing 0 despite emails being sent
**Cause:** Route queries `opened_at IS NOT NULL` (timestamp column) but seed script only populates integer columns (`open_count`, `click_count`, `cv_open_count`)
**Solution:**
```python
# WRONG — timestamp may never be written:
WHERE opened_at IS NOT NULL

# CORRECT — use integer column:
WHERE open_count > 0
```
**Prevention:** Verify which column type the seed script actually populates before querying

### 12. DuckDB: Can't Write After Read-Only Open
**Problem:** INSERT fails with "read-only" error
**Cause:** Opening warehouse.duckdb with `read_only=True`
**Solution:**
```python
# CORRECT pattern for Radar/any component needing reads + writes:
conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")
```
**Prevention:** Never open writable DB as read_only

---

## BLUEPRINT & ROUTE ISSUES

### 13. Blueprint Not Registered
**Problem:** Route returns 404 despite existing in routes file
**Cause:** Blueprint created but not registered in `act_dashboard/routes/__init__.py`
**Solution:** Add to `__init__.py`:
```python
from .new_module import bp as new_module_bp
app.register_blueprint(new_module_bp)
```
**Prevention:** Always register new blueprints immediately on creation

### 14. Route Decorator Quote Style Mismatch
**Problem:** str_replace fails to find route decorator
**Cause:** File uses single quotes `'`, str_replace uses double quotes `"`
**Solution:** View file first, copy exact quote style before any str_replace
**Prevention:** Always view current file before editing

### 15. rules_config.json Not Found
**Problem:** Rules API returns 500 — file not found
**Cause:** Routes are 3 levels deep: routes/ → act_dashboard/ → project root
**Solution:**
```python
# In any file inside routes/:
config_path = Path(__file__).parent.parent.parent / 'act_autopilot' / 'rules_config.json'
```
**Prevention:** Always use `.parent.parent.parent` from route files

### 16. CSRF 400 on Accept/Decline
**Problem:** JavaScript POST to recommendations route returns HTTP 400
**Cause:** JavaScript fetch() doesn't automatically include CSRF tokens
**Solution:** Add CSRF exemption in app.py:
```python
from flask_wtf.csrf import CSRFProtect
csrf.exempt(recommendations_bp)
# Or specific routes:
@csrf.exempt
@bp.route('/recommendations/accept', methods=['POST'])
```
**Prevention:** Always add CSRF exemptions for JSON API routes called from JavaScript

---

## DRAWER & MODAL ISSUES

### 17. Campaign Picker Empty
**Problem:** Scope card shows empty dropdown
**Cause:** Picker not fetching from API on open
**Solution:** Fetch on scope card click:
```javascript
fetch('/api/campaigns-list')
  .then(r => r.json())
  .then(data => populatePicker(data));
```
**Prevention:** Always wire campaign picker to live API endpoint

### 18. "Budget Budget" Double Word in UI
**Problem:** Action labels show "budget budget" or similar repetition
**Cause:** Using generic label + appending type from data
**Solution:** Use explicit type→label map:
```python
TYPE_LABELS = {
    'budget': 'Daily Budget',
    'bid': 'Target ROAS',
    'status': 'Campaign Status'
}
```
**Prevention:** Use explicit lookup maps, never concatenate type + label

---

## CAMPAIGN & DATA ISSUES

### 19. Ad Group Table Empty
**Problem:** Ad groups table shows no data
**Cause:** Querying `bid_micros` column which doesn't exist; correct column is `cpc_bid_micros`
**Solution:** Use `cpc_bid_micros` for ad group bid values
**Prevention:** Verify actual column names in DuckDB before writing queries

### 20. Sort Not Working on Full Dataset
**Problem:** Sorting works on current page only, not all data
**Cause:** Sort applied in Python after fetching page of data
**Solution:** Sort must be SQL-side `ORDER BY` before pagination
**Prevention:** Always apply ORDER BY in SQL, never in Python post-fetch

### 21. New Sort Column Not Working
**Problem:** Clicking new column header doesn't sort
**Cause:** Column not in ALLOWED_*_SORT whitelist
**Solution:** Add column to whitelist in route file:
```python
ALLOWED_CAMPAIGN_SORT = ['name', 'cost', 'roas', 'new_column']
```
**Prevention:** Add to whitelist when adding new sortable columns

---

## RADAR & MONITORING ISSUES

### 22. Radar "ro Catalog Does Not Exist"
**Problem:** Radar crashes with catalog error on startup
**Cause:** Radar connection doesn't ATTACH warehouse_readonly.duckdb
**Solution:** Always use the established pattern:
```python
conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")
```
**Prevention:** Copy exact connection pattern from radar.py

### 23. Radar Conflicts with Dashboard Connection
**Problem:** DuckDB "file is locked" or "already open" error
**Cause:** Opening same file twice with different configurations
**Solution:** Never open warehouse.duckdb with read_only=True anywhere if Radar is running
**Prevention:** All connections to warehouse.duckdb must be read-write

### 24. Changes JOIN to Recommendations Fails
**Problem:** Changes page shows no data or wrong data
**Cause:** No recommendation_id FK in changes table
**Solution:**
```sql
SELECT c.*, r.display_name
FROM changes c
JOIN recommendations r ON c.campaign_id = r.campaign_id AND c.rule_id = r.rule_id
QUALIFY ROW_NUMBER() OVER (PARTITION BY c.campaign_id, c.rule_id ORDER BY r.generated_at DESC) = 1
```
**Prevention:** Always join on compound key (campaign_id + rule_id)

---

## WEBSITE DEPLOYMENT ISSUES

### 25. Three.js colorSpace Error
**Problem:** Hero animation crashes with "colorSpace" property error
**Cause:** CDN uses Three.js r128 which doesn't support `colorSpace` property
**Solution:** Remove `texture.colorSpace = THREE.SRGBColorSpace;` line
**Prevention:** Check CDN version, verify API against that version's docs

### 26. Next.js Build Fails
**Problem:** `npm run build` fails, npm run dev was fine
**Cause:** Dev mode is forgiving; build catches all errors
**Solution:** Check all imports are valid, remove unused components, fix TypeScript errors
**Prevention:** Always run `npm run build` locally before pushing to Vercel

### 27. Vercel Deployment 404
**Problem:** Domain shows 404 after deployment
**Cause:** DNS not configured or pointing to wrong service
**Solution:** Add A record (76.76.21.21) + CNAME (cname.vercel-dns.com) in GoDaddy
**Prevention:** Verify DNS configuration before testing

### 28. www Works But Root Doesn't
**Problem:** https://www.christopherhoole.online works, https://christopherhoole.online doesn't
**Cause:** CNAME propagates in 5-15 min; A record takes 15-60 min
**Solution:** Wait 30-60 minutes for root domain A record to propagate
**Prevention:** Test www first; wait before declaring root broken

### 29. GoDaddy DNS Conflict
**Problem:** New Vercel records don't work despite being added
**Cause:** Old GoDaddy parking page A records conflict
**Solution:** Delete ALL existing A records before adding Vercel records
**Prevention:** Always clear old records first

### 30. Contact Form Doesn't Submit
**Problem:** Form submissions not reaching backend
**Cause:** Contact form frontend is complete but /api/leads endpoint not yet built
**Status:** Planned work item — Google Sheets integration via Vercel serverless function
**Prevention:** Note this is planned, not a bug

---

## SEARCH TERMS & API ISSUES

### 31. Dry-Run Still Loading Google Ads Client
**Problem:** Dry-run mode is slow, sometimes fails despite dry_run=True
**Cause:** dry_run check happens after client loading
**Solution:** Check dry_run flag as FIRST thing after request parsing:
```python
dry_run = request.json.get('dry_run', True)
if dry_run:
    return simulate_response()
# Only reach here for live mode:
client = load_google_ads_client()
```
**Prevention:** Always check dry_run before any external API calls

### 32. google_ads_config_path Attribute Error
**Problem:** AttributeError when loading Google Ads config
**Cause:** Config object doesn't have google_ads_config_path attribute
**Solution:** Manually detect config with fallback paths:
```python
for path in ['.', 'configs/', 'secrets/']:
    candidate = Path(path) / 'google-ads.yaml'
    if candidate.exists():
        config_path = candidate
        break
```
**Prevention:** Never assume config attribute; always use fallback detection

### 33. Expansion Flags in Wrong Column
**Problem:** Keyword expansion flags appearing in wrong table column
**Cause:** Old "Flag" header in table with wrong colspan
**Solution:** Remove old Flag header, update colspan to match actual column count
**Prevention:** Count columns carefully when adding/removing table columns

### 34. Search Terms Client-Side Search Limitation
**Problem:** Search only finds terms visible on current page
**Cause:** Client-side search by design — works on rendered rows only
**Known limitation:** For cross-page search, server-side required (adds reload)
**Recommendation:** Accept for Phase 1 (<1,000 rows), add server-side if users request

---

## MULTI-ENTITY ISSUES

### 35. Entity Type Contamination
**Problem:** Keywords showing campaign recommendations or vice versa
**Cause:** Filtering on wrong entity_type string
**Solution:** Use exact entity_type strings:
```
'campaign'         — Campaign recommendations
'keyword'          — Keyword recommendations
'shopping_product' — Shopping recommendations
'ad_group'         — Ad Group recommendations
'ad'               — Ad recommendations
```
**Prevention:** Copy exact string from database values, not guessing

### 36. Empty State Wrong Alert Style
**Problem:** Empty state styling looks like an error when it's temporary
**Cause:** Using warning (yellow) for temporary "no data yet" states
**Solution:**
- Info (blue/cyan) = temporary state, data will appear when conditions met
- Warning (yellow/orange) = structural issue (missing table, blocked feature)
**Prevention:** Choose alert style based on whether the issue is fixable by the user

### 37. Load More Missing on High-Volume Pages
**Problem:** Page freezes or is very slow loading all recommendations
**Cause:** Rendering 1,000+ cards at once
**Solution:** Add Load More pattern (20 cards initial, 20 per click):
```javascript
let loaded = 20;
function loadMore() {
    cards.slice(loaded, loaded + 20).forEach(c => c.style.display = '');
    loaded += 20;
}
```
**Prevention:** Any dataset >100 items should use Load More

### 38. Backward Compatibility Broken After Schema Change
**Problem:** Old campaign recommendations break after multi-entity migration
**Cause:** Removed campaign_id/campaign_name columns during migration
**Solution:** Always keep old columns; add new columns alongside:
```sql
-- Keep: campaign_id, campaign_name
-- Add: entity_type, entity_id, entity_name
```
**Prevention:** Never remove columns — add new ones alongside existing

---

## OUTREACH SYSTEM ISSUES

### 39. Opened/Clicked Metrics Showing Zero
**Problem:** Analytics page shows 0 opened, 0 clicked despite emails being sent
**Cause:** Route queries `opened_at IS NOT NULL` but that timestamp column is never written by seed script. Actual data lives in `open_count` / `click_count` / `cv_open_count` integer columns.
**Solution:**
```python
# WRONG:
WHERE opened_at IS NOT NULL

# CORRECT:
WHERE open_count > 0
WHERE click_count > 0
WHERE cv_open_count > 0
```
Also run `tools/seed_outreach_clicks.py` to populate integer columns.
**Prevention:** Check which columns the seed script actually writes before querying

### 40. Client Selector Auto-Switching on Page Load
**Problem:** Every outreach page load triggers `/switch-client/3` in logs, resetting client
**Cause:** `current_client_path = get_current_config()` returns a DashboardConfig object. Template comparison `{% if cpath == current_client_config %}` always False (object vs string), putting browser in undefined state that triggers spurious onchange.
**Solution:**
```python
# WRONG — returns DashboardConfig object:
current_client_path = get_current_config()

# CORRECT — returns string matching template comparison:
current_client_path = session.get("current_client_config")
```
**Prevention:** Always use `session.get("current_client_config")` to get current client path. Check all other routes use this pattern as the established standard.

### 41. Jinja/JavaScript Double Brace Conflict
**Problem:** Jinja2 tries to evaluate JavaScript template literals or variable placeholders containing `{{ }}`
**Cause:** Jinja2 pre-processes all `{{ }}` before the browser sees JavaScript
**Solution:**
```javascript
// WRONG — Jinja tries to evaluate {{first_name}}:
let body = "Hello {{first_name}}, ...";

// CORRECT — split the opening braces:
let body = "Hello " + '{' + '{' + "first_name}}, ...";

// OR use raw block:
// {% raw %} ... {{ first_name }} ... {% endraw %}
```
**Prevention:** Never use `{{ }}` in JavaScript strings inside Jinja templates. Pass Jinja data to JS via data attributes instead.

### 42. Duplicate Flask Process / Port Already In Use
**Problem:** Flask won't start — "Address already in use" on port 5000
**Cause:** Previous Flask process still running from earlier terminal session
**Solution:**
```powershell
taskkill /IM python.exe /F
# Then start Flask fresh:
python act_dashboard/app.py
```
**Prevention:** Always kill existing processes before starting a new Flask instance. Use a fresh PowerShell window.

### 43. Worktrees Causing Git Issues
**Problem:** Git operations fail with unexpected errors related to worktrees
**Cause:** Git worktrees not excluded from tracking
**Solution:** Add to `.gitignore`:
```
.git/worktrees/
```
**Prevention:** Add worktrees to .gitignore at project setup

---

**Version:** 2.0 | **Last Updated:** 2026-03-06
**Total Pitfalls:** 43 (37 original + 6 outreach)
**See Also:** LESSONS_LEARNED.md | MASTER_KNOWLEDGE_BASE.md
