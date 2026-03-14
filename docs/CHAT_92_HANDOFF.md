# CHAT 92 HANDOFF

**Completed:** 2026-03-14
**Next Chat:** Chat 93

---

## State at Handoff

`impression_share_lost_rank` is fully wired end-to-end:
- Column exists in both `warehouse.duckdb` and `warehouse_readonly.duckdb`
- `build_campaign_features_daily()` computes it as a 7-day rolling average of `search_rank_lost_impression_share`
- `CAMPAIGN_METRIC_MAP` resolves it to the real column (not a proxy)
- 4 seeded rules that use this metric will now find a matching DB column

## Known Limitation

`search_rank_lost_impression_share` is absent from the current **synthetic** `analytics.campaign_daily`. Until real GA data is loaded, `impression_share_lost_rank` will be NULL in all feature rows. This is expected and handled — the `_pick_expr()` fallback returns `CAST(NULL AS DOUBLE)` when the source column is missing.

## schema_version

`build_campaign_features_daily()` now defaults to `schema_version=2`. Existing rows in the DB retain `schema_version=1` (they were written before this chat). New runs will write `schema_version=2`.

## Suggested Next Steps

- **Chat 93:** Add `search_rank_lost_impression_share` to the synthetic data seeder (`tools/seed_campaign_daily.py` or equivalent) so the column is non-NULL in test runs
- Or: add the next missing metric to the features pipeline
