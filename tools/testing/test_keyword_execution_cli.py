"""
Keyword Execution Test Script (CLI)
Tests keyword execution in dry-run mode without making actual API calls.

Test scenarios:
1. Add keyword with calculated bid (Q1: A)
2. Pause keyword (high CPA scenario)
3. Adjust keyword bid (+15%)
4. Add negative keyword
5. Verify cooldown enforcement (14-day)
6. Verify daily add limit (max 10/day)
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


def create_keyword_add_recommendation():
    """Create recommendation for adding a keyword"""
    return Recommendation(
        rule_id="KW-ADD-001",
        rule_name="Add High-Intent Keyword",
        entity_type="keyword",
        entity_id="new_keyword_001",
        action_type="add_keyword",
        risk_tier="MEDIUM",
        campaign_name="Test Campaign",
        current_value=0,
        recommended_value=2.50,  # £2.50 bid
        change_pct=0,
        confidence=0.85,
        rationale="High-intent keyword with strong purchase intent",
        evidence={
            "ad_group_id": 12345,
            "campaign_id": 67890,
            "keyword_text": "buy nike shoes",  # Now in evidence
            "match_type": "EXACT",
            "bid_micros": 2500000,  # £2.50 in micros (Q1: required)
            "search_volume": 1200,
            "competition": "HIGH",
        },
    )


def create_keyword_pause_recommendation():
    """Create recommendation for pausing a keyword"""
    return Recommendation(
        rule_id="KW-PAUSE-001",
        rule_name="Pause High CPA Keyword",
        entity_type="keyword",
        entity_id="123456789",
        action_type="pause_keyword",
        risk_tier="LOW",
        campaign_name="Test Campaign",
        current_value=85.50,  # Current CPA
        recommended_value=0,  # Paused
        change_pct=-1.0,
        confidence=0.92,
        rationale="CPA £85.50 exceeds target £50.00 by 71%",
        evidence={
            "ad_group_id": 12345,
            "campaign_id": 67890,
            "keyword_text": "expensive keyword",
            "cpa": 85.50,
            "target_cpa": 50.00,
            "clicks_30d": 45,  # ≥30 clicks required
            "conversions_30d": 2,
        },
    )


def create_keyword_bid_recommendation():
    """Create recommendation for adjusting keyword bid"""
    return Recommendation(
        rule_id="KW-BID-001",
        rule_name="Increase Keyword Bid",
        entity_type="keyword",
        entity_id="987654321",
        action_type="update_keyword_bid",
        risk_tier="LOW",
        campaign_name="Test Campaign",
        current_value=1.50,  # £1.50
        recommended_value=1.725,  # £1.73 (+15%)
        change_pct=0.15,
        confidence=0.88,
        rationale="Keyword performing well, increase bid by 15%",
        evidence={
            "ad_group_id": 12345,
            "campaign_id": 67890,
            "keyword_text": "running shoes",
            "current_bid_micros": 1500000,
            "new_bid_micros": 1725000,
            "cpa": 35.00,
            "target_cpa": 50.00,
        },
    )


def create_negative_keyword_recommendation():
    """Create recommendation for adding negative keyword"""
    return Recommendation(
        rule_id="KW-NEG-001",
        rule_name="Add Negative Keyword",
        entity_type="keyword",
        entity_id="neg_keyword_001",
        action_type="add_negative_keyword",
        risk_tier="LOW",
        campaign_name="Test Campaign",
        current_value=0,
        recommended_value=0,
        change_pct=0,
        confidence=0.95,
        rationale="Blocks non-converting 'free' searches",
        evidence={
            "campaign_id": 67890,
            "keyword_text": "free",
            "match_type": "BROAD",
            "search_term": "free nike shoes",
            "clicks": 25,
            "conversions": 0,
        },
    )


def test_basic_keyword_operations():
    """Test 1-4: Basic keyword operations"""
    print_header("TEST 1-4: Basic Keyword Operations (Dry-Run)")

    executor = Executor(customer_id="1234567890", db_path="warehouse.duckdb")

    # Test 1: Add keyword with bid
    print("\nTest 1: Add Keyword with Calculated Bid")
    rec_add = create_keyword_add_recommendation()
    result = executor.execute([rec_add], dry_run=True)

    test_1_passed = (
        result["successful"] == 1
        and "buy nike shoes" in result["results"][0]["message"]
        and "£2.50" in result["results"][0]["message"]
    )
    print_result(
        "Add keyword 'buy nike shoes' with £2.50 bid",
        test_1_passed,
        f"Success: {result['successful']}/1",
    )

    # Test 2: Pause keyword (high CPA)
    print("\nTest 2: Pause Keyword (High CPA)")
    rec_pause = create_keyword_pause_recommendation()
    result = executor.execute([rec_pause], dry_run=True)

    test_2_passed = (
        result["successful"] == 1
        and "expensive keyword" in result["results"][0]["message"]
    )
    print_result(
        "Pause keyword due to high CPA",
        test_2_passed,
        f"Success: {result['successful']}/1",
    )

    # Test 3: Adjust keyword bid
    print("\nTest 3: Adjust Keyword Bid (+15%)")
    rec_bid = create_keyword_bid_recommendation()
    result = executor.execute([rec_bid], dry_run=True)

    test_3_passed = (
        result["successful"] == 1
        and "+15" in result["results"][0]["message"]
        and "running shoes" in result["results"][0]["message"]
    )
    print_result(
        "Increase bid by 15%",
        test_3_passed,
        f"Success: {result['successful']}/1",
    )

    # Test 4: Add negative keyword
    print("\nTest 4: Add Negative Keyword")
    rec_negative = create_negative_keyword_recommendation()
    result = executor.execute([rec_negative], dry_run=True)

    test_4_passed = (
        result["successful"] == 1 and "free" in result["results"][0]["message"]
    )
    print_result(
        "Add negative keyword 'free'",
        test_4_passed,
        f"Success: {result['successful']}/1",
    )

    all_passed = test_1_passed and test_2_passed and test_3_passed and test_4_passed
    return all_passed


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
                "keyword",
                1.50,
                1.80,
                "TEST-COOLDOWN",
                "LOW",
                "test",
                datetime.now() - timedelta(days=10),
                "update_keyword_bid",
                "keyword",
                "987654321",  # Same keyword ID as our test
            ],
        )
        conn.commit()
    finally:
        conn.close()

    # Try to change the same keyword again (should fail validation)
    print("\nAttempting to modify keyword within 14-day cooldown...")
    rec_bid = create_keyword_bid_recommendation()
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
            WHERE rule_id = 'TEST-COOLDOWN'
        """
        )
        conn.commit()
    finally:
        conn.close()

    return test_5_passed


