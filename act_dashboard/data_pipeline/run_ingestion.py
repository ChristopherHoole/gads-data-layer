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

import argparse
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import duckdb

from act_dashboard.data_pipeline.google_ads_ingestion import GoogleAdsDataPipeline

# Logging
logger = logging.getLogger('act_v2_ingestion')

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = str(PROJECT_ROOT / "warehouse.duckdb")


def main():
    parser = argparse.ArgumentParser(description="ACT v2 Data Ingestion")
    parser.add_argument('--client', required=True, help='ACT client_id (e.g., oe001)')
    parser.add_argument('--date', help='Single date to ingest (YYYY-MM-DD)')
    parser.add_argument('--start', help='Start date for range (YYYY-MM-DD)')
    parser.add_argument('--end', help='End date for range (YYYY-MM-DD)')
    args = parser.parse_args()

    # Look up client
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        row = con.execute(
            "SELECT client_name, google_ads_customer_id FROM act_v2_clients WHERE client_id = ?",
            [args.client]
        ).fetchone()
        con.close()
    except duckdb.IOException:
        print("ERROR: Database is locked. Stop the Flask app first:")
        print("  taskkill /IM python.exe /F")
        sys.exit(1)

    if not row:
        print(f"ERROR: Client '{args.client}' not found in act_v2_clients")
        sys.exit(1)

    client_name, customer_id = row
    logger.info(f"Client: {client_name} ({args.client}), Google Ads ID: {customer_id}")

    # Determine dates
    if args.date:
        start_date = args.date
        end_date = args.date
    elif args.start and args.end:
        start_date = args.start
        end_date = args.end
    else:
        # Default: yesterday
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        start_date = yesterday
        end_date = yesterday

    # Run ingestion
    t0 = time.time()
    pipeline = GoogleAdsDataPipeline(args.client, customer_id)

    try:
        if start_date == end_date:
            pipeline.ingest_date(start_date)
        else:
            pipeline.ingest_date_range(start_date, end_date)
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise
    finally:
        pipeline.close()

    elapsed = time.time() - t0

    # Print summary
    print()
    print('=' * 40)
    print('ACT v2 Data Ingestion Complete')
    print('=' * 40)
    print(f'Client: {client_name} ({args.client})')
    print(f'Date range: {start_date} to {end_date}')
    if pipeline.stats:
        for key, val in pipeline.stats.items():
            print(f'  {key}: {val}')
    print(f'Total time: {elapsed:.1f} seconds')
    print('=' * 40)


if __name__ == '__main__':
    main()
