import sys, io, pandas as pd, warnings, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings('ignore')

df = pd.read_csv('data/Search terms/Search terms report 13-4-26.csv', skiprows=2, thousands=',')
df = df[~df['Search term'].astype(str).str.startswith('Total') & df['Search term'].notna()].copy()
df['Search term'] = df['Search term'].astype(str).str.lower().str.strip()
agg = df.groupby('Search term').agg({'Cost':'sum','Conversions':'sum'}).reset_index()

# ======== FLIPPED LOGIC: default BLOCK unless clearly potential DBD client ========

# DBD location signals (these make a term POTENTIAL CLIENT if present)
dbd_area = {'hammersmith','ravenscourt','chiswick'}

# Greater London / London boroughs & areas
london_words = set("""
london hammersmith chiswick fulham kensington chelsea westminster mayfair marylebone
camden islington hackney shoreditch bermondsey brixton clapham putney wandsworth
battersea wimbledon balham streatham tooting earlsfield mitcham sutton croydon
bromley lewisham greenwich woolwich bexleyheath bexley erith catford sydenham
dulwich peckham deptford rotherhithe stratford leyton walthamstow chingford
edmonton enfield barnet finchley hendon harrow ruislip uxbridge hillingdon hayes
southall ealing acton hanwell greenford perivale wembley kilburn willesden
cricklewood hornsey tottenham haringey highgate archway holloway pimlico
bayswater paddington knightsbridge belgravia soho bloomsbury holborn barbican
clerkenwell aldgate whitechapel dalston hoxton wapping limehouse poplar barking
dagenham romford ilford redbridge wanstead havering upminster hornchurch rainham
kingston richmond teddington twickenham hampton feltham hounslow brentford
isleworth heston cranford colindale neasden southgate harlesden wealdstone
stanmore edgware morden surbiton tolworth beckenham penge anerley purley
coulsdon selhurst mottingham eltham charlton blackheath plumstead orpington
chislehurst shirley addiscombe sanderstead carshalton chessington sheen kew
walworth chadwell welling sidcup dartford wallington belsize parsons friern
raynes charing stepney mitcham tulse w1 w2 w3 w4 w5 w6 w7 w8 w9 w10 w11 w12 w13 w14
se1 se3 se6 se9 se13 se15 se17 se22 e1 e3 e5 e8 e11 e14 e15 e17 n1 n5 n6 n10
n13 n19 n21 n22 nw1 nw3 nw5 nw6 nw10 sw1 sw3 sw6 sw11 sw15 sw18 sw19 sw20
gloucester_road holland_park
""".split())

london_phrases = [
    'forest hill','golders green','muswell hill','notting hill','kentish town',
    'covent garden','shepherds bush','shepherd bush','mile end','bethnal green',
    'stoke newington','chadwell heath','abbey wood','crystal palace','crouch end',
    'colliers wood','worcester park','new malden','thames ditton','palmers green',
    'winchmore hill','canons park','burnt oak','mill hill','elmers end',
    'ponders end','new addington','hackney wick','south woodford','harley street',
    'west drayton','thornton heath','south norwood','moor park','west kensington',
    'earls court','north finchley','east finchley','west london','north london',
    'east london','south london','north east london','south east london',
    'south west london','north west london','holland park','gloucester road',
    'maida vale','st johns wood','st johns',
]

# DBD services (these make term POTENTIAL CLIENT)
dbd_services = {
    'invisalign','veneer','veneers','implant','implants','composite','bonding',
    'cosmetic','smile','makeover','all-on-4','all-on-6','aligners','zygomatic',
    'full mouth','same day teeth','whitening',  # offered but borderline
}

# Buying intent signals (keep if matched with service/location)
buying_signals = {
    'cost','costs','price','prices','pricing','finance','financing','financed',
    'payment','monthly','quote','quotes','consultation','book','appointment','near me',
    'near-me','afford','affordable',  # wait affordable is cheap - removed below
    'best','top','private','luxury','premium','specialist','expert','experts',
    'advanced','ready','get','need','want','how much','reviews',
}
# Remove "affordable" - it's cheap-shopping signal not buying
buying_signals.discard('afford')
buying_signals.discard('affordable')

