# CHAT 23 BRIEF — M2: Metrics Cards

**Chat:** 23  
**Module:** M2 — Metrics Cards (Financial row + Actions row + Sparklines)  
**Part of:** Dashboard 3.0 Phase 1  
**Estimated Time:** 120–150 minutes  
**Pilot Page:** Campaigns (`/campaigns`)  
**Rollout Pages:** Dashboard, Ad Groups, Keywords, Ads, Shopping  
**Wireframe:** `docs/M2_WIREFRAME.html` (included in this commit)

---

## MANDATORY FIRST STEPS

Before doing anything else, request these 3 uploads from Christopher:

1. **Codebase ZIP:** `C:\Users\User\Desktop\gads-data-layer`
2. **PROJECT_ROADMAP.md:** `C:\Users\User\Desktop\gads-data-layer\docs\PROJECT_ROADMAP.md`
3. **CHAT_WORKING_RULES.md:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_WORKING_RULES.md`

Do NOT proceed until all 3 are provided.

---

## MANDATORY 3-PHASE WORKFLOW — READ THIS BEFORE DOING ANYTHING

This chat follows a strict 3-phase workflow. Each phase requires explicit approval from Christopher before moving to the next. Do not skip phases. Do not combine phases.

---

### PHASE 1 — RULES CONFIRMATION + 5 QUESTIONS

**Step 1A: Post rules confirmation**

Before anything else, post this exact block:

```
CHAT WORKING RULES CONFIRMATION:
✅ Rule 1 (Codebase Upload): I have the ZIP and have explored the structure
✅ Rule 2 (File Handling): I will request the current version of ANY file before editing it — even if I just read it from the ZIP
✅ Rule 3 (Full Paths): I will use full Windows paths on every single file reference — no partial paths ever
✅ Rule 4 (One Step at a Time): I will complete and test each step fully before proceeding. I will wait for confirmation from Christopher
✅ Rule 5 (Show My Work): I will show analysis and proposed changes BEFORE making them
✅ Rule 6 (Debugging Protocol): I will add debug logging and request output before guessing at fixes
✅ Rule 7 (Error Handling): All code will include input validation, safe defaults, and try/except with specific errors
✅ Rule 8 (Testing Protocol): I will specify exact test steps and success criteria after every file change
✅ Rule 9 (Downloads Only): ALL files delivered as download links — no code in chat
✅ Rule 10 (Git Commits): I will suggest a commit message at the end for Master Chat approval
✅ Rule 11 (When to Stop): I will stop and escalate if hitting the same error 3+ times
✅ Rule 12 (Communication): Professional, honest, clear — I will admit mistakes immediately

M2-SPECIFIC:
✅ Pilot first: Campaigns page built and fully tested before touching any other page
✅ Schema first: IS metrics data gap fixed before touching any dashboard files
✅ One file at a time: complete file delivered as download with exact save path, Christopher confirms saved before next file
```

**Step 1B: Ask 5 questions**

After the confirmation block, ask Christopher exactly 5 questions about anything in this brief that is ambiguous or needs a decision before building. Do not ask about things already clearly specified in the brief.

Good question areas:
- Sparkline behaviour when selected period has very few days (e.g. 7d = only 7 data points)
- Default collapse state on first visit before any session value exists
- Behaviour when no previous period data exists to calculate change % (e.g. new account, show 0% or show —?)
- Wasted Spend sparkline: daily wasted spend or cumulative?
- Any schema uncertainty identified after reading the codebase

**Step 1C: Wait for Christopher's answers**

Do not proceed to Phase 2 until Christopher has answered all 5 questions and you have confirmed understanding.

---

### PHASE 2 — DETAILED BUILD PLAN APPROVAL

After Phase 1 is approved, create a detailed build plan. This must cover:
- Every file you will create or modify
- In the exact order you will work on them
- One line per file explaining exactly what you will do to it

Format:
```
DETAILED BUILD PLAN — CHAT 23 M2

Step 1: [Full Windows path to file] — [Exactly what you will do]
Step 2: [Full Windows path to file] — [Exactly what you will do]
...
Step N: TEST — [What you will test, how, and what passing looks like]

Total files: N
Total steps: N

