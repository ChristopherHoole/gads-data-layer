"""
Test Google Ads API error handling - Input Validation Tests.

Tests validation without needing mock exceptions:
1. Invalid campaign ID
2. Negative budget
3. Invalid customer ID
4. Zero budget

Run: python tools/testing/test_api_error_handling.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unittest.mock import Mock
from act_autopilot.google_ads_api import update_campaign_budget


def test_invalid_campaign():
    """Test invalid campaign ID handling."""
    print("\n=== TEST 1: Invalid Campaign ID ===")

    mock_client = Mock()

    result = update_campaign_budget(
        client=mock_client,
        customer_id="9999999999",
        campaign_id="INVALID",  # Non-numeric
        new_budget_micros=100000000,
    )

    assert result["status"] == "failed", "Should fail on invalid campaign ID"
    assert (
        "invalid campaign_id" in result["error"].lower()
    ), "Should mention invalid campaign_id"
    print(f"✅ PASS: Invalid campaign ID rejected")
    print(f"   Error: {result['error']}")


def test_negative_budget():
    """Test negative budget validation."""
    print("\n=== TEST 2: Negative Budget ===")

    mock_client = Mock()

    result = update_campaign_budget(
        client=mock_client,
        customer_id="9999999999",
        campaign_id="12345",
        new_budget_micros=-100000000,  # Negative
    )

    assert result["status"] == "failed", "Should fail on negative budget"
    assert (
        "must be positive" in result["error"].lower()
    ), "Should mention positive requirement"
    print(f"✅ PASS: Negative budget rejected")
    print(f"   Error: {result['error']}")


def test_invalid_customer_id():
    """Test invalid customer ID format."""
    print("\n=== TEST 3: Invalid Customer ID ===")

    mock_client = Mock()

    result = update_campaign_budget(
        client=mock_client,
        customer_id="123-456-7890",  # Contains dashes
        campaign_id="12345",
        new_budget_micros=100000000,
    )

    assert result["status"] == "failed", "Should fail on invalid customer ID"
    assert (
        "invalid customer_id" in result["error"].lower()
    ), "Should mention invalid customer_id"
    print(f"✅ PASS: Invalid customer ID rejected")
    print(f"   Error: {result['error']}")


def test_zero_budget():
    """Test zero budget validation."""
    print("\n=== TEST 4: Zero Budget ===")

    mock_client = Mock()

    result = update_campaign_budget(
        client=mock_client,
        customer_id="9999999999",
        campaign_id="12345",
        new_budget_micros=0,  # Zero
    )

    assert result["status"] == "failed", "Should fail on zero budget"
    assert (
        "must be positive" in result["error"].lower()
    ), "Should mention positive requirement"
    print(f"✅ PASS: Zero budget rejected")
    print(f"   Error: {result['error']}")


def test_short_customer_id():
    """Test customer ID with wrong length."""
    print("\n=== TEST 5: Wrong Length Customer ID ===")

    mock_client = Mock()

    result = update_campaign_budget(
        client=mock_client,
        customer_id="123",  # Too short
        campaign_id="12345",
        new_budget_micros=100000000,
    )

    assert result["status"] == "failed", "Should fail on wrong length"
    assert (
        "10 digits" in result["error"].lower()
    ), "Should mention 10 digits requirement"
    print(f"✅ PASS: Wrong length customer ID rejected")
    print(f"   Error: {result['error']}")


if __name__ == "__main__":
    print("=" * 60)
    print("Google Ads API Input Validation Tests")
    print("=" * 60)

    all_passed = True

    try:
        test_invalid_campaign()
    except AssertionError as e:
        print(f"❌ FAIL: {e}")
        all_passed = False

    try:
        test_negative_budget()
    except AssertionError as e:
        print(f"❌ FAIL: {e}")
        all_passed = False

    try:
        test_invalid_customer_id()
    except AssertionError as e:
        print(f"❌ FAIL: {e}")
        all_passed = False

    try:
        test_zero_budget()
    except AssertionError as e:
        print(f"❌ FAIL: {e}")
        all_passed = False

    try:
        test_short_customer_id()
    except AssertionError as e:
        print(f"❌ FAIL: {e}")
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("\nInput validation working correctly:")
        print("  ✅ Invalid campaign IDs rejected")
        print("  ✅ Invalid budgets rejected")
        print("  ✅ Invalid customer IDs rejected")
        print("  ✅ API won't crash on bad inputs")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60)
