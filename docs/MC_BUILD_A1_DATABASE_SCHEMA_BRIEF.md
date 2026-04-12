# MC Build A1 — Database Schema Redesign
**Session:** MC Build A1 — Database Schema
**Date:** 2026-04-12
**Objective:** Design and implement the database schema for the new ACT engine. This is the foundation — everything else depends on having the right tables.

---

## CONTEXT

This is the FIRST session in the ACT build phase. The prototype is complete and signed off across 8 pages. Now we start building the real application.

**Key decisions already made:**
- Keep the old 75-rule engine and its tables in place — do NOT delete anything
- Build new tables alongside the old ones (prefixed `act_v2_` to keep them separate)
- First client: Objection Experts (live Google Ads data via API — Basic Access granted)
- Each client has per-level activation: Off / Monitor Only / Active
- Ecommerce clients will come later (Dental Supplies Direct was just prototype data)

**Source of truth for the logic:**
- `docs/ACT_OPTIMIZATION_ARCHITECTURE_v54.html` — the architecture document
- `docs/ACT_OPTIMIZATION_ARCHITECTURE_SUMMARY.md` — quick reference
- `act_dashboard/prototypes/client-config.html` — the UI that this schema needs to support
- `docs/ACT_PROTOTYPE_STANDARDS.md` — design patterns and standards

**Client Google Ads IDs (for seeding):**
- Objection Experts customer ID: `853-021-1223` (format as `8530211223` in API calls — strip dashes)
- MCC (Manager Account): `152-796-4125` (format as `1527964125`)
- API access level: Basic Access (15,000 operations/day, approved Apr 2026)
- If these IDs don't match reality, ASK before seeding — do not guess

---

## CRITICAL RULES

