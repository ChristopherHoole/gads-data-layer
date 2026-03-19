import duckdb, json

conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")

# Get most recent valid campaign features
rows = conn.execute("""
    SELECT DISTINCT ON (campaign_id)
           campaign_name,
           roas_w7_vs_prev_pct,
           cpa_w7_vs_prev_pct,
           ctr_w7_vs_prev_pct,
           cvr_w7_vs_prev_pct,
           conversions_w7_vs_prev_pct,
           cost_micros_w7_vs_prev_pct
    FROM ro.analytics.campaign_features_daily
    WHERE customer_id = '1254895944' AND campaign_name IS NOT NULL
    ORDER BY campaign_id, snapshot_date DESC
""").fetchall()

print("=== VS_PREV_PCT VALUES IN SYNTHETIC DATA ===\n")
print(f"{'Campaign':<30} {'roas%':>8} {'cpa%':>8} {'ctr%':>8} {'cvr%':>8} {'conv%':>8} {'cost%':>8}")
print("-"*80)
def f(v): return f"{v*100:.1f}%" if v is not None else "NULL"
for r in rows:
    print(f"{str(r[0]):<30} {f(r[1]):>8} {f(r[2]):>8} {f(r[3]):>8} {f(r[4]):>8} {f(r[5]):>8} {f(r[6]):>8}")

print("\n=== FLAG THRESHOLDS (after fix) ===")
flags = conn.execute("""
    SELECT id, name, conditions FROM rules 
    WHERE rule_or_flag='flag' AND enabled=TRUE AND conditions IS NOT NULL
    ORDER BY id
""").fetchall()
for f_row in flags:
    conds = json.loads(f_row[2])
    for c in conds:
        if 'vs_prev_pct' in (c.get('metric') or ''):
            print(f"id={f_row[0]} {f_row[1]}: {c.get('metric')} {c.get('op')} {c.get('value')}")

conn.close()
