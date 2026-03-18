"""
Fix broken conditions on rules 19 and 20.

Rules 19 and 20 were created via the flow builder but their condition
operators (op) and reference types (ref) were saved as None. The engine's
_evaluate() receives operator=None and returns False, so these rules never fire.

This script:
1. Reads current conditions for rules 19 and 20 and prints them
2. Updates conditions JSON with correct op and ref values
3. Prints updated conditions to confirm

Run from: gads-data-layer root directory.
"""

import json
import duckdb

DB_PATH = "warehouse.duckdb"

CORRECT_CONDITIONS = {
    19: [
        {
            "metric": "cpa_14d",
            "op": "gte",
            "value": 1.05,
            "ref": "x_target",
        },
        {
            "metric": "impression_share_lost_rank",
            "op": "gt",
            "value": 20,
            "ref": "pct",
        },
    ],
    20: [
        {
            "metric": "impression_share_lost_rank",
            "op": "gt",
            "value": 30,
            "ref": "pct",
        },
        {
            "metric": "clicks_7d",
            "op": "gte",
            "value": 20,
            "ref": "absolute",
        },
    ],
}


def print_conditions(label, rule_id, rule_name, conditions):
    print(f"\n  Rule {rule_id} — {rule_name}:")
    for i, c in enumerate(conditions, 1):
        print(
            f"    condition {i}: metric={c.get('metric')}  "
            f"op={c.get('op')}  value={c.get('value')}  ref={c.get('ref')}"
        )


def main():
    print("=" * 70)
    print("FIX RULES 19 & 20 CONDITIONS — warehouse.duckdb")
    print("=" * 70)

    conn = duckdb.connect(DB_PATH)

    # ── Step 1: read current state ──────────────────────────────────────────
    print("\n[1/3] Current conditions (before fix):")
    rows = conn.execute(
        "SELECT id, name, conditions FROM rules WHERE id IN (19, 20) ORDER BY id"
    ).fetchall()

    if not rows:
        print("  ERROR: No rows found for rule ids 19 and 20 — aborting.")
        conn.close()
        return

    for row in rows:
        rule_id, rule_name, conds_raw = row
        try:
            conditions = json.loads(conds_raw) if isinstance(conds_raw, str) else (conds_raw or [])
        except Exception as e:
            print(f"  ERROR parsing conditions for rule {rule_id}: {e}")
            continue
        print_conditions("BEFORE", rule_id, rule_name, conditions)

    # ── Step 2: apply correct conditions ────────────────────────────────────
    print("\n[2/3] Applying correct conditions...")
    for rule_id, correct_conds in CORRECT_CONDITIONS.items():
        new_json = json.dumps(correct_conds)
        conn.execute(
            "UPDATE rules SET conditions = ? WHERE id = ?",
            [new_json, rule_id],
        )
        print(f"  Updated rule {rule_id}")

    # ── Step 3: read back and confirm ────────────────────────────────────────
    print("\n[3/3] Updated conditions (after fix):")
    rows = conn.execute(
        "SELECT id, name, conditions FROM rules WHERE id IN (19, 20) ORDER BY id"
    ).fetchall()

    all_ok = True
    for row in rows:
        rule_id, rule_name, conds_raw = row
        try:
            conditions = json.loads(conds_raw) if isinstance(conds_raw, str) else (conds_raw or [])
        except Exception as e:
            print(f"  ERROR parsing updated conditions for rule {rule_id}: {e}")
            all_ok = False
            continue
        print_conditions("AFTER", rule_id, rule_name, conditions)

        # Validate ops are no longer None
        for c in conditions:
            if c.get("op") is None:
                print(f"  WARNING: op is still None in rule {rule_id}!")
                all_ok = False
            if c.get("ref") is None:
                print(f"  WARNING: ref is still None in rule {rule_id}!")
                all_ok = False

    conn.close()

    print()
    if all_ok:
        print("SUCCESS: Rules 19 and 20 conditions fixed.")
    else:
        print("WARNING: Some conditions may still have None values — check output above.")
    print("=" * 70)


if __name__ == "__main__":
    main()
