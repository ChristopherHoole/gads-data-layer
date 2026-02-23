import duckdb
conn = duckdb.connect('warehouse.duckdb')
print('=== changes columns ===')
for r in conn.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'changes' ORDER BY ordinal_position").fetchall():
    print(r[0])
print()
print('=== executed_by values ===')
for r in conn.execute("SELECT DISTINCT executed_by FROM changes").fetchall():
    print(r[0])
conn.close()
