"""
Orchestration script: pull Google Ads data + copy to readonly DB.

Usage:
    python tools/run_ingestion.py --customer-id 1254895944 --date 2026-03-07 --mode live
    python tools/run_ingestion.py --customer-id 1254895944 --date 2026-03-07 --mode mock

Run from: gads-data-layer root (with venv active)
"""

import argparse
import importlib.util
import sys
from datetime import datetime
from pathlib import Path

# Ensure project root and src are on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import duckdb
from gads_pipeline.v1_runner import (
    pull_campaign_data,
    pull_keyword_data,
    pull_search_term_data,
    pull_ad_group_data,
    pull_ad_data,
)

# Load copy_all_to_readonly from file (scripts/ has no __init__.py)
_copy_spec = importlib.util.spec_from_file_location(
    "copy_all_to_readonly",
    PROJECT_ROOT / "scripts" / "copy_all_to_readonly.py",
)
_copy_mod = importlib.util.module_from_spec(_copy_spec)
_copy_spec.loader.exec_module(_copy_mod)
copy_all_to_readonly = _copy_mod.copy_all_to_readonly

TABLES = [
    "campaign_daily",
    "keyword_daily",
    "search_term_daily",
    "ad_group_daily",
    "ad_daily",
]


def get_row_count(db_path: str, table: str) -> int:
    """Return row count for analytics.<table> in given DB, or 0 if missing."""
    try:
        conn = duckdb.connect(db_path)
        count = conn.execute(f"SELECT COUNT(*) FROM analytics.{table}").fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


def print_summary(warehouse_counts: dict, readonly_counts: dict):
    """Print a formatted summary table of row counts."""
    col_w = 22
    print("\n" + "=" * 60)
    print("INGESTION SUMMARY")
    print("=" * 60)
    print(f"{'Table':<{col_w}} {'warehouse.duckdb':>16} {'readonly.duckdb':>16}")
    print("-" * 60)
    for table in TABLES:
        w = warehouse_counts.get(table, 0)
        r = readonly_counts.get(table, 0)
        print(f"{table:<{col_w}} {w:>16,} {r:>16,}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Run Google Ads ingestion pipeline")
    parser.add_argument("--customer-id", required=True, help="Google Ads customer ID")
    parser.add_argument("--date", required=True, help="Date to pull (YYYY-MM-DD)")
    parser.add_argument(
        "--mode",
        choices=["mock", "live"],
        default="mock",
        help="mock = no API calls; live = real Google Ads API",
    )
    args = parser.parse_args()

    snapshot_date = datetime.strptime(args.date, "%Y-%m-%d")
    start_date = snapshot_date.strftime("%Y-%m-%d")
    end_date = snapshot_date.strftime("%Y-%m-%d")

    print(f"\n{'=' * 60}")
    print(f"INGESTION PIPELINE — {args.date} — MODE: {args.mode.upper()}")
    print(f"Customer ID: {args.customer_id}")
    print(f"{'=' * 60}\n")

    # ── STEP 1: Pull data into warehouse.duckdb ────────────────────────────
    print("[Step 1/3] Pulling data into warehouse.duckdb...")
    conn = duckdb.connect("warehouse.duckdb")
    conn.execute("CREATE SCHEMA IF NOT EXISTS analytics")

    pull_campaign_data(args.customer_id, start_date, end_date, conn, args.mode)
    pull_keyword_data(args.customer_id, start_date, end_date, conn, args.mode)
    pull_search_term_data(args.customer_id, start_date, end_date, conn, args.mode)
    pull_ad_group_data(args.customer_id, start_date, end_date, conn, args.mode)
    pull_ad_data(args.customer_id, start_date, end_date, conn, args.mode)

    conn.close()
    print("[Step 1/3] Pull complete.\n")

    # ── STEP 2: Copy to warehouse_readonly.duckdb ──────────────────────────
    print("[Step 2/3] Copying tables to warehouse_readonly.duckdb...")
    copy_all_to_readonly()
    print("[Step 2/3] Copy complete.\n")

    # ── STEP 3: Print summary ──────────────────────────────────────────────
    print("[Step 3/3] Collecting row counts...")
    warehouse_counts = {t: get_row_count("warehouse.duckdb", t) for t in TABLES}
    readonly_counts = {t: get_row_count("warehouse_readonly.duckdb", t) for t in TABLES}

    print_summary(warehouse_counts, readonly_counts)

    if args.mode == "mock":
        print("\nNOTE: Mock mode — no API calls made, no data inserted.")
    else:
        print("\nLive ingestion complete.")


if __name__ == "__main__":
    main()
