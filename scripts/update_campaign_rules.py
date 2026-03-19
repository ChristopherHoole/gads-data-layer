import duckdb

conn = duckdb.connect('warehouse.duckdb')

# --- DELETE: 4 pacing rules (account-level, not campaign-level) ---
conn.execute("DELETE FROM rules WHERE id IN (4, 5, 10, 15)")
print("Deleted 4 pacing rules (ids: 4, 5, 10, 15) - pacing is account-level")

# --- UPDATE: Rule 7 — conversions_7d threshold 3 → 10 ---
conn.execute("""
UPDATE rules
SET conditions = '[{"metric":"cpa_7d","op":"gt","value":"1.2","ref":"x_target"},{"metric":"conversions_7d","op":"gt","value":"10","ref":"absolute"}]'
WHERE id = 7
""")
print("Updated Rule 7: conversions_7d threshold 3 -> 10")

# --- UPDATE: Rule 11 - ctr_7d threshold 5.0 -> 4.0 ---
conn.execute("""
UPDATE rules
SET conditions = '[{"metric":"ctr_7d","operator":">=","value":4.0,"unit":"percent"},{"metric":"clicks_7d","operator":">=","value":50,"unit":"absolute"}]'
WHERE id = 11
""")
print("Updated Rule 11: ctr_7d threshold 5.0% -> 4.0%")

# --- UPDATE: Rule 20 - clicks_7d threshold 20 -> 30 ---
conn.execute("""
UPDATE rules
SET conditions = '[{"metric":"impression_share_lost_rank","op":"gt","value":30,"ref":"pct"},{"metric":"clicks_7d","op":"gte","value":"30","ref":"absolute"}]'
WHERE id = 20
""")
print("Updated Rule 20: clicks_7d threshold 20 -> 30")

# --- UPDATE: Rules 23 & 24 - cooldown_days 14 -> 30 ---
conn.execute("UPDATE rules SET cooldown_days = 30 WHERE id IN (23, 24)")
print("Updated Rules 23 & 24: cooldown_days 14 -> 30")

# --- DIAGNOSTIC: Confirm all changes ---
print()
print("=== DIAGNOSTIC: Deleted rules (should be 0 rows) ===")
rows = conn.execute("SELECT COUNT(*) FROM rules WHERE id IN (4, 5, 10, 15)").fetchall()
print(f"  Count of deleted rules remaining: {rows[0][0]}")

print()
print("=== DIAGNOSTIC: Updated rules ===")
rows = conn.execute(
    "SELECT id, name, conditions, cooldown_days FROM rules WHERE id IN (7, 11, 20, 23, 24) ORDER BY id"
).fetchall()
for r in rows:
    print(f"  id={r[0]}, name={r[1]}, cooldown_days={r[3]}")
    print(f"    conditions={r[2]}")

conn.close()
print()
print("All updates complete.")
