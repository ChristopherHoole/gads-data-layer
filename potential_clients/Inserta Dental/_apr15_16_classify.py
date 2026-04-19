"""
Run the allowlist-based classifier on the April 15-16 combined report.
"""
import sys, io, pandas as pd, warnings, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings('ignore')

df = pd.read_csv('data/Search terms/Search terms report all campaigns 15th + 16h April.csv', skiprows=2, thousands=',')
df = df[~df['Search term'].astype(str).str.startswith('Total') & df['Search term'].notna()].copy()
df['Search term'] = df['Search term'].astype(str).str.lower().str.strip()
agg = df.groupby('Search term').agg({'Cost':'sum','Conversions':'sum'}).reset_index()

# DBD services + implant/dental vocab
SERVICES = set("""
implant implants dental dentist dentistry dentists teeth tooth veneer veneers
invisalign composite bonding cosmetic smile smiles makeover aligner aligners
bridge bridges crown crowns whitening brace braces straighten straightening
zygomatic aesthetic aesthetics dentures denture hollywood prosthetic prosthodontic
screw screwed implanted fitted fix fixed fixing replace replacement
replacing replaces permanent temporary porcelain ceramic zirconia zirconium
full partial upper lower front back molar incisor canine wisdom jaw mouth gum
gums arch arches single double multiple whole
""".split())

GENERIC = set("""
the a an and or of for with to by at in on from up down
is are was were be been being have has had do does did
best top great good bad better worse
near me nearby local private public my your our his her their
new old young adult adults senior seniors children kids family
london uk britain england wales scotland ireland europe
cost costs price prices pricing fee fees afford affordable finance
financing financed monthly payment pay quote quotes consultation book
appointment reviews review rated top-rated recommended trusted certified
quick fast easy hard difficult simple complex
how what why when where who which whom
is am are were been
can could should would will shall may might must ought
much many more most less least
need needs wants want looking seeking search find finds found
get getting got got
help guide info information faq tips advice
compare comparing vs versus difference between
before after during while since still yet now today tomorrow
before-and-after trial visit
hour hours day days week weeks month months year years
online offline same next this last
buy buying purchase purchasing
free trial insurance cover covered claim
1 2 3 4 5 6 7 8 9 10 12 14 16 18 20 24 25 30 40 50 60 65 one two three four five six seven eight nine ten
first second third final
yes no maybe ok okay
about over under
pros cons advantages disadvantages benefits risks
types type kind kinds options option alternative alternatives
process procedure steps step methods method
look looks looking
work works working worked
worth
""".split())

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
wallington belsize parsons friern raynes charing stepney tulse
ravenscourt bush shepherds shepherd forest hill golders muswell notting kentish
covent garden mile bethnal stoke newington abbey crystal palace crouch colliers
worcester park new malden thames ditton palmers winchmore canons burnt oak mill
elmers ponders woodford harley street west drayton
thornton norwood moor earls north east south holland park gloucester maida vale
st johns wood
w1 w2 w3 w4 w5 w6 w7 w8 w9 w10 w11 w12 w13 w14
se1 se3 se5 se6 se9 se13 se15 se17 se22 se23 se24 se27
e1 e2 e3 e5 e6 e8 e9 e11 e13 e14 e15 e17 e18
n1 n4 n5 n6 n8 n10 n11 n13 n17 n19 n21 n22
nw1 nw2 nw3 nw4 nw5 nw6 nw8 nw10 nw11
sw1 sw3 sw4 sw5 sw6 sw7 sw8 sw9 sw10 sw11 sw12 sw13 sw14 sw15 sw16 sw17 sw18 sw19 sw20
ec1 ec2 ec3 ec4 wc1 wc2
""".split())

ABROAD = set("""
turkey turkish poland polish hungary hungarian spain spanish albania albanian
croatia croatian romania romanian bulgaria bulgarian thailand thai india indian
mexico mexican germany german italy italian france french portugal portuguese
dubai uae emirates saudi qatar abroad switzerland swiss cyprus cypriot
ukrainian ukraine lithuanian lithuania latvia estonia slovakia slovenia serbia
bosnia czech greek greece irish dublin
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
perth paisley derry sedgefield nuneaton harrogate rochdale felixstowe
guildford knutsford lymington lowestoft beccles blyburgate grinstead haywards
brighouse midlands merseyside
surrey sussex kent hampshire essex hertfordshire berkshire oxfordshire
buckinghamshire cambridgeshire bedfordshire norfolk suffolk devon cornwall
dorset somerset wiltshire gloucestershire worcestershire warwickshire
northamptonshire leicestershire nottinghamshire derbyshire staffordshire
shropshire cheshire lancashire yorkshire durham cumbria lincolnshire
scotland wales britain
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
    if any(w in wset for w in ABROAD):
        return True
    if any(w in wset for w in CHEAP_NHS):
        return True
    if any(w in wset for w in DENTURE_WORDS) or 'false teeth' in term or 'fake teeth' in term:
        return True
    if any(w in wset for w in NON_DBD) or 'bone graft' in term or 'gum disease' in term or \
       'gum graft' in term or 'root canal' in term or 'sinus lift' in term or \
       'oral surgeon' in term or 'oral surgery' in term or 'hair transplant' in term:
        return True
    if any(w in wset for w in BRAND_RESEARCH):
        return True
    has_london = any(w in wset for w in LONDON) or 'london' in term
    if any(w in wset for w in UK_OUTSIDE) and not has_london:
        return True
    if re.match(r'^(dr|mr|mrs|ms|miss)\s', term):
        return True
    if wc == 1 and words[0] in {'teeth','tooth','smile','smiles','dentistry',
                                  'implant','implants','dental','oral','dentist',
                                  'dentists'}:
        return True
    ALL = SERVICES | GENERIC | LONDON
    unknown_words = [w for w in words if w not in ALL and not w.isdigit() and w not in {"'", "&", "/", "-"}]
    for uw in unknown_words[:]:
        if re.match(r'^[a-z]*\d+[a-z]*$', uw):
            unknown_words.remove(uw); continue
    if unknown_words:
        return True
    # 2-word brand pattern
    allowed_first_x_dental = {'cosmetic','implant','implants','private','new',
                                'best','top','my','your','the','a','free','mobile',
                                'holistic','family','childrens','kids','pediatric',
                                'paediatric','emergency','24','24/7','hour','hours',
                                'good','great','trusted','advanced','modern','digital',
                                'in','at','to','for','near','same','day','online'}
    if wc == 2 and words[1] in {'dental','smiles','smile','dentistry','dent'}:
        if words[0] not in allowed_first_x_dental and words[0] not in SERVICES:
            return True
    if wc == 3 and words[2] in {'dental','smiles','smile','dentistry','dent','dentist'}:
        if words[0] not in allowed_first_x_dental and words[0] not in SERVICES and \
           words[1] not in allowed_first_x_dental and words[1] not in SERVICES:
            return True
    if wc == 3 and words[1] in {'smiles','smile'} and words[2] in {'dental','dentist','dentistry'}:
        return True
    if wc >= 2 and words[0].isdigit() and (words[-1] in LONDON or words[-1] in UK_OUTSIDE):
        return True
    if 'harley street' in term or 'harley st' in term:
        return True
    if wc == 1 and words[0] not in SERVICES:
        for suf in ('dental','dentist','dentistry','smiles','smile','dent','teeth','tooth','implant','implants'):
            if words[0].endswith(suf) and words[0] != suf:
                if 'dentalbydesign' not in term:
                    return True
    return False

