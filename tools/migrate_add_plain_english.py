#!/usr/bin/env python3
"""
Chat 91: Migrate warehouse.duckdb rules table.
Adds plain_english TEXT column and populates all 24 rule rows.
Run from project root: python tools/migrate_add_plain_english.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / 'warehouse.duckdb'

PLAIN_ENGLISH = {
    "Increase Budget – Strong ROAS":
        "Spend more when ROAS is comfortably beating target with enough clicks to be confident",
    "Decrease Budget – Weak ROAS":
        "Pull back spend when ROAS is below target and there's enough data to be sure it's a real problem",
    "Emergency Budget Cut – Critical ROAS":
        "Cut budget hard if ROAS has collapsed to a point where every pound spent is a loss",
    "Pacing Reduction – Over Budget (tROAS)":
        "Trim budget if the campaign is on track to overshoot the monthly spend cap",
    "Pacing Increase – Under Budget (tROAS)":
        "Add budget if spend is tracking under cap and ROAS is strong enough to justify it",
    "Increase Budget – Strong CPA":
        "Spend more when CPA is well under target and conversions confirm the signal is real",
    "Decrease Budget – Weak CPA":
        "Pull back spend when CPA is above target and there are enough conversions to be certain",
    "Emergency Budget Cut – Critical CPA":
        "Cut budget hard if CPA has risen to a point where every conversion is unprofitable",
    "Pacing Reduction – Over Budget (tCPA)":
        "Trim budget if the campaign is on track to overshoot the monthly spend cap",
    "Pacing Increase – Under Budget (tCPA)":
        "Add budget if spend is tracking under cap and CPA is low enough to justify it",
    "Increase Budget – Strong CTR":
        "Spend more when CTR is strong and clicks are flowing — the traffic quality justifies it",
    "Decrease Budget – Weak CTR":
        "Pull back spend when CTR is weak and click volume is too low to be worth the cost",
    "Emergency Budget Cut – Very Low CTR":
        "Cut budget if CTR has dropped to a level that suggests something is fundamentally wrong",
    "Pacing Reduction – Over Budget (Max Clicks)":
        "Trim budget if the campaign is on track to overshoot the monthly spend cap",
    "Pacing Increase – Under Budget (Max Clicks)":
        "Add budget if spend is tracking under cap and click volume is healthy",
    "Tighten tROAS Target – Strong Performance":
        "Make the system work harder when ROAS has been beating target for a sustained period",
    "Loosen tROAS Target – Constrained Volume":
        "Give the system more room when ROAS has been missing target — trade efficiency for volume",
    "Tighten tCPA Target – Strong CPA":
        "Lower the CPA target to force more conservative bidding when leads are costing too much",
    "Loosen tCPA Target – Volume Constrained":
        "Raise the CPA target to free up volume when the system is too constrained to spend",
    "Increase Max CPC Cap – Low Impression Share":
        "Raise the CPC cap when it's being hit and impression share is suffering as a result",
    "Decrease Max CPC Cap – High CPC Low CTR":
        "Lower the CPC cap when clicks are expensive but CTR is too weak to justify the cost",
    "Pause – Poor ROAS":
        "Recommend pausing if ROAS has been critically low for two weeks and spend is high enough to be a real concern",
    "Pause – High CPA":
        "Recommend pausing if CPA is more than double target for two weeks and conversions confirm it's not noise",
    "Pause – High CPC":
        "Recommend pausing if CPC is more than double the threshold and click volume is too low to justify the cost",
}


def main():
    try:
        import duckdb
    except ImportError:
        print("ERROR: duckdb not installed. Run: pip install duckdb")
        sys.exit(1)

    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        sys.exit(1)

    print(f"Opening {DB_PATH}")
    conn = duckdb.connect(str(DB_PATH))

    try:
        # Check current columns
        cols = [r[0] for r in conn.execute("DESCRIBE rules").fetchall()]
        print(f"Existing columns: {cols}")

        # Add column if missing
        if 'plain_english' not in cols:
            print("Adding plain_english column...")
            conn.execute("ALTER TABLE rules ADD COLUMN plain_english TEXT")
            print("  ✓ Column added.")
        else:
            print("  Column plain_english already exists — updating values.")

        # Populate
        updated_total = 0
        not_found = []
        for name, text in PLAIN_ENGLISH.items():
            rows = conn.execute(
                "SELECT COUNT(*) FROM rules WHERE name = ?", [name]
            ).fetchone()[0]
            if rows == 0:
                not_found.append(name)
                continue
            conn.execute(
                "UPDATE rules SET plain_english = ? WHERE name = ?",
                [text, name]
            )
            updated_total += rows
            print(f"  ✓ {rows} row(s): {name!r}")

        # Commit (DuckDB auto-commits on close but explicit is cleaner)
        conn.commit()

        print(f"\n{'='*60}")
        print(f"Done. Updated {updated_total} rows.")
        if not_found:
            print(f"\nWARNING: {len(not_found)} name(s) not found in DB:")
            for n in not_found:
                print(f"  - {n!r}")

        # Verify
        total = conn.execute("SELECT COUNT(*) FROM rules WHERE plain_english IS NOT NULL").fetchone()[0]
        print(f"Rows with plain_english populated: {total}")

    finally:
        conn.close()


if __name__ == '__main__':
    main()
