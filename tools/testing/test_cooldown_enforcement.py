"""
Test cooldown enforcement with real database changes.

Test Flow:
1. Execute a budget change (logs to change_log table)
2. Attempt duplicate change immediately (should be BLOCKED)
3. Verify cooldown violation logged correctly
4. Test one-lever rule (budget → bid within 7 days)

Run: python tools/testing/test_cooldown_enforcement.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import duckdb
from datetime import date, timedelta, datetime

from act_autopilot.change_log import ChangeLog
from act_autopilot.models import Recommendation, AutopilotConfig, GuardrailCheck
from act_autopilot.guardrails import validate_recommendation


def setup_test_database():
    """Create fresh test database with change_log table."""
    print("Setting up test database...")
    
    db_path = "test_cooldown.duckdb"
    
    # Delete if exists
    if Path(db_path).exists():
        Path(db_path).unlink()
    
    # Create database and table
    con = duckdb.connect(db_path)
    
    con.execute("""
        CREATE SCHEMA IF NOT EXISTS analytics;
    """)
    
    # Create sequence for auto-increment
    con.execute("""
        CREATE SEQUENCE analytics.change_log_seq START 1;
    """)
    
    con.execute("""
        CREATE TABLE analytics.change_log (
            change_id INTEGER DEFAULT nextval('analytics.change_log_seq'),
            customer_id TEXT NOT NULL,
            campaign_id TEXT NOT NULL,
            change_date DATE NOT NULL,
            lever TEXT NOT NULL,
            old_value DOUBLE,
            new_value DOUBLE,
            change_pct DOUBLE,
            rule_id TEXT,
            risk_tier TEXT,
            approved_by TEXT,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (change_id)
        );
    """)
    
    con.execute("""
        CREATE INDEX idx_cooldown ON analytics.change_log (
            customer_id, 
            campaign_id, 
            lever, 
            change_date
        );
    """)
    
    con.close()
    
    print(f"✅ Test database created: {db_path}\n")
    return db_path


def test_cooldown_enforcement(db_path: str):
    """Test 7-day cooldown enforcement."""
    print("="*60)
    print("TEST 1: Cooldown Enforcement (7-day rule)")
    print("="*60)
    
    change_log = ChangeLog(db_path)
    customer_id = "9999999999"
    campaign_id = "12345"
    today = date(2026, 2, 14)
    
    # Step 1: Log a budget change today
    print("\n1. Logging initial budget change...")
    change_log.log_change(
        customer_id=customer_id,
        campaign_id=campaign_id,
        change_date=today,
        lever='budget',
        old_value=100_000_000,
        new_value=105_000_000,
        change_pct=0.05,
        rule_id='BUDGET-001',
        risk_tier='low',
        approved_by='system',
        executed_at=datetime.now()
    )
    print("   ✅ Change logged")
    
    # Step 2: Check cooldown (should FAIL - change was today)
    print("\n2. Checking cooldown for duplicate change today...")
    cooldown_ok = change_log.check_cooldown(
        customer_id=customer_id,
        campaign_id=campaign_id,
        lever='budget',
        check_date=today
    )
    
    if not cooldown_ok:
        print("   ✅ PASS: Cooldown correctly BLOCKED duplicate change")
    else:
        print("   ❌ FAIL: Cooldown should have blocked change")
        return False
    
    # Step 3: Check cooldown 3 days later (should still FAIL)
    print("\n3. Checking cooldown 3 days later...")
    check_date_3d = today + timedelta(days=3)
    cooldown_ok = change_log.check_cooldown(
        customer_id=customer_id,
        campaign_id=campaign_id,
        lever='budget',
        check_date=check_date_3d
    )
    
    if not cooldown_ok:
        print("   ✅ PASS: Cooldown still blocking (within 7 days)")
    else:
        print("   ❌ FAIL: Cooldown should still block within 7 days")
        return False
    
    # Step 4: Check cooldown 8 days later (should PASS)
    print("\n4. Checking cooldown 8 days later...")
    check_date_8d = today + timedelta(days=8)
    cooldown_ok = change_log.check_cooldown(
        customer_id=customer_id,
        campaign_id=campaign_id,
        lever='budget',
        check_date=check_date_8d
    )
    
    if cooldown_ok:
        print("   ✅ PASS: Cooldown expired after 7 days")
    else:
        print("   ❌ FAIL: Cooldown should allow change after 7 days")
        return False
    
    print("\n✅ TEST 1 PASSED: Cooldown enforcement working\n")
    return True


def test_one_lever_rule(db_path: str):
    """Test one-lever rule (budget ↔ bid within 7 days)."""
    print("="*60)
    print("TEST 2: One-Lever Rule (budget ↔ bid separation)")
    print("="*60)
    
    change_log = ChangeLog(db_path)
    customer_id = "9999999999"
    campaign_id = "67890"
    today = date(2026, 2, 14)
    
    # Step 1: Log a BUDGET change today
    print("\n1. Logging budget change...")
    change_log.log_change(
        customer_id=customer_id,
        campaign_id=campaign_id,
        change_date=today,
        lever='budget',
        old_value=100_000_000,
        new_value=105_000_000,
        change_pct=0.05,
        rule_id='BUDGET-001',
        risk_tier='low',
        approved_by='system',
        executed_at=datetime.now()
    )
    print("   ✅ Budget change logged")
    
    # Step 2: Try to change BID on same campaign (should FAIL)
    print("\n2. Checking if BID change allowed (should be blocked)...")
    one_lever_ok = change_log.check_one_lever(
        customer_id=customer_id,
        campaign_id=campaign_id,
        lever='bid',  # Different lever
        check_date=today
    )
    
    if not one_lever_ok:
        print("   ✅ PASS: Bid change correctly BLOCKED (budget changed today)")
    else:
        print("   ❌ FAIL: Should block bid change when budget changed recently")
        return False
    
    # Step 3: Try bid change 8 days later (should PASS)
    print("\n3. Checking bid change 8 days later...")
    check_date_8d = today + timedelta(days=8)
    one_lever_ok = change_log.check_one_lever(
        customer_id=customer_id,
        campaign_id=campaign_id,
        lever='bid',
        check_date=check_date_8d
    )
    
    if one_lever_ok:
        print("   ✅ PASS: Bid change allowed after 7 days")
    else:
        print("   ❌ FAIL: Should allow bid change after 7 days")
        return False
    
    print("\n✅ TEST 2 PASSED: One-lever rule working\n")
    return True


def test_guardrail_integration(db_path: str):
    """Test cooldown enforcement via guardrails.validate_recommendation()."""
    print("="*60)
    print("TEST 3: Guardrail Integration")
    print("="*60)
    
    change_log = ChangeLog(db_path)
    customer_id = "9999999999"
    campaign_id = "99999"
    today = date(2026, 2, 14)
    
    # Step 1: Log a change
    print("\n1. Logging budget change...")
    change_log.log_change(
        customer_id=customer_id,
        campaign_id=campaign_id,
        change_date=today,
        lever='budget',
        old_value=100_000_000,
        new_value=105_000_000,
        change_pct=0.05,
        rule_id='BUDGET-001',
        risk_tier='low',
        approved_by='system',
        executed_at=datetime.now()
    )
    print("   ✅ Change logged")
    
    # Step 2: Create recommendation for same campaign/lever
    print("\n2. Creating duplicate recommendation...")
    rec = Recommendation(
        rule_id='BUDGET-001',
        campaign_id=campaign_id,
        campaign_name='Test Campaign',
        lever='budget',
        action='budget_increase',
        risk_tier='low',
        blocked=False,
        blocked_reason=None,
        evidence={
            'current_budget_micros': 105_000_000,
            'proposed_budget_micros': 110_000_000,
            'change_pct': 0.05,
            'clicks_w7': 100,
            'conversions_w7': 10
        },
        triggering_diagnosis=None,
        triggering_confidence=0.9
    )
    
    # Step 3: Validate with guardrails (should FAIL cooldown)
    print("\n3. Validating with guardrails...")
    config = AutopilotConfig(
        customer_id=customer_id,
        automation_mode='suggest',
        risk_tolerance='conservative',
        daily_spend_cap=500.0,
        monthly_spend_cap=15000.0,
        brand_is_protected=False,
        protected_entities=[],
        max_changes_per_day=10
    )
    
    result = validate_recommendation(
        rec=rec,
        config=config,
        snapshot_date=today,
        db_path=db_path
    )
    
    if not result.valid:
        cooldown_violation = any('cooldown' in reason.lower() for reason in result.blocked_reasons)
        if cooldown_violation:
            print(f"   ✅ PASS: Guardrails correctly blocked due to cooldown")
            print(f"   Reason: {result.blocked_reasons}")
        else:
            print(f"   ❌ FAIL: Blocked for wrong reason: {result.blocked_reasons}")
            return False
    else:
        print("   ❌ FAIL: Guardrails should have blocked due to cooldown")
        return False
    
    print("\n✅ TEST 3 PASSED: Guardrail integration working\n")
    return True


def view_change_log(db_path: str):
    """Display all changes in database."""
    print("="*60)
    print("CHANGE LOG (all entries)")
    print("="*60)
    
    con = duckdb.connect(db_path, read_only=True)
    
    result = con.execute("""
        SELECT 
            change_id,
            customer_id,
            campaign_id,
            change_date,
            lever,
            old_value/1000000 as old_budget,
            new_value/1000000 as new_budget,
            change_pct,
            rule_id,
            risk_tier
        FROM analytics.change_log
        ORDER BY change_date DESC, change_id DESC
    """).fetchall()
    
    if not result:
        print("(empty)")
    else:
        for row in result:
            print(f"\nID: {row[0]}")
            print(f"  Campaign: {row[2]}")
            print(f"  Date: {row[3]}")
            print(f"  Lever: {row[4]}")
            print(f"  Change: £{row[5]:.2f} → £{row[6]:.2f} ({row[7]:+.1%})")
            print(f"  Rule: {row[8]} ({row[9]})")
    
    con.close()
    print("\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("COOLDOWN ENFORCEMENT TEST SUITE")
    print("="*60 + "\n")
    
    # Setup
    db_path = setup_test_database()
    
    # Run tests
    test1_pass = test_cooldown_enforcement(db_path)
    test2_pass = test_one_lever_rule(db_path)
    test3_pass = test_guardrail_integration(db_path)
    
    # Show change log
    view_change_log(db_path)
    
    # Summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Test 1 (Cooldown):       {'✅ PASS' if test1_pass else '❌ FAIL'}")
    print(f"Test 2 (One-lever):      {'✅ PASS' if test2_pass else '❌ FAIL'}")
    print(f"Test 3 (Guardrails):     {'✅ PASS' if test3_pass else '❌ FAIL'}")
    print("="*60)
    
    if all([test1_pass, test2_pass, test3_pass]):
        print("\n✅ ALL TESTS PASSED")
        print(f"\nTest database: {db_path}")
        print("You can query this database to verify changes were logged correctly.\n")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Check output above for details.\n")
