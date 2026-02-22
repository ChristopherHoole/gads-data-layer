# CHAT 27 BRIEF — M6: Recommendations Engine + UI

**Module:** M6
**Scope:** Recommendations engine + Global Recommendations page + Campaigns Recommendations tab
**Approved wireframe:** M6_WIREFRAME_v5.html
**Last commit:** 025986a (M5 complete)

---

## MANDATORY FIRST STEP

Before doing anything, request 3 uploads from Christopher:

```
Before I begin, I need 3 mandatory uploads:

1. Codebase ZIP
   Location: C:\Users\User\Desktop\gads-data-layer
   (ZIP the entire folder and upload here)

2. PROJECT_ROADMAP.md
   Location: C:\Users\User\Desktop\gads-data-layer\docs\PROJECT_ROADMAP.md

3. CHAT_WORKING_RULES.md
   Location: C:\Users\User\Desktop\gads-data-layer\docs\CHAT_WORKING_RULES.md
```

Do not proceed until all 3 are uploaded.

---

## CONTEXT

M5 (Chat 26) built a card-based Rules tab on the Campaigns page backed by `rules_config.json`. The Recommendations tab on that page was left as a placeholder. M6 replaces that placeholder and builds the full recommendations system.

The dual-layer architecture is critical: `rules_config.json` is the UI config layer only. Python execution functions in `act_autopilot/rules/*.py` are **never touched**.

---

## WHAT CHAT 27 BUILDS

### Part 1: Recommendations Engine (backend)
- New Python module that reads `rules_config.json`, evaluates each enabled rule against `warehouse.duckdb` campaign data, and generates recommendations
- Stores results in a new DuckDB table: `recommendations` (in `warehouse.duckdb`, not the readonly DB)
- Manual trigger via "Run Recommendations Now" button (HTTP POST endpoint)
- No scheduled/automated execution in this chat — manual only

### Part 2: Global Recommendations Page
- Route: `/recommendations` (replaces the existing basic page)
- Template: `recommendations.html` extending `base_bootstrap.html`
- Summary strip: 4 cards (Pending count / Monitoring count / Success rate % / Last run time)
- 3 tabs: **Pending** | **Monitoring** | **History**
- Full design per M6_WIREFRAME_v5.html (approved)

### Part 3: Campaigns → Recommendations Tab
- Replaces the placeholder tab added in Chat 26
- Two sections: Pending (blue left border) + Monitoring (purple left border)
- 1-col card grid (narrower than global 2-col)
- "View full history →" link pointing to global `/recommendations?tab=history`
- "Run Recommendations Now" button

---

## DATABASE SCHEMA

### New table: `recommendations`
To be created in `warehouse.duckdb` (writable). Fields:

| Column | Type | Notes |
|---|---|---|
| rec_id | VARCHAR | UUID, primary key |
| rule_id | VARCHAR | e.g. "budget_1" |
| rule_type | VARCHAR | budget / bid / status |
| campaign_id | BIGINT | from warehouse |
| campaign_name | VARCHAR | resolved at generation time |
| status | VARCHAR | pending / monitoring / successful / reverted / declined |
| action_direction | VARCHAR | increase / decrease / hold / flag |
| action_magnitude | INTEGER | % change |
| current_value | FLOAT | budget/bid before change |
| proposed_value | FLOAT | calculated new value |
| trigger_summary | VARCHAR | human-readable "ROAS (7d) 6.2x > target × 1.15" |
| confidence | VARCHAR | high / medium / low |
| generated_at | TIMESTAMP | when the engine ran |
| accepted_at | TIMESTAMP | NULL until accepted (Chat 28) |
| monitoring_ends_at | TIMESTAMP | NULL until accepted (Chat 28) |
| resolved_at | TIMESTAMP | NULL until resolved |
| outcome_metric | FLOAT | metric value at resolution |
| created_at | TIMESTAMP | row created |
| updated_at | TIMESTAMP | last updated |

---

## RECOMMENDATIONS ENGINE LOGIC

