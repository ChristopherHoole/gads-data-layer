import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('_batch5_out.txt','r',encoding='utf-8') as f:
    c = f.read()

sections = re.split(r'=== (\w+): .+? ===', c)
cats = {}
for i in range(1, len(sections)-1, 2):
    cat = sections[i]
    body = sections[i+1]
    if cat == 'KEEP': continue
    terms = re.findall(r'\[([^\]]+)\]', body)
    cats[cat] = terms

manual = {
    'COMPETITOR': [
        'chelsea house dental','bamboo dental prices','coco dental london',
        'magyar fogorvos london','smile dental harrow','dental east london',
        'dentafly london clinic','tooth clinic london','new malden dental',
        'nuvia teeth implants','dream smile lewisham','tooth club romford',
        'smile dentist wanstead','gentle dental london','gentle dental molesey',
        'halo dental prices','denta clinic reviews','alma smiles hammersmith',
        'royal wharf dental','smile well clinic','putney hill dental',
        'keppel advanced dentistry','aura dental london','figges marsh dental',
        'nur smiles northwood','canon house clinic','new river dental',
        'chalton street dental','silicon dental perivale','finn dental specialists',
        'the mindful dentist','the complete smile','the wimbledon dentist',
        'crossways dental coulsdon','precision dental oldham','almas dental acton',
        'white dentist chiswick','bryer wallace belgravia',
        'kinston dental implants','dental estetik center','private dentist romford',
    ],
    'NAMED_DR': [
        'marshall hanson dentistry','david neal dental','goossens and odendaal',
        'dentist roman barking',
    ],
    'WRONG_UK': [
        'dentist chelmer village','dental implants broxbourne','dental implants buxton',
        'dental implants rickmansworth','dental implants pembrokeshire',
        'dental implants scarborough','dental implants wirral','private dentist wirral',
        'private dentist rawtenstall','dentist bishops stortford','private dentist whitehaven',
        'dental implants bridgwater',
    ],
    'ABROAD': [
        'dental implants bali','dental implant greece','dental treatment holiday',
        'impianto dentaire prix','implanturi dentare pret','implant dentar pret',
        'implant zeba koszt','mayo clinic teeth','dentist in johannesburg',
    ],
    'DENTURE': [
        'cover rotten teeth','gold implants teeth','gold tooth replacement',
        'permanent silver teeth','permanent silver tooth','silicone dental implants',
        'set of teeth','teeth set cost','missing tooth retainer','single tooth partial',
        'permanent gold teeth',
    ],
    'NON_DBD': [
        'dental ozone therapy','northwood hills orthodontist','bioclear near me',
        'youtube dental implants','dental insurance cosmetic','dental insurance london',
        'cosmetic dental insurance','teeth insurance uk','teeth implant insurance',
        'dental check up','endodontic treatment cost','gum transplant uk',
        'teeth straightening surgery','teeth surgery prices','zygomatic arch implant',
    ],
    'BRAND_RESEARCH': [
        'camlog implant price','mono implant price','emax crowns uk',
        'titanium dental implant','hybrid teeth implants','mini teeth implants',
        'zygomatic implants uk',
    ],
    'CHEAP_NHS': [
        'private dental plans','private dental insurance','dental plan uk','full dental plan',
    ]
}

for cat, items in manual.items():
    if cat not in cats: cats[cat] = []
    for item in items:
        if item not in cats[cat]:
            cats[cat].append(item)

for cat in ['COMPETITOR','NAMED_DR','ABROAD','WRONG_UK','DENTURE','CHEAP_NHS','NON_DBD','BRAND_RESEARCH']:
    print(f"\n### {cat} ({len(cats[cat])}) ###")
    for t in cats[cat]:
        print(f"[{t}]")

total = sum(len(cats[c]) for c in cats)
print(f"\n\nTOTAL: {total}")
