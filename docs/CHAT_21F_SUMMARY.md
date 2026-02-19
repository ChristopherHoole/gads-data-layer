# CHAT 21F — MASTER CHAT SUMMARY
## Ads Page Bootstrap 5 Redesign — Full Session Record

**Chat:** 21f  
**Date:** 2026-02-19  
**Status:** COMPLETE ✅ — Master Chat Approved  
**Worker:** Claude (Sonnet)  

---

## Objective

Redesign the Ads page (`/ads`) with Bootstrap 5, matching the pattern from Chats 21c/21d/21e. Maintain all existing functionality and add: rules integration, ad strength visualisation, expandable asset rows.

Pre-chat answers from Master Chat:
- Q1: Correct table is `ro.analytics.ad_daily`  ← **this turned out to be wrong** (see Issues)
- Q2: Use snapshot_date range filtering (same as campaigns.py/ad_groups.py) ← **also wrong**
- Q3: headlines_count/descriptions_count are INTEGER counts; final_url is TEXT ← **also wrong**
- Q4: Overwrite existing /ads route to render ads_new.html directly
- Q5: Load rules via get_rules_for_page('ad'), report actual count

---

## Full Issue Log — Every Problem and Fix

### PROBLEM 1 — Page loaded but zero ads (first attempt)
**Symptom:** Page rendered, 0 ads, PowerShell showed:
```
Binder Error: Referenced column "status" not found in FROM clause!
Candidate bindings: "ad_daily.ad_status", "ad_daily.roas", 
"ad_daily.snapshot_date", "ad_daily.headlines", "ad_daily.final_url"
```
**Diagnosis:** Two sub-problems:
1. Column named `ad_status` not `status`
2. Error hint showed `headlines` not `headlines_count` and no `descriptions_count`

**Action taken:** Ran DESCRIBE command on live DB to get exact column names.

---

### PROBLEM 2 — Table `ad_daily` does not exist
**Symptom:** Running `DESCRIBE analytics.ad_daily` returned:
```
Catalog Error: Table with name ad_daily does not exist!
Did you mean "campaign_daily"?
```
**Diagnosis:** The table name given in pre-chat Q1 answers was wrong. `ad_daily` does not exist at all. Ran `SHOW ALL TABLES` to find the real table.

**Discovery:** The correct table is `analytics.ad_features_daily` — a pre-aggregated features table, not a raw daily table. This completely changes the query pattern required.

---

### PROBLEM 3 — `ro.analytics.ad_features_daily` does not exist in readonly catalog
**Symptom:** After rewriting query to use `ro.analytics.ad_features_daily`, error:
```
Catalog Error: Table with name ad_features_daily does not exist!
Did you mean "analytics.ad_features_daily"?
FROM ro.analytics.ad_features_daily
```
**Diagnosis:** Two separate databases exist:
- `warehouse_readonly.duckdb` → accessed as `ro.analytics.*`  
- `warehouse.duckdb` → accessed as `analytics.*`

`ad_features_daily` was only ever created in `warehouse.duckdb`. It was never synced to the readonly database. DuckDB's own error message confirmed this.

**Fix:** Changed both SQL occurrences from `ro.analytics.ad_features_daily` to `analytics.ad_features_daily`.

**Escalated to Master Chat:** Confirmed fix before implementing.

---

### PROBLEM 4 — Wrong query pattern (GROUP BY vs snapshot)
**Root cause:** Pre-chat answers assumed `ad_daily` was a raw daily table (like `campaign_daily`) requiring GROUP BY + SUM aggregation. `ad_features_daily` is pre-aggregated with windowed columns (`_7d`, `_30d`, `_90d`). One row per ad per snapshot date.

**Fix:** Complete query rewrite:
- FROM: GROUP BY + SUM + date range → TO: latest snapshot + windowed column selection
- Suffix variable (`7d`/`30d`/`90d`) controls which columns are selected
- Two `?` params passed for the subquery (DuckDB requires explicit binding for each usage)
- CTR and CPA calculated in Python from raw counts (no pre-calculated 90d versions exist)

---

### PROBLEM 5 — Rules tab blank
**Symptom:** Clicking Rules tab activated the tab but showed no content. Large blank space visible.

**Diagnosis:** `rules_tab.html` already wraps its entire content in:
```html
<div class="tab-pane fade" id="rules-tab">
```
The template had wrapped the include in ANOTHER identical div:
```html
<div class="tab-pane fade" id="rules-tab" role="tabpanel">
  {% include 'components/rules_tab.html' %}
</div>
```
Bootstrap manages the outer div only — the inner div (with the actual content) never receives the `show active` classes. Content was present but permanently faded/invisible.

**Fix:** Removed outer wrapper div. Moved `{% include 'components/rules_tab.html' %}` outside the `.tab-content` div entirely, as a direct sibling. The component's own div becomes Bootstrap's target.

---

### PROBLEM 6 — CTR/CPA metric cards too narrow
**Symptom:** CTR card showing `0.00%` stacked vertically across multiple lines.

**Root cause:** Cards 5 and 6 used `col-md-1` — only 1/12 of the grid width. Too narrow for the content.

**Fix:** Changed `col-md-1` to `col` (Bootstrap auto equal-width distribution across all 7 cards).

---

## DB Schema Discovery — Critical for Future Reference

### analytics.ad_features_daily — Confirmed Column List

