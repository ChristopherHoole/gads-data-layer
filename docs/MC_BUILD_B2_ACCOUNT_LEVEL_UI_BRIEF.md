# MC Build B2 — Account Level UI
**Session:** MC Build B2 — Account Level UI
**Date:** 2026-04-13
**Objective:** Build the Account Level page as a real Flask page, wired to real data from the database and the B1 engine output. This is the second v2 page (after Client Config) using the base_v2.html template.

---

## CONTEXT

Sessions A1-B1 are complete:
- 13 `act_v2_*` tables + 2 data tables (search_terms, campaign_segments) = 15 tables
- 71 settings, 90 days real data, Account Level engine built and tested
- Client Config page live at `/v2/config`
- Base template `base_v2.html` exists and works
- Account Level engine produces 0 recommendations for Objection Experts (1 ENABLED campaign — valid outcome)
- `act_v2_snapshots` has real campaign data with metrics_json

**This session builds the Account Level UI page — converting the prototype to a Flask page with real data.**

**Source of truth:**
- Prototype: `act_dashboard/prototypes/account-level-v10.html` — the exact UI to replicate
- Prototype CSS: `act_dashboard/prototypes/css/account-level-v10.css`
- Prototype JS: `act_dashboard/prototypes/js/account-level-v10.js`
- Design standards: `docs/ACT_PROTOTYPE_STANDARDS.md`
- Engine output: `act_v2_recommendations` (may be empty for Objection Experts — that's expected)

---

## CRITICAL RULES

1. **Match the prototype account-level-v10.html EXACTLY.** Same layout, same sections, same interactions.

2. **Reuse base_v2.html.** Extend the base template created in Session A3. Use `active_page='account'` for the sidebar highlight.

3. **Read from real database.** All data comes from `act_v2_snapshots`, `act_v2_recommendations`, `act_v2_executed_actions`, `act_v2_monitoring`, `act_v2_alerts`, `act_v2_campaign_roles`, `act_v2_clients`, `act_v2_client_settings`.

4. **Do NOT modify base_v2.html or any A3 files.** Create new files for the Account Level page.

5. **Handle empty data gracefully.** Objection Experts has 1 ENABLED campaign and 0 recommendations. The page should show:
   - Health cards with real data (budget, CPA, spend MTD, conversions)
   - Campaign Performance section with real chart and table (1 campaign: "GLO Campaign" ENABLED — the only campaign)
   - Empty review sections with appropriate empty states ("All clear — no actions need your review today")
   - Budget Allocation section (collapsed, shows current allocation even with 1 campaign)

6. **Reuse prototype CSS/JS.** Copy and adapt like we did for Client Config.

---

## TASK 1: Read the Prototype and Existing Code

Read these files:
1. `act_dashboard/prototypes/account-level-v10.html` — the full Account Level prototype
2. `act_dashboard/prototypes/css/account-level-v10.css` — page styles
3. `act_dashboard/prototypes/js/account-level-v10.js` — interactions (chart, date range, table sorting, slide-in, approval/decline)
4. `act_dashboard/templates/v2/base_v2.html` — the base template to extend
5. `act_dashboard/templates/v2/client_config.html` — reference for how A3 extends base_v2
6. `act_dashboard/routes/v2_config.py` — reference for route patterns, DB connection, template rendering

Confirm what you understand about the prototype structure and the page sections.

---

## TASK 2: Create the Account Level Route

Create `act_dashboard/routes/v2_account.py` — a new Flask Blueprint.

```python
v2_account_bp = Blueprint('v2_account', __name__, url_prefix='/v2')

@v2_account_bp.route('/account')
def account_level():
    """Render the Account Level page."""
    client_id = request.args.get('client', 'oe001')
    date_range = request.args.get('days', '30')  # 7, 30, or 90 — using 'days' not 'range' to avoid shadowing Python built-in
    
    # Read from database:
    # 1. Client info from act_v2_clients
    # 2. Client list for switcher
    # 3. Campaign snapshots from act_v2_snapshots (level='campaign', for date range)
    # 4. Account snapshot from act_v2_snapshots (level='account', latest date)
    # 5. Campaign roles from act_v2_campaign_roles
    # 6. Awaiting Approval: act_v2_recommendations WHERE level='account' AND status='pending'
    # 7. Actions Executed Overnight: act_v2_executed_actions WHERE level='account' AND execution_status='success' AND executed_at >= midnight today (or last 24h)
    # 8. Currently Monitoring: act_v2_monitoring WHERE level='account' AND resolved_at IS NULL
    # 9. Recent Alerts: act_v2_alerts WHERE level='account' AND raised_at >= NOW() - 7 days
    # 10. Account-level settings for health cards (deviation_threshold_pct from act_v2_client_settings; target_cpa and monthly_budget already in #1 from act_v2_clients)
    # 11. Signal decomposition data (compute from campaign snapshots)
    # 12. Budget shift history from act_v2_executed_actions (level='account', last 10)
    
    return render_template('v2/account_level.html', ...)
```

**Also create a shared API blueprint** for recommendation actions (used by ALL level pages, not just Account):

Create `act_dashboard/routes/v2_api.py`:

```python
v2_api_bp = Blueprint('v2_api', __name__, url_prefix='/v2/api')

@v2_api_bp.route('/recommendations/<int:rec_id>/approve', methods=['POST'])
def approve_recommendation(rec_id):
    """Approve a recommendation. Used by all level pages."""
    # Update act_v2_recommendations SET status='approved', actioned_at=CURRENT_TIMESTAMP, actioned_by='user'
    # Return JSON {success: true}

@v2_api_bp.route('/recommendations/<int:rec_id>/decline', methods=['POST'])
def decline_recommendation(rec_id):
    """Decline a recommendation. Used by all level pages."""
    # Update act_v2_recommendations SET status='declined', actioned_at=CURRENT_TIMESTAMP, actioned_by='user'
    # Return JSON {success: true}
```

Note: These endpoints won't be used for Objection Experts yet (0 recommendations) but should exist so the UI components work when recommendations appear. They are on a SHARED blueprint so all level pages use the same endpoints.

**Register BOTH blueprints in `act_dashboard/routes/__init__.py`** inside the `register_blueprints(app)` function (follow the existing pattern from v2_config_bp). Then add CSRF exemptions for the API endpoints in `act_dashboard/app.py` (follow the existing pattern from v2_config exemptions near line 530).

**Date range handling:** The `days` query parameter controls both the chart and the campaigns table. The route should:
- `days=7` → query snapshots for last 7 days, daily intervals on chart
- `days=30` → query snapshots for last 30 days, daily intervals on chart
- `days=90` → query snapshots for last 90 days, weekly aggregated intervals on chart

---

## TASK 3: Create the Account Level Template

Create `act_dashboard/templates/v2/account_level.html` extending `base_v2.html`.

The page structure from the prototype (top to bottom):

### Section 1: Page Header
- Blue (#3b82f6) level accent border
- Title: "Budget Allocation & Health"
- Subtitle: "Objection Experts" (client name)
- "ACT last ran" timestamp in the top bar (from MAX of act_v2_executed_actions or act_v2_recommendations identified_at, or "Never" if no engine has run)
- NO duplicated metrics in the header — budget, CPA, etc. are shown in the health cards below (we removed header duplication in prototype v10)

### Section 2: Health Summary Cards
4 cards from real data:
- Monthly Budget: from act_v2_clients.monthly_budget
- Current CPA: from latest account snapshot metrics_json.cost_per_conversion, with zone badge (Outperforming/On Target/Underperforming)
- Budget Used (MTD): sum of campaign costs this month vs monthly budget, with progress bar
- Conversions (MTD): sum of campaign conversions this month

### Section 3: Campaign Performance (Combined Section)
This is the main section with chart + table.

**Summary metric cards:** Cost, Impressions, Clicks, Avg CPC, CTR, Conversions, Avg CPA, Conv Rate — aggregated from campaign snapshots for the selected date range.

**Timeline chart:** Chart.js line chart with dual axes (y1 left, y2 right), 10 metric dropdown options (Cost, Impressions, Clicks, Avg CPC, CTR, Conversions, CPA, Conv Rate, Performance Score, Budget Utilisation %). Straight lines (tension: 0), light semi-transparent fill (rgba with 0.08 alpha), gridlines on x-axis and y1-axis only (y2 drawOnChartArea: false). Default: Cost (line 1) + Conversions (line 2). Line 1 colour: #3b82f6 (blue), Line 2 colour: #10b981 (green). Point radius 3 (hover 5), border width 2, responsive, legend hidden. Match prototype `account-level-v10.js` Chart.js config exactly.

**Campaigns data table:** One row per campaign from act_v2_snapshots. Columns: Status, Campaign, Role, Budget, Share, Cost, Impr., Clicks, Avg CPC, CTR, Conv., Cost/Conv, Conv Rate, Score. Sortable, left-aligned, totals/averages row, rows per page dropdown, status filters (All/Enabled/Paused). Match the exact column headers from the prototype.

**Date range pills (7d/30d/90d):** Control BOTH chart and table. When changed, reload page with `?client=X&days=Y` query parameters (preserve the client param when switching date range). Or use AJAX to update chart + table without full reload — session's choice. Note: query param is `days` not `range` (avoids shadowing Python built-in).

### Section 4: Account-Level Review Sections
Same 4 sections as Morning Review, filtered to Account Level:
- Awaiting Approval (expanded by default)
- Actions Executed Overnight (collapsed)
- Currently Monitoring (collapsed)
- Recent Alerts (collapsed)

**For Objection Experts:** All 4 sections will show empty states since the engine produced 0 recommendations for the 1-campaign account. This is correct — the empty states should display using the same patterns from the Morning Review prototype.

### Section 5: Budget Allocation (Collapsed by default)
- Stacked budget bar (campaign segments by budget share)
- Signal Decomposition table (CPC/CVR/CPA trends per campaign)
- Budget Shift History table (from act_v2_executed_actions, level='account')
- Guardrails list (from settings)

**For Objection Experts:** Shows 1 campaign at 100% budget share. Signal decomposition shows real CPC/CVR trends from snapshots. Budget shift history will be empty (no shifts executed yet). Guardrails show real values from settings.

---

## TASK 4: Create Static Assets

1. **`act_dashboard/static/css/v2_account_level.css`** — copy from `account-level-v10.css`, adapt paths
2. **`act_dashboard/static/js/v2_account_level.js`** — copy from `account-level-v10.js`, adapt for real data:
   - Chart.js with real data points from template variables
   - Date range switching (page reload preserving all query params, or AJAX)
   - Table sorting
   - Review section collapse/expand
   - Slide-in panel for campaign details (if clicking a campaign name)
   - Approve/Decline buttons (send AJAX to backend — create endpoint if needed)
   - Empty state handling

**Chart data:** Pass chart data as JSON from the route via a `<script>` tag in the template:
```html
<script>
  const chartData = {{ chart_data | tojson }};
</script>
```

The route prepares `chart_data` as a dict with account-level aggregated metrics (summed across all campaigns). Structure: `{labels: ['2026-03-15', ...], metrics: {cost: [41, 38, ...], impressions: [314, 290, ...], clicks: [20, 18, ...], avgCpc: [...], ctr: [...], conversions: [...], cpa: [...], convRate: [...], score: [...], budgetUtil: [...]}}`. For 90d, aggregate into 13 weekly points (SUM for volume, AVG for rates). For 7d/30d, one point per day.

---

## TASK 5: Test Everything

1. Navigate to `http://localhost:5000/v2/account`
2. Verify health cards show real data (budget £1,500, current CPA from snapshots, MTD spend, MTD conversions)
3. Verify chart renders with real campaign data points
4. Verify campaigns table shows real campaigns (1 campaign: "GLO Campaign" ENABLED — this is the only campaign for Objection Experts)
5. Verify date range switching works (7d/30d/90d)
6. Verify table sorting works
7. Verify review sections show empty states (0 recommendations)
8. Verify Budget Allocation section shows 1 campaign at 100%
9. Verify dark mode works
10. Verify old pages and Client Config still work
11. Check browser console — zero errors

---

## TASK 6: Commit

Git commit with clear message.

---

## DELIVERABLES

1. `act_dashboard/templates/v2/account_level.html`
2. `act_dashboard/static/css/v2_account_level.css`
3. `act_dashboard/static/js/v2_account_level.js`
4. `act_dashboard/routes/v2_account.py` — Account Level page route
5. `act_dashboard/routes/v2_api.py` — shared API endpoints (approve/decline)
6. Updated `act_dashboard/routes/__init__.py` — both blueprints registered
7. Updated `act_dashboard/app.py` — CSRF exemptions for API endpoints
8. Page loads with real data at `/v2/account`
9. Git commit

---

## EXECUTION ORDER

1. Read prototype and existing Flask v2 code (Task 1)
2. Copy CSS/JS static assets from prototype (Task 4 — do first so templates can reference them)
3. Create Flask route (Task 2)
4. Create Account Level template (Task 3)
5. Test everything (Task 5)
6. Commit (Task 6)

---

## VERIFICATION CHECKLIST

- [ ] Page loads at `/v2/account` with real data
- [ ] Health cards show correct values from database
- [ ] Chart renders with real campaign data (Chart.js, straight lines, light fill, dual axes, match prototype config exactly)
- [ ] Date range switching works (7d/30d/90d update chart + table + summary cards)
- [ ] Campaigns table shows real campaigns with correct metrics
- [ ] Table sorting works on all columns
- [ ] Review sections show empty states correctly
- [ ] Budget Allocation section renders (even with 1 campaign)
- [ ] Signal Decomposition shows real CPC/CVR trends
- [ ] Dark mode works
- [ ] Sidebar highlights "Account Level" as active
- [ ] Client Config page still works at `/v2/config`
- [ ] Old Flask pages still work
- [ ] Zero browser console errors
- [ ] Git commit created

---

## IMPORTANT NOTES

- The prototype `account-level-v10.html` is the source of truth for layout — match it exactly
- Use `{{ url_for('static', filename='...') }}` for all asset paths
- **Chart.js is NOT in base_v2.html** — include it per-page. The prototype uses Chart.js 4.4.0 from CDN: `https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js`. Add this in the `page_js` block before the account level JS file.
- Pass chart data as JSON via `{{ chart_data | tojson }}` in a script tag
- **`metrics_json` returns as a string from DuckDB**, not a dict. Use `json.loads()` on each row's metrics_json value (see `act_dashboard/engine/base.py` line 142 for the pattern). Or use DuckDB's `->>'key'` JSON extraction in SQL to avoid parsing in Python.
- The page will mostly show real data but with empty review sections (no engine recommendations) — this is expected and correct for Objection Experts
- The slide-in panel (if campaign name is clicked) can be a simplified version for now — full slide-in detail comes later with the Campaign Level page
- For 90d date range, aggregate weekly: SUM for volume metrics (cost, impressions, clicks, conversions), AVERAGE for rate metrics (CPC, CTR, CPA, conv rate)
- **Performance Score column:** Reuse the scoring logic from `AccountLevelEngine._score_campaigns()` in `act_dashboard/engine/account_level.py`. Note: this is an instance method that requires `self` (client, settings, DB connection). Either instantiate `AccountLevelEngine(client_id)` in the route and call `_score_campaigns()`, or extract the scoring math into a standalone helper function that both the engine and the route can call. For paused campaigns, show "—" (no score computed for inactive campaigns). For enabled campaigns, show the weighted score with colour coding (green > 0, red < 0).
- Budget Utilisation %: (MTD spend / monthly budget) × 100
- **Chart metric computation:** Most chart metrics (cost, impressions, clicks, conversions, avgCpc, ctr, cpa, convRate) come directly from daily account snapshots in `metrics_json`. The `score` and `budgetUtil` metrics require extra computation: `score` needs the weighted scoring calc per day (expensive — can be computed once per date range and cached), `budgetUtil` needs cumulative MTD spend per day divided by monthly budget. If these are complex to compute per-day, it's acceptable to show them as flat/zero in the dropdown for now and implement full computation later.
- **Zero conversions CPA handling:** If conversions = 0, `cost_per_conversion` in the snapshot will be 0.0. Do NOT display £0.00 CPA with an "Outperforming" badge — that's misleading. Instead show "—" for CPA and no zone badge (or a neutral "No data" badge) when conversions = 0.
- **Campaign roles:** The `act_v2_campaign_roles` table is currently empty for Objection Experts (no roles assigned yet). The Role column in the campaigns table should show "—" or be blank when no role is assigned. The role badge classes exist in the CSS (`.role-badge--bd`, `.role-badge--cp`, etc.) and will work once roles are assigned.
- **Zone badge logic:** Read `deviation_threshold_pct` setting (default 10%). Outperforming: CPA < target × (1 - deviation/100). On Target: CPA between those bounds. Underperforming: CPA > target × (1 + deviation/100). For Objection Experts with target £25 and 10% deviation: Outperforming < £22.50, On Target £22.50-£27.50, Underperforming > £27.50. Only show zone badge when conversions > 0 (see zero conversions note above).

---

**END OF BRIEF**