def test_daily_add_limit():
    """Test 6: Daily add limit (max 10 keywords/day)"""
    print_header("TEST 6: Daily Add Limit (Max 10/Day)")

    import duckdb

    # Setup: Create 10 keyword adds today
    conn = duckdb.connect("warehouse.duckdb")
    try:
        today = datetime.now().date()
        for i in range(10):
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
                    today,
                    "keyword",
                    0,
                    2.00,
                    f"TEST-LIMIT-{i}",
                    "LOW",
                    "test",
                    datetime.now(),
                    "add_keyword",
                    "keyword",
                    f"test_keyword_{i}",
                ],
            )
        conn.commit()
    finally:
        conn.close()

    # Try to add 11th keyword (should fail validation)
    print("\nAttempting to add 11th keyword today (limit is 10)...")
    rec_add = create_keyword_add_recommendation()
    executor = Executor(customer_id="1234567890", db_path="warehouse.duckdb")
    result = executor.execute([rec_add], dry_run=True)

    # Should fail due to daily limit
    test_6_passed = result["failed"] == 1 and "limit" in result["results"][0][
        "message"
    ].lower()

    print_result(
        "11th keyword add blocked by daily limit",
        test_6_passed,
        f"Failed (as expected): {result['failed']}/1",
    )

    # Cleanup
    conn = duckdb.connect("warehouse.duckdb")
    try:
        conn.execute(
            """
            DELETE FROM analytics.change_log 
            WHERE rule_id LIKE 'TEST-LIMIT-%'
        """
        )
        conn.commit()
    finally:
        conn.close()

    return test_6_passed


def main():
    """Run all keyword execution tests"""
    print("\n" + "=" * 80)
    print("  KEYWORD EXECUTION TEST SUITE (CLI)")
    print("  Testing dry-run mode - No actual API calls")
    print("=" * 80)

    try:
        # Run all tests
        test_1_4 = test_basic_keyword_operations()
        test_5 = test_cooldown_enforcement()
        test_6 = test_daily_add_limit()

        # Summary
        print_header("TEST SUMMARY")

        total_tests = 6
        passed_tests = sum([test_1_4, test_5, test_6])  # test_1_4 counts as 4 tests

        # Adjust count (test_1_4 is actually 4 tests)
        if test_1_4:
            passed_tests += 3  # 4 tests total, already counted 1

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
