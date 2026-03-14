#!/usr/bin/env python3
"""
tools/migrate_rules_schema.py

Chat 91: Creates rules table, rule_evaluation_log table in warehouse.duckdb.
         Adds nullable rule_id FK column to recommendations table.
         Wipes all existing rows from recommendations.
         Safe to re-run (checks existence before creating).

Run from project root:
    python tools/migrate_rules_schema.py
"""

import sys
from pathlib import Path
import duckdb

WAREHOUSE_PATH = Path(__file__).parent.parent / "warehouse.duckdb"


def main():
    print("=" * 60)
    print("Chat 91: migrate_rules_schema.py")
    print("=" * 60)

    if not WAREHOUSE_PATH.exists():
        print(f"ERROR: warehouse.duckdb not found at {WAREHOUSE_PATH}")
        sys.exit(1)

    conn = duckdb.connect(str(WAREHOUSE_PATH))

    try:
        # ── Create rules table ────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                id                INTEGER PRIMARY KEY,
                client_config     VARCHAR NOT NULL,
                entity_type       VARCHAR NOT NULL DEFAULT 'campaign',
                name              VARCHAR NOT NULL,
                rule_or_flag      VARCHAR NOT NULL,
                type              VARCHAR NOT NULL,
                campaign_type_lock VARCHAR,
                entity_scope      JSON NOT NULL DEFAULT '{"scope":"all"}',
                conditions        JSON NOT NULL,
                action_type       VARCHAR,
                action_magnitude  FLOAT,
                cooldown_days     INTEGER DEFAULT 7,
                risk_level        VARCHAR,
                enabled           BOOLEAN NOT NULL DEFAULT TRUE,
                created_at        TIMESTAMP DEFAULT NOW(),
                updated_at        TIMESTAMP DEFAULT NOW(),
                last_evaluated_at TIMESTAMP,
                last_fired_at     TIMESTAMP
            )
        """)
        print("✅  rules table: created (or already exists)")

        # ── Create rule_evaluation_log table ──────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rule_evaluation_log (
                id                INTEGER PRIMARY KEY,
                rule_id           INTEGER NOT NULL,
                entity_type       VARCHAR NOT NULL,
                entity_id         VARCHAR NOT NULL,
                evaluated_at      TIMESTAMP DEFAULT NOW(),
                conditions_met    BOOLEAN NOT NULL,
                recommendation_id INTEGER,
                skip_reason       VARCHAR
            )
        """)
        print("✅  rule_evaluation_log table: created (or already exists)")

        # ── Add rule_id column to recommendations ─────────────────────────────
        try:
            conn.execute("ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS rule_id INTEGER")
            print("✅  recommendations.rule_id column: added (or already exists)")
        except Exception as e:
            print(f"   (recommendations.rule_id: {e})")

        # ── Wipe existing recommendations ─────────────────────────────────────
        result = conn.execute("DELETE FROM recommendations").fetchone()
        print("✅  recommendations: all rows wiped")

        conn.commit()
        print()
        print("Migration complete. Run seed_campaign_rules.py next.")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
