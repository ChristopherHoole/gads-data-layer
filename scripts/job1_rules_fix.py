"""
JOB 1 — DB Rules Cleanup
Master Chat 12 — Rules Strategic Review

Changes:
1. Delete Rule 56 (test duplicate)
2. Delete Rules 9 and 14 (redundant pacing reduction duplicates)
3. Update Rule 4 — add ROAS condition 2 + updated plain English
4. Update Rule 17 — fix action_type increase_troas -> decrease_troas
5. Update Rule 18 — fix action_type increase_troas -> decrease_target_cpa
6. Update all 30 flag plain_english values (currently all NULL)
"""

import duckdb
import json
from datetime import datetime

conn = duckdb.connect('warehouse.duckdb')
now = datetime.now()

print("=" * 60)
print("JOB 1 — DB Rules Cleanup")
print("=" * 60)

# ── 1. Delete Rule 56, 9, 14 ─────────────────────────────────
print("\n[1] Deleting rules 9, 14, 56...")
conn.execute("DELETE FROM rules WHERE id IN (9, 14, 56)")
count = conn.execute("SELECT COUNT(id) FROM rules WHERE id IN (9, 14, 56)").fetchone()[0]
print(f"    Done — remaining rows with those IDs: {count} (expected 0)")

# ── 2. Fix Rule 4 — add ROAS condition 2 ─────────────────────
print("\n[2] Updating Rule 4 — Pacing Reduction (add ROAS condition 2)...")
new_conditions_4 = json.dumps([
    {"metric": "pacing_vs_cap", "op": "gt", "value": "105", "ref": "pct"},
    {"metric": "roas_7d", "op": "lt", "value": "1.0", "ref": "x_target"}
])
new_plain_4 = "Trim budget if the campaign is on track to overshoot the monthly spend cap and performance does not justify the extra spend"
conn.execute(
    "UPDATE rules SET conditions = ?, plain_english = ?, updated_at = ? WHERE id = 4",
    [new_conditions_4, new_plain_4, now]
)
row = conn.execute("SELECT conditions, plain_english FROM rules WHERE id = 4").fetchone()
print(f"    Conditions: {row[0]}")
print(f"    Plain English: {row[1]}")

# ── 3. Fix Rule 17 — action_type ─────────────────────────────
print("\n[3] Updating Rule 17 — fix action_type to decrease_troas...")
conn.execute(
    "UPDATE rules SET action_type = 'decrease_troas', updated_at = ? WHERE id = 17",
    [now]
)
row = conn.execute("SELECT name, action_type FROM rules WHERE id = 17").fetchone()
print(f"    {row[0]} — action_type: {row[1]}")

# ── 4. Fix Rule 18 — action_type ─────────────────────────────
print("\n[4] Updating Rule 18 — fix action_type to decrease_target_cpa...")
conn.execute(
    "UPDATE rules SET action_type = 'decrease_target_cpa', updated_at = ? WHERE id = 18",
    [now]
)
row = conn.execute("SELECT name, action_type FROM rules WHERE id = 18").fetchone()
print(f"    {row[0]} — action_type: {row[1]}")

# ── 5. Update all 30 flag plain_english values ────────────────
print("\n[5] Updating flag plain_english values...")

flag_plain_english = {
    25: "ROAS has dropped more than 20% week on week — check budget, bid and landing pages",
    26: "ROAS has spiked more than 50% week on week — could be a real opportunity or an anomaly worth checking",
    27: "CPA has risen more than 30% week on week — check if competition or quality score is driving this",
    28: "CPA has improved more than 20% week on week — a good signal that bidding or quality is improving",
    29: "Click through rate is trending down more than 20% — ads may be losing relevance or competition has increased",
    30: "CTR has spiked more than 50% vs last week — ads may be gaining relevance or competition has dropped",
    31: "Conversion rate has dropped more than 20% week on week — check landing page and offer relevance",
    32: "Conversion rate has improved more than 50% week on week — landing page or offer resonance is improving",
    33: "Conversions have dropped more than 30% vs the previous week — check bids, quality and landing pages",
    34: "Conversions have spiked more than 50% vs the previous week — check if tracking is double counting",
    35: "Spend has dropped more than 30% vs the previous week — check if ads are being limited",
    36: "Spend has risen more than 50% above the campaign normal level — review before it hits the cap",
    37: "Impression share has dropped more than 20% week on week — check budget, bid and quality score",
    38: "Impression share has risen more than 30% week on week — the campaign is gaining more auction coverage",
    39: "Campaign recorded no impressions today — could be a budget, targeting, approval or billing issue",
    40: "Average CPC has risen more than 40% week on week — review bids and auction competition",
    41: "Spend has risen to a statistically abnormal level — review immediately before budget is exhausted",
    42: "Spend has dropped to an anomalous level — check if ads are serving normally",
    43: "Click volume spike detected — check for invalid clicks or unusual traffic",
    44: "Click volume drop detected — ads may have stopped serving or you have lost traffic",
    45: "Impression volume spike detected — check for anomalous traffic patterns",
    46: "Impression volume drop detected — ads may have limited reach",
    47: "Conversions are at zero — check tracking, bids and landing page performance",
    48: "Conversions dropped to zero after previously recording — very likely a broken tracking tag",
    49: "One or more landing pages may be returning an error — ads may be running to a broken destination",
    50: "Landing page is loading slowly — this will hurt Quality Score and conversion rate",
    51: "One or more ads have been disapproved — impressions may be limited",
    52: "Daily budget was fully spent before the end of the day — the campaign is missing evening traffic",
    53: "A billing issue has been detected — campaigns may stop running",
    54: "Tracking tag is missing from the landing page — conversion data will not be recorded",
}

for flag_id, plain in flag_plain_english.items():
    conn.execute(
        "UPDATE rules SET plain_english = ?, updated_at = ? WHERE id = ?",
        [plain, now, flag_id]
    )

null_count = conn.execute(
    "SELECT COUNT(id) FROM rules WHERE rule_or_flag = 'flag' AND plain_english IS NULL"
).fetchone()[0]
print(f"    Done — flags with NULL plain_english remaining: {null_count} (expected 0)")

# ── Final state check ─────────────────────────────────────────
print("\n" + "=" * 60)
print("FINAL STATE CHECK")
print("=" * 60)

print("\nRules count by action_type:")
rows = conn.execute(
    "SELECT action_type, COUNT(id) FROM rules WHERE rule_or_flag = 'rule' AND is_template = FALSE GROUP BY action_type ORDER BY action_type"
).fetchall()
for r in rows:
    print(f"  {r[0]}: {r[1]}")

print("\nTotal rules:", conn.execute(
    "SELECT COUNT(id) FROM rules WHERE rule_or_flag = 'rule' AND is_template = FALSE"
).fetchone()[0])
print("Total flags:", conn.execute(
    "SELECT COUNT(id) FROM rules WHERE rule_or_flag = 'flag' AND is_template = FALSE"
).fetchone()[0])

conn.close()
print("\n✅ Job 1 complete.")
