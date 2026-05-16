"""N10 — Create kw_st_history table for the KW + Search Term History Viewer.

Brief: docs/BRIEF_KW_ST_HISTORY_VIEWER.md (Phase 1 schema).

One row per (client_id, term, type). Aggregates impressions/clicks/cost/
conversions across the full GAds history; tracks the (campaign, ad_group)
pair with the highest impressions (`old_campaign`, `old_ad_group`) so
Chris can see the term's historical home. Mapping fields
(`proposed_ad_group`, `proposal_method`, `proposal_rationale`,
`ai_cached_at`) are populated by Phase 2's mapping pipeline.

DBD-only for v1 — `client_id` defaults aren't enforced here but the
ingest + mapping + UI all guard on ALLOWED_CLIENTS_V1 = {'dbd001'}.

Idempotent: probes the table first and exits clean if already present.

Run:
    python -m act_dashboard.db.migrations.migrate_n10_kw_st_history
"""
from __future__ import annotations

import logging
import os
import sys

import duckdb

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')
LOG_PATH = os.path.join(SCRIPT_DIR, 'migration.log')

logger = logging.getLogger('act_n10_kw_st_history')
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); logger.addHandler(sh)
    fh = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8'); fh.setFormatter(fmt); logger.addHandler(fh)


DDL_KW_ST_HISTORY = """
CREATE TABLE IF NOT EXISTS kw_st_history (
    client_id              VARCHAR NOT NULL,
    term                   VARCHAR NOT NULL,
    term_raw               VARCHAR,
    type                   VARCHAR NOT NULL
        CHECK (type IN ('keyword', 'search_term', 'both')),
    impressions_total      BIGINT  DEFAULT 0,
    clicks_total           BIGINT  DEFAULT 0,
    cost_total             DOUBLE  DEFAULT 0.0,
    conversions_total      DOUBLE  DEFAULT 0.0,
    old_campaign           VARCHAR,
    old_ad_group           VARCHAR,
    is_brand_campaign      BOOLEAN DEFAULT FALSE,
    in_new_ex              BOOLEAN DEFAULT FALSE,
    current_new_ex_ad_group VARCHAR,
    proposed_ad_group      VARCHAR,
    proposal_method        VARCHAR
        CHECK (proposal_method IS NULL OR proposal_method IN
               ('rule', 'ai', 'manual', 'skip_brand', 'skip_low_volume')),
    proposal_rationale     VARCHAR,
    ai_cached_at           TIMESTAMP,
    first_seen             DATE,
    last_updated           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (client_id, term, type)
);
"""

# Per-ingest staging tables (recreated each run). Kept simple — Phase 1
# aggregates from raw CSV rows; Phase 2 layers mapping fields on top.
DDL_STAGING_DROP = """
DROP TABLE IF EXISTS _stg_kw_history_st_raw;
DROP TABLE IF EXISTS _stg_kw_history_kw_raw;
DROP TABLE IF EXISTS _stg_kw_history_ag_raw;
"""


def main() -> int:
    logger.info('=' * 60)
    logger.info('N10 — create kw_st_history table')
    logger.info('=' * 60)
    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException:
        logger.error('Database locked. Stop the Flask app first.')
        return 1
    try:
        # Probe — is the table already there?
        exists = con.execute(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'kw_st_history' LIMIT 1"
        ).fetchone()
        if exists:
            logger.info('kw_st_history already exists; no-op.')
            return 0

        con.execute(DDL_KW_ST_HISTORY)
        # Drop any orphan staging tables from prior runs.
        con.execute(DDL_STAGING_DROP)
        n = con.execute(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_name = 'kw_st_history'"
        ).fetchone()[0]
        if n != 1:
            logger.error('Post-create probe failed (n=%s). Migration aborted.', n)
            return 1
        logger.info('kw_st_history created successfully.')
        return 0
    except Exception as e:  # noqa: BLE001
        logger.exception('Migration failed: %s', e)
        return 1
    finally:
        con.close()


if __name__ == '__main__':
    sys.exit(main())
