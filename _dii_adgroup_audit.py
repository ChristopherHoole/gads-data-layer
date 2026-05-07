"""Audit DII ad-group level assets:
- Group by Added by + Asset type + Status
- Show CPA totals
- Identify what google AI is generating
"""
import csv
from collections import defaultdict

SRC = r'C:\Users\User\Downloads\Asset association report (6).csv'

with open(SRC, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()

# Find header
hdr_idx = next(i for i, l in enumerate(lines[:10]) if l.startswith('Asset status,'))
reader = csv.DictReader(lines[hdr_idx:])

def num(v):
    if not v: return 0.0
    s = str(v).replace(',','').replace('£','').replace('--','0').strip()
    if s in ('','-','–'): return 0.0
    try: return float(s)
    except: return 0.0

rows = []
for r in reader:
    rows.append({
        'asset': (r.get('Asset') or '').strip()[:60],
        'type': r.get('Asset type') or '',
        'level': r.get('Level') or '',
        'status': r.get('Status') or '',
        'addedby': r.get('Added by') or '',
        'cost': num(r.get('Cost')),
        'imps': num(r.get('Impr.')),
        'clicks': num(r.get('Clicks')),
        'conv': num(r.get('Conversions')),
        'item_id': r.get('Item ID') or '',
    })

print(f"Total rows: {len(rows)}\n")

# Filter ad-group only
ag_rows = [r for r in rows if r['level'].lower() == 'ad group']
print(f"Ad-group level rows: {len(ag_rows)}")

# Group by Added by
print(f"\n=== Ad group rows by Added by ===")
by_addedby = defaultdict(lambda: {'n':0,'cost':0,'conv':0})
for r in ag_rows:
    k = r['addedby']
    by_addedby[k]['n'] += 1
    by_addedby[k]['cost'] += r['cost']
    by_addedby[k]['conv'] += r['conv']
for k, v in by_addedby.items():
    cpa = v['cost']/v['conv'] if v['conv']>0 else 0
    print(f"  {k:15s}  rows={v['n']:>3}  cost=£{v['cost']:>9.2f}  conv={v['conv']:>6.1f}  cpa=£{cpa:>7.2f}")

# By Asset type within Ad group
print(f"\n=== Ad group rows by Asset type ===")
by_type = defaultdict(lambda: {'n':0,'cost':0,'conv':0,'addedby':set()})
for r in ag_rows:
    k = r['type']
    by_type[k]['n'] += 1
    by_type[k]['cost'] += r['cost']
    by_type[k]['conv'] += r['conv']
    by_type[k]['addedby'].add(r['addedby'])
for k, v in sorted(by_type.items(), key=lambda x: -x[1]['cost']):
    cpa = v['cost']/v['conv'] if v['conv']>0 else 0
    print(f"  {k:25s}  rows={v['n']:>3}  cost=£{v['cost']:>9.2f}  conv={v['conv']:>6.1f}  cpa=£{cpa:>7.2f}  addedby={v['addedby']}")

# Status breakdown for ad group
print(f"\n=== Ad group rows by Status ===")
by_status = defaultdict(lambda: {'n':0,'cost':0,'conv':0})
for r in ag_rows:
    k = r['status']
    by_status[k]['n'] += 1
    by_status[k]['cost'] += r['cost']
    by_status[k]['conv'] += r['conv']
for k, v in by_status.items():
    cpa = v['cost']/v['conv'] if v['conv']>0 else 0
    print(f"  {k:25s}  rows={v['n']:>3}  cost=£{v['cost']:>9.2f}  conv={v['conv']:>6.1f}  cpa=£{cpa:>7.2f}")

# Google AI sitelinks specifically — these are the duplicates
print(f"\n=== Google AI sitelinks at ad-group level (top 20 by spend) ===")
ai_sitelinks = [r for r in ag_rows if 'sitelink' in r['type'].lower() and r['addedby']=='Google AI']
ai_sitelinks.sort(key=lambda x: -x['cost'])
for r in ai_sitelinks[:20]:
    cpa = r['cost']/r['conv'] if r['conv']>0 else 0
    print(f"  {r['asset']:50s}  £{r['cost']:>8.2f}  conv={r['conv']:>5.1f}  CPA=£{cpa:>7.2f}  {r['status']}")

# All ad-group AI sitelinks total
total_ai_sitelink_cost = sum(r['cost'] for r in ai_sitelinks)
total_ai_sitelink_conv = sum(r['conv'] for r in ai_sitelinks)
total_ai_sitelink_cpa = total_ai_sitelink_cost/total_ai_sitelink_conv if total_ai_sitelink_conv>0 else 0
print(f"\nTotal AI ad-group sitelinks: {len(ai_sitelinks)} rows / £{total_ai_sitelink_cost:.2f} / {total_ai_sitelink_conv:.1f} conv / £{total_ai_sitelink_cpa:.2f} CPA")
