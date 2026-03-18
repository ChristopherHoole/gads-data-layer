# CHAT 101: Flags System — Engine, DB, Routes, UI

**Date:** 2026-03-18
**Priority:** HIGH
**Estimated Time:** 5–7 hours
**Dependencies:** Chats 97-100 complete ✅

---

## CONTEXT

Flags are performance anomaly alerts, distinct from recommendations. They detect issues (ROAS Drop, CPA Spike, Zero Conversions etc.) without proposing a change. The rules table already has 30 flag rows (`rule_or_flag = 'flag'`). The recommendations engine currently only processes `rule_or_flag = 'rule'` — flags have never been evaluated. This chat builds the complete flags system end-to-end.

A wireframe has been approved at:
`C:\Users\User\Desktop\gads-data-layer\docs\flags_wireframe.html`
Open it in a browser to verify UI before building.

---

## OBJECTIVE

Build the flags system: DB table, engine loop, backend routes, and UI tabs/subtabs on all relevant pages.

---

## BUILD PLAN

### PART 1 — DATABASE

**File:** `C:\Users\User\Desktop\gads-data-layer\scripts\create_flags_table.py` — CREATE + RUN IMMEDIATELY

Create the `flags` table in `warehouse.duckdb`:

```sql
CREATE TABLE IF NOT EXISTS flags (
    flag_id         VARCHAR PRIMARY KEY,
    rule_id         VARCHAR,
    rule_name       VARCHAR,
    entity_type     VARCHAR,
    entity_id       VARCHAR,
    entity_name     VARCHAR,
    customer_id     VARCHAR,
    status          VARCHAR DEFAULT 'active',
    severity        VARCHAR,
    trigger_summary VARCHAR,
    plain_english   VARCHAR,
    conditions      VARCHAR,
    generated_at    TIMESTAMP,
    acknowledged_at TIMESTAMP,
    snooze_until    TIMESTAMP,
    snooze_days     INTEGER,
    updated_at      TIMESTAMP
)
```

Run the script immediately after creating it. Print confirmation and row count.

---

### PART 2 — ENGINE

**File:** `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py` — MODIFY

Add `_run_flag_engine(conn, customer_id)` function:

- Queries rules table: `WHERE rule_or_flag = 'flag' AND enabled = TRUE AND is_template = FALSE`
- Uses same `CAMPAIGN_METRIC_MAP` and `_evaluate_condition()` as rules engine — do NOT duplicate logic
- Uses same `MAX(snapshot_date) WHERE name_col IS NOT NULL` entity data query pattern (Chat 100 fix)
- Duplicate check: skip if flag with same `rule_id + entity_id + customer_id` already exists with `status = 'active'` OR (`status = 'snoozed'` AND `snooze_until > NOW()`)
- Generates `flag_id` using `str(uuid.uuid4())`
- Sets `severity` from `risk_level` on the rule row
- Sets `plain_english` from `plain_english` on the rule row
- Inserts into `flags` table with `status = 'active'`, `generated_at = NOW()`, `updated_at = NOW()`
- Prints `[FLAGS ENGINE] Generated: {rule_id} | {entity_type} {entity_id} | severity={severity}`
- Prints `[FLAGS ENGINE] Done. Generated={n} | SkippedDuplicate={n} | SkippedNoData={n}`

Call `_run_flag_engine(conn, customer_id)` at the END of the existing `run_recommendations()` function, after the rules engine loop completes.

---

### PART 3 — BACKEND ROUTES

**File:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\recommendations.py` — MODIFY

Add 3 new routes:

**`GET /flags/cards`**

Before returning, update any snoozed flags where `snooze_until <= NOW()` to `status = 'history'` and `updated_at = NOW()`.

Returns JSON:
```json
{
  "active":  [...],
  "snoozed": [...],
  "history": [...]
}
```

Each flag dict includes: `flag_id`, `rule_id`, `rule_name`, `entity_type`, `entity_id`, `entity_name`, `customer_id`, `status`, `severity`, `trigger_summary`, `plain_english`, `conditions`, `generated_at`, `acknowledged_at`, `snooze_until`, `snooze_days`, `updated_at`, plus a computed `generated_ago` age label (e.g. "2m ago", "3d ago").

Filter by `customer_id` from `get_current_config()`.

**`POST /flags/<flag_id>/acknowledge`**

Reads `cooldown_days` from rules table using the flag's `rule_id` (extract integer from `db_campaign_N`).
Sets:
- `status = 'snoozed'`
- `acknowledged_at = NOW()`
- `snooze_until = NOW() + cooldown_days`
- `snooze_days = 0`
- `updated_at = NOW()`

Returns `{"success": true, "new_status": "snoozed"}`.

**`POST /flags/<flag_id>/ignore`**

Accepts JSON body `{"days": 7|14|30}`.
Sets:
- `status = 'snoozed'`
- `acknowledged_at = NOW()`
- `snooze_until = NOW() + days`
- `snooze_days = days`
- `updated_at = NOW()`

Returns `{"success": true, "new_status": "snoozed", "snooze_days": days}`.

**CSRF exemptions** — add all 3 routes to app.py CSRF exemption list with comment `# [Chat 101] Flags routes`.

