"""
JOB 1B — DB Rules Cleanup (second pass)
Master Chat 12 — Rules Strategic Review

Changes:
1. Rule 2  — campaign_type_lock: all → troas
2. Rule 7  — campaign_type_lock: all → tcpa
3. Rule 12 — campaign_type_lock: all → max_clicks
4. Rule 21 — CPC threshold: £3 → £5
"""

import duckdb
import json
from datetime import datetime

conn = duckdb.connect('warehouse.duckdb')
now = datetime.now()

print("=" * 60)
print("JOB 1B — DB Rules Cleanup (second pass)")
print("=" * 60)

# ── 1. Rule 2 — lock: all → troas ────────────────────────────
print("\n[1] Rule 2 — campaign_type_lock: all → troas...")
conn.execute(
    "UPDATE rules SET campaign_type_lock = 'troas', updated_at = ? WHERE id = 2",
    [now]
)
row = conn.execute("SELECT name, campaign_type_lock FROM rules WHERE id = 2").fetchone()
print(f"    {row[0]} — lock: {row[1]}")

# ── 2. Rule 7 — lock: all → tcpa ─────────────────────────────
print("\n[2] Rule 7 — campaign_type_lock: all → tcpa...")
conn.execute(
    "UPDATE rules SET campaign_type_lock = 'tcpa', updated_at = ? WHERE id = 7",
    [now]
)
row = conn.execute("SELECT name, campaign_type_lock FROM rules WHERE id = 7").fetchone()
print(f"    {row[0]} — lock: {row[1]}")

# ── 3. Rule 12 — lock: all → max_clicks ──────────────────────
print("\n[3] Rule 12 — campaign_type_lock: all → max_clicks...")
conn.execute(
    "UPDATE rules SET campaign_type_lock = 'max_clicks', updated_at = ? WHERE id = 12",
    [now]
)
row = conn.execute("SELECT name, campaign_type_lock FROM rules WHERE id = 12").fetchone()
print(f"    {row[0]} — lock: {row[1]}")

# ── 4. Rule 21 — CPC threshold: £3 → £5 ──────────────────────
print("\n[4] Rule 21 — CPC threshold: £3 → £5...")
new_conditions_21 = json.dumps([
    {"metric": "cpc_avg_7d", "op": "gt", "value": "5", "ref": "absolute"},
    {"metric": "ctr_7d", "op": "lt", "value": "2", "ref": "pct"}
])
conn.execute(
    "UPDATE rules SET conditions = ?, updated_at = ? WHERE id = 21",
    [new_conditions_21, now]
)
row = conn.execute("SELECT name, conditions FROM rules WHERE id = 21").fetchone()
print(f"    {row[0]}")
print(f"    Conditions: {row[1]}")

# ── Final state check ─────────────────────────────────────────
print("\n" + "=" * 60)
print("FINAL STATE CHECK")
print("=" * 60)

print("\nCampaign type locks:")
rows = conn.execute(
    "SELECT id, name, campaign_type_lock FROM rules "
    "WHERE rule_or_flag = 'rule' AND is_template = FALSE "
    "ORDER BY id"
).fetchall()
for r in rows:
    print(f"  Rule {r[0]}: {r[1]} — lock: {r[2]}")

conn.close()
print("\n✅ Job 1B complete.")
