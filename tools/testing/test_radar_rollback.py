"""
Test Script: Radar Rollback System
Simulates bad changes and verifies rollback detection and execution.

Usage:
    python tools/testing/test_radar_rollback.py
"""

import duckdb
from datetime import date, datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from act_radar.monitor import ChangeMonitor
from act_radar.triggers import should_rollback
from act_radar.rollback_executor import RollbackExecutor


def setup_test_data(db_path: str = "warehouse.duckdb"):
    """
    Set up test scenario:
    1. Insert a fake budget increase change on campaign 3008 (Decline Fast)
    2. Worsen performance data post-change to trigger regression
    """
    conn = duckdb.connect(db_path)

    print("\n" + "=" * 80)
    print("SETTING UP TEST DATA")
    print("=" * 80)

    # Test parameters
    customer_id = "9999999999"
    campaign_id = "3008"  # Decline Fast campaign
    change_date = date.today() - timedelta(days=10)  # 10 days ago

    print(f"\nCustomer: {customer_id}")
    print(f"Campaign: {campaign_id} (Decline Fast)")
    print(f"Change Date: {change_date}")

    # 1. Get baseline performance (14 days before change)
    baseline_start = change_date - timedelta(days=14)
    baseline_end = change_date - timedelta(days=1)

    baseline_query = """
    SELECT 
        AVG(cost_micros) as avg_cost_micros,
        AVG(conversions) as avg_conversions,
        AVG(conversions_value) as avg_value_micros
    FROM analytics.campaign_daily
    WHERE customer_id = ?
    AND campaign_id = ?
    AND snapshot_date >= ?
    AND snapshot_date <= ?
    """

    baseline = conn.execute(
        baseline_query, [customer_id, campaign_id, baseline_start, baseline_end]
    ).fetchone()

    if not baseline or baseline[0] is None:
        print("\n❌ ERROR: No baseline data found for campaign 3008")
        print("   Run: python tools/testing/generate_synthetic_data_v2.py")
        conn.close()
        sys.exit(1)

    avg_cost = baseline[0]
    avg_conversions = baseline[1]
    avg_value = baseline[2]

    baseline_cpa = avg_cost / avg_conversions if avg_conversions > 0 else 0
    baseline_roas = avg_value / avg_cost if avg_cost > 0 else 0

    print(f"\nBaseline Performance ({baseline_start} to {baseline_end}):")
    print(f"  Avg Cost: ${avg_cost / 1_000_000:.2f}")
    print(f"  Avg Conversions: {avg_conversions:.1f}")
    print(f"  Avg Value: ${avg_value / 1_000_000:.2f}")
    print(f"  CPA: ${baseline_cpa / 1_000_000:.2f}")
    print(f"  ROAS: {baseline_roas:.2f}")

    # 2. Insert fake budget increase change
    print(f"\n📝 Inserting fake budget increase change...")

    # Use fake budget values (realistic for synthetic data)
    old_budget = 100_000_000  # $100/day
    new_budget = 110_000_000  # $110/day (+10%)

    print(
        f"  Budget: ${old_budget / 1_000_000:.2f} → ${new_budget / 1_000_000:.2f} (+10%)"
    )

    # Check if change already exists
    check_query = """
    SELECT COUNT(*) 
    FROM analytics.change_log
    WHERE customer_id = ?
    AND campaign_id = ?
    AND change_date = ?
    AND lever = 'budget'
    """

    existing = conn.execute(
        check_query, [customer_id, campaign_id, change_date]
    ).fetchone()[0]

    if existing > 0:
        print("  ⚠️  Change already exists - deleting old test data first")
        delete_query = """
        DELETE FROM analytics.change_log
        WHERE customer_id = ?
        AND campaign_id = ?
        AND change_date = ?
        """
        conn.execute(delete_query, [customer_id, campaign_id, change_date])

    # Insert change
    insert_query = """
    INSERT INTO analytics.change_log (
        customer_id,
        campaign_id,
        change_date,
        lever,
        old_value,
        new_value,
        change_pct,
        rule_id,
        risk_tier,
        approved_by,
        executed_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    executed_at = datetime.combine(change_date, datetime.min.time())

    conn.execute(
        insert_query,
        [
            customer_id,
            campaign_id,
            change_date,
            "budget",
            old_budget,
            new_budget,
            0.10,
            "BUDGET-001",
            "low",
            "TEST",
            executed_at,
        ],
    )

    change_id = conn.execute(
        "SELECT MAX(change_id) FROM analytics.change_log"
    ).fetchone()[0]

    print(f"  ✅ Change inserted (change_id={change_id})")

    # 3. Worsen post-change performance data
    print(f"\n📉 Worsening post-change performance...")

    # Post-change period: 4 days after change (after 72hr wait) for 7 days
    post_start = change_date + timedelta(days=4)
    post_end = post_start + timedelta(days=6)

    print(f"  Post-change period: {post_start} to {post_end}")

    # Worsen CPA by +25% and conversions by -12% (triggers Constitution rollback)
    worsened_cost = avg_cost * 1.25  # +25% cost (worse)
    worsened_conversions = avg_conversions * 0.88  # -12% conversions (worse)
    worsened_value = avg_value * 0.88  # -12% value (worse, keeps ROAS similar)

    worsened_cpa = (
        worsened_cost / worsened_conversions if worsened_conversions > 0 else 0
    )
    worsened_roas = worsened_value / worsened_cost if worsened_cost > 0 else 0

    print(f"\n  Target worsened metrics:")
    print(
        f"    Cost: ${avg_cost / 1_000_000:.2f} → ${worsened_cost / 1_000_000:.2f} (+25%)"
    )
    print(f"    Conversions: {avg_conversions:.1f} → {worsened_conversions:.1f} (-12%)")
    print(
        f"    CPA: ${baseline_cpa / 1_000_000:.2f} → ${worsened_cpa / 1_000_000:.2f} (+{((worsened_cpa/baseline_cpa - 1) * 100):.0f}%)"
    )
    print(f"    ROAS: {baseline_roas:.2f} → {worsened_roas:.2f}")

    # Update snap_campaign_daily (base table)
    update_snap_query = """
    UPDATE snap_campaign_daily
    SET 
        cost_micros = ?,
        conversions = ?,
        conversions_value = ?
    WHERE customer_id = ?
    AND campaign_id = ?
    AND snapshot_date >= ?
    AND snapshot_date <= ?
    """

    conn.execute(
        update_snap_query,
        [
            int(worsened_cost),
            worsened_conversions,
            int(worsened_value),
            customer_id,
            campaign_id,
            post_start,
            post_end,
        ],
    )

    conn.commit()
    conn.close()

    print(f"  ✅ Performance data worsened (snap_campaign_daily updated)")

    print(f"\n✅ Test data setup complete")
    print("=" * 80)

    return {
        "customer_id": customer_id,
        "campaign_id": campaign_id,
        "change_id": change_id,
        "change_date": change_date,
        "baseline_cpa": baseline_cpa,
        "worsened_cpa": worsened_cpa,
        "baseline_conversions": avg_conversions,
        "worsened_conversions": worsened_conversions,
    }


def test_monitoring(test_data: dict, config: dict):
    """Test the ChangeMonitor system."""
    print("\n" + "=" * 80)
    print("TEST 1: CHANGE MONITORING")
    print("=" * 80)

    monitor = ChangeMonitor()

    # Get changes to monitor
    changes = monitor.get_changes_to_monitor(test_data["customer_id"])

    print(f"\nChanges in monitoring window: {len(changes)}")

    if len(changes) == 0:
        print("❌ FAIL: Expected 1 change, found 0")
        return False

    # Find our test change
    test_change = None
    for change in changes:
        if change.change_id == test_data["change_id"]:
            test_change = change
            break

    if not test_change:
        print(f"❌ FAIL: Test change {test_data['change_id']} not found in monitoring")
        return False

    print(f"✅ Found test change: {test_change.change_id}")
    print(f"   Campaign: {test_change.campaign_name} ({test_change.campaign_id})")
    print(f"   Lever: {test_change.lever}")
    print(
        f"   Change: {test_change.old_value:.2f} → {test_change.new_value:.2f} ({test_change.change_pct:+.1%})"
    )

    # Monitor the change
    monitored = monitor.monitor_all_changes(test_data["customer_id"])

    test_monitored = None
    for m in monitored:
        if m.change_id == test_data["change_id"]:
            test_monitored = m
            break

    if not test_monitored:
        print("❌ FAIL: Change not in monitored list")
        return False

    if not test_monitored.delta:
        print("⚠️  WARNING: No performance delta (insufficient data)")
        return False

    print(f"\n📊 Performance Delta:")
    print(
        f"   CPA: ${test_monitored.delta['baseline_cpa']:.2f} → ${test_monitored.delta['current_cpa']:.2f} ({test_monitored.delta['cpa_change_pct']:+.1%})"
    )
    print(
        f"   Conversions: {test_monitored.delta['baseline_conversions']:.1f} → {test_monitored.delta['current_conversions']:.1f} ({test_monitored.delta['conversions_change_pct']:+.1%})"
    )
    print(
        f"   ROAS: {test_monitored.delta['baseline_roas']:.2f} → {test_monitored.delta['current_roas']:.2f} ({test_monitored.delta['roas_change_pct']:+.1%})"
    )

    print("\n✅ TEST 1 PASSED: Monitoring system working")

    return test_monitored


def test_triggers(monitored_change, config: dict):
    """Test rollback trigger logic."""
    print("\n" + "=" * 80)
    print("TEST 2: ROLLBACK TRIGGERS")
    print("=" * 80)

    decision = should_rollback(monitored_change, config)

    print(f"\nRollback Decision:")
    print(f"   Should Rollback: {decision.should_rollback}")
    print(f"   Trigger: {decision.trigger}")
    print(f"   Confidence: {decision.confidence:.0%}")
    print(f"   Reason: {decision.reason}")

    if not decision.should_rollback:
        print("\n❌ FAIL: Expected rollback trigger, but got no rollback")
        print(
            f"   CPA change: {monitored_change.delta['cpa_change_pct']:+.1%} (need >+20%)"
        )
        print(
            f"   Conv change: {monitored_change.delta['conversions_change_pct']:+.1%} (need <-10%)"
        )
        return False

    # Verify it's a CPA regression (since primary_kpi is 'roas' but we forced CPA regression)
    # Actually for ROAS clients, should trigger on ROAS regression
    if decision.trigger not in [
        "CPA_REGRESSION",
        "ROAS_REGRESSION",
        "VALUE_REGRESSION",
        "ROAS_AND_VALUE_REGRESSION",
    ]:
        print(f"\n❌ FAIL: Unexpected trigger type: {decision.trigger}")
        return False

    print("\n✅ TEST 2 PASSED: Rollback trigger detected correctly")

    return decision


def test_rollback_executor(test_data: dict, decision):
    """Test rollback execution (dry-run only)."""
    print("\n" + "=" * 80)
    print("TEST 3: ROLLBACK EXECUTION (DRY-RUN)")
    print("=" * 80)

    executor = RollbackExecutor()

    # Plan rollback
    change = executor.plan_rollback(test_data["change_id"])

    if not change:
        print(f"❌ FAIL: Could not plan rollback for change {test_data['change_id']}")
        return False

    print(f"\nPlanned Rollback:")
    print(f"   Change ID: {change['change_id']}")
    print(f"   Campaign: {change['campaign_id']}")
    print(f"   Lever: {change['lever']}")
    print(f"   Revert: {change['new_value']:.2f} → {change['old_value']:.2f}")

    # Execute (dry-run)
    result = executor.execute_rollback(
        change=change, reason=decision.reason, dry_run=True
    )

    if not result.success:
        print(f"\n❌ FAIL: Rollback execution failed")
        return False

    print(f"\n✅ Rollback simulated successfully")
    print(f"   Mode: DRY-RUN")
    print(f"   Would revert: {result.old_value:.2f} → {result.new_value:.2f}")

    print("\n✅ TEST 3 PASSED: Rollback executor working")

    return True


def cleanup_test_data(test_data: dict, db_path: str = "warehouse.duckdb"):
    """Clean up test data."""
    print("\n" + "=" * 80)
    print("CLEANUP")
    print("=" * 80)

    conn = duckdb.connect(db_path)

    # Delete test change
    delete_query = """
    DELETE FROM analytics.change_log
    WHERE change_id = ?
    """

    conn.execute(delete_query, [test_data["change_id"]])
    conn.commit()
    conn.close()

    print(f"\n✅ Deleted test change {test_data['change_id']}")
    print("⚠️  Note: Worsened performance data remains in database")
    print("   To reset: python tools/testing/generate_synthetic_data_v2.py")

    print("\n" + "=" * 80)


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("RADAR ROLLBACK SYSTEM TEST")
    print("=" * 80)
    print("\nThis test will:")
    print("1. Insert a fake budget increase on campaign 3008")
    print("2. Worsen performance data to trigger regression")
    print("3. Test monitoring, triggers, and rollback execution")
    print("4. Clean up test data")

    # Load config
    config = {
        "client_name": "Synthetic_Test_Client",
        "customer_id": "9999999999",
        "primary_kpi": "roas",
        "target_roas": 3.0,
    }

    try:
        # Setup test data
        test_data = setup_test_data()

        # Test 1: Monitoring
        monitored_change = test_monitoring(test_data, config)
        if not monitored_change:
            print("\n❌ TEST SUITE FAILED at Test 1")
            cleanup_test_data(test_data)
            sys.exit(1)

        # Test 2: Triggers
        decision = test_triggers(monitored_change, config)
        if not decision:
            print("\n❌ TEST SUITE FAILED at Test 2")
            cleanup_test_data(test_data)
            sys.exit(1)

        # Test 3: Rollback Executor
        success = test_rollback_executor(test_data, decision)
        if not success:
            print("\n❌ TEST SUITE FAILED at Test 3")
            cleanup_test_data(test_data)
            sys.exit(1)

        # Cleanup
        cleanup_test_data(test_data)

        # Summary
        print("\n" + "=" * 80)
        print("🎉 ALL TESTS PASSED")
        print("=" * 80)
        print("\nRadar rollback system is working correctly!")
        print("\nNext steps:")
        print(
            "  1. Run real monitoring: python -m act_radar.cli check configs/client_synthetic.yaml"
        )
        print(
            "  2. Test rollback CLI: python -m act_radar.cli rollback configs/client_synthetic.yaml --dry-run"
        )
        print("\n" + "=" * 80)

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
