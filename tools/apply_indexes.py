"""
Apply performance indexes to DuckDB database.
Run this script to add indexes that improve query performance.
"""

import duckdb
import sys
from pathlib import Path
from datetime import datetime


def apply_indexes(db_path: str = "warehouse.duckdb"):
    """Apply performance indexes from migration file."""

    print("=" * 80)
    print("PERFORMANCE OPTIMIZATION - Adding Database Indexes")
    print("=" * 80)
    print()

    # Connect to database
    print(f"Connecting to database: {db_path}")
    conn = duckdb.connect(db_path)

    # Read migration file
    migration_file = (
        Path(__file__).parent / "migrations" / "add_performance_indexes.sql"
    )

    if not migration_file.exists():
        print(f"❌ ERROR: Migration file not found: {migration_file}")
        return 1

    print(f"Reading migration file: {migration_file}")
    sql = migration_file.read_text()

    # Execute migration
    print("\nApplying indexes...")
    try:
        # Split by semicolon and execute each statement
        statements = [
            s.strip()
            for s in sql.split(";")
            if s.strip() and not s.strip().startswith("--")
        ]

        for i, statement in enumerate(statements, 1):
            if "CREATE INDEX" in statement.upper():
                # Extract index name
                lines = statement.split("\n")
                index_line = [l for l in lines if "CREATE INDEX" in l.upper()][0]
                index_name = (
                    index_line.split("idx_")[1].split()[0]
                    if "idx_" in index_line
                    else "unknown"
                )

                print(f"  {i}. Creating index: idx_{index_name}...", end=" ")
                conn.execute(statement)
                print("✅")

            elif "SELECT" in statement.upper() and "duckdb_indexes" in statement:
                # Verify indexes query
                print("\nVerifying indexes created:")
                print("-" * 80)
                result = conn.execute(statement).fetchall()

                for row in result:
                    table_name, index_name, col_count = row
                    print(
                        f"  {table_name:30s} | {index_name:40s} | {col_count} columns"
                    )

        print("-" * 80)
        print("\n✅ All indexes applied successfully!")

    except Exception as e:
        print(f"\n❌ ERROR: Failed to apply indexes")
        print(f"Error: {e}")
        return 1

    finally:
        conn.close()

    print()
    print("=" * 80)
    print("COMPLETE - Database indexes optimized")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "warehouse.duckdb"
    sys.exit(apply_indexes(db_path))
