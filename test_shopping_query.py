import duckdb

conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")

print("=" * 60)
print("TESTING SHOPPING PAGE QUERY")
print("=" * 60)

# This simulates what the Shopping page route uses
# Based on shopping.py pattern from other entities

customer_id = "1254895944"  # Christopher Hoole synthetic

try:
    # Test the query that shopping.py likely uses
    result = conn.execute("""
        SELECT 
            campaign_id,
            campaign_name,
            campaign_status,
            COUNT(*) as data_points
        FROM ro.analytics.shopping_campaign_daily
        WHERE customer_id = ?
        GROUP BY campaign_id, campaign_name, campaign_status
        ORDER BY campaign_name
    """, [customer_id]).fetchall()
    
    if result:
        print(f"Found {len(result)} shopping campaigns for customer {customer_id}:")
        for row in result:
            print(f"  Campaign: {row[1]} (ID: {row[0]}, Status: {row[2]}, Data Points: {row[3]})")
    else:
        print(f"NO shopping campaigns found for customer {customer_id}")
except Exception as e:
    print(f"ERROR: {e}")

print()

# Check what metrics are available for a campaign
print("=" * 60)
print("AVAILABLE SHOPPING METRICS (from one campaign)")
print("=" * 60)

try:
    sample = conn.execute("""
        SELECT 
            cost_micros,
            impressions,
            clicks,
            conversions,
            conversions_value_micros
        FROM ro.analytics.shopping_campaign_daily
        WHERE customer_id = ?
        LIMIT 1
    """, [customer_id]).fetchone()
    
    if sample:
        print(f"  Cost (micros):    {sample[0]:,}" if sample[0] else "  Cost: NULL")
        print(f"  Impressions:      {sample[1]:,}" if sample[1] else "  Impressions: NULL")
        print(f"  Clicks:           {sample[2]:,}" if sample[2] else "  Clicks: NULL")
        print(f"  Conversions:      {sample[3]}" if sample[3] else "  Conversions: NULL")
        print(f"  Conv Value (μ):   {sample[4]:,}" if sample[4] else "  Conv Value: NULL")
    else:
        print("  NO DATA")
except Exception as e:
    print(f"ERROR: {e}")

print()

# Check if features table exists
print("=" * 60)
print("SHOPPING FEATURES TABLE")
print("=" * 60)

try:
    features = conn.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'analytics' 
        AND (table_name LIKE '%shopping%feature%' OR table_name LIKE '%product%feature%')
    """).fetchall()
    
    if features:
        for f in features:
            count = conn.execute(f"SELECT COUNT(*) FROM ro.analytics.{f[0]}").fetchone()[0]
            print(f"  {f[0]}: {count:,} rows")
    else:
        print("  NO FEATURES TABLE FOUND")
        print("  (Shopping rules would need this for windowed metrics)")
except Exception as e:
    print(f"ERROR: {e}")

conn.close()