1. **DO NOT TOUCH EXISTING TABLES.** The old 75-rule engine and all other existing tables must remain untouched and functional. Everything new gets prefixed `act_v2_`.

   **Task 1 will discover what actually exists.** The list below is an ILLUSTRATIVE hint of what may exist — treat the actual discovery output as the source of truth:
   - `rules`, `flags`, `recommendations`, `changes` — likely old engine tables
   - `outreach_*` tables — likely outreach system
   - `jobs` — likely jobs tracker
   - `clients` (if exists) — existing client config
   - `campaigns`, `ad_groups`, `keywords`, `ads`, `shopping_*` — likely synthetic data tables
   
   After Task 1 discovery, work from the ACTUAL list, not this hint. If any existing table has the same name as one you want to create (shouldn't happen since we prefix with `act_v2_`, but check), halt the session and report the conflict back with details — do NOT proceed with creation.

2. **DuckDB database:** `warehouse.duckdb` at project root.

3. **No data migration yet.** Just create the new schema. Real data will be populated in Session A2 (Google Ads API ingestion).

4. **All timestamps are UTC naive.** Use DuckDB `TIMESTAMP` type. Defaults use `CURRENT_TIMESTAMP`.

5. **DuckDB SQL only.** No MySQL/Postgres-specific features. Specific DuckDB gotchas to watch for:
   - No `AUTO_INCREMENT` — use `CREATE SEQUENCE` and `DEFAULT nextval('seq_name')`
   - No `ON UPDATE CURRENT_TIMESTAMP` — handle `updated_at` in application code
   - No partial indexes (`CREATE INDEX ... WHERE` syntax) — create regular indexes
   - Foreign keys: DuckDB supports FK declarations for documentation. **Enforcement behaviour varies by version** — some versions enforce at insert time, others do not. Write schema declaratively with FK constraints as documented, but rely on application code to validate relationships before inserts (do not assume the DB will catch orphaned FK values).
   - `INSERT OR REPLACE INTO` is supported, but behaviour with CHECK constraints and sequences may vary. Verify idempotency by running twice.
   - `CREATE INDEX IF NOT EXISTS` syntax may vary by DuckDB version. If the `IF NOT EXISTS` clause fails, wrap in a try/except in Python or check for existence first using `duckdb_indexes()`.
   - `CHECK` constraints are supported
   - `JSON` type is supported as a first-class type (not just VARCHAR)
   - `TEXT` is an alias for `VARCHAR` — use `VARCHAR` for consistency
   - `PRAGMA table_info('<table>')` returns columns that may vary slightly between DuckDB versions. Inspect actual output rather than assuming column names/count.
   - `duckdb_sequences()` and `duckdb_indexes()` system function output columns may vary by version — inspect the output to find the right column names.

6. **Flask app must be stopped before running migrations.** DuckDB locks the database file when Flask is running. Migration scripts should verify the database isn't locked, and if it is, print a clear error telling the user to run:
   ```
   taskkill /IM python.exe /F
   ```

7. **Document everything.** Every table and every column needs a purpose explained in the code and in the schema docs.

8. **Idempotency required.** All migration scripts must be safely re-runnable. Second run should succeed without errors or duplicate data.

9. **Transactions where possible.** Wrap related DDL operations in transactions so partial failures don't leave the schema half-created.

10. **Logging.** Migration scripts should log both to stdout and to `act_dashboard/db/migrations/migration.log` so there's a permanent record of what happened.

11. **Commit your work.** After all tasks verified, commit with a clear message following the existing commit style in the repo (check `git log --oneline -5` for examples).

---

## TECHNICAL REFERENCE

**Python library:** `duckdb` (already in project dependencies — check existing Flask routes for usage examples)

**Database connection pattern:** Check existing code at `act_dashboard/app.py` or similar to see how the existing Flask app opens `warehouse.duckdb`. Use the same pattern. Do not reinvent it.

**DuckDB system functions for verification:**
- List tables: `SHOW TABLES;` or `SELECT * FROM information_schema.tables WHERE table_schema = 'main';`
- Table columns: `PRAGMA table_info('<table>');`
- List sequences: `SELECT * FROM duckdb_sequences();`
- List indexes: `SELECT * FROM duckdb_indexes();`

**Creation order (critical — do NOT deviate from this):**

The order below ensures every referenced table exists before a table that references it.

1. **All sequences** (`CREATE SEQUENCE IF NOT EXISTS ...`) — before any table
2. **Root tables** (referenced by others, depend on nothing):
   - `act_v2_clients`
   - `act_v2_checks`
3. **Tables referencing only `clients`:**
   - `act_v2_client_level_state`
   - `act_v2_client_settings`
   - `act_v2_campaign_roles`
   - `act_v2_negative_keyword_lists`
   - `act_v2_snapshots`
   - `act_v2_alerts`
4. **Table referencing `clients` + `checks`:**
   - `act_v2_recommendations`
5. **Table referencing `clients` + `checks` + `recommendations`:**
   - `act_v2_executed_actions`
6. **Table referencing `clients` + `recommendations` + `executed_actions`:**
   - `act_v2_monitoring`
7. **All indexes** — after all tables exist

**Interactive scripts:** The rollback script uses `input()` for confirmation, which means it only works when run interactively. If run in a non-interactive context, it will fail or hang. This is intentional — rollback should require human confirmation.

**Python logging:** Use the standard `logging` module with both `StreamHandler` (stdout) and `FileHandler` (`migration.log`, append mode so history persists across runs). Log level INFO.

---

## TASK 1: Discover and Document Existing Database State

Before creating anything, document what already exists in `warehouse.duckdb`.

### Steps

1. **Check if the db/migrations folder path exists:**
   ```
   act_dashboard/db/
   act_dashboard/db/migrations/
   ```
   Create any missing folders AND create both `__init__.py` files:
   - `act_dashboard/db/__init__.py` (empty file)
   - `act_dashboard/db/migrations/__init__.py` (empty file)
   
   Both `__init__.py` files are required for the full Python module path to work:
   `python -m act_dashboard.db.migrations.create_act_v2_schema`
   
   (`act_dashboard/__init__.py` already exists in the project — confirmed.)

2. **Connect to `warehouse.duckdb` and discover tables:**

   Test this query first to make sure DuckDB's information_schema works as expected:
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'main' 
   ORDER BY table_name;
   ```
   
   If this doesn't work, try DuckDB's native syntax:
   ```sql
   SHOW TABLES;
   ```
   
   Use whichever works.

3. **For each existing table, get the column schema:**
   ```sql
   PRAGMA table_info('<table_name>');
   ```
   This is DuckDB's native way to get table info. The output typically includes columns like `cid`, `name`, `type`, `notnull`, `dflt_value`, `pk` — but exact column names may vary by DuckDB version. Inspect the actual output to find the column you need.

4. **Get row counts** for each table (helps identify which are test data vs live data).

5. **Save the complete inventory to `docs/CURRENT_DATABASE_INVENTORY.md`** with:
   - Table list with row counts
   - Full column schema per table
   - Notes on what each table appears to be used for (inferred from name and columns)
   - Any table that conflicts with the proposed `act_v2_*` names (should be none, but check)

   **This file is the pre-migration snapshot of the existing schema.** It does NOT include the new `act_v2_*` tables (those don't exist yet). After migrations run, the verify script will diff against this snapshot to confirm no existing tables were modified.

**This is a READ-ONLY discovery task.** Do not modify anything.

---

## TASK 2: Create the Core Schema (6 Tables)

All tables prefixed `act_v2_`. Use DuckDB syntax throughout.

**IMPORTANT — Sequence ordering:** Some tables have `CREATE SEQUENCE IF NOT EXISTS ...` shown inline with their SQL blocks below for readability. In the actual migration script, ALL sequences must be created BEFORE any table is created — do NOT copy-paste the blocks as-is. The TECHNICAL REFERENCE "Creation order" section above shows the exact order: sequences first, then root tables, then tables with FKs (in dependency order), then indexes.

**IMPORTANT — Level enum values:** The `level` column appears in multiple tables with slightly different allowed values:
- Most tables (`client_level_state`, `client_settings`, `checks`, `recommendations`, `executed_actions`, `monitoring`, `alerts`): use `('account', 'campaign', 'ad_group', 'keyword', 'ad', 'shopping')` — these are the 6 optimization levels
- `act_v2_snapshots`: uses `('account', 'campaign', 'ad_group', 'keyword', 'ad', 'product')` — note `'product'` instead of `'shopping'` because snapshots store individual product data

Rationale: The optimization level is "shopping" (the Shopping-level checks), but individual entity snapshots for Shopping products are stored as `level='product'` since they are product entities. This mismatch is deliberate.

### `act_v2_clients`
Stores client accounts managed by ACT v2.

```sql
CREATE TABLE IF NOT EXISTS act_v2_clients (
    client_id VARCHAR PRIMARY KEY,
    google_ads_customer_id VARCHAR(20) UNIQUE NOT NULL,
    client_name VARCHAR(500) NOT NULL,
    persona VARCHAR(50) NOT NULL CHECK (persona IN ('lead_gen_cpa', 'ecommerce_roas')),
    monthly_budget DECIMAL(18,2) NOT NULL,
    target_cpa DECIMAL(10,2),
    target_roas DECIMAL(10,2),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (
        (persona = 'lead_gen_cpa' AND target_cpa IS NOT NULL AND target_roas IS NULL) OR
        (persona = 'ecommerce_roas' AND target_roas IS NOT NULL AND target_cpa IS NULL)
    )
);
```

Notes:
- `google_ads_customer_id` is UNIQUE — you can't have two clients with the same Google Ads account
- Persona-specific CHECK constraint enforces either CPA or ROAS target (not both, not neither)
- `updated_at` must be set manually in application code on updates (DuckDB doesn't auto-update)

### `act_v2_client_level_state`
Per-client, per-level activation state. Controls whether ACT runs checks on each level.

```sql
CREATE TABLE IF NOT EXISTS act_v2_client_level_state (
    client_id VARCHAR NOT NULL,
    level VARCHAR(20) NOT NULL CHECK (level IN ('account', 'campaign', 'ad_group', 'keyword', 'ad', 'shopping')),
    state VARCHAR(20) NOT NULL DEFAULT 'off' CHECK (state IN ('off', 'monitor_only', 'active')),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100) NOT NULL DEFAULT 'system',
    PRIMARY KEY (client_id, level),
    FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
);
```

### `act_v2_client_settings`
Per-client configuration settings (45 settings from the Client Config page, excluding persona/budget/target which live in `act_v2_clients`).

```sql
CREATE TABLE IF NOT EXISTS act_v2_client_settings (
    client_id VARCHAR NOT NULL,
    setting_key VARCHAR(100) NOT NULL,
    setting_value VARCHAR,
    setting_type VARCHAR(20) NOT NULL CHECK (setting_type IN ('int', 'decimal', 'bool', 'string', 'json')),
    level VARCHAR(20) NOT NULL CHECK (level IN ('account', 'campaign', 'ad_group', 'keyword', 'ad', 'shopping')),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (client_id, setting_key),
    FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
);
```

### `act_v2_campaign_roles`
Assigns roles to campaigns (BD / CP / RT / PR / TS).

```sql
CREATE TABLE IF NOT EXISTS act_v2_campaign_roles (
    client_id VARCHAR NOT NULL,
    google_ads_campaign_id VARCHAR(30) NOT NULL,
    campaign_name VARCHAR(500),
    role VARCHAR(10) NOT NULL CHECK (role IN ('BD', 'CP', 'RT', 'PR', 'TS')),
    role_assigned_by VARCHAR(100) NOT NULL DEFAULT 'auto',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (client_id, google_ads_campaign_id),
    FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
);
```

Role meanings (document in schema docs):
- BD = Brand Defence
- CP = Core Performance
- RT = Retargeting
- PR = Prospecting
- TS = Testing

### `act_v2_negative_keyword_lists`
The 9 standardised negative keyword lists per client.

```sql
CREATE TABLE IF NOT EXISTS act_v2_negative_keyword_lists (
    list_id VARCHAR PRIMARY KEY,
    client_id VARCHAR NOT NULL,
    google_ads_list_id VARCHAR(30),
    list_name VARCHAR(100) NOT NULL,
    word_count INTEGER NOT NULL CHECK (word_count IN (1, 2, 3, 4, 5)),
    match_type VARCHAR(20) NOT NULL CHECK (match_type IN ('exact', 'phrase')),
    keyword_count INTEGER NOT NULL DEFAULT 0,
    last_synced_at TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
);
```

The 9 list types per client (word_count × match_type):
1. 1 WORD phrase
2. 1 WORD exact
3. 2 WORDS phrase
4. 2 WORDS exact
5. 3 WORDS phrase
6. 3 WORDS exact
7. 4 WORDS phrase
8. 4 WORDS exact
9. 5+ WORDS exact (no phrase variant for 5+ — word_count=5 means 5+)

### `act_v2_snapshots`
Daily snapshots of account data pulled from Google Ads API.

**Future note:** This table will grow large over time. For Objection Experts (small account) it's fine. Consider partitioning by client_id + snapshot_date when scaling to multiple large clients.

```sql
CREATE SEQUENCE IF NOT EXISTS seq_act_v2_snapshots;

