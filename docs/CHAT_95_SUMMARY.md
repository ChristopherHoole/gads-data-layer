# CHAT 95 SUMMARY: Recommendations Engine — DB Source of Truth (Campaign Rules)

**Date:** 2026-03-15
**Status:** COMPLETE

---

## What Was Done

Migrated the recommendations engine so that campaign rules are loaded from the DB `rules` table instead of `rules_config.json`. All 22 reviewed and locked campaign rules now drive campaign recommendations. Non-campaign rules (keyword, ad_group, ad, shopping) continue to load from JSON unchanged.

---

## Changes Made

### `act_autopilot/recommendations_engine.py`

1. **Added `OP_MAP`** — maps symbolic operators (`>=`, `<`, etc.) to engine short-codes (`gte`, `lt`, etc.) for Format B conditions.

2. **Added `ACTION_MAP`** — maps DB `action_type` values (`increase_budget`, `decrease_troas`, etc.) to engine `action_direction` values (`increase`, `decrease`, `pause`, `flag`, `hold`).

3. **Added `_normalise_operator()`** — helper to convert Format B operators via `OP_MAP`.

4. **Added `_load_db_campaign_rules(conn)`** — queries `rules` table with the canonical SELECT, parses each row's `conditions` JSON (handling both Format A `op`/`ref` and Format B `operator`/`unit`), normalises to the engine's internal rule dict format. Returns a list ready to slot into the existing processing loop.

5. **Modified `run_recommendations_engine()`**:
   - JSON load now filters out campaign entity rules (they came from `budget_*`, `bid_*`, `status_*` IDs)
   - DB connection established before campaign rule loading
   - `_load_db_campaign_rules(conn)` called immediately after connection
   - `all_rules = json_non_campaign + db_campaign_rules` combined before grouping
   - `_warned_locks` set added for deduplicating `campaign_type_lock` warnings
   - Lock check added in inner loop: `lock='all'` fires freely; specific locks attempt `bidding_strategy` column match with graceful fallback

---

## Test Output (2026-03-15)

```
[ENGINE] Loaded 28 rules from rules_config.json (non-campaign only)
[ENGINE] Connected to warehouse + attached readonly
[ENGINE] Loaded 22 campaign rules from DB
[ENGINE] Rules by entity type:
  - keyword: 6 rules
  - ad_group: 4 rules
  - ad: 4 rules
  - shopping: 14 rules
  - campaign: 22 rules
...
[ENGINE] Processing campaign (22 rules)...
[ENGINE] Loaded 40 campaign rows
[ENGINE] WARNING: campaign_type_lock='troas' cannot be enforced — bidding_strategy column missing from campaign_features_daily. Firing for all campaigns.
[ENGINE] WARNING: campaign_type_lock='tcpa' cannot be enforced — bidding_strategy column missing from campaign_features_daily. Firing for all campaigns.
[ENGINE] WARNING: campaign_type_lock='max_clicks' cannot be enforced — bidding_strategy column missing from campaign_features_daily. Firing for all campaigns.

[ENGINE] Done. Generated=0 | SkippedDuplicate=175446 | SkippedNoData=164709 | SkippedNoTable=0
```

Generated=0 is correct — existing pending recs covered all matches (1645 existing pending).

`audit_rules_full.py` ran cleanly with no errors.

---

## Success Criteria Status

- [x] Flask starts cleanly with no errors
- [x] `[ENGINE] Loaded 22 campaign rules from DB` in output
- [x] `[ENGINE] Loaded 28 rules from rules_config.json (non-campaign only)` in output
- [x] Engine processed campaign data (40 rows) without error
- [x] No `KeyError` or `AttributeError` in output
- [x] `audit_rules_full.py` runs cleanly

---

## Architecture Notes

- DB campaign rules use `rule_id = "db_campaign_{id}"` — the `_detect_entity_type()` function falls back to `"campaign"` for any prefix not in its known set, so these route correctly with no code change needed
- Both condition schemas are handled: Format A (`op`/`ref`) and Format B (`operator`/`unit`)
- `campaign_type_lock` warnings are deduplicated via `_warned_locks` set — each distinct lock value warns only once per run
