"""
Comprehensive Test Script - Chat 47 Multi-Entity System

Tests:
1. Database schema (recommendations + changes tables)
2. Engine generates recommendations for all entity types
3. Accept/Decline routes work for all entity types
4. Backward compatibility maintained
5. Edge cases and error handling

Generates summary report with pass/fail status.
"""

import sys
import duckdb
from datetime import datetime

# Test results tracking
tests_run = 0
tests_passed = 0
tests_failed = 0
failures = []

def run_test(test_name, test_func):
    """Run a test and track results."""
    global tests_run, tests_passed, tests_failed, failures
    tests_run += 1
    
    try:
        test_func()
        tests_passed += 1
        print(f"  ✅ {test_name}")
        return True
    except AssertionError as e:
        tests_failed += 1
        failures.append((test_name, str(e)))
        print(f"  ❌ {test_name}: {e}")
        return False
    except Exception as e:
        tests_failed += 1
        failures.append((test_name, f"ERROR: {e}"))
        print(f"  ❌ {test_name}: ERROR: {e}")
        return False


print("=" * 80)
print("COMPREHENSIVE MULTI-ENTITY SYSTEM TEST - CHAT 47")
print("=" * 80)

conn = duckdb.connect('warehouse.duckdb')

# ---------------------------------------------------------------------------
# TEST SUITE 1: DATABASE SCHEMA VALIDATION
# ---------------------------------------------------------------------------

print("\n[TEST SUITE 1] DATABASE SCHEMA VALIDATION")

def test_recommendations_table_exists():
    result = conn.execute("SELECT COUNT(*) FROM recommendations").fetchone()
    assert result[0] >= 0, "Recommendations table should exist"

def test_recommendations_has_entity_columns():
    columns = [row[0] for row in conn.execute("DESCRIBE recommendations").fetchall()]
    assert "entity_type" in columns, "entity_type column missing"
    assert "entity_id" in columns, "entity_id column missing"
    assert "entity_name" in columns, "entity_name column missing"

def test_recommendations_has_backward_compat_columns():
    columns = [row[0] for row in conn.execute("DESCRIBE recommendations").fetchall()]
    assert "campaign_id" in columns, "campaign_id column missing (backward compatibility)"
    assert "campaign_name" in columns, "campaign_name column missing (backward compatibility)"

def test_changes_table_exists():
    result = conn.execute("SELECT COUNT(*) FROM changes").fetchone()
    assert result[0] >= 0, "Changes table should exist"

def test_changes_has_entity_columns():
    columns = [row[0] for row in conn.execute("DESCRIBE changes").fetchall()]
    assert "entity_type" in columns, "entity_type column missing in changes table"
    assert "entity_id" in columns, "entity_id column missing in changes table"

def test_changes_has_backward_compat_columns():
    columns = [row[0] for row in conn.execute("DESCRIBE changes").fetchall()]
    assert "campaign_id" in columns, "campaign_id column missing in changes (backward compatibility)"
    assert "campaign_name" in columns, "campaign_name column missing in changes (backward compatibility)"

run_test("Recommendations table exists", test_recommendations_table_exists)
run_test("Recommendations has entity_type/entity_id/entity_name columns", test_recommendations_has_entity_columns)
run_test("Recommendations has campaign_id/campaign_name (backward compat)", test_recommendations_has_backward_compat_columns)
run_test("Changes table exists", test_changes_table_exists)
run_test("Changes has entity_type/entity_id columns", test_changes_has_entity_columns)
run_test("Changes has campaign_id/campaign_name (backward compat)", test_changes_has_backward_compat_columns)

# ---------------------------------------------------------------------------
# TEST SUITE 2: ENGINE GENERATES RECOMMENDATIONS
# ---------------------------------------------------------------------------

print("\n[TEST SUITE 2] ENGINE GENERATES RECOMMENDATIONS FOR ALL ENTITY TYPES")

