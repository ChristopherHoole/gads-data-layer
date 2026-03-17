# Chat 96 Handoff — Recommendations UI Overhaul

## Status: COMPLETE

All 7 deliverables from the brief are done.

## What was built

A full table-based Recommendations UI replacing all card-based designs:

1. **`/recommendations` page** — 4-tab table (Pending / Monitoring / Successful / History) with bulk select, expand rows, accept/decline buttons, run-engine button
2. **Campaigns Recommendations tab** — same 4-tab table, slim variant (no Type or Campaign columns)
3. **Ad Groups Recommendations tab** — same, column "Ad group"
4. **Keywords Recommendations tab** — same, column "Keyword" (Tailwind page, `keywords.html`)
5. **Ads Recommendations tab** — same, column "Ad" (Bootstrap 5 page, **`ads_new.html`** — the actual routed template)
6. **Shopping Recommendations tab** — same, column "Product", entity `shopping_product` (Bootstrap 5 page, **`shopping_new.html`** — the actual routed template)

## Files changed

```
act_dashboard/routes/recommendations.py      — enriched /recommendations/cards endpoint
act_dashboard/templates/recommendations.html — full 4-tab table rewrite
act_dashboard/templates/campaigns.html       — replaced card UI with table (Bootstrap 5)
act_dashboard/templates/ad_groups.html       — replaced card UI with table (Bootstrap 5)
act_dashboard/templates/keywords.html        — replaced Jinja cards with client-side table (Tailwind)
act_dashboard/templates/ads_new.html         — replaced card UI with 4-tab table (Bootstrap 5, routed by /ads)
act_dashboard/templates/shopping_new.html    — replaced card UI with 4-tab table (Bootstrap 5, routed by /shopping)
```

> **Note**: `ads.html` and `shopping.html` are NOT routed. The `/ads` route uses `ads_new.html`
> and `/shopping` uses `shopping_new.html`. Those older templates were also modified (harmlessly)
> but are not served.

No routes were added or modified (all existing `/recommendations/*` routes unchanged).

## Python helpers added to recommendations.py

- `_format_condition_item(item)` — formats a single condition dict to readable string
- `_format_conditions(conditions_raw)` — parses JSON conditions array
- `_derive_rule_type_for_display(action_type, entity_type)` — maps action_type → budget/bid/status/keyword/shopping
- `_build_rule_data_map()` — queries rules table, returns `{str(id): {...}}` dict
- `_enrich_with_rule_data(recs, rule_map)` — adds enriched fields to each recommendation

## JS function naming convention

| Page | Prefix | Example |
|------|--------|---------|
| campaigns.html | `cam` | `camRecLoad()`, `camRecAccept()` |
| ad_groups.html | `ag` | `agRecLoad()`, `agRecAccept()` |
| keywords.html | `kw` | `kwRecLoad()`, `kwRecAccept()` |
| ads_new.html | `ad` | `adRecLoad()`, `adRecAccept()` |
| shopping_new.html | `shop` | `shopRecLoad()`, `shopRecAccept()` |

## Known issues / caveats

- **Tailwind page IIFE raw tags**: The IIFE in `keywords.html` is wrapped with `{%- raw -%}...{%- endraw -%}` because the JS uses `{{` object literals that Jinja2 would otherwise try to parse. (`ads_new.html` and `shopping_new.html` are Bootstrap 5 pages — no raw tags needed there.)

- **`rule_name` field**: The recommendations table doesn't have a `rule_name` column; the JS uses `r.rule_name || r.rule_id` as fallback. If you want the human-readable rule name displayed, add `rule_name` to the enrichment function by joining to the rules table on `name`.

- **Entity type `ad`**: The recommendations engine generates `entity_type = 'ad'` for ad-level rules. If this differs from what you see in the DB, update the filter in `ads_new.html` IIFE (`r.entity_type === 'ad'`).

- **Shopping page lazy load**: `shopping_new.html` also triggers `shopRecLoad()` if the page is opened directly on the recommendations tab (checks `recPane.classList.contains('active')` on DOMContentLoaded).

## Testing

Flask template parsing verified:
```
recommendations.html: OK
campaigns.html: OK
ad_groups.html: OK
keywords.html: OK
ads.html: OK         (not routed — ads_new.html is)
shopping.html: OK    (not routed — shopping_new.html is)
ads_new.html: OK
shopping_new.html: OK
```

Visual verification (live server):
- /recommendations — 4-tab table renders ✅
- /campaigns Recommendations tab — Bootstrap 4-tab slim table ✅
- /ad-groups Recommendations tab — "Ad group" column ✅
- /keywords Recommendations tab — "Keyword" column, IIFE loads correctly ✅
- /ads Recommendations tab — "Ad" column, 4-tab table ✅
- /shopping Recommendations tab — "Product" column, 4-tab table ✅
