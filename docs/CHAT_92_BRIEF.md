# CHAT 92: ADD IMPRESSION_SHARE_LOST_RANK TO FEATURES PIPELINE

**Date:** 2026-03-14
**Estimated Time:** 1–2 hours
**Priority:** HIGH
**Dependencies:** Chat 91 complete ✅

---

## CONTEXT

4 seeded rules use `impression_share_lost_rank` as a condition metric:
- Loosen tROAS Target – Constrained Volume
- Loosen tCPA Target – Volume Constrained
- Tighten tROAS Target – Strong Performance (C2)
- Increase Max CPC Cap – Low Impression Share

`CAMPAIGN_METRIC_MAP` in `recommendations_engine.py` currently has a placeholder proxy
for this metric. It needs to point to a real column in `campaign_features_daily`.

The source data already exists: `search_rank_lost_impression_share` is in
`analytics.campaign_daily` (sourced from `snap_campaign_daily`).

---

## OBJECTIVE

Add `impression_share_lost_rank` as a computed column to `campaign_features_daily`,
sourced from `search_rank_lost_impression_share` in `analytics.campaign_daily`,
then wire it into `CAMPAIGN_METRIC_MAP`.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\act_lighthouse\features.py` — MODIFY
   - Add `impression_share_lost_rank DOUBLE` to the column DDL (cols list, near `has_impr_share`)
   - Add `impression_share_lost_rank` to `insert_cols` list
   - Add `search_rank_lost_impression_share` to the src CTE
   - Compute 7d rolling average in the final SELECT as `impression_share_lost_rank`
   - Bump `schema_version` from 1 to 2

2. `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py` — MODIFY
   - Replace the proxy entry for `impression_share_lost_rank` with the real column:
     `"impression_share_lost_rank": ("impression_share_lost_rank", None, None)`

3. `C:\Users\User\Desktop\gads-data-layer\scripts\add_impression_share_col.py` — CREATE
   - Migration script: ALTER TABLE to add column to both warehouse.duckdb and warehouse_readonly.duckdb
   - Safe to re-run (catch existing column error)

4. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_92_HANDOFF.md` — CREATE
5. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_92_SUMMARY.md` — CREATE

---

## REQUIREMENTS

### Technical

- Source column: `search_rank_lost_impression_share` in `analytics.campaign_daily`
  (DOUBLE, range 0.0–1.0, e.g. 0.35 = 35% IS lost to rank)
- Target column: `impression_share_lost_rank` in `analytics.campaign_features_daily`
- Computation: 7-day rolling average of `search_rank_lost_impression_share`
- NULL handling: if no IS data available, column should be NULL (not 0)

### How features.py works (critical context)

The build function follows this pattern:
1. src CTE: reads raw data from analytics.campaign_daily for the date window
2. Rolls up aggregates across windows (w1, w3, w7, w14, w30)
3. final SELECT: picks snapshot_date row and outputs all computed columns
4. INSERT into analytics.campaign_features_daily
5. Separate UPDATE adds pacing/cap data

`impression_share_lost_rank` should be added in the src CTE and included in the
final SELECT. It is NOT a pacing metric — do not add via UPDATE.

### In the src CTE (around line 408), add:
```sql
cd.search_rank_lost_impression_share AS rank_lost_is
```

### In the final SELECT, compute:
```sql
AVG(rank_lost_is) OVER (
    PARTITION BY customer_id, campaign_id
    ORDER BY snapshot_date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
) AS impression_share_lost_rank
```

### Migration script:
```python
import duckdb

for db_path in [r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb',
                r'C:\Users\User\Desktop\gads-data-layer\warehouse_readonly.duckdb']:
    conn = duckdb.connect(db_path)
    try:
        conn.execute("ALTER TABLE analytics.campaign_features_daily ADD COLUMN impression_share_lost_rank DOUBLE")
        print(f"{db_path}: column added")
    except Exception as e:
        print(f"{db_path}: {e} (safe to ignore if column already exists)")
    conn.close()
```

### Constraints
- Migration script must be run BEFORE testing features.py changes
- Never open warehouse.duckdb with read_only=True
- CREATE TABLE IF NOT EXISTS in DDL means existing DB won't auto-add column

---

## SUCCESS CRITERIA

- [ ] Migration script runs cleanly on both databases
- [ ] `impression_share_lost_rank` column exists in analytics.campaign_features_daily
- [ ] `build_campaign_features_daily()` runs without errors
- [ ] Column is populated with non-NULL values from existing synthetic data
- [ ] `CAMPAIGN_METRIC_MAP` entry points to real column (not proxy)
- [ ] Flask starts cleanly with no errors

---

## REFERENCE FILES

- `C:\Users\User\Desktop\gads-data-layer\act_lighthouse\features.py` — full build function
- `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py` — CAMPAIGN_METRIC_MAP at line 79
- `C:\Users\User\Desktop\gads-data-layer\scripts\add_indexes.py` — example migration script pattern

---

## TESTING

1. Run migration script:
   `python C:\Users\User\Desktop\gads-data-layer\scripts\add_impression_share_col.py`

2. Verify column exists:
   `python -c "import duckdb; conn = duckdb.connect(r'C:\Users\User\Desktop\gads-data-layer\warehouse_readonly.duckdb'); print(conn.execute('SELECT impression_share_lost_rank FROM analytics.campaign_features_daily LIMIT 3').fetchall())"`

3. Start Flask and confirm no errors:
   `python act_dashboard/app.py`

4. Report output of step 2 and any Flask log errors.
