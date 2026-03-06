# Canonical Query Contract — Chunk 1

## Approved Query Interface (ONLY)

All downstream usage (humans, dashboards, agents, exports) MUST query:

```sql
SELECT *
FROM analytics.campaign_daily;
