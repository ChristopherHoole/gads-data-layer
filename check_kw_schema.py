import duckdb
conn = duckdb.connect("warehouse.duckdb")
cols = conn.execute("DESCRIBE snap_keyword_daily").fetchall()
for c in cols: print(c[0], c[1])
conn.close()
