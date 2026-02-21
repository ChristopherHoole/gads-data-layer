# CHAT 25 DETAILED SUMMARY — M4 TABLE OVERHAUL

**Dashboard 3.0 | Module 4 | Table Overhaul**
**Date:** 2026-02-21
**Status:** COMPLETE — Approved by Master Chat
**Preceding commit:** df7909c (M3 Chart Overhaul)
**Git commit:** pending

---

## OBJECTIVE

Overhaul all data tables across 5 dashboard pages to match exact Google Ads UI column sets, with server-side sorting, sticky first column, and status/match-type filters.

---

## STEP A — GENERATORS (completed before route work)

All 5 synthetic data generators run and verified.

| Generator | File | Result |
|---|---|---|
| A1 | `tools/testing/generate_synthetic_data_v2.py` | campaign_daily: 7,300 rows, 21 cols |
| A2 | `tools/testing/generate_synthetic_ad_group_data.py` | ad_group_daily: 23,725 rows, 30 cols |
| A3 | `tools/testing/generate_synthetic_keywords.py` | keyword_daily: 77,368 rows, 33 cols |
| A4 | `tools/testing/generate_synthetic_ads.py` | ad_features_daily: 983 rows, 51 cols |
| A5 | `tools/testing/generate_synthetic_shopping_v2.py` | shopping_campaign_daily: 7,300 rows, 26 cols |

`warehouse_readonly.duckdb` synced with `Copy-Item -Force warehouse.duckdb warehouse_readonly.duckdb`.

---

## STEP B — CAMPAIGNS (pre-existing, reference standard)

Not modified in this chat. Already complete from earlier work.

**24 columns:** Campaign (sticky) → Status → Type → Cost → Conv. Value → Conv. → Conv. Value/Cost → Cost/Conv. → Conv. Rate → All Conv. (5 cols) → Impr. → Clicks → Avg. CPC → CTR → Search IS → Search Top IS → Search Abs. Top IS → Click Share → Opt. Score → Bid Strategy

---

## STEP C — AD GROUPS

**File:** `act_dashboard/routes/ad_groups.py`
**Template:** `act_dashboard/templates/ad_groups_new.html` (or `ad_groups.html`)
**Table:** `ro.analytics.ad_group_daily`

**26 columns:** Ad Group (sticky) → Campaign → Status → Cost → Conv. Value → Conv. → Conv. Value/Cost → Cost/Conv. → Conv. Rate → All Conv. (5 cols) → Impr. → Clicks → Avg. CPC → CTR → Search IS → Search Top IS → Search Abs. Top IS → Click Share → Opt. Score → Target CPA → Bid Strategy

**Key notes:**
- Status column is `ad_group_status` in DB
- Target CPA: `target_cpa_micros / 1000000.0` with NULL handling
- Confirmed uses `ro.analytics.ad_group_daily` throughout

---

## STEP D — KEYWORDS

**File:** `act_dashboard/routes/keywords.py`
**Template:** `act_dashboard/templates/keywords_new.html`
**Table:** `ro.analytics.keyword_features_daily` (uses windowed `_w7` / `_w30` columns)

**17 columns (exact spec):**

| # | Column | DB Source |
|---|---|---|
| 1 | Keyword (sticky, match type pill inside) | `keyword_text` + `match_type` |
| 2 | Campaign | `campaign_name` |
| 3 | Ad Group | `ad_group_name` |
| 4 | Status | `status` |
| 5 | Cost | `cost_micros_{w}_sum / 1000000` |
| 6 | Conv. Value | `conversion_value_{w}_sum` |
| 7 | Conv. | `conversions_{w}_sum` |
| 8 | Conv. Value / Cost | CALC |
| 9 | Cost / Conv. | `cpa_{w} / 1000000` |
| 10 | Conv. Rate | CALC |
| 11 | Impr. | `impressions_{w}_sum` |
| 12 | Clicks | `clicks_{w}_sum` |
| 13 | Avg. CPC | CALC |
| 14 | CTR | CALC |
| 15 | Quality Score | `quality_score` |
| 16 | Exp. CTR | `quality_score_creative` |
| 17 | Ad Relevance | `quality_score_relevance` |

**Match type pill colours:** Exact=`bg-success`, Phrase=`bg-primary`, Broad=`bg-warning text-dark`
**QS colour coding:** 8–10 green, 5–7 orange, 1–4 red, NULL grey
**Columns NOT included:** All Conv. block, IS columns, Click Share, Landing Page Exp., Bid Strategy, Final URL

**Issues fixed during this chat:**
- Delivered 24 cols initially (used Campaigns spec by mistake) → corrected to 17
- Jinja nesting error from column removal (stray IS `<td>` cells + orphaned `{% else %}{% endif %}`) → fixed and validated with Jinja parser

---

## STEP E — ADS

**File:** `act_dashboard/routes/ads.py`
**Template:** `act_dashboard/templates/ads_new.html`
**Table:** `ro.analytics.ad_features_daily` (windowed 30d columns)

