# Chat 24 — Handoff Document
## Dashboard 3.0 — Module 3 (M3): Chart Overhaul

**Date:** 2026-02-20
**Chat:** 24
**Module:** M3 — Chart Overhaul
**Status:** COMPLETE ✅

---

## What Was Delivered

A reusable `performance_chart.html` Jinja2 macro deployed to all 6 dashboard pages. Each page now shows a dual-axis Chart.js line chart below the M2 metrics cards, with 4 toggleable metrics and session-persistent state.

---

## Current Codebase State

### Active Template Files Per Page
| Page | Route File | Template File |
|------|-----------|---------------|
| Dashboard | `routes/dashboard.py` | `templates/dashboard_new.html` |
| Campaigns | `routes/campaigns.py` | `templates/campaigns.html` |
| Ad Groups | `routes/ad_groups.py` | `templates/ad_groups.html` |
| Keywords | `routes/keywords.py` | `templates/keywords_new.html` |
| Ads | `routes/ads.py` | `templates/ads_new.html` |
| Shopping | `routes/shopping.py` | `templates/shopping_new.html` |

### Key Shared Components
| File | Purpose |
|------|---------|
| `templates/macros/performance_chart.html` | M3 chart macro |
| `templates/macros/metrics_cards.html` | M2 metrics cards macro |
| `routes/shared.py` | `get_chart_metrics()`, `get_metrics_collapsed()`, `get_date_range_from_session()` |

---

## How To Add M3 Chart To A New Page

If a new page is added in future, follow this exact pattern:

**Step 1 — shared.py import:**
```python
from act_dashboard.routes.shared import (..., get_chart_metrics)
```

**Step 2 — Add builder function BEFORE the @bp.route decorator:**
```python
def _build_<page>_chart_data(conn, customer_id, active_days, date_from=None, date_to=None) -> dict:
    # Copy pattern from any existing builder
    # Use ro.analytics.campaign_daily for account-level pages
    # Use page-specific table for campaign/ad-group level pages
```

**Step 3 — Call before conn.close():**
```python
chart_data = _build_<page>_chart_data(conn, config.customer_id, active_days, date_from, date_to)
conn.close()
```

**Step 4 — Add to render_template:**
```python
chart_data=chart_data,
active_metrics=get_chart_metrics('<page_id>'),
```

**Step 5 — Template macro import (line 2-3 of template):**
```jinja
{% from "macros/performance_chart.html" import performance_chart %}
```

**Step 6 — Template macro call (after M2 metrics section):**
```jinja
{{ performance_chart(chart_data, active_metrics, '<page_id>') }}
```

---

## Critical Rules For Future Development

### ⚠️ Route Decorator Placement
Helper functions MUST be placed BEFORE `@bp.route` decorators, never between the decorator and the function definition.

**CORRECT:**
```python
def _build_chart_data(...):  # helper
    ...

@bp.route("/page")           # decorator immediately before function
@login_required
def page():
    ...
```

**WRONG — BREAKS FLASK SILENTLY:**
```python
@bp.route("/page")
def _build_chart_data(...):  # Flask registers this as the route handler!
    ...
@login_required
def page():
    ...
```

### Database Prefix Rules
- Dashboard page: uses `analytics.campaign_daily` (no `ro.` prefix) — matches existing dashboard.py pattern
- All other pages: use `ro.analytics.*` prefix

### Variable Name Differences
| Route File | Date Filter Variables |
|-----------|----------------------|
| `dashboard.py` | `date_filter`, `prev_filter` (string SQL fragments) |
| `campaigns.py` | `date_filter`, `prev_filter` |
| `ad_groups.py` | `_date_filter`, `_prev_filter` |
| `keywords.py` | `active_days`, `date_from`, `date_to` (session values) |
| `ads.py` | `active_days`, `date_from`, `date_to` |
| `shopping.py` | `active_days`, `date_from`, `date_to` |

---

## Next Steps — Dashboard 3.0 Remaining Modules

| Module | Description | Priority |
|--------|-------------|----------|
| M4 | Table improvements | Next |
| M5 | Rules upgrades | After M4 |
| M6 | Action buttons | After M5 |

### Starting Next Chat (M4)
Mandatory uploads:
1. Codebase ZIP: `C:\Users\User\Desktop\gads-data-layer`
2. `docs\PROJECT_ROADMAP.md`
3. `docs\CHAT_WORKING_RULES.md`

---

## Git Commit Reference

```
Chat 24 M3: Chart overhaul complete - performance_chart macro deployed to all 6 pages (Dashboard, Campaigns, Ad Groups, Keywords, Ads, Shopping)
```

