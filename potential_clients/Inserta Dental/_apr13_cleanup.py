import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('_apr13_blocks.txt','r',encoding='utf-8') as f:
    c = f.read().replace('\r','')

# Terms to REMOVE from blocks - these are actually potential DBD clients
remove = set([
    # Generic London buying intent - DBD IS a London dental clinic
    'london dental clinic','london dental implant','london dental smile',
    'london dental specialists','dental clinic london','dental excellence london',
    'dental centre uk','dental clinics uk','uk dental clinic','uk dental services',
    # DBD's own area
    'dental care hammersmith','dentist hammersmith road','kings dental clinic hammersmith',
    'nhs dentists in hammersmith',
    # Generic buying intent
    'best dental clinic london','best dental surgery london','dental clinic in london',
    'dental care near me','dental clinic near me','dental surgery near me',
    'implant clinic near me','cosmetic dental clinic near me','dental clinic dentist near me',
    'dental design studio near me','dental implant centre near me','elite dental care near me',
    'orodental clinic near me','the best dental clinic in london',
    'made in london dental','premium smile dental clinic london',
    'best dentures in uk','sd swiss dental solutions',
])

sections = re.split(r'### (\S+) \(\d+\) ###', c)
cats = {}
for i in range(1, len(sections)-1, 2):
    cat = sections[i]
    terms = re.findall(r'\[([^\]]+)\]', sections[i+1])
    # Filter out removals
    cats[cat] = [t for t in terms if t not in remove]

for cat in ['1_word','2_word','3_word','4_word','5plus_word']:
    print(f"\n### {cat} ({len(cats[cat])}) ###")
    for t in cats[cat]:
        print(f"[{t}]")

total = sum(len(cats[c]) for c in cats)
print(f"\n\nTOTAL: {total}")