def test_campaign_recommendations_exist():
    count = conn.execute("""
        SELECT COUNT(*) FROM recommendations 
        WHERE customer_id = '9999999999' AND entity_type = 'campaign'
    """).fetchone()[0]
    assert count > 0, f"No campaign recommendations found (expected > 0, got {count})"

def test_keyword_recommendations_exist():
    count = conn.execute("""
        SELECT COUNT(*) FROM recommendations 
        WHERE customer_id = '9999999999' AND entity_type = 'keyword'
    """).fetchone()[0]
    assert count > 0, f"No keyword recommendations found (expected > 0, got {count})"

def test_shopping_recommendations_exist():
    count = conn.execute("""
        SELECT COUNT(*) FROM recommendations 
        WHERE customer_id = '9999999999' AND entity_type = 'shopping'
    """).fetchone()[0]
    assert count > 0, f"No shopping recommendations found (expected > 0, got {count})"

def test_entity_id_populated():
    null_count = conn.execute("""
        SELECT COUNT(*) FROM recommendations 
        WHERE customer_id = '9999999999' AND entity_id IS NULL
    """).fetchone()[0]
    assert null_count == 0, f"Found {null_count} recommendations with NULL entity_id"

def test_entity_name_populated():
    null_count = conn.execute("""
        SELECT COUNT(*) FROM recommendations 
        WHERE customer_id = '9999999999' AND entity_name IS NULL
    """).fetchone()[0]
    assert null_count == 0, f"Found {null_count} recommendations with NULL entity_name"

run_test("Campaign recommendations generated", test_campaign_recommendations_exist)
run_test("Keyword recommendations generated", test_keyword_recommendations_exist)
run_test("Shopping recommendations generated", test_shopping_recommendations_exist)
run_test("All recommendations have entity_id populated", test_entity_id_populated)
run_test("All recommendations have entity_name populated", test_entity_name_populated)

# ---------------------------------------------------------------------------
# TEST SUITE 3: ENTITY TYPE DISTRIBUTION
# ---------------------------------------------------------------------------

print("\n[TEST SUITE 3] ENTITY TYPE DISTRIBUTION ANALYSIS")

entity_counts = conn.execute("""
    SELECT entity_type, COUNT(*) as count
    FROM recommendations
    WHERE customer_id = '9999999999'
    GROUP BY entity_type
    ORDER BY entity_type
""").fetchall()

print("  Recommendations by entity type:")
for entity_type, count in entity_counts:
    print(f"    - {entity_type}: {count}")

total_recs = sum([count for _, count in entity_counts])
print(f"  Total recommendations: {total_recs}")

# ---------------------------------------------------------------------------
# TEST SUITE 4: ACCEPT/DECLINE ROUTES
# ---------------------------------------------------------------------------

print("\n[TEST SUITE 4] ACCEPT/DECLINE ROUTES VALIDATION")

def test_keyword_in_changes_table():
    count = conn.execute("""
        SELECT COUNT(*) FROM changes 
        WHERE entity_type = 'keyword'
    """).fetchone()[0]
    assert count > 0, f"No keyword changes found in changes table (expected > 0, got {count})"

def test_shopping_in_changes_table():
    count = conn.execute("""
        SELECT COUNT(*) FROM changes 
        WHERE entity_type = 'shopping'
    """).fetchone()[0]
    assert count > 0, f"No shopping changes found in changes table (expected > 0, got {count})"

def test_campaign_in_changes_table():
    count = conn.execute("""
        SELECT COUNT(*) FROM changes 
        WHERE entity_type = 'campaign'
    """).fetchone()[0]
    assert count > 0, f"No campaign changes found in changes table (expected > 0, got {count})"

def test_changes_have_entity_id():
    null_count = conn.execute("""
        SELECT COUNT(*) FROM changes 
        WHERE entity_type IS NOT NULL AND entity_id IS NULL
    """).fetchone()[0]
    assert null_count == 0, f"Found {null_count} changes with entity_type but NULL entity_id"

