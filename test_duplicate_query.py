import duckdb

conn = duckdb.connect(r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb')

# Simulate what create_rule does for "Increase Budget - Strong ROAS"
# type=budget, action_type=increase_budget, campaign_type_lock=all, c1_metric=roas_7d
print("=== Test: would duplicate detection catch Increase Budget - Strong ROAS? ===")
try:
    dup = conn.execute("""
        SELECT name FROM rules
        WHERE client_config = 'client_christopher_hoole'
          AND type = 'budget'
          AND action_type = 'increase_budget'
          AND campaign_type_lock = 'all'
          AND is_template = FALSE
          AND json_extract_string(conditions, '$[0].metric') = 'roas_7d'
        LIMIT 1
    """).fetchone()
    if dup:
        print(f"WOULD BLOCK: found existing rule '{dup[0]}'")
    else:
        print("WOULD NOT BLOCK: no match found")
except Exception as e:
    print(f"QUERY FAILED: {e}")

# Check what conditions look like for rule id=1
print("\n=== Conditions format for rule id=1 ===")
row = conn.execute("SELECT conditions, typeof(conditions) FROM rules WHERE id=1").fetchone()
print(f"  value: {row[0]}")
print(f"  type:  {row[1]}")

# Test json_extract on actual data
print("\n=== json_extract_string result ===")
row = conn.execute("SELECT json_extract_string(conditions, '$[0].metric') FROM rules WHERE id=1").fetchone()
print(f"  result: {row[0]}")

conn.close()
