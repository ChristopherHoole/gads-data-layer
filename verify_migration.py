import duckdb

conn = duckdb.connect('warehouse.duckdb')

print('=== MIGRATION VERIFICATION ===')

# Sample rows
result = conn.execute('SELECT entity_type, entity_id, entity_name, campaign_id, campaign_name FROM recommendations LIMIT 3').fetchall()
print('\nSample rows:')
for r in result:
    entity_name_short = r[2][:30] if r[2] else 'NULL'
    print(f'  entity_type={r[0]}, entity_id={r[1]}, entity_name={entity_name_short}..., campaign_id={r[3]}')

# Counts by entity type
print('\nCounts by entity_type:')
counts = conn.execute('SELECT entity_type, COUNT(*) FROM recommendations GROUP BY entity_type').fetchall()
for c in counts:
    print(f'  {c[0]}: {c[1]} recommendations')

# Check indexes
print('\nIndexes:')
indexes = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='recommendations'").fetchall()
for idx in indexes:
    print(f'  - {idx[0]}')

conn.close()
