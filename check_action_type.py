import duckdb, json

conn = duckdb.connect('warehouse.duckdb')

# Check what the recommendations table actually stores for the CPC cap rule
print("=== RECOMMENDATIONS TABLE ===")
rows = conn.execute("""
    SELECT rec_id, rule_id, rule_type, action_direction, action_magnitude
    FROM recommendations 
    WHERE status='pending' AND rule_id='db_campaign_21'
    LIMIT 2
""").fetchall()
for r in rows:
    print(f"rec_id={r[0][:8]}... rule_id={r[1]} rule_type={r[2]} action_direction={r[3]} action_magnitude={r[4]}")

print()
print("=== RULES TABLE (rule 21) ===")
row = conn.execute("""
    SELECT id, name, type, action_type, action_magnitude
    FROM rules WHERE id=21
""").fetchone()
print(f"id={row[0]} name={row[1]} type={row[2]} action_type={row[3]} magnitude={row[4]}")

print()
print("=== DOES recommendations TABLE HAVE action_type COLUMN? ===")
cols = conn.execute("PRAGMA table_info('recommendations')").fetchall()
col_names = [c[1] for c in cols]
print("action_type in recommendations:", "action_type" in col_names)
print("All columns:", col_names)

conn.close()
