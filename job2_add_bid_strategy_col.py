"""
Migration: Add bid_strategy_type to campaign_features_daily
from existing campaign_daily data.
"""
import duckdb

conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")

# Add column if missing
try:
    conn.execute("ALTER TABLE analytics.campaign_features_daily ADD COLUMN IF NOT EXISTS bid_strategy_type VARCHAR")
    print("Column added (or already exists)")
except Exception as e:
    print(f"Column step: {e}")

# Populate from campaign_daily
conn.execute("""
    UPDATE analytics.campaign_features_daily f
    SET bid_strategy_type = (
        SELECT MAX(bid_strategy_type)
        FROM ro.analytics.campaign_daily cd
        WHERE CAST(cd.campaign_id AS VARCHAR) = f.campaign_id
          AND CAST(cd.customer_id AS VARCHAR) = f.customer_id
    )
""")

# Verify
rows = conn.execute(
    "SELECT bid_strategy_type, COUNT(*) FROM analytics.campaign_features_daily "
    "GROUP BY bid_strategy_type ORDER BY COUNT(*) DESC"
).fetchall()
print("bid_strategy_type distribution:")
for r in rows:
    print(f"  {r[0]}: {r[1]} rows")

conn.close()
print("✅ Done.")
