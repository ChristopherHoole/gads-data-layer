"""
Clear all pending recommendations for Synthetic_Test_Client (customer_id=9999999999)
and re-run the recommendations engine to generate fresh DB-sourced recommendations.
"""
import duckdb

conn = duckdb.connect('warehouse.duckdb')

# Count before
before = conn.execute(
    "SELECT COUNT(rec_id) FROM recommendations WHERE customer_id = '9999999999'"
).fetchone()[0]
print(f"Before: {before} recommendations for customer 9999999999")

# Delete all
conn.execute("DELETE FROM recommendations WHERE customer_id = '9999999999'")

# Count after
after = conn.execute(
    "SELECT COUNT(rec_id) FROM recommendations WHERE customer_id = '9999999999'"
).fetchone()[0]
print(f"After: {after} recommendations remaining (expected 0)")

conn.close()
print("✅ Done. Now run the engine to generate fresh recommendations.")