```
customer_id        VARCHAR    PK
snapshot_date      DATE       PK — always query MAX(snapshot_date)
ad_id              BIGINT     PK
campaign_id        BIGINT
campaign_name      VARCHAR
ad_group_id        BIGINT
ad_group_name      VARCHAR
ad_type            VARCHAR    RSA / ETA / RDA / FTA etc.
ad_status          VARCHAR    ENABLED / PAUSED / REMOVED
ad_strength        VARCHAR    POOR / AVERAGE / GOOD / EXCELLENT / NULL
headlines          VARCHAR[]  Array — use array_length() for count
descriptions       VARCHAR[]  Array — use array_length() for count
final_url          VARCHAR
impressions_7d     BIGINT
clicks_7d          BIGINT
cost_micros_7d     BIGINT
conversions_7d     DOUBLE
conversions_value_7d DOUBLE
ctr_7d             DOUBLE
cvr_7d             DOUBLE
cpa_7d             BIGINT
roas_7d            DOUBLE
impressions_14d    BIGINT
clicks_14d         BIGINT
cost_micros_14d    BIGINT
conversions_14d    DOUBLE
conversions_value_14d DOUBLE
impressions_30d    BIGINT
clicks_30d         BIGINT
cost_micros_30d    BIGINT
conversions_30d    DOUBLE
conversions_value_30d DOUBLE
ctr_30d            DOUBLE
cvr_30d            DOUBLE
cpa_30d            BIGINT
roas_30d           DOUBLE
impressions_90d    BIGINT
clicks_90d         BIGINT
cost_micros_90d    BIGINT
conversions_90d    DOUBLE
conversions_value_90d DOUBLE
ctr_trend_7d_vs_30d DOUBLE
cvr_trend_7d_vs_30d DOUBLE
ctr_vs_ad_group    DOUBLE
cvr_vs_ad_group    DOUBLE
days_since_creation INTEGER
low_data_impressions BOOLEAN
low_data_clicks    BOOLEAN
low_data_flag      BOOLEAN
```

### Important notes on this table:
- No `ctr_90d` column — calculate in Python from `clicks_90d` / `impressions_90d`
- No `cpa_90d` column — calculate in Python from `cost_micros_90d` / `conversions_90d`
- `14d` window columns exist but dashboard only exposes 7/30/90 — 14d available for future use
- `cpa_7d` and `cpa_30d` are BIGINT (micros) not DOUBLE — divide by 1,000,000 if using directly
- `conversions_value` columns available for ROAS calculation if needed in future

---

## Files Delivered — Final State

### ads.py (full rewrite)
- Blueprint: `ads`
- Route: `/ads`
- Template: `ads_new.html`
- Functions: `load_ad_data()`, `apply_status_filter()`, `compute_metrics()`, `apply_pagination()`
- Table: `analytics.ad_features_daily` (NOT `ro.analytics.*`)
- Query pattern: latest snapshot + windowed suffix columns
- Status field: maps `ad_status` → `d['status']` for template compatibility
- Rules: `get_rules_for_page('ad', customer_id=config.customer_id)`

### ads_new.html (new file)
- Extends: `base_bootstrap.html` ✅
- No jQuery — vanilla JS only ✅
- No DB refs in template ✅
- NULL ad_strength handled → N/A grey badge ✅
- Rules components: `rules_tab.html`, `rules_sidebar.html`, `rules_card.html` all included ✅

---

## Test Results — Synthetic Client (customer_id: 9999999999)

```
[Ads] 983 ads loaded, 983 after filter, 12 rules
```

| Metric | Value |
|---|---|
| Total Ads | 983 |
| Clicks | 98,762 |
| Cost | $295,933.80 |
| Conversions | 4,039.6 |
| CTR | 4.82% |
| CPA | $73.26 |
| Ad Strength (Good/Excellent) | 240/983 |
| Poor Strength | 129 |
| Rules loaded | 12 |
| Pages | 40 (25/page) |

**All 10 success criteria: PASSED ✅**

---

## Pre-existing Issues (NOT introduced by Chat 21f)

| Issue | Detail |
|---|---|
| `favicon.ico` 500 errors | `404.html` template missing — affects all pages |
| `rule_helpers` warning `Unknown page_type 'ad_group'` | From Chat 21e — `ad_group` not registered as valid page type |
| Config YAML validation errors | Pre-existing across all client yaml files |

---

## Carry-Forwards to Chat 21h

| Item | Priority |
|---|---|
| Rules card renders below large blank gap on Ads tab | Medium — cosmetic |
| CPA thresholds hardcoded in template | Low — could be per-client config |
| `favicon.ico` 404 / missing `404.html` | Low — global fix needed |
| `rule_helpers` `ad_group` warning | Low — register page type in rule_helpers |

---

## Chat Sequence Status

| Chat | Page | Status |
|---|---|---|
| 21a | Bootstrap foundation | ✅ Complete |
| 21b | Main dashboard | ✅ Complete |
| 21c | Campaigns | ✅ Complete |
| 21d | Keywords | ✅ Complete |
| 21e | Ad Groups | ✅ Complete |
| 21f | Ads | ✅ Complete |
| 21g | Shopping View | ⏳ Next |
| 21h | Final Polish | ⏳ Pending |

---

## Next Action

Git commit all Chat 21f changes, then open **Chat 21g — Shopping View**.
