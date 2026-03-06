# KNOWN PITFALLS - ADS CONTROL TOWER (A.C.T)

**Version:** 1.0  
**Created:** 2026-02-28  
**Purpose:** Troubleshooting guide with solutions and prevention strategies

**See Also:** LESSONS_LEARNED.md (best practices), MASTER_KNOWLEDGE_BASE.md (current state)

---

## 🗂️ CATEGORIES

1. **Template & CSS Issues** (7 pitfalls)
2. **Database & Query Issues** (5 pitfalls)
3. **Blueprint & Route Issues** (3 pitfalls)
4. **Drawer & Modal Issues** (2 pitfalls)
5. **Campaign & Data Issues** (3 pitfalls)
6. **Radar & Monitoring Issues** (3 pitfalls)
7. **Website Deployment Issues** (6 pitfalls)
8. **Search Terms & API Issues** (4 pitfalls)
9. **Multi-Entity Issues** (4 pitfalls)

**Total:** 37 pitfalls with solutions

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
**Related:** Lesson #1

### 2. Jinja Template 500 Error
**Problem:** 500 error on page load, no specific error message  
**Cause:** Jinja2 syntax error (missing {% endif %}, {% endfor %}, unmatched tags)  
**Solution:**
- Check all {% if %} have matching {% endif %}
- Check all {% for %} have matching {% endfor %}
- Validate template with jinja2 Environment before deploying
**Prevention:** Test template rendering in isolation before full deployment  
**Related:** Chat 49 (Jinja2 syntax error)

### 3. Drawer Visible on Page Load
**Problem:** Drawer/modal shows immediately on page load instead of hidden  
**Cause:** Conflicting display values: `style="display:none; display:flex;"`  
**Solution:** Remove display:flex from inline style, let JavaScript add it
```html
<!-- Wrong: -->
<div class="drawer" style="display:none; display:flex;">
<!-- Correct: -->
<div class="drawer" style="display:none;">
<!-- JavaScript: drawer.style.display = 'flex'; -->
```
**Prevention:** Initial state in HTML, transitions in JavaScript  
**Related:** Lesson #10

### 4. New Sort Column Not Working
**Problem:** Clicking column header doesn't sort  
**Cause:** Column not in ALLOWED_*_SORT whitelist  
**Solution:** Add column to whitelist in route file
```python
ALLOWED_CAMPAIGN_SORT = ['name', 'status', 'budget', 'cost', 'conversions']
# Add new column: 'roas'
ALLOWED_CAMPAIGN_SORT = ['name', 'status', 'budget', 'cost', 'conversions', 'roas']
```
**Prevention:** Check whitelist when adding new sortable columns

### 5. Sort Not Working on Full Dataset
**Problem:** Sort only works on visible rows, not entire dataset  
**Cause:** Client-side sort instead of SQL-side ORDER BY  
**Solution:** Move sorting to SQL query
```python
# Wrong (Python sort, only sorts fetched rows):
rows = conn.execute("SELECT * FROM table").fetchall()
rows.sort(key=lambda x: x.cost)

# Correct (SQL sort, sorts entire dataset):
rows = conn.execute("SELECT * FROM table ORDER BY cost DESC").fetchall()
```
**Prevention:** Always use SQL ORDER BY for server-side sorting

### 6. Ad Group Table Empty
**Problem:** Ad groups table shows no data  
**Cause:** Using bid_micros column instead of cpc_bid_micros  
**Solution:** Use correct column name from schema
```python
# Wrong:
SELECT bid_micros FROM ad_group_daily
# Correct:
SELECT cpc_bid_micros FROM ad_group_daily
```
**Prevention:** Verify column names in schema before querying

### 7. Rules Showing 0 Count
**Problem:** Rules tab shows "0 rules" when rules exist  
**Cause:** Wrong regex pattern for detecting rule IDs  
**Solution:** Use correct regex: `r'_\d{3}(?:_|$)'`
```python
# Wrong:
pattern = r'_\d{3}'  # Matches campaign_1, campaign_12, campaign_123
# Correct:
pattern = r'_\d{3}(?:_|$)'  # Matches only campaign_001, campaign_002, etc.
```
**Prevention:** Test regex pattern with sample rule IDs

---

## DATABASE & QUERY ISSUES

### 8. DB Query Fails
**Problem:** "no such table: analytics.campaign_daily"  
**Cause:** Missing ro.analytics.* prefix  
**Solution:** Add ro prefix to analytics tables
```sql
-- Wrong:
SELECT * FROM analytics.campaign_daily
-- Correct:
SELECT * FROM ro.analytics.campaign_daily
```
**Prevention:** Always use ro.analytics.* for readonly database  
**Related:** Lesson #2

