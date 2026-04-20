"""N1a — One-off runner: snapshot current negative-keyword lists for all active clients.

Calls only ingest_negative_lists(today) — doesn't re-run campaigns/search_terms/etc.
Use for initial backfill and any manual refresh. The nightly scheduler picks up
the same method via ingest_date().

Run: python -m act_dashboard.data_pipeline.run_negatives_snapshot
"""
import os
import sys
from datetime import date

import duckdb

from act_dashboard.data_pipeline.google_ads_ingestion import GoogleAdsDataPipeline, logger

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')


def main():
    today = date.today().strftime('%Y-%m-%d')
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        clients = con.execute(
            "SELECT client_id, google_ads_customer_id FROM act_v2_clients WHERE active = TRUE ORDER BY client_id"
        ).fetchall()
    finally:
        con.close()

    logger.info(f'=== Negative-list snapshot for {today} — {len(clients)} clients ===')
    for client_id, customer_id in clients:
        logger.info(f'--- {client_id} ({customer_id}) ---')
        pipeline = GoogleAdsDataPipeline(client_id=client_id, customer_id=customer_id)
        try:
            result = pipeline.ingest_negative_lists(today)
            if result['unmatched_names']:
                logger.warning(f"  Unmatched list names for {client_id}: {result['unmatched_names']}")
        except Exception as e:
            logger.error(f'  FAILED {client_id}: {e}')
        finally:
            pipeline.close()


if __name__ == '__main__':
    main()
