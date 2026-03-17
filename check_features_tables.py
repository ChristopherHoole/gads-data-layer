import duckdb

conn = duckdb.connect('warehouse_readonly.duckdb')
print("=== All tables in analytics schema ===")
rows = conn.execute("""
    SELECT table_name, table_type 
    FROM information_schema.tables 
    WHERE table_schema = 'analytics'
    ORDER BY table_name
""").fetchall()
for r in rows:
    count = conn.execute(f"SELECT COUNT(*) FROM analytics.{r[0]}").fetchone()[0]
    print(f"  {r[1]:<10} analytics.{r[0]:<40} {count:>8,} rows")

conn.close()
print("\n✅ Done.")
