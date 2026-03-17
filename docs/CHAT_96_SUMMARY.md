# Chat 96 Summary — Recommendations UI Overhaul

## What was done

Full replacement of all card-based recommendation UIs with table-based designs across the entire app.

### Files modified

| File | Change |
|------|--------|
| `act_dashboard/routes/recommendations.py` | Enriched `/recommendations/cards` endpoint with `plain_english`, `rule_or_flag`, `rule_type_display`, `conditions`, `risk_level`, `cooldown_days`, `completed_at` |
| `act_dashboard/templates/recommendations.html` | Full rewrite — 4-tab Bootstrap table (Pending / Monitoring / Successful / History) |
| `act_dashboard/templates/campaigns.html` | Replaced card UI with Bootstrap 5 4-tab slim table; added `recommendations.css` |
| `act_dashboard/templates/ad_groups.html` | Same as campaigns; column header "Ad group"; `ag-` prefix |
| `act_dashboard/templates/keywords.html` | Replaced Jinja server-rendered cards with client-side 4-tab table; Tailwind page |
| `act_dashboard/templates/ads.html` | Same pattern; column header "Ad"; Tailwind page |
| `act_dashboard/templates/shopping.html` | Same pattern; column header "Product"; entity type `shopping_product`; Tailwind page |
| `act_dashboard/static/css/recommendations.css` | Existing — unchanged |

### New file

`act_dashboard/static/css/recommendations.css` — created in an earlier chat (Chat 96 Job 3 per file header), contains all `rec-` prefixed classes used by the new tables.

## Architecture decisions

**Bootstrap pages** (campaigns, ad_groups): Use Bootstrap 5 `nav-tabs`, `table table-sm table-hover align-middle rec-tab-slim`, Bootstrap badge/button classes.

**Tailwind pages** (keywords, ads, shopping): Inline `<link>` to `recommendations.css`, plain HTML tables with `rec-` classes only. `showTab()` patched via wrapper function to lazy-load data. IIFE wrapped in `{%- raw -%}...{%- endraw -%}` to prevent Jinja2 parsing of JavaScript `{{` object literals.

**Data loading**: All entity-page tabs call `/recommendations/cards` and filter client-side by `entity_type`. No server routes changed.

**History tab**: Merges `declined` + `reverted` arrays client-side, sorted by most-recent date.

**IIFE pattern**: All entity-page JS is scoped in `(function(){...})();` with window-exposed functions (`window.xxRecLoad`, `window.xxRecAccept`, etc.).

## Entity type strings

| Page | `entity_type` value |
|------|---------------------|
| campaigns.html | `campaign` |
| ad_groups.html | `ad_group` |
| keywords.html | `keyword` |
| ads.html | `ad` |
| shopping.html | `shopping_product` |

## Key constraints followed

- No changes to `recommendation_accept`, `recommendation_decline`, `recommendations_run` routes
- All badge/action/risk/condition styles use `rec-` CSS classes (no inline styles for those elements)
- Bootstrap 5 only; Vanilla JS only (no jQuery)
- No `{{ }}` Jinja braces inside `<script>` tags in Tailwind pages (IIFE wrapped in raw tags)
