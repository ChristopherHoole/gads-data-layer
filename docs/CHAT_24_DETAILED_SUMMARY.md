# Chat 24 — Detailed Summary
## Dashboard 3.0 — Module 3 (M3): Chart Overhaul

**Date:** 2026-02-20
**Status:** COMPLETE ✅
**All 6 pages validated**

---

## Objective

Replace all legacy per-page chart implementations with a single reusable `performance_chart.html` Jinja2 macro, deployed consistently across all 6 dashboard pages.

---

## Architecture Decisions

### Shared Macro Pattern
- Single macro file: `act_dashboard/templates/macros/performance_chart.html`
- Imported at the top of each template: `{% from "macros/performance_chart.html" import performance_chart %}`
- Called with 3 args: `{{ performance_chart(chart_data, active_metrics, 'page_id') }}`

### Chart Specification
| Metric | Colour | Axis | Default Active |
|--------|--------|------|----------------|
| Cost | Red | Y1 ($ left) | ✅ |
| Impressions | Blue | Y2 (count right) | ❌ |
| Clicks | Green | Y2 (count right) | ✅ |
| Avg CPC | Orange | Y1 ($ left) | ❌ |

### Session Persistence
- Toggle state stored in Flask session as `chart_metrics_<page_id>`
- `get_chart_metrics(page_id)` helper in `shared.py` reads session, returns list of active metric keys
- `POST /set-chart-metrics` endpoint handles toggle updates (built in earlier step)

### Data Sources Per Page
| Page | Table | Comparison Period |
|------|-------|-------------------|
| Campaigns | `ro.analytics.campaign_daily` (per-campaign) | ✅ vs previous period |
| Dashboard | `analytics.campaign_daily` (account totals) | ✅ vs previous period |
| Ad Groups | `ro.analytics.ad_group_daily` | ✅ vs previous period |
| Keywords | `ro.analytics.campaign_daily` (account-level) | ✅ vs previous period |
| Ads | `ro.analytics.campaign_daily` (account-level) | ✅ vs previous period |
| Shopping | `ro.analytics.campaign_daily` (account-level) | ✅ vs previous period |

Note: Keywords/Ads/Shopping use account-level campaign_daily as a proxy (no keyword/ad/product daily table with consistent date ranges available).

---

## Files Modified

### New Files
| File | Description |
|------|-------------|
| `act_dashboard/templates/macros/performance_chart.html` | Reusable chart macro (built in earlier chat step) |

### Modified Files
| File | Changes |
|------|---------|
| `act_dashboard/routes/shared.py` | Added `get_chart_metrics(page_id)` helper |
| `act_dashboard/routes/campaigns.py` | Added `_build_campaign_chart_data()`, wired to render_template |
| `act_dashboard/routes/dashboard.py` | Added `_build_dashboard_chart_data()`, wired to render_template, removed legacy trend_data |
| `act_dashboard/routes/ad_groups.py` | Added `_build_ag_chart_data()`, wired to render_template |
| `act_dashboard/routes/keywords.py` | Added `_build_kw_chart_data()`, wired to render_template |
| `act_dashboard/routes/ads.py` | Added `_build_ads_chart_data()`, wired to render_template |
| `act_dashboard/routes/shopping.py` | Added `_build_shopping_chart_data()`, wired to render_template |
| `act_dashboard/templates/dashboard_new.html` | Macro import + call, removed legacy chart block |
| `act_dashboard/templates/ad_groups.html` | Macro import + call after M2 metrics |
| `act_dashboard/templates/keywords_new.html` | Macro import + call after M2 metrics |
| `act_dashboard/templates/ads_new.html` | Macro import + call after M2 metrics |
| `act_dashboard/templates/shopping_new.html` | Macro import + call after Campaigns tab M2 metrics |

---

## Chart Data Builder Pattern

All 6 routes follow the same pattern:

```python
def _build_<page>_chart_data(conn, customer_id, active_days, date_from=None, date_to=None) -> dict:
    # 1. Build date filter strings from session params
    # 2. Query daily rows (cost, impressions, clicks, avg_cpc per day)
    # 3. Query current period totals
    # 4. Query previous period totals
    # 5. Compute change_pct for each metric
    # 6. Return structured dict
```

Return structure:
```python
{
    'dates': ['2026-01-21', ...],
    'cost':        {'values': [...], 'total': float, 'change_pct': float, 'axis': 'y1'},
    'impressions': {'values': [...], 'total': float, 'change_pct': float, 'axis': 'y2'},
    'clicks':      {'values': [...], 'total': float, 'change_pct': float, 'axis': 'y2'},
    'avg_cpc':     {'values': [...], 'total': float, 'change_pct': float, 'axis': 'y1'},
}
```

---

## Debugging Issues Encountered

### Route Decorator Placement Bug (Step D)
**Symptom:** `TypeError: _build_dashboard_chart_data() missing 4 required positional arguments`
**Root cause:** `str_replace` inserted helper function BETWEEN `@bp.route("/")` decorator and `home()` definition. Flask registered the helper as the route handler instead of `home()`.
**Fix:** Helper function must always be placed BEFORE the `@bp.route` decorator block.
**Lesson:** Always verify decorator-function adjacency after any str_replace near route definitions.

---

## Validation Results

| Page | URL | Status | Chart Renders | Toggles Work |
|------|-----|--------|---------------|--------------|
| Dashboard | `/` | ✅ 200 | ✅ | ✅ |
| Campaigns | `/campaigns` | ✅ 200 | ✅ | ✅ |
| Ad Groups | `/ad-groups` | ✅ 200 | ✅ | ✅ |
| Keywords | `/keywords` | ✅ 200 | ✅ | ✅ |
| Ads | `/ads` | ✅ 200 | ✅ | ✅ |
| Shopping | `/shopping` | ✅ 200 | ✅ | ✅ |

---

## M3 Complete — Dashboard 3.0 Progress

| Module | Description | Status |
|--------|-------------|--------|
| M1 | Global date range picker (Flatpickr, session-based) | ✅ Complete (Chat 22) |
| M2 | Metrics cards (Bootstrap 5, sparklines, collapsible) | ✅ Complete (Chat 23) |
| M3 | Chart overhaul (reusable macro, all 6 pages) | ✅ Complete (Chat 24) |
| M4 | Table improvements | 🔲 Pending |
| M5 | Rules upgrades | 🔲 Pending |
| M6 | Action buttons | 🔲 Pending |