---

### PART 4 — UI

#### 4a. Main Recommendations page
**File:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\recommendations.html` — MODIFY

**Step 1:** Add Flags tab to the existing `#recStatusTabs` nav:
```html
<li class="nav-item" role="presentation">
  <button class="nav-link" id="tab-btn-flags" data-tab="flags" role="tab" type="button">
    Flags <span class="badge ms-1" style="background:#ea4335;" id="badge-flags">0</span>
  </button>
</li>
```

**Step 2:** Add `#panel-flags` div after the existing `#panel-history` div:

Structure inside `#panel-flags`:

```
Entity filter pills: All / Campaigns / Ad Groups / Keywords / Ads / Shopping
Count label: "N active flags"

ACTIVE FLAGS TABLE — columns:
  Type | Name | Campaign/s name | Flag name | Plain English | Rule/Flag | Severity | Age | Actions

Each row clickable — expand row shows:
  Why this was triggered | Flag details | Rule details
  (same 3-column rec-expand-grid pattern as existing recommendations)

Actions column — Bootstrap dropdown button:
  Acknowledge
  ─────────────
  Ignore 7 days
  Ignore 14 days
  Ignore 30 days

SNOOZED SECTION — collapsible (▶ Snoozed [count])
  Same columns as Active + "Snoozed until" column
  Actions dropdown on every row (same options)
  Expand row same pattern

HISTORY SECTION — collapsible (▶ History [count])
  Same columns as Active + "Actioned" date column
  Actions dropdown on every row (same options)
  Expand row same pattern
```

**Step 3:** Add JS to load `/flags/cards` and render all three sections. Use the same `esc()`, `typePill()`, `rfBadge()`, `fmtDate()`, `ageLabel()` helpers already defined on the page. Add `flagsAction(flag_id, action, days)` function that POSTs to `/flags/<flag_id>/acknowledge` or `/flags/<flag_id>/ignore` with `{days}`, then refreshes the flags panel.

Tab switching: hook into the existing tab switching JS — when `#tab-btn-flags` is clicked, load `/flags/cards` and render.

**Step 4:** Wire up entity filter pills to filter the active flags table client-side by `entity_type`.

---

#### 4b–4f. Entity pages — Flags subtab

Apply the same pattern to all 5 entity pages:

| File | Entity filter | ID prefix |
|------|--------------|-----------|
| `act_dashboard/templates/campaigns.html` | `entity_type === 'campaign'` | `cam-flag` |
| `act_dashboard/templates/ad_groups.html` | `entity_type === 'ad_group'` | `ag-flag` |
| `act_dashboard/templates/keywords.html` | `entity_type === 'keyword'` | `kw-flag` |
| `act_dashboard/templates/ads.html` | `entity_type === 'ad'` | `ad-flag` |
| `act_dashboard/templates/shopping.html` | `entity_type === 'shopping'` | `sh-flag` |

**For each entity page:**

1. Add "Flags" button to the existing inner tabs nav (e.g. `#camRecTabs`):
```html
<button class="nav-link" id="{prefix}-tab" ...>
  Flags <span class="badge ms-1" style="background:#ea4335;" id="{prefix}-badge">0</span>
</button>
```

2. Add `#{prefix}-panel` tab pane with a single table — **no Snoozed/History sections on entity pages** (active flags only):

Columns for entity pages (no Type column — all same entity):
`Name | Flag name | Plain English | Rule/Flag | Severity | Age | Actions`

3. Load from `/flags/cards`, filter client-side by `entity_type`, render active flags only.

