"""
Migration: Add entity_type and entity_id columns to changes table

Chat 47 - Step 6
Adds entity_type and entity_id columns to support multi-entity recommendations.
"""

import duckdb
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "warehouse.duckdb"

print("=" * 80)
print("CHANGES TABLE MIGRATION - ADD ENTITY COLUMNS")
print("=" * 80)
print(f"Database: {DB_PATH}")

conn = duckdb.connect(str(DB_PATH))

try:
    # Check current schema
    print("\n[BEFORE] Current changes table schema:")
    result = conn.execute("DESCRIBE changes").fetchall()
    for row in result:
        print(f"  {row[0]}: {row[1]}")
    
    existing_columns = [row[0] for row in result]
    
    # Add entity_type column if it doesn't exist
    if "entity_type" not in existing_columns:
        print("\n[MIGRATION] Adding entity_type column...")
        conn.execute("ALTER TABLE changes ADD COLUMN entity_type VARCHAR")
        print("[MIGRATION] ✅ Added entity_type column")
    else:
        print("\n[MIGRATION] ⚠️  entity_type column already exists")
    
    # Add entity_id column if it doesn't exist
    if "entity_id" not in existing_columns:
        print("[MIGRATION] Adding entity_id column...")
        conn.execute("ALTER TABLE changes ADD COLUMN entity_id VARCHAR")
        print("[MIGRATION] ✅ Added entity_id column")
    else:
        print("[MIGRATION] ⚠️  entity_id column already exists")
    
    # Verify new schema
    print("\n[AFTER] Updated changes table schema:")
    result = conn.execute("DESCRIBE changes").fetchall()
    for row in result:
        print(f"  {row[0]}: {row[1]}")
    
    # Check if there are existing rows that need migration
    row_count = conn.execute("SELECT COUNT(*) FROM changes").fetchone()[0]
    print(f"\n[INFO] Total rows in changes table: {row_count}")
    
    if row_count > 0:
        # Migrate existing rows: set entity_type='campaign', entity_id=campaign_id
        print("[MIGRATION] Migrating existing rows...")
        conn.execute("""
            UPDATE changes 
            SET entity_type = 'campaign',
                entity_id = campaign_id
            WHERE entity_type IS NULL AND campaign_id IS NOT NULL
        """)
        
        migrated = conn.execute("""
            SELECT COUNT(*) FROM changes 
            WHERE entity_type = 'campaign'
        """).fetchone()[0]
        
        print(f"[MIGRATION] ✅ Migrated {migrated} existing rows to entity_type='campaign'")
    
    print("\n" + "=" * 80)
    print("✅ MIGRATION COMPLETE")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ MIGRATION FAILED: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()
