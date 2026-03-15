import duckdb

conn = duckdb.connect(r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb')

# Test 1: JSON_EXTRACT syntax
print("=== Test 1: JSON_EXTRACT ===")
try:
    result = conn.execute("""
        SELECT name, JSON_EXTRACT(conditions, '$[0].metric') as c1_metric
        FROM rules WHERE id = 1
    """).fetchone()
    print(f"JSON_EXTRACT works: {result}")
except Exception as e:
    print(f"JSON_EXTRACT FAILED: {e}")

# Test 2: json_extract_string syntax
print("\n=== Test 2: json_extract_string ===")
try:
    result = conn.execute("""
        SELECT name, json_extract_string(conditions, '$[0].metric') as c1_metric
        FROM rules WHERE id = 1
    """).fetchone()
    print(f"json_extract_string works: {result}")
except Exception as e:
    print(f"json_extract_string FAILED: {e}")

# Test 3: conditions raw value to understand format
print("\n=== Test 3: Raw conditions for rule id=1 ===")
result = conn.execute("SELECT conditions FROM rules WHERE id = 1").fetchone()
print(f"Raw: {result[0]}")

conn.close()
