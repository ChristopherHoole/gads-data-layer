# CHAT 21F HANDOFF DOCUMENT
## Ads Page — Bootstrap 5 Redesign

**Status:** COMPLETE ✅  
**Date:** 2026-02-19  
**Master Chat Approval:** GRANTED  

---

## What Was Built

Full Bootstrap 5 redesign of the Ads page (`/ads` route), matching the patterns established in:
- Chat 21c — Campaigns
- Chat 21d — Keywords  
- Chat 21e — Ad Groups

The old Tailwind-based `ads.html` was replaced with a new `ads_new.html` (Bootstrap 5). The route was fully rewritten in `ads.py`.

---

## Files Modified

| File | Full Path | Change |
|---|---|---|
| `ads.py` | `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\ads.py` | Full rewrite |
| `ads_new.html` | `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\ads_new.html` | New file created |

**Old file preserved (not deleted):**  
`C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\ads.html` — original Tailwind template, untouched.

---

## Features Delivered

### Metrics Bar (7 cards)
- Total Ads (with active/paused breakdown)
- Clicks
- Cost
- Conversions
- CTR (colour-coded)
- CPA (colour-coded)
- Ad Strength summary (Good/Excellent count, Poor count warning in red)

### Filters
- Date: Last 7 / 30 / 90 Days
- Status: All / Enabled / Paused
- Per-page: 10 / 25 / 50 / 100

### Table Columns
- Ad (final_url truncated)
- Campaign
- Ad Group
- Status badge (ENABLED=green, PAUSED=grey, REMOVED=red)
- Type (RSA/ETA/RDA short labels)
- Ad Strength (progress bar — Poor=red, Average=yellow, Good=green, Excellent=blue, NULL=grey N/A badge)
- Impressions
- Clicks
- CTR (colour-coded)
- Cost
- Conversions
- CPA (colour-coded)

### Expandable Asset Rows
- Click any row → detail row expands below
- Shows: Ad Type badge, Headlines count (colour-coded vs 15 max), Descriptions count (colour-coded vs 4 max), Final URL with external link
- Chevron icon flips right→down on expand
- Vanilla JS only — zero jQuery

### Pagination
- Previous / Next buttons
- Page number links (if ≤7 pages) or Page X/Y display
- "Showing X–Y of Z ads" count

### Rules Integration
- Rules tab: full 12-rule table with Rule ID, Name, Description, Conditions, Risk, Status
- Rules sidebar: floating panel activated by RULES button
- Rules card: Active Optimization Rules summary below main content
- Rules count badge on tab button

---

## Critical Discovery — Database Architecture

### ⚠️ IMPORTANT FOR ALL FUTURE WORKERS

**Two separate DuckDB databases exist:**

| Catalog | File | Tables |
|---|---|---|
| `ro.analytics.*` | `warehouse_readonly.duckdb` | campaign_daily, keyword_daily, ad_group_daily, etc. |
| `analytics.*` | `warehouse.duckdb` | Everything above PLUS `ad_features_daily` |

**`analytics.ad_features_daily` does NOT exist in the readonly catalog.**  
It only exists in `warehouse.duckdb` and must be queried as `analytics.ad_features_daily` — NOT `ro.analytics.ad_features_daily`.

This caused the initial data failure. DuckDB's own error message confirmed it:  
`"Did you mean analytics.ad_features_daily?"`

**Rule going forward:** Any new table created in `warehouse.duckdb` must be verified against both catalogs before assuming `ro.` prefix will work.

---

## Column Mapping — analytics.ad_features_daily

This table is **pre-aggregated** — one row per ad per snapshot date. No GROUP BY needed.

| Column Name | Type | Notes |
|---|---|---|
| `customer_id` | VARCHAR | PK |
| `snapshot_date` | DATE | PK — use MAX() to get latest |
| `ad_id` | BIGINT | PK |
| `campaign_id` | BIGINT | |
| `campaign_name` | VARCHAR | |
| `ad_group_id` | BIGINT | |
| `ad_group_name` | VARCHAR | |
| `ad_type` | VARCHAR | RSA, ETA, RDA etc. |
| `ad_status` | VARCHAR | ENABLED, PAUSED, REMOVED — NOT `status` |
| `ad_strength` | VARCHAR | POOR, AVERAGE, GOOD, EXCELLENT — nullable |
| `headlines` | VARCHAR[] | Array — use `array_length(headlines)` for count |
| `descriptions` | VARCHAR[] | Array — use `array_length(descriptions)` for count |
| `final_url` | VARCHAR | |
| `impressions_7d` | BIGINT | |
| `clicks_7d` | BIGINT | |
| `cost_micros_7d` | BIGINT | Divide by 1,000,000 for $ |
| `conversions_7d` | DOUBLE | |
| `impressions_30d` | BIGINT | |
| `clicks_30d` | BIGINT | |
| `cost_micros_30d` | BIGINT | |
| `conversions_30d` | DOUBLE | |
| `impressions_90d` | BIGINT | |
| `clicks_90d` | BIGINT | |
| `cost_micros_90d` | BIGINT | |
| `conversions_90d` | DOUBLE | |
| `ctr_7d` / `ctr_30d` | DOUBLE | Pre-calculated — no ctr_90d column |
| `cpa_7d` / `cpa_30d` | BIGINT | Pre-calculated — no cpa_90d column |

