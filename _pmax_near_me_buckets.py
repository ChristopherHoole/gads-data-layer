"""Bucket the 740 PMax near-me terms by ad-group intent. Surface anything
that doesn't fit one of the 7 existing buckets — those are the candidates
for new ad groups OR missed keyword variants in existing ad groups.
"""
import csv, re, os
from collections import defaultdict

SRC = r'C:\Users\User\Downloads\Search terms report (5).csv'
OUT = r'C:\Users\User\Desktop\gads-data-layer\potential_clients\Inserta Dental\Campaigns\Near Me - All Implants\07_pmax_near_me_bucketed.md'

NEAR_RE = re.compile(
    r'\bnear me\b|\bnear my\b|\bnearby\b|\bnearest\b|'
    r'\bclose to me\b|\bclose by\b|\bclosest\b|'
    r'\bin my area\b|\baround me\b|\baround here\b|'
    r'\blocal\b|\blocally\b|\bnear by\b',
    re.I
)

# Bucket rules — order matters, FIRST MATCH WINS, so put specific before broad
BUCKETS = [
    ('AG2 — Full Mouth Implants Near Me', [
        'full mouth', 'full arch', 'full dental', 'full set', 'all on 4',
        'all on four', 'all-on-4', 'all on six', 'whole mouth', 'replace all',
        'reconstruction', 'restoration', 'complete mouth', 'all-on-6'
    ]),
    ('AG3 — Same Day Implants Near Me', [
        'same day', 'one day', 'immediate', '24 hour', 'same-day', 'one-day',
        'teeth in a day', 'in one day'
    ]),
    ('AG5 — Pay Monthly / Finance Near Me', [
        'pay monthly', 'finance', 'payment plan', '0%', 'monthly payment',
        'on finance', 'spread the cost', 'instalment', 'installment',
        'dentist with payment'
    ]),
    ('AG6 — Teeth Fixing Near Me', [
        'teeth fixing', 'fix my teeth', 'fix teeth', 'fix my smile',
        'fixed teeth', 'teeth fixed', 'get my teeth'
    ]),
    ('AG4 — Single Tooth / Tooth Replacement Near Me', [
        'single tooth', 'one tooth', 'tooth replacement', 'replace a tooth',
        'replace one tooth', 'missing tooth', 'molar implant', 'front tooth',
        'tooth implant', '1 tooth'
    ]),
    ('AG1 — Dental Implant Clinic Near Me', [
        'implant clinic', 'implant centre', 'implant center', 'implant practice',
        'implant dentist', 'implant specialist', 'implant surgeon',
        'implant practitioner', 'implants clinic', 'implants centre'
    ]),
]

CATCHALL_TOKENS = [
    'dental implants near me', 'dental implant near me', 'implants near me',
    'tooth implants near me', 'teeth implants near me', 'dental implants nearby',
    'dental implants close to me', 'dental implants closest to me',
    'local dental implants', 'dental implants local', 'dental implants in my area',
    'affordable dental implants', 'best dental implants', 'cheap dental implants',
    'dental implants cost', 'dental implant prices', 'dental implants uk',
    'dental implant in my area', 'implant in my area', 'implants in my area',
    'implant near me', 'implant nearby', 'implants nearby', 'best implants',
    'cheap implants', 'affordable implants', 'implants close to me',
    'implants closest to me'
]

def num(v):
    if not v: return 0.0
    s = str(v).replace(',','').replace('£','').replace('--','0').strip()
    if s in ('','-','–'): return 0.0
    try: return float(s)
    except: return 0.0

def bucket_of(term):
    t = term.lower()
    for name, tokens in BUCKETS:
        if any(tok in t for tok in tokens):
            return name
    if any(tok in t for tok in CATCHALL_TOKENS):
        return 'AG7 — Catchall Dental Implants Near Me'
    # Specifically the bare "implants near me" / "dental implants near me" type
    if re.search(r'\bdental implants?\b', t) or re.search(r'\bimplants?\b', t):
        return 'AG7 — Catchall Dental Implants Near Me'
    return 'UNCLASSIFIED — review for new ad group / missing keyword'

# Read CSV
with open(SRC, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()
header_idx = next(i for i,l in enumerate(lines[:10]) if l.startswith('Search term,'))
reader = csv.DictReader(lines[header_idx:])

# Aggregate near-me terms only
agg = {}
for r in reader:
    term = (r.get('Search term') or '').strip()
    if not term or term.lower().startswith('total'): continue
    if not NEAR_RE.search(term): continue
    k = term.lower()
    if k not in agg:
        agg[k] = {'term':term,'cost':0,'clicks':0,'imps':0,'conv':0}
    agg[k]['cost']   += num(r.get('Cost'))
    agg[k]['clicks'] += num(r.get('Clicks'))
    agg[k]['imps']   += num(r.get('Impr.'))
    agg[k]['conv']   += num(r.get('Conversions'))

# Bucket
buckets = defaultdict(list)
for v in agg.values():
    b = bucket_of(v['term'])
    buckets[b].append(v)

# Report order
order = [
    'AG1 — Dental Implant Clinic Near Me',
    'AG2 — Full Mouth Implants Near Me',
    'AG3 — Same Day Implants Near Me',
    'AG4 — Single Tooth / Tooth Replacement Near Me',
    'AG5 — Pay Monthly / Finance Near Me',
    'AG6 — Teeth Fixing Near Me',
    'AG7 — Catchall Dental Implants Near Me',
    'UNCLASSIFIED — review for new ad group / missing keyword',
]

with open(OUT, 'w', encoding='utf-8') as f:
    f.write("# PMax Near-Me Terms — bucketed against new campaign ad groups\n\n")
    f.write("**Source:** `Search terms report (5).csv` (April 2026)\n")
    f.write(f"**Total unique near-me terms:** {len(agg)}\n\n")

    # Summary table
    total_cost = sum(v['cost'] for v in agg.values())
    f.write("## Bucket summary\n\n")
    f.write("| Bucket | Unique terms | Spend | Clicks | Conv. |\n")
    f.write("|---|---:|---:|---:|---:|\n")
    for b in order:
        rows = buckets.get(b, [])
        if not rows: continue
        bcost = sum(r['cost'] for r in rows)
        bclicks = sum(r['clicks'] for r in rows)
        bconv = sum(r['conv'] for r in rows)
        f.write(f"| {b} | {len(rows)} | £{bcost:.2f} | {int(bclicks)} | {bconv:.1f} |\n")
    f.write(f"| **TOTAL** | **{len(agg)}** | **£{total_cost:.2f}** | | |\n\n")

    # Detail per bucket
    for b in order:
        rows = buckets.get(b, [])
        if not rows: continue
        rows = sorted(rows, key=lambda x: -x['cost'])
        bcost = sum(r['cost'] for r in rows)
        f.write(f"\n## {b}\n\n")
        f.write(f"**{len(rows)} terms · £{bcost:.2f} spend**\n\n")
        f.write(f"| # | Search term | Cost | Clicks | Impr. | Conv. |\n")
        f.write(f"|---|---|---:|---:|---:|---:|\n")
        for i, r in enumerate(rows, 1):
            f.write(f"| {i} | {r['term']} | £{r['cost']:.2f} | {int(r['clicks'])} | {int(r['imps'])} | {r['conv']:.1f} |\n")

print(f"Wrote {OUT}")
print(f"\nBucket breakdown:")
for b in order:
    rows = buckets.get(b, [])
    if not rows: continue
    bcost = sum(r['cost'] for r in rows)
    print(f"  {b:60s} {len(rows):>4} terms  £{bcost:>9.2f}")
