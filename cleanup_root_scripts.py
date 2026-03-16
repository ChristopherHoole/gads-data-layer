"""
Move diagnostic/fix scripts from repo root to scripts/ folder.
"""
import os
import shutil
from pathlib import Path

root = Path('.')
scripts_dir = Path('scripts')
scripts_dir.mkdir(exist_ok=True)

files_to_move = [
    'audit_rules.py',
    'audit_rules_full.py',
    'check_bid_strategy.py',
    'check_db_recs.py',
    'check_troas_cols.py',
    'clear_synthetic_recs.py',
    'job1_rules_fix.py',
    'job1b_rules_fix.py',
    'job1c_rules_fix.py',
    'job2_disable_proxy_flags.py',
    'job2_add_bid_strategy_col.py',
]

for filename in files_to_move:
    src = root / filename
    dst = scripts_dir / filename
    if src.exists():
        shutil.move(str(src), str(dst))
        print(f"  Moved: {filename} → scripts/")
    else:
        print(f"  Not found (skipping): {filename}")

print(f"\nscripts/ contents:")
for f in sorted(scripts_dir.iterdir()):
    print(f"  {f.name}")

print("\n✅ Done.")