# ======== WRONG-INTENT SIGNALS (these force BLOCK regardless) ========
abroad = set("""
turkey turkish poland polish hungary hungarian spain spanish albania albanian
croatia croatian romania romanian bulgaria bulgarian thailand thai india indian
mexico mexican germany german italy italian france french portugal portuguese
dubai uae emirates saudi qatar europe european abroad switzerland swiss cyprus
ukrainian ukraine lithuanian lithuania latvia estonia slovakia slovenia slovenian
serbia serbian bosnia czech greek greece
istanbul antalya bodrum izmir ankara marmaris kusadasi warsaw krakow gdansk
budapest sofia plovdiv bucharest prague brno zagreb split dubrovnik ljubljana
maribor tirana durres athens thessaloniki lisbon porto faro bangkok phuket
chiangmai pattaya krabi mumbai delhi bangalore chennai hyderabad kolkata pune
cancun tijuana cairo alexandria hurghada casablanca marrakech dublin cork
galway vienna salzburg zurich geneva basel brussels antwerp copenhagen stockholm
helsinki oslo manila jakarta lahore cebu bali benidorm toronto johannesburg
dublin ireland irish
""".split())

uk_outside = set("""
birmingham manchester liverpool leeds sheffield bristol newcastle nottingham
leicester coventry cardiff belfast glasgow edinburgh aberdeen dundee swansea
oxford cambridge brighton bournemouth portsmouth southampton plymouth norwich
york reading swindon hull stoke derby wolverhampton bath exeter bradford
blackpool preston doncaster sunderland middlesbrough northampton peterborough
gloucester worcester colchester ipswich chester warrington blackburn bolton
burnley carlisle lancaster stockport wigan rotherham barnsley wakefield
huddersfield halifax scunthorpe grimsby lincoln mansfield kettering corby
rugby tamworth burton walsall dudley sandwell solihull redditch kidderminster
telford shrewsbury hereford bangor wrexham newport spalding
inverness stirling perth paisley derry sedgefield nuneaton harrogate rochdale
bradford felixstowe guildford knutsford lymington lowestoft beccles blyburgate
grinstead haywards
surrey sussex kent hampshire essex hertfordshire berkshire oxfordshire
buckinghamshire cambridgeshire bedfordshire norfolk suffolk devon cornwall
dorset somerset wiltshire gloucestershire worcestershire warwickshire
northamptonshire leicestershire nottinghamshire derbyshire staffordshire
shropshire cheshire lancashire yorkshire durham cumbria lincolnshire
scotland wales midlands england britain merseyside
camberley chelmsford maidstone woking reigate watford luton
slough basingstoke stevenage welwyn hitchin braintree harlow southend rochester
chatham gillingham tunbridge tonbridge sevenoaks canterbury margate ramsgate
ashford folkestone dover horsham crawley worthing chichester bognor aldershot
farnham farnborough leatherhead dorking redhill gatwick eastbourne hastings
hove lewes windsor eton bedford grantham brentwood dorchester fareham medway
wimborne cobham egham chertsey petersfield weybridge cheshunt hawick
clacton beaconsfield bushey borehamwood elstree radlett caterham
loughton epping stafford magherafelt barnstaple devizes
esher byfleet stroud pontypridd datchet hook benfleet redruth
cirencester daventry maidenhead ascot kidbrooke whitstable rickmansworth
broxbourne buxton pembrokeshire scarborough wirral rawtenstall stortford
whitehaven bridgwater oldham hertford molesey walton staines bagshot bedfont
bedfordshire southwark sunderland stirling pinner
""".split())

denture_words = {'denture','dentures','false teeth','false tooth','fake teeth','fake tooth',
                 'flipper','overdenture','partial denture','dental plate','dental plates',
                 'snap in','snap on','snap fit','clip in','clip on','plastic teeth',
                 'acrylic teeth','bolt in','bolted in','screw in teeth','ivoclar',
                 'set of teeth','silicone dentures','valplast','plateless',
                 'palateless','soft dentures','removable teeth','teeth set'}
cheap_nhs = {'cheap','cheapest','cheaper','affordable','groupon','wowcher','free',
             'grants','grant','nhs','budget','inexpensive','pensioner','pensioners',
             'low cost','bargain'}
non_dbd = {'extraction','extractions','root canal','filling','fillings','whitening',
           'gum disease','gum graft','gum grafting','gum restoration','gum recession',
           'receding gums','hair transplant','hair implants','periodontal','periodontitis',
           'periodontist','periodontic','periodontics','endodontist','endodontics',
           'prosthodontics','prosthodontist','orthognathic','hearing aids','decay',
           'tooth decay','ozone therapy','maxillofacial','oral surgeon','oral surgery',
           'sinus lift','sinus augmentation','bone graft','bone grafting','apicoectomy',
           'abutment','cerec','dds'}
brand_research = {'straumann','osstem','astra','dentium','biomet','neodent','alpha bio',
                  'nobel active','nobel teeth','nobel biocare','ivoclar','camlog',
                  'subperiosteal','mini implant','mini dental','basal','ceramic dental',
                  'zirconia dental','zirconium','emax','swiss implant','sirona',
                  'dentsply','zimmer biomet'}

