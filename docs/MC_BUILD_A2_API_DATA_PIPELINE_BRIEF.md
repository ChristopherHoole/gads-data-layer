# MC Build A2 — Google Ads API Data Pipeline
**Session:** MC Build A2 — API Data Pipeline
**Date:** 2026-04-12
**Objective:** Build the data ingestion pipeline that pulls real Google Ads data from Objection Experts into the act_v2_snapshots table. This feeds the optimization engine with real performance data.

---

## CONTEXT

Session A1 (Database Schema) is complete. The act_v2_* tables exist in warehouse.duckdb with Objection Experts seeded as the first client (client_id='oe001', all levels OFF).

**This session connects ACT to real Google Ads data for the first time.**

**Existing Google Ads API code exists in the codebase BUT has NEVER been connected to a live account:**
- `act_autopilot/google_ads_api.py` — 1104 lines, implements campaign/keyword/ad/shopping API operations. Useful for GAQL query patterns and error handling patterns. But has never been tested live.
- `secrets/google-ads.yaml` — **CONTAINS WRONG CREDENTIALS.** The developer_token and login_customer_id in this file are WRONG for the current setup. This file must be updated before anything will work.
- `act_dashboard/routes/shared.py` — `get_google_ads_client()` helper. May be useful for the loading pattern.
- `src/gads_pipeline/v1_runner.py` — existing data pipeline (mock and live modes). Reference only.
- `scripts/google_ads_oauth.py` — OAuth token generator script (Desktop app flow). Will be needed to generate a fresh refresh_token.
- `google-ads==29.0.0` already in requirements.txt

**THE CREDENTIALS FILE IS WRONG. Here are the CORRECT values:**

| Field | Current (WRONG) | Correct |
|-------|-----------------|---------|
| `developer_token` | `qAJz1YTgID7c7Jd2PDA1QA` | `oDANZ-BXQprTm7_Sg4rjDg` |
| `login_customer_id` | `4434379827` | `1527964125` |
| `client_id` | Unknown if valid | Needs verification — may need a new OAuth client from Google Cloud Console |
| `client_secret` | Unknown if valid | Needs verification |
| `refresh_token` | Likely expired or wrong account | Must be regenerated using `scripts/google_ads_oauth.py` |

**Before ANY API calls will work, the session must complete Task 1B which:**
1. Checks for `secrets/google_ads_client_secret.json` (asks user to provide if missing)
2. Runs `scripts/google_ads_oauth.py` with correct dev token + MCC to generate `secrets/google-ads.yaml`
3. Tests the connection with a simple API call

See Task 1B for the full step-by-step flow. ASK the user for help if authentication fails — do not guess at credentials.

**Client details:**
- Objection Experts customer ID: `853-021-1223` (format as `8530211223` — no dashes)
- MCC (login_customer_id): `152-796-4125` (format as `1527964125` — no dashes)
- Developer token: `oDANZ-BXQprTm7_Sg4rjDg` (approved for Basic Access, Apr 2026)
- API access: Basic (15,000 operations/day)
- Account size: small (1 active Search campaign + several paused campaigns, ~12 keywords, ~3 ads). Ingest ALL non-removed campaigns including paused ones (they have historical data).

---

## CRITICAL RULES

1. **Reuse existing API code PATTERNS only.** Read `act_autopilot/google_ads_api.py` for GAQL query patterns, error handling patterns, and micros conversion. But do NOT assume it works — it has never been tested against a live account. The credentials file is wrong and must be fixed (see Task 1B). Write new code for the v2 pipeline that follows the same patterns but is independently tested.

2. **Do NOT modify pre-ACT-v2 files** (anything in the old engine, outreach, jobs, etc.). Create new files for the v2 pipeline. Exception: you WILL update the ACT v2 migration scripts (`create_act_v2_schema.py`, `verify_act_v2_schema.py`) and `secrets/google-ads.yaml` — these are our files from Session A1 and need updating.

3. **Store data in `act_v2_snapshots`** — the table created in Session A1.

4. **All monetary values in GBP as DECIMAL** — Google Ads API returns costs in micros (1 GBP = 1,000,000 micros). **Divide by 1,000,000** to convert to GBP before storing. Example: `cost_micros = 487000000` → `cost = 487.00`. The existing code in `act_autopilot/google_ads_api.py` shows this pattern.

5. **Date range for initial backfill:** Pull 90 days of historical data (to support the 7d/14d/30d weighted scoring windows with buffer).

6. **Daily snapshot = one row per entity per date** in act_v2_snapshots.

