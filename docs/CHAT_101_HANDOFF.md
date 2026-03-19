# Chat 101 Handoff — Flags System

## What was built

A complete end-to-end **Flags system** — performance anomaly alerts separate from the Recommendations system. Flags alert on problems without proposing an action.

---

## DB

**Table:** `flags` (in `warehouse.duckdb`)

| Column | Type | Notes |
|---|---|---|
| `flag_id` | VARCHAR PK | UUID |
| `rule_id` | VARCHAR | e.g. `db_campaign_42` |
| `rule_name` | VARCHAR | Display name |
| `entity_type` | VARCHAR | campaign / ad_group / keyword / ad / shopping |
| `entity_id` | VARCHAR | |
| `entity_name` | VARCHAR | |
| `customer_id` | VARCHAR | |
| `status` | VARCHAR | active / snoozed / history |
| `severity` | VARCHAR | high / medium / low |
| `trigger_summary` | VARCHAR | What triggered it |
| `plain_english` | VARCHAR | Human-readable description |
| `conditions` | VARCHAR | JSON array of condition strings |
| `generated_at` | TIMESTAMP | |
| `acknowledged_at` | TIMESTAMP | Set on acknowledge |
| `snooze_until` | TIMESTAMP | Set on snooze |
| `snooze_days` | INTEGER | 0 = cooldown-based acknowledge, 7/14/30 = manual snooze |
| `updated_at` | TIMESTAMP | |

Created by: `scripts/create_flags_table.py`

---

## Engine

**File:** `act_autopilot/recommendations_engine.py`

Function `_run_flag_engine(conn, customer_id)` is called at the end of `run_recommendations_engine()` (before `conn.close()`).

**How it works:**
1. Queries `rules` WHERE `rule_or_flag='flag' AND enabled=TRUE AND is_template=FALSE`
2. Groups rules by `entity_type`
3. Loads existing active/snoozed `(rule_id, entity_id)` pairs into a skip set (duplicate prevention)
4. For each entity type, queries data via `MAX(snapshot_date) WHERE name_col IS NOT NULL`
5. Evaluates conditions using shared `_evaluate()` function
6. Inserts new flags with `uuid4()` as `flag_id`

**Rule ID format:** `db_campaign_{id}` (for all entity types — consistent with recommendations engine)

**Print output:**
```
[FLAGS ENGINE] Generated: db_campaign_42 | campaign abc123 | severity=high
[FLAGS ENGINE] Done. Generated=3 | SkippedDuplicate=2 | SkippedNoData=0
```

---

## Routes

**File:** `act_dashboard/routes/recommendations.py`

| Route | Method | Description |
|---|---|---|
| `/flags/cards` | GET | Returns `{active, snoozed, history}` lists; expires snoozed→history server-side |
| `/flags/<flag_id>/acknowledge` | POST | Snoozes for `cooldown_days` from the rule; `snooze_days=0` |
| `/flags/<flag_id>/ignore` | POST | Snoozes for `days` (7/14/30); body: `{"days": N}` |

All three routes are CSRF exempt (added in `app.py`).

**Helper functions added:**
- `_age_label(dt)` — returns "2h ago", "3d ago" etc.
- `_serialise_flag(row_dict)` — converts a DB row to JSON-ready dict

---

## CSS

**File:** `act_dashboard/static/css/recommendations.css`

Severity badges appended at end of file:
```css
.flag-sev-badge        /* container */
.flag-sev-high         /* red dot + text */
.flag-sev-medium       /* amber dot + text */
.flag-sev-low          /* green dot + text */
```

---

## UI

### `recommendations.html` — Full flags page
- **Flags tab** added to `#recStatusTabs` nav with red badge
- **`#panel-flags`** contains:
  - Entity filter pills (All / Campaigns / Ad Groups / Keywords / Ads / Shopping)
  - Active flags table (9 cols: Type | Name | Campaigns | Flag name | Plain English | Rule/Flag | Severity | Age | Actions)
  - Collapsible Snoozed section (+ Snoozed until column)
  - Collapsible History section (+ Actioned column)
- **JS functions:** `loadFlags()`, `renderFlags()`, `flagsAction()`, `flagsToggleSection()`, `sevBadge()`, `flagActionsDropdown()`, `flagRowMain()`, `flagRowSnoozed()`, `flagRowHistory()`, `toggleFlagExpand()`
- `TABS` array updated to include `'flags'`

### Entity pages — Active flags only (no Snoozed/History sections)

| Template | Prefix | Entity type | Tab control |
|---|---|---|---|
| `campaigns.html` | `cam-flag` | campaign | Bootstrap 5 `data-bs-toggle="tab"` |
| `ad_groups.html` | `ag-flag` | ad_group | Bootstrap 5 `data-bs-toggle="tab"` |
| `keywords.html` | `kw-flag` | keyword | `kwSwitchTab()` |
| `ads.html` | `ad-flag` | ad | `adSwitchTab()` |
| `shopping.html` | `shop-flag` | shopping | `shopSwitchTab()` |

Each entity page:
1. Adds a **Flags** button to the inner tab nav with a red badge
2. Adds a `{prefix}-panel` / `{prefix}-pane-flags` div with a 6-column table (Name | Flag name | Plain English | Severity | Age | Actions)
3. Fetches `/flags/cards`, filters by `entity_type`, renders active flags only
4. Actions: Acknowledge (uses rule cooldown) or Snooze 7/14/30 days

---

## Testing

1. **Engine:** Add a flag-type rule in Rules & Flags, run engine via "Run engine" button → check `[FLAGS ENGINE]` output in terminal
2. **API:** `curl http://localhost:5000/flags/cards` → should return `{active:[], snoozed:[], history:[]}`
3. **UI:** Navigate to `/recommendations` → click Flags tab → should show active flags
4. **Acknowledge:** Click Acknowledge on a flag → badge count decreases, flag moves to Snoozed
5. **Snooze expiry:** Set `snooze_until` to a past timestamp in DuckDB → next `/flags/cards` call transitions to history
6. **Entity pages:** Visit `/campaigns` → Recommendations tab → Flags subtab → should show campaign-scoped flags

---

## Known behaviour

- Flag engine runs after recommendations engine on the same `run_recommendations_engine()` call
- Duplicate prevention: active OR snoozed flags for the same `(rule_id, entity_id)` are skipped
- Snooze expiry runs server-side in `/flags/cards` — no background task needed
- `acknowledge` uses `cooldown_days` from the rule (defaults to 7 if not set)
- Entity pages show active flags only; full Snoozed + History is only on `/recommendations` Flags tab