4. Same Actions dropdown and expand row as main Recommendations page.

---

### PART 5 — CSS

**File:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\recommendations.css` — MODIFY

Add severity badge styles (dot + coloured label, matching existing `.rec-risk-*` pattern):

```css
.flag-sev-badge { display: inline-flex; align-items: center; gap: 4px; font-size: 13px; font-weight: 500; }
.flag-sev-high::before   { content: '●'; font-size: 10px; color: #ea4335; }
.flag-sev-medium::before { content: '●'; font-size: 10px; color: #fbbc05; }
.flag-sev-low::before    { content: '●'; font-size: 10px; color: #34a853; }
.flag-sev-high   { color: #c5221f; }
.flag-sev-medium { color: #b45309; }
.flag-sev-low    { color: #137333; }
```

Note: `.rec-rf-flag` and `.rec-type-*` pills already exist in recommendations.css — reuse them, do not redefine.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\scripts\create_flags_table.py` — CREATE + RUN
2. `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py` — MODIFY
3. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\recommendations.py` — MODIFY
4. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — MODIFY (CSRF exemptions only)
5. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\recommendations.html` — MODIFY
6. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\campaigns.html` — MODIFY
7. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\ad_groups.html` — MODIFY
8. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\keywords.html` — MODIFY
9. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\ads.html` — MODIFY
10. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\shopping.html` — MODIFY
11. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\recommendations.css` — MODIFY
12. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_101_HANDOFF.md` — CREATE

---

## REQUIREMENTS

- Read every file before editing
- `flags` table is SEPARATE from `recommendations` table — never modify recommendations table
- Flag engine uses existing `CAMPAIGN_METRIC_MAP` and `_evaluate_condition()` — no logic duplication
- `_run_flag_engine()` MUST use the `MAX(snapshot_date) WHERE name IS NOT NULL` pattern (Chat 100 fix)
- Duplicate prevention: flag must not re-fire if already active or within snooze window
- Entity pages show active flags only — no Snoozed/History sections
- Main Recommendations page shows Active + collapsible Snoozed + collapsible History
- All new routes CSRF exempted
- Bootstrap 5 only — no jQuery
- Reuse existing CSS classes where possible (rec-rf-flag, rec-type-*, rec-expand-grid etc.)
- Wireframe reference: `C:\Users\User\Desktop\gads-data-layer\docs\flags_wireframe.html`

---

## SUCCESS CRITERIA

- [ ] `flags` table exists in `warehouse.duckdb`
- [ ] Running engine with Conversion Drop flag (id=33) enabled generates rows in flags table
- [ ] `/flags/cards` returns correct JSON with active/snoozed/history groups
- [ ] Flags tab visible on main Recommendations page with correct badge count
- [ ] Active flags table shows Type | Name | Campaign/s name | Flag name | Plain English | Rule/Flag | Severity | Age | Actions
- [ ] Snoozed section collapsible with correct columns including "Snoozed until"
- [ ] History section collapsible with correct columns including "Actioned" date
- [ ] Actions dropdown works on Active, Snoozed and History rows
- [ ] Expand row works on all flag rows
- [ ] Flags subtab visible on Campaigns, Ad Groups, Keywords, Ads, Shopping pages
- [ ] Entity page flags subtabs show active flags only for that entity type
- [ ] Acknowledge moves flag to snoozed using flag's own cooldown_days
- [ ] Ignore 7/14/30 days moves flag to snoozed with correct snooze_until
- [ ] Re-running engine does not duplicate active/snoozed flags
- [ ] Flask starts cleanly
- [ ] No console errors

---

## TESTING

```
1. python scripts/create_flags_table.py — confirm table created
2. Enable Conversion Drop flag (id=33) in Rules & Flags tab
3. Run Recommendations Now
4. Check Flags tab on Recommendations page — confirm flag appears with correct data
5. Click row to expand — confirm trigger summary shows
6. Click Actions → Acknowledge — confirm moves to Snoozed section
7. Click Actions → Ignore 14 days on another — confirm snooze_until = today + 14
8. Check Snoozed section expanded — confirm correct columns and Actions dropdown
9. Re-run engine — confirm no duplicate flags created
10. Check Flags subtab on Campaigns page — confirm campaign flags show
11. Check Flags subtab on Ad Groups, Keywords, Ads, Shopping pages
12. Confirm Flask log shows [FLAGS ENGINE] output
```
