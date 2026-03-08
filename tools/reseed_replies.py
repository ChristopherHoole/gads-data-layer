"""
reseed_replies.py — seed a fake inbound reply for safe Replies page testing.

SAFETY: only ever touches the fixed TEST_LEAD_ID row.
Never inserts real prospect email addresses.

Run before testing the Replies page:
    python tools/reseed_replies.py
"""
import os
import duckdb
from datetime import datetime

db_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'warehouse.duckdb'))
conn = duckdb.connect(db_path)

TEST_LEAD_ID  = "00000000-0000-0000-0000-000000000001"
TEST_EMAIL    = "chrishoole101@gmail.com"
TEST_REPLY_ID = "00000000-0000-0000-0000-000000000010"
TEST_OE_ID    = "00000000-0000-0000-0000-000000000011"  # outreach_emails row

# 1. Create email_replies table if not exists
conn.execute("""
    CREATE TABLE IF NOT EXISTS email_replies (
        id          VARCHAR PRIMARY KEY,
        lead_id     VARCHAR,
        from_email  VARCHAR,
        from_name   VARCHAR,
        subject     VARCHAR,
        body        VARCHAR,
        received_at TIMESTAMP,
        read        BOOLEAN DEFAULT false
    )
""")

# 2. Upsert the test reply into email_replies
conn.execute("""
    INSERT INTO email_replies (id, lead_id, from_email, from_name, subject, body, received_at, read)
    VALUES (?, ?, ?, 'Test User',
            'Re: Google Ads Specialist — 16 Years Experience, Available Now',
            'Hi Christopher, thanks for reaching out. I''d be interested in learning more.',
            ?, false)
    ON CONFLICT (id) DO UPDATE SET
        from_email  = excluded.from_email,
        subject     = excluded.subject,
        body        = excluded.body,
        received_at = excluded.received_at,
        read        = false
""", [TEST_REPLY_ID, TEST_LEAD_ID, TEST_EMAIL, datetime.now()])

# 3. Upsert a sent email with reply_received=true so Replies page shows it
conn.execute("""
    INSERT INTO outreach_emails (
        email_id, lead_id, email_type, subject, body,
        status, sent_at, created_at,
        reply_received, reply_read, reply_text
    ) VALUES (?, ?,
              'initial',
              'Google Ads Specialist — 16 Years Experience, Available Now',
              'Hi {first_name},\n\nThis is a test send — safe to ignore.\n\nChristopher',
              'sent', ?, ?,
              true, false,
              'Hi Christopher, thanks for reaching out. I''d be interested in learning more.')
    ON CONFLICT (email_id) DO UPDATE SET
        status         = 'sent',
        reply_received = true,
        reply_read     = false,
        reply_text     = excluded.reply_text
""", [TEST_OE_ID, TEST_LEAD_ID, datetime.now(), datetime.now()])

# 4. Always set test lead status to 'replied' last — overrides anything reseed_queue.py set
conn.execute(
    "UPDATE outreach_leads SET status = 'replied', last_activity = ? WHERE lead_id = ?",
    [datetime.now(), TEST_LEAD_ID],
)

# Confirm
row = conn.execute(
    "SELECT id, from_email, subject FROM email_replies WHERE id = ?", [TEST_REPLY_ID]
).fetchone()
print(f"Done. Test reply seeded for {TEST_EMAIL}.")
print(f"  email_replies row: id={row[0]}, from={row[1]}")
conn.close()
