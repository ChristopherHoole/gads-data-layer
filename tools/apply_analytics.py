# tools/apply_analytics.py
import os
import sys
import duckdb

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SQL_PATH = os.path.join(REPO_ROOT, "sql", "analytics_views.sql")
DB_PATH = os.path.join(REPO_ROOT, "warehouse.duckdb")


def main() -> int:
    if not os.path.exists(DB_PATH):
        print(f"ERROR: DuckDB not found: {DB_PATH}")
        return 1

    if not os.path.exists(SQL_PATH):
        print(f"ERROR: SQL file not found: {SQL_PATH}")
        return 1

    sql_text = open(SQL_PATH, "r", encoding="utf-8").read()

    # Split on semicolons; execute statement-by-statement
    statements = [s.strip() for s in sql_text.split(";") if s.strip()]

    con = duckdb.connect(DB_PATH)
    try:
        for stmt in statements:
            con.execute(stmt)
        print("SUCCESS: analytics views applied to warehouse.duckdb")
        return 0
    finally:
        con.close()


if __name__ == "__main__":
    raise SystemExit(main())
