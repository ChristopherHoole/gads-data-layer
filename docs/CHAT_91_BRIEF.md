# CHAT 91: CAMPAIGN RULES & FLAGS — FULL BUILD

**Date:** 2026-03-13
**Estimated Time:** 4–6 hours
**Priority:** HIGH
**Dependencies:** Chats 88, 89, 90 complete

---

## CONTEXT

The existing rules system (41 rules in rules_config.json) is being replaced entirely. The new system introduces a `rules` database table with 24 campaign rules and 30 campaign flags. The old rules_config.json and legacy execution Python files are NOT deleted — left as dead code for reference only. All existing rows in the `recommendations` table are wiped as part of migration (they reference old rule IDs).

## OBJECTIVE

Build the complete Campaign Rules & Flags system: database schema, seed data, backend routes, Rules & Flags tab UI, 5-step flow builder, and CSS — all integrated into the existing campaigns page.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\tools\migrate_rules_schema.py` — CREATE
   - Creates `rules` table and `rule_evaluation_log` table in warehouse.duckdb
   - Adds nullable `rule_id` FK column to `recommendations` table
   - Wipes all existing rows from `recommendations`
   - Safe to re-run (checks existence before creating)

2. `C:\Users\User\Desktop\gads-data-layer\tools\seed_campaign_rules.py` — CREATE
   - Seeds all 54 rows: 24 rules + 30 flags (full list in REQUIREMENTS)
   - Safe to re-run (DELETE all then INSERT)

3. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\campaigns.py` — MODIFY
   - Add 5 new API endpoints for rules CRUD (full list in REQUIREMENTS)

4. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — MODIFY
   - Add campaigns rules routes to CSRF exempt list

5. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\rules_flags_tab.html` — CREATE
   - Rules & Flags tab content with sub-tabs, tables, filter tabs, search

6. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\rules_flow_builder.html` — CREATE
   - 5-step full-page overlay flow builder

7. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\campaigns.html` — MODIFY
   - Rename "Rules" tab to "Rules & Flags", update badge, include new components

8. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\rules.css` — CREATE
   - All styles for flow builder, tables, badges (no body/container overrides)

9. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_91_HANDOFF.md` — CREATE
10. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_91_SUMMARY.md` — CREATE

---

## REQUIREMENTS

### DATABASE SCHEMA

#### `rules` table (warehouse.duckdb)
```sql
CREATE TABLE IF NOT EXISTS rules (
    id INTEGER PRIMARY KEY,
    client_config VARCHAR NOT NULL,
    entity_type VARCHAR NOT NULL DEFAULT 'campaign',
    name VARCHAR NOT NULL,
    rule_or_flag VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    campaign_type_lock VARCHAR,
    entity_scope JSON NOT NULL DEFAULT '{"scope":"all"}',
    conditions JSON NOT NULL,
    action_type VARCHAR,
    action_magnitude FLOAT,
    cooldown_days INTEGER DEFAULT 7,
    risk_level VARCHAR,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_evaluated_at TIMESTAMP,
    last_fired_at TIMESTAMP
);
```

#### `rule_evaluation_log` table (warehouse.duckdb)
```sql
CREATE TABLE IF NOT EXISTS rule_evaluation_log (
    id INTEGER PRIMARY KEY,
    rule_id INTEGER NOT NULL,
    entity_type VARCHAR NOT NULL,
    entity_id VARCHAR NOT NULL,
    evaluated_at TIMESTAMP DEFAULT NOW(),
    conditions_met BOOLEAN NOT NULL,
    recommendation_id INTEGER,
    skip_reason VARCHAR
);
```

#### Modify `recommendations` table
```sql
ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS rule_id INTEGER;
DELETE FROM recommendations;
```

---

### SEED DATA — ALL 54 ROWS

Use `client_config = 'client_christopher_hoole'` for all rows.
`entity_scope = '{"scope":"all"}'` for all seeded rows.
`enabled = TRUE` for all.