# Over-vague / generic terms that don't qualify as intent
too_vague = {'teeth','tooth','smile','smiles','dentist','dentists','dentistry',
             'implant','implants','dental','missing tooth','missing teeth','oral',
             'dents','dent'}

# Branch/practice patterns — if term has "X dental" or "X dent" where X is any token,
# it's very likely a specific clinic brand (e.g. "shine dental", "prem dent")
practice_words = {'clinic','clinics','practice','practices','centre','center','centres',
                  'centers','surgery','surgeries','studio','studios','suite','suites',
                  'house','spa','group','lounge','wellness','aesthetics','specialists',
                  'specialist','emporium','boutique','sanctuary','gallery','artistry',
                  'institute','rooms','office','arts','solutions','hub','spa','partners',
                  'department','school','trials','experts'}

# Named dentist regex
dr_re = re.compile(r'\bdr\s+[a-z]+')  # "dr X" - any dr
# first_name last_name dentist pattern (block if not London area)
fn_ln_re = re.compile(r'^([a-z\']+)\s+([a-z\']+)\s+(dentist|dental|dentistry|orthodontist)$')
first_generic = {'the','best','cheap','good','local','private','nhs','emergency',
                 'cosmetic','family','kids','children','my','your','a','an','find',
                 'new','top','free','affordable','budget','uk','london','near','great',
                 'quality','premium','luxury','smart','modern','beautiful','perfect'}


def is_london(raw, wset):
    if 'london' in wset: return True
    if any(w in wset for w in london_words): return True
    if any(p in raw for p in london_phrases): return True
    return False