7. **Idempotency:** Running the pipeline twice for the same date should not create duplicate rows. Use check-then-insert or delete-then-insert per (client_id, snapshot_date, level, entity_id).

8. **Stop Flask before running** (DuckDB lock). Same as Session A1.

9. **Log everything** — stdout + `act_dashboard/data_pipeline/ingestion.log` (append mode). Use Python's `logging` module.

10. **This session creates 2 additional tables** beyond the A1 schema (for search terms and campaign segments). These are needed for the engine checks but weren't in the original A1 schema because we only defined them after understanding the data requirements.

---

## TASK 1: Read Existing API Code

Before writing anything, read and understand these files:

1. `act_autopilot/google_ads_api.py` — understand the client loading, GAQL queries, error handling, micros conversion
2. `secrets/google-ads.yaml` — understand the credential structure
3. `act_dashboard/routes/shared.py` — understand `get_google_ads_client()`
4. `src/gads_pipeline/v1_runner.py` — understand the existing data pipeline approach
5. `act_dashboard/db/migrations/create_act_v2_schema.py` — understand the act_v2_snapshots table structure

Confirm what you understand about:
- How to instantiate GoogleAdsClient
- How to run GAQL queries
- How micros conversion works
- What the act_v2_snapshots columns expect

---

## TASK 1B: Fix Credentials and Test API Connection

The existing `secrets/google-ads.yaml` has WRONG credentials. This must be fixed first.

### Step 1: Check for client_secret JSON file

Read `scripts/google_ads_oauth.py` first — it already handles everything. The script:
- Takes `--client-secret` (default: `secrets/google_ads_client_secret.json`)
- Takes `--developer-token` and `--login-customer-id` as CLI args
- Takes `--out-yaml` (default: `secrets/google-ads.yaml`)
- Has `--no-browser` mode (prints auth URL for manual browser flow)
- Generates the full `secrets/google-ads.yaml` with all correct values

**Check if the client_secret JSON exists:**
```
ls secrets/google_ads_client_secret.json
```

If it exists, proceed to Step 2.

If it does NOT exist, ASK the user:
- "I need the OAuth client_secret JSON file to authenticate with Google Ads API. Please check Google Cloud Console → APIs & Services → Credentials → find or create a Desktop OAuth 2.0 Client ID → click Download JSON → save to `secrets/google_ads_client_secret.json`"
- STOP and wait for the user to provide the file.

### Step 2: Generate credentials

Run the OAuth script with the correct developer token and MCC, using `--no-browser` mode (Claude Code may not be able to open a browser directly):

```
python scripts/google_ads_oauth.py --developer-token oDANZ-BXQprTm7_Sg4rjDg --login-customer-id 1527964125 --no-browser
```

This will:
1. Read `secrets/google_ads_client_secret.json`
2. Print an auth URL — tell the user to open it in their browser
3. User authenticates with chris@christopherhoole.com and grants access
4. User pastes the redirect URL back into the terminal
5. Script generates `secrets/google-ads.yaml` with ALL correct values (developer_token, login_customer_id, client_id, client_secret, refresh_token)

**If the script fails** (file not found, invalid JSON, auth error):
- ASK the user for help. Do not guess at credentials.
- Common issue: the client_secret JSON may be for a "Web" type OAuth client instead of "Desktop" — it must be Desktop type.

**If the script succeeds:**
- Verify the generated `secrets/google-ads.yaml` contains `developer_token: oDANZ-BXQprTm7_Sg4rjDg` and `login_customer_id: "1527964125"`
- Proceed to Step 3

### Step 3: Write and run a connection test

First create the data_pipeline directory if it doesn't exist:
```
mkdir -p act_dashboard/data_pipeline
touch act_dashboard/data_pipeline/__init__.py
```

Then create `act_dashboard/data_pipeline/test_api_connection.py`:

```python
"""
Tests the Google Ads API connection.
Run from project root: python -m act_dashboard.data_pipeline.test_api_connection
"""
import sys
from pathlib import Path
from google.ads.googleads.client import GoogleAdsClient

# Derive absolute path to secrets/google-ads.yaml from this file's location
YAML_PATH = str(Path(__file__).resolve().parents[2] / "secrets" / "google-ads.yaml")

def test_connection():
    try:
        client = GoogleAdsClient.load_from_storage(YAML_PATH)
        print("✓ Client loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load client: {e}")
        sys.exit(1)
    
    customer_id = "8530211223"  # Objection Experts
    
    try:
        ga_service = client.get_service("GoogleAdsService")
        query = """
            SELECT campaign.id, campaign.name, campaign.status
            FROM campaign
            WHERE campaign.status != 'REMOVED'
            LIMIT 10
        """
        response = ga_service.search(customer_id=customer_id, query=query)
        
        campaigns = []
        for row in response:
            campaigns.append({
                "id": row.campaign.id,
                "name": row.campaign.name,
                "status": row.campaign.status.name
            })
        
        print(f"✓ API call successful — found {len(campaigns)} campaigns:")
        for c in campaigns:
            print(f"  - {c['name']} ({c['status']})")
        
    except Exception as e:
        print(f"✗ API call failed: {e}")
        sys.exit(1)
    
    print("\n✓ Google Ads API connection verified successfully")

if __name__ == "__main__":
    test_connection()
```

