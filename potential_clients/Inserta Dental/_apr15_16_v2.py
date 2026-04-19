"""
V2 classifier — much more aggressive. Fixes identified misses:
- Remove 'abbey', 'hayes' from ambiguous London set
- Add 'bury', 'hollywood smile', 'enameloplasty', mobile dentist, dental school to blocks
- Detect non-ASCII (Cyrillic/Greek/Polish special chars) as foreign = block
- Block compound words with brand suffixes (club, house, hub, lab, works, care)
- Add 'veneers', 'veneera', single-word services to too_vague
- Block NHS-style phrases: accepting new patients, taking new patients, register with dentist
"""
import sys, io, pandas as pd, warnings, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings('ignore')

df = pd.read_csv('data/Search terms/Search terms report all campaigns 15th + 16h April-1.csv', skiprows=2, thousands=',')
df = df[~df['Search term'].astype(str).str.startswith('Total') & df['Search term'].notna()].copy()
df['Search term'] = df['Search term'].astype(str).str.lower().str.strip()
agg = df.groupby('Search term').agg({'Cost':'sum','Conversions':'sum'}).reset_index()

SERVICES = set("""
implant implants dental dentist dentistry dentists teeth tooth veneer veneers
invisalign composite bonding cosmetic smile smiles makeover aligner aligners
bridge bridges crown crowns brace braces straighten straightening
zygomatic aesthetic aesthetics hollywood prosthetic prosthodontic
screw screwed implanted fitted fix fixed fixing replace replacement
replacing replaces permanent porcelain ceramic zirconia zirconium
full partial upper lower front back molar incisor canine wisdom jaw mouth
arch arches single double multiple whole
""".split())

