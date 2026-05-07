"""Audit 5+ WRDS [ex]: high-intent queries blocking real implant traffic."""
import csv, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

src = r'C:\Users\User\Downloads\Negative keyword details report (12).csv'
with open(src, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()
hdr = next(i for i, l in enumerate(lines[:10]) if l.startswith('keyword_text'))
reader = csv.DictReader(lines[hdr:])
kws = [r['keyword_text'].strip() for r in reader if r.get('keyword_text', '').strip()]
sorted_kws = sorted(kws, key=lambda s: s.lower())
print(f'Total: {len(sorted_kws)}')
PAGE = 500
for i in range(0, len(sorted_kws), PAGE):
    chunk = sorted_kws[i:i+PAGE]
    print(f'Page {i//PAGE+1}: {chunk[0]!r} ... {chunk[-1]!r} ({len(chunk)})')

DEFINITE = [
    # Cheapest/finance (DBD does monthly payments, finance customers are target)
    'cheapest place for dental implants uk', 'cheapest dental implants northern ireland',
    'cheapest place to get tooth implants', 'cheapest dental implants near me',
    'cheap dental implants in england', 'where can i get cheap implants',
    'cheap options for missing teeth uk', 'cheap options for missing teeth',
    'cheap dental clinic near me', 'cheapest dental implants in uk',
    'cheap alternative to dental implants', 'cheap dental implants full mouth',
    'cheapest place to get dental implants', 'low cost dental implants uk',
    'cheapest full mouth dental implants uk', 'cheapest crowns for teeth near me',
    'dental implants in london cheapest', 'cheapest way to get new teeth',
    'cheapest dental clinic near me', 'cheap dentist near me prices',
    'budget friendly dentist near me', 'affordable dental clinic near me',
    'whats the cheapest way to get dental implants',

    # Generic best/specialist queries
    'how expensive are dental implants', 'how expensive is a dental implant',
    'dentist that specializes in implants', 'best place for dental implants',
    'best place for dental implants uk', 'best place to get tooth implants',
    'best place to get full mouth dental implants', 'best material for dental implants',
    'what is the best material for dental implants',

    # DBD has free consultation
    'free implant consultation near me', 'free dental consultation near me',
    'free dental appointment near me', 'free dentist consultation near me',

    # Procedure cost queries
    'cost of 2 dental implants with bone grafting uk',
    'how much does it cost for 2 dental implants',
    'tooth removal and implant cost', 'tooth implant bone graft cost',
    'dental bone graft cost uk', 'full mouth bone grafting cost',

    # Whole-mouth replacement (high intent)
    'all teeth replaced with implants', 'replacing all teeth with implants cost',
    'can you replace all your teeth with implants', 'can you have all your teeth replaced',
    'can you get all your teeth replaced',

    # Missing teeth options (high intent prospects)
    'dental implants for older adults', 'how to fix missing teeth without implants',
    'what can be done for missing teeth', 'what can you do to replace missing teeth',
    'what can replace an extracted tooth', 'what is the cheapest tooth replacement',
    'options for a missing tooth', 'options for missing teeth uk',
    'what are some options for missing teeth',
    'i have bad teeth what are my options',
    'i have really bad teeth what are my options uk',
    'i need help with dental costs',
    'temporary tooth for missing tooth',
    'how much is it to replace a tooth',

    # Geo (DBD-relevant)
    'dental implant kingston upon thames',
    'all on 4 dental implants kent',

    # Procedure / timeline questions (high-intent research stage that converts)
    'how long does dental implants take', 'how long do teeth implants take',
    'how long do dental implants take', 'how long dental implant last',
    'how long does it take to get teeth implants',
    'how long do dental implants take to put in',
    'how long does it take for implants',
    'how long do dental implants last',
    'how long is a tooth implant procedure',
    'how long is a tooth implant process',
    'how long after tooth extraction can i get implant',
    'how soon after extraction can you get an implant',
    'how soon can you have a dental implant after extraction',
    'best time to get implant after tooth extraction',
    'how long does a dental implant take to complete',
    'recovery time for dental implant surgery',
    'what to expect after dental implant surgery',
    'how bad is dental implant surgery',

    # Implant process research
    'dental implants how does it work',
    'patient selection for dental implants',
    'who is not suitable for dental implants',
    'components of a dental implant',
    'what is the warranty on dental implants',
    'is permanent tooth implant safe',
    'is dental implant painful process',
    'is getting a dental implant painful',
    'can implants be done in one day',
    'can you get implants in one day',
    'can a dental implant be done in one day',
    'teeth implants in 24 hours',

    # Finance
    'dental implants no credit check',
    'no credit check dental payment plans uk',

    # Single tooth implant
    'can i get one tooth implant',
    'can one tooth be replaced',
    'what replaces a missing tooth',
    'how to fill gap from missing tooth',

    # Bone loss / sinus lift (clinical but high intent — DBD does these)
    'sinus lift procedure for dental implants',
    'sinus lift and bone graft',
    'do all implants require bone grafts',
    'bone loss after implant placement',
    'severe bone loss and dental implants',
    'dental implants with bone loss cost',
    'how to know if you have bone loss in teeth',
    'how to fix bone loss in teeth',
    'can you have implants with bone loss',
    'can you get implants if you have bone loss',
    'can i get implants if i have bone loss',

    # Full set
    'full top set of dental implants',
    'how much is a full set of dental implants uk',
    'full set of new teeth cost uk',
    'how much is it to get teeth done',
    'how much does it cost to get your teeth done',

    # Misc high-intent
    'rheumatoid arthritis and dental implants',
    'dental implants north east england',
    'new dental technology for missing teeth',
    'dental plates for missing teeth',
    'clip in teeth for missing teeth',
    'clipping teeth for missing teeth',
]

PENDING_DENTURE = [
    'affordable dentures snap on implants', 'implant retained dentures cost uk',
    'dentures or implants which is better', 'how much for fixed dentures',
    'snap in dentures cost uk', 'problems with snap in dentures',
    'snap in dentures before and after',
    'which is better dentures or implants', 'is implants better than dentures',
    'is there a dental plan that covers implants',
    'cost of single tooth denture', 'single tooth denture near me',
    'top dentures without palate uk',
    'the denture and implant clinic',
    'clip in dentures for missing teeth',
    'alternative to dentures with gum disease',
]

PENDING_ABROAD_AS_DENTURE_RELATED = [
    # All-on-4 abroad — keep blocked anyway, but tagged as denture-pending if all-on-4 is denture-supported
    'cheapest country for all on 4 dental implants',
    'all on 4 dental implants turkey reviews',
    'all on 4 dental implants thailand price',
    'cost of full mouth dental implants in ireland',
    'cost of dental implants thailand',
    'cost of dental implants in bali',
    'cost of dental implant in australia',
    'dental implants in germany prices',
]

PENDING_BRAND = [
    'is osstem a good implant', 'best dental implant brands in the world',
    'dental implant brands to avoid', 'nobel biocare multi unit abutment',
]
PENDING_CERAMIC = [
    'what is basal dental implant', 'holistic alternatives to dental implants',
    'dental implant vs root canal holistic',
]


def page_of(t):
    try:
        return sorted_kws.index(t) // PAGE + 1
    except ValueError:
        return None


NPAGES = (len(sorted_kws) + PAGE - 1) // PAGE
groups = {p: {'def': [], 'den': [], 'brand': [], 'cer': []} for p in range(1, NPAGES + 1)}
missing = []
for label, items in [('def', DEFINITE), ('den', PENDING_DENTURE),
                     ('brand', PENDING_BRAND), ('cer', PENDING_CERAMIC)]:
    for t in items:
        p = page_of(t)
        if p is None:
            missing.append((label, t))
        else:
            groups[p][label].append(t)

for p in range(1, NPAGES + 1):
    print(f'\n========== PAGE {p} ==========')
    for lbl, name in [('def', 'DEFINITE REMOVES'), ('den', 'PENDING DENTURE'),
                      ('brand', 'PENDING BRAND'), ('cer', 'PENDING CERAMIC/BASAL/HOLISTIC')]:
        items = sorted(set(groups[p][lbl]), key=str.lower)
        if not items:
            continue
        print(f'\n  {name} ({len(items)}):')
        for t in items:
            print(f'    {t}')

if missing:
    print('\nNOT IN LIST (typo or already removed):')
    for lbl, t in missing:
        print(f'  [{lbl}] {t}')
