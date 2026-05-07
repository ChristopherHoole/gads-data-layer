"""Sort the 2 WRDS [ex] list alphabetically + find page boundaries (500/page).
Then map all removal candidates to their page."""
import csv

SRC = r'C:\Users\User\Downloads\Negative keyword details report (5).csv'

# Read all keywords
keywords = []
with open(SRC, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()
hdr_idx = next(i for i, l in enumerate(lines[:10]) if l.startswith('keyword_text'))
reader = csv.DictReader(lines[hdr_idx:])
for r in reader:
    txt = (r.get('keyword_text') or '').strip()
    if txt: keywords.append(txt)

# GAds UI sorts case-insensitively
keywords_sorted = sorted(keywords, key=lambda s: s.lower())
print(f"Total: {len(keywords_sorted)}")
print(f"Page 1 (1-500):    {keywords_sorted[0]!r} ... {keywords_sorted[499]!r}")
print(f"Page 2 (501-1000): {keywords_sorted[500]!r} ... {keywords_sorted[999]!r}")
print(f"Page 3 (1001+):    {keywords_sorted[1000]!r} ... {keywords_sorted[-1]!r}")
print()

# All my removal candidates (Pass 1 + Pass 4 likely-removes + denture/brand placeholders)
PASS1 = [
    "mouth implants","best implants","dental implantation","implant offers","total implants",
    "implant clinic","full implants","1 implant","implant uk","uk implants","implant london",
    "implant specialist","implant experts","getting implants","dentist implants","dentist implant",
    "implant dental","implants dental","implants dentist","double implant","arch implants",
    "missing teeth","missing tooth","replacement teeth","replace teeth","dental replacement",
    "tooth replacements","failing teeth",
]
PASS2_DENTURE = [
    "implant dentures","implant denture","denture implants","dentures implant",
    "implanted dentures","overdenture implant",
]
PASS3_BRANDS = [
    "osstem implant","osstem implants","swiss implant","swiss implants","bredent implants",
    "megagen implant","megagen implants","mis implant","medentika implant","neoss implant",
    "biohorizon implants","hiossen implant","neodent implants","ndi implant","ndi implants",
    "artisan implants","jax implants","tdc implants","mimi implants","21d implants",
    "oxi implant","ukmec implant","mini implants","zygomatic implants","zygomatic implant",
    "pterygoid implants","basal implants","screwless implants",
]
PASS4 = [
    "fake teeth","fake tooth","artificial tooth","teeth done","getting teeth","new tooth",
    "front teeth","front tooth","fixed tooth","fixing teeth","teeth fixing","teeth surgery",
    "tooth surgery","tooth restoration","teeth restoration","dental restoration","dental restorations",
    "tooth treatment","teeth treatment","tooth replacement","lose tooth","loose tooth",
    "fractured tooth","bad teeth","chipped teeth","dental finance","dentistry finance","dental loans",
    "dental abutment","tooth abutment","bone implant","gold implant","perio implant","implant types",
    "cheap implants","cheapest implants","affordable implants","implant cheap",
    "mobile implant","fail implant","veneers implants","implantation teeth",
]

# Find page for each
def page_of(term):
    try:
        idx = keywords_sorted.index(term)
        if idx < 500: return 1
        if idx < 1000: return 2
        return 3
    except ValueError:
        return None

groups = {1: {'p1':[],'p2':[],'p3':[],'p4':[]},
          2: {'p1':[],'p2':[],'p3':[],'p4':[]},
          3: {'p1':[],'p2':[],'p3':[],'p4':[]},
          'missing': []}

for t in PASS1:
    p = page_of(t)
    if p is None: groups['missing'].append(('PASS1', t))
    else: groups[p]['p1'].append(t)

for t in PASS2_DENTURE:
    p = page_of(t)
    if p is None: groups['missing'].append(('PASS2', t))
    else: groups[p]['p2'].append(t)

for t in PASS3_BRANDS:
    p = page_of(t)
    if p is None: groups['missing'].append(('PASS3', t))
    else: groups[p]['p3'].append(t)

for t in PASS4:
    p = page_of(t)
    if p is None: groups['missing'].append(('PASS4', t))
    else: groups[p]['p4'].append(t)

for page in [1,2,3]:
    print(f"\n========== PAGE {page} ==========")
    for label, key in [('PASS 1 — Definite remove','p1'),('PASS 2 — Denture-pending','p2'),('PASS 3 — Brand check','p3'),('PASS 4 — Borderline','p4')]:
        items = sorted(groups[page][key], key=str.lower)
        if not items: continue
        print(f"\n  {label}: ({len(items)})")
        for t in items: print(f"    {t}")

if groups['missing']:
    print(f"\n========== NOT IN LIST (already removed?) ==========")
    for pass_id, t in groups['missing']: print(f"  [{pass_id}] {t}")
