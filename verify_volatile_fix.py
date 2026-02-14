"""
Verify Bug #4 fix - Check volatile campaign variance
"""

import duckdb

db_path = "warehouse.duckdb"
con = duckdb.connect(db_path, read_only=True)

print("="*60)
print("BUG #4 VERIFICATION - Volatile Campaign Variance")
print("="*60)

result = con.execute("""
    SELECT 
        campaign_id,
        campaign_name,
        ROUND(STDDEV(cost_micros)::DOUBLE / AVG(cost_micros)::DOUBLE, 3) as cv,
        CASE 
            WHEN STDDEV(cost_micros)::DOUBLE / AVG(cost_micros)::DOUBLE > 0.35 THEN '✅ High variance (>35%)'
            WHEN STDDEV(cost_micros)::DOUBLE / AVG(cost_micros)::DOUBLE > 0.20 THEN '✅ Medium variance (>20%)'
            WHEN STDDEV(cost_micros)::DOUBLE / AVG(cost_micros)::DOUBLE > 0.10 THEN '✅ Low variance (>10%)'
            ELSE '❌ Too stable'
        END as status
    FROM snap_campaign_daily
    WHERE campaign_id IN ('3013', '3014', '3015')
    GROUP BY campaign_id, campaign_name
    ORDER BY campaign_id
""").fetchall()

print("\nResults:")
print("-"*60)
for row in result:
    print(f"\nCampaign: {row[1]} ({row[0]})")
    print(f"  Coefficient of Variation: {row[2]:.3f} ({row[2]*100:.1f}%)")
    print(f"  Status: {row[3]}")

print("\n" + "="*60)

# Check if all passed
all_pass = all('✅' in row[3] for row in result)

if all_pass:
    print("✅ BUG #4 FIXED - All volatile campaigns have proper variance!")
else:
    print("❌ Some campaigns still don't have enough variance")

print("="*60)

con.close()
