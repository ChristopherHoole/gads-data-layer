# CHAT 95 HANDOFF

**Date:** 2026-03-15
**Completed:** Recommendations Engine — DB Source of Truth (Campaign Rules)

---

## State Left In

- `recommendations_engine.py` loads campaign rules from DB, non-campaign from JSON
- 22 DB campaign rules active; 28 JSON non-campaign rules active
- All engine functionality preserved; no schema changes needed

---

## Known Limitations / Next Steps

### 1. `campaign_type_lock` Not Yet Enforced
Rules with `campaign_type_lock = 'troas'`, `'tcpa'`, or `'max_clicks'` fire for ALL campaigns because `campaign_features_daily` has no `bidding_strategy` column. Each run logs a one-time warning per lock value. Fix: add `bidding_strategy` column to `campaign_features_daily` and the enforcement code in `_load_db_campaign_rules` will activate automatically.

Look for the TODO comment in `recommendations_engine.py`:
```python
# TODO: proper lock enforcement requires bidding_strategy column
#       in campaign_features_daily
```

### 2. Non-Campaign Rules Still in JSON
keyword, ad_group, ad, shopping rules have not been reviewed for DB migration yet. Future chat: migrate them the same way campaign rules were migrated in Chat 95.

### 3. Cooldown Enforcement
The engine still only checks for existing `pending` recommendations as the deduplication guard. Actual cooldown days are stored in both DB rules and JSON but are not enforced. Future task.

### 4. `_build_trigger_summary` / `_get_current_value` Use Flat Fields
These functions were written for the old JSON flat-field rule format. They still work because `_load_db_campaign_rules` normalises DB rows into that same format. No changes needed unless the rule structure diverges further.

---

## File Modified

- `act_autopilot/recommendations_engine.py` — only this file changed

## Files Not Modified (as required)
- `features.py`, `celery_app.py`, `radar.py` — unchanged
- `rules_config.json` — unchanged (non-campaign rules still read from here)
- `warehouse.duckdb` — unchanged (read-only for campaign rules)