Run it:
```
python -m act_dashboard.data_pipeline.test_api_connection
```

Expected output (campaign names and count may vary — the key is that at least 1 campaign is returned):
```
✓ Client loaded successfully
✓ API call successful — found N campaigns:
  - GLO Campaign (ENABLED)
  - Planning Objection Letters (PAUSED)
  - ...

✓ Google Ads API connection verified successfully
```

**If the test fails with an authentication error:** ASK the user for help. Do not guess at credentials.
**If the test fails with a permissions error:** The developer token may not have access to this customer ID. ASK the user.
**If the test succeeds but returns 0 campaigns:** The customer_id may be wrong. ASK the user.

**Do NOT proceed to Task 2 until this test passes.** Everything else depends on a working API connection.

---

## TASK 2: Create 2 Additional Tables

The act_v2_snapshots table stores one row per entity per date — good for campaigns, ad groups, keywords, ads. But two data types don't fit this pattern:

### `act_v2_search_terms`
Search term performance data. Too high-volume to store as JSON inside campaign snapshots.

```sql
CREATE SEQUENCE IF NOT EXISTS seq_act_v2_search_terms;

CREATE TABLE IF NOT EXISTS act_v2_search_terms (
    search_term_id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_search_terms'),
    client_id VARCHAR NOT NULL,
    snapshot_date DATE NOT NULL,
    campaign_id VARCHAR(30) NOT NULL,
    campaign_name VARCHAR(500),
    ad_group_id VARCHAR(30) NOT NULL,
    ad_group_name VARCHAR(500),
    search_term VARCHAR NOT NULL,
    match_type VARCHAR(20),
    keyword_text VARCHAR,
    keyword_id VARCHAR(100),
    cost DECIMAL(18,2),
    impressions INTEGER,
    clicks INTEGER,
    conversions DECIMAL(10,2),
    conversion_value DECIMAL(18,2),
    ctr DECIMAL(10,4),
    avg_cpc DECIMAL(10,2),
    cost_per_conversion DECIMAL(10,2),
    conversion_rate DECIMAL(10,4),
    FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
);

CREATE INDEX IF NOT EXISTS idx_act_v2_search_terms_lookup
    ON act_v2_search_terms(client_id, snapshot_date, campaign_id);
```

### `act_v2_campaign_segments`
Campaign performance broken down by device, geo, and schedule segments. Needed for Campaign Level universal lever checks.

```sql
CREATE SEQUENCE IF NOT EXISTS seq_act_v2_campaign_segments;

CREATE TABLE IF NOT EXISTS act_v2_campaign_segments (
    segment_id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_campaign_segments'),
    client_id VARCHAR NOT NULL,
    snapshot_date DATE NOT NULL,
    campaign_id VARCHAR(30) NOT NULL,
    campaign_name VARCHAR(500),
    segment_type VARCHAR(20) NOT NULL CHECK (segment_type IN ('device', 'geo', 'ad_schedule', 'day_of_week')),
    segment_value VARCHAR(200) NOT NULL,
    cost DECIMAL(18,2),
    impressions INTEGER,
    clicks INTEGER,
    conversions DECIMAL(10,2),
    conversion_value DECIMAL(18,2),
    ctr DECIMAL(10,4),
    avg_cpc DECIMAL(10,2),
    cost_per_conversion DECIMAL(10,2),
    conversion_rate DECIMAL(10,4),
    bid_modifier DECIMAL(10,2),
    FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
);

CREATE INDEX IF NOT EXISTS idx_act_v2_segments_lookup
    ON act_v2_campaign_segments(client_id, snapshot_date, campaign_id, segment_type);
```

**Add these tables to `act_dashboard/db/migrations/create_act_v2_schema.py`** (update it — add the new tables, sequences, and indexes). Update the verify script too — expected column counts:
- `act_v2_search_terms`: **20 columns**
- `act_v2_campaign_segments`: **17 columns**

Run both scripts and verify.

