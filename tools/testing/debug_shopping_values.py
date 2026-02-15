"""Debug script to check actual values in database"""
import duckdb
from pathlib import Path

db_path = Path("warehouse.duckdb")
conn = duckdb.connect(str(db_path))

print("\n=== RAW TABLE VALUES ===")
raw = conn.execute("""
    SELECT 
        product_id,
        clicks,
        conversions,
        conversions_value,
        cost_micros
    FROM raw_product_performance_daily
    WHERE customer_id = '9999999999'
        AND snapshot_date = '2026-02-15'
    LIMIT 3
""").fetchall()

for r in raw:
    print(f"\nProduct: {r[0]}")
    print(f"  Clicks: {r[1]}")
    print(f"  Conversions: {r[2]}")
    print(f"  Conversions_value: {r[3]:,.0f} (micros)")
    print(f"  Cost_micros: {r[4]:,.0f}")
    if r[1] > 0:
        print(f"  CVR calc: {r[2]} / {r[1]} = {r[2] / r[1]:.4f}")
    if r[4] > 0:
        print(f"  ROAS calc: {r[3]} / {r[4]} = {r[3] / r[4]:.4f}")

print("\n=== FEATURES TABLE VALUES ===")
features = conn.execute("""
    SELECT 
        product_id,
        clicks_w30_sum,
        conversions_w30_sum,
        conversions_value_w30_sum,
        cost_micros_w30_sum,
        cvr_w30,
        roas_w30
    FROM analytics.product_features_daily
    WHERE customer_id = '9999999999'
        AND snapshot_date = '2026-02-15'
    LIMIT 3
""").fetchall()

for f in features:
    print(f"\nProduct: {f[0]}")
    print(f"  Clicks_w30: {f[1]}")
    print(f"  Conversions_w30: {f[2]}")
    print(f"  Conv_value_w30: {f[3]:,.0f}")
    print(f"  Cost_w30: {f[4]:,.0f}")
    print(f"  CVR_w30 (from DB): {f[5]}")
    print(f"  ROAS_w30 (from DB): {f[6]}")
    if f[1] > 0:
        print(f"  CVR expected: {f[2]} / {f[1]} = {f[2] / f[1]:.4f}")
    if f[4] > 0:
        print(f"  ROAS expected: {f[3]} / {f[4]} = {f[3] / f[4]:.4f}")

conn.close()
