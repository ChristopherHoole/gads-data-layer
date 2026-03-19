"""
Create flags table in warehouse.duckdb — Chat 101

Run once to create the flags table. Safe to run multiple times (CREATE TABLE IF NOT EXISTS).
"""

import duckdb
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "warehouse.duckdb"


def create_flags_table():
    conn = duckdb.connect(str(DB_PATH))

    conn.execute("""
        CREATE TABLE IF NOT EXISTS flags (
            flag_id         VARCHAR PRIMARY KEY,
            rule_id         VARCHAR,
            rule_name       VARCHAR,
            entity_type     VARCHAR,
            entity_id       VARCHAR,
            entity_name     VARCHAR,
            customer_id     VARCHAR,
            status          VARCHAR DEFAULT 'active',
            severity        VARCHAR,
            trigger_summary VARCHAR,
            plain_english   VARCHAR,
            conditions      VARCHAR,
            generated_at    TIMESTAMP,
            acknowledged_at TIMESTAMP,
            snooze_until    TIMESTAMP,
            snooze_days     INTEGER,
            updated_at      TIMESTAMP
        )
    """)

    row_count = conn.execute("SELECT COUNT(*) FROM flags").fetchone()[0]
    print(f"[FLAGS TABLE] Created successfully. Current row count: {row_count}")

    conn.close()


if __name__ == "__main__":
    create_flags_table()
