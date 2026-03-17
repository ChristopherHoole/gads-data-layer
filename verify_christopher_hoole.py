"""
Verify synthetic data for Christopher Hoole client (1254895944)
"""
import duckdb

CID = "1254895944"
conn = duckdb.connect('warehouse.duckdb')

print("=" * 70)
print("DATA VERIFICATION — Christopher Hoole (1254895944)")
print("=" * 70)

# ── 1. Row counts ─────────────────────────────────────────────────────────────
print("\n--- Row counts ---")
tables = ['campaign_daily','ad_group_daily','keyword_daily','ad_daily','search_term_daily']
for t in tables:
    n = conn.execute(f"SELECT COUNT(*) FROM analytics.{t} WHERE customer_id=?", [CID]).fetchone()[0]
    print(f"  {t:<30} {n:>8,} rows")

# ── 2. Date range ─────────────────────────────────────────────────────────────
print("\n--- Date ranges ---")
for t in tables:
    row = conn.execute(f"SELECT MIN(snapshot_date), MAX(snapshot_date), COUNT(DISTINCT snapshot_date) FROM analytics.{t} WHERE customer_id=?", [CID]).fetchone()
    print(f"  {t:<30} {row[0]} → {row[1]}  ({row[2]} days)")

# ── 3. Campaigns ──────────────────────────────────────────────────────────────
print("\n--- Campaigns ---")
rows = conn.execute("""
    SELECT DISTINCT campaign_id, campaign_name, campaign_status, bid_strategy_type,
           COUNT(*) as days
    FROM analytics.campaign_daily WHERE customer_id=?
    GROUP BY 1,2,3,4 ORDER BY campaign_id
""", [CID]).fetchall()
for r in rows:
    print(f"  id={r[0]}  strategy={r[3]:<30} status={r[2]}  days={r[4]}  name={r[1]}")

# ── 4. Ad groups ──────────────────────────────────────────────────────────────
print("\n--- Ad groups (distinct) ---")
rows = conn.execute("""
    SELECT DISTINCT campaign_name, ad_group_id, ad_group_name
    FROM analytics.ad_group_daily WHERE customer_id=?
    ORDER BY campaign_name, ad_group_id
""", [CID]).fetchall()
for r in rows:
    print(f"  [{r[0][:35]:<35}]  ag={r[1]}  {r[2]}")

# ── 5. Keywords ───────────────────────────────────────────────────────────────
print("\n--- Keywords summary ---")
kw_count = conn.execute("SELECT COUNT(DISTINCT keyword_id) FROM analytics.keyword_daily WHERE customer_id=?", [CID]).fetchone()[0]
match_types = conn.execute("SELECT match_type, COUNT(DISTINCT keyword_id) FROM analytics.keyword_daily WHERE customer_id=? GROUP BY 1", [CID]).fetchall()
qs_dist = conn.execute("SELECT quality_score, COUNT(DISTINCT keyword_id) FROM analytics.keyword_daily WHERE customer_id=? AND snapshot_date=(SELECT MAX(snapshot_date) FROM analytics.keyword_daily WHERE customer_id=?) GROUP BY 1 ORDER BY 1", [CID,CID]).fetchall()
print(f"  Total unique keywords: {kw_count}")
print(f"  Match types: {dict(match_types)}")
print(f"  Quality score distribution: {dict(qs_dist)}")

# Sample keywords
print("\n--- Sample keywords (first 10) ---")
rows = conn.execute("""
    SELECT DISTINCT keyword_text, match_type, quality_score, ad_group_name
    FROM analytics.keyword_daily WHERE customer_id=? AND snapshot_date=(SELECT MAX(snapshot_date) FROM analytics.keyword_daily WHERE customer_id=?)
    LIMIT 10
""", [CID,CID]).fetchall()
for r in rows:
    print(f"  [{r[3][:30]:<30}]  qs={r[2]}  {r[1]:<8}  {r[0]}")

# ── 6. Ads ────────────────────────────────────────────────────────────────────
print("\n--- Ads ---")
rows = conn.execute("""
    SELECT DISTINCT ad_type, ad_strength, COUNT(DISTINCT ad_id) as cnt
    FROM analytics.ad_daily WHERE customer_id=?
    GROUP BY 1,2 ORDER BY 1,2
""", [CID]).fetchall()
for r in rows:
    print(f"  {r[0]:<30}  strength={r[1]:<12}  count={r[2]}")

# ── 7. Performance spot check ─────────────────────────────────────────────────
print("\n--- Performance spot check (campaign averages over 90d) ---")
rows = conn.execute("""
    SELECT campaign_name,
           SUM(clicks) as total_clicks,
           ROUND(SUM(cost_micros)/1e6, 2) as total_cost_gbp,
           SUM(conversions) as total_convs,
           ROUND(AVG(CAST(search_impression_share AS DOUBLE))*100,1) as avg_is_pct,
           bid_strategy_type
    FROM analytics.campaign_daily WHERE customer_id=?
    GROUP BY campaign_name, bid_strategy_type ORDER BY campaign_name
""", [CID]).fetchall()
for r in rows:
    print(f"  {r[0][:35]:<35}  clicks={r[1]:>6}  cost=£{r[2]:>7.2f}  convs={r[3]:>6.1f}  IS={r[4]}%  {r[5]}")

# ── 8. Search terms ───────────────────────────────────────────────────────────
print("\n--- Search terms sample ---")
rows = conn.execute("""
    SELECT DISTINCT search_term, keyword_text, search_term_status
    FROM analytics.search_term_daily WHERE customer_id=?
    LIMIT 8
""", [CID]).fetchall()
for r in rows:
    print(f"  status={r[2]:<10}  kw=[{r[1][:30]}]  term={r[0]}")

# ── 9. Null checks ────────────────────────────────────────────────────────────
print("\n--- Null checks (should all be 0) ---")
checks = [
    ("campaign_daily", "campaign_name"),
    ("campaign_daily", "bid_strategy_type"),
    ("keyword_daily", "keyword_text"),
    ("keyword_daily", "quality_score"),
    ("ad_daily", "ad_strength"),
    ("ad_group_daily", "ad_group_name"),
]
for t, col in checks:
    n = conn.execute(f"SELECT COUNT(*) FROM analytics.{t} WHERE customer_id=? AND {col} IS NULL", [CID]).fetchone()[0]
    status = "✅" if n == 0 else "❌"
    print(f"  {status}  {t}.{col} nulls: {n}")

conn.close()
print("\n✅ Verification complete.")