#### BUDGET RULES (15 rows)

**tROAS / Max Conversion Value — campaign_type_lock = 'troas'**

| name | conditions (JSON) | action_type | action_magnitude | cooldown_days | risk_level |
|------|-------------------|-------------|-----------------|---------------|------------|
| Increase Budget – Strong ROAS | [{"metric":"roas_7d","operator":">=","value":1.15,"unit":"x_target"},{"metric":"clicks_7d","operator":">=","value":30,"unit":"absolute"}] | increase_budget | 10.0 | 7 | low |
| Decrease Budget – Weak ROAS | [{"metric":"roas_7d","operator":"<","value":0.85,"unit":"x_target"},{"metric":"clicks_7d","operator":">=","value":30,"unit":"absolute"}] | decrease_budget | 10.0 | 7 | low |
| Emergency Budget Cut – Critical ROAS | [{"metric":"roas_7d","operator":"<","value":0.50,"unit":"x_target"},{"metric":"cost_7d","operator":">=","value":100,"unit":"absolute"}] | decrease_budget | 25.0 | 14 | medium |
| Pacing Reduction – Over Budget | [{"metric":"pacing_vs_cap","operator":">","value":105,"unit":"percent"}] | decrease_budget | 15.0 | 7 | medium |
| Pacing Increase – Under Budget | [{"metric":"pacing_vs_cap","operator":"<","value":80,"unit":"percent"},{"metric":"roas_7d","operator":">=","value":1.0,"unit":"x_target"}] | increase_budget | 10.0 | 7 | low |

**tCPA — campaign_type_lock = 'tcpa'**

| name | conditions (JSON) | action_type | action_magnitude | cooldown_days | risk_level |
|------|-------------------|-------------|-----------------|---------------|------------|
| Increase Budget – Strong CPA | [{"metric":"cpa_7d","operator":"<=","value":0.90,"unit":"x_target"},{"metric":"conversions_7d","operator":">=","value":10,"unit":"absolute"}] | increase_budget | 10.0 | 7 | low |
| Decrease Budget – Weak CPA | [{"metric":"cpa_7d","operator":">","value":1.20,"unit":"x_target"},{"metric":"conversions_7d","operator":">=","value":5,"unit":"absolute"}] | decrease_budget | 10.0 | 7 | low |
| Emergency Budget Cut – Critical CPA | [{"metric":"cpa_7d","operator":">","value":2.0,"unit":"x_target"},{"metric":"cost_7d","operator":">=","value":100,"unit":"absolute"}] | decrease_budget | 25.0 | 14 | medium |
| Pacing Reduction – Over Budget | [{"metric":"pacing_vs_cap","operator":">","value":105,"unit":"percent"}] | decrease_budget | 15.0 | 7 | medium |
| Pacing Increase – Under Budget | [{"metric":"pacing_vs_cap","operator":"<","value":80,"unit":"percent"},{"metric":"cpa_7d","operator":"<=","value":1.0,"unit":"x_target"}] | increase_budget | 10.0 | 7 | low |

**Max Clicks — campaign_type_lock = 'max_clicks'**

| name | conditions (JSON) | action_type | action_magnitude | cooldown_days | risk_level |
|------|-------------------|-------------|-----------------|---------------|------------|
| Increase Budget – Strong CTR | [{"metric":"ctr_7d","operator":">=","value":5.0,"unit":"percent"},{"metric":"clicks_7d","operator":">=","value":50,"unit":"absolute"}] | increase_budget | 10.0 | 7 | low |
| Decrease Budget – Weak CTR | [{"metric":"ctr_7d","operator":"<","value":2.0,"unit":"percent"},{"metric":"clicks_7d","operator":">=","value":50,"unit":"absolute"}] | decrease_budget | 10.0 | 7 | low |
| Emergency Budget Cut – Very Low CTR | [{"metric":"ctr_7d","operator":"<","value":1.0,"unit":"percent"},{"metric":"cost_7d","operator":">=","value":100,"unit":"absolute"}] | decrease_budget | 25.0 | 14 | medium |
| Pacing Reduction – Over Budget | [{"metric":"pacing_vs_cap","operator":">","value":105,"unit":"percent"}] | decrease_budget | 15.0 | 7 | medium |
| Pacing Increase – Under Budget | [{"metric":"pacing_vs_cap","operator":"<","value":80,"unit":"percent"},{"metric":"ctr_7d","operator":">=","value":3.0,"unit":"percent"}] | increase_budget | 10.0 | 7 | low |

