import duckdb, json

conn = duckdb.connect('warehouse.duckdb')

# Check all 6 bid rules and their conditions
print("=== BID RULES ===")
rows = conn.execute("""
    SELECT id, name, enabled, conditions, action_type
    FROM rules WHERE id IN (16,17,18,19,20,21) ORDER BY id
""").fetchall()
for r in rows:
    conds = json.loads(r[3]) if r[3] else []
    print(f"\nid={r[0]} name={r[1]} enabled={r[2]} action_type={r[4]}")
    for c in conds:
        print(f"  condition: metric={c.get('metric')} op={c.get('op')} value={c.get('value')} ref={c.get('ref')}")

print("\n\n=== CAMPAIGN FEATURES (last 7 days avg) ===")
rows2 = conn.execute("""
    SELECT campaign_id, campaign_name, 
           roas_7d, cpa_7d, ctr_7d, cpc_7d,
           search_impr_share, pacing_ratio
    FROM ro.analytics.campaign_features_daily
    WHERE customer_id = '1254895944'
    ORDER BY snapshot_date DESC
    LIMIT 8
""").fetchall()
for r in rows2:
    print(f"campaign={r[1]} roas_7d={r[2]:.2f} cpa_7d={r[3]:.2f} ctr_7d={r[4]:.4f} cpc_7d={r[5]:.2f} is={r[6]:.2f}")

conn.close()