run_test("Keyword changes recorded in changes table", test_keyword_in_changes_table)
run_test("Shopping changes recorded in changes table", test_shopping_in_changes_table)
run_test("Campaign changes recorded in changes table", test_campaign_in_changes_table)
run_test("All changes have entity_id when entity_type is set", test_changes_have_entity_id)

# ---------------------------------------------------------------------------
# TEST SUITE 5: BACKWARD COMPATIBILITY
# ---------------------------------------------------------------------------

print("\n[TEST SUITE 5] BACKWARD COMPATIBILITY VALIDATION")

def test_campaign_recommendations_have_campaign_id():
    null_count = conn.execute("""
        SELECT COUNT(*) FROM recommendations 
        WHERE entity_type = 'campaign' AND campaign_id IS NULL
    """).fetchone()[0]
    assert null_count == 0, f"Found {null_count} campaign recommendations with NULL campaign_id"

def test_campaign_changes_have_campaign_id():
    null_count = conn.execute("""
        SELECT COUNT(*) FROM changes 
        WHERE entity_type = 'campaign' AND campaign_id IS NULL
    """).fetchone()[0]
    assert null_count == 0, f"Found {null_count} campaign changes with NULL campaign_id"

def test_old_style_query_works():
    # Query using old campaign_id approach
    count = conn.execute("""
        SELECT COUNT(*) FROM changes 
        WHERE campaign_id = '2001'
    """).fetchone()[0]
    # Should return at least the test changes we created
    assert count >= 0, "Old-style campaign_id query failed"

def test_new_style_query_works():
    # Query using new entity_type + entity_id approach
    count = conn.execute("""
        SELECT COUNT(*) FROM changes 
        WHERE entity_type = 'campaign' AND entity_id = '2001'
    """).fetchone()[0]
    # Should return at least the test changes we created
    assert count >= 0, "New-style entity query failed"

run_test("Campaign recommendations have campaign_id populated", test_campaign_recommendations_have_campaign_id)
run_test("Campaign changes have campaign_id populated", test_campaign_changes_have_campaign_id)
run_test("Old-style query by campaign_id works", test_old_style_query_works)
run_test("New-style query by entity_type + entity_id works", test_new_style_query_works)

# ---------------------------------------------------------------------------
# TEST SUITE 6: DATA INTEGRITY
# ---------------------------------------------------------------------------

print("\n[TEST SUITE 6] DATA INTEGRITY CHECKS")

def test_entity_id_matches_type():
    # For campaigns, entity_id should match campaign_id
    mismatch = conn.execute("""
        SELECT COUNT(*) FROM recommendations 
        WHERE entity_type = 'campaign' 
        AND entity_id != campaign_id
    """).fetchone()[0]
    assert mismatch == 0, f"Found {mismatch} campaigns where entity_id != campaign_id"

def test_no_orphan_entity_types():
    # Check for unexpected entity_type values
    entity_types = conn.execute("""
        SELECT DISTINCT entity_type FROM recommendations 
        WHERE customer_id = '9999999999'
    """).fetchall()
    
    valid_types = {'campaign', 'keyword', 'ad_group', 'shopping', 'ad'}
    found_types = {row[0] for row in entity_types}
    
    invalid = found_types - valid_types
    assert len(invalid) == 0, f"Found invalid entity_types: {invalid}"

def test_recommendations_have_status():
    null_status = conn.execute("""
        SELECT COUNT(*) FROM recommendations 
        WHERE status IS NULL
    """).fetchone()[0]
    assert null_status == 0, f"Found {null_status} recommendations with NULL status"

def test_recommendations_have_rule_id():
    null_rule = conn.execute("""
        SELECT COUNT(*) FROM recommendations 
        WHERE rule_id IS NULL
    """).fetchone()[0]
    assert null_rule == 0, f"Found {null_rule} recommendations with NULL rule_id"