#### BID RULES (6 rows)

**tROAS — campaign_type_lock = 'troas'**

| name | conditions (JSON) | action_type | action_magnitude | cooldown_days | risk_level |
|------|-------------------|-------------|-----------------|---------------|------------|
| Tighten tROAS Target – Strong Performance | [{"metric":"roas_14d","operator":">=","value":1.20,"unit":"x_target"},{"metric":"conversions_14d","operator":">=","value":15,"unit":"absolute"}] | increase_target_roas | 5.0 | 14 | medium |
| Loosen tROAS Target – Constrained Volume | [{"metric":"roas_14d","operator":">=","value":1.05,"unit":"x_target"},{"metric":"impression_share_lost_rank","operator":">","value":20,"unit":"percent"}] | decrease_target_roas | 5.0 | 14 | medium |

**tCPA — campaign_type_lock = 'tcpa'**

| name | conditions (JSON) | action_type | action_magnitude | cooldown_days | risk_level |
|------|-------------------|-------------|-----------------|---------------|------------|
| Tighten tCPA Target – Strong CPA | [{"metric":"cpa_14d","operator":"<=","value":0.85,"unit":"x_target"},{"metric":"conversions_14d","operator":">=","value":15,"unit":"absolute"}] | decrease_target_cpa | 5.0 | 14 | medium |
| Loosen tCPA Target – Volume Constrained | [{"metric":"cpa_14d","operator":"<=","value":1.05,"unit":"x_target"},{"metric":"impression_share_lost_rank","operator":">","value":20,"unit":"percent"}] | increase_target_cpa | 5.0 | 14 | medium |

**Max Clicks — campaign_type_lock = 'max_clicks'**

| name | conditions (JSON) | action_type | action_magnitude | cooldown_days | risk_level |
|------|-------------------|-------------|-----------------|---------------|------------|
| Increase Max CPC Cap – Low Impression Share | [{"metric":"impression_share_lost_rank","operator":">","value":30,"unit":"percent"},{"metric":"clicks_7d","operator":">=","value":20,"unit":"absolute"}] | increase_max_cpc | 10.0 | 7 | medium |
| Decrease Max CPC Cap – High CPC Low CTR | [{"metric":"cpc_avg_7d","operator":">","value":3.0,"unit":"absolute"},{"metric":"ctr_7d","operator":"<","value":2.0,"unit":"percent"}] | decrease_max_cpc | 10.0 | 7 | medium |

#### STATUS RULES (3 rows) — ALL cooldown_days=14, risk_level='high', action_magnitude=NULL

| name | campaign_type_lock | conditions (JSON) | action_type |
|------|-------------------|-------------------|-------------|
| Pause – Poor ROAS | troas | [{"metric":"roas_14d","operator":"<","value":0.50,"unit":"x_target"},{"metric":"cost_14d","operator":">=","value":200,"unit":"absolute"}] | pause_campaign |
| Pause – High CPA | tcpa | [{"metric":"cpa_14d","operator":">","value":2.0,"unit":"x_target"},{"metric":"cost_14d","operator":">=","value":200,"unit":"absolute"}] | pause_campaign |
| Pause – High CPC | max_clicks | [{"metric":"cpc_avg_14d","operator":">","value":5.0,"unit":"absolute"},{"metric":"cost_14d","operator":">=","value":200,"unit":"absolute"}] | pause_campaign |

