"""
reseed_queue.py — create a single safe test email in the queue.

SAFETY: only ever touches the fixed TEST_LEAD_ID / TEST_EMAIL_ID rows.
Never re-queues real prospect emails. Protects sender reputation on
chris@christopherhoole.com.
"""
import os
import uuid
import duckdb
from datetime import datetime, date

db_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'warehouse.duckdb'))
conn = duckdb.connect(db_path)

# Fixed IDs so repeated runs are idempotent (upsert, not insert)
TEST_LEAD_ID  = "00000000-0000-0000-0000-000000000001"
TEST_EMAIL_ID = "00000000-0000-0000-0000-000000000002"
TEST_EMAIL    = "chrishoole101@gmail.com"

# Upsert the test lead
conn.execute("""
    INSERT INTO outreach_leads (
        lead_id, first_name, last_name, full_name,
        company, email, track, status, progress_stage,
        added_date, sequence_step, do_not_contact
    ) VALUES (?, 'Test', 'User', 'Test User',
              'Test Company', ?, 'Agency', 'cold', 0,
              ?, 0, false)
    ON CONFLICT (lead_id) DO UPDATE SET
        email          = excluded.email,
        progress_stage = 0,
        sequence_step  = 0
""", [TEST_LEAD_ID, TEST_EMAIL, date.today()])

# Upsert the test queued email
conn.execute("""
    INSERT INTO outreach_emails (
        email_id, lead_id, email_type, subject, body,
        status, scheduled_at, created_at
    ) VALUES (?, ?,
              'outreach',
              'Google Ads Specialist — 16 Years Experience, Available Now',
              'Hi {first_name},\n\nThis is a test send — safe to ignore.\n\nChristopher',
              'queued', ?, ?)
    ON CONFLICT (email_id) DO UPDATE SET
        status       = 'queued',
        sent_at      = NULL,
        scheduled_at = excluded.scheduled_at
""", [TEST_EMAIL_ID, TEST_LEAD_ID, datetime.now(), datetime.now()])

count = conn.execute(
    "SELECT COUNT(*) FROM outreach_emails WHERE status='queued'"
).fetchone()[0]
print(f"Done. Test email reseeded to {TEST_EMAIL}. Total queued: {count}")
conn.close()