results = {'1_word':[], '2_word':[], '3_word':[], '4_word':[], '5plus_word':[]}
for _, r in agg.iterrows():
    term = r['Search term']
    if classify(term):
        wc = len(term.split())
        key = f'{wc}_word' if wc <= 4 else '5plus_word'
        results[key].append(term)

# DBD substring exclusion (final safety net)
dbd_substrings = [
    'all on 4','all on 6','all on four','all on six','all in 4','all in 6',
    'all on x','4 on all','on all 4','on all 6',
    'screwless','screw-less',
    'dental by design','dentalbydesign',
    'vivo bridge','smile design','digital smile',
    'immediate implant placement','immediate dental implants',
    'payment plan','finance','on finance','0% finance',
    'near me','hammersmith',
    'implant specialist','dental specialist',
    'dental implants cost','dental implant cost',
    'cost of dental implant','cost of a dental implant','cost of teeth implant',
    'price of dental implant','price of implant','implant price','implants price',
    'how much','how much is','how much does','how much for','how much to',
    'average cost','average price',
    'full mouth implant','full mouth dental',
    'full set of dental implants','full set of teeth implants','full set of implants',
    'full set of new teeth','full set dental implants',
    'best dental implant','best implant','best tooth implant','best teeth implant',
    'best place','best replacement',
    'what is the cost','what is the average','what is the best','what are',
    'what is all','what is an all','what does all','which is better all',
    'veneer','veneers','bonding','invisalign','aligner','cosmetic','makeover',
]
def is_dbd(term):
    return any(s in term for s in dbd_substrings)

for k in results:
    results[k] = [t for t in results[k] if not is_dbd(t)]

# Load all prior additions (Apr 13 + Apr 14 first pass + Apr 14 2nd pass)
prior_all = {'1_word':set(),'2_word':set(),'3_word':set(),'4_word':set(),'5plus_word':set()}
for pf in ['_apr13_clean_diff.txt','_apr13_final.txt','_apr14_FINAL.txt','_apr14_2nd_FINAL.txt']:
    try:
        with open(pf,'r',encoding='utf-8') as f: pc = f.read().replace(chr(13),'')
        cur = None
        for line in pc.splitlines():
            m = re.match(r'### (\S+)', line)
            if m and m.group(1) in prior_all:
                cur = m.group(1); continue
            elif m:
                cur = None; continue
            mm = re.match(r'\[([^\]]+)\]', line)
            if mm and cur:
                prior_all[cur].add(mm.group(1))
    except: pass

# Dedupe against prior
new_by_cat = {}
for k in results:
    new_by_cat[k] = [t for t in results[k] if t not in prior_all[k]]

with open('_apr15_16_final.txt','w',encoding='utf-8') as f:
    for k in ['1_word','2_word','3_word','4_word','5plus_word']:
        f.write(f'### {k} ({len(new_by_cat[k])}) ###\n')
        for t in new_by_cat[k]:
            f.write(f'[{t}]\n')
        f.write('\n')
    total = sum(len(new_by_cat[k]) for k in new_by_cat)
    f.write(f'TOTAL NEW: {total}\n')

for k in ['1_word','2_word','3_word','4_word','5plus_word']:
    print(f'{k}: {len(new_by_cat[k])}')
print(f'Total NEW: {sum(len(new_by_cat[k]) for k in new_by_cat)}')