#### PERFORMANCE FLAGS (16 rows)
All: rule_or_flag='flag', type='performance', action_type=NULL, action_magnitude=NULL, risk_level=NULL, campaign_type_lock='all', cooldown_days=1

| name | conditions (JSON) |
|------|-------------------|
| ROAS Drop | [{"metric":"roas_w7_vs_prev_pct","operator":"<","value":-20,"unit":"percent"}] |
| ROAS Spike | [{"metric":"roas_w7_vs_prev_pct","operator":">","value":50,"unit":"percent"}] |
| CPA Spike | [{"metric":"cpa_w7_vs_prev_pct","operator":">","value":30,"unit":"percent"}] |
| CPA Drop | [{"metric":"cpa_w7_vs_prev_pct","operator":"<","value":-20,"unit":"percent"}] |
| CTR Drop | [{"metric":"ctr_w7_vs_prev_pct","operator":"<","value":-20,"unit":"percent"}] |
| CTR Spike | [{"metric":"ctr_w7_vs_prev_pct","operator":">","value":50,"unit":"percent"}] |
| CVR Drop | [{"metric":"cvr_w7_vs_prev_pct","operator":"<","value":-20,"unit":"percent"}] |
| CVR Spike | [{"metric":"cvr_w7_vs_prev_pct","operator":">","value":50,"unit":"percent"}] |
| Conversion Drop | [{"metric":"conversions_w7_vs_prev_pct","operator":"<","value":-30,"unit":"percent"}] |
| Conversion Spike | [{"metric":"conversions_w7_vs_prev_pct","operator":">","value":50,"unit":"percent"}] |
| Spend Drop | [{"metric":"cost_w7_vs_prev_pct","operator":"<","value":-30,"unit":"percent"}] |
| Spend Spike | [{"metric":"cost_w7_vs_prev_pct","operator":">","value":50,"unit":"percent"}] |
| Impression Share Drop | [{"metric":"impression_share_w7_vs_prev_pct","operator":"<","value":-20,"unit":"percent"}] |
| Impression Share Spike | [{"metric":"impression_share_w7_vs_prev_pct","operator":">","value":30,"unit":"percent"}] |
| Zero Impressions | [{"metric":"impressions_7d","operator":"=","value":0,"unit":"absolute"}] |
| CPC Spike | [{"metric":"cpc_w7_vs_prev_pct","operator":">","value":40,"unit":"percent"}] |

#### ANOMALY FLAGS (8 rows)
All: rule_or_flag='flag', type='anomaly', action_type=NULL, action_magnitude=NULL, risk_level=NULL, campaign_type_lock='all', cooldown_days=1

| name | conditions (JSON) |
|------|-------------------|
| Cost Spike | [{"metric":"cost_z_score","operator":">=","value":2.0,"unit":"absolute"}] |
| Cost Drop | [{"metric":"cost_z_score","operator":"<=","value":-2.0,"unit":"absolute"}] |
| Click Volume Spike | [{"metric":"click_z_score","operator":">=","value":2.0,"unit":"absolute"}] |
| Click Volume Drop | [{"metric":"click_z_score","operator":"<=","value":-2.0,"unit":"absolute"}] |
| Impression Spike | [{"metric":"impression_z_score","operator":">=","value":2.0,"unit":"absolute"}] |
| Impression Drop | [{"metric":"impression_z_score","operator":"<=","value":-2.0,"unit":"absolute"}] |
| Zero Conversions | [{"metric":"conversions_7d","operator":"=","value":0,"unit":"absolute"}] |
| Conversion Tracking Loss | [{"metric":"conv_tracking_loss_detected","operator":"=","value":1,"unit":"absolute"}] |

