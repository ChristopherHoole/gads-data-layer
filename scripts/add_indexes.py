"""
Add performance indexes to warehouse_readonly.duckdb on all 6 analytics tables.

Indexes target the most common query patterns (entity ID, campaign ID, date).
Only warehouse_readonly.duckdb is indexed -- never warehouse.duckdb.

Run from: gads-data-layer root directory.
"""

import duckdb

INDEXES = [
    # campaign_daily
    ("idx_campaign_daily_campaign_id",  "analytics.campaign_daily",  "campaign_id"),
    ("idx_campaign_daily_date",         "analytics.campaign_daily",  "snapshot_date"),

    # keyword_daily
    ("idx_keyword_daily_keyword_id",    "analytics.keyword_daily",   "keyword_id"),
    ("idx_keyword_daily_campaign_id",   "analytics.keyword_daily",   "campaign_id"),
    ("idx_keyword_daily_date",          "analytics.keyword_daily",   "snapshot_date"),

    # ad_group_daily
    ("idx_ad_group_daily_ag_id",        "analytics.ad_group_daily",  "ad_group_id"),
    ("idx_ad_group_daily_campaign_id",  "analytics.ad_group_daily",  "campaign_id"),
    ("idx_ad_group_daily_date",         "analytics.ad_group_daily",  "snapshot_date"),

    # ad_daily
    ("idx_ad_daily_ad_id",              "analytics.ad_daily",        "ad_id"),
    ("idx_ad_daily_campaign_id",        "analytics.ad_daily",        "campaign_id"),
    ("idx_ad_daily_date",               "analytics.ad_daily",        "snapshot_date"),

    # shopping_campaign_daily
    ("idx_shopping_daily_campaign_id",  "analytics.shopping_campaign_daily", "campaign_id"),
    ("idx_shopping_daily_date",         "analytics.shopping_campaign_daily", "snapshot_date"),
]


def add_indexes():
    """Add indexes to warehouse_readonly.duckdb."""
    print("=" * 70)
    print("ADD INDEXES -> warehouse_readonly.duckdb")
    print("=" * 70)

    conn = duckdb.connect("warehouse_readonly.duckdb")

    created = 0
    skipped = 0
    errors = []

    for idx_name, table_name, column in INDEXES:
        try:
            # Check if table exists before indexing
            schema, tbl = table_name.split(".")
            exists = conn.execute(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = ? AND table_name = ?",
                [schema, tbl],
            ).fetchone()[0]

            if not exists:
                print(f"  [skip] {table_name} not found -- skipping {idx_name}")
                skipped += 1
                continue

            conn.execute(
                f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name} ({column})"
            )
            print(f"  [ok]   {idx_name} ON {table_name}({column})")
            created += 1

        except Exception as e:
            msg = f"{idx_name}: {e}"
            print(f"  [err]  {msg}")
            errors.append(msg)

    # Verify via information_schema
    print("\n[verify] Indexes in warehouse_readonly.duckdb:")
    try:
        index_rows = conn.execute("""
            SELECT index_name, table_name
            FROM duckdb_indexes()
            ORDER BY table_name, index_name
        """).fetchall()
        for row in index_rows:
            print(f"  {row[0]}  -->  {row[1]}")
        verified_count = len(index_rows)
    except Exception as e:
        print(f"  [warn] Could not query duckdb_indexes(): {e}")
        verified_count = -1

    conn.close()

    print("\n" + "=" * 70)
    print(f"COMPLETE -- created: {created}, skipped: {skipped}, errors: {len(errors)}")
    if verified_count >= 0:
        print(f"Total indexes verified: {verified_count}")
    if errors:
        print("Errors:")
        for err in errors:
            print(f"  {err}")
    print("=" * 70)
    return {"created": created, "skipped": skipped, "errors": errors}


if __name__ == "__main__":
    add_indexes()
