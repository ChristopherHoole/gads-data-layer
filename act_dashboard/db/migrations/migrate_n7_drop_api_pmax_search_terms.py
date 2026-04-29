"""N7 — Backfill cleanup: drop API-ghost PMax search-term rows.

Companion to the code change in google_ads_ingestion.ingest_pmax_search_terms
that stopped writing per-term PMax rows to act_v2_search_terms (the API's
campaign_search_term_insight resource prohibits cost_micros at term grain,
so every API-ingested PMax row landed with cost=NULL and polluted the
Search Term Review UI). PMax per-term data now comes exclusively from
pmax_csv_ingest.

This migration cleans up the historical ghost rows.

Predicate justification:
  - Every API-ingested PMax row had cost=NULL (Google blocks cost at this
    grain on campaign_search_term_insight).
  - Every CSV-ingested PMax row has cost populated (CSV always carries it).
  - So `campaign_type='PERFORMANCE_MAX' AND cost IS NULL` cleanly separates
    "API ghost row" from "real CSV row" with no false positives.

Idempotent — safe to re-run. Subsequent runs will simply find 0 matching
rows once the code change is live and any pre-CSV PMax days have aged out.

Run:
    python -m act_dashboard.db.migrations.migrate_n7_drop_api_pmax_search_terms
"""
import logging
import os
import sys

import duckdb

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')
LOG_PATH = os.path.join(SCRIPT_DIR, 'migration.log')

logger = logging.getLogger('act_v2_n7')
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); logger.addHandler(sh)
    fh = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8'); fh.setFormatter(fmt); logger.addHandler(fh)


_PREDICATE = "campaign_type = 'PERFORMANCE_MAX' AND cost IS NULL"


def main():
    logger.info('=' * 50)
    logger.info('N7 — Drop API-ghost PMax search-term rows — Starting')
    logger.info('=' * 50)

    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException:
        logger.error('DB locked — stop Flask + watcher first.')
        sys.exit(1)

    try:
        # Dry-run count first so the log records what we'd delete BEFORE
        # the DELETE runs (useful when re-running for audit).
        ghost = con.execute(
            f"SELECT COUNT(*) FROM act_v2_search_terms WHERE {_PREDICATE}"
        ).fetchone()[0]
        kept = con.execute(
            "SELECT COUNT(*) FROM act_v2_search_terms "
            "WHERE campaign_type = 'PERFORMANCE_MAX' AND cost IS NOT NULL"
        ).fetchone()[0]
        logger.info(f'  pre-delete: {ghost} API-ghost PMax rows (cost IS NULL)')
        logger.info(f'  pre-delete: {kept} CSV-derived PMax rows (cost NOT NULL, will be kept)')

        if ghost == 0:
            logger.info('  no rows match — already clean (idempotent no-op)')
        else:
            con.execute(
                f"DELETE FROM act_v2_search_terms WHERE {_PREDICATE}"
            )
            after = con.execute(
                f"SELECT COUNT(*) FROM act_v2_search_terms WHERE {_PREDICATE}"
            ).fetchone()[0]
            kept_after = con.execute(
                "SELECT COUNT(*) FROM act_v2_search_terms "
                "WHERE campaign_type = 'PERFORMANCE_MAX' AND cost IS NOT NULL"
            ).fetchone()[0]
            logger.info(f'  deleted {ghost} ghost rows')
            logger.info(f'  post-delete: {after} ghost rows remaining (expected 0)')
            logger.info(f'  post-delete: {kept_after} CSV-derived rows preserved '
                        f'(expected {kept}, delta should be 0)')
            assert after == 0, 'unexpected residual ghost rows'
            assert kept_after == kept, 'CSV-derived row count changed — abort'

        logger.info('=' * 50)
        logger.info('N7 — Complete')
        logger.info('=' * 50)
    finally:
        con.close()


if __name__ == '__main__':
    main()