#### TECHNICAL FLAGS (6 rows)
All: rule_or_flag='flag', type='technical', action_type=NULL, action_magnitude=NULL, risk_level=NULL, campaign_type_lock='all', cooldown_days=1

| name | conditions (JSON) |
|------|-------------------|
| Landing Page Down | [{"metric":"landing_page_status","operator":"=","value":0,"unit":"absolute"}] |
| Landing Page Slow | [{"metric":"landing_page_load_ms","operator":">","value":3000,"unit":"absolute"}] |
| Ad Disapproved | [{"metric":"ads_disapproved_count","operator":">","value":0,"unit":"absolute"}] |
| Budget Exhausted Early | [{"metric":"budget_exhausted_hour","operator":"<","value":18,"unit":"absolute"}] |
| Billing Issue | [{"metric":"billing_issue_detected","operator":"=","value":1,"unit":"absolute"}] |
| Tracking Tag Missing | [{"metric":"tracking_tag_present","operator":"=","value":0,"unit":"absolute"}] |

---

### BACKEND ROUTES (add to campaigns.py)

All 5 routes share the same pattern:
- Get `client_config` from `session.get("current_client_config")` — NEVER `get_current_config()`
- Connect to `warehouse.duckdb` (writable, never read_only=True)
- Return `{"success": true, "data": ...}` or `{"success": false, "error": "..."}`

```
GET  /campaigns/rules                      → return all rules + flags for client as JSON array
POST /campaigns/rules                      → insert new rule/flag, return new row with id
PUT  /campaigns/rules/<int:rule_id>        → full replace of all mutable columns, update updated_at
DELETE /campaigns/rules/<int:rule_id>      → delete by id
POST /campaigns/rules/<int:rule_id>/toggle → flip enabled boolean, return new enabled state
```

Add all 5 to CSRF exempt in app.py — same pattern as existing outreach routes.

---

### UI — rules_flags_tab.html

**Sub-tab bar** (inside the Rules & Flags main tab):
- Rules | Flags | Templates
- Each sub-tab shows its own live count badge
- Rules badge = total enabled rules count; Flags badge = total enabled flags count

**Rules sub-tab:**
- Filter bar: All · Budget · Bid · Status (pill buttons)
- Search input (filters by name or plain English column)
- "+ Add rule" button (opens flow builder)
- Table — sticky first column (on/off toggle)

| Column | Notes |
|--------|-------|
| On/Off | Bootstrap toggle switch, calls /toggle on change, no page reload |
| Rule name | |
| Type | Coloured badge: Budget=blue, Bid=purple, Status=red |
| Campaign type | tROAS / tCPA / Max Clicks / All |
| Campaigns | "All campaigns" or comma-separated names |
| Plain English | 320–480px wide, italic 12px muted, auto-generated from conditions + action |
| Conditions | Compact text: "metric operator value" |
| Action | Explicit: "↑ Increase budget 10%" / "⏸ Pause campaign" |
| Guardrail | Short note e.g. "≥30 clicks required" |
| Risk | Coloured badge: Low=green, Medium=amber, High=red |
| Actions | Edit (pencil icon) · Delete (trash icon) |

Group header rows separate Budget / Bid / Status sections (light grey, 600 weight, not allcaps).
Empty state: info-blue alert "No rules yet — click Add rule to create your first one."

**Flags sub-tab:**
- Filter bar: All · Performance · Anomaly · Technical
- Search input
- "+ Add flag" button (opens flow builder)

| Column | Notes |
|--------|-------|
| On/Off | Toggle |
| Flag name | |
| Type | Coloured badge: Performance=orange, Anomaly=yellow (dark text), Technical=grey |
| Campaigns | "All campaigns" or list |
| Plain English | Same italic muted style |
| Condition | "metric operator value" |
| Direction | Up / Down / Either |
| Window | "7 days" / "14 days" etc. |
| Actions | Edit · Delete |

