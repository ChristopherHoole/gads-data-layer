"""Extract all near-me / close-to-me / nearby / local / in-my-area variants
from the PMax search terms CSV. Output: markdown table sorted by spend desc.
"""
import csv, re, os

SRC = r'C:\Users\User\Downloads\Search terms report (5).csv'
OUT = r'C:\Users\User\Desktop\gads-data-layer\potential_clients\Inserta Dental\Campaigns\Near Me - All Implants\06_pmax_near_me_terms.md'

NEAR_RE = re.compile(
    r'\bnear me\b|\bnear my\b|\bnearby\b|\bnearest\b|'
    r'\bclose to me\b|\bclose by\b|\bclosest\b|'
    r'\bin my area\b|\baround me\b|\baround here\b|'
    r'\blocal\b|\blocally\b|\bnear by\b',
    re.I
)

def num(v):
    if not v: return 0.0
    s = str(v).replace(',','').replace('£','').replace('--','0').strip()
    if s in ('','-','–'): return 0.0
    try: return float(s)
    except: return 0.0

with open(SRC, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()

# Find header row
header_idx = None
for i, line in enumerate(lines[:10]):
    if line.startswith('Search term,') or 'Search term,Match type' in line:
        header_idx = i
        break
if header_idx is None:
    print("Header not found")
    exit(1)

reader = csv.DictReader(lines[header_idx:])
cols = reader.fieldnames

# Find columns
def find(keys):
    for k in keys:
        for c in cols:
            if c and k.lower() in c.lower():
                return c
    return None

c_term = find(['search term'])
c_camp = find(['campaign'])
c_cost = find(['cost'])
c_clicks = find(['clicks'])
c_imps = find(['impr'])
c_conv = find(['conversion'])

print(f"term={c_term} cost={c_cost} camp={c_camp}")

rows = []
total_rows = 0
total_pmax = 0
for r in reader:
    term = (r.get(c_term) or '').strip()
    if not term or term.lower().startswith('total'): continue
    total_rows += 1
    # File is PMax-only by default (Match type column = "Performance Max")
    total_pmax += 1
    if not NEAR_RE.search(term): continue
    rows.append({
        'term': term,
        'cost': num(r.get(c_cost)),
        'clicks': num(r.get(c_clicks)),
        'imps': num(r.get(c_imps)),
        'conv': num(r.get(c_conv)),
    })

print(f"total rows: {total_rows}, pmax rows: {total_pmax}, near-me pmax: {len(rows)}")

# Dedupe by term, summing
agg = {}
for r in rows:
    k = r['term'].lower()
    if k not in agg:
        agg[k] = {'term': r['term'], 'cost':0,'clicks':0,'imps':0,'conv':0}
    agg[k]['cost']   += r['cost']
    agg[k]['clicks'] += r['clicks']
    agg[k]['imps']   += r['imps']
    agg[k]['conv']   += r['conv']

# Sort by cost desc
sorted_terms = sorted(agg.values(), key=lambda x: -x['cost'])

total_cost = sum(t['cost'] for t in sorted_terms)
total_clicks = sum(t['clicks'] for t in sorted_terms)
total_imps = sum(t['imps'] for t in sorted_terms)
total_conv = sum(t['conv'] for t in sorted_terms)

# Write markdown
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(f"# PMax Near-Me Search Terms — April 2026\n\n")
    f.write(f"**Source:** `Search terms report (5).csv`\n")
    f.write(f"**Filter:** PMax campaign only, terms matching near me / close to me / nearby / local / in my area / closest / nearest\n")
    f.write(f"**Sorted by:** spend descending\n\n")
    f.write(f"## Totals\n\n")
    f.write(f"- **Unique terms:** {len(sorted_terms)}\n")
    f.write(f"- **Total spend:** £{total_cost:.2f}\n")
    f.write(f"- **Total clicks:** {int(total_clicks)}\n")
    f.write(f"- **Total impressions:** {int(total_imps)}\n")
    f.write(f"- **Total conversions:** {total_conv:.1f}\n\n")
    f.write(f"## Search terms\n\n")
    f.write(f"| # | Search term | Cost | Clicks | Impr. | Conv. |\n")
    f.write(f"|---|---|---:|---:|---:|---:|\n")
    for i, r in enumerate(sorted_terms, 1):
        f.write(f"| {i} | {r['term']} | £{r['cost']:.2f} | {int(r['clicks'])} | {int(r['imps'])} | {r['conv']:.1f} |\n")

print(f"Wrote {OUT}")
print(f"Total spend on near-me PMax terms: £{total_cost:.2f}")
print(f"Top 10 by spend:")
for r in sorted_terms[:10]:
    print(f"  £{r['cost']:>8.2f}  {r['term']}")