For each enabled rule in `rules_config.json`:
1. Query `ro.analytics.campaign_daily` for recent data (match date window to condition metric: 7d or 30d)
2. Evaluate `condition_metric` against `condition_operator` + `condition_value`
3. If condition_2 exists, evaluate that too (AND logic)
4. If both conditions pass AND no existing `pending` recommendation exists for this campaign+rule combination:
   - Calculate `proposed_value` (current value ± action_magnitude %)
   - Generate human-readable `trigger_summary`
   - Assign confidence (use rule's risk_level as proxy: low=high confidence, medium=medium, high=low)
   - Insert new row into `recommendations` table with status = `pending`
5. Log how many recommendations were generated

### Condition metrics to support:
- `roas_7d` — 7-day ROAS vs target
- `roas_30d` — 30-day ROAS vs target
- `clicks_7d` — 7-day click count
- `conversions_30d` — 30-day conversion count
- `cost_spike_confidence` — boolean flag (gte 0.6 = True)
- `cost_drop_detected` — boolean flag (gte 1 = True)
- `pace_over_cap_detected` — boolean flag (gte 1 = True)
- `cost_cv_14d` — 14-day cost coefficient of variation
- `cvr_drop_detected` — boolean flag (gte 1 = True)
- `ctr_drop_detected` — boolean flag (gte 1 = True)

**For synthetic/test data:** Boolean flag metrics will not exist as real columns — handle gracefully with a fallback (skip the rule, do not error).

**`x_target` unit:** The condition_value is a multiplier of the campaign's tROAS/tCPA target. Worker must confirm where target ROAS is stored in the schema (diagnostic question 1).

---

## CARD DESIGN (LOCKED — match v5 exactly)

### Card anatomy (order is mandatory):
1. 4px coloured top bar (blue=budget, green=bid, red=status; monitoring = blue→purple gradient)
2. Header row: rule tag + campaign name (left) + status pill (right)
3. **Change block** — gradient background, icon, main text ("Increase daily budget by 10%"), sub text ("£450 → £495 · 7-day cooldown after")
4. **Trigger block** — grey background, "Why this triggered" label, condition values in monospace pill boxes
5. Footer row 1: confidence badge + source pill ("Campaigns") + timestamp + "Buttons active in Chat 28" (right-aligned, amber)
6. Footer row 2: Modify / Decline / Accept buttons full-width (disabled placeholders — Chat 28 wires them)

### Monitoring card differences:
- Replaces trigger block + action buttons with monitoring block
- Monitoring block: purple background, "Monitoring period" label + "Day X of Y" (right), progress bar, two outcome pills
- Footer: confidence badge + source pill + accepted date + "X days remaining" (right, purple)
- No action buttons on monitoring cards

### Status pill colours:
- Pending → `sp-pending` (blue: `#dbeafe` / `#1d4ed8`)
- Monitoring → `sp-monitoring` (purple: `#ede9fe` / `#6d28d9`)
- Successful → `sp-success` (green: `#dcfce7` / `#15803d`)
- Reverted → `sp-reverted` (red: `#fee2e2` / `#991b1b`)
- Declined → `sp-declined` (grey: `#f3f4f6` / `#6b7280`)

---

## HISTORY TABLE (locked)

Columns: Date | Rule | Campaign | Change Applied | Outcome | Result

- Rule column: coloured link matching rule type (blue=budget, green=bid, red=status)
- Outcome column: coloured dot + text (Monitoring=purple, Successful=green, Reverted=red, Declined=grey)
- Result column: coloured text ("ROAS +18% after 7d" green / "ROAS −12% after 5d" red / "User declined" grey / "—" for monitoring)
- Success rate banner above table: green background, "75% success rate (30d) — 9 of 12 accepted recommendations were successful"
- Filter bar: All | Successful | Reverted | Declined | Monitoring

---

## SYNTHETIC DATA REQUIREMENT

The engine will generate real recommendations from `warehouse.duckdb`. The worker must also seed **historical recommendations** (past 30 days) into the `recommendations` table so the History and Monitoring tabs are not empty on first run. Seeded data must include a mix of: Successful, Reverted, Declined, and Monitoring statuses.

---

## FILE PATHS (FULL WINDOWS PATHS)

### Files to CREATE:
- `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\recommendations.py`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\recommendations.html`

### Files to MODIFY:
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\__init__.py`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\campaigns.html`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\base_bootstrap.html` (sidebar badge)

---

## CRITICAL CONSTRAINTS

- Always extend `base_bootstrap.html` (NEVER `base.html`)
- Always use `ro.analytics.*` prefix for readonly queries
- Writable tables go to `warehouse.duckdb` directly (not the readonly DB)
- Inline SVG only — NO Bootstrap Icons CDN
- Never insert helper functions between `@bp.route` decorator and its `def` — they must be adjacent
- Always use full Windows paths
- `rules_config.json` path needs `.parent.parent.parent` (routes/ is 3 levels from project root)

---

## DIAGNOSTIC QUESTIONS

**Sequence:**
1. Worker receives the 3 mandatory uploads (codebase ZIP, PROJECT_ROADMAP.md, CHAT_WORKING_RULES.md)
2. Worker reads this brief in full
3. Worker explores the codebase ZIP thoroughly
4. Worker reads PROJECT_ROADMAP.md and CHAT_WORKING_RULES.md
5. **Only then** — worker formulates exactly 5 diagnostic questions based on their own findings and gaps
6. Christopher pastes the 5 questions to Master Chat — Master answers
7. Worker writes build plan — Christopher pastes to Master Chat for approval
8. Only after approval does work begin

Questions must come entirely from the worker's own analysis. Do not ask questions already answered in this brief or the docs.

---

## ACCEPTANCE CRITERIA

Chat 27 is complete when all of the following are confirmed working on `Synthetic_Test_Client`:

1. ✅ "Run Recommendations Now" generates new recommendations from `rules_config.json` rules
2. ✅ Global Recommendations page loads — all 3 tabs render with data
3. ✅ Pending tab shows 2-col card grid with correct card anatomy (change first, trigger second)
4. ✅ Monitoring tab shows progress bars and outcome pills
5. ✅ History tab shows success rate banner + full table with filter bar
6. ✅ Campaigns → Recommendations tab loads with 1-col cards (not the placeholder)
7. ✅ "View full history →" link navigates to global History tab
8. ✅ Recommendations persist in DuckDB after page reload
9. ✅ Running engine twice does not create duplicate `pending` recommendations for same campaign+rule
10. ✅ Seeded historical data visible in History tab on first load

---

## WORKFLOW (MANDATORY — NO EXCEPTIONS)

```
Worker sends 5 diagnostic questions
        ↓
Christopher pastes questions to Master Chat → Master answers
        ↓
Worker writes detailed build plan
        ↓
Christopher pastes plan to Master Chat → Master approves
        ↓
Worker builds FILE 1 → Christopher tests → reports result to Master
        ↓
Master confirms → Worker builds FILE 2 → test → confirm
        ↓
... repeat for every file ...
        ↓
All files tested → Worker produces handoff docs → Master approves commit
```

**ONE FILE AT A TIME. Test and confirm before proceeding to the next file. No exceptions.**

---

## DELIVERABLES (in order — one at a time)

1. 5 diagnostic questions → paste to Master Chat for answers
2. Detailed build plan → paste to Master Chat for approval
3. DB migration/seed script → **TEST** → confirm with Master
4. `recommendations_engine.py` → **TEST** → confirm with Master
5. `recommendations.py` Blueprint → **TEST** → confirm with Master
6. `recommendations.html` template → **TEST** → confirm with Master
7. Modified `campaigns.html` → **TEST** → confirm with Master
8. Modified `__init__.py` → **TEST** → confirm with Master
9. Modified `base_bootstrap.html` (if needed) → **TEST** → confirm with Master
10. `CHAT_27_DETAILED_SUMMARY.md`
11. `CHAT_27_HANDOFF.md` → Master approves git commit

---

**End of Chat 27 Brief**
**Created by:** Master Chat 3.0
**Date:** 2026-02-22
**Git state at brief creation:** 025986a — M5 complete, M6 next
