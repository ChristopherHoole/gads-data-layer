"""
Shopping Execution Test Script (CLI)
Tests Shopping execution in dry-run mode without making actual API calls.

Test scenarios:
1. Increase product bid (high ROAS scenario)
2. Exclude product (Q3: A - campaign-level exclusion)
3. Verify out-of-stock protection (blocks changes to OOS products)
4. Verify feed quality protection (blocks exclusions with feed issues)
5. Verify 14-day cooldown enforcement
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


def create_product_bid_increase_recommendation():
    """Create recommendation for increasing product bid (high ROAS)"""
    return Recommendation(
        rule_id="SHOP-BID-001",
        rule_name="Increase High ROAS Product Bid",
        entity_type="product",
        entity_id="999888777",
        action_type="update_product_bid",
        risk_tier="LOW",
        campaign_name="Test Shopping Campaign",
        current_value=1.50,  # £1.50 current bid
        recommended_value=1.725,  # £1.73 (+15%)
        change_pct=0.15,
        confidence=0.92,
        rationale="Product ROAS 8.5 significantly exceeds target 5.0, increase bid by 15%",
        evidence={
            "ad_group_id": 12345,
            "campaign_id": 67890,
            "product_id": "PROD-12345",
            "current_bid_micros": 1500000,
            "new_bid_micros": 1725000,
            "roas": 8.5,
            "target_roas": 5.0,
            "out_of_stock": False,
            "feed_quality_issue": False,
        },
    )


def create_product_exclusion_recommendation():
    """Create recommendation for excluding a product (Q3: A - campaign-level)"""
    return Recommendation(
        rule_id="SHOP-EXCL-001",
        rule_name="Exclude Chronic Underperformer",
        entity_type="product",
        entity_id="product_exclude_001",
        action_type="exclude_product",
        risk_tier="MEDIUM",
        campaign_name="Test Shopping Campaign",
        current_value=0,
        recommended_value=0,
        change_pct=0,
        confidence=0.88,
        rationale="Product consistently underperforming with ROAS 1.2 vs target 5.0",
        evidence={
            "campaign_id": 67890,
            "product_id": "PROD-67890",
            "roas": 1.2,
            "target_roas": 5.0,
            "spend_30d": 250.0,
            "revenue_30d": 300.0,
            "out_of_stock": False,
            "feed_quality_issue": False,
            "only_in_category": False,
        },
    )


def create_product_bid_oos_recommendation():
    """Create recommendation that should be blocked (out-of-stock product)"""
    return Recommendation(
        rule_id="SHOP-BID-002",
        rule_name="Increase Product Bid",
        entity_type="product",
        entity_id="555444333",
        action_type="update_product_bid",
        risk_tier="LOW",
        campaign_name="Test Shopping Campaign",
        current_value=2.00,
        recommended_value=2.30,
        change_pct=0.15,
        confidence=0.85,
        rationale="High ROAS product",
        evidence={
            "ad_group_id": 12345,
            "campaign_id": 67890,
            "product_id": "PROD-OOS",
            "current_bid_micros": 2000000,
            "new_bid_micros": 2300000,
            "roas": 7.0,
            "target_roas": 5.0,
            "out_of_stock": True,  # OOS - should block
            "feed_quality_issue": False,
        },
    )


def create_product_exclusion_feed_issue_recommendation():
    """Create recommendation that should be blocked (feed quality issue)"""
    return Recommendation(
        rule_id="SHOP-EXCL-002",
        rule_name="Exclude Underperformer",
        entity_type="product",
        entity_id="product_exclude_002",
        action_type="exclude_product",
        risk_tier="MEDIUM",
        campaign_name="Test Shopping Campaign",
        current_value=0,
        recommended_value=0,
        change_pct=0,
        confidence=0.80,
        rationale="Low ROAS product",
        evidence={
            "campaign_id": 67890,
            "product_id": "PROD-FEED-ISSUE",
            "roas": 1.5,
            "target_roas": 5.0,
            "out_of_stock": False,
            "feed_quality_issue": True,  # Feed issue - should block
            "only_in_category": False,
        },
    )


def test_basic_shopping_operations():
    """Test 1-2: Basic Shopping operations"""
    print_header("TEST 1-2: Basic Shopping Operations (Dry-Run)")

    executor = Executor(customer_id="1234567890", db_path="warehouse.duckdb")

    # Test 1: Increase product bid (high ROAS)
    print("\nTest 1: Increase Product Bid (High ROAS)")
    rec_bid = create_product_bid_increase_recommendation()
    result = executor.execute([rec_bid], dry_run=True)

    test_1_passed = (
        result["successful"] == 1
        and "999888777" in result["results"][0]["message"]
        and "+15" in result["results"][0]["message"]
    )
    print_result(
        "Increase bid by 15% for high ROAS product",
        test_1_passed,
        f"Success: {result['successful']}/1",
    )

    # Test 2: Exclude product (Q3: A - campaign-level)
    print("\nTest 2: Exclude Product (Campaign-Level)")
    rec_exclude = create_product_exclusion_recommendation()
    result = executor.execute([rec_exclude], dry_run=True)

    test_2_passed = (
        result["successful"] == 1
        and "PROD-67890" in result["results"][0]["message"]
        and "campaign-level" in result["results"][0]["message"].lower()
    )
    print_result(
        "Exclude chronic underperformer (campaign-level)",
        test_2_passed,
        f"Success: {result['successful']}/1",
    )

    return test_1_passed and test_2_passed


def test_out_of_stock_protection():
    """Test 3: Out-of-stock protection"""
    print_header("TEST 3: Out-of-Stock Protection")

    executor = Executor(customer_id="1234567890", db_path="warehouse.duckdb")

    print("\nAttempting to modify out-of-stock product...")
    rec_bid = create_product_bid_oos_recommendation()
    result = executor.execute([rec_bid], dry_run=True)

    # Should fail due to OOS protection
    test_3_passed = (
        result["failed"] == 1
        and "out-of-stock" in result["results"][0]["message"].lower()
    )

    print_result(
        "Bid change blocked for out-of-stock product",
        test_3_passed,
        f"Failed (as expected): {result['failed']}/1",
    )

    return test_3_passed


def test_feed_quality_protection():
    """Test 4: Feed quality protection"""
    print_header("TEST 4: Feed Quality Protection")

    executor = Executor(customer_id="1234567890", db_path="warehouse.duckdb")

    print("\nAttempting to exclude product with feed quality issues...")
    rec_exclude = create_product_exclusion_feed_issue_recommendation()
    result = executor.execute([rec_exclude], dry_run=True)

    # Should fail due to feed quality protection
    test_4_passed = (
        result["failed"] == 1
        and "feed" in result["results"][0]["message"].lower()
    )

    print_result(
        "Exclusion blocked for product with feed quality issues",
        test_4_passed,
        f"Failed (as expected): {result['failed']}/1",
    )

    return test_4_passed


def test_cooldown_enforcement():
    """Test 5: Cooldown enforcement (14 days)"""
    print_header("TEST 5: Cooldown Enforcement (14 Days)")

    import duckdb

    # Setup: Create a recent change in the database
    conn = duckdb.connect("warehouse.duckdb")
    try:
        # Insert a change from 10 days ago (within 14-day cooldown)
        conn.execute(
            """
            INSERT INTO analytics.change_log (
                customer_id, campaign_id, change_date, lever,
                old_value, new_value, rule_id, risk_tier,
                approved_by, executed_at,
                action_type, entity_type, entity_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            [
                "1234567890",
                "67890",
                (datetime.now() - timedelta(days=10)).date(),
                "product",
                1.50,
                1.80,
                "TEST-COOLDOWN-PRODUCT",
                "LOW",
                "test",
                datetime.now() - timedelta(days=10),
                "update_product_bid",
                "product",
                "999888777",  # Same product ID as our test
            ],
        )
        conn.commit()
    finally:
        conn.close()

    # Try to change the same product again (should fail validation)
    print("\nAttempting to modify product within 14-day cooldown...")
    rec_bid = create_product_bid_increase_recommendation()
    executor = Executor(customer_id="1234567890", db_path="warehouse.duckdb")
    result = executor.execute([rec_bid], dry_run=True)

    # Should fail due to cooldown
    test_5_passed = result["failed"] == 1 and "Cooldown" in result["results"][0][
        "message"
    ]

    print_result(
        "Second change blocked by 14-day cooldown",
        test_5_passed,
        f"Failed (as expected): {result['failed']}/1",
    )

    # Cleanup
    conn = duckdb.connect("warehouse.duckdb")
    try:
        conn.execute(
            """
            DELETE FROM analytics.change_log 
            WHERE rule_id = 'TEST-COOLDOWN-PRODUCT'
        """
        )
        conn.commit()
    finally:
        conn.close()

    return test_5_passed


def main():
    """Run all Shopping execution tests"""
    print("\n" + "=" * 80)
    print("  SHOPPING EXECUTION TEST SUITE (CLI)")
    print("  Testing dry-run mode - No actual API calls")
    print("=" * 80)

    try:
        # Run all tests
        test_1_2 = test_basic_shopping_operations()
        test_3 = test_out_of_stock_protection()
        test_4 = test_feed_quality_protection()
        test_5 = test_cooldown_enforcement()

        # Summary
        print_header("TEST SUMMARY")

        total_tests = 5
        passed_tests = sum([test_1_2, test_3, test_4, test_5])

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