CREATE TABLE IF NOT EXISTS act_v2_snapshots (
    snapshot_id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_snapshots'),
    client_id VARCHAR NOT NULL,
    snapshot_date DATE NOT NULL,
    level VARCHAR(20) NOT NULL CHECK (level IN ('account', 'campaign', 'ad_group', 'keyword', 'ad', 'product')),
    entity_id VARCHAR(100) NOT NULL,
    entity_name VARCHAR(500),
    parent_entity_id VARCHAR(100),
    metrics_json JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
);

CREATE INDEX IF NOT EXISTS idx_act_v2_snapshots_lookup 
    ON act_v2_snapshots(client_id, snapshot_date, level, entity_id);
```

---

## TASK 3: Create the Engine Output Tables (5 Tables)

### `act_v2_checks`
Reference table defining all checks at each level. Populated once, rarely changes.

```sql
CREATE TABLE IF NOT EXISTS act_v2_checks (
    check_id VARCHAR(100) PRIMARY KEY,
    level VARCHAR(20) NOT NULL CHECK (level IN ('account', 'campaign', 'ad_group', 'keyword', 'ad', 'shopping')),
    check_name VARCHAR(200) NOT NULL,
    description VARCHAR,
    action_category VARCHAR(20) NOT NULL CHECK (action_category IN ('act', 'monitor', 'investigate', 'alert')),
    auto_execute BOOLEAN NOT NULL DEFAULT FALSE,
    cooldown_hours INTEGER,
    active BOOLEAN NOT NULL DEFAULT TRUE
);
```

### Checks to Populate (all 35 from v54)

Use `INSERT OR REPLACE INTO` for idempotency.

**Description column:** For each check below, also populate the `description` column with a concise one-line explanation derived from the v54 architecture document. Example: `account_budget_allocation` → "Reallocates daily budget across campaigns based on performance scoring (7d/14d/30d weighted blend)." Read the relevant v54 sections to write accurate descriptions.

**Account Level (1 check):**

| check_id | check_name | action_category | auto_execute | cooldown_hours |
|----------|-----------|-----------------|--------------|----------------|
| `account_budget_allocation` | Budget Allocation | act | TRUE | 72 |

**Campaign Level — Universal Levers (5 checks):**

| check_id | check_name | action_category | auto_execute | cooldown_hours |
|----------|-----------|-----------------|--------------|----------------|
| `campaign_negative_keywords` | Negative Keywords | act | TRUE | NULL |
| `campaign_device_modifiers` | Device Modifiers | act | TRUE | 168 |
| `campaign_geo_modifiers` | Geographic Modifiers | act | TRUE | 720 |
| `campaign_ad_schedule` | Ad Schedule Modifiers | act | TRUE | 720 |
| `campaign_match_types` | Match Type Migration | investigate | FALSE | NULL |

**Campaign Level — Strategy-Specific (7 checks):**

| check_id | check_name | action_category | auto_execute | cooldown_hours |
|----------|-----------|-----------------|--------------|----------------|
| `campaign_manual_cpc` | Manual CPC | act | TRUE | NULL |
| `campaign_tcpa` | Target CPA Adjustment | investigate | FALSE | 336 |
| `campaign_troas` | Target ROAS Adjustment | investigate | FALSE | 336 |
| `campaign_max_conversions` | Maximize Conversions | monitor | FALSE | NULL |
| `campaign_max_clicks` | Maximize Clicks | act | TRUE | 168 |
| `campaign_pmax` | Performance Max | monitor | FALSE | NULL |
| `campaign_standard_shopping` | Standard Shopping | act | TRUE | NULL |

Note on tCPA/tROAS: the spec says "tightening auto-executes, loosening needs approval". For this table, set `auto_execute=FALSE` because loosening is the more common recommendation. The engine code (built in Session B1) will handle the auto-execution of tightening separately.

**Ad Group Level (4 checks):**

| check_id | check_name | action_category | auto_execute | cooldown_hours |
|----------|-----------|-----------------|--------------|----------------|
| `ag_negative_outlier` | Negative Performance Outlier | investigate | FALSE | NULL |
| `ag_positive_outlier` | Positive Performance Outlier | investigate | FALSE | NULL |
| `ag_budget_concentration` | Budget Concentration Alert | alert | FALSE | NULL |
| `ag_pause_recommendation` | Pause Recommendation | investigate | FALSE | NULL |

**Keyword Level (8 checks):**

| check_id | check_name | action_category | auto_execute | cooldown_hours |
|----------|-----------|-----------------|--------------|----------------|
| `kw_performance_monitoring` | Keyword Performance Monitoring | act | TRUE | NULL |
| `kw_search_term_negatives` | Search Term Mining - Negatives | act | TRUE | NULL |
| `kw_search_term_discovery` | Search Term Mining - Discovery | investigate | FALSE | NULL |
| `kw_quality_score` | Quality Score Monitoring | alert | FALSE | NULL |
| `kw_status_monitoring` | Keyword Status Monitoring | alert | FALSE | NULL |
| `kw_conflicts` | Keyword Conflicts & Cannibalisation | investigate | FALSE | NULL |
| `kw_pause_recommendation` | Keyword Pause Recommendation | investigate | FALSE | NULL |
| `kw_bid_management` | Keyword Bid Management | act | TRUE | 72 |

**Ad Level (6 checks):**

| check_id | check_name | action_category | auto_execute | cooldown_hours |
|----------|-----------|-----------------|--------------|----------------|
| `ad_strength_monitoring` | Ad Strength Monitoring | investigate | FALSE | NULL |
| `ad_rsa_asset_performance` | RSA Asset Performance | investigate | FALSE | NULL |
| `ad_count_per_ad_group` | Ad Count per Ad Group | investigate | FALSE | NULL |
| `ad_performance_comparison` | Ad Performance Comparison | investigate | FALSE | NULL |
| `ad_disapprovals` | Ad Disapprovals | alert | FALSE | NULL |
| `ad_extensions_monitoring` | Ad Extensions Monitoring | investigate | FALSE | NULL |

**Shopping Level (4 checks):**

| check_id | check_name | action_category | auto_execute | cooldown_hours |
|----------|-----------|-----------------|--------------|----------------|
| `shop_search_term_negatives` | Shopping Search Term Mining | act | TRUE | NULL |
| `shop_product_tiers` | Product Performance Tiers | act | TRUE | 72 |
| `shop_product_exclusions` | Product Exclusion Recommendations | investigate | FALSE | NULL |
| `shop_best_seller_maximisation` | Best Seller Budget Maximisation | act | TRUE | 72 |

**Total: 35 checks. Verification script must confirm exactly 35 rows in `act_v2_checks`.**

### `act_v2_recommendations`

```sql
CREATE SEQUENCE IF NOT EXISTS seq_act_v2_recommendations;