After this task: 13 tables, 7 sequences, 7 indexes.

---

## TASK 3: Build the Data Ingestion Module

The `act_dashboard/data_pipeline/` directory and `__init__.py` were already created in Task 1B (for the test script). If not, create them now.

Add the following files:

### `act_dashboard/data_pipeline/google_ads_ingestion.py`
The main data ingestion module. This pulls data from the Google Ads API and stores it in act_v2_* tables.

**Structure:**

```python
class GoogleAdsDataPipeline:
    def __init__(self, client_id: str, customer_id: str):
        """
        client_id: ACT internal client ID (e.g., 'oe001')
        customer_id: Google Ads customer ID (e.g., '8530211223')
        """
        self.client_id = client_id
        self.customer_id = customer_id
        self.google_ads_client = self._load_client()
        self.db = self._connect_db()
    
    def _load_client(self) -> GoogleAdsClient:
        """Load Google Ads client from secrets/google-ads.yaml"""
        # Use: GoogleAdsClient.load_from_storage(yaml_path)
        # Derive absolute path from __file__ to avoid working-directory issues
    
    def _connect_db(self):
        """Connect to warehouse.duckdb and return DuckDB connection"""
    
    def ingest_date(self, date: str):
        """Pull all data for a single date and store in act_v2_* tables."""
        self.ingest_campaigns(date)
        self.ingest_ad_groups(date)
        self.ingest_keywords(date)
        self.ingest_ads(date)
        self.ingest_search_terms(date)
        self.ingest_campaign_segments(date)
        self.ingest_account(date)  # computed from campaign data, not a separate API call
    
    def ingest_date_range(self, start_date: str, end_date: str):
        """Pull data for a range of dates (for backfill)."""
        # Loop through each date in range
        # Call ingest_date() for each
        # Add a small delay between dates (0.5-1 second) to avoid API rate limits
        # Log progress: "Ingesting date X of Y (YYYY-MM-DD)..."
    
    def ingest_campaigns(self, date: str):
        """Pull campaign-level data for a single date."""
    
    def ingest_ad_groups(self, date: str):
        """Pull ad group-level data for a single date."""
    
    def ingest_keywords(self, date: str):
        """Pull keyword-level data for a single date."""
    
    def ingest_ads(self, date: str):
        """Pull ad-level data for a single date."""
    
    def ingest_search_terms(self, date: str):
        """Pull search term data for a single date."""
    
    def ingest_campaign_segments(self, date: str):
        """Pull campaign segment data (device, geo, schedule) for a single date."""
    
    def ingest_account(self, date: str):
        """Compute account-level snapshot by aggregating campaign data already ingested for this date.
        NOT a separate API call — reads from act_v2_snapshots where level='campaign' and aggregates.
        Stores as level='account' with entity_id = customer_id.
        
        Implementation: either use DuckDB's json_extract() in SQL to sum across campaign rows,
        or read rows in Python, parse metrics_json, and sum in Python. Either approach works.
        
        Aggregation rules:
        - SUM: cost, impressions, clicks, conversions, conversion_value
        - COMPUTE: ctr = clicks/impressions, avg_cpc = cost/clicks, 
          cost_per_conversion = cost/conversions, conversion_rate = conversions/clicks
        - Handle division by zero for all computed fields (return 0.0)
        """
```

### GAQL Queries per Level

For each `ingest_*` method, use a GAQL query via `GoogleAdsService.search()`. Follow the existing pattern from `act_autopilot/google_ads_api.py`.

**Campaign query:**
Note: The bidding strategy fields (`campaign.target_cpa.target_cpa_micros`, `campaign.target_roas.target_roas`) may have different field paths depending on the Google Ads API version. In recent versions, these might be under `campaign.maximize_conversions.target_cpa_micros` or similar. Check the existing queries in `act_autopilot/google_ads_api.py` and the API docs. If a field doesn't exist, remove it from the query and handle as NULL in the metrics_json.

```sql
SELECT
    campaign.id,
    campaign.name,
    campaign.status,
    campaign.advertising_channel_type,
    campaign_budget.amount_micros,
    campaign.bidding_strategy_type,
    campaign.target_cpa.target_cpa_micros,
    campaign.target_roas.target_roas,
    metrics.cost_micros,
    metrics.impressions,
    metrics.clicks,
    metrics.conversions,
    metrics.conversions_value,
    metrics.ctr,
    metrics.average_cpc,
    metrics.cost_per_conversion,
    metrics.search_impression_share,
    metrics.search_budget_lost_impression_share,
    metrics.search_rank_lost_impression_share,
    segments.date
FROM campaign
WHERE segments.date = '{date}'
    AND campaign.status != 'REMOVED'
```

