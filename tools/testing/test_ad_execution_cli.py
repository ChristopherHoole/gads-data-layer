"""
Ad Execution Test Script (CLI)
Tests ad execution in dry-run mode without making actual API calls.

Test scenarios:
1. Pause ad (low CTR scenario)
2. Enable ad (CTR improved scenario - Q2: A check)
3. Verify minimum active ads (try to pause when only 2 active - should block)
4. Verify 7-day cooldown enforcement
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from act_autopilot.executor import Executor
from act_autopilot.models import Recommendation


def print_header(title):
    """Print test section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_result(test_name, passed, message=""):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {test_name}")
    if message:
        print(f"      {message}")


def create_ad_pause_recommendation():
    """Create recommendation for pausing an ad (low CTR)"""
    return Recommendation(
        rule_id="AD-PAUSE-001",
        rule_name="Pause Low CTR Ad",
        entity_type="ad",
        entity_id="111222333",
        action_type="pause_ad",
        risk_tier="LOW",
        campaign_name="Test Campaign",
        current_value=1.5,  # Current CTR 1.5%
        recommended_value=0,  # Paused
        change_pct=-1.0,
        confidence=0.90,
        rationale="Ad CTR 1.5% significantly below ad group average 3.2%",
        evidence={
            "ad_group_id": 12345,
            "campaign_id": 67890,
            "ctr": 0.015,
            "ad_group_ctr": 0.032,
            "impressions_30d": 5000,  # ≥1000 impressions required
            "clicks_30d": 75,
            "active_ads_count": 5,  # Has 5 active ads (safe to pause)
        },
    )


def create_ad_enable_recommendation():
    """Create recommendation for enabling a paused ad (CTR improved - Q2: A)"""
    return Recommendation(
        rule_id="AD-ENABLE-001",
        rule_name="Re-Enable Ad After CTR Improvement",
        entity_type="ad",
        entity_id="444555666",
        action_type="enable_ad",
        risk_tier="MEDIUM",
        campaign_name="Test Campaign",
        current_value=0,  # Currently paused
        recommended_value=1,  # Enable
        change_pct=0,
        confidence=0.85,
        rationale="Ad group CTR improved 25% since ad was paused",
        evidence={
            "ad_group_id": 12345,
            "campaign_id": 67890,
            "ctr_at_pause": 0.025,  # Ad group CTR when ad was paused
            "current_ad_group_ctr": 0.03125,  # Current ad group CTR (+25%)
            "impressions_30d": 8000,
            "clicks_30d": 250,
        },
    )


def create_ad_pause_min_active_recommendation():
    """Create recommendation that should be blocked (only 2 active ads)"""
    return Recommendation(
        rule_id="AD-PAUSE-002",
        rule_name="Pause Low CTR Ad",
        entity_type="ad",
        entity_id="777888999",
        action_type="pause_ad",
        risk_tier="LOW",
        campaign_name="Test Campaign",
        current_value=1.2,  # Current CTR
        recommended_value=0,  # Paused
        change_pct=-1.0,
        confidence=0.88,
        rationale="Ad CTR below average",
        evidence={
            "ad_group_id": 12345,
            "campaign_id": 67890,
            "ctr": 0.012,
            "ad_group_ctr": 0.028,
            "impressions_30d": 3000,
            "clicks_30d": 36,
            "active_ads_count": 2,  # Only 2 active - should block pause
        },
    )


def test_basic_ad_operations():
    """Test 1-2: Basic ad operations"""
    print_header("TEST 1-2: Basic Ad Operations (Dry-Run)")

    executor = Executor(customer_id="1234567890", db_path="warehouse.duckdb")

    # Test 1: Pause ad (low CTR)
    print("\nTest 1: Pause Ad (Low CTR)")
    rec_pause = create_ad_pause_recommendation()
    result = executor.execute([rec_pause], dry_run=True)

    test_1_passed = result["successful"] == 1 and "111222333" in result["results"][0][
        "message"
    ]
    print_result(
        "Pause ad with low CTR", test_1_passed, f"Success: {result['successful']}/1"
    )

    # Test 2: Enable ad (CTR improved - Q2: A check)
    print("\nTest 2: Enable Ad (CTR Improved ≥20%)")
    rec_enable = create_ad_enable_recommendation()
    result = executor.execute([rec_enable], dry_run=True)

    test_2_passed = (
        result["successful"] == 1
        and "444555666" in result["results"][0]["message"]
        and "CTR" in result["results"][0]["message"].upper()
    )
    print_result(
        "Enable ad after CTR improvement",
        test_2_passed,
        f"Success: {result['successful']}/1",
    )

    return test_1_passed and test_2_passed


