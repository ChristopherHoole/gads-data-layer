# CHAT 97: Fix _load_monitoring_days for DB Rules

**Date:** 2026-03-17
**Priority:** HIGH
**Estimated Time:** 15 minutes
**Dependencies:** None

---

## CONTEXT

The recommendations engine generates recs from two sources:
1. JSON rules in `act_autopilot/rules_config.json` — IDs like `budget_1`, `bid_2`
2. DB rules in the `rules` table in `warehouse.duckdb` — referenced as `db_campaign_7` etc.

When a user accepts a recommendation, `_load_monitoring_days(rule_id)` is called to determine how long to monitor the change. It currently only searches `rules_config.json`. DB rules (rule_id starting with `db_campaign_`) are never found, so monitoring_days returns 0 and accepted recs go straight to "successful" instead of "monitoring".

---

## OBJECTIVE

Fix `_load_monitoring_days` so DB rules return their `cooldown_days` value as `monitoring_days`.

---

## DELIVERABLES

### 1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\recommendations.py` — MODIFY ONE FUNCTION ONLY

Find `_load_monitoring_days(rule_id)` — it starts around line 178.

Change the logic to:

1. If `rule_id` starts with `"db_campaign_"`:
   - Extract the integer ID from the string (e.g. `"db_campaign_7"` → `7`)
   - Connect to `warehouse.duckdb`
   - Query: `SELECT cooldown_days FROM rules WHERE id = ?`
   - Return `{"monitoring_days": cooldown_days, "monitoring_minutes": 0}`
   - If not found or error, return `{"monitoring_days": 0, "monitoring_minutes": 0}`
2. Otherwise (JSON rule ID like `budget_1`):
   - Keep existing logic — search `rules_config.json` for matching `rule_id`
   - Return `{"monitoring_days": monitoring_days, "monitoring_minutes": monitoring_minutes}`
3. If nothing found anywhere:
   - Return `{"monitoring_days": 0, "monitoring_minutes": 0}`

---

## REQUIREMENTS

- **ONLY edit `_load_monitoring_days`** — do not touch any other function
- Do NOT change the return dict format — it must still return `{"monitoring_days": int, "monitoring_minutes": int}`
- Use `duckdb.connect("warehouse.duckdb")` and close the connection in a try/finally
- Add a print statement on success: `[RECOMMENDATIONS] DB rule {rule_id} monitoring_days={cooldown_days}`
- Read the function back after editing to confirm the change is correct

---

## SUCCESS CRITERIA

- [ ] `_load_monitoring_days("db_campaign_7")` returns `{"monitoring_days": 7, "monitoring_minutes": 0}`
- [ ] `_load_monitoring_days("budget_1")` still works as before (reads from JSON)
- [ ] Flask starts cleanly with no errors
- [ ] No other functions modified

---

## DO NOT TOUCH

- Any other function in recommendations.py
- Any other file
- Any CSS or HTML files
- The DB schema
