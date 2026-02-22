"""
Fix: Recreate analytics.campaign_daily VIEW to expose new M4 columns.
Run once after A1 added optimization_score / bid_strategy_type / all_conversions columns.
"""
import duckdb

conn = duckdb.connect("warehouse.duckdb")

# Show current columns in base table
cols = [c[0] for c in conn.execute("DESCRIBE snap_campaign_daily").fetchall()]
print(f"snap_campaign_daily has {len(cols)} columns:")
for c in cols:
    print(f"  {c}")

# Recreate VIEW as SELECT * so it always matches the base table
conn.execute("CREATE OR REPLACE VIEW analytics.campaign_daily AS SELECT * FROM snap_campaign_daily")
print("\n✅ analytics.campaign_daily VIEW recreated with all columns")

# Verify
view_cols = [c[0] for c in conn.execute("DESCRIBE analytics.campaign_daily").fetchall()]
print(f"VIEW now has {len(view_cols)} columns")

new_cols = ['optimization_score', 'bid_strategy_type', 'all_conversions', 'all_conversions_value']
for c in new_cols:
    status = "✅" if c in view_cols else "❌ MISSING"
    print(f"  {status} {c}")

conn.close()

# Copy to readonly
import shutil
shutil.copy2("warehouse.duckdb", "warehouse_readonly.duckdb")
print("\n✅ Copied to warehouse_readonly.duckdb")
print("Done — restart Flask and refresh.")
