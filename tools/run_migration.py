"""
Run SQL migrations on warehouse.duckdb
"""

import sys
from pathlib import Path
import duckdb


def run_migration(sql_file: str):
    """Run a SQL migration file"""
    sql_path = Path(sql_file)

    if not sql_path.exists():
        print(f"❌ Migration file not found: {sql_file}")
        sys.exit(1)

    db_path = Path("warehouse.duckdb")

    print(f"Running migration: {sql_path.name}")
    print(f"Database: {db_path}")

    # Read SQL
    sql = sql_path.read_text()

    # Execute
    conn = duckdb.connect(str(db_path))

    try:
        conn.execute(sql)
        print(f"âœ… Migration successful")

        # Verify table exists
        tables = conn.execute("SHOW TABLES").fetchall()
        print(f"\nCurrent tables: {[t[0] for t in tables]}")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python tools/run_migration.py <sql_file>")
        sys.exit(1)

    run_migration(sys.argv[1])
