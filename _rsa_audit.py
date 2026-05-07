"""Audit 04_RSAs.md for char-count + £25 deposit issues."""
import re
path = r'C:\Users\User\Desktop\gads-data-layer\potential_clients\Inserta Dental\Campaigns\Near Me - All Implants\04_RSAs.md'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Find all numbered list items in Headlines + Descriptions sections
issues = []
deposit_count = 0
overlong_h = 0
overlong_d = 0

current_ag = None
current_ad = None
mode = None  # 'h' or 'd'

for line in text.split('\n'):
    # Track ad group / ad
    m = re.match(r'^## AG (\d+)', line)
    if m: current_ag = m.group(1); continue
    m = re.match(r'^### Ad (\d+)', line)
    if m: current_ad = m.group(1); continue
    if 'Headlines' in line and '**' in line: mode = 'h'; continue
    if 'Descriptions' in line and '**' in line: mode = 'd'; continue
    if line.startswith('---'): mode = None; continue

    m = re.match(r'^\d+\.\s+(.+?)(\s+\*\(pin.*\))?$', line.strip())
    if m and mode:
        kw_text = m.group(1).strip()
        # Strip pin suffix
        kw_text = re.sub(r'\s*\*\(pin \d+\)\*\s*$', '', kw_text).strip()
        n = len(kw_text)
        limit = 30 if mode == 'h' else 90
        if '£25' in kw_text or '25 deposit' in kw_text.lower() or '£25 booking' in kw_text.lower() or '£25 refundable' in kw_text.lower():
            deposit_count += 1
            issues.append(f"  [DEPOSIT] AG{current_ag} Ad{current_ad} {mode}: {kw_text!r}")
        if n > limit:
            if mode == 'h': overlong_h += 1
            else: overlong_d += 1
            issues.append(f"  [LEN {n}>{limit}] AG{current_ag} Ad{current_ad} {mode}: {kw_text!r}")

print(f"=== AUDIT RESULTS ===")
print(f"  £25 deposit lines: {deposit_count}")
print(f"  overlong headlines (>30): {overlong_h}")
print(f"  overlong descriptions (>90): {overlong_d}")
print(f"  total issues: {len(issues)}")
print()
for i in issues[:60]:
    print(i)