**Ad Group query:**
```sql
SELECT
    ad_group.id,
    ad_group.name,
    ad_group.status,
    campaign.id,
    campaign.name,
    metrics.cost_micros,
    metrics.impressions,
    metrics.clicks,
    metrics.conversions,
    metrics.conversions_value,
    metrics.ctr,
    metrics.average_cpc,
    metrics.cost_per_conversion,
    segments.date
FROM ad_group
WHERE segments.date = '{date}'
    AND campaign.status != 'REMOVED'
    AND ad_group.status != 'REMOVED'
```

**Keyword query:**
```sql
SELECT
    ad_group_criterion.criterion_id,
    ad_group_criterion.keyword.text,
    ad_group_criterion.keyword.match_type,
    ad_group_criterion.status,
    ad_group_criterion.quality_info.quality_score,
    ad_group_criterion.quality_info.creative_quality_score,
    ad_group_criterion.quality_info.search_predicted_ctr,
    ad_group_criterion.quality_info.post_click_quality_score,
    ad_group_criterion.effective_cpc_bid_micros,
    ad_group.id,
    ad_group.name,
    campaign.id,
    campaign.name,
    metrics.cost_micros,
    metrics.impressions,
    metrics.clicks,
    metrics.conversions,
    metrics.conversions_value,
    metrics.ctr,
    metrics.average_cpc,
    metrics.cost_per_conversion,
    segments.date
FROM keyword_view
WHERE segments.date = '{date}'
    AND campaign.status != 'REMOVED'
    AND ad_group.status != 'REMOVED'
```

**Ad query:**
```sql
SELECT
    ad_group_ad.ad.id,
    ad_group_ad.ad.type,
    ad_group_ad.ad.name,
    ad_group_ad.ad.responsive_search_ad.headlines,
    ad_group_ad.ad.responsive_search_ad.descriptions,
    ad_group_ad.ad.final_urls,
    ad_group_ad.status,
    ad_group_ad.ad_strength,
    ad_group.id,
    ad_group.name,
    campaign.id,
    campaign.name,
    metrics.cost_micros,
    metrics.impressions,
    metrics.clicks,
    metrics.conversions,
    metrics.conversions_value,
    metrics.ctr,
    metrics.average_cpc,
    metrics.cost_per_conversion,
    segments.date
FROM ad_group_ad
WHERE segments.date = '{date}'
    AND campaign.status != 'REMOVED'
    AND ad_group.status != 'REMOVED'
    AND ad_group_ad.status != 'REMOVED'
```

**Search terms query:**
```sql
SELECT
    search_term_view.search_term,
    search_term_view.status,
    ad_group.id,
    ad_group.name,
    campaign.id,
    campaign.name,
    segments.keyword.info.text,
    segments.keyword.info.match_type,
    segments.keyword.ad_group_criterion,
    metrics.cost_micros,
    metrics.impressions,
    metrics.clicks,
    metrics.conversions,
    metrics.conversions_value,
    metrics.ctr,
    metrics.average_cpc,
    metrics.cost_per_conversion,
    segments.date
FROM search_term_view
WHERE segments.date = '{date}'
    AND campaign.status != 'REMOVED'
```

**Campaign segments — Device:**
```sql
SELECT
    campaign.id,
    campaign.name,
    segments.device,
    metrics.cost_micros,
    metrics.impressions,
    metrics.clicks,
    metrics.conversions,
    metrics.conversions_value,
    metrics.ctr,
    metrics.average_cpc,
    metrics.cost_per_conversion,
    segments.date
FROM campaign
WHERE segments.date = '{date}'
    AND campaign.status != 'REMOVED'
```

**Campaign segments — Geo (user location):**
```sql
SELECT
    campaign.id,
    campaign.name,
    geographic_view.country_criterion_id,
    geographic_view.location_type,
    metrics.cost_micros,
    metrics.impressions,
    metrics.clicks,
    metrics.conversions,
    metrics.conversions_value,
    metrics.ctr,
    metrics.average_cpc,
    metrics.cost_per_conversion,
    segments.date
FROM geographic_view
WHERE segments.date = '{date}'
    AND campaign.status != 'REMOVED'
```

**Campaign segments — Ad schedule (hour of day):**
```sql
SELECT
    campaign.id,
    campaign.name,
    segments.hour,
    segments.day_of_week,
    metrics.cost_micros,
    metrics.impressions,
    metrics.clicks,
    metrics.conversions,
    metrics.conversions_value,
    metrics.ctr,
    metrics.average_cpc,
    metrics.cost_per_conversion,
    segments.date
FROM campaign
WHERE segments.date = '{date}'
    AND campaign.status != 'REMOVED'
```

