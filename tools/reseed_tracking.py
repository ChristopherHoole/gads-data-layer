"""
reseed_tracking.py — seed fake open/click/CV tracking data for Analytics page testing.

SAFETY: only ever touches the fixed TEST_EMAIL_ID row.
Idempotent — safe to run multiple times.

Run before testing the Analytics page:
    python tools/reseed_tracking.py
"""
import os
import duckdb
from datetime import datetime

db_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'warehouse.duckdb'))
conn = duckdb.connect(db_path)

TEST_EMAIL_ID = "00000000-0000-0000-0000-000000000002"  # matches reseed_queue.py

# Use today so the chart shows data for the current date
now = datetime.now()
opened_at    = now
clicked_at   = now
cv_opened_at = now

conn.execute("""
    UPDATE outreach_emails
    SET open_count     = 3,
        click_count    = 1,
        cv_open_count  = 1,
        opened_at      = ?,
        clicked_at     = ?,
        cv_opened_at   = ?,
        status         = 'sent',
        sent_at        = ?
    WHERE email_id = ?
""", [opened_at, clicked_at, cv_opened_at, now, TEST_EMAIL_ID])

rows_affected = conn.execute(
    "SELECT open_count, click_count, cv_open_count FROM outreach_emails WHERE email_id = ?",
    [TEST_EMAIL_ID]
).fetchone()

conn.close()

if rows_affected:
    print(f"Done. Tracking data seeded for test lead.")
    print(f"  open_count={rows_affected[0]}, click_count={rows_affected[1]}, cv_open_count={rows_affected[2]}")
else:
    print(f"WARNING: email_id={TEST_EMAIL_ID} not found in outreach_emails. Run reseed_queue.py first.")
