# CHAT 88: AD_DAILY TABLE + DATABASE INDEXES

**Date:** 2026-03-12
**Estimated Time:** 4–6 hours
**Priority:** HIGH
**Dependencies:** None

---

## CONTEXT

The ACT dashboard has 4 Ad rules that cannot generate recommendations because
the analytics.ad_daily table does not exist in either database. All other entity
tables (campaign_daily, keyword_daily, ad_group_daily, shopping_daily) exist and
are working. Additionally, no database indexes exist on any analytics tables —
adding them now prepares the system for real API data volume.

## OBJECTIVE

Create the ad_daily table in both databases, seed it with synthetic data, update
the copy script, verify Ad recommendations generate, then add indexes across all
analytics tables in warehouse_readonly.duckdb.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\tools\seed_ad_daily.py` — CREATE
   - Populates ad_daily in warehouse.duckdb with ~90 days of synthetic data
   - Multiple ads, ad groups, campaigns
   - Columns must exactly match what Ad rules query

2. `C:\Users\User\Desktop\gads-data-layer\scripts\copy_all_to_readonly.py` — MODIFY
   - Add ad_daily to the existing copy operation alongside the 5 existing tables

3. `C:\Users\User\Desktop\gads-data-layer\scripts\add_indexes.py` — CREATE
   - Adds indexes to warehouse_readonly.duckdb on all 6 analytics tables
   - campaign_daily: campaign_id, date
   - keyword_daily: keyword_id, campaign_id, date
   - ad_group_daily: ad_group_id, campaign_id, date
   - ad_daily: ad_id, campaign_id, date
   - shopping_daily: product_id, campaign_id, date

4. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_88_HANDOFF.md` — CREATE
5. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_88_SUMMARY.md` — CREATE

---

## REQUIREMENTS

### Step 1 — Before writing anything
Read all 4 Ad rules in:
`C:\Users\User\Desktop\gads-data-layer\act_autopilot\rules\`
Extract the exact column names the Ad rules query. The ad_daily schema
MUST match these exactly — do not guess column names.

### Step 2 — ad_daily table
- Create table in warehouse.duckdb first
- Minimum columns: ad_id, campaign_id, ad_group_id, date, impressions,
  clicks, cost, conversions, conversion_value, ctr, cpc
- Seed with realistic values — not all zeros
- Cover at least 90 days of data, at least 10 ads

### Step 3 — copy_all_to_readonly.py
- Follow exact same pattern as existing table copies in that script
- Confirm ad_daily lands in warehouse_readonly.duckdb under ro.analytics.ad_daily

### Step 4 — Indexes
- Only add indexes to warehouse_readonly.duckdb (never warehouse.duckdb)
- Use DuckDB CREATE INDEX IF NOT EXISTS syntax
- Verify indexes exist after creation via PRAGMA or information_schema query

### Step 5 — Verify recommendations
- Run the recommendations engine manually
- Confirm Ad recommendations are generated and appear in warehouse.duckdb
- Report exact count of Ad recommendations generated

### Constraints
- Never open warehouse.duckdb with read_only=True
- Always ATTACH warehouse_readonly.duckdb as ro for read queries
- Follow exact DuckDB connection pattern from existing scripts

---

## SUCCESS CRITERIA

- [ ] ad_daily table exists in both warehouse.duckdb and warehouse_readonly.duckdb
- [ ] Seed script runs without errors
- [ ] copy_all_to_readonly.py includes ad_daily and runs cleanly
- [ ] Ad recommendations count > 0 in warehouse.duckdb
- [ ] Ad recommendations visible on /recommendations page in dashboard
- [ ] Indexes exist on all 6 analytics tables in warehouse_readonly.duckdb
- [ ] add_indexes.py runs without errors
- [ ] No Flask errors on any dashboard page after changes
- [ ] Flask starts cleanly

---

## REFERENCE FILES

- `C:\Users\User\Desktop\gads-data-layer\act_autopilot\rules\` — Read all Ad rules first
- `C:\Users\User\Desktop\gads-data-layer\scripts\copy_all_to_readonly.py` — Existing copy pattern
- `C:\Users\User\Desktop\gads-data-layer\tools\seed_outreach_clicks.py` — Example seed pattern
- `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py` — How recs generate

---

## TESTING

1. Run `python tools/seed_ad_daily.py` — confirm no errors
2. Run `python scripts/copy_all_to_readonly.py` — confirm ad_daily included
3. Run `python scripts/add_indexes.py` — confirm indexes created
4. Run recommendations engine — report exact Ad recommendation count
5. Start Flask, open /recommendations in Opera — confirm Ad recs visible
6. Check all 5 entity pages load without errors
7. Report Flask terminal output for any warnings or errors
