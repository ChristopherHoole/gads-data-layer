"""
Feature Validation Script for Lighthouse

Validates that feature engineering calculations are mathematically correct by:
1. Reading raw data from analytics.campaign_daily
2. Manually calculating expected features
3. Comparing against actual features in campaign_features_daily
4. Reporting discrepancies

Usage:
    python tools/testing/validate_features.py --customer-id 9999999999 --snapshot-date 2026-02-11 --campaign-id 2003
"""

from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import duckdb


def fetch_raw_data(
    conn: duckdb.DuckDBPyConnection,
    customer_id: str,
    campaign_id: str,
    snapshot_date: date,
    lookback_days: int = 30,
) -> List[Dict]:
    """Fetch raw campaign_daily data for validation."""
    start_date = snapshot_date - timedelta(days=lookback_days - 1)

    sql = """
    SELECT
        snapshot_date,
        impressions,
        clicks,
        cost_micros,
        conversions,
        conversions_value
    FROM analytics.campaign_daily
    WHERE customer_id = ?
      AND campaign_id = ?
      AND snapshot_date BETWEEN ? AND ?
    ORDER BY snapshot_date;
    """

    result = conn.execute(
        sql, [customer_id, campaign_id, start_date, snapshot_date]
    ).fetchall()

    rows = []
    for r in result:
        rows.append(
            {
                "snapshot_date": r[0],
                "impressions": int(r[1] or 0),
                "clicks": int(r[2] or 0),
                "cost_micros": int(r[3] or 0),
                "conversions": float(r[4] or 0),
                "conversions_value": float(r[5] or 0) if r[5] is not None else 0.0,
            }
        )

    return rows


def calculate_rolling_window(
    data: List[Dict], metric: str, window: int, target_date: date
) -> Dict:
    """Calculate rolling window sum and mean for a metric."""
    # Find target date index
    target_idx = None
    for i, row in enumerate(data):
        if row["snapshot_date"] == target_date:
            target_idx = i
            break

    if target_idx is None:
        return {"sum": None, "mean": None, "count": 0}

    # Calculate window (inclusive of target date)
    start_idx = max(0, target_idx - window + 1)
    window_data = data[start_idx : target_idx + 1]

    values = [row[metric] if row[metric] is not None else 0 for row in window_data]
    total = sum(values)
    mean = total / len(values) if values else 0

    return {"sum": total, "mean": mean, "count": len(values)}


def calculate_vs_prev(current_sum: float, prev_sum: Optional[float]) -> Dict:
    """Calculate absolute and percentage change vs previous period."""
    if prev_sum is None or prev_sum == 0:
        return {"abs": None, "pct": None}

    abs_change = current_sum - prev_sum
    pct_change = abs_change / prev_sum

    return {"abs": abs_change, "pct": pct_change}


def calculate_derived_metric(
    data: List[Dict], window: int, target_date: date, metric_type: str
) -> Optional[float]:
    """Calculate derived metrics (CTR, CPC, CVR, CPA, ROAS) as ratio-of-sums."""
    impr = calculate_rolling_window(data, "impressions", window, target_date)
    clicks = calculate_rolling_window(data, "clicks", window, target_date)
    cost = calculate_rolling_window(data, "cost_micros", window, target_date)
    conv = calculate_rolling_window(data, "conversions", window, target_date)
    value = calculate_rolling_window(data, "conversions_value", window, target_date)

    if metric_type == "ctr":
        if impr["sum"] == 0:
            return None
        return clicks["sum"] / impr["sum"]

    elif metric_type == "cpc":
        if clicks["sum"] == 0:
            return None
        return cost["sum"] / clicks["sum"]

    elif metric_type == "cvr":
        if clicks["sum"] == 0:
            return None
        return conv["sum"] / clicks["sum"]

    elif metric_type == "cpa":
        if conv["sum"] == 0:
            return None
        return cost["sum"] / conv["sum"]

    elif metric_type == "roas":
        if cost["sum"] == 0:
            return None
        cost_dollars = cost["sum"] / 1_000_000.0
        return value["sum"] / cost_dollars

    return None


