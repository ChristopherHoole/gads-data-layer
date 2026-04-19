"""
Allowlist-based classifier: a term is KEPT only if every word is in a known
allowlist (services, generic/common, London locations). Any unknown word =
likely a brand/named person/unfamiliar location = block the term.
"""
import sys, io, pandas as pd, warnings, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings('ignore')

df = pd.read_csv('data/Search terms/Search terms report all campaigns 14-4-26 2nd pass.csv', skiprows=2, thousands=',')
df = df[~df['Search term'].astype(str).str.startswith('Total') & df['Search term'].notna()].copy()
df['Search term'] = df['Search term'].astype(str).str.lower().str.strip()
agg = df.groupby('Search term').agg({'Cost':'sum','Conversions':'sum'}).reset_index()

# DBD services + implant/dental vocab
SERVICES = set("""
implant implants dental dentist dentistry dentists teeth tooth veneer veneers
invisalign composite bonding cosmetic smile smiles makeover aligner aligners
bridge bridges crown crowns whitening brace braces straighten straightening
zygomatic aesthetic aesthetics dentures denture hollywood prosthetic prosthodontic
screw screwed implanted fitted implanted fix fixed fixing replace replacement
replacing replaces permanent temporary porcelain ceramic zirconia zirconium
full partial upper lower front back molar incisor canine wisdom jaw mouth gum
gums arch arches single double multiple whole all-on-4 all-on-6 allon4 allon6
""".split())

# Generic / common English + buying intent
GENERIC = set("""
the a an and or of for with to by at in on from up down
is are was were be been being have has had do does did
best top great good bad better worse cheap cheapest affordable pricey
near me nearby local private public my your our his her their
new old young adult adults senior seniors children kids family
london uk britain england britain england wales scotland ireland europe
cost costs price prices pricing fee fees afford affordable finance
financing financed monthly payment pay quote quotes consultation book
appointment reviews review rated top-rated recommended trusted certified
quick fast easy hard difficult simple complex
how what why when where who which whom why
is am are were been
can could should would will shall may might must ought
much many more most less least
need needs wants want looking seeking search find finds found
get getting got got
help guide info information faq tips advice
compare comparing vs versus difference between
before after during while since still yet now today tomorrow
before-and-after trial visit consultation
hour hours day days week weeks month months year years
online offline same next this last next
buy buying purchase purchasing buying
free trial insurance cover covered claim
1 2 3 4 5 6 7 8 9 10 12 14 16 18 20 24 25 30 40 50 60 65 one two three four five six seven eight nine ten
first second third final last
yes no maybe ok okay
about over under more less
pros cons advantages disadvantages benefits risks
types type kind kinds options option alternative alternatives
process procedure steps step methods method
good-looking natural looking look looks looking
work works working worked
worth
""".split())

# London areas
LONDON = set("""
london hammersmith chiswick fulham kensington chelsea westminster mayfair
marylebone camden islington hackney shoreditch bermondsey brixton clapham
putney wandsworth battersea wimbledon balham streatham tooting earlsfield
mitcham sutton croydon bromley lewisham greenwich woolwich bexleyheath bexley
erith catford sydenham dulwich peckham deptford rotherhithe stratford leyton
walthamstow chingford edmonton enfield barnet finchley hendon harrow ruislip
uxbridge hillingdon hayes southall ealing acton hanwell greenford perivale
wembley kilburn willesden cricklewood hornsey tottenham haringey highgate
archway holloway pimlico bayswater paddington knightsbridge belgravia soho
bloomsbury holborn barbican clerkenwell aldgate whitechapel dalston hoxton
wapping limehouse poplar barking dagenham romford ilford redbridge wanstead
havering upminster hornchurch rainham kingston richmond teddington twickenham
hampton feltham hounslow brentford isleworth heston cranford colindale neasden
southgate harlesden wealdstone stanmore edgware morden surbiton tolworth
beckenham penge anerley purley coulsdon selhurst mottingham eltham charlton
blackheath plumstead orpington chislehurst shirley addiscombe sanderstead
carshalton chessington sheen kew walworth chadwell welling sidcup dartford
wallington belsize parsons friern raynes charing stepney tulse mitcham
ravenscourt bush shepherds shepherd forest hill golders muswell notting kentish
covent garden mile bethnal stoke newington abbey crystal palace crouch colliers
worcester park new malden thames ditton palmers winchmore canons burnt oak mill
elmers ponders new addington hackney wick woodford harley street west drayton
thornton norwood moor kensington earls north finchley east finchley west north
east south holland park gloucester maida vale st johns wood
w1 w2 w3 w4 w5 w6 w7 w8 w9 w10 w11 w12 w13 w14
se1 se3 se5 se6 se9 se13 se15 se17 se22 se23 se24 se27
e1 e2 e3 e5 e6 e8 e9 e11 e13 e14 e15 e17 e18
n1 n4 n5 n6 n8 n10 n11 n13 n17 n19 n21 n22
nw1 nw2 nw3 nw4 nw5 nw6 nw8 nw10 nw11
sw1 sw3 sw4 sw5 sw6 sw7 sw8 sw9 sw10 sw11 sw12 sw13 sw14 sw15 sw16 sw17 sw18 sw19 sw20
ec1 ec2 ec3 ec4 wc1 wc2
""".split())

