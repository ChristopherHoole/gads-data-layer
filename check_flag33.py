import duckdb, json

conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")

print("=== FLAG 33 CONDITIONS ===")
row = conn.execute("SELECT id, name, conditions, risk_level, cooldown_days FROM rules WHERE id=33").fetchone()
print(f"id={row[0]} name={row[1]} risk={row[3]} cooldown={row[4]}")
conds = json.loads(row[2]) if row[2] else []
for c in conds:
    print(f"  metric={c.get('metric')} op={c.get('op')} value={c.get('value')} ref={c.get('ref')}")

print("\n=== CAMPAIGN FEATURES — CONVERSION METRICS (most recent valid date) ===")
rows = conn.execute("""
    SELECT DISTINCT ON (campaign_id)
           campaign_name,
           conversions_w7_sum,
           conversions_w7_vs_prev_pct,
           conversions_w14_sum,
           conversions_w14_vs_prev_pct
    FROM ro.analytics.campaign_features_daily
    WHERE customer_id = '1254895944'
      AND campaign_name IS NOT NULL
    ORDER BY campaign_id, snapshot_date DESC
""").fetchall()

def fmt(v):
    return f"{v:.4f}" if v is not None else "NULL"

print(f"{'Campaign':<30} {'conv_7d_sum':>12} {'conv_7d_pct':>12} {'conv_14d_sum':>13} {'conv_14d_pct':>13}")
print("-"*85)
for r in rows:
    print(f"{str(r[0]):<30} {fmt(r[1]):>12} {fmt(r[2]):>12} {fmt(r[3]):>13} {fmt(r[4]):>13}")

conn.close()
