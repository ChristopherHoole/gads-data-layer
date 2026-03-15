"""
Migration: add is_template column to rules table.
Chat 93 — safe to re-run (catches AlreadyExistsException).
"""
import duckdb

for db_path in [
    r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb',
    r'C:\Users\User\Desktop\gads-data-layer\warehouse_readonly.duckdb',
]:
    conn = duckdb.connect(db_path)
    try:
        conn.execute("ALTER TABLE rules ADD COLUMN is_template BOOLEAN DEFAULT FALSE")
        print(f"{db_path}: column added")
    except Exception as e:
        print(f"{db_path}: {e} (safe to ignore if column exists)")
    conn.close()

print("Migration complete.")
