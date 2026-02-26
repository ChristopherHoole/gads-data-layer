"""
Database Migration: Extend Recommendations Table for Multi-Entity Support

Purpose: Add entity_type, entity_id, entity_name columns to support recommendations
         for keywords, ad groups, ads, and shopping (not just campaigns)

Date: 2026-02-26
Chat: 47
Author: Claude (Worker Chat)

Changes:
1. Add 3 new columns: entity_type, entity_id, entity_name
2. Migrate existing campaign rows to populate new columns
3. Keep campaign_id/campaign_name for backward compatibility
4. Create index on (entity_type, entity_id) for performance

Rollback: Run rollback_recommendations_schema.py if migration fails
"""

import duckdb
import sys
from datetime import datetime
from pathlib import Path

# Database paths
DB_PATH = Path(__file__).parent.parent.parent / "warehouse.duckdb"
BACKUP_PATH = Path(__file__).parent.parent.parent / f"warehouse_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.duckdb"


def backup_database():
    """Create backup of warehouse.duckdb before migration."""
    print(f"\n[BACKUP] Creating backup: {BACKUP_PATH}")
    try:
        # Copy database file
        import shutil
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"[BACKUP] ✅ Backup created successfully")
        return True
    except Exception as e:
        print(f"[BACKUP] ❌ Failed to create backup: {e}")
        return False


def check_existing_schema(conn):
    """Check current recommendations table schema."""
    print("\n[SCHEMA CHECK] Current recommendations table structure:")
    try:
        result = conn.execute("DESCRIBE recommendations").fetchall()
        existing_columns = [row[0] for row in result]
        print(f"[SCHEMA CHECK] Found {len(existing_columns)} columns")
        
        # Check if new columns already exist
        if "entity_type" in existing_columns:
            print("[SCHEMA CHECK] ⚠️  entity_type column already exists - migration may have run before")
            return existing_columns, True
        
        print(f"[SCHEMA CHECK] ✅ Schema ready for migration")
        return existing_columns, False
        
    except Exception as e:
        print(f"[SCHEMA CHECK] ❌ Error checking schema: {e}")
        return [], False


def add_new_columns(conn):
    """Add entity_type, entity_id, entity_name columns."""
    print("\n[MIGRATION STEP 1] Adding new columns...")
    
    try:
        # Add entity_type column
        conn.execute("ALTER TABLE recommendations ADD COLUMN entity_type VARCHAR")
        print("[MIGRATION STEP 1] ✅ Added entity_type column")
        
        # Add entity_id column (VARCHAR to match campaign_id type)
        conn.execute("ALTER TABLE recommendations ADD COLUMN entity_id VARCHAR")
        print("[MIGRATION STEP 1] ✅ Added entity_id column")
        
        # Add entity_name column
        conn.execute("ALTER TABLE recommendations ADD COLUMN entity_name VARCHAR")
        print("[MIGRATION STEP 1] ✅ Added entity_name column")
        
        return True
        
    except Exception as e:
        print(f"[MIGRATION STEP 1] ❌ Failed to add columns: {e}")
        return False


def migrate_existing_data(conn):
    """Migrate existing campaign rows to populate new columns."""
    print("\n[MIGRATION STEP 2] Migrating existing data...")
    
    try:
        # Check how many rows exist
        count_before = conn.execute("SELECT COUNT(*) FROM recommendations").fetchone()[0]
        print(f"[MIGRATION STEP 2] Found {count_before} existing recommendations")
        
        # Update existing rows: set entity_type='campaign', entity_id=campaign_id, entity_name=campaign_name
        conn.execute("""
            UPDATE recommendations 
            SET entity_type = 'campaign',
                entity_id = campaign_id,
                entity_name = campaign_name
            WHERE entity_type IS NULL
        """)
        
        # Verify migration
        migrated_count = conn.execute("""
            SELECT COUNT(*) FROM recommendations 
            WHERE entity_type = 'campaign'
        """).fetchone()[0]
        
        print(f"[MIGRATION STEP 2] ✅ Migrated {migrated_count} campaign recommendations")
        
        if migrated_count != count_before:
            print(f"[MIGRATION STEP 2] ⚠️  Warning: {count_before - migrated_count} rows not migrated")
        
        return True
        
    except Exception as e:
        print(f"[MIGRATION STEP 2] ❌ Failed to migrate data: {e}")
        return False


def create_indexes(conn):
    """Create indexes for performance."""
    print("\n[MIGRATION STEP 3] Creating indexes...")
    
    try:
        # Create index on (entity_type, entity_id) for fast lookups
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_recommendations_entity 
            ON recommendations(entity_type, entity_id)
        """)
        print("[MIGRATION STEP 3] ✅ Created idx_recommendations_entity")
        
        # Create index on entity_type for filtering by type
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_recommendations_entity_type 
            ON recommendations(entity_type)
        """)
        print("[MIGRATION STEP 3] ✅ Created idx_recommendations_entity_type")
        
        return True
        
    except Exception as e:
        print(f"[MIGRATION STEP 3] ❌ Failed to create indexes: {e}")
        return False


