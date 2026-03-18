"""
Rebuild analytics.campaign_features_daily for customer 1254895944.

Uses updated features.py logic that falls back to (1 - search_impression_share) * 100
for impression_share_lost_rank when search_rank_lost_impression_share is not available.

Steps:
1. Rebuild campaign_features_daily in warehouse.duckdb for the last 90 days
2. Copy rebuilt table to warehouse_readonly.duckdb
3. Print row count and sample impression_share_lost_rank values

Run from: gads-data-layer root directory.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

import duckdb

# Resolve project root and add to path so act_lighthouse imports work
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from act_lighthouse.config import ClientConfig, SpendCaps, load_client_config
from act_lighthouse.features import build_campaign_features_daily

CONFIG_PATH = PROJECT_ROOT / "configs" / "client_christopher_hoole.yaml"
DB_PATH = str(PROJECT_ROOT / "warehouse.duckdb")
RO_PATH = str(PROJECT_ROOT / "warehouse_readonly.duckdb")
CUSTOMER_ID = "1254895944"
DAYS_BACK = 90


def main():
    print("=" * 70)
    print("REBUILD campaign_features_daily — customer", CUSTOMER_ID)
    print("=" * 70)

    # Load client config
    cfg = load_client_config(CONFIG_PATH)
    print(f"Client: {cfg.client_id} / customer_id: {cfg.customer_id}")

    # Connect to warehouse (writable), attach readonly as 'ro'
    conn = duckdb.connect(DB_PATH)
    conn.execute(f"ATTACH '{RO_PATH}' AS ro (READ_ONLY)")
    print(f"Connected to {DB_PATH}")

    # Drop existing rows for this customer so we do a clean rebuild
    deleted = conn.execute(
        "DELETE FROM analytics.campaign_features_daily WHERE customer_id = ?",
        [CUSTOMER_ID],
    ).rowcount
    print(f"Deleted {deleted} existing rows for customer {CUSTOMER_ID}")

    # Rebuild for each of the last 90 days
    end_date = date.today()
    start_date = end_date - timedelta(days=DAYS_BACK - 1)

    print(f"\nRebuilding {DAYS_BACK} days: {start_date} to {end_date}")
    total_rows = 0
    for i in range(DAYS_BACK):
        snap = start_date + timedelta(days=i)
        try:
            result = build_campaign_features_daily(conn, cfg, snap)
            total_rows += result.rows_inserted
        except Exception as e:
            print(f"  WARNING: {snap} failed — {e}")

    print(f"\nTotal rows inserted: {total_rows}")

    # Sample impression_share_lost_rank to confirm non-NULL
    print("\nSample impression_share_lost_rank values (10 most recent):")
    rows = conn.execute("""
        SELECT snapshot_date, campaign_id, campaign_name, impression_share_lost_rank
        FROM analytics.campaign_features_daily
        WHERE customer_id = ?
          AND impression_share_lost_rank IS NOT NULL
        ORDER BY snapshot_date DESC
        LIMIT 10
    """, [CUSTOMER_ID]).fetchall()

    if not rows:
        print("  WARNING: All impression_share_lost_rank values are still NULL!")
    else:
        for r in rows:
            print(f"  {r[0]}  campaign_id={r[1]}  name={str(r[2])[:30]:30s}  IS_lost_rank={r[3]:.2f}%")

    null_count = conn.execute("""
        SELECT COUNT(*) FROM analytics.campaign_features_daily
        WHERE customer_id = ?
          AND impression_share_lost_rank IS NULL
    """, [CUSTOMER_ID]).fetchone()[0]
    non_null_count = conn.execute("""
        SELECT COUNT(*) FROM analytics.campaign_features_daily
        WHERE customer_id = ?
          AND impression_share_lost_rank IS NOT NULL
    """, [CUSTOMER_ID]).fetchone()[0]
    print(f"\nNULL rows: {null_count}  |  Non-NULL rows: {non_null_count}")

    conn.close()

    # ── Copy rebuilt table to warehouse_readonly.duckdb ─────────────────────
    print("\n" + "=" * 70)
    print("Copying campaign_features_daily to warehouse_readonly.duckdb")
    print("=" * 70)

    conn_ro = duckdb.connect(RO_PATH)
    conn_ro.execute(f"ATTACH '{DB_PATH}' AS src (READ_ONLY)")

    # Drop existing
    existing = conn_ro.execute(
        "SELECT table_type FROM information_schema.tables "
        "WHERE table_schema = 'analytics' AND table_name = 'campaign_features_daily'"
    ).fetchone()
    if existing:
        if existing[0] == "VIEW":
            conn_ro.execute("DROP VIEW analytics.campaign_features_daily")
        else:
            conn_ro.execute("DROP TABLE analytics.campaign_features_daily")

    # Copy
    conn_ro.execute(
        "CREATE TABLE analytics.campaign_features_daily AS "
        "SELECT * FROM src.analytics.campaign_features_daily"
    )

    count = conn_ro.execute(
        "SELECT COUNT(*) FROM analytics.campaign_features_daily"
    ).fetchone()[0]
    print(f"Copied {count:,} rows to warehouse_readonly.duckdb")

    conn_ro.execute("DETACH src")
    conn_ro.close()

    print("\n" + "=" * 70)
    print("DONE — campaign_features_daily rebuilt and copied to readonly DB.")
    print("=" * 70)


if __name__ == "__main__":
    main()
