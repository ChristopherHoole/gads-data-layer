# CHAT 29 (M8): HANDOFF DOCUMENT
**For:** Next Worker Chat  
**From:** Chat 29 (M8) Worker  
**Date:** 2026-02-22  
**Status:** COMPLETE ✅ — approved by Master Chat

---

## WHAT THIS CHAT BUILT

M8 delivered three things:

1. **Radar background job** — auto-monitors accepted recommendations, reverts them if KPI degrades
2. **Changes page Bootstrap 5 rewrite** — replaces old Tailwind table with card-based My Actions + System Changes tabs
3. **Reverted tab** — added to both `/recommendations` and `/campaigns` Recommendations section

---

## CURRENT STATE OF THE CODEBASE

### New files added
- `act_autopilot/radar.py` — background monitoring thread, runs every 60s
- `act_dashboard/routes/changes.py` — `/changes` blueprint

### Modified files
- `act_autopilot/rules_config.json` — `monitoring_minutes` added to all 13 rules
- `act_dashboard/routes/recommendations.py` — reverted_recs, monitoring_minutes, last_run fix
- `act_dashboard/routes/__init__.py` — changes blueprint registered
- `act_dashboard/templates/recommendations.html` — 5 tabs (added Reverted)
- `act_dashboard/templates/campaigns.html` — 5 inner tabs + 5 summary cards
- `act_dashboard/templates/changes.html` — full Bootstrap 5 rewrite

### Flask startup output (expected)
```
✅ [Chat 29 M8] Registered changes blueprint (/changes)
✅ [Chat 29 M8] Radar background thread started (60s cycle)
```

---

## CRITICAL TECHNICAL PATTERNS ESTABLISHED

### DuckDB connection pattern (IMPORTANT)
Any component needing both read and write access must use this pattern:
```python
conn = duckdb.connect('warehouse.duckdb')          # read-write
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")
# Now use conn for reads (ro.analytics.*) AND writes (changes table)
# Close conn when done — never open two connections to same file
```
**Never** open `warehouse.duckdb` with `read_only=True` if you need to write. **Never** open it twice with different configs in the same process.

### changes table JOIN strategy
The `changes` table has NO `recommendation_id` column. To join with `recommendations`, use:
```sql
LEFT JOIN recommendations r
  ON r.campaign_id = c.campaign_id
  AND r.rule_id = c.rule_id
QUALIFY ROW_NUMBER() OVER (PARTITION BY r.campaign_id, r.rule_id ORDER BY r.generated_at DESC) = 1
```

### executed_by values in changes table
| Value | Meaning |
|---|---|
| `user_accept` | User clicked Accept |
| `user_modify` | User modified value then accepted |
| `user_decline` | User clicked Decline |
| `radar_resolved` | Radar: monitoring complete, KPI held, change kept |
| `radar_revert` | Radar: KPI degraded, change auto-reverted |

### monitoring_minutes
All rules now have a `monitoring_minutes` field in `rules_config.json`. When `> 0`, this takes priority over `monitoring_days`. Leave at `0` for normal operation. Useful for fast-testing monitoring/revert flow in development.

---

## WHAT STILL NEEDS DOING (per roadmap)

Check `PROJECT_ROADMAP.md` and `DASHBOARD_PROJECT_PLAN.md` for the full list. Known remaining items as of this chat:

- **Config YAML validation errors** — `client_001`, `client_001_mcc`, `client_002`, `client_synthetic` all have missing/invalid fields. App starts despite these but they need fixing for clean operation.
- **Master Chat documentation update** — Steps 14/15 of workflow (Master's responsibility, not worker's).

---

## PAGES AND ROUTES — CURRENT STATUS

| Route | File | Status |
|---|---|---|
| `/` | `dashboard.py` | ✅ Complete |
| `/campaigns` | `campaigns.py` | ✅ Complete |
| `/ad-groups` | `ad_groups.py` | ✅ Complete |
| `/keywords` | `keywords.py` | ✅ Complete |
| `/ads` | `ads.py` | ✅ Complete |
| `/shopping` | `shopping.py` | ✅ Complete |
| `/recommendations` | `recommendations.py` | ✅ Complete |
| `/changes` | `changes.py` | ✅ Complete (this chat) |
| `/settings` | `settings.py` | Status unknown — check roadmap |

---

## WARNINGS FOR NEXT WORKER

1. **Flask route decorator rule** — NEVER insert helper functions between a `@bp.route(...)` decorator and its function. Silently breaks routing.
2. **Always extend `base_bootstrap.html`** — NOT `base.html`. Using `base.html` will render Tailwind styling (wrong).
3. **Database prefix** — Always `ro.analytics.*` for readonly queries. Never just `analytics.*`.
4. **Full Windows paths always** — e.g. `C:\Users\User\Desktop\gads-data-layer\...`
5. **Request current file before editing** — Never assume a file matches what you last saw.