Awaiting approval. Reply "Approved" to begin building.
```

**DO NOT WRITE A SINGLE LINE OF CODE until Christopher replies "Approved."**

---

### PHASE 3 — BUILD (ONE FILE AT A TIME)

After Phase 2 is approved, build in the exact order of the approved plan.

For every file:
1. Request the current version from Christopher before editing ("Please upload `C:\...\filename.py`")
2. Make all changes
3. Deliver the complete file as a download link with exact Windows save path
4. Specify test steps if the dashboard can be tested at this point
5. Wait for Christopher to confirm saved (and tested if applicable) before delivering the next file

**Never deliver more than one file at a time.**  
**Never put code in chat — downloads only.**  
**Never proceed to the next file without confirmation from Christopher.**

---

## CONTEXT

Dashboard 3.0 Phase 1. Chat 22 (M1) delivered the global date range picker across all 6 pages. This chat (M2) delivers the standardised metrics cards component.

**Current state:** Each page has its own ad-hoc metrics cards with inconsistent layout, no change indicators, no sparklines, and no collapsible Actions row. The Dashboard has 6 cards. Campaigns has 6 cards. Ad Groups has 7 cards. Keywords has a different layout entirely. None are built from a shared component.

**Target state:** All 6 pages use the same Jinja2 macro-based component with:
- Financial Metrics row (always visible) — 8 cards split into two groups of 4
- Actions Metrics row (collapsible) — 8 cards, same two-group split
- Change % indicators vs previous equivalent period on every card
- Inverted colour logic for cost metrics
- Sparkline mini-chart at bottom of each card
- Collapse state persists in session

---

## WIREFRAME REFERENCE

Open `C:\Users\User\Desktop\gads-data-layer\docs\M2_WIREFRAME.html` in a browser before building. It shows:

- Two-group layout (Financial | Leads) with vertical separator between card 4 and card 5
- Sub-labels "Financial" and "Leads" above each group
- Option A toggle: thin horizontal line with pill button centred on it (`▼ Actions Metrics`)
- Collapsed state: pill shows `▶ Actions Metrics`, chart follows immediately below
- All 6 page variants with exact metric sets
- Sparklines at bottom of each card (thin line, no axes)

---

## CONFIRMED METRIC SETS — ALL 6 PAGES

### Dashboard
- **Financial:** Cost | Revenue | ROAS | BLANK | Conversions | Cost per Conv | Conv Rate | BLANK
- **Actions:** Impressions | Clicks | Avg CPC | Avg CTR | Search Impr Share | Search Top IS | Search Abs Top IS | Click Share

### Campaigns (identical to Dashboard)
- **Financial:** Cost | Revenue | ROAS | BLANK | Conversions | Cost per Conv | Conv Rate | BLANK
- **Actions:** Impressions | Clicks | Avg CPC | Avg CTR | Search Impr Share | Search Top IS | Search Abs Top IS | Click Share

### Ad Groups (identical to Campaigns)
- **Financial:** Cost | Revenue | ROAS | BLANK | Conversions | Cost per Conv | Conv Rate | BLANK
- **Actions:** Impressions | Clicks | Avg CPC | Avg CTR | Search Impr Share | Search Top IS | Search Abs Top IS | Click Share

### Keywords
- **Financial:** Cost | Revenue | ROAS | Wasted Spend | Conversions | Cost per Conv | Conv Rate | BLANK
- **Actions:** Impressions | Clicks | Avg CPC | Avg CTR | Search Impr Share | Search Top IS | Search Abs Top IS | Click Share

### Ads
- **Financial:** Cost | Revenue | ROAS | BLANK | Conversions | Cost per Conv | Conv Rate | BLANK
- **Actions:** Impressions | Clicks | Avg CPC | Avg CTR | Ad Strength | BLANK | BLANK | BLANK

### Shopping
- **Financial:** Cost | Conv Value | ROAS | BLANK | Conversions | Cost per Conv | Conv Rate | BLANK
- **Actions:** Impressions | Clicks | Avg CPC | Avg CTR | BLANK | BLANK | BLANK | BLANK

---

## CRITICAL DATA GAP — MUST READ

### Search IS Metrics NOT in Database Schema

**Search Impr Share, Search Top IS, Search Abs Top IS, and Click Share do not exist in the warehouse.**

The synthetic data generator (`tools/testing/generate_synthetic_data_v2.py`) generates `search_impression_share` but never inserts it. Search Top IS, Search Abs Top IS, and Click Share don't exist in the generator at all. The `campaign_daily` and `ad_group_daily` schemas have no IS columns.

**You MUST fix this as Step 1 before any other work:**

1. Add 4 columns to `snap_campaign_daily` table in `warehouse_duckdb.py`:
   - `search_impression_share DOUBLE`
   - `search_top_impression_share DOUBLE`
   - `search_abs_top_impression_share DOUBLE`
   - `click_share DOUBLE`

2. Update `analytics.campaign_daily` view to expose these columns

3. Update `generate_synthetic_data_v2.py` to generate and insert all 4:
   - `search_impression_share`: already generated (0.6–0.9), just needs inserting
   - `search_top_impression_share`: ~60–75% of search_impression_share
   - `search_abs_top_impression_share`: ~40–55% of search_top_impression_share
   - `click_share`: random 0.15–0.40

4. Re-run the synthetic data generator after schema changes

5. For ad_groups: add same 4 columns to `ad_group_daily` in `v1_runner.py` and generate synthetic equivalents

**Do this before touching any dashboard files.**

### Revenue in Ad Groups

`conversions_value` IS in `ad_group_daily` schema — confirmed. Revenue and ROAS can be computed from it. No schema changes needed for ad_groups revenue/ROAS.

### Wasted Spend in Keywords

Already calculated in `keywords.py` (keywords with 0 conversions but cost > 0). Available as `wasted_spend` variable. No changes needed.

### Ad Strength in Ads

Already in `ads.py` as aggregate counts. Available as summary data. No changes needed.

---

## ARCHITECTURE

### Jinja2 Macros File (NEW)

Create: `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\macros\metrics_cards.html`

This file defines two macros:

**Macro 1: `metric_card(label, value, formatted_value, change_pct, sparkline_data, format_type, invert_colours=False)`**

Parameters:
- `label` — display label (e.g. "Cost")
- `formatted_value` — pre-formatted string (e.g. "$183,733")
- `change_pct` — float, e.g. -10.5 (negative = down)
- `sparkline_data` — list of floats, daily values for sparkline (e.g. [1200, 1350, 1180, ...])
- `format_type` — "currency", "number", "percent", "roas", "ratio", "text"
- `invert_colours` — True for Cost, Cost per Conv, Wasted Spend (↑ = red, ↓ = green)

Card renders:
- Label (top, small caps)
- Formatted value (large, bold)
- Change indicator: arrow + % (colour logic below)
- Sparkline (bottom, thin Chart.js line, no axes, no labels)

**Colour logic:**
- Default: change_pct > 0 → green (↑), change_pct < 0 → red (↓)
- Inverted (invert_colours=True): change_pct > 0 → red (↑), change_pct < 0 → green (↓)
- change_pct == 0 or None → grey neutral

**Macro 2: `metrics_section(financial_cards, actions_cards, page_id)`**

Parameters:
- `financial_cards` — list of card config dicts
- `actions_cards` — list of card config dicts
- `page_id` — string, used for session key (e.g. "campaigns")

Renders:
- "Financial" sub-label | 4 financial cards | vertical separator | "Leads" sub-label | 4 leads cards
- Option A pill toggle (`▼/▶ Actions Metrics`)
- Actions row (shown/hidden based on session state)
- Toggle JS: POSTs to `/set-metrics-collapse` then toggles visibility

### Blank Cards

Blank cards render as an empty styled placeholder (dashed border, no label, no value). Pass `None` in the card list to render a blank.

### Session — Collapse State

Add to `shared.py`:
- Route: `POST /set-metrics-collapse` — accepts `{"page_id": "campaigns", "collapsed": true/false}`, stores in `session['metrics_collapsed'][page_id]`
- Helper: `get_metrics_collapsed(page_id)` → returns bool, default False (expanded)

### Sparklines

Use Chart.js inline canvas inside each card. Each card gets a `<canvas>` element ~60px tall, full width of card.

Chart.js config for sparklines:
```javascript
{
  type: 'line',
  data: { labels: [...], datasets: [{ data: sparkline_data, borderColor: color, borderWidth: 1.5, pointRadius: 0, tension: 0.3 }] },
  options: {
    plugins: { legend: { display: false }, tooltip: { enabled: false } },
    scales: { x: { display: false }, y: { display: false } },
    animation: false,
    responsive: true,
    maintainAspectRatio: false
  }
}
```

Sparkline colour: match change direction (green line if positive period change, red if negative, grey if neutral).

**Sparkline data source:** Each route must return daily data arrays per metric alongside the aggregate totals. This is the main backend complexity of this chat.

---

## BACKEND CHANGES — ROUTES

Each route needs two queries:

**Query 1 (existing):** Aggregate totals for the selected period (already exists)

**Query 2 (new):** Daily breakdown for sparklines — one row per day, same date filter, returns daily values for each metric shown in cards

Example for Campaigns:
```sql
SELECT 
    snapshot_date,
    SUM(cost_micros) / 1000000.0 as daily_cost,
    SUM(conversions_value) as daily_revenue,
    SUM(impressions) as daily_impressions,
    SUM(clicks) as daily_clicks,
    SUM(conversions) as daily_conversions,
    AVG(search_impression_share) as daily_search_is,
    ...
