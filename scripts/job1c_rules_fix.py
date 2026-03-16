"""
JOB 1C — DB Rules Cleanup (third pass)
Master Chat 12 — Rules Strategic Review

Changes:
1. Rule 16 — campaign_type_lock: all → troas
2. Rule 17 — campaign_type_lock: all → troas
3. Rule 18 — campaign_type_lock: all → tcpa
"""

import duckdb
from datetime import datetime

conn = duckdb.connect('warehouse.duckdb')
now = datetime.now()

print("=" * 60)
print("JOB 1C — DB Rules Cleanup (third pass)")
print("=" * 60)

# ── 1. Rule 16 — lock: all → troas ───────────────────────────
print("\n[1] Rule 16 — campaign_type_lock: all → troas...")
conn.execute(
    "UPDATE rules SET campaign_type_lock = 'troas', updated_at = ? WHERE id = 16",
    [now]
)
row = conn.execute("SELECT name, campaign_type_lock FROM rules WHERE id = 16").fetchone()
print(f"    {row[0]} — lock: {row[1]}")

# ── 2. Rule 17 — lock: all → troas ───────────────────────────
print("\n[2] Rule 17 — campaign_type_lock: all → troas...")
conn.execute(
    "UPDATE rules SET campaign_type_lock = 'troas', updated_at = ? WHERE id = 17",
    [now]
)
row = conn.execute("SELECT name, campaign_type_lock FROM rules WHERE id = 17").fetchone()
print(f"    {row[0]} — lock: {row[1]}")

# ── 3. Rule 18 — lock: all → tcpa ────────────────────────────
print("\n[3] Rule 18 — campaign_type_lock: all → tcpa...")
conn.execute(
    "UPDATE rules SET campaign_type_lock = 'tcpa', updated_at = ? WHERE id = 18",
    [now]
)
row = conn.execute("SELECT name, campaign_type_lock FROM rules WHERE id = 18").fetchone()
print(f"    {row[0]} — lock: {row[1]}")

# ── Final state check ─────────────────────────────────────────
print("\n" + "=" * 60)
print("FINAL STATE — ALL CAMPAIGN TYPE LOCKS")
print("=" * 60)

rows = conn.execute(
    "SELECT id, name, campaign_type_lock FROM rules "
    "WHERE rule_or_flag = 'rule' AND is_template = FALSE "
    "ORDER BY id"
).fetchall()
for r in rows:
    print(f"  Rule {r[0]}: {r[1]} — lock: {r[2]}")

conn.close()
print("\n✅ Job 1C complete.")