# Wrong-intent signals (force block regardless)
ABROAD = set("""
turkey turkish poland polish hungary hungarian spain spanish albania albanian
croatia croatian romania romanian bulgaria bulgarian thailand thai india indian
mexico mexican germany german italy italian france french portugal portuguese
dubai uae emirates saudi qatar abroad switzerland swiss cyprus cypriot
ukrainian ukraine lithuanian lithuania latvia estonia slovakia slovenia serbia
bosnia czech greek greece ireland irish dublin
istanbul antalya bodrum izmir ankara marmaris warsaw krakow budapest sofia
plovdiv bucharest prague brno zagreb split dubrovnik ljubljana tirana athens
thessaloniki lisbon porto bangkok phuket mumbai delhi bangalore chennai cancun
cairo alexandria hurghada casablanca marrakech vienna salzburg zurich geneva
brussels copenhagen stockholm helsinki oslo manila jakarta lahore cebu bali
benidorm toronto johannesburg
""".split())

UK_OUTSIDE = set("""
birmingham manchester liverpool leeds sheffield bristol newcastle nottingham
leicester coventry cardiff belfast glasgow edinburgh aberdeen dundee swansea
oxford cambridge brighton bournemouth portsmouth southampton plymouth norwich
york reading swindon hull stoke derby wolverhampton bath exeter bradford
blackpool preston doncaster sunderland middlesbrough northampton peterborough
gloucester worcester colchester ipswich chester warrington blackburn bolton
burnley carlisle lancaster stockport wigan rotherham barnsley wakefield
huddersfield halifax scunthorpe grimsby lincoln mansfield kettering corby
rugby tamworth burton walsall dudley sandwell solihull redditch kidderminster
telford shrewsbury hereford bangor wrexham newport spalding inverness stirling
perth paisley derry sedgefield nuneaton harrogate rochdale bradford felixstowe
guildford knutsford lymington lowestoft beccles blyburgate grinstead haywards
brighouse
surrey sussex kent hampshire essex hertfordshire berkshire oxfordshire
buckinghamshire cambridgeshire bedfordshire norfolk suffolk devon cornwall
dorset somerset wiltshire gloucestershire worcestershire warwickshire
northamptonshire leicestershire nottinghamshire derbyshire staffordshire
shropshire cheshire lancashire yorkshire durham cumbria lincolnshire midlands
merseyside
camberley chelmsford maidstone woking reigate watford luton slough basingstoke
stevenage welwyn hitchin braintree harlow southend rochester chatham gillingham
tunbridge tonbridge sevenoaks canterbury margate ramsgate ashford folkestone
dover horsham crawley worthing chichester bognor aldershot farnham farnborough
leatherhead dorking redhill gatwick eastbourne hastings hove lewes windsor eton
bedford grantham brentwood dorchester fareham medway wimborne cobham egham
chertsey petersfield weybridge cheshunt hawick clacton beaconsfield bushey
borehamwood elstree radlett caterham loughton epping stafford magherafelt
barnstaple devizes esher byfleet stroud pontypridd datchet hook benfleet
redruth cirencester daventry maidenhead ascot kidbrooke whitstable rickmansworth
broxbourne buxton pembrokeshire scarborough wirral rawtenstall stortford
whitehaven bridgwater oldham hertford molesey walton staines bagshot bedfont
bedfordshire southwark pinner
""".split())