**24 columns:**

| # | Column | Notes |
|---|---|---|
| 1 | ☑ Checkbox | sticky left:0 |
| 2 | Ad (sticky) | `final_url` truncated + `ad_id` |
| 3 | Campaign | `campaign_name` |
| 4 | Ad Group | `ad_group_name` |
| 5 | Status | `ad_status` |
| 6 | Ad Type | `ad_type` (RSA/ETA/RDA) |
| 7 | Cost | `cost_micros_30d / 1000000` |
| 8 | Conv. Value | `conversions_value_30d` |
| 9 | Conv. | `conversions_30d` |
| 10 | Conv. Value / Cost | CALC |
| 11 | Cost / Conv. | `cpa_30d / 1000000` |
| 12 | Conv. Rate | `cvr_30d` |
| 13–17 | All Conv. block | NULL (Step A4 col not in schema) |
| 18 | Impr. | `impressions_30d` |
| 19 | Clicks | `clicks_30d` |
| 20 | Avg. CPC | CALC |
| 21 | CTR | `ctr_30d` |
| 22 | Ad Strength | progress bar (Excellent/Good/Average/Poor) |
| 23 | Final URL | full, non-sortable |
| 24 | Actions | dropdown |

**Ad Strength progress bar:**
- Excellent → 100% `bg-success`
- Good → 75% `bg-primary`
- Average → 50% `bg-warning`
- Poor → 25% `bg-danger`

**Result:** 983 ads loading ✅

---

## STEP F — SHOPPING

**File:** `act_dashboard/routes/shopping.py`
**Template:** `act_dashboard/templates/shopping_new.html` (Campaigns tab only)
**Table:** `ro.analytics.shopping_campaign_daily`

**24 columns:** Campaign (sticky) → Status → Type → Cost → Conv. Value → Conv. → Conv. Value/Cost → Cost/Conv. → Conv. Rate → All Conv. block (5, NULL) → Impr. → Clicks → Avg. CPC → CTR → Search IS (NULL) → Search Top IS (NULL) → Search Abs. Top IS (NULL) → Click Share (NULL) → Opt. Score (NULL) → Bid Strategy (NULL)

**Migration:** Old route queried `raw_shopping_campaign_daily` (legacy). Migrated to `ro.analytics.shopping_campaign_daily`.

**Bug fixed:** `compute_campaign_metrics` KeyError — old code used `c['conv_value']`, new schema returns `c['conversions_value']`. Fixed with `.get()` throughout for safety.

**Result:** 20 shopping campaigns loading ✅

---

## FILES MODIFIED

| File | Change |
|---|---|
| `act_dashboard/routes/keywords.py` | 17-col SQL, ALLOWED_KW_SORT updated, row dict processing cleaned |
| `act_dashboard/templates/keywords_new.html` | 17-col table, match type pill inside keyword, Jinja fix |
| `act_dashboard/routes/ads.py` | 24-col SQL on ad_features_daily, ALLOWED_ADS_SORT |
| `act_dashboard/templates/ads_new.html` | 24-col table, ad strength progress bar |
| `act_dashboard/routes/shopping.py` | ALLOWED_SHOPPING_SORT, migrated to shopping_campaign_daily, compute_campaign_metrics fix |
| `act_dashboard/templates/shopping_new.html` | Campaigns tab 24-col table |

---

## VERIFIED STATE

| Page | Rows | Cols | Sort | Filter | Pagination | Notes |
|---|---|---|---|---|---|---|
| Campaigns | 20 campaigns | 24 | ✅ | ✅ | ✅ | Pre-existing |
| Ad Groups | 65 ad groups | 26 | ✅ | ✅ | ✅ | |
| Keywords | 540 keywords | 17 | ✅ | ✅ | ✅ | Match type filter works |
| Ads | 983 ads | 24 | ✅ | ✅ | ✅ | Ad strength bars working |
| Shopping | 20 campaigns | 24 | ✅ | ✅ | ✅ | |

---

## KNOWN STATES (expected, not bugs)

- All Conv. columns show `—` on all pages — correct, all_conversions not populated by generators yet
- Shopping IS/Opt. Score/Click Share show `—` — correct, these are NULL in SQL pending real data
- `favicon.ico` 500 errors in PowerShell — pre-existing, unrelated to M4 (missing 404.html template)
- Config validation warnings — pre-existing, unrelated to M4

---

## ARCHITECTURAL DECISIONS

- All pages use `ro.analytics.*` prefix (readonly DB connection)
- Missing schema columns → SQL `NULL AS col_name` → displayed as `—` in template
- Sort whitelists (`ALLOWED_*_SORT`) prevent SQL injection on all pages
- Keywords uses `keyword_features_daily` (windowed), not `keyword_daily` (raw)
- Shopping migrated off legacy `raw_shopping_campaign_daily` to proper analytics table