### 9. Route Replacement Fails
**Problem:** str_replace says "string not found"  
**Cause:** Quote style mismatch (' vs ")  
**Solution:** Match exact quote style from original
```python
# Original uses single quotes:
@bp.route('/recommendations', methods=['GET'])
# str_replace must use single quotes too:
old_str="@bp.route('/recommendations', methods=['GET'])"
```
**Prevention:** View file first, copy exact syntax

### 10. Shopping Metrics Missing
**Problem:** CTR shows 0% on Shopping page  
**Cause:** compute_campaign_metrics() doesn't include total_clicks  
**Solution:** Add SUM(clicks) to aggregation
```python
metrics = {
  'cost': SUM(cost),
  'clicks': SUM(clicks),  # Add this
  'ctr': (SUM(clicks) / SUM(impressions)) * 100
}
```
**Prevention:** Always include all metrics needed for calculations  
**Related:** Lesson #5

### 11. Collapse State Lost
**Problem:** Metrics card collapse state doesn't persist  
**Cause:** Not saving to session  
**Solution:** POST to /set-metrics-collapse endpoint
```javascript
fetch('/set-metrics-collapse', {
  method: 'POST',
  body: JSON.stringify({page_id: 'dashboard', collapsed: true})
})
```
**Prevention:** Use session storage for UI preferences

### 12. rules_config.json Not Found
**Problem:** FileNotFoundError when loading rules  
**Cause:** Wrong path depth from routes/  
**Solution:** Use .parent.parent.parent (3 levels up)
```python
# Wrong (only goes up 2):
Path(__file__).parent.parent / 'rules_config.json'
# Correct (goes up 3 to project root):
Path(__file__).parent.parent.parent / 'act_autopilot' / 'rules_config.json'
```
**Prevention:** Count directory levels, verify with print(path.exists())  
**Related:** Lesson #9

---

## BLUEPRINT & ROUTE ISSUES

### 13. Blueprint Not Registered
**Problem:** 404 error for new route  
**Cause:** Blueprint not added to __init__.py  
**Solution:** Register blueprint in act_dashboard/routes/__init__.py
```python
from . import dashboard, campaigns, keywords, changes  # Add changes
def init_app(app):
  app.register_blueprint(changes.bp)  # Add this
```
**Prevention:** Check __init__.py after creating new blueprint

### 14. Campaign Picker Empty
**Problem:** Campaign dropdown shows no options  
**Cause:** Not fetching from /api/campaigns-list  
**Solution:** Wire endpoint to fetch campaigns on click
```javascript
pickerButton.addEventListener('click', () => {
  fetch('/api/campaigns-list')
    .then(res => res.json())
    .then(data => populatePicker(data.campaigns));
});
```
**Prevention:** Test data fetching before declaring feature complete

### 15. "budget budget" Double Word
**Problem:** UI shows "budget budget" instead of "budget"  
**Cause:** Using rule_type as label without mapping  
**Solution:** Use explicit type→label map
```python
type_labels = {
  'budget': 'Budget',
  'bid': 'Bid Target',
  'status': 'Campaign Status'
}
label = type_labels.get(rule_type, rule_type)
```
**Prevention:** Always map internal names to display labels

---

## DRAWER & MODAL ISSUES

(Already covered in Template & CSS #3)

---

## CAMPAIGN & DATA ISSUES

### 16. Campaign Scope Pill Name Resolution
**Problem:** Campaign pill shows ID instead of name  
**Cause:** Not resolving campaign_id to campaign_name  
**Solution:** Query campaigns table for name
```python
name = conn.execute("""
  SELECT campaign_name FROM ro.analytics.campaign_daily
  WHERE campaign_id = ? LIMIT 1
""", [campaign_id]).fetchone()
```
**Prevention:** Always display names, not IDs

### 17. All Conv. Pipeline
**Problem:** "All Conversions" metric shows 0  
**Cause:** Column not populated in database  
**Solution:** Check if all_conversions column exists and has data
**Prevention:** Verify data availability before adding metric to UI

### 18. Shopping IS/Opt. Score Columns NULL
**Problem:** Impression Share and Optimization Score show NULL  
**Cause:** Columns exist but not populated (Google Ads API limitation)  
**Solution:** Document that these are future fields, show N/A when NULL
**Prevention:** Check sample data before adding metrics

---

## RADAR & MONITORING ISSUES

### 19. Radar "ro Catalog Does Not Exist"
**Problem:** Radar crashes with catalog error  
**Cause:** Not attaching readonly database  
**Solution:** ATTACH warehouse_readonly in Radar connection
```python
conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")
```
**Prevention:** Use established connection pattern  
**Related:** Lesson #20

### 20. Radar Read-Write Conflict
**Problem:** "database is locked" error  
**Cause:** Opening warehouse.duckdb with read_only=True  
**Solution:** Open as writable, ATTACH readonly separately
```python
# Wrong:
conn = duckdb.connect('warehouse.duckdb', read_only=True)
# Correct:
conn = duckdb.connect('warehouse.duckdb')  # Writable
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")
```
**Prevention:** Never open writable DB as readonly if writes needed

### 21. Changes JOIN to Recommendations
**Problem:** Can't join changes to recommendations (no FK)  
**Cause:** No recommendation_id foreign key  
**Solution:** Use compound key (campaign_id + rule_id) + QUALIFY
```sql
SELECT c.*, r.rule_name
FROM changes c
LEFT JOIN (
  SELECT campaign_id, rule_id, rule_name
  FROM recommendations
  QUALIFY ROW_NUMBER() OVER (PARTITION BY campaign_id, rule_id ORDER BY generated_at DESC) = 1
) r ON c.campaign_id = r.campaign_id AND c.rule_id = r.rule_id
```
**Prevention:** Document intentional lack of FK  
**Related:** Lesson #21

---

## WEBSITE DEPLOYMENT ISSUES

### 22. Three.js colorSpace Error
**Problem:** Canvas doesn't render, black screen  
**Cause:** r128 doesn't support texture.colorSpace property  
**Solution:** Remove or comment out colorSpace line
```javascript
// Wrong (r128 doesn't support):
texture.colorSpace = THREE.SRGBColorSpace;
// Correct:
// texture.colorSpace = THREE.SRGBColorSpace;  // Not supported in r128
```
**Prevention:** Check CDN version, use matching docs  
**Related:** Lesson #25

### 23. Next.js Build Fails
**Problem:** Vercel deployment fails  
**Cause:** TypeScript errors, missing imports, case sensitivity  
**Solution:** Run npm run build locally first
```bash
npm run build  # Catches errors before deploy
# Fix all errors
git commit -am "Fixed build errors"
git push  # Now Vercel succeeds
```
**Prevention:** Always test build locally before pushing

### 24. Vercel Deployment 404
**Problem:** Domain shows 404  
**Cause:** DNS not configured correctly  
**Solution:** Add both A and CNAME records in DNS
```
A @ 76.76.21.21
CNAME www cname.vercel-dns.com
```
**Prevention:** Follow Vercel DNS setup guide exactly

### 25. www Works But Root Doesn't
**Problem:** www.domain.com works, domain.com doesn't  
**Cause:** A record takes longer to propagate (30-60 min)  
**Solution:** Wait 30-60 minutes, check https://dnschecker.org  
**Prevention:** Expect propagation delay, document in handoff  
**Related:** Lesson #26

### 26. GoDaddy DNS Conflicts
**Problem:** Domain works intermittently  
**Cause:** Old parking page A records conflict with Vercel  
**Solution:** Delete ALL old A records before adding Vercel records  
**Prevention:** Clean slate - remove old before adding new  
**Related:** Lesson #27

### 27. Contact Form No Backend
**Problem:** Form submits but no email/database entry  
**Cause:** Backend integration not complete  
**Solution:** Wire to /api/leads endpoint (future work)  
**Prevention:** Mark as "frontend only" until backend ready

---

## SEARCH TERMS & API ISSUES

### 28. Dry-Run Still Loading API
**Problem:** Dry-run mode slow (500-1000ms)  
**Cause:** Loading Google Ads client before checking dry_run flag  
**Solution:** Check dry_run FIRST, before any client loading
```python
def add_negative_keywords(keywords, dry_run=False):
  if dry_run:
    return {'success': True, 'dry_run': True}  # Fast return
  client = GoogleAdsClient.load_from_storage()  # Only if live
```
**Prevention:** Always check flags before expensive operations  
**Related:** Lesson #32

### 29. google_ads_config_path Attribute Error
**Problem:** AttributeError: 'Config' has no attribute 'google_ads_config_path'  
**Cause:** Config doesn't have this attribute  
**Solution:** Manually detect with 3 fallback paths
```python
paths = ['google_ads_config.yaml', 'configs/google_ads_config.yaml', 'secrets/google_ads_config.yaml']
for path in paths:
  if os.path.exists(path): return path
```
**Prevention:** Don't assume config attributes, detect paths manually  
**Related:** Lesson #35

### 30. Expansion Flags in Wrong Column
**Problem:** Expansion flag appears in wrong table column  
**Cause:** Old header count doesn't match new columns  
**Solution:** Remove old "Flag" header, update colspan to 17 (was 16)  
**Prevention:** Count columns when adding new ones

### 31. CSRF 400 on Accept/Decline
**Problem:** HTTP 400 "Security token missing or invalid"  
**Cause:** JSON API routes require CSRF exemption  
**Solution:** Add csrf.exempt() in app.py
```python
csrf.exempt(recommendations.recommendation_accept)
csrf.exempt(recommendations.recommendation_decline)
```
**Prevention:** Exempt JSON APIs called from JavaScript  
**Related:** Lesson #43

---

## MULTI-ENTITY ISSUES

### 32. Rules Tab Generic Component
**Problem:** CSS/JS conflicts when multiple entity pages use rules_tab.html  
**Cause:** Generic component doesn't work for entity-specific schemas  
**Solution:** Create entity-specific components
```
keywords_rules_tab.html (for keywords page)
ad_group_rules_tab.html (for ad groups page)
ad_rules_tab.html (for ads page)
```
**Prevention:** Use specific components for different entity types  
**Related:** Lesson #36

### 33. Schema Field Mismatch
**Problem:** TypeError: 'condition_1_metric' not found  
**Cause:** Keywords use old schema (condition_metric), new entities use new (condition_1_metric)  
**Solution:** Use correct schema for each entity type  
**Prevention:** Document schema divergence, plan future migration  
**Related:** Lesson #37

### 34. Backend Limit=200 Truncates Data
**Problem:** Only 162 of 1,256 keywords show  
**Cause:** Query has LIMIT 200, keywords exceed limit  
**Solution:** Increase to limit=5000
```python
# Wrong:
SELECT * FROM recommendations LIMIT 200
# Correct:
SELECT * FROM recommendations LIMIT 5000
```
**Prevention:** Set limits to max expected × 2  
**Related:** Lesson #42

### 35. Entity Contamination
**Problem:** Keywords page shows campaign recommendations  
**Cause:** Missing entity_type filter  
**Solution:** Add exact entity_type match
```javascript
// Filter:
recs.filter(r => r.entity_type === 'keyword')  // Exact match
// Not:
recs.filter(r => r.entity_type.includes('keyword'))  // Too broad
```
**Prevention:** Use exact entity_type values: 'campaign', 'keyword', 'shopping_product', 'ad_group', 'ad'

### 36. Empty State Wrong Alert Style
**Problem:** Empty state uses wrong color (red when should be blue)  
**Cause:** Not differentiating temporary vs structural issues  
**Solution:** 
- Info (blue/cyan): Temporary, will resolve
- Warning (yellow): Structural, needs admin
```html
<!-- Temporary (conditions not met): -->
<div class="alert alert-info">
<!-- Structural (table missing): -->
<div class="alert alert-warning">
```
**Prevention:** Match styling to cause and solution  
**Related:** Lesson #44

### 37. Load More Missing on High-Volume
**Problem:** Page slow to load, browser lag  
**Cause:** Rendering 1,256 cards at once  
**Solution:** Add Load More pattern (20 cards/load)
```javascript
function loadMore() {
  const batch = allRecs.slice(displayedCount, displayedCount + 20);
  batch.forEach(rec => renderCard(rec));
  displayedCount += 20;
}
```
**Prevention:** Always use Load More for >100 items  
**Related:** Lesson #46

---

## QUICK REFERENCE TABLE

| Problem | Cause | Solution | Related Lesson |
|---------|-------|----------|----------------|
| No CSS | Wrong base template | Use base_bootstrap.html | #1 |
| Query fails | Missing ro prefix | Use ro.analytics.* | #2 |
| Drawer visible | Conflicting display | HTML: none, JS: flex | #10 |
| Campaign picker empty | No data fetch | Wire /api/campaigns-list | #12 |
| Radar crash | No ATTACH | ATTACH readonly as ro | #20 |
| Three.js black | Unsupported property | Remove colorSpace | #25 |
| Root domain 404 | DNS propagation | Wait 30-60 min | #26 |
| Dry-run slow | Loading client first | Check flag first | #32 |
| CSRF 400 | No exemption | csrf.exempt() routes | #43 |
| Only 162 of 1256 | Low limit | Increase to 5000 | #42 |

---

**Total Pitfalls:** 37  
**Categories:** 9  
**Purpose:** Quick troubleshooting, prevent recurring issues  
**Application:** Search by problem, find solution fast

**Version:** 1.0 | **Updated:** 2026-02-28