**Templates sub-tab:**
- Card grid: 4 columns desktop, 2 tablet, 1 mobile
- Each card: icon · name · description · "Use template" button
- 6 pre-built template cards:
  1. Increase Budget – Strong ROAS
  2. Decrease Budget – Weak ROAS
  3. Pause – Poor ROAS
  4. ROAS Drop Flag
  5. Cost Spike Flag
  6. Landing Page Down Flag
- Clicking "Use template" opens flow builder with fields pre-filled for that template

---

### UI — rules_flow_builder.html

Full-page overlay: position fixed, top/left 0, width/height 100%, z-index 1050, white background.
Close button (×) top-right. NOT a Bootstrap modal.

**Progress bar** at top: 5 numbered step circles with connector lines. Completed steps show checkmark. Active step highlighted. Labels below each: "Campaigns", "Type", "Category", "Conditions", "Summary".

**Step 1 — Select Campaigns**
- Heading: "Which campaigns does this rule apply to?"
- Default: nothing pre-selected. User must make an explicit choice.
- "All campaigns" radio button option at top
- Below: campaign list with individual checkboxes — each row: checkbox · campaign name · strategy badge (tROAS / tCPA / Max Clicks / Manual CPC)
- Strategy lock (JavaScript, rules only): first campaign selected captures its strategy; any subsequent campaign with a different strategy shows as disabled with tooltip "This rule requires a single bidding strategy"
- For flags (detected from Step 2 choice): strategy lock does NOT apply, all campaigns selectable
- "Next" button disabled until at least one selection made

**Step 2 — Rule or Flag**
- Two large cards side by side
- Left: bolt icon · "Rule" · "Triggers a recommendation to take action"
- Right: flag icon · "Flag" · "Raises an alert — no action taken"
- Single click selects (highlighted border), enables Next

**Step 3 — Category**
- If Rule: Budget · Bid · Status (3 large pill buttons)
- If Flag: Performance · Anomaly · Technical (3 large pill buttons)
- Status rules: show info callout "Status rules require human confirmation before any action is taken"

**Step 4 — Conditions & Action**
- Condition row 1: [metric dropdown] [operator dropdown] [value input] [unit label]
- "+ Add second condition" link (adds second identical row, max 2)
- Metric dropdown options filtered by campaign type from Step 1 (use campaign_type_lock value)
- If Rule — Action section below conditions:
  - Action type dropdown (options filtered by category from Step 3)
  - Magnitude input (% value, hidden for pause_campaign)
  - Cooldown dropdown: 7 days / 14 days / 30 days
  - Risk badge auto-calculated read-only: Status=High always, Bid=Medium always, Budget ≤10%=Low, Budget >10%=Medium
  - Guardrail note (static): "Minimum data threshold required before this rule can fire"
- If Flag — Direction dropdown: ↑ Rising / ↓ Falling / Either + Alert window dropdown: 1 day / 7 days / 14 days

**Step 5 — Summary & Save**
- Name field: pre-suggested based on type + action, user can edit
- Full read-only summary card of all choices made
- "Save rule" / "Save flag" primary button
- On click: POST to /campaigns/rules → on success: close overlay, new row appears in table without reload, show success toast
- On error: show inline error message inside overlay (do not close)

---

### CSS — rules.css

Must include:
- Flow builder overlay (position fixed, z-index 1050, white bg, scroll handling)
- Progress bar: step circles (32px), connector lines, completed/active/inactive colour states
- Step fade transition between steps
- Table group header row: `background: #f8f9fa; font-weight: 600; font-size: 12px`
- Type badge colours: Budget `#0d6efd`, Bid `#6f42c1`, Status `#dc3545`, Performance `#fd7e14`, Anomaly `#ffc107` with dark text, Technical `#6c757d`
- Risk badge colours: Low `#198754`, Medium `#fd7e14`, High `#dc3545`
- Template card: border `1px solid #dee2e6`, hover `box-shadow: 0 2px 8px rgba(0,0,0,0.1)`
- Plain English column: `font-style: italic; font-size: 12px; color: #6c757d; min-width: 320px; max-width: 480px`

