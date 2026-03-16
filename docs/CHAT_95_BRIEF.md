# CHAT 95: Recommendations Engine — DB Source of Truth (Campaign Rules)

**Date:** 2026-03-15
**Estimated Time:** 2–3 hours
**Priority:** HIGH
**Dependencies:** Job 1 complete (DB rules reviewed, locked, correct) ✅

---

## CONTEXT

The recommendations engine (`act_autopilot/recommendations_engine.py`) currently reads campaign rules from `act_autopilot/rules_config.json`. This JSON is a first-draft system that predates the DB rules overhaul. The DB now has 22 well-structured campaign rules with proper campaign_type_lock, reviewed thresholds, and correct conditions. The JSON and DB are out of sync and the JSON must be retired for campaign rules.

Non-campaign rules (keyword, ad_group, ad, shopping) remain in the JSON for now — those entity types haven't been through their review phase yet. They will be migrated to DB in a future chat.

---

## OBJECTIVE

Rewrite `recommendations_engine.py` so that campaign rules are loaded from the DB `rules` table instead of `rules_config.json`. All other entity types (keyword, ad_group, ad, shopping) continue reading from JSON unchanged.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py` — MODIFY
   - Campaign rules loaded from DB `rules` table
   - Non-campaign rules still loaded from JSON
   - campaign_type_lock filtering implemented with graceful fallback
   - Both condition schemas handled (`op`/`ref` and `operator`/`unit`)
   - action_type mapped correctly to engine action_direction expectations
   - All existing engine functionality preserved

2. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_95_HANDOFF.md` — CREATE
3. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_95_SUMMARY.md` — CREATE

---

## REQUIREMENTS

### DB Rules Schema
Read from `warehouse.duckdb` table `rules`:
```sql
SELECT id, name, entity_type, rule_or_flag, type, campaign_type_lock,
       conditions, action_type, action_magnitude, cooldown_days, risk_level,
       enabled, plain_english
FROM rules
WHERE entity_type = 'campaign'
  AND rule_or_flag = 'rule'
  AND is_template = FALSE
  AND enabled = TRUE
```

### Condition Schema — Handle Both Formats
Conditions are stored as a JSON array. Two schemas exist:

Format A (newer): `{"metric": "roas_7d", "op": "gte", "value": "1.15", "ref": "x_target"}`
Format B (older): `{"metric": "roas_7d", "operator": ">=", "value": 0.85, "unit": "x_target"}`

Normalisation:
- `op` = `cond.get("op") or _normalise_operator(cond.get("operator"))`
- `ref` = `cond.get("ref") or cond.get("unit")`
- `value` = always cast to float

Operator normalisation map:
```python
OP_MAP = {">": "gt", ">=": "gte", "<": "lt", "<=": "lte", "=": "eq", "==": "eq"}
```

### campaign_type_lock Filtering
The features table does NOT have a bidding strategy column yet. Implement as follows:
- Lock = `'all'` → rule fires for all campaigns (no filter)
- Lock = `'troas'`, `'tcpa'`, `'max_clicks'` → attempt to match against a `bidding_strategy` column in features if it exists, otherwise **fire for all campaigns** (graceful fallback — log a warning)
- Add a TODO comment noting that proper lock enforcement requires `bidding_strategy` column in `campaign_features_daily`

### action_type Mapping
DB uses `action_type`. Engine uses `action_direction` internally. Map as follows:
```python
ACTION_MAP = {
    "increase_budget":     "increase",
    "decrease_budget":     "decrease",
    "increase_troas":      "increase",
    "decrease_troas":      "decrease",
    "increase_target_cpa": "increase",
    "decrease_target_cpa": "decrease",
    "increase_max_cpc":    "increase",
    "decrease_max_cpc":    "decrease",
    "pause":               "pause",
    "flag":                "flag",
    "hold":                "hold",
}
```

### Rule ID Format
DB uses integer `id`. Engine uses string `rule_id` for deduplication and recommendations table.
Convert: `rule_id = f"db_campaign_{row['id']}"` — this distinguishes DB-sourced rules from JSON rules.

### Cooldown Enforcement
The engine currently does NOT enforce cooldowns — it only checks for existing pending recommendations. This is unchanged. Cooldown enforcement is a future task.

### Non-Campaign Rules — Unchanged
JSON loading for keyword, ad_group, ad, shopping rules must remain exactly as-is. Do not modify that code path. Only the campaign entity loading changes.

### Backward Compatibility
The `recommendations` table insert must continue to work. The `rule_id` field will now contain `db_campaign_N` format strings for campaign rules. This is fine — no schema change needed.

---

## CONSTRAINTS

- Never use bare `except Exception: pass` — always log: `except Exception as e: print(f"[ENGINE] error: {e}")`
- Always open DB connection before any query that uses it
- Use `json.loads()` safely — wrap in try/except per condition row
- Do not modify `features.py`, `celery_app.py`, `radar.py`, or any other file
- Do not run git commands

---

## SUCCESS CRITERIA

- [ ] Flask starts cleanly with no errors
- [ ] Running the engine produces `[ENGINE] Loaded N campaign rules from DB` in output
- [ ] Non-campaign rules still load from JSON (confirmed by `[ENGINE] Loaded N rules from rules_config.json` for keyword/shopping etc.)
- [ ] At least one campaign recommendation generates (or engine reports skipped_no_data if features table is empty — both are acceptable)
- [ ] No `KeyError` or `AttributeError` in engine output
- [ ] `audit_rules_full.py` still runs cleanly from project root

---

## REFERENCE FILES

- `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py` — file to modify
- `C:\Users\User\Desktop\gads-data-layer\act_autopilot\rules_config.json` — JSON source (non-campaign rules still read from here)
- `C:\Users\User\Desktop\gads-data-layer\audit_rules_full.py` — shows exact DB schema and condition formats

---

## TESTING

1. Run `python act_autopilot/recommendations_engine.py` directly (or trigger via dashboard)
2. Confirm output shows DB rules loading for campaign entity
3. Confirm JSON rules still loading for keyword/shopping/ad/ad_group
4. Confirm no errors in Flask terminal
5. Report exact engine output including generated/skipped counts
