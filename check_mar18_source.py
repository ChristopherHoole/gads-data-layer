import duckdb
conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")

# Check campaign_daily (source table) for 2026-03-18
print("=== campaign_daily rows for 2026-03-18 ===")
try:
    rows = conn.execute("""
        SELECT campaign_id, campaign_name, snapshot_date
        FROM ro.analytics.campaign_daily
        WHERE customer_id='1254895944' AND snapshot_date='2026-03-18'
        ORDER BY campaign_id
    """).fetchall()
    if rows:
        for r in rows:
            print(f"  campaign_id={r[0]} name={r[1]} date={r[2]}")
    else:
        print("  NO ROWS for 2026-03-18")
except Exception as e:
    print(f"  Error: {e}")

# Check 2026-03-17 too
print("\n=== campaign_daily rows for 2026-03-17 ===")
try:
    rows = conn.execute("""
        SELECT campaign_id, campaign_name, snapshot_date
        FROM ro.analytics.campaign_daily
        WHERE customer_id='1254895944' AND snapshot_date='2026-03-17'
        ORDER BY campaign_id
    """).fetchall()
    if rows:
        for r in rows:
            print(f"  campaign_id={r[0]} name={r[1]} date={r[2]}")
    else:
        print("  NO ROWS for 2026-03-17")
except Exception as e:
    print(f"  Error: {e}")

conn.close()