Must NOT include:
- Any `body { }` or `html { }` rules
- Any `.container { }` overrides
- Any redefinition of `.d-none`, `.d-flex`, `.d-block` or any Bootstrap utility class

---

### campaigns.html CHANGES

1. Rename tab label: "Rules" → "Rules & Flags"
2. Tab badge: load rules + flags count via GET /campaigns/rules on page load, sum them
3. Inside the Rules & Flags tab pane: replace old rules include with `{% include 'components/rules_flags_tab.html' %}`
4. Before `</body>`: add `{% include 'components/rules_flow_builder.html' %}`
5. In head CSS includes: add `<link rel="stylesheet" href="{{ url_for('static', filename='css/rules.css') }}">`

---

## CONSTRAINTS

- `session.get("current_client_config")` everywhere — NEVER `get_current_config()`
- Never open warehouse.duckdb with `read_only=True`
- Never redefine Bootstrap utility classes in rules.css
- No body/container CSS overrides in rules.css (KNOWN_PITFALLS.md pitfall 48)
- No `.d-none` in any custom CSS (KNOWN_PITFALLS.md pitfall 49)
- Material Symbols Outlined for all icons — no emoji
- No allcaps in any UI text
- Bootstrap 5 components only
- All templates extend base_bootstrap.html

---

## SUCCESS CRITERIA

- [ ] Flask starts cleanly — no import errors
- [ ] `python tools/migrate_rules_schema.py` runs, prints confirmation, no errors
- [ ] `python tools/seed_campaign_rules.py` runs, prints "Seeded 54 rows: 24 rules, 30 flags"
- [ ] Campaigns page loads — tab shows "Rules & Flags" with correct badge count
- [ ] Rules sub-tab: 24 rows visible, grouped Budget (15) / Bid (6) / Status (3)
- [ ] Flags sub-tab: 30 rows visible, grouped Performance (16) / Anomaly (8) / Technical (6)
- [ ] Templates sub-tab: 6 template cards visible
- [ ] Toggle switch calls /toggle, flips state, no page reload
- [ ] "+ Add rule" opens flow builder overlay
- [ ] Step 1: nothing pre-selected by default
- [ ] Step 1: mixed bidding strategies blocked for rules (visual error shown)
- [ ] All 5 flow builder steps navigable (Next / Back)
- [ ] Saving a new rule: row appears in table, success toast shown
- [ ] Deleting a rule: row removed, success toast shown
- [ ] No Flask console errors
- [ ] No browser console errors

---

## REFERENCE FILES

- `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_91_WIREFRAME.html` — target UI design, match this exactly
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\campaigns.html`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\campaigns.py`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — CSRF exempt pattern
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — CSRF exempt registration
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\table-styles.css` — table patterns
- `C:\Users\User\Desktop\gads-data-layer\docs\KNOWN_PITFALLS.md` — pitfalls 48, 49, 50 critical

---

## TESTING

1. Run `python tools/migrate_rules_schema.py` — confirm output
2. Run `python tools/seed_campaign_rules.py` — confirm "54 rows" output
3. Start Flask (fresh PowerShell)
4. Open Opera → Campaigns page → Rules & Flags tab
5. Confirm Rules sub-tab: 24 rows, grouped correctly, all badges correct
6. Confirm Flags sub-tab: 30 rows, grouped correctly
7. Toggle a rule — confirm state flips, no reload
8. Click "+ Add rule" — flow builder opens
9. Step 1 — confirm nothing pre-selected
10. Select two campaigns with different strategies — confirm blocked with error
11. Complete full 5-step flow, save — confirm new row appears and toast fires
12. Delete a row — confirm removed and toast fires
13. Report exact Flask terminal output for any DB writes
