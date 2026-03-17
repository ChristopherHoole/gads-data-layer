# CHAT 96: RECOMMENDATIONS UI OVERHAUL

**Date:** 2026-03-16
**Estimated Time:** 6–8 hours
**Priority:** HIGH
**Dependencies:** Chat 95 complete (engine reads from DB, display bug fixed)
**Architecture:** 2-Tier — Claude Code executes autonomously, reports back when complete

---

## CONTEXT

The recommendations system generates 1,500+ recommendations across 5 entity types. The current UI uses cards which are impossible to scan at scale. Master Chat 12 has designed a full table-based replacement matching the existing Rules & Flags table design. All wireframes and CSS are complete and approved.

---

## OBJECTIVE

Replace all card-based recommendation UIs with table-based designs across the full Recommendations page and the Recommendations tab on all 5 entity pages.

---

## FIRST STEP — READ THESE FILES BEFORE WRITING ANY CODE

```
C:\Users\User\Desktop\gads-data-layer\docs\wireframes\recommendations_wireframe_v6.html
C:\Users\User\Desktop\gads-data-layer\docs\wireframes\recommendations_all_tabs_v2.html
C:\Users\User\Desktop\gads-data-layer\docs\wireframes\campaigns_recommendations_tab.html
C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\recommendations.css
```

Read all 4 files in full before writing any code. The wireframes are the design authority.

---

## DELIVERABLES

### MODIFY (do not create from scratch — always read current file first):

**1.** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\recommendations.py`
Enrich the `/recommendations/cards` endpoint response with these additional fields per recommendation:
- `plain_english` — from rules table `plain_english` column
- `rule_or_flag` — from rules table `rule_or_flag` column (`rule` or `flag`)
- `rule_type` — derived from `action_type` using this mapping:
  - `increase_budget`, `decrease_budget`, `pacing_increase`, `pacing_reduction` → `budget`
  - `increase_troas`, `decrease_troas`, `increase_target_cpa`, `decrease_target_cpa`, `increase_max_cpc_cap`, `decrease_max_cpc_cap` → `bid`
  - `pause`, `enable` → `status`
  - keyword entity rules → `keyword`
  - shopping entity rules → `shopping`
- `conditions` — parsed from rules table `conditions` JSON as a list of plain English strings. Each condition object has `metric`, `op`/`operator`, `ref`/`unit`. Format each as e.g. `"ROAS (7d) ≥ 1.15× target"`, `"Clicks (7d) ≥ 30"`.
- `campaign_name` — the campaign name for the entity this recommendation is for
- `risk_level` — from rules table `risk_level` column
- `accepted_at` — already in DB, include in response
- `completed_at` — already in DB, include in response
- `cooldown_days` — from rules table `cooldown_days` column

Do NOT change any other endpoint in this file. Do not change `recommendation_accept`, `recommendation_decline`, `recommendations_run`, or any other route.

---

**2.** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\recommendations.html`
Full rewrite of `{% block content %}` only. Keep `{% extends "base_bootstrap.html" %}`, `{% block title %}`, `{% block extra_css %}` (add `recommendations.css` link here).

The new design has 4 status tabs: Pending / Monitoring / Successful / History.

**Pending tab columns:** ☐ · Type · Name · Campaign/s name · Rule name · Plain English · Rule/Flag · Rule type · Conditions · Action · Risk · Age · Accept/Decline buttons

**Monitoring tab columns:** ☐(empty) · Accepted · Monitoring progress · Type · Name · Campaign/s name · Rule name · Plain English · Rule/Flag · Rule type · Conditions · Action taken · Risk

**Successful tab columns:** ☐(empty) · Accepted · Completed · Type · Name · Campaign/s name · Rule name · Plain English · Rule/Flag · Rule type · Conditions · Action taken · Risk

**History tab columns:** ☐(empty) · Outcome · Date actioned · Type · Name · Campaign/s name · Rule name · Plain English · Rule/Flag · Rule type · Conditions · Action · Risk

**Expand row** on all tabs — 3 column grid: WHY THIS WAS TRIGGERED / Proposed change / Rule details (bullet list)

**Page header:** "Run Recommendations Engine" button + "Accept all low risk" button (hidden on non-Pending tabs)