def validate_campaign_features(
    conn: duckdb.DuckDBPyConnection,
    customer_id: str,
    campaign_id: str,
    snapshot_date: date,
) -> Dict:
    """Validate features for a single campaign on a single date."""

    print(f"\n{'='*80}")
    print(f"VALIDATING: Campaign {campaign_id} on {snapshot_date}")
    print(f"{'='*80}\n")

    # Fetch raw data
    raw_data = fetch_raw_data(
        conn, customer_id, campaign_id, snapshot_date, lookback_days=60
    )

    if not raw_data:
        print(f"❌ No raw data found for campaign {campaign_id}")
        return {"status": "no_data"}

    print(f"✓ Fetched {len(raw_data)} days of raw data")

    # Fetch actual features from Lighthouse
    actual = conn.execute(
        """
        SELECT *
        FROM analytics.campaign_features_daily
        WHERE customer_id = ?
          AND campaign_id = ?
          AND snapshot_date = ?;
        """,
        [customer_id, campaign_id, snapshot_date],
    ).fetchone()

    if not actual:
        print(f"❌ No features found for campaign {campaign_id}")
        return {"status": "no_features"}

    # Get column names
    cols = [
        desc[0]
        for desc in conn.execute(
            "SELECT * FROM analytics.campaign_features_daily LIMIT 0;"
        ).description
    ]
    actual_dict = dict(zip(cols, actual))

    print(f"✓ Fetched actual features from Lighthouse\n")

    # Validation results
    results = {"passed": [], "failed": [], "skipped": []}

    # Validate rolling windows for base metrics
    windows = [1, 3, 7, 14, 30]
    metrics = [
        "impressions",
        "clicks",
        "cost_micros",
        "conversions",
        "conversions_value",
    ]

    print("VALIDATING ROLLING WINDOWS:")
    print("-" * 80)

    for metric in metrics:
        for w in windows:
            expected = calculate_rolling_window(raw_data, metric, w, snapshot_date)

            actual_sum = actual_dict.get(f"{metric}_w{w}_sum")
            actual_mean = actual_dict.get(f"{metric}_w{w}_mean")

            # Use relative tolerance for large numbers, absolute for small
            tolerance = (
                max(0.01, abs(expected["sum"]) * 0.0001)
                if expected["sum"] is not None
                else 0.01
            )

            # Handle None cases
            if actual_sum is None or expected["sum"] is None:
                sum_match = actual_sum is None and expected["sum"] is None
            else:
                sum_match = abs(expected["sum"] - actual_sum) < tolerance

            if actual_mean is None or expected["mean"] is None:
                mean_match = actual_mean is None and expected["mean"] is None
            else:
                mean_tolerance = max(0.01, abs(expected["mean"]) * 0.0001)
                mean_match = abs(expected["mean"] - actual_mean) < mean_tolerance

            if sum_match and mean_match:
                results["passed"].append(f"{metric}_w{w}")
                status = "✓"
            else:
                results["failed"].append(f"{metric}_w{w}")
                status = "✗"
                exp_sum_str = (
                    f"{expected['sum']:.2f}" if expected["sum"] is not None else "None"
                )
                act_sum_str = f"{actual_sum:.2f}" if actual_sum is not None else "None"
                exp_mean_str = (
                    f"{expected['mean']:.2f}"
                    if expected["mean"] is not None
                    else "None"
                )
                act_mean_str = (
                    f"{actual_mean:.2f}" if actual_mean is not None else "None"
                )
                print(
                    f"{status} {metric}_w{w}_sum: expected={exp_sum_str}, actual={act_sum_str}"
                )
                print(
                    f"{status} {metric}_w{w}_mean: expected={exp_mean_str}, actual={act_mean_str}"
                )

    print(
        f"✓ Rolling windows: {len(results['passed'])} passed, {len(results['failed'])} failed\n"
    )

    # Validate derived metrics
    print("VALIDATING DERIVED METRICS:")
    print("-" * 80)

    derived_metrics = ["ctr", "cpc", "cvr", "cpa", "roas"]

    for metric in derived_metrics:
        for w in windows:
            expected = calculate_derived_metric(raw_data, w, snapshot_date, metric)
            actual_val = actual_dict.get(f"{metric}_w{w}_mean")

            if expected is None and actual_val is None:
                results["passed"].append(f"{metric}_w{w}")
            elif expected is None or actual_val is None:
                results["failed"].append(f"{metric}_w{w}")
                print(f"✗ {metric}_w{w}_mean: expected={expected}, actual={actual_val}")
            else:
                # Allow for floating point precision differences
                if abs(expected - actual_val) < 0.0001:
                    results["passed"].append(f"{metric}_w{w}")
                else:
                    results["failed"].append(f"{metric}_w{w}")
                    print(
                        f"✗ {metric}_w{w}_mean: expected={expected:.6f}, actual={actual_val:.6f}, diff={abs(expected - actual_val):.6f}"
                    )

    print(
        f"✓ Derived metrics: {len(results['passed']) - len([x for x in results['passed'] if 'w' in x and any(m in x for m in metrics)])} passed\n"
    )

    # Validate low data flags
    print("VALIDATING LOW DATA FLAGS:")
    print("-" * 80)

    clicks_7d = calculate_rolling_window(raw_data, "clicks", 7, snapshot_date)["sum"]
    conv_30d = calculate_rolling_window(raw_data, "conversions", 30, snapshot_date)[
        "sum"
    ]
    impr_7d = calculate_rolling_window(raw_data, "impressions", 7, snapshot_date)["sum"]

    expected_low_clicks = clicks_7d < 30
    expected_low_conv = conv_30d < 15
    expected_low_impr = impr_7d < 500
    expected_low_data_flag = (
        expected_low_clicks or expected_low_conv or expected_low_impr
    )

    actual_low_clicks = actual_dict.get("low_data_clicks_7d")
    actual_low_conv = actual_dict.get("low_data_conversions_30d")
    actual_low_impr = actual_dict.get("low_data_impressions_7d")
    actual_low_data_flag = actual_dict.get("low_data_flag")

    if expected_low_clicks == actual_low_clicks:
        print(f"✓ low_data_clicks_7d: {actual_low_clicks} (clicks_7d={clicks_7d:.0f})")
        results["passed"].append("low_data_clicks_7d")
    else:
        print(
            f"✗ low_data_clicks_7d: expected={expected_low_clicks}, actual={actual_low_clicks}"
        )
        results["failed"].append("low_data_clicks_7d")

    if expected_low_conv == actual_low_conv:
        print(
            f"✓ low_data_conversions_30d: {actual_low_conv} (conv_30d={conv_30d:.0f})"
        )
        results["passed"].append("low_data_conversions_30d")
    else:
        print(
            f"✗ low_data_conversions_30d: expected={expected_low_conv}, actual={actual_low_conv}"
        )
        results["failed"].append("low_data_conversions_30d")

    if expected_low_impr == actual_low_impr:
        print(f"✓ low_data_impressions_7d: {actual_low_impr} (impr_7d={impr_7d:.0f})")
        results["passed"].append("low_data_impressions_7d")
    else:
        print(
            f"✗ low_data_impressions_7d: expected={expected_low_impr}, actual={actual_low_impr}"
        )
        results["failed"].append("low_data_impressions_7d")

    if expected_low_data_flag == actual_low_data_flag:
        print(f"✓ low_data_flag: {actual_low_data_flag}")
        results["passed"].append("low_data_flag")
    else:
        print(
            f"✗ low_data_flag: expected={expected_low_data_flag}, actual={actual_low_data_flag}"
        )
        results["failed"].append("low_data_flag")

    print()

    # Summary
    print("=" * 80)
    print("VALIDATION SUMMARY:")
    print("=" * 80)
    print(f"✓ PASSED: {len(results['passed'])} checks")
    print(f"✗ FAILED: {len(results['failed'])} checks")

    if results["failed"]:
        print(f"\nFailed checks:")
        for f in results["failed"]:
            print(f"  - {f}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Validate Lighthouse feature calculations"
    )
    parser.add_argument("--customer-id", required=True, help="Customer ID")
    parser.add_argument(
        "--snapshot-date", required=True, help="Snapshot date (YYYY-MM-DD)"
    )
    parser.add_argument("--campaign-id", required=True, help="Campaign ID to validate")
    parser.add_argument(
        "--db", default="warehouse_readonly.duckdb", help="Database path"
    )

    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    snapshot_date = date.fromisoformat(args.snapshot_date)

    conn = duckdb.connect(str(db_path), read_only=True)

    results = validate_campaign_features(
        conn, args.customer_id, args.campaign_id, snapshot_date
    )

    conn.close()

    if results.get("status") in ["no_data", "no_features"]:
        return 1

    if len(results["failed"]) > 0:
        print("\n⚠️  VALIDATION FAILED - Some checks did not pass")
        return 1

    print("\n✅ VALIDATION PASSED - All checks passed!")
    return 0


if __name__ == "__main__":
    exit(main())
