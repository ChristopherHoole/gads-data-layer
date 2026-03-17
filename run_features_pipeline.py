"""
Run all features pipelines for Christopher Hoole client.
Builds: campaign_features_daily, keyword_features_daily, ad_features_daily
Then copies all to warehouse_readonly.duckdb.

Run from: gads-data-layer root directory.
"""
import sys
import duckdb
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path('.').absolute()))

CID         = "1254895944"
CLIENT_ID   = "client_christopher_hoole"
SNAP_DATE   = date(2026, 3, 16)
CONFIG_PATH = Path("configs/client_christopher_hoole.yaml")

print("=" * 70)
print("FEATURES PIPELINE — Christopher Hoole")
print(f"  customer_id  : {CID}")
print(f"  snapshot_date: {SNAP_DATE}")
print("=" * 70)

# ── Step 1: Patch ad_daily — add missing columns ───────────────────────────
print("\n[0/4] Patching ad_daily — adding missing columns...")
conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")

missing_cols = [
    ("headlines",    "VARCHAR[]"),
    ("descriptions", "VARCHAR[]"),
    ("final_url",    "VARCHAR"),
]
for col, dtype in missing_cols:
    try:
        conn.execute(f"ALTER TABLE analytics.ad_daily ADD COLUMN IF NOT EXISTS {col} {dtype}")
        print(f"  Added column: {col} {dtype}")
    except Exception as e:
        print(f"  {col}: {e}")

conn.close()

# Copy patched ad_daily to readonly
conn_ro = duckdb.connect('warehouse_readonly.duckdb')
conn_ro.execute("ATTACH 'warehouse.duckdb' AS src (READ_ONLY)")
try:
    conn_ro.execute("DROP TABLE IF EXISTS analytics.ad_daily")
    conn_ro.execute("CREATE TABLE analytics.ad_daily AS SELECT * FROM src.analytics.ad_daily")
    n = conn_ro.execute("SELECT COUNT(*) FROM analytics.ad_daily").fetchone()[0]
    print(f"  Copied ad_daily to readonly: {n:,} rows")
except Exception as e:
    print(f"  ERROR copying ad_daily: {e}")
conn_ro.execute("DETACH src")
conn_ro.close()

# ── Step 2: Campaign features ──────────────────────────────────────────────
print("\n[1/4] Building campaign_features_daily...")
try:
    from act_lighthouse.config import load_client_config
    from act_lighthouse.db import DBPaths, connect_build_with_readonly_attached
    from act_lighthouse.features import build_campaign_features_daily

    cfg = load_client_config(str(CONFIG_PATH))
    con = connect_build_with_readonly_attached(
        DBPaths(build_db=Path('warehouse.duckdb'), readonly_db=Path('warehouse_readonly.duckdb'))
    )
    res = build_campaign_features_daily(con, cfg, snapshot_date=SNAP_DATE)
    print(f"  ✅ Campaign features: {res.rows_inserted} rows inserted")
    con.close()
except Exception as e:
    print(f"  ❌ Campaign features failed: {e}")
    import traceback; traceback.print_exc()

# ── Step 3: Keyword features ───────────────────────────────────────────────
print("\n[2/4] Building keyword_features_daily...")
try:
    from act_lighthouse.config import load_client_config
    from act_lighthouse.db import DBPaths, connect_build_with_readonly_attached
    from act_lighthouse.keyword_features import build_keyword_features_daily

    cfg = load_client_config(str(CONFIG_PATH))
    con = connect_build_with_readonly_attached(
        DBPaths(build_db=Path('warehouse.duckdb'), readonly_db=Path('warehouse_readonly.duckdb'))
    )
    res = build_keyword_features_daily(con, cfg, snapshot_date=SNAP_DATE)
    print(f"  ✅ Keyword features: {res.rows_inserted} rows inserted")
    con.close()
except Exception as e:
    print(f"  ❌ Keyword features failed: {e}")
    import traceback; traceback.print_exc()

# ── Step 4: Ad features ────────────────────────────────────────────────────
print("\n[3/4] Building ad_features_daily...")
try:
    from act_lighthouse.ad_features import build_ad_features_daily, save_ad_features

    con = duckdb.connect('warehouse.duckdb')
    try:
        con.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")
    except:
        pass

    features = build_ad_features_daily(con, CID, str(SNAP_DATE))
    save_ad_features(con, features)
    print(f"  ✅ Ad features: {len(features)} rows inserted")
    con.close()
except Exception as e:
    print(f"  ❌ Ad features failed: {e}")
    import traceback; traceback.print_exc()

# ── Step 5: Copy all to readonly ───────────────────────────────────────────
print("\n[4/4] Copying all features tables to warehouse_readonly.duckdb...")
tables = [
    'campaign_features_daily',
    'keyword_features_daily',
    'ad_features_daily',
]
conn_ro = duckdb.connect('warehouse_readonly.duckdb')
conn_ro.execute("ATTACH 'warehouse.duckdb' AS src (READ_ONLY)")

for table in tables:
    try:
        existing = conn_ro.execute(
            "SELECT table_type FROM information_schema.tables WHERE table_schema='analytics' AND table_name=?",
            [table]
        ).fetchone()
        if existing:
            drop_cmd = "DROP VIEW" if existing[0] == 'VIEW' else "DROP TABLE"
            conn_ro.execute(f"{drop_cmd} analytics.{table}")
        conn_ro.execute(f"CREATE TABLE analytics.{table} AS SELECT * FROM src.analytics.{table}")
        n = conn_ro.execute(f"SELECT COUNT(*) FROM analytics.{table}").fetchone()[0]
        cid_n = conn_ro.execute(f"SELECT COUNT(*) FROM analytics.{table} WHERE customer_id=?", [CID]).fetchone()[0]
        print(f"  ✅ {table}: {n:,} total rows ({cid_n:,} for Christopher Hoole)")
    except Exception as e:
        print(f"  ❌ {table}: {e}")

conn_ro.execute("DETACH src")
conn_ro.close()

print("\n" + "=" * 70)
print("✅ PIPELINE COMPLETE")
print("=" * 70)
print("Restart Flask and test Keywords and Ads pages.")