def test_minimum_active_ads():
    """Test 3: Minimum active ads protection"""
    print_header("TEST 3: Minimum Active Ads Protection")

    executor = Executor(customer_id="1234567890", db_path="warehouse.duckdb")

    print("\nAttempting to pause ad when only 2 active (min 2 required)...")
    rec_pause = create_ad_pause_min_active_recommendation()
    result = executor.execute([rec_pause], dry_run=True)

    # Should fail due to minimum active ads requirement
    test_3_passed = (
        result["failed"] == 1
        and "active ads" in result["results"][0]["message"].lower()
    )

    print_result(
        "Pause blocked by minimum active ads rule",
        test_3_passed,
        f"Failed (as expected): {result['failed']}/1",
    )

    return test_3_passed


def test_cooldown_enforcement():
    """Test 4: Cooldown enforcement (7 days)"""
    print_header("TEST 4: Cooldown Enforcement (7 Days)")

    import duckdb

    # Setup: Create a recent change in the database
    conn = duckdb.connect("warehouse.duckdb")
    try:
        # Insert a change from 5 days ago (within 7-day cooldown)
        conn.execute(
            """
            INSERT INTO analytics.change_log (
                customer_id, campaign_id, change_date, lever,
                old_value, new_value, rule_id, risk_tier,
                approved_by, executed_at,
                action_type, entity_type, entity_id, ad_group_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            [
                "1234567890",
                "67890",
                (datetime.now() - timedelta(days=5)).date(),
                "ad",
                1,
                0,
                "TEST-COOLDOWN-AD",
                "LOW",
                "test",
                datetime.now() - timedelta(days=5),
                "pause_ad",
                "ad",
                "111222333",  # Same ad ID as our test
                12345,
            ],
        )
        conn.commit()
    finally:
        conn.close()

    # Try to change the same ad again (should fail validation)
    print("\nAttempting to modify ad within 7-day cooldown...")
    rec_pause = create_ad_pause_recommendation()
    executor = Executor(customer_id="1234567890", db_path="warehouse.duckdb")
    result = executor.execute([rec_pause], dry_run=True)

    # Should fail due to cooldown
    test_4_passed = result["failed"] == 1 and "Cooldown" in result["results"][0][
        "message"
    ]

    print_result(
        "Second change blocked by 7-day cooldown",
        test_4_passed,
        f"Failed (as expected): {result['failed']}/1",
    )

    # Cleanup
    conn = duckdb.connect("warehouse.duckdb")
    try:
        conn.execute(
            """
            DELETE FROM analytics.change_log 
            WHERE rule_id = 'TEST-COOLDOWN-AD'
        """
        )
        conn.commit()
    finally:
        conn.close()

    return test_4_passed


def main():
    """Run all ad execution tests"""
    print("\n" + "=" * 80)
    print("  AD EXECUTION TEST SUITE (CLI)")
    print("  Testing dry-run mode - No actual API calls")
    print("=" * 80)

    try:
        # Run all tests
        test_1_2 = test_basic_ad_operations()
        test_3 = test_minimum_active_ads()
        test_4 = test_cooldown_enforcement()

        # Summary
        print_header("TEST SUMMARY")

        total_tests = 4
        passed_tests = sum([test_1_2, test_3, test_4])

        # Adjust count (test_1_2 is actually 2 tests)
        if test_1_2:
            passed_tests += 1  # 2 tests total, already counted 1

        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")

        if passed_tests == total_tests:
            print("\n✓ ALL TESTS PASSED")
            return 0
        else:
            print(f"\n✗ {total_tests - passed_tests} TEST(S) FAILED")
            return 1

    except Exception as e:
        print(f"\n✗ TEST SUITE FAILED WITH ERROR:")
        print(f"   {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
