import duckdb, os
db_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'warehouse.duckdb'))
conn = duckdb.connect(db_path)
conn.execute("""
    UPDATE outreach_emails
    SET status='queued', sent_at=NULL
    WHERE email_id IN (
        SELECT email_id FROM outreach_emails
        WHERE status='sent'
        LIMIT 5
    )
""")
count = conn.execute("SELECT COUNT(*) FROM outreach_emails WHERE status='queued'").fetchone()[0]
print(f'Done. Queued emails: {count}')
conn.close()