CREATE TABLE IF NOT EXISTS act_v2_recommendations (
    recommendation_id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_recommendations'),
    client_id VARCHAR NOT NULL,
    level VARCHAR(20) NOT NULL CHECK (level IN ('account', 'campaign', 'ad_group', 'keyword', 'ad', 'shopping')),
    check_id VARCHAR(100) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    entity_name VARCHAR(500),
    parent_entity_id VARCHAR(100),
    action_category VARCHAR(20) NOT NULL CHECK (action_category IN ('act', 'monitor', 'investigate', 'alert')),
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('low', 'medium', 'high')),
    summary VARCHAR NOT NULL,
    recommendation_text VARCHAR,
    estimated_impact VARCHAR,
    decision_tree_json JSON,
    current_value_json JSON,
    proposed_value_json JSON,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'declined', 'executed', 'rolled_back', 'expired')),
    mode VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (mode IN ('active', 'monitor_only')),
    identified_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actioned_at TIMESTAMP,
    actioned_by VARCHAR(100),
    FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id),
    FOREIGN KEY (check_id) REFERENCES act_v2_checks(check_id)
);

CREATE INDEX IF NOT EXISTS idx_act_v2_recs_client_status 
    ON act_v2_recommendations(client_id, status, identified_at);
```

### `act_v2_executed_actions`

```sql
CREATE SEQUENCE IF NOT EXISTS seq_act_v2_executed_actions;

CREATE TABLE IF NOT EXISTS act_v2_executed_actions (
    action_id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_executed_actions'),
    client_id VARCHAR NOT NULL,
    recommendation_id BIGINT,
    level VARCHAR(20) NOT NULL CHECK (level IN ('account', 'campaign', 'ad_group', 'keyword', 'ad', 'shopping')),
    check_id VARCHAR(100) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    entity_name VARCHAR(500),
    action_type VARCHAR(50) NOT NULL,
    before_value_json JSON,
    after_value_json JSON,
    reason VARCHAR,
    execution_status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (execution_status IN ('success', 'failed', 'pending')),
    error_message VARCHAR,
    executed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    google_ads_api_response JSON,
    FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id),
    FOREIGN KEY (check_id) REFERENCES act_v2_checks(check_id),
    FOREIGN KEY (recommendation_id) REFERENCES act_v2_recommendations(recommendation_id)
);