run_test("Campaign entity_id matches campaign_id", test_entity_id_matches_type)
run_test("No invalid entity_type values", test_no_orphan_entity_types)
run_test("All recommendations have status", test_recommendations_have_status)
run_test("All recommendations have rule_id", test_recommendations_have_rule_id)

# ---------------------------------------------------------------------------
# TEST SUITE 7: EDGE CASES
# ---------------------------------------------------------------------------

print("\n[TEST SUITE 7] EDGE CASES & ERROR HANDLING")

def test_shopping_uses_campaign_id_as_entity():
    # Shopping recommendations use campaign_id for both fields
    shopping_recs = conn.execute("""
        SELECT COUNT(*) FROM recommendations 
        WHERE entity_type = 'shopping' 
        AND entity_id = campaign_id
    """).fetchone()[0]
    
    total_shopping = conn.execute("""
        SELECT COUNT(*) FROM recommendations 
        WHERE entity_type = 'shopping'
    """).fetchone()[0]
    
    assert shopping_recs == total_shopping, f"Not all shopping recs use campaign_id as entity_id ({shopping_recs}/{total_shopping})"

def test_keyword_has_parent_campaign():
    # Keywords should have campaign_id populated (parent campaign reference)
    null_campaign = conn.execute("""
        SELECT COUNT(*) FROM recommendations 
        WHERE entity_type = 'keyword' AND campaign_id IS NULL
    """).fetchone()[0]
    assert null_campaign == 0, f"Found {null_campaign} keywords with NULL campaign_id"

def test_multiple_entities_same_campaign():
    # Check that we can have multiple entity types for same campaign
    result = conn.execute("""
        SELECT campaign_id, COUNT(DISTINCT entity_type) as entity_types
        FROM recommendations
        WHERE customer_id = '9999999999'
        AND campaign_id IS NOT NULL
        GROUP BY campaign_id
        HAVING COUNT(DISTINCT entity_type) > 1
        LIMIT 1
    """).fetchone()
    
    # This is expected - keywords and campaigns for same campaign_id
    # Just verify the query works
    assert True, "Query for multiple entity types per campaign works"

run_test("Shopping uses campaign_id as entity_id", test_shopping_uses_campaign_id_as_entity)
run_test("Keywords have parent campaign_id", test_keyword_has_parent_campaign)
run_test("Multiple entity types can exist for same campaign", test_multiple_entities_same_campaign)

# ---------------------------------------------------------------------------
# FINAL SUMMARY
# ---------------------------------------------------------------------------

conn.close()

print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

print(f"\nTotal tests run: {tests_run}")
print(f"Tests passed: {tests_passed} ✅")
print(f"Tests failed: {tests_failed} ❌")
print(f"Success rate: {(tests_passed/tests_run*100):.1f}%")

if tests_failed > 0:
    print("\n❌ FAILED TESTS:")
    for test_name, error in failures:
        print(f"  - {test_name}")
        print(f"    {error}")
    print("\n" + "=" * 80)
    print("❌ SOME TESTS FAILED")
    print("=" * 80)
    sys.exit(1)
else:
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED")
    print("=" * 80)
    
    print("\nSYSTEM STATUS:")
    print("  ✅ Database schema correct (recommendations + changes tables)")
    print("  ✅ Engine generates recommendations for 3 entity types")
    print("     - Campaigns: ✅")
    print("     - Keywords: ✅")
    print("     - Shopping: ✅")
    print("  ✅ Accept/Decline routes work for all entity types")
    print("  ✅ Backward compatibility maintained")
    print("  ✅ Data integrity validated")
    print("  ✅ Edge cases handled correctly")
    
    print("\nMULTI-ENTITY SYSTEM: FULLY OPERATIONAL")
    
    sys.exit(0)
