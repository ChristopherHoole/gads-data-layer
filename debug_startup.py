"""
Debug: isolate exact line in outreach.py that causes crash
"""
import sys, os, traceback
sys.path.insert(0, '.')

print("Step 1: Testing duckdb connect to warehouse.duckdb...")
import duckdb
try:
    conn = duckdb.connect('warehouse.duckdb')
    print("  ✅ Connected")
    conn.close()
    print("  ✅ Closed")
except Exception as e:
    print(f"  ❌ {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nStep 2: Check for WAL or lock files...")
import glob
files = glob.glob('warehouse*.duckdb*')
for f in files:
    size = os.path.getsize(f)
    print(f"  {f} ({size:,} bytes)")

print("\nStep 3: Testing _ensure_schema manually...")
try:
    _WAREHOUSE_PATH = os.path.normpath('warehouse.duckdb')
    conn = duckdb.connect(_WAREHOUSE_PATH)
    print("  ✅ Connected for schema")
    
    # Test the exact ALTER TABLE that runs after the migration
    conn.execute("ALTER TABLE outreach_emails ADD COLUMN IF NOT EXISTS scheduled_at TIMESTAMP")
    print("  ✅ ALTER TABLE succeeded")
    conn.close()
    print("  ✅ Closed")
except Exception as e:
    print(f"  ❌ {e}")
    traceback.print_exc()

print("\nStep 4: Importing outreach with verbose error catching...")
try:
    import act_dashboard.routes.outreach as o
    print("  ✅ outreach imported OK")
except SystemExit as e:
    print(f"  ❌ SystemExit: {e.code}")
    traceback.print_exc()
except Exception as e:
    print(f"  ❌ Exception: {e}")
    traceback.print_exc()

print("\nDone.")