CREATE INDEX IF NOT EXISTS idx_act_v2_actions_client_date 
    ON act_v2_executed_actions(client_id, executed_at);
```

### `act_v2_monitoring`

Records are kept permanently for history. `resolved_at` marks completion.

```sql
CREATE SEQUENCE IF NOT EXISTS seq_act_v2_monitoring;

CREATE TABLE IF NOT EXISTS act_v2_monitoring (
    monitoring_id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_monitoring'),
    client_id VARCHAR NOT NULL,
    recommendation_id BIGINT,
    action_id BIGINT,
    level VARCHAR(20) NOT NULL CHECK (level IN ('account', 'campaign', 'ad_group', 'keyword', 'ad', 'shopping')),
    entity_id VARCHAR(100) NOT NULL,
    monitoring_type VARCHAR(30) NOT NULL CHECK (monitoring_type IN ('cooldown', 'post_action_observation', 'trend_watch')),
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ends_at TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP,
    health_status VARCHAR(30) NOT NULL DEFAULT 'too_early_to_assess' CHECK (health_status IN ('healthy', 'trending_down', 'too_early_to_assess')),
    consecutive_days_stable INTEGER NOT NULL DEFAULT 0,
    metrics_json JSON,
    FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id),
    FOREIGN KEY (recommendation_id) REFERENCES act_v2_recommendations(recommendation_id),
    FOREIGN KEY (action_id) REFERENCES act_v2_executed_actions(action_id)
);

-- Note: DuckDB does NOT support partial indexes. Using regular index and filtering in queries.
CREATE INDEX IF NOT EXISTS idx_act_v2_monitoring_active 
    ON act_v2_monitoring(client_id, resolved_at);
```

### `act_v2_alerts`

```sql
CREATE SEQUENCE IF NOT EXISTS seq_act_v2_alerts;

CREATE TABLE IF NOT EXISTS act_v2_alerts (
    alert_id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_alerts'),
    client_id VARCHAR NOT NULL,
    level VARCHAR(20) NOT NULL CHECK (level IN ('account', 'campaign', 'ad_group', 'keyword', 'ad', 'shopping')),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
    title VARCHAR NOT NULL,
    description VARCHAR,
    entity_id VARCHAR(100),
    raised_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolution VARCHAR(30) CHECK (resolution IN ('acknowledged', 'auto_resolved', 'approved_fix')),
    FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
);

-- Regular index, not partial (DuckDB limitation)
CREATE INDEX IF NOT EXISTS idx_act_v2_alerts_client 
    ON act_v2_alerts(client_id, resolved_at, raised_at);
