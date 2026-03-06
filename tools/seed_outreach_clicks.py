#!/usr/bin/env python3
"""
tools/seed_outreach_clicks.py

Seeds realistic click_count and cv_open_count values into outreach_emails.
Run once from project root:
    python tools/seed_outreach_clicks.py

Logic:
  - click_count > 0 only if open_count > 0
  - cv_open_count > 0 only if cv_attached = true AND click_count > 0
  - Probabilities tuned to produce ~30% click rate, ~18% CV open rate
"""
import duckdb
import random
from pathlib import Path

random.seed(99)

WAREHOUSE_PATH = Path(__file__).parent.parent / "warehouse.duckdb"

def main():
    conn = duckdb.connect(str(WAREHOUSE_PATH))

    rows = conn.execute("""
        SELECT email_id, open_count, cv_attached
        FROM outreach_emails
        WHERE status = 'sent'
    """).fetchall()

    print(f"Updating {len(rows)} sent emails with click / cv_open data...")

    updated = 0
    for email_id, open_count, cv_attached in rows:
        if not open_count or open_count == 0:
            continue  # never clicked if never opened

        # click probability scales with open_count
        if open_count >= 3:
            click_prob = 0.60
        elif open_count == 2:
            click_prob = 0.40
        else:  # open_count == 1
            click_prob = 0.20

        if random.random() < click_prob:
            click_count = random.randint(1, open_count)
        else:
            click_count = 0

        # CV open only possible if email had cv attached and they clicked
        cv_open_count = 0
        if cv_attached and click_count > 0:
            if random.random() < 0.65:  # 65% of cv_attached+clicked -> cv opened
                cv_open_count = random.randint(1, click_count)

        if click_count > 0 or cv_open_count > 0:
            conn.execute(
                "UPDATE outreach_emails SET click_count = ?, cv_open_count = ? WHERE email_id = ?",
                [click_count, cv_open_count, email_id]
            )
            updated += 1

    print(f"  Updated {updated} emails with click/cv_open data.")

    # Verify
    r = conn.execute("""
        SELECT
            COUNT(*) FILTER (WHERE open_count > 0)    AS opened,
            COUNT(*) FILTER (WHERE click_count > 0)   AS clicked,
            COUNT(*) FILTER (WHERE cv_open_count > 0) AS cv_opened,
            COUNT(*)                                   AS total
        FROM outreach_emails WHERE status = 'sent'
    """).fetchone()
    print(f"\nVerification (sent emails):")
    print(f"  opened:    {r[0]} / {r[3]}  ({r[0]/r[3]*100:.0f}%)")
    print(f"  clicked:   {r[1]} / {r[3]}  ({r[1]/r[3]*100:.0f}%)")
    print(f"  cv_opened: {r[2]} / {r[3]}  ({r[2]/r[3]*100:.0f}%)")

    conn.close()

if __name__ == "__main__":
    main()
