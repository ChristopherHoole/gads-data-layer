import duckdb

conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")

print("=== CAMPAIGN FEATURES vs BID RULE THRESHOLDS ===\n")

rows = conn.execute("""
    SELECT DISTINCT ON (campaign_id)
           campaign_name,
           roas_w14_mean,
           cpa_w14_mean,
           conversions_w14_sum,
           ctr_w7_mean,
           cpc_w7_mean,
           impression_share_lost_rank
    FROM ro.analytics.campaign_features_daily
    WHERE customer_id = '1254895944'
    ORDER BY campaign_id, snapshot_date DESC
""").fetchall()

def fmt(v, fmt_str):
    return format(v, fmt_str) if v is not None else 'NULL'

print(f"{'Campaign':<30} {'roas_14d':>8} {'cpa_14d':>8} {'conv_14d':>9} {'ctr_7d':>7} {'cpc_7d':>7} {'is_lost%':>9}")
print("-" * 90)
for r in rows:
    print(f"{str(r[0]):<30} {fmt(r[1],'.2f'):>8} {fmt(r[2],'.2f'):>8} {fmt(r[3],'.1f'):>9} {fmt(r[4],'.4f'):>7} {fmt(r[5],'.2f'):>7} {fmt(r[6],'.2f'):>9}")

print()
print("RULE 16 needs: roas_14d >= 1.2x target AND conv_14d >= 15")
print("RULE 17 needs: roas_14d >= 1.05x target AND is_lost_rank > 20%")
print("RULE 18 needs: cpa_14d <= 0.85x target AND conv_14d >= 15")
print("RULE 19 needs: BROKEN (op=None)")
print("RULE 20 needs: BROKEN (op=None)")
print("RULE 21 needs: cpc_7d > 5 AND ctr_7d < 2%")
conn.close()