```

---

## TASK 4: Create Migration Scripts

Create these files in `act_dashboard/db/migrations/`.

(Note: The `__init__.py` files for `act_dashboard/db/` and `act_dashboard/db/migrations/` are created as part of Task 1 — see Task 1 step 1.)

### `act_dashboard/db/migrations/README.md`
Documents:
- What each migration script does
- Execution order
- How to run them (exact command lines — must be run from project root)
- When to use rollback
- Migration log file location

### `act_dashboard/db/migrations/create_act_v2_schema.py`

Top of file:
```python
"""
ACT v2 Schema Creation Migration

Creates all act_v2_* tables, sequences, indexes, and populates the act_v2_checks
reference table with all 35 checks from the v54 optimization architecture.

Prerequisites:
- Flask app must be stopped (DuckDB file lock)
- Run from project root: python -m act_dashboard.db.migrations.create_act_v2_schema

Idempotent: can be run multiple times safely.

Logs to: act_dashboard/db/migrations/migration.log
"""
```

Requirements:
1. Must be run from project root directory: `python -m act_dashboard.db.migrations.create_act_v2_schema`
2. Connect to `warehouse.duckdb` at project root (use absolute path derived from `__file__`, or the same pattern used by the existing Flask app)
3. Set up logging to both stdout and `act_dashboard/db/migrations/migration.log` using Python's `logging` module with INFO level
4. Check for database lock. If locked, catch the `duckdb.IOException` (or similar) and print clear error:
   ```
   ERROR: Database is locked. Stop the Flask app first:
     taskkill /IM python.exe /F
   Then re-run this migration.
   ```
   Then exit with code 1.
5. Create ALL sequences first (all 5 sequences before any table):
   - `seq_act_v2_snapshots`
   - `seq_act_v2_recommendations`
   - `seq_act_v2_executed_actions`
   - `seq_act_v2_monitoring`
   - `seq_act_v2_alerts`
   Do NOT copy the sequence creation from Task 2-3 SQL blocks inline with tables — separate them out.
6. Create tables in strict dependency order (see TECHNICAL REFERENCE "Creation order"):
   - **Roots (no FK dependencies):** `act_v2_clients`, `act_v2_checks`
   - **References `clients` only:** `act_v2_client_level_state`, `act_v2_client_settings`, `act_v2_campaign_roles`, `act_v2_negative_keyword_lists`, `act_v2_snapshots`, `act_v2_alerts`
   - **References `clients` + `checks`:** `act_v2_recommendations`
   - **References `clients` + `checks` + `recommendations`:** `act_v2_executed_actions`
   - **References `clients` + `recommendations` + `executed_actions`:** `act_v2_monitoring`
7. Create all 5 indexes (after all tables exist):
   - `idx_act_v2_snapshots_lookup`
   - `idx_act_v2_recs_client_status`
   - `idx_act_v2_actions_client_date`
   - `idx_act_v2_monitoring_active`
   - `idx_act_v2_alerts_client`
8. Populate `act_v2_checks` with all 35 checks using `INSERT OR REPLACE INTO` (including description column populated from v54 docs)
9. Print summary at the end:
   ```
   ========================================
   ACT v2 Schema Migration Complete
   ========================================
   Tables created: 11
   Sequences created: 5
   Indexes created: 5
   Checks populated: 35
   ========================================
   ```
10. Wrap table creation in a transaction where possible
11. Must be idempotent (second run succeeds without errors)

### `act_dashboard/db/migrations/seed_objection_experts.py`

**Run command:** `python -m act_dashboard.db.migrations.seed_objection_experts` (from project root)

Requirements:
1. Insert Objection Experts into `act_v2_clients`:
   - `client_id`: 'oe001'
   - `google_ads_customer_id`: '8530211223'
   - `client_name`: 'Objection Experts'
   - `persona`: 'lead_gen_cpa'
   - `monthly_budget`: 1500.00
   - `target_cpa`: 25.00
   - `target_roas`: NULL
   - `active`: TRUE

2. Insert all 6 level states in `act_v2_client_level_state` with state='off':
   ```python
   levels = ['account', 'campaign', 'ad_group', 'keyword', 'ad', 'shopping']
   for level in levels:
       insert level state with state='off'
   ```

3. Insert default settings in `act_v2_client_settings`. **Do not parse HTML** — use this hard-coded list.

   **IMPORTANT:** `client_persona`, `monthly_budget`, `target_cpa`, and `target_roas` are stored in `act_v2_clients` (as columns) — they are NOT in the settings table. The settings table is only for optimization tunables. Do not duplicate these values.

   **Account-Level Settings (9):**
   - `budget_allocation_mode` = 'automatic' (string)
   - `budget_shift_cooldown_hours` = '72' (int)
   - `max_overnight_budget_move_pct` = '10' (int)
   - `performance_scoring_weight_7d` = '50' (int)
   - `performance_scoring_weight_14d` = '30' (int)
   - `performance_scoring_weight_30d` = '20' (int)
   - `signal_window_cpc_days` = '7' (int)
   - `signal_window_cvr_days` = '14' (int)
   - `signal_window_aov_days` = '30' (int)

   **Campaign-Level Settings (16):**
   - `device_mod_min_pct` = '-60' (int)
   - `device_mod_max_pct` = '30' (int)
   - `geo_mod_min_pct` = '-50' (int)
   - `geo_mod_max_pct` = '30' (int)
   - `schedule_mod_min_pct` = '-50' (int)
   - `schedule_mod_max_pct` = '25' (int)
   - `tcpa_adjustment_cooldown_days` = '14' (int)
   - `troas_adjustment_cooldown_days` = '14' (int)
   - `max_cpc_cap_cooldown_days` = '7' (int)
   - `device_bid_cooldown_days` = '7' (int)
   - `geo_bid_cooldown_days` = '30' (int)
   - `schedule_bid_cooldown_days` = '30' (int)
   - `max_single_tcpa_move_pct` = '10' (int)
   - `max_single_troas_move_pct` = '10' (int)
   - `match_type_migration_enabled` = 'true' (bool)
   - `search_partners_optout_check_enabled` = 'true' (bool)

   **Keyword-Level Settings (6):**
   - `keyword_bid_adjustment_per_cycle_pct` = '10' (int)
   - `keyword_bid_cooldown_hours` = '72' (int)
   - `keyword_bid_7day_cap_pct` = '30' (int)
   - `auto_pause_spend_multiplier` = '1' (int)
   - `auto_pause_days_threshold` = '14' (int)
   - `quality_score_alert_threshold` = '4' (int)

   **Ad Group-Level Settings (4):**
   - `negative_outlier_spend_pct` = '30' (int)
   - `negative_outlier_performance_pct` = '50' (int)
   - `positive_outlier_performance_pct` = '40' (int)
   - `pause_inactive_days_threshold` = '30' (int)

   **Ad-Level Settings (6):**
   - `ad_scan_frequency` = 'weekly' (string)
   - `ad_strength_minimum` = 'good' (string)
   - `rsa_asset_low_rated_days_threshold` = '30' (int)
   - `min_ads_per_ad_group` = '3' (int)
   - `ad_performance_comparison_pct` = '30' (int)
   - `ad_minimum_days_live` = '14' (int)

   **Shopping-Level Settings (4):**
   - `product_spend_threshold` = '50.00' (decimal)
   - `product_bid_adjustment_per_cycle_pct` = '10' (int)
   - `product_bid_cooldown_hours` = '72' (int)
   - `product_bid_7day_cap_pct` = '30' (int)

   **Counts:** Account 9 + Campaign 16 + Keyword 6 + Ad Group 4 + Ad 6 + Shopping 4 = **45 settings total**

4. Create the 9 negative keyword list entries for Objection Experts with IDs like:
   - 'oe001-list-1word-phrase', 'oe001-list-1word-exact'
   - 'oe001-list-2word-phrase', 'oe001-list-2word-exact'
   - 'oe001-list-3word-phrase', 'oe001-list-3word-exact'
   - 'oe001-list-4word-phrase', 'oe001-list-4word-exact'
   - 'oe001-list-5word-exact' (no phrase variant for 5+)
   
   Column values for each: `keyword_count = 0` (column is NOT NULL with default 0), `google_ads_list_id = NULL`, `last_synced_at = NULL`.

5. Idempotent — use `INSERT OR REPLACE INTO` for all inserts
6. Log to stdout and `migration.log`
7. Print summary at the end

### `act_dashboard/db/migrations/rollback_act_v2_schema.py`

**Run command:** `python -m act_dashboard.db.migrations.rollback_act_v2_schema` (from project root, interactive only)

Requirements:
1. Connect to `warehouse.duckdb`
2. Check for database lock (same as create script — catch `duckdb.IOException` and print the stop-Flask error)
3. Prompt for confirmation:
   ```
   WARNING: This will DELETE all act_v2_* tables and all data in them.
   This action cannot be undone.
   Type 'YES' (all caps) to confirm: 
   ```
4. If user types anything other than 'YES', abort and print "Rollback cancelled."
5. Drop all tables in dependency order (children first, then parents) — see order below
6. Drop all 5 sequences (order doesn't matter — all tables that referenced them are now dropped):
   - `DROP SEQUENCE IF EXISTS seq_act_v2_snapshots;`
   - `DROP SEQUENCE IF EXISTS seq_act_v2_recommendations;`
   - `DROP SEQUENCE IF EXISTS seq_act_v2_executed_actions;`
   - `DROP SEQUENCE IF EXISTS seq_act_v2_monitoring;`
   - `DROP SEQUENCE IF EXISTS seq_act_v2_alerts;`
7. Print summary of what was dropped (table count + sequence count)
8. Log to stdout and `migration.log` (append mode so log history is preserved across runs)

Table drop order (children first):
1. `act_v2_monitoring` (FKs to recommendations, executed_actions, clients)
2. `act_v2_executed_actions` (FKs to recommendations, checks, clients)
3. `act_v2_recommendations` (FKs to checks, clients)
4. `act_v2_alerts` (FK to clients)
5. `act_v2_snapshots` (FK to clients)
6. `act_v2_negative_keyword_lists` (FK to clients)
7. `act_v2_campaign_roles` (FK to clients)
8. `act_v2_client_settings` (FK to clients)
9. `act_v2_client_level_state` (FK to clients)
10. `act_v2_checks` (no dependents — all referencing tables already dropped)
11. `act_v2_clients` (no dependents — all referencing tables already dropped)

Note: `monitoring` must drop before `executed_actions` (since monitoring has FK to executed_actions), and both must drop before `recommendations` (both have FKs to recommendations). Similarly, `recommendations` must drop before `checks`.

---

## TASK 5: Create Verification Script

Create `act_dashboard/db/migrations/verify_act_v2_schema.py`:

**Run command:** `python -m act_dashboard.db.migrations.verify_act_v2_schema` (from project root)

Requirements:
1. Connect to `warehouse.duckdb` — handle database lock the same way as the create script (catch `duckdb.IOException` and print the stop-Flask error)
2. For each expected table, verify it exists using `SHOW TABLES` or `information_schema`
3. For each expected table, verify column count matches the spec using `PRAGMA table_info('<table>')`:

   | Table | Expected Column Count |
   |-------|----------------------|
   | `act_v2_clients` | 10 |
   | `act_v2_client_level_state` | 5 |
   | `act_v2_client_settings` | 6 |
   | `act_v2_campaign_roles` | 6 |
   | `act_v2_negative_keyword_lists` | 8 |
   | `act_v2_snapshots` | 9 |
   | `act_v2_checks` | 8 |
   | `act_v2_recommendations` | 20 |
   | `act_v2_executed_actions` | 15 |
   | `act_v2_monitoring` | 13 |
   | `act_v2_alerts` | 11 |

4. Run these data checks:
   - `SELECT COUNT(*) FROM act_v2_checks` — must equal 35
   - `SELECT COUNT(*) FROM act_v2_clients WHERE client_id = 'oe001'` — must equal 1
   - `SELECT COUNT(*) FROM act_v2_client_level_state WHERE client_id = 'oe001'` — must equal 6
   - `SELECT COUNT(*) FROM act_v2_client_level_state WHERE client_id = 'oe001' AND state != 'off'` — must equal 0
   - `SELECT COUNT(*) FROM act_v2_client_settings WHERE client_id = 'oe001'` — must equal 45
   - `SELECT COUNT(*) FROM act_v2_negative_keyword_lists WHERE client_id = 'oe001'` — must equal 9
5. Verify all 5 sequences exist using DuckDB's system function `duckdb_sequences()`. Query example: `SELECT * FROM duckdb_sequences();` — inspect the output to find the correct column name for the sequence identifier (may be `sequence_name`, `name`, or similar depending on DuckDB version). Expected sequences:
   - `seq_act_v2_snapshots`
   - `seq_act_v2_recommendations`
   - `seq_act_v2_executed_actions`
   - `seq_act_v2_monitoring`
   - `seq_act_v2_alerts`
6. Verify all 5 indexes exist using DuckDB's system function `duckdb_indexes()`. Query example: `SELECT * FROM duckdb_indexes();` — inspect the output to find the correct column name. Expected indexes:
   - `idx_act_v2_snapshots_lookup`
   - `idx_act_v2_recs_client_status`
   - `idx_act_v2_actions_client_date`
   - `idx_act_v2_monitoring_active`
   - `idx_act_v2_alerts_client`
7. Print PASS or FAIL for each check
8. Exit code 0 if all pass, 1 if any fail

Output format (illustrative example, actual check count will be higher):
```
========================================
ACT v2 Schema Verification
========================================
[PASS] Table act_v2_clients exists
[PASS] Table act_v2_clients has 10 columns
[PASS] Table act_v2_checks exists
[PASS] act_v2_checks has 35 rows
[PASS] Objection Experts client exists
[PASS] All 6 level states exist and are 'off'
[PASS] 45 settings seeded
[PASS] 9 negative keyword lists created
[PASS] Sequence seq_act_v2_snapshots exists
[PASS] Index idx_act_v2_recs_client_status exists
...
========================================
Result: ALL PASSED
========================================
```

The verify script should run approximately 30+ checks in total (11 tables exist + 11 table column counts + 6 data counts + 5 sequences + 5 indexes).

---

## TASK 6: Document the Schema

Create `docs/ACT_V2_SCHEMA.md`:

Sections:
1. **Overview** — purpose of the v2 schema, how it relates to the v54 architecture
2. **Table List** — all 11 act_v2_* tables with one-line descriptions, grouped by functional area:
   - **Client Configuration:** `act_v2_clients`, `act_v2_client_level_state`, `act_v2_client_settings`, `act_v2_campaign_roles`, `act_v2_negative_keyword_lists`
   - **Data Ingestion:** `act_v2_snapshots`
   - **Engine Reference:** `act_v2_checks`
   - **Engine Output:** `act_v2_recommendations`, `act_v2_executed_actions`, `act_v2_monitoring`, `act_v2_alerts`
3. **Entity Relationship Diagram** — mermaid diagram showing relationships between tables
4. **Table Details** — for each table:
   - Purpose
   - Full column list with types, constraints, defaults
   - Indexes
   - Example INSERT statement
   - Example common queries
5. **Workflow Examples** — how the tables interact for:
   - A new client being onboarded
   - A recommendation being created, approved, and executed
   - An action going through monitoring
   - An alert being raised and resolved
6. **Important Notes:**
   - DuckDB-specific quirks (no ON UPDATE, no partial indexes, etc.)
   - `updated_at` must be set manually in application code
   - JSON columns store structured data
7. **Future Considerations:**
   - Partitioning strategy for `act_v2_snapshots`
   - Archive strategy for old recommendations
   - Migration path to PostgreSQL if needed

---

## DELIVERABLES

1. `docs/CURRENT_DATABASE_INVENTORY.md`
2. `act_dashboard/db/__init__.py` (empty, for module path)
3. `act_dashboard/db/migrations/__init__.py` (empty, for module path)
4. `act_dashboard/db/migrations/README.md`
5. `act_dashboard/db/migrations/create_act_v2_schema.py`
6. `act_dashboard/db/migrations/seed_objection_experts.py`
7. `act_dashboard/db/migrations/rollback_act_v2_schema.py`
8. `act_dashboard/db/migrations/verify_act_v2_schema.py`
9. `docs/ACT_V2_SCHEMA.md`
10. All 11 `act_v2_*` tables created in `warehouse.duckdb`
11. Objection Experts seeded with all levels OFF and 45 settings
12. Verification script passes 100%
13. Git commit with clear message

---

## EXECUTION ORDER

1. **Task 1** — discover existing schema → create `act_dashboard/db/__init__.py` and `act_dashboard/db/migrations/__init__.py` if missing → write `CURRENT_DATABASE_INVENTORY.md` → verify no name conflicts with `act_v2_*`
2. **Write create_act_v2_schema.py** → run it → verify tables created
3. **Write seed_objection_experts.py** → run it → verify data inserted
4. **Write rollback_act_v2_schema.py** → DO NOT RUN IT (emergency only)
5. **Write verify_act_v2_schema.py** → run it → must pass all checks
6. **Test idempotency** — run `create_act_v2_schema.py` a SECOND time → must succeed with no errors
7. **Test idempotency** — run `seed_objection_experts.py` a SECOND time → must succeed with no duplicates
8. **Re-run verify_act_v2_schema.py** → must still pass all checks after idempotency tests
9. **Write ACT_V2_SCHEMA.md** documentation
10. **Start Flask app** (`python act_dashboard/app.py` or equivalent) → confirm no errors in startup log → stop the app again
11. **Git commit** everything

---

## VERIFICATION CHECKLIST

Before considering this session done, ALL must pass:

- [ ] CURRENT_DATABASE_INVENTORY.md exists and documents all existing tables
- [ ] `act_dashboard/db/__init__.py` exists (empty, for module path)
- [ ] `act_dashboard/db/migrations/__init__.py` exists (empty, for module path)
- [ ] `act_dashboard/db/migrations/README.md` exists and documents all migration scripts
- [ ] All 11 `act_v2_*` tables exist in warehouse.duckdb
- [ ] All 5 sequences exist (`seq_act_v2_snapshots`, `seq_act_v2_recommendations`, `seq_act_v2_executed_actions`, `seq_act_v2_monitoring`, `seq_act_v2_alerts`)
- [ ] All 5 indexes exist
- [ ] `act_v2_checks` has exactly 35 rows
- [ ] Objection Experts exists with `client_id='oe001'`
- [ ] Objection Experts has 6 level states, all `'off'`
- [ ] Objection Experts has 9 negative keyword list entries
- [ ] Objection Experts has 45 settings entries
- [ ] `verify_act_v2_schema.py` passes all checks
- [ ] Running `create_act_v2_schema.py` a SECOND time succeeds without errors (idempotency)
- [ ] Running `seed_objection_experts.py` a SECOND time succeeds without duplicates (idempotency)
- [ ] `migration.log` contains clear log of all operations performed
- [ ] No existing tables in warehouse.duckdb were modified (diff against CURRENT_DATABASE_INVENTORY.md)
- [ ] Flask app starts without errors after migrations (check startup log, stop app afterwards)
- [ ] `docs/ACT_V2_SCHEMA.md` exists and is complete
- [ ] Git commit created with clear message

**If ANY item fails, debug and fix. Do not consider this session done until all pass.**

---

## IMPORTANT NOTES

- This session is PURELY database work. No UI, no Flask routes, no engine logic.
- The existing Flask app should still work unchanged after this session.
- Stop Flask before running any migration: `taskkill /IM python.exe /F`
- DuckDB quirks (see full list in CRITICAL RULES section 5):
  - No `ON UPDATE CURRENT_TIMESTAMP` — handle in app code
  - No partial indexes — use regular indexes
  - No `AUTO_INCREMENT` — use sequences
  - `INSERT OR REPLACE INTO` is supported (behaviour with CHECK constraints may vary — verify idempotency by running twice)
  - Foreign key enforcement varies by DuckDB version — declare them but validate in app code
  - `TEXT` is an alias for `VARCHAR` — use `VARCHAR`
  - JSON is a first-class type
  - `CREATE INDEX IF NOT EXISTS` syntax may vary — handle gracefully if it fails
- If Objection Experts' Google Ads customer ID (`8530211223`) is wrong, STOP and ask before seeding
- Settings list in seed script is hard-coded (45 settings) — do NOT parse HTML from the prototype
- Dropping tables in DuckDB automatically drops their indexes (rollback script doesn't need to drop indexes separately)

---

**END OF BRIEF**