**IMPORTANT GAQL NOTES:**
- These queries are starting points. The exact field names and availability WILL likely need adjustment. Verify against the Google Ads API documentation for the version matching `google-ads==29.0.0`.
- GAQL does NOT support parameterised queries — string formatting/f-strings for the date is the standard approach.
- Some fields (like `quality_score`) are only available for enabled keywords — handle missing values gracefully.
- Some metrics may return 0 or NULL for days with no activity — this is normal, store as-is.
- The search terms query field `segments.keyword.info.text` may need adjustment depending on the API version — check the existing queries in `act_autopilot/google_ads_api.py` for working field paths.
- The `bid_modifier` column in `act_v2_campaign_segments` may need a separate query from `campaign_criterion` for device/geo/schedule modifiers — the standard metrics queries don't return bid adjustments. If getting bid modifiers is complex, store NULL for now and populate in a later session.
- **Account-level snapshots:** The `act_v2_snapshots` table supports `level='account'` but account metrics are aggregates of campaign data. Compute account-level snapshots by summing campaign snapshots for each date (don't make a separate API call). Add an `ingest_account()` method that reads from the campaign data already ingested.
- **Idempotency for search terms and segments:** Use the same delete-then-insert pattern as snapshots. Delete all rows for the given `(client_id, snapshot_date)` before inserting new ones. This is simpler than per-entity deletion because search terms and segments are date-level bulk data.

**Directory creation note:** The `act_dashboard/data_pipeline/` directory is created in Task 1B (when writing the test script) before Task 3 formally defines it. Ensure the directory and `__init__.py` exist before writing any files into it.

### Storing Data in act_v2_snapshots

For campaigns, ad groups, keywords, and ads — store one row per entity per date:

```python
def _store_snapshot(self, date, level, entity_id, entity_name, parent_entity_id, metrics_dict):
    """Store a single entity snapshot. Handles idempotency via delete-then-insert in a transaction."""
    self.db.begin()
    try:
        self.db.execute("""
            DELETE FROM act_v2_snapshots 
            WHERE client_id = ? AND snapshot_date = ? AND level = ? AND entity_id = ?
        """, [self.client_id, date, level, entity_id])
        
        self.db.execute("""
            INSERT INTO act_v2_snapshots 
            (client_id, snapshot_date, level, entity_id, entity_name, parent_entity_id, metrics_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [self.client_id, date, level, entity_id, entity_name, parent_entity_id, 
              json.dumps(metrics_dict)])
        self.db.commit()
    except Exception:
        self.db.rollback()
        raise
```

Note: DuckDB's `begin()`/`commit()`/`rollback()` API may differ — check the Python duckdb library docs. The key principle: delete and insert must be atomic so data isn't lost if the insert fails.

### metrics_json Format Per Level

Define explicit JSON schemas so the engine knows what to expect.

**Campaign metrics_json:**
```json
{
    "cost": 487.00,
    "impressions": 10050,
    "clicks": 780,
    "conversions": 26.0,
    "conversion_value": 0.0,
    "ctr": 0.0776,
    "avg_cpc": 0.62,
    "cost_per_conversion": 18.73,
    "conversion_rate": 0.0333,
    "budget_amount": 30.00,
    "bid_strategy_type": "MAXIMIZE_CONVERSIONS",
    "target_cpa": 25.00,
    "target_roas": null,
    "campaign_status": "ENABLED",
    "campaign_type": "SEARCH",
    "search_impression_share": 0.391,
    "search_lost_is_budget": 0.152,
    "search_lost_is_rank": 0.457
}
```

**Ad Group metrics_json:**
```json
{
    "cost": 320.00,
    "impressions": 8200,
    "clicks": 620,
    "conversions": 21.0,
    "conversion_value": 0.0,
    "ctr": 0.0756,
    "avg_cpc": 0.52,
    "cost_per_conversion": 15.24,
    "conversion_rate": 0.0339,
    "ad_group_status": "ENABLED"
}
```

**Keyword metrics_json:**
```json
{
    "cost": 45.00,
    "impressions": 1200,
    "clicks": 95,
    "conversions": 3.0,
    "conversion_value": 0.0,
    "ctr": 0.0792,
    "avg_cpc": 0.47,
    "cost_per_conversion": 15.00,
    "conversion_rate": 0.0316,
    "keyword_text": "planning objection",
    "match_type": "EXACT",
    "keyword_status": "ENABLED",
    "quality_score": 7,
    "expected_ctr": "ABOVE_AVERAGE",
    "ad_relevance": "AVERAGE",
    "landing_page_experience": "ABOVE_AVERAGE",
    "max_cpc_bid": 3.50
}
```

**Ad metrics_json:**
```json
{
    "cost": 120.00,
    "impressions": 3500,
    "clicks": 280,
    "conversions": 9.0,
    "conversion_value": 0.0,
    "ctr": 0.08,
    "avg_cpc": 0.43,
    "cost_per_conversion": 13.33,
    "conversion_rate": 0.0321,
    "ad_type": "RESPONSIVE_SEARCH_AD",
    "ad_status": "ENABLED",
    "ad_strength": "GOOD",
    "headlines": ["Expert Planning Objections", "RTPI Qualified", ...],
    "descriptions": ["Professional planning objection letters...", ...],
    "final_urls": ["https://objectionexperts.com"]
}
```

**Data conversion rules:**
- All monetary values (cost, avg_cpc, cost_per_conversion, max_cpc_bid, budget_amount, target_cpa): **divide micros by 1,000,000** to get GBP
- `conversion_rate`: **compute as `conversions / clicks`** — this is NOT a direct API field. Handle division by zero (0 clicks → conversion_rate = 0.0)
- `ctr`: available directly from `metrics.ctr` (Google returns as a decimal, e.g., 0.0776 = 7.76%)
- `avg_cpc`: available from `metrics.average_cpc` in micros — divide by 1,000,000
- Conversion values that are 0 or NULL: store as 0.0 (for lead gen clients, conversion_value is typically 0)

---

## TASK 4: Build the Ingestion Runner Script

Create `act_dashboard/data_pipeline/run_ingestion.py`:

```python
"""
ACT v2 Data Ingestion Runner

Pulls Google Ads data and stores in act_v2_* tables.

Usage (from project root):
    # Single date:
    python -m act_dashboard.data_pipeline.run_ingestion --client oe001 --date 2026-04-11
    
    # Date range (backfill):
    python -m act_dashboard.data_pipeline.run_ingestion --client oe001 --start 2026-01-12 --end 2026-04-11
    
    # Yesterday (default for daily runs):
    python -m act_dashboard.data_pipeline.run_ingestion --client oe001

Prerequisites:
    - Flask app must be stopped (DuckDB lock)
    - Google Ads credentials configured in secrets/google-ads.yaml
"""
```

**Requirements:**
1. Parse command-line arguments: `--client` (required), `--date` (single date), `--start`/`--end` (range), default to yesterday if no date specified
2. Look up the client in `act_v2_clients` to get the `google_ads_customer_id`
3. Instantiate `GoogleAdsDataPipeline` with the client_id and customer_id
4. Call `ingest_date()` or `ingest_date_range()` based on arguments
5. Log progress: which date is being ingested, how many entities found per level, total time taken
6. Handle errors gracefully: if one date fails, log the error and continue to the next date
7. Print summary at the end:
```
========================================
ACT v2 Data Ingestion Complete
========================================
Client: Objection Experts (oe001)
Dates processed: 90
Campaigns: 1 per day
Ad Groups: 4 per day
Keywords: 12 per day
Ads: 3 per day
Search Terms: ~150 per day
Segments: ~50 per day
Total snapshots created: X
Total time: X seconds
========================================
```

---

## TASK 5: Run Initial Backfill

Run the ingestion script for Objection Experts with a 90-day backfill.

**Use yesterday as the end date** (Google Ads data for "today" isn't finalized until midnight). Calculate the start date as 90 days before yesterday.

Example (adjust dates for when this is actually run):
```
python -m act_dashboard.data_pipeline.run_ingestion --client oe001 --start 2026-01-12 --end 2026-04-11
```

**Verify after backfill:**
1. Query `act_v2_snapshots` for row count and date range
2. Verify data exists for each level (campaign, ad_group, keyword, ad)
3. Verify `act_v2_search_terms` has data
4. Verify `act_v2_campaign_segments` has data
5. Spot-check a few metrics_json values against what you'd expect for a small account
6. Verify no duplicate rows (same client_id + date + level + entity_id should be unique)

**If the backfill takes too long** (API rate limiting), reduce to 30 days initially and note that the full 90-day backfill can be done overnight.

---

## TASK 6: Verify and Document

1. **Verify the data is correct:**
   - Pick a recent date and query the ingested data — verify cost values look reasonable (not in millions, which would indicate micros weren't converted)
   - Check that cost values are in GBP (not micros) — a daily cost of £50 is reasonable; £50,000,000 means micros weren't converted
   - Check that conversion rates are decimals (0.0-1.0, not percentages like 3.27)
   - Check that Quality Scores are integers 1-10 (not NULL for enabled keywords)
   - ASK the user to spot-check one date against the Google Ads UI to confirm accuracy

2. **Update `docs/ACT_V2_SCHEMA.md`** — add documentation for the 2 new tables (act_v2_search_terms, act_v2_campaign_segments)

3. **Update the verify script** — add checks for the 2 new tables existing with correct column counts

4. **Git commit** with clear message

---

## DELIVERABLES

1. `act_dashboard/data_pipeline/__init__.py`
2. `act_dashboard/data_pipeline/test_api_connection.py` — API connection test script
3. `act_dashboard/data_pipeline/google_ads_ingestion.py` — main ingestion module
4. `act_dashboard/data_pipeline/run_ingestion.py` — CLI runner script
5. Updated `act_dashboard/db/migrations/create_act_v2_schema.py` — 2 new tables added
6. Updated `act_dashboard/db/migrations/verify_act_v2_schema.py` — 2 new table checks added
7. Updated `docs/ACT_V2_SCHEMA.md` — 2 new tables documented
8. Updated `secrets/google-ads.yaml` with correct credentials (LOCAL ONLY — do NOT commit to git)
9. 90 days of Objection Experts data in act_v2_snapshots
10. Search term data in act_v2_search_terms
11. Segment data in act_v2_campaign_segments
12. Git commit

---

## EXECUTION ORDER

1. **Task 1** — read existing API code, understand patterns (read-only, no changes)
2. **Task 1B** — check for client_secret JSON, run OAuth script to generate `secrets/google-ads.yaml` with correct credentials, test API connection. **STOP HERE if connection fails — ASK the user.**
3. **Task 2** — create 2 new tables, update schema/verify scripts, run them
4. **Task 3** — build the ingestion module
5. **Task 4** — build the runner script
6. **Task 5** — run the 90-day backfill (or 30 days if API is slow)
7. **Task 6** — verify data, update docs, commit

---

## VERIFICATION CHECKLIST

- [ ] `secrets/google-ads.yaml` has correct developer_token (`oDANZ-BXQprTm7_Sg4rjDg`) and login_customer_id (`1527964125`)
- [ ] `test_api_connection.py` passes — campaigns returned from API
- [ ] 2 new tables exist (act_v2_search_terms, act_v2_campaign_segments) with correct columns
- [ ] Updated verify script passes
- [ ] Ingestion module connects to Google Ads API successfully
- [ ] Data exists in act_v2_snapshots for 90 days (or 30 days if API was slow)
- [ ] Data exists for account, campaign, ad_group, keyword, ad levels (verify with `SELECT level, COUNT(*) FROM act_v2_snapshots WHERE client_id='oe001' GROUP BY level`)
- [ ] Data exists in act_v2_search_terms
- [ ] Data exists in act_v2_campaign_segments (device, geo, schedule segments)
- [ ] Cost values are in GBP (not micros)
- [ ] No duplicate rows in snapshots (verify: `SELECT client_id, snapshot_date, level, entity_id, COUNT(*) FROM act_v2_snapshots GROUP BY 1,2,3,4 HAVING COUNT(*) > 1` returns 0 rows)
- [ ] Flask app still starts without errors
- [ ] Git commit created

---

## IMPORTANT NOTES

- **Reuse existing API code PATTERNS only** — the existing code has never been tested live. Use it for reference on GAQL syntax and error handling, but write and test your own code.
- **The credentials file `secrets/google-ads.yaml` is WRONG out of the box.** Task 1B fixes it. Do NOT skip Task 1B.
- Stop Flask before running: `taskkill /IM python.exe /F`
- Google Ads API returns costs in micros — divide by 1,000,000 for GBP
- The GAQL queries in this brief are starting points — verify field names against the Google Ads API documentation and the existing code patterns in `act_autopilot/google_ads_api.py`
- **If API authentication fails, ASK the user for help.** Do not guess at credentials, tokens, or customer IDs.
- If Objection Experts' customer ID doesn't work, ASK before proceeding
- The 90-day backfill may take 10-30 minutes depending on API response times
- For days with zero activity, the API may return no rows — this is normal, not an error
- The `scripts/google_ads_oauth.py` script generates refresh tokens via browser-based OAuth flow — the user must be present to authenticate
- **Security:** The `secrets/` folder is NOT tracked in git (already gitignored). Do NOT commit `secrets/google-ads.yaml` or any credentials file. The git commit at the end should NOT include the secrets folder.

---

**END OF BRIEF**
