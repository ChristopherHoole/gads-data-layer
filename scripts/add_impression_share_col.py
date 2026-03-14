"""
Migration: add impression_share_lost_rank DOUBLE to analytics.campaign_features_daily
Safe to re-run — catches "column already exists" errors.
"""
import duckdb

DB_PATHS = [
    r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb',
    r'C:\Users\User\Desktop\gads-data-layer\warehouse_readonly.duckdb',
]

for db_path in DB_PATHS:
    conn = duckdb.connect(db_path)
    try:
        conn.execute(
            "ALTER TABLE analytics.campaign_features_daily "
            "ADD COLUMN impression_share_lost_rank DOUBLE"
        )
        print(f"{db_path}: column added")
    except Exception as e:
        print(f"{db_path}: {e} (safe to ignore if column already exists)")
    finally:
        conn.close()
