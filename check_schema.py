import duckdb

con = duckdb.connect('warehouse_readonly.duckdb')
result = con.execute("PRAGMA table_info('analytics.campaign_daily');").fetchall()

print("Column name | Type")
print("-" * 50)
for row in result:
    print(f"{row[1]:30} {row[2]}")

con.close()