FROM ro.analytics.campaign_daily
WHERE customer_id = ?
  AND [date_filter]
GROUP BY snapshot_date
ORDER BY snapshot_date ASC
```

**Query 3 (new):** Previous period totals for change % calculation — same structure as Query 1 but with the previous equivalent date window.

Previous period logic (already used in dashboard.py — reuse the same pattern):
- Preset 30d: previous 30d window before current period
- Custom range: equal-length window before date_from

Each route passes to template:
- `financial_cards` — list of card config dicts with value, change_pct, sparkline_data
- `actions_cards` — same
- `metrics_collapsed` — bool from session

---

## STEP-BY-STEP IMPLEMENTATION

### STEP 1: Schema + synthetic data (IS metrics)
- Update `warehouse_duckdb.py` — add 4 IS columns to schema and analytics view
- Update `generate_synthetic_data_v2.py` — generate + insert all 4 IS columns
- Update `v1_runner.py` — add 4 IS columns to `ad_group_daily`
- Re-run synthetic data generator
- **Test:** Verify IS columns exist and have data in database

### STEP 2: Create macros file
- Create `act_dashboard/templates/macros/metrics_cards.html`
- Implement `metric_card` macro with sparkline canvas
- Implement `metrics_section` macro with two-group layout + pill toggle
- **Test:** Not yet — needs route data first

### STEP 3: Add session route to shared.py
- Add `POST /set-metrics-collapse` route
- Add `get_metrics_collapsed(page_id)` helper
- **Test:** POST to route, verify session stores correctly

### STEP 4: Campaigns pilot — backend
- Request current `campaigns.py` from Christopher before editing
- Add Query 2 (daily sparkline data) and Query 3 (previous period) to route
- Build `financial_cards` and `actions_cards` lists
- Pass to template
- **Test:** Confirm data structure in template with `{{ financial_cards | tojson }}`

### STEP 5: Campaigns pilot — template
- Request current `campaigns.html` from Christopher before editing
- Remove existing metrics cards section
- Import macros: `{% from 'macros/metrics_cards.html' import metrics_section %}`
- Call `{{ metrics_section(financial_cards, actions_cards, 'campaigns') }}`
- **Test:** Full visual check — cards render, sparklines show, collapse works, change indicators correct

### STEPS 6–10: Rollout
Apply same pattern to each remaining page in order:

**Step 6:** Dashboard (`dashboard.py` + `dashboard_new.html`)  
**Step 7:** Ad Groups (`ad_groups.py` + `ad_groups.html`)  
**Step 8:** Keywords (`keywords.py` + `keywords_new.html`) — Wasted Spend in slot 4  
**Step 9:** Ads (`ads.py` + `ads_new.html`) — Ad Strength in Actions slot 5  
**Step 10:** Shopping (`shopping.py` + `shopping_new.html`) — Conv Value in slot 2, 4 BLANKs in Actions  

**Step 11:** Cross-page session test
- Collapse Actions on Campaigns → navigate to Keywords → confirm still collapsed
- Expand on Ad Groups → navigate to Ads → confirm still expanded

---

## COLOUR INVERSION — CONFIRMED LIST

These metrics use `invert_colours=True` (↑ = red/bad, ↓ = green/good):
- Cost
- Cost per Conv (CPA)
- Wasted Spend

All other metrics use default logic (↑ = green, ↓ = red).

---

## AD STRENGTH CARD — SPECIAL FORMAT

The Ad Strength card in Ads page uses a different display:
- Value: `240/983` (Good or Excellent count / Total)
- Sub-label below value: `Good/Excellent`
- Change indicator: % change in Good/Excellent count vs previous period
- Sparkline: daily Good/Excellent count trend
- format_type: `"ratio"` — use this to trigger special rendering in the macro

---

## FILES TO CREATE/MODIFY

| # | File | Action |
|---|---|---|
| 1 | `src/gads_pipeline/warehouse_duckdb.py` | Add 4 IS columns to schema + analytics view |
| 2 | `tools/testing/generate_synthetic_data_v2.py` | Generate + insert 4 IS columns |
| 3 | `src/gads_pipeline/v1_runner.py` | Add 4 IS columns to ad_group_daily |
| 4 | `act_dashboard/templates/macros/metrics_cards.html` | CREATE NEW — macro definitions |
| 5 | `act_dashboard/routes/shared.py` | Add collapse route + helper |
| 6 | `act_dashboard/routes/campaigns.py` | Add sparkline + prev period queries |
| 7 | `act_dashboard/templates/campaigns.html` | Replace cards with macro |
| 8 | `act_dashboard/routes/dashboard.py` | Add sparkline + prev period queries |
| 9 | `act_dashboard/templates/dashboard_new.html` | Replace cards with macro |
| 10 | `act_dashboard/routes/ad_groups.py` | Add sparkline + prev period queries |
| 11 | `act_dashboard/templates/ad_groups.html` | Replace cards with macro |
| 12 | `act_dashboard/routes/keywords.py` | Add sparkline + prev period queries |
| 13 | `act_dashboard/templates/keywords_new.html` | Replace cards with macro |
| 14 | `act_dashboard/routes/ads.py` | Add sparkline + prev period queries |
| 15 | `act_dashboard/templates/ads_new.html` | Replace cards with macro |
| 16 | `act_dashboard/routes/shopping.py` | Add sparkline + prev period queries |
| 17 | `act_dashboard/templates/shopping_new.html` | Replace cards with macro |

---

## KNOWN GOTCHAS

1. **Database prefix** — all SQL must use `ro.analytics.*` not `analytics.*`

2. **Keywords windowed columns** — Keywords uses pre-aggregated `_w7`/`_w30` columns for most metrics. For sparklines, you'll need to use `ro.analytics.keyword_features_daily` or fall back to raw `ro.analytics.keyword_daily` if available. Check what's available before building — don't assume.

3. **Shopping — two data sources** — Shopping Campaigns tab uses raw SQL, Shopping Products tab uses windowed feature columns. Sparklines only needed for the aggregate summary cards (top of page), not per-product.

4. **Template base** — ALL templates MUST extend `base_bootstrap.html`, not `base.html`

5. **Jinja2 macro import syntax** — use `{% from 'macros/metrics_cards.html' import metrics_section %}` at top of each template, not `{% include %}`

6. **Chart.js already loaded** — base_bootstrap.html may or may not load Chart.js. Check before adding it. If not present, add to `{% block extra_js %}` in the template or to base_bootstrap.html.

7. **Session key for collapse** — use `session['metrics_collapsed']` as a dict keyed by page_id. Don't create a separate session key per page.

8. **Previous period with custom date range** — carry forward the same prev period logic already in `dashboard.py`. Don't invent a new approach.

---

## TESTING CHECKLIST

Before declaring complete, ALL must pass:

- [ ] IS metrics exist in database with synthetic data values
- [ ] Financial row shows correct 8 cards on Campaigns (2 groups of 4)
- [ ] Leads sub-label appears above cards 5-8
- [ ] Financial sub-label appears above cards 1-4
- [ ] Vertical separator visible between card 4 and 5
- [ ] Change indicators show on every non-BLANK card
- [ ] Cost card: ↑ shows RED, ↓ shows GREEN
- [ ] Revenue card: ↑ shows GREEN, ↓ shows RED
- [ ] Sparklines render inside each card
- [ ] Actions row visible by default (expanded)
- [ ] Pill toggle collapses Actions row
- [ ] Collapsed state: only pill shows, chart follows directly
- [ ] Collapse state persists: collapse on Campaigns, navigate to Keywords, still collapsed
- [ ] BLANK cards render as empty placeholders (no error)
- [ ] Ad Strength card: 240/983 format with Good/Excellent sub-label
- [ ] Shopping Conv Value card in slot 2
- [ ] All 6 pages render without errors
- [ ] No regressions on date picker (M1) or existing page functionality

---

## HANDOFF REQUIREMENTS

On completion create:
`C:\Users\User\Desktop\gads-data-layer\docs\CHAT_23_HANDOFF.md`
`C:\Users\User\Desktop\gads-data-layer\docs\CHAT_23_SUMMARY.md`

Include:
- All files changed with exact paths
- Schema changes made (exact SQL)
- Macro API documentation (parameters, expected data shapes)
- Any deviations from brief and why
- Known issues or limitations
- Git commit message ready for Master Chat approval

Do NOT create handoff until all checklist items pass.

---

## SUCCESS CRITERIA

Chat 23 is complete when:
- ✅ IS metrics in database with synthetic data
- ✅ Jinja2 macro producing correct 2-row 8-card layout on all 6 pages
- ✅ Financial/Leads group separator and sub-labels visible
- ✅ Option A pill toggle working, collapse state in session
- ✅ Change indicators with correct colour logic including inversions
- ✅ Sparklines rendering in every non-BLANK card
- ✅ All 17 checklist items pass
- ✅ Handoff + Summary docs created and approved by Master Chat