DENTURE_WORDS = {'denture','dentures','false','fake','flipper','overdenture',
                 'valplast','plateless','palateless','snap','clip','screw-in',
                 'removable','silicone','plastic-teeth'}
CHEAP_NHS = {'cheap','cheapest','cheaper','affordable','groupon','wowcher','free',
             'grants','grant','nhs','budget','inexpensive','pensioner','pensioners'}
NON_DBD = {'extraction','extractions','root','canal','filling','fillings',
           'whitening','disease','graft','grafting','restoration','recession',
           'receding','hair','transplant','periodontal','periodontitis',
           'periodontist','periodontic','periodontics','endodontist','endodontics',
           'prosthodontics','prosthodontist','orthognathic','hearing','decay',
           'ozone','maxillofacial','sinus','augmentation','apicoectomy','abutment',
           'cerec','dds'}
BRAND_RESEARCH = {'straumann','osstem','astra','dentium','biomet','neodent',
                  'alphabio','nobel','ivoclar','camlog','subperiosteal','basal',
                  'emax','sirona','dentsply','zimmer','biomet','bredent','biohorizon',
                  'dentakay','dentaprime','banning','evo','kreativ','attelia',
                  'vital','dentafly','osstem','implantly','implanty'}

def classify(term):
    words = re.findall(r"[a-z0-9'&/-]+", term.lower())
    wset = set(words)
    wc = len(words)

    # Hard blocks
    if any(w in wset for w in ABROAD):
        return True, 'abroad'
    if any(w in wset for w in CHEAP_NHS):
        return True, 'cheap_nhs'
    if any(w in wset for w in DENTURE_WORDS) or 'false teeth' in term or 'fake teeth' in term:
        return True, 'denture'
    if any(w in wset for w in NON_DBD) or 'bone graft' in term or 'gum disease' in term or \
       'gum graft' in term or 'root canal' in term or 'sinus lift' in term or \
       'oral surgeon' in term or 'oral surgery' in term or 'hair transplant' in term:
        return True, 'non_dbd'
    if any(w in wset for w in BRAND_RESEARCH):
        return True, 'brand_research'
    has_london = any(w in wset for w in LONDON) or 'london' in term
    if any(w in wset for w in UK_OUTSIDE) and not has_london:
        return True, 'wrong_uk'
    # Dr / Mr / Mrs named
    if re.match(r'^(dr|mr|mrs|ms|miss)\s', term):
        return True, 'named_person'

    # Over-vague single words
    if wc == 1 and words[0] in {'teeth','tooth','smile','smiles','dentistry',
                                  'implant','implants','dental','oral','dentist',
                                  'dentists'}:
        return True, 'too_vague'

    # Allowlist check: every word must be in SERVICES, GENERIC, or LONDON
    ALL = SERVICES | GENERIC | LONDON
    unknown_words = [w for w in words if w not in ALL and not w.isdigit() and w not in {"'", "&", "/", "-"}]
    # Trailing/leading suffixes of known words
    for uw in unknown_words[:]:
        # Check if it's a number-adjacent thing like "24/7"
        if re.match(r'^[a-z]*\d+[a-z]*$', uw):  # alphanumeric like w12, nw1, n21, 24hr
            unknown_words.remove(uw); continue
        # Check if it's a suffix-variant of a known word
        for base in ['dent','dentist','dental','smile','tooth','implant','veneer','clinic','surgery']:
            if uw.startswith(base) or uw.endswith(base):
                if uw not in {'dent1st','denturely','denturly'}:  # known brands
                    pass  # still unknown, keep as unknown
        pass

    if unknown_words:
        return True, f'unknown_word:{unknown_words[0]}'

    # Brand patterns that slip through allowlist: "X dental", "X smiles", "X smile",
    # "X dentistry" - these are typically clinic brand names
    # (e.g. "abbey dental", "better dental", "beckenham smiles")
    allowed_first_x_dental = {'cosmetic','implant','implants','private','new',
                                'best','top','my','your','the','a','free','mobile',
                                'holistic','family','childrens','kids','pediatric',
                                'paediatric','emergency','24','24/7','hour','hours',
                                'good','great','trusted','advanced','modern','digital',
                                'in','at','to','for','near','same','day','online'}
    if wc == 2 and words[1] in {'dental','smiles','smile','dentistry','dent'}:
        if words[0] not in allowed_first_x_dental and words[0] not in SERVICES:
            return True, 'brand_x_dental'
    # 3-word brand: "[brand] dental [location/word]" or "[location] [brand] dental"
    if wc == 3 and words[2] in {'dental','smiles','smile','dentistry','dent','dentist'}:
        # "[word1] [word2] dental" - if word1 and word2 aren't services/generics, likely brand
        if words[0] not in allowed_first_x_dental and words[0] not in SERVICES and \
           words[1] not in allowed_first_x_dental and words[1] not in SERVICES:
            return True, 'brand_3word_compound'
    # 3-word with "dental" middle: "[loc] dental [word]"
    if wc == 3 and words[1] in {'dental','smiles','smile'}:
        if words[0] in LONDON and words[2] not in SERVICES and words[2] not in allowed_first_x_dental:
            # "beckenham smiles dental" - location + brand = block
            return True, 'brand_location_compound'
    # 1-word compounds ending in dental/dent/smiles/smile
    if wc == 1 and words[0] not in SERVICES:
        for suf in ('dental','dentist','dentistry','smiles','smile','dent','teeth','tooth','implant','implants'):
            if words[0].endswith(suf) and words[0] != suf:
                return True, 'brand_compound'

    # "[location] smiles dental" or similar 3-word brand patterns
    if wc == 3 and words[1] in {'smiles','smile'} and words[2] in {'dental','dentist','dentistry'}:
        return True, 'brand_3word_smile'
    # "[number] [word] dental" / "[number] [word] dentist" - e.g. "119 dental streatham"
    if wc >= 2 and words[0].isdigit() and (words[-1] in LONDON or words[-1] in UK_OUTSIDE):
        return True, 'brand_number_prefix'
    # "[number] harley street" / "X harley street" - Harley Street specific (not DBD area)
    if 'harley street' in term or 'harley st' in term:
        return True, 'harley_street'

    # All words are in allowlist — KEEP
    return False, 'keep_allowlist'


