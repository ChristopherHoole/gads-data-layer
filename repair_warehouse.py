"""
Repair warehouse.duckdb by forcing a clean checkpoint.
This resolves WAL files left by scripts that exited uncleanly.
"""
import duckdb
import os

print("=" * 60)
print("WAREHOUSE.DUCKDB REPAIR")
print("=" * 60)

# Check for WAL files
print("\nChecking for WAL files...")
for f in os.listdir('.'):
    if 'warehouse' in f and 'duckdb' in f:
        size = os.path.getsize(f)
        print(f"  {f}  ({size:,} bytes)")

print("\nOpening warehouse.duckdb...")
conn = duckdb.connect('warehouse.duckdb')
print("  ✅ Connected")

print("\nRunning CHECKPOINT...")
try:
    conn.execute("CHECKPOINT")
    print("  ✅ CHECKPOINT complete")
except Exception as e:
    print(f"  ⚠️  CHECKPOINT: {e}")

print("\nRunning PRAGMA database_list...")
try:
    rows = conn.execute("PRAGMA database_list").fetchall()
    for r in rows:
        print(f"  {r}")
except Exception as e:
    print(f"  ⚠️  {e}")

print("\nClosing connection cleanly...")
conn.close()
print("  ✅ Closed")

print("\nChecking WAL files after repair...")
for f in os.listdir('.'):
    if 'warehouse' in f and 'duckdb' in f:
        size = os.path.getsize(f)
        print(f"  {f}  ({size:,} bytes)")

print("\n✅ Repair complete. Try starting Flask now.")