def classify(term, cost):
    """Returns (block:bool, reason:str)."""
    words = term.split()
    wc = len(words)
    wset = set(words)

    has_london = is_london(term, wset)

    # ===== WRONG-INTENT CHECKS (force block) =====
    # Non-DBD service
    for w in non_dbd:
        if w in term:
            return True, 'non_dbd'
    # Denture
    for w in denture_words:
        if w in term:
            return True, 'denture'
    # Cheap/NHS/free
    if any(w in wset for w in cheap_nhs):
        return True, 'cheap_nhs'
    # Abroad
    if any(w in wset for w in abroad):
        return True, 'abroad'
    # Brand research
    for b in brand_research:
        if b in term:
            return True, 'brand_research'
    # Wrong UK (no London)
    if any(w in wset for w in uk_outside) and not has_london:
        return True, 'wrong_uk'
    # Named "Dr X"
    if dr_re.search(term):
        return True, 'named_dr'
    # first_name last_name dentist pattern
    m = fn_ln_re.match(term)
    if m:
        fw = m.group(1)
        if fw not in first_generic and fw not in london_words and fw not in dbd_area:
            return True, 'named_dr'

    # ===== BRAND PATTERN: "X dental" / "X dent" / similar =====
    # 2-word ending in "dental" where first word isn't a service or generic
    service_first_words = {'cosmetic','dental','tooth','teeth','implant','veneer','bridge',
                           'crown','full','private','uk','london','modern','new','the',
                           'best','top','professional','affordable','family','my','your',
                           'advanced','comprehensive'}
    if wc == 2 and words[1] in {'dental','dent','dentistry','smiles','smile','dentist'}:
        if words[0] not in service_first_words and words[0] not in dbd_area:
            return True, 'brand_x_dental'
    # Single compound words like "shinedental" or "ktdental"
    if wc == 1 and (words[0].endswith('dental') or words[0].endswith('dent') or
                    words[0].endswith('dentist') or words[0].endswith('smiles') or
                    words[0].endswith('smile') or words[0].endswith('dentistry')) and \
       words[0] not in {'dental','dentist','dentistry','smiles','smile','implant',
                         'implants','teeth','tooth'}:
        # e.g. 'dent1st', 'denturely', 'ktdental', 'smile2o', 'dentalbydesign'
        if 'dentalbydesign' not in term:  # DBD itself!
            return True, 'brand_compound'

    # 3+ words: X Y dental/dent/etc as brand
    if wc >= 2 and any(words[-1] == pw or words[-1].endswith('dental') for pw in {'dental','dent','dentistry','dentist','smiles','smile'}):
        pass  # covered above

    # Any term with practice_words (boutique, sanctuary, studio, clinic, etc.) + dental-ish word
    if any(w in wset for w in practice_words):
        # Check for DBD-adjacent: if term explicitly mentions "near me" with london context, maybe keep
        # Otherwise the practice word = brand
        if has_london and any(w in wset for w in buying_signals) and 'clinic' not in wset and 'practice' not in wset:
            pass  # borderline, let it through to KEEP check
        else:
            # If it has a practice marker word + ANY other token that looks branded, block
            return True, 'brand_practice'

    # ===== TOO VAGUE (1-word generic) =====
    if wc == 1 and words[0] in too_vague:
        return True, 'too_vague'
    # "missing tooth" alone - too vague for DBD
    if term in {'missing tooth','missing teeth','oral surgeon','oral surgery','tooth','teeth'}:
        return True, 'too_vague'

    # ===== BRAND PATTERN: "dental + practice word" = competitor clinic brand =====
    # Block even in London (these are specific competitor clinics)
    brand_markers_multi = ['dental clinic','dental practice','dental centre','dental center',
                            'dental surgery','dental studio','dental care','dental beauty',
                            'dental suite','dental house','dental spa','dental group',
                            'dental lounge','dental arts','dental office','dental art',
                            'dental artistry','dental services','dental experts','dental aesthetic',
                            'dental wellness','dental boutique','dental sanctuary','dental academy',
                            'dental hub','dental partners','dental solutions','smile clinic',
                            'smile studio','smile centre','smile spa','smile boutique',
                            'smile academy','smile creator','smile sanctuary','smile direct',
                            'smile sanctuary','implant centre','implant clinic','implant studio',
                            'implant suite','dentist in ','dentists in ','dental care near me',
                            'tooth club','dental hospital','dental lounge','dentistry london']
    # Exception: DBD's own area in Hammersmith
    is_dbd_clinic = 'hammersmith' in term and any(s in term for s in ['dental by design','dbd'])
    if any(bm in term for bm in brand_markers_multi) and not is_dbd_clinic:
        # Check if it's a DBD service search with clinic mention (e.g. "implant clinic near me")
        # "near me" with clinic = still brand-shopping, block
        return True, 'brand_competitor'

    # ===== KEEP signals =====
    # London + service/buying
    has_service = any(s in wset for s in dbd_services) or \
                   any(s in term for s in ['all on 4','all on 6','all-on-4','all-on-6',
                                            'same day','full mouth','composite bonding'])
    has_buying = any(s in wset for s in buying_signals) or 'near me' in term

    if has_london and (has_service or has_buying):
        return False, 'keep_london_service'
    if has_service and has_buying:
        return False, 'keep_service_buying'
    # DBD-area-specific
    if any(w in wset for w in dbd_area):
        return False, 'keep_dbd_area'
    # Service alone (buying intent)
    if has_service and wc >= 2:
        return False, 'keep_service'
    # Pure London search (e.g. "dentist london", "london dental clinic" — generic London is fine)
    if has_london and wc >= 2 and not any(w in wset for w in practice_words - {'clinic','practice','centre'}):
        # London + clinic/practice/centre = generic London clinic = DBD potential
        return False, 'keep_london'
    # 1-word DBD service (veneers, invisalign)
    if wc == 1 and words[0] in {'invisalign','veneers','veneer'}:
        return False, 'keep_dbd_service'

    # Default: BLOCK — term doesn't qualify as potential DBD client
    return True, 'block_default'


results = {'1_word':[], '2_word':[], '3_word':[], '4_word':[], '5plus_word':[], 'kept':[]}
reasons_summary = {}

for _, r in agg.iterrows():
    term = r['Search term']
    cost = r['Cost']
    words = term.split()
    wc = len(words)
    block, reason = classify(term, cost)
    reasons_summary[reason] = reasons_summary.get(reason, 0) + 1
    if block:
        key = f'{wc}_word' if wc <= 4 else '5plus_word'
        results[key].append((term, cost, reason))
    else:
        results['kept'].append((term, cost, reason))

for k in ['1_word','2_word','3_word','4_word','5plus_word']:
    print(f'{k}: {len(results[k])}')
print(f'kept: {len(results["kept"])}')
print()
print('Reason breakdown:')
for r, n in sorted(reasons_summary.items(), key=lambda x:-x[1]):
    print(f'  {r}: {n}')

with open('_apr13_v2.txt','w',encoding='utf-8') as f:
    for k in ['1_word','2_word','3_word','4_word','5plus_word']:
        f.write(f'\n### {k} ({len(results[k])}) ###\n')
        for term, cost, reason in results[k]:
            f.write(f'[{term}]\n')
    f.write(f'\n### KEPT ({len(results["kept"])}) ###\n')
    for term, cost, reason in results['kept']:
        f.write(f'[{term}]  ({reason})\n')