**Query pattern used in ads.py:**
```sql
SELECT ... impressions_{suffix} AS impressions ...
FROM analytics.ad_features_daily
WHERE customer_id = ?
  AND snapshot_date = (
      SELECT MAX(snapshot_date)
      FROM analytics.ad_features_daily
      WHERE customer_id = ?
  )
ORDER BY cost_micros_{suffix} DESC NULLS LAST
```

---

## Issues Found and Fixed

### Issue 1 — Wrong Table Name
- **Error:** `ro.analytics.ad_daily does not exist`
- **Root cause:** Table was named `ad_features_daily` not `ad_daily`, and only exists in `warehouse.duckdb` not the readonly catalog
- **Fix:** Changed table reference to `analytics.ad_features_daily`

### Issue 2 — Wrong Column Names
- **Error:** `Referenced column "status" not found. Candidate: ad_status`
- **Root cause:** Column is `ad_status` not `status`; `headlines_count`/`descriptions_count` don't exist — actual columns are `headlines` and `descriptions` as VARCHAR arrays
- **Fix:** Used `ad_status`, `array_length(headlines)`, `array_length(descriptions)`

### Issue 3 — Wrong Query Pattern
- **Error:** Used GROUP BY + SUM pattern (like campaign_daily)
- **Root cause:** `ad_features_daily` is pre-aggregated — one row per ad per snapshot. No aggregation needed.
- **Fix:** Rewrote query to fetch latest snapshot with windowed column selection

### Issue 4 — Rules Tab Blank
- **Error:** Rules tab activated but showed no content
- **Root cause:** `rules_tab.html` already wraps itself in `<div class="tab-pane fade" id="rules-tab">`. Wrapping the include in another identical div caused double-wrapping — Bootstrap managed the outer div, inner content stayed faded/hidden
- **Fix:** Moved `{% include 'components/rules_tab.html' %}` outside the `.tab-content` div as a direct sibling, letting the component's own div be Bootstrap's target

### Issue 5 — CTR/CPA Card Width
- **Error:** CTR and CPA metric cards used `col-md-1` — too narrow, content stacked vertically
- **Fix:** Changed to `col` (Bootstrap auto equal-width distribution)

---

## Test Results — All 10 Criteria Passed

| # | Criterion | Result |
|---|---|---|
| 1 | Page loads — no 500 error | ✅ |
| 2 | 7 metrics cards with real data | ✅ 983 ads, 98,762 clicks, $295,933, 4,039 conv, 4.82% CTR, $73.26 CPA |
| 3 | Table renders with ad rows | ✅ 25 rows/page, 40 pages |
| 4 | Ad Strength progress bars | ✅ All strength levels render correctly |
| 5 | Row expand — asset detail | ✅ Chevron toggles, detail row shows |
| 6 | CTR/CPA card widths | ✅ Equal width, no stacking |
| 7 | Rules tab content | ✅ 12 rules displaying |
| 8 | Date filter 7d/30d/90d | ✅ Data updates |
| 9 | Status filter All/Enabled/Paused | ✅ Rows filter correctly |
| 10 | Per-page + pagination | ✅ All options work |

---

## Known Carry-Forwards to Chat 21h (Polish)

| Item | Description |
|---|---|
| `favicon.ico` 500 error | Pre-existing across all pages — no 404.html template exists. Not introduced by Chat 21f. |
| `rule_helpers` warning | `Unknown page_type 'ad_group'` — pre-existing from Chat 21e |
| Config YAML validation errors | Pre-existing — missing fields in client_001.yaml etc. |
| Rules card blank gap | `rules_card.html` renders below the tab content area causing a large blank gap on the Ads tab when viewing the Ads pane. Cosmetic only. Fix in Chat 21h. |
| CPA thresholds hardcoded | <$25=green, ≤$50=yellow, >$50=red — hardcoded in template. Could be made configurable per client in Chat 21h. |

---

## Next Step

**Chat 21g — Shopping View redesign** is next in the Chat 21 sequence.

After 21g, **Chat 21h — Final Polish** will address carry-forward items above across all pages.
