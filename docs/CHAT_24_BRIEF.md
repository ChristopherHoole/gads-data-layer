# CHAT_24_BRIEF.md
## Dashboard 3.0 — Module 3 (M3): Chart Overhaul

**Chat:** 24  
**Module:** M3 — Chart Overhaul  
**Status:** READY TO START  
**Created:** 2026-02-20  
**Wireframe:** `C:\Users\User\Desktop\gads-data-layer\docs\M3_WIREFRAME.html`

---

## 1. OBJECTIVE

Add an interactive performance chart to all 6 dashboard pages. The chart has 4 selectable metric slots above it. Clicking a slot toggles its line on/off. Selection persists per page in Flask session.

Replaces the existing static Performance Trend chart on the Dashboard page. All other pages get a new chart section between M2 (metrics cards) and the data table.

---

## 2. ALL DECISIONS — LOCKED

No design questions needed. Everything below is confirmed.

### Metrics (same on all 6 pages)
| Slot | Metric | Axis | Colour |
|------|--------|------|--------|
| 1 | Cost | Y1 · Left ($) | #dc3545 (red) |
| 2 | Impressions | Y2 · Right (count) | #0d6efd (blue) |
| 3 | Clicks | Y2 · Right (count) | #198754 (green) |
| 4 | Avg CPC | Y1 · Left ($) | #fd7e14 (orange) |

### Dual-axis logic
- Y1 (left, $): Cost + Avg CPC
- Y2 (right, count): Impressions + Clicks
- Each axis hides automatically when all its metrics are inactive
- Both axes visible when at least one metric from each is active

### Toggle behaviour
- Google Ads style: click slot to activate/deactivate
- All 4 can be active simultaneously
- 0 active = empty state message ("Select a metric above to show chart")
- Default on first load: Cost + Clicks active

### Chart style
- Chart.js line chart, all lines, no bars
- No point markers (`pointRadius: 0`)
- Slight tension (`tension: 0.3`)
- Y2 grid lines suppressed (`drawOnChartArea: false`) to avoid clutter
- Axis title labels: left = "$ · Cost / Avg CPC", right = "Count · Impr / Clicks"

### Session persistence
- Selected metrics saved per page via Flask session
- Key pattern: `chart_metrics_<page_id>` (e.g. `chart_metrics_campaigns`)
- Toggle fires POST `/set-chart-metrics` in background — no page reload
- Chart updates client-side via Chart.js dataset show/hide

### Slot card design
- Each slot shows: label, aggregated total for period, change % vs prev period (or `—` for windowed pages)
- Active slot: coloured border + light coloured background + coloured dot top-right
- Inactive slot: opacity 0.5
- Axis badge bottom-right of each slot: `Y1·$` (red bg) or `Y2·count` (blue bg)

---

## 3. PAGE-BY-PAGE SPEC

| Page | Data source | Date range | Change % | Notes |
|------|-------------|------------|----------|-------|
| Dashboard | campaign_daily (all summed) | Session range | ✅ vs prev period | Replaces existing Performance Trend chart |
| Campaigns | campaign_daily (all summed) | Session range | ✅ vs prev period | ✅ Pilot page — build here first |
| Ad Groups | ad_group_daily (all summed) | Session range | ✅ vs prev period | Same macro |
| Keywords | keyword_features_daily | 30d window | `—` | Windowed data only |
| Ads | ad-level daily data | 30d window | `—` | Windowed data only |
| Shopping | shopping_campaign_daily (synthetic) | Session range | ✅ vs prev period | Synthetic until account activated |

---

## 4. DATA STRUCTURE

### chart_data dict (built in each route)
```python
{
    'dates': ['2026-01-21', '2026-01-22', ...],   # list of date strings
    'cost': {
        'values': [1200.5, 1350.2, ...],           # daily values
        'total': 199900.0,                          # period total (for slot display)
        'change_pct': -1.5,                         # vs prev period (None if windowed)
        'axis': 'y1'
    },
    'impressions': {
        'values': [84000, 91000, ...],
        'total': 8330000,
        'change_pct': -1.5,
        'axis': 'y2'
    },
    'clicks': {
        'values': [...],
        'total': 249000,
        'change_pct': -1.5,
        'axis': 'y2'
    },
    'avg_cpc': {
        'values': [0.78, 0.82, ...],
        'total': 0.80,                              # average, not sum
        'change_pct': 0.0,
        'axis': 'y1'
    }
}
```

### active_metrics list (from session)
```python
['cost', 'clicks']   # default
# possible values: 'cost', 'impressions', 'clicks', 'avg_cpc'
```

---

## 5. MACRO SIGNATURE

**File:** `act_dashboard/templates/macros/performance_chart.html`

```jinja
{% from "macros/performance_chart.html" import performance_chart %}
{{ performance_chart(chart_data, active_metrics, page_id) }}
```

The macro renders:
1. Row of 4 slot cards (with axis badges, values, change %)
2. Chart.js canvas with dual-axis config
3. Empty state div (shown when 0 metrics active)
4. Inline JavaScript for toggle logic + POST to `/set-chart-metrics`