**Entity filter pills on Pending:** All / Campaigns / Keywords / Ads / Shopping

**Bulk select bar:** appears when rows selected — Accept selected / Decline selected / Clear selection

Keep all existing Flask route calls and CSRF token handling.

---

**3.** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\campaigns.html`
Replace ONLY the content inside `<div class="tab-pane fade" id="recommendations-tab" role="tabpanel">`.
Do not touch anything outside that div.

Slim table — no Type column, no Campaign/s name column. Column header says "Campaign name".

**Pending:** ☐ · Campaign name · Rule name · Plain English · Rule/Flag · Rule type · Conditions · Action · Risk · Age · Accept/Decline
**Monitoring:** ☐(empty) · Accepted · Monitoring progress · Campaign name · Rule name · Plain English · Rule/Flag · Rule type · Conditions · Action taken · Risk
**Successful:** ☐(empty) · Accepted · Completed · Campaign name · Rule name · Plain English · Rule/Flag · Rule type · Conditions · Action taken · Risk
**History:** ☐(empty) · Outcome · Date actioned · Campaign name · Rule name · Plain English · Rule/Flag · Rule type · Conditions · Action · Risk

Tab header: "Campaign Recommendations" + subtitle + "View full recommendations page →" link + "Run Recommendations Engine" button + "Accept all low risk" button (hidden on non-Pending tabs).

---

**4.** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\keywords.html`
Same pattern as campaigns.html. Replace recommendations tab section ONLY.
Column header says "Keyword". Everything else identical to campaigns slim tab.

---

**5.** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\ads.html`
Same pattern. Column header says "Ad".

---

**6.** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\shopping.html`
Same pattern. Column header says "Product".

---

