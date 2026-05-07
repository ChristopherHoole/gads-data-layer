"""Audit 3 WRDS [ex]: target risky 3-word exact match negs that could block real implant queries."""
import csv, re

SRC = r'C:\Users\User\Downloads\Negative keyword details report (9).csv'

with open(SRC, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()
hdr_idx = next(i for i, l in enumerate(lines[:10]) if l.startswith('keyword_text'))
reader = csv.DictReader(lines[hdr_idx:])
keywords = [r['keyword_text'].strip() for r in reader if r.get('keyword_text','').strip()]

keywords_sorted = sorted(keywords, key=lambda s: s.lower())
print(f"Total: {len(keywords_sorted)}")

# Page boundaries (600/page)
def page_of(term):
    try:
        idx = keywords_sorted.index(term)
        return (idx // 600) + 1
    except ValueError: return None

# Risky 3-word exact patterns (block direct implant intent or DBD's actual targets)
RISKY = []

# Pattern 1: any phrase that matches typical implant search queries
implant_intent_patterns = [
    r'^all on \d+$', r'^all on four$', r'^all on six$',
    r'^single tooth implant$', r'^single dental implant$', r'^one tooth implant$',
    r'^missing tooth implant$', r'^front tooth implant$', r'^molar tooth implant$',
    r'^tooth implant cost$', r'^tooth implants cost$', r'^dental implant cost$',
    r'^dental implants cost$', r'^dental implants price$', r'^dental implants prices$',
    r'^dental implants uk$', r'^dental implants london$', r'^dental implants near$',
    r'^best dental implants?$', r'^cheap dental implants?$', r'^affordable dental implants?$',
    r'^cheapest dental implants?$', r'^dental implant clinic$', r'^dental implant clinics$',
    r'^dental implant surgery$', r'^dental implant centre$', r'^dental implant center$',
    r'^dental implant practice$', r'^dental implant specialist$', r'^dental implant specialists$',
    r'^dental implant surgeon$', r'^dental implant surgeons$',
    r'^full mouth implant$', r'^full mouth implants$', r'^full arch implants?$',
    r'^full mouth dental$', r'^full mouth restoration$', r'^full mouth reconstruction$',
    r'^teeth in (a )?day$', r'^same day implant$', r'^same day implants$',
    r'^immediate dental implants?$', r'^immediate tooth implant$',
    r'^pay monthly implants?$', r'^pay monthly dental$', r'^dental implants finance$',
    r'^dental implant finance$', r'^implants on finance$', r'^dental implant payment$',
    r'^dental implants payment$',
    r'^tooth replacement options?$', r'^tooth replacement cost$', r'^teeth replacement cost$',
    r'^replace missing teeth$', r'^replace missing tooth$', r'^replace one tooth$',
    r'^missing tooth replacement$', r'^missing teeth replacement$',
    r'^dental implants reviews?$', r'^dental implant reviews?$',
    r'^how much implant$', r'^how much implants$',
    r'^cost dental implants?$', r'^cost dental implant$',
    r'^dental implants quote$', r'^dental implants today$',
    r'^dental implants required$', r'^dental implants available$',
]

for kw in keywords_sorted:
    for pattern in implant_intent_patterns:
        if re.match(pattern, kw.lower()):
            RISKY.append(kw)
            break

# Also flag specific keyword sub-patterns
extra_check = [
    'dental implants', 'all on 4', 'all on 6', 'single tooth', 'tooth replacement',
    'tooth implant', 'tooth implants', 'pay monthly', 'monthly implants',
]
for kw in keywords_sorted:
    if kw in RISKY: continue
    kwl = kw.lower()
    # Check if this 3-word exact would block direct implant queries
    # Specifically: contains "dental implants" / "all on 4" / etc. as core phrase
    for ec in extra_check:
        if ec in kwl:
            # Already in implant_intent? Skip duplicates
            RISKY.append(kw)
            break

# Dedupe
RISKY = sorted(set(RISKY), key=str.lower)
print(f"\n=== Risky 3-word exact negs ({len(RISKY)}) ===\n")

# Group by page
by_page = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[]}
for kw in RISKY:
    p = page_of(kw)
    if p: by_page[p].append(kw)

# Report
for p in [1,2,3,4,5]:
    items = by_page[p]
    if not items: continue
    print(f"\n========== PAGE {p} ({len(items)} flags) ==========")
    for kw in items: print(f"  {kw}")

# Show page boundaries clearly
print(f"\n\n=== Page boundaries ===")
for i in range(0, len(keywords_sorted), 600):
    chunk = keywords_sorted[i:i+600]
    print(f"Page {i//600+1}: {chunk[0]!r} ... {chunk[-1]!r}")