---

## 6. NEW ROUTE

Add to `act_dashboard/routes/shared.py`:

```python
POST /set-chart-metrics
Body: { page_id: 'campaigns', metrics: ['cost', 'clicks'] }
Response: { status: 'ok' }

get_chart_metrics(page_id) -> list   # returns active metrics from session
set_chart_metrics(page_id, metrics)  # saves to session
```

---

## 7. FILES TO CREATE / MODIFY

| File | Action |
|------|--------|
| `act_dashboard/templates/macros/performance_chart.html` | **CREATE** — new macro |
| `act_dashboard/routes/shared.py` | **MODIFY** — add helpers + POST route |
| `act_dashboard/routes/campaigns.py` | **MODIFY** — add chart_data builder (pilot) |
| `act_dashboard/templates/campaigns.html` | **MODIFY** — replace existing chart, add macro call |
| `act_dashboard/routes/dashboard.py` | **MODIFY** — add chart_data builder |
| `act_dashboard/templates/dashboard_new.html` | **MODIFY** — replace existing Performance Trend chart with macro |
| `act_dashboard/routes/ad_groups.py` | **MODIFY** — add chart_data builder |
| `act_dashboard/templates/ad_groups.html` | **MODIFY** — add macro call |
| `act_dashboard/routes/keywords.py` | **MODIFY** — add chart_data builder (windowed) |
| `act_dashboard/templates/keywords_new.html` | **MODIFY** — add macro call |
| `act_dashboard/routes/ads.py` | **MODIFY** — add chart_data builder (windowed) |
| `act_dashboard/templates/ads_new.html` | **MODIFY** — add macro call |
| `act_dashboard/routes/shopping.py` | **MODIFY** — add chart_data builder (synthetic) |
| `act_dashboard/templates/shopping_new.html` | **MODIFY** — add macro call (Campaigns tab only) |
| `tools/testing/generate_synthetic_data_v2.py` | **VERIFY** — confirm daily data exists for all pages |

**Total: 15 files**

---

## 8. WORKFLOW

Follow the standard 3-phase pattern used in M1 and M2:

**Phase 1 — Pilot (Campaigns)**
1. Upload codebase ZIP + PROJECT_ROADMAP.md + CHAT_WORKING_RULES.md
2. Send 5 questions to Master Chat, wait for answers
3. Send build plan to Master Chat, wait for approval
4. Build macro + shared.py route
5. Build Campaigns route + template
6. Test on Campaigns page — confirm both axes work, toggle works, session persists
7. Report pilot complete to Master Chat

**Phase 2 — Rollout (remaining 5 pages)**
8. Build remaining 5 routes + templates one at a time
9. Test each page after modification
10. Shopping: Campaigns tab only (Products tab has no time-series chart)

**Phase 3 — Wrap up**
11. Full regression test — all 6 pages
12. Create CHAT_24_DETAILED_SUMMARY.md
13. Create CHAT_24_HANDOFF.md
14. Report to Master Chat for git commit approval

---

## 9. KNOWN COMPLEXITY POINTS

1. **avg_cpc is an average not a sum** — daily values = cost/clicks per day. Slot total = period average (total_cost / total_clicks). Don't SUM the daily avg_cpc values.

2. **Shopping — Campaigns tab only** — the Products tab has no daily time-series. Only inject `chart_data` into the Campaigns tab section of `shopping_new.html`.

3. **Dashboard replacement** — the existing Performance Trend chart in `dashboard_new.html` has its own Chart.js instance and 7d/30d/90d tab buttons. The M3 macro replaces this entire block. The date range is now controlled globally by M1 session date picker, so the 7d/30d/90d tabs are no longer needed.

4. **Windowed pages (Keywords + Ads)** — no prev-period comparison available. Set `change_pct: None` for all 4 metrics. Macro renders `—` for change indicator. Daily values still render on chart.

5. **Toggle is client-side only** — chart shows/hides datasets without page reload. The POST to `/set-chart-metrics` saves state to session for persistence on next load. If POST fails, chart still works — session just won't persist.

---

## 10. SUCCESS CRITERIA

- [ ] Macro renders correctly on all 6 pages
- [ ] Dual Y-axis: Y1 left ($), Y2 right (count)
- [ ] Each axis hides when all its metrics are inactive
- [ ] Toggle works (click to activate/deactivate)
- [ ] 0 active = empty state message shown
- [ ] Default selection (Cost + Clicks) on first load
- [ ] Session persists selection across page refreshes
- [ ] Slot values show correct period totals
- [ ] Change % shows correctly (or `—` for windowed pages)
- [ ] Axis badges visible on each slot (Y1·$ or Y2·count)
- [ ] Dashboard old chart fully replaced, no regression
- [ ] Shopping: chart only on Campaigns tab, not Products
- [ ] No console errors on any page

---

**Wireframe reference:** `C:\Users\User\Desktop\gads-data-layer\docs\M3_WIREFRAME.html`  
**Prior module handoff:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_23M2_HANDOFF.md`