**7.** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\ad_groups.html`
Same pattern. Column header says "Ad group".

---

**8.** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_96_HANDOFF.md` — CREATE
**9.** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_96_SUMMARY.md` — CREATE

---

## CSS USAGE RULES

All new styles must use classes from `recommendations.css` with the `rec-` prefix.
Do NOT write inline styles for badges, action text, conditions, progress bars, expand rows or buttons.
Table wrapper, thead, th, td, pagination use existing `table-styles.css` classes unchanged.

Key classes:
- Type pills: `rec-type-pill rec-type-campaign` / `rec-type-keyword` / `rec-type-ad` / `rec-type-shopping`
- RF badge: `rec-rf-badge rec-rf-rule` / `rec-rf-badge rec-rf-flag`
- Rule type badge: `rec-rt-badge rec-rt-budget` / `rec-rt-bid` / `rec-rt-status` / `rec-rt-keyword` / `rec-rt-shopping`
- Action text: `rec-action-text rec-action-increase` / `rec-action-decrease` / `rec-action-pause`
- Action sub-line: `rec-action-sub`
- Risk: `rec-risk-badge rec-risk-low` / `rec-risk-medium` / `rec-risk-high`
- Conditions: `rec-conditions-cell` with `<span>` per condition line
- Human confirm: `rec-human-badge`
- Outcome: `rec-outcome-badge rec-outcome-declined` / `rec-outcome-reverted`
- Progress: `rec-progress-bg` / `rec-progress-fill` / `rec-progress-label`
- Expand row: `rec-expand-row` (add class `open` to show) / `rec-expand-grid` / `rec-expand-label` / `rec-expand-val`
- Row buttons: `rec-row-btn rec-row-btn-accept` / `rec-row-btn-decline`
- Bulk bar: `rec-bulk-bar`
- Column widths: `rec-col-cb` / `rec-col-type` / `rec-col-name` / `rec-col-campaigns` / `rec-col-rule` / `rec-col-plain` / `rec-col-ruleflag` / `rec-col-ruletype` / `rec-col-conditions` / `rec-col-action` / `rec-col-risk` / `rec-col-age` / `rec-col-date` / `rec-col-progress` / `rec-col-status` / `rec-col-acts`

---

## DO NOT TOUCH — HARD LIST

| File | Reason |
|------|--------|
| `act_dashboard/app.py` | Flask startup — any change risks breaking all routing |
| `act_dashboard/routes/campaigns.py` | Rules CRUD — not part of this job |
| `act_dashboard/routes/keywords.py` | Not part of this job |
| `act_dashboard/routes/ads.py` | Not part of this job |
| `act_dashboard/routes/shopping.py` | Not part of this job |
| `act_dashboard/routes/ad_groups.py` | Not part of this job |
| `act_dashboard/routes/outreach.py` | Not part of this job |
| `act_dashboard/routes/dashboard.py` | Not part of this job |
| `act_autopilot/recommendations_engine.py` | Already updated in Job 2 |
| `act_autopilot/rules_config.json` | Not part of this job |
| `act_lighthouse/features.py` | Already updated in Job 2 |
| `warehouse.duckdb` | Database — never touch |
| `warehouse_readonly.duckdb` | Database — never touch |
| `act_dashboard/static/css/table-styles.css` | Do not modify |
| `act_dashboard/static/css/custom.css` | Do not modify |
| `act_dashboard/static/css/rules.css` | Do not modify |
| `act_dashboard/static/css/navigation.css` | Do not modify |
| `act_dashboard/templates/base_bootstrap.html` | Do not modify |
| `act_dashboard/templates/components/rules_flags_tab.html` | Not part of this job |
| `act_dashboard/templates/components/rules_flow_builder.html` | Not part of this job |
| `act_dashboard/templates/components/navbar.html` | Not part of this job |
| All files in `tests/` | Do not modify tests |

---

## TECHNICAL CONSTRAINTS

1. Flask route decorators must be immediately adjacent to their functions — never insert helpers between a decorator and its function.
2. DuckDB string comparisons — always use `json_extract_string` not `JSON_EXTRACT`.
3. CSRF — `recommendation_accept`, `recommendation_decline`, `recommendations_run` are already exempted. Do not add or remove any CSRF exemptions.
4. All templates extend `base_bootstrap.html`. Bootstrap 5 only — no Bootstrap 4 classes.
5. Vanilla JS only — no jQuery.
6. Never use `{{ }}` Jinja braces inside `<script>` tags. Pass data via `data-` attributes or a dedicated `<script>` block using `json.dumps`.
7. DuckDB pattern: `duckdb.connect('warehouse.duckdb')` + `ATTACH 'warehouse_readonly.duckdb' AS ro`. Read from `ro.analytics.*`.
8. Entity type exact strings: `campaign`, `keyword`, `ad`, `shopping_product`, `ad_group`.

---

## ORDER OF WORK

1. Read all 4 wireframe/CSS files in full
2. Update `recommendations.py` — enrich endpoint data
3. Rewrite `recommendations.html` — full page all 4 tabs
4. Update `campaigns.html` — recommendations tab section only
5. Update `keywords.html` — recommendations tab section only
6. Update `ads.html` — recommendations tab section only
7. Update `shopping.html` — recommendations tab section only
8. Update `ad_groups.html` — recommendations tab section only
9. Verify all success criteria
10. Create handoff and summary docs

---

## SUCCESS CRITERIA

ALL must pass before reporting complete:

- [ ] Flask starts cleanly with no errors
- [ ] `/recommendations` loads — all 4 tabs visible and switchable
- [ ] Pending tab — all columns visible, no text cut off
- [ ] Entity filter pills filter correctly
- [ ] Bulk select bar appears when rows selected
- [ ] Accept / Decline buttons work with toast confirmation
- [ ] Click any row → expand row shows WHY THIS WAS TRIGGERED / Proposed change / Rule details
- [ ] Monitoring tab — progress bar column visible
- [ ] Successful tab — Accepted + Completed date columns visible
- [ ] History tab — Outcome badge + Date actioned columns visible
- [ ] "Run Recommendations Engine" button works
- [ ] "Accept all low risk" visible on Pending only, hidden on other tabs
- [ ] `/campaigns` Recommendations tab — slim table, no Type or Campaign/s name column
- [ ] `/keywords` Recommendations tab — slim table, column says "Keyword"
- [ ] `/ads` Recommendations tab — slim table, column says "Ad"
- [ ] `/shopping` Recommendations tab — slim table, column says "Product"
- [ ] `/ad-groups` Recommendations tab — slim table, column says "Ad group"
- [ ] All existing tabs on all pages still work (Campaigns table, Rules & Flags etc.)
- [ ] No console errors on any page

---

**Brief version:** 1.0 | **Master Chat:** 12 | **Date:** 2026-03-16
