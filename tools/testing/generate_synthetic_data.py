"""
Synthetic Data Generator for Lighthouse Testing

Inserts data into snap_campaign_daily table (the base table for analytics.campaign_daily view).

Usage:
    python tools/testing/generate_synthetic_data.py --customer-id 9999999999 --days 60
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List

# Add src to path so we can import gads_pipeline modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from gads_pipeline.warehouse_duckdb import (
    connect_warehouse,
    init_warehouse,
    insert_snap_campaign_daily,
)


def generate_stable_campaign(
    campaign_id: int,
    customer_id: str,
    start_date: date,
    days: int,
    run_id: str,
    base_impressions: int = 1500,
    base_ctr: float = 0.05,
    base_cvr: float = 0.08,
    base_cpc_micros: int = 1_200_000,
    base_aov: float = 50.0,
) -> List[Dict]:
    """Generate stable campaign with consistent performance."""
    rows = []
    for i in range(days):
        d = start_date + timedelta(days=i)
        ingested_at = datetime(d.year, d.month, d.day, 12, 0, 0)

        # Add small random noise (±10%)
        impressions = int(base_impressions * random.uniform(0.9, 1.1))
        clicks = int(impressions * base_ctr * random.uniform(0.95, 1.05))
        conversions = clicks * base_cvr * random.uniform(0.95, 1.05)
        cost_micros = clicks * base_cpc_micros
        conversion_value = conversions * base_aov * random.uniform(0.95, 1.05)

        rows.append(
            {
                "run_id": run_id,
                "ingested_at": ingested_at,
                "customer_id": customer_id,
                "snapshot_date": d,
                "campaign_id": campaign_id,
                "campaign_name": f"Campaign_{campaign_id}_STABLE",
                "campaign_status": "ENABLED",
                "channel_type": "Search",
                "impressions": impressions,
                "clicks": clicks,
                "cost_micros": cost_micros,
                "conversions": conversions,
                "conversions_value": conversion_value,
                "all_conversions": conversions * 1.1,
                "all_conversions_value": conversion_value * 1.1,
            }
        )

    return rows


def generate_cost_spike_campaign(
    campaign_id: int,
    customer_id: str,
    start_date: date,
    days: int,
    run_id: str,
) -> List[Dict]:
    """Generate campaign with 60% cost spike in last day."""
    rows = generate_stable_campaign(campaign_id, customer_id, start_date, days, run_id)

    # Spike last day by 60%
    if len(rows) > 0:
        last = rows[-1]
        last["impressions"] = int(last["impressions"] * 1.6)
        last["clicks"] = int(last["clicks"] * 1.6)
        last["cost_micros"] = int(last["cost_micros"] * 1.6)
        last["campaign_name"] = f"Campaign_{campaign_id}_COST_SPIKE"

    return rows


def generate_cost_drop_campaign(
    campaign_id: int,
    customer_id: str,
    start_date: date,
    days: int,
    run_id: str,
) -> List[Dict]:
    """Generate campaign with 60% cost drop in last day."""
    rows = generate_stable_campaign(campaign_id, customer_id, start_date, days, run_id)

    # Drop last day by 60%
    if len(rows) > 0:
        last = rows[-1]
        last["impressions"] = int(last["impressions"] * 0.4)
        last["clicks"] = int(last["clicks"] * 0.4)
        last["cost_micros"] = int(last["cost_micros"] * 0.4)
        last["campaign_name"] = f"Campaign_{campaign_id}_COST_DROP"

    return rows


def generate_ctr_drop_campaign(
    campaign_id: int,
    customer_id: str,
    start_date: date,
    days: int,
    run_id: str,
) -> List[Dict]:
    """Generate campaign with 30% CTR drop in last 7 days."""
    base_ctr = 0.05
    rows = []

    for i in range(days):
        d = start_date + timedelta(days=i)
        ingested_at = datetime(d.year, d.month, d.day, 12, 0, 0)

        # Drop CTR by 30% in last 7 days
        if i >= days - 7:
            ctr = base_ctr * 0.7 * random.uniform(0.95, 1.05)
        else:
            ctr = base_ctr * random.uniform(0.95, 1.05)

        impressions = int(1500 * random.uniform(0.9, 1.1))
        clicks = int(impressions * ctr)
        conversions = clicks * 0.08 * random.uniform(0.95, 1.05)
        cost_micros = clicks * 1_200_000
        conversion_value = conversions * 50.0 * random.uniform(0.95, 1.05)

        rows.append(
            {
                "run_id": run_id,
                "ingested_at": ingested_at,
                "customer_id": customer_id,
                "snapshot_date": d,
                "campaign_id": campaign_id,
                "campaign_name": f"Campaign_{campaign_id}_CTR_DROP",
                "campaign_status": "ENABLED",
                "channel_type": "Search",
                "impressions": impressions,
                "clicks": clicks,
                "cost_micros": cost_micros,
                "conversions": conversions,
                "conversions_value": conversion_value,
                "all_conversions": conversions * 1.1,
                "all_conversions_value": conversion_value * 1.1,
            }
        )

    return rows


def generate_cvr_drop_campaign(
    campaign_id: int,
    customer_id: str,
    start_date: date,
    days: int,
    run_id: str,
) -> List[Dict]:
    """Generate campaign with 30% CVR drop in last 14 days."""
    base_cvr = 0.08
    rows = []

    for i in range(days):
        d = start_date + timedelta(days=i)
        ingested_at = datetime(d.year, d.month, d.day, 12, 0, 0)

        # Drop CVR by 30% in last 14 days
        if i >= days - 14:
            cvr = base_cvr * 0.7 * random.uniform(0.95, 1.05)
        else:
            cvr = base_cvr * random.uniform(0.95, 1.05)

        impressions = int(1500 * random.uniform(0.9, 1.1))
        clicks = int(impressions * 0.05 * random.uniform(0.95, 1.05))
        conversions = clicks * cvr
        cost_micros = clicks * 1_200_000
        conversion_value = conversions * 50.0 * random.uniform(0.95, 1.05)

        rows.append(
            {
                "run_id": run_id,
                "ingested_at": ingested_at,
                "customer_id": customer_id,
                "snapshot_date": d,
                "campaign_id": campaign_id,
                "campaign_name": f"Campaign_{campaign_id}_CVR_DROP",
                "campaign_status": "ENABLED",
                "channel_type": "Search",
                "impressions": impressions,
                "clicks": clicks,
                "cost_micros": cost_micros,
                "conversions": conversions,
                "conversions_value": conversion_value,
                "all_conversions": conversions * 1.1,
                "all_conversions_value": conversion_value * 1.1,
            }
        )

    return rows


def generate_volatile_campaign(
    campaign_id: int,
    customer_id: str,
    start_date: date,
    days: int,
    run_id: str,
) -> List[Dict]:
    """Generate campaign with high volatility (CV > 0.6)."""
    rows = []

    for i in range(days):
        d = start_date + timedelta(days=i)
        ingested_at = datetime(d.year, d.month, d.day, 12, 0, 0)

        # High variance in daily performance (±50%)
        impressions = int(1500 * random.uniform(0.5, 1.5))
        clicks = int(impressions * 0.05 * random.uniform(0.5, 1.5))
        conversions = clicks * 0.08 * random.uniform(0.5, 1.5)
        cost_micros = clicks * int(1_200_000 * random.uniform(0.5, 1.5))
        conversion_value = conversions * 50.0 * random.uniform(0.5, 1.5)

        rows.append(
            {
                "run_id": run_id,
                "ingested_at": ingested_at,
                "customer_id": customer_id,
                "snapshot_date": d,
                "campaign_id": campaign_id,
                "campaign_name": f"Campaign_{campaign_id}_VOLATILE",
                "campaign_status": "ENABLED",
                "channel_type": "Search",
                "impressions": impressions,
                "clicks": clicks,
                "cost_micros": cost_micros,
                "conversions": conversions,
                "conversions_value": conversion_value,
                "all_conversions": conversions * 1.1,
                "all_conversions_value": conversion_value * 1.1,
            }
        )

    return rows


def generate_low_data_campaign(
    campaign_id: int,
    customer_id: str,
    start_date: date,
    days: int,
    run_id: str,
) -> List[Dict]:
    """Generate campaign with low volume (fails low_data thresholds)."""
    rows = []

    for i in range(days):
        d = start_date + timedelta(days=i)
        ingested_at = datetime(d.year, d.month, d.day, 12, 0, 0)

        # Very low volume
        impressions = int(100 * random.uniform(0.8, 1.2))  # < 500/7d
        clicks = int(impressions * 0.03 * random.uniform(0.8, 1.2))  # < 30/7d
        conversions = clicks * 0.05 * random.uniform(0.8, 1.2)  # < 15/30d
        cost_micros = clicks * 1_200_000
        conversion_value = conversions * 50.0 * random.uniform(0.8, 1.2)

        rows.append(
            {
                "run_id": run_id,
                "ingested_at": ingested_at,
                "customer_id": customer_id,
                "snapshot_date": d,
                "campaign_id": campaign_id,
                "campaign_name": f"Campaign_{campaign_id}_LOW_DATA",
                "campaign_status": "ENABLED",
                "channel_type": "Search",
                "impressions": impressions,
                "clicks": clicks,
                "cost_micros": cost_micros,
                "conversions": conversions,
                "conversions_value": conversion_value,
                "all_conversions": conversions * 1.1,
                "all_conversions_value": conversion_value * 1.1,
            }
        )

    return rows


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic campaign data for Lighthouse testing"
    )
    parser.add_argument(
        "--customer-id", required=True, help="Customer ID (e.g., 9999999999)"
    )
    parser.add_argument(
        "--days", type=int, default=60, help="Number of days to generate (default: 60)"
    )
    parser.add_argument(
        "--db",
        default="warehouse.duckdb",
        help="Database path (default: warehouse.duckdb)",
    )

    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    end_date = date.today() - timedelta(days=1)  # Yesterday
    start_date = end_date - timedelta(days=args.days - 1)
    run_id = f"SYNTHETIC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print(f"Generating synthetic data...")
    print(f"  Customer ID: {args.customer_id}")
    print(f"  Date range: {start_date} to {end_date}")
    print(f"  Run ID: {run_id}")

    # Connect and ensure tables exist
    conn = connect_warehouse(db_path)
    init_warehouse(conn)

    # Generate different scenarios
    scenarios = [
        (2001, generate_stable_campaign, "STABLE (baseline)"),
        (2002, generate_stable_campaign, "STABLE (baseline)"),
        (2003, generate_cost_spike_campaign, "COST_SPIKE (+60% last day)"),
        (2004, generate_cost_drop_campaign, "COST_DROP (-60% last day)"),
        (2005, generate_ctr_drop_campaign, "CTR_DROP (-30% last 7 days)"),
        (2006, generate_cvr_drop_campaign, "CVR_DROP (-30% last 14 days)"),
        (2007, generate_volatile_campaign, "VOLATILE (high variance)"),
        (2008, generate_low_data_campaign, "LOW_DATA (insufficient volume)"),
    ]

    total_rows = 0
    for campaign_id, generator, desc in scenarios:
        rows = generator(campaign_id, args.customer_id, start_date, args.days, run_id)
        insert_snap_campaign_daily(conn, rows)
        total_rows += len(rows)
        print(f"  ✓ {campaign_id}: {desc} ({len(rows)} rows)")

    conn.close()

    print(f"\n✓ Inserted {total_rows} rows across {len(scenarios)} campaigns")
    print(f"\nNext steps:")
    print(f"  1. Refresh readonly: .\\tools\\refresh_readonly.ps1")
    print(
        f"  2. Run Lighthouse: python -m act_lighthouse.cli run-v0 configs/client_001.yaml --snapshot-date {end_date} --max-insights 8"
    )


if __name__ == "__main__":
    main()
