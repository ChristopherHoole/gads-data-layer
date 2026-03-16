import duckdb

conn = duckdb.connect('warehouse_readonly.duckdb')
cols = [r[1] for r in conn.execute('PRAGMA table_info("analytics.campaign_daily")').fetchall()]
troas_cols = [c for c in cols if 'roas' in c.lower() or 'target' in c.lower() or 'bid' in c.lower()]
print('tROAS/target/bid columns in campaign_daily:')
for c in troas_cols:
    print(' ', c)
if not troas_cols:
    print('  None found')
conn.close()
