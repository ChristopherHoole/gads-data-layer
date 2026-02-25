import duckdb

conn = duckdb.connect('warehouse.duckdb')

# Get 10 successful recommendation IDs
ids = conn.execute("""
    SELECT rec_id 
    FROM warehouse.recommendations 
    WHERE status = 'successful' 
    LIMIT 10
""").fetchall()

# Convert them to pending
for (rec_id,) in ids:
    conn.execute("""
        UPDATE warehouse.recommendations 
        SET status = 'pending' 
        WHERE rec_id = ?
    """, [rec_id])

conn.commit()
print(f"Converted {len(ids)} successful recommendations to pending")

# Verify
count = conn.execute("SELECT COUNT(*) FROM warehouse.recommendations WHERE status = 'pending'").fetchone()[0]
print(f"Total pending recommendations: {count}")

conn.close()