results = {'1_word':[], '2_word':[], '3_word':[], '4_word':[], '5plus_word':[], 'kept':[]}
reasons = {}

for _, r in agg.iterrows():
    term = r['Search term']
    words = term.split()
    wc = len(words)
    block, reason = classify(term)
    rkey = reason.split(':')[0]
    reasons[rkey] = reasons.get(rkey, 0) + 1
    if block:
        key = f'{wc}_word' if wc <= 4 else '5plus_word'
        results[key].append((term, reason))
    else:
        results['kept'].append((term, reason))

for k in ['1_word','2_word','3_word','4_word','5plus_word']:
    print(f'{k}: {len(results[k])}')
print(f'kept: {len(results["kept"])}')
print()
for r, n in sorted(reasons.items(), key=lambda x:-x[1]):
    print(f'  {r}: {n}')

with open('_apr14_2nd.txt','w',encoding='utf-8') as f:
    for k in ['1_word','2_word','3_word','4_word','5plus_word']:
        f.write(f'\n### {k} ({len(results[k])}) ###\n')
        for term, reason in results[k]:
            f.write(f'[{term}]\n')
    f.write(f'\n### KEPT ({len(results["kept"])}) ###\n')
    for term, reason in results['kept']:
        f.write(f'[{term}]  ({reason})\n')
