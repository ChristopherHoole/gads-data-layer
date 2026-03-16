"""
JOB 2 — Disable 5 technical flags that use wrong proxy metrics
Master Chat 12

Flags 49, 50, 51, 53, 54 all use pacing_flag_over_105 as a proxy.
They cannot fire correctly without real API data.
Disabling them until pipeline supports the real columns.
"""

import duckdb
from datetime import datetime

conn = duckdb.connect('warehouse.duckdb')
now = datetime.now()

flags_to_disable = [
    (49, 'Landing Page Down'),
    (50, 'Landing Page Slow'),
    (51, 'Ad Disapproved'),
    (53, 'Billing Issue'),
    (54, 'Tracking Tag Missing'),
]

print("=" * 60)
print("JOB 2 — Disable 5 technical proxy flags")
print("=" * 60)

for flag_id, flag_name in flags_to_disable:
    conn.execute(
        "UPDATE rules SET enabled = FALSE, updated_at = ? WHERE id = ?",
        [now, flag_id]
    )
    row = conn.execute(
        "SELECT name, enabled FROM rules WHERE id = ?", [flag_id]
    ).fetchone()
    print(f"  Flag {flag_id}: {row[0]} — enabled: {row[1]}")

print()
print("=== FINAL FLAG STATE ===")
rows = conn.execute(
    "SELECT id, name, enabled FROM rules "
    "WHERE rule_or_flag = 'flag' AND is_template = FALSE "
    "ORDER BY id"
).fetchall()
enabled_count = sum(1 for r in rows if r[2])
disabled_count = sum(1 for r in rows if not r[2])
print(f"Total flags: {len(rows)} | Enabled: {enabled_count} | Disabled: {disabled_count}")

conn.close()
print("\n✅ Job 2 — proxy flags disabled.")