GENERIC = set("""
the a an and or of for with to by at in on from up down
is are was were be been being have has had do does did
best top great good bad better worse
near me nearby local private public my your our his her their
new old young adult adults senior seniors children kids family
london uk britain england
cost costs price prices pricing fee fees
payment pay quote quotes consultation book
appointment reviews review rated top-rated recommended trusted certified
quick fast easy hard difficult simple complex
how what why when where who which whom
is am are were been
can could should would will shall may might must ought
much many more most less least
need needs wants want looking seeking search find finds found
get getting got
help guide info information faq tips advice
compare comparing vs versus difference between
before after during while since still yet now today tomorrow
hour hours day days week weeks month months year years
online offline same next this last
buy buying purchase purchasing
trial cover covered claim
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

# London — REMOVED: abbey (ambiguous), hayes (Hillingdon borderline)
LONDON = set("""
london hammersmith chiswick fulham kensington chelsea westminster mayfair
marylebone camden islington hackney shoreditch bermondsey brixton clapham
putney wandsworth battersea wimbledon balham streatham tooting earlsfield
mitcham sutton croydon bromley lewisham greenwich woolwich bexleyheath bexley
erith catford sydenham dulwich peckham deptford rotherhithe stratford leyton
walthamstow chingford edmonton enfield barnet finchley hendon harrow ruislip
uxbridge hillingdon southall ealing acton hanwell greenford perivale
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
ravenscourt bush shepherds shepherd forest golders muswell notting kentish
covent mile bethnal stoke newington crystal palace crouch colliers
worcester new malden thames ditton palmers winchmore canons burnt oak mill
elmers ponders woodford harley drayton norwood moor earls holland gloucester
maida vale johns
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
bosnia czech greek greece irish dublin moldova pakistan philippines
istanbul antalya bodrum izmir ankara marmaris warsaw krakow budapest sofia
plovdiv bucharest prague brno zagreb split dubrovnik ljubljana tirana athens
thessaloniki lisbon porto bangkok phuket mumbai delhi bangalore chennai cancun
cairo alexandria hurghada casablanca marrakech vienna salzburg zurich geneva
brussels copenhagen stockholm helsinki oslo manila jakarta lahore cebu bali
benidorm toronto johannesburg kuala lumpur hyderabad pondicherry
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
brighouse midlands merseyside bury middleton crosby sandbach clacton edenbridge
caterham nantwich andover abingdon addlestone bracknell borough cheadle ayr
shrewsbury leigh wirral whitehaven oldham hertford molesey walton staines
bagshot bedfont derby sedgefield salisbury welling bagshot basingstoke maidenhead
ascot windsor eton bedford grantham brentwood dorchester fareham medway
wimborne cobham egham chertsey petersfield weybridge cheshunt hawick
beaconsfield bushey borehamwood elstree radlett loughton epping stafford
magherafelt barnstaple devizes esher byfleet stroud pontypridd datchet hook
benfleet redruth cirencester daventry kidbrooke whitstable rickmansworth
broxbourne buxton pembrokeshire scarborough rawtenstall stortford bridgwater
pinner chigwell brentford woking reigate watford luton slough stevenage welwyn
hitchin braintree harlow southend rochester chatham gillingham tunbridge
tonbridge sevenoaks canterbury margate ramsgate ashford folkestone dover
horsham crawley worthing chichester bognor aldershot farnham farnborough
leatherhead dorking redhill gatwick eastbourne hastings hove lewes bedfordshire
bedfont southwark chelmsford maidstone bordon ross hayes ashford hove potters
barnehurst bellshill bridport chorley chorleywood crayford denton downend
eastcote faversham haslemere horley nailsworth penarth pinner puckeridge shoreham
smithfield towcester wantage warwick wellingborough darlington knowle loughton
haslemere
surrey sussex kent hampshire essex hertfordshire berkshire oxfordshire
buckinghamshire cambridgeshire bedfordshire norfolk suffolk devon cornwall
dorset somerset wiltshire gloucestershire worcestershire warwickshire
northamptonshire leicestershire nottinghamshire derbyshire staffordshire
shropshire cheshire lancashire yorkshire durham cumbria lincolnshire
scotland wales britain
""".split())

DENTURE_WORDS = {'denture','dentures','false','fake','flipper','overdenture',
                 'valplast','plateless','palateless','snap','clip','screw-in',
                 'removable','silicone','plastic-teeth'}
CHEAP_NHS = {'cheap','cheapest','cheaper','affordable','groupon','wowcher','free',
             'grants','grant','nhs','budget','inexpensive','pensioner','pensioners',
             'charity','charities'}
NON_DBD = {'extraction','extractions','root','canal','filling','fillings',
           'whitening','disease','graft','grafting','restoration','recession',
           'receding','hair','transplant','periodontal','periodontitis',
           'periodontist','periodontic','periodontics','endodontist','endodontics',
           'prosthodontics','prosthodontist','orthognathic','hearing','decay',
           'ozone','maxillofacial','sinus','augmentation','apicoectomy','abutment',
           'cerec','dds','enameloplasty','orthodontist','orthodontics','orthodontic',
           'mobile','schools','school'}
BRAND_RESEARCH = {'straumann','osstem','astra','dentium','biomet','neodent',
                  'alphabio','nobel','ivoclar','camlog','subperiosteal','basal',
                  'emax','sirona','dentsply','zimmer','biomet','bredent','biohorizon',
                  'dentakay','dentaprime','banning','evo','kreativ','attelia',
                  'vital','dentafly','implantly','implanty','hiossen','megagen',
                  'anthogyr','bicon','dentis','tiger','xi','ukmec','oxi','mis'}

# NHS/social care phrases
NHS_PHRASES = ['accepting new patients','taking new patients','nhs patients',
               'register with','registering with','dental school','schools that take',
               'free treatment','free dental','for pensioners','benefits','universal credit',
               'under 18','for children','for kids','nhs dentist','on the nhs']

# Foreign language detection: any Cyrillic, Greek, Chinese, Arabic, Hebrew chars
def is_foreign_script(term):
    return bool(re.search(r'[\u0400-\u04FF\u0370-\u03FF\u4e00-\u9fff\u0600-\u06FF\u0590-\u05FF]', term))

# Non-English vocabulary (common foreign words for dental)
FOREIGN_WORDS = {'clinica','clinique','dentista','zahnarzt','zahn','zahnbrücke',
                 'fogorvos','dantistai','stomatologia','dantu','zębów','zębowe','zeba',
                 'zęba','zebowe','implanty','impianto','implanturi','implante',
                 'dentaire','dentales','odontologia','prothese','londra',
                 'londres','londone','londonban','londyn','fogaszat',
                 'tanam','gigi','harga','terdekat','stratforde','stomatologic',
                 'klinika','paradantoze','fogbeültetés','klinik',
                 'proximité','dentystyczne','dentysta','cena','koszt',
                 'pret','prix','preco','costo','prezzo','gdzie','najlepiej','zrobic',
                 'zeby','desmineralizacion','puente','zirconio','piezas','regeneracion',
                 'osea','recuperar','dientes','melhor','preço','anglia'}

def classify(term):
    # Non-ASCII = foreign language = block
    if is_foreign_script(term):
        return True
    words = re.findall(r"[a-z0-9'&/-]+", term.lower())
    if not words:
        return True
    wset = set(words)
    wc = len(words)
    raw = term.lower()

    # Foreign language words
    if any(w in wset for w in FOREIGN_WORDS):
        return True

    # Hard blocks
    if any(w in wset for w in ABROAD):
        return True
    if any(w in wset for w in CHEAP_NHS):
        return True
    if any(w in wset for w in DENTURE_WORDS) or 'false teeth' in raw or 'fake teeth' in raw:
        return True
    if any(w in wset for w in NON_DBD) or 'bone graft' in raw or 'gum disease' in raw or \
       'gum graft' in raw or 'root canal' in raw or 'sinus lift' in raw or \
       'oral surgeon' in raw or 'oral surgery' in raw or 'hair transplant' in raw or \
       'hollywood smile' in raw or 'mobile dentist' in raw or 'snap on smile' in raw or \
       'snap-on smile' in raw:
        return True
    if any(w in wset for w in BRAND_RESEARCH):
        return True
    # NHS-style phrases
    if any(p in raw for p in NHS_PHRASES):
        return True

    has_london = any(w in wset for w in LONDON) or 'london' in raw
    if any(w in wset for w in UK_OUTSIDE) and not has_london:
        return True
    if re.match(r'^(dr|mr|mrs|ms|miss)\s', raw):
        return True

    # Over-vague single words — expanded
    if wc == 1 and words[0] in {'teeth','tooth','smile','smiles','dentistry',
                                  'implant','implants','dental','oral','dentist',
                                  'dentists','veneer','veneers','veneera','crown',
                                  'crowns','bridge','bridges','denture','dentures',
                                  'invisalign','braces','brace'}:
        return True

    # Allowlist check
    ALL = SERVICES | GENERIC | LONDON
    unknown_words = [w for w in words if w not in ALL and not w.isdigit() and w not in {"'", "&", "/", "-"}]
    for uw in unknown_words[:]:
        if re.match(r'^[a-z]*\d+[a-z]*$', uw):
            unknown_words.remove(uw)
    if unknown_words:
        return True

    # Brand compound patterns
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
    if 'harley street' in raw or 'harley st' in raw:
        return True

    # Compound 1-word brand patterns (ends in various brand-marker suffixes)
    if wc == 1:
        w = words[0]
        if w not in SERVICES:
            brand_suffixes = ('dental','dentist','dentistry','smiles','smile','dent',
                              'teeth','tooth','implant','implants','clinic','club',
                              'house','hub','works','care','lab','pro','spa','co')
            for suf in brand_suffixes:
                if w.endswith(suf) and w != suf and len(w) > len(suf):
                    if 'dentalbydesign' not in raw:
                        return True
    return False

results = {'1_word':[], '2_word':[], '3_word':[], '4_word':[], '5plus_word':[]}
for _, r in agg.iterrows():
    term = r['Search term']
    if classify(term):
        wc = len(term.split())
        key = f'{wc}_word' if wc <= 4 else '5plus_word'
        results[key].append(term)

# DBD substring safety net
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
]
def is_dbd(term):
    return any(s in term for s in dbd_substrings)

for k in results:
    results[k] = [t for t in results[k] if not is_dbd(t)]

# Dedupe against all priors (including today's Apr 15-16 first-pass additions)
prior_all = {'1_word':set(),'2_word':set(),'3_word':set(),'4_word':set(),'5plus_word':set()}
for pf in ['_apr13_clean_diff.txt','_apr13_final.txt','_apr14_FINAL.txt',
           '_apr14_2nd_FINAL.txt','_apr15_16_final.txt']:
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

new_by_cat = {}
for k in results:
    new_by_cat[k] = [t for t in results[k] if t not in prior_all[k]]

with open('_apr15_16_v2.txt','w',encoding='utf-8') as f:
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