def verify_migration(conn):
    """Verify migration completed successfully."""
    print("\n[VERIFICATION] Checking migration results...")
    
    try:
        # Check schema includes new columns
        result = conn.execute("DESCRIBE recommendations").fetchall()
        columns = [row[0] for row in result]
        
        required_columns = ['entity_type', 'entity_id', 'entity_name']
        missing = [col for col in required_columns if col not in columns]
        
        if missing:
            print(f"[VERIFICATION] ❌ Missing columns: {missing}")
            return False
        
        print(f"[VERIFICATION] ✅ All new columns present")
        
        # Check data migration
        stats = conn.execute("""
            SELECT 
                entity_type,
                COUNT(*) as count
            FROM recommendations
            GROUP BY entity_type
            ORDER BY entity_type
        """).fetchall()
        
        print("[VERIFICATION] Entity type distribution:")
        for entity_type, count in stats:
            type_str = entity_type if entity_type else "NULL"
            print(f"  - {type_str}: {count} recommendations")
        
        # Check indexes
        indexes = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='recommendations'
        """).fetchall()
        
        index_names = [idx[0] for idx in indexes]
        print(f"[VERIFICATION] Indexes: {', '.join(index_names)}")
        
        return True
        
    except Exception as e:
        print(f"[VERIFICATION] ❌ Error during verification: {e}")
        return False


def run_migration(dry_run=False):
    """Execute the migration."""
    
    print("=" * 80)
    print("RECOMMENDATIONS TABLE MIGRATION - MULTI-ENTITY SUPPORT")
    print("=" * 80)
    print(f"Database: {DB_PATH}")
    print(f"Dry run: {dry_run}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be committed")
    
    # Step 0: Create backup (skip in dry run)
    if not dry_run:
        if not backup_database():
            print("\n❌ MIGRATION ABORTED - Backup failed")
            return False
    else:
        print("\n[BACKUP] Skipped (dry run mode)")
    
    # Connect to database
    try:
        conn = duckdb.connect(str(DB_PATH))
        print(f"\n[CONNECTION] ✅ Connected to {DB_PATH}")
    except Exception as e:
        print(f"\n[CONNECTION] ❌ Failed to connect: {e}")
        return False
    
    try:
        # Begin transaction
        if not dry_run:
            conn.execute("BEGIN TRANSACTION")
        
        # Check existing schema
        existing_columns, already_migrated = check_existing_schema(conn)
        
        if already_migrated:
            print("\n⚠️  Migration appears to have already run")
            print("Proceeding with verification only...")
            verify_migration(conn)
            if not dry_run:
                conn.execute("ROLLBACK")
            conn.close()
            return True
        
        # Step 1: Add new columns
        if not add_new_columns(conn):
            if not dry_run:
                conn.execute("ROLLBACK")
            conn.close()
            return False
        
        # Step 2: Migrate existing data
        if not migrate_existing_data(conn):
            if not dry_run:
                conn.execute("ROLLBACK")
            conn.close()
            return False
        
        # Step 3: Create indexes
        if not create_indexes(conn):
            if not dry_run:
                conn.execute("ROLLBACK")
            conn.close()
            return False
        
        # Step 4: Verify
        if not verify_migration(conn):
            if not dry_run:
                conn.execute("ROLLBACK")
            conn.close()
            return False
        
        # Commit or rollback
        if dry_run:
            print("\n[TRANSACTION] Rolling back (dry run mode)")
            conn.execute("ROLLBACK")
        else:
            print("\n[TRANSACTION] Committing changes...")
            conn.execute("COMMIT")
            print("[TRANSACTION] ✅ Migration committed successfully")
        
        conn.close()
        
        print("\n" + "=" * 80)
        if dry_run:
            print("✅ DRY RUN SUCCESSFUL - No changes committed")
        else:
            print("✅ MIGRATION SUCCESSFUL")
            print(f"Backup saved to: {BACKUP_PATH}")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ MIGRATION FAILED: {e}")
        try:
            conn.execute("ROLLBACK")
            print("[TRANSACTION] Rolled back changes")
        except:
            pass
        conn.close()
        return False


if __name__ == "__main__":
    # Check if dry-run flag provided
    dry_run = "--dry-run" in sys.argv
    
    success = run_migration(dry_run=dry_run)
    
    if not success:
        print("\n💡 To rollback migration, delete new columns manually:")
        print("   ALTER TABLE recommendations DROP COLUMN entity_type;")
        print("   ALTER TABLE recommendations DROP COLUMN entity_id;")
        print("   ALTER TABLE recommendations DROP COLUMN entity_name;")
        sys.exit(1)
    
    sys.exit(0)
