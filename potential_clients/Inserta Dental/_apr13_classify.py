import sys, io, pandas as pd, warnings, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings('ignore')

df = pd.read_csv('data/Search terms/Search terms report 13-4-26.csv', skiprows=2, thousands=',')
df = df[~df['Search term'].astype(str).str.startswith('Total') & df['Search term'].notna()].copy()
df['Search term'] = df['Search term'].astype(str).str.lower().str.strip()
# Dedupe
agg = df.groupby('Search term').agg({'Cost':'sum','Conversions':'sum'}).reset_index()
print(f'Total unique terms: {len(agg)}')

# Greater London / London-related terms - KEEP
extra_london = set('wallington belsize parsons friern raynes charing stepney brixton'.split())
london_words = extra_london | set("""
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
walworth chadwell catford welling sidcup dartford
""".split())

london_phrases = [
    'forest hill','golders green','muswell hill','notting hill','kentish town',
    'covent garden','shepherds bush','mile end','bethnal green','stoke newington',
    'chadwell heath','abbey wood','crystal palace','crouch end','colliers wood',
    'worcester park','new malden','thames ditton','palmers green','winchmore hill',
    'canons park','burnt oak','mill hill','elmers end','ponders end',
    'new addington','hackney wick','south woodford','harley street','west drayton',
    'thornton heath','south norwood','moor park','west kensington','earls court',
    'north finchley','east finchley','west london','north london','east london',
    'south london','south east london','south west london','north west london',
]

abroad = set("""
turkey turkish poland polish hungary hungarian spain spanish albania albanian
croatia croatian romania romanian bulgaria bulgarian thailand thai india indian
mexico mexican germany german italy italian france french portugal portuguese
dubai uae emirates saudi qatar europe european abroad switzerland swiss
cyprus cypriot ukrainian ukraine lithuanian lithuania latvia estonia slovakia
slovenia slovenian serbia serbian bosnia czech greek greece
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
telford shrewsbury hereford bangor wrexham newport
inverness stirling perth paisley derry sedgefield nuneaton harrogate rochdale
surrey sussex kent hampshire essex hertfordshire berkshire oxfordshire
buckinghamshire cambridgeshire bedfordshire norfolk suffolk devon cornwall
dorset somerset wiltshire gloucestershire worcestershire warwickshire
northamptonshire leicestershire nottinghamshire derbyshire staffordshire
shropshire cheshire lancashire yorkshire durham cumbria lincolnshire
scotland wales midlands england britain merseyside
camberley chelmsford maidstone guildford woking reigate watford luton
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
whitehaven bridgwater oldham hertford molesey walton staines bagshot bexley
bedfont bedfordshire southwark
""".split())

# DBD's own neighborhood - keep
dbd_location = {'hammersmith','ravenscourt','shepherds','bush','chiswick'}

brand_phrases = [
    'dental clinic','dental practice','dental centre','dental center','dental studio',
    'dental surgery','dental house','dental group','dental lounge','dental arts',
    'dental care','dental beauty','dental spa','dental suite','dental emporium',
    'dental office','dental services','dental experts','dental hospital','dental harmony',
    'dental design','design dental','dental art','dental artistry','dental insurance',
    'dental aesthetics','dental prime','dental implants bupa','smile clinic',
    'smile studio','smile centre','smile spa','smile aesthetica','smile clinique',
    'implant centre','implant clinic',
    'co uk','co. uk','dental com','trustpilot','bad reviews','uk reviews',
    'dentakay','dentaprime','evo dental','banning dental','bupa dental',
    'dawood','bond dental','vital europe','kreativ','mds dental','pearl dental',
    'perfect smile','complete smiles','smile solutions','smile savers','smile makers',
    'smile stories','magic smile','hollywood smile','ten dental','whites dental',
    'white dental','baker street','park lane','park dental','shirland road',
    'thayer street','cannon street','cannon st','hertford road','walworth road',
    'hammersmith road','knightsfield','clocktower','kirby','dove dental','pinn dental',
    'apple dental','eco dent','portman dental','coleman dental','care dental',
    'advance dental','chrome dental','chelsea dental','chelsea green','green dental',
    'blue dental','blue bird','blue pearl','blue care','smile white','true smile',
    'true smiles','new smile','faces & smiles','smile aesthetica','smile aesthetic',
    'genix','ikon dental','aqua dental','nova dental','nova smiles','trinity dental',
    'forma dental','focus dental','eagle brow','siha dental','claradent',
    'cap city','tdc','mcr implant','s3 dental','sevil smile',
    'hospident','atrium clinic','sona dental','luna dental','bankview',
    'pristine','aesthetika','waldron','forest ray','queens dental','zen dental',
    'welling dental','sandford','smilecare','smile studios','student dental',
    'barbican dental','imperial dental','stunning smile','harley street','dent1st',
    'synergy','abbey dental','ark dental','london dental','vivadent',
    'nobel biocare','osstem','straumann','astra','dentium','biomet','neodent',
    'alpha bio','nobel active','nobel teeth','colosseum','dental harmony',
    'envy smile','unique dental','angel smile','space dental','aliadent','se1 dental',
    'tml smile','1 kings','southgate dental','pinner dental','pinner green','eva dental',
    'brighton implant','cobham abc','abc dental','bupa','simply teeth','billericay',
    'haringey','streatham dental','i smile','junction dental','enfield dental',
    'b dental','banning','sensu','impress','ivy dentistry','sweet tooth','92 dental',
    'implanty','impianto','implant masea','74 harley','75 harley','90 harley',
    '94 harley','139 harley','tdc harley','thousand smiles','kit spears',
    'andrew dawood','satinder dhami','justin glaister','paul niland','ian seddon',
    'anna peterson','joe oliver','rupert young','frances carling','joe bansal',
    'kavit shah','alberto lopez','king george','dr vittorio','dr oliver',
    'dr ahmed','dr sal','dr parrish','dr sethi','dr brar','dr adeel','dr tidu',
    'dr priscila','bruno silva','muntazir ali','dipan shah','emanuele clozza',
    'gurs sehmi','graham tinkler','simon blank','affan saghir','robbie hughes',
    'kyle stanley','ucl implant','cosmo dentist','refresh dental','kreate dental',
    'revived smiles','optimal dental','pure elegant','pure smile','puresmile',
    'smile implant','jubilee dental','lakeside dental','bupa cosmetic',
    'aviva cosmetic','biomimetic','love teeth','beaconsfield dentist','bluebell',
    'ardent smile','true life','ivory','buckingham gate','holistic','digismile',
    'dct zero','dct dental','inspire dental','dental excellence','n6 dental',
    'ascot dental','kew dental','kew road','implantly','market square',
    'crowborough','chrysanth','infident','simplyteeth','islington beauty',
    'islington dental','harley st','chadwell','abbey wood dental','guys dental',
    'face & smiles','coco dental','nuvia','dream smile','tooth club','gentle dental',
    'halo dental','denta clinic','alma smiles','royal wharf','smile well',
    'putney hill','keppel','aura dental','figges marsh','nur smiles','canon house',
    'new river','chalton street','silicon dental','finn dental','mindful dentist',
    'the complete smile','the wimbledon','crossways','precision dental','almas dental',
    'bryer wallace','kinston','dental estetik','camlog','mono implant','emax crowns',
    'titanium dental implant','hybrid teeth','mini teeth','zygomatic implants',
    'mayo clinic teeth','haynes dental','cedars dental','dunstable','dentique',
    'hockerill','abney','knightshill','bright dental','bermondsey dental','hersham',
    'queens park dental','katherine dental','kingsbury dental','kilburn dental',
    'belmont park dental','maldent','beam dental','bright smile','lama dental',
    'uk dental practices','dentafly','solutions dental','leigh dental','overcliffe',
    'lema dental','hanwell dental','vitaleurope','staines dental','tlc dental',
    'lim dental','cedars','angel dental','oraldent','malpas','iver dental',
    'mortlake','ap dental','sbc dental','vitruvian','dente dental','better dental',
    'tnc smile','abacus','perfect smile','ko dental','elite dental','pembury',
    'miswak','epsom dental','kingston dental','swedish smile','ivory dental',
    'overcliffe','vidadent','fitze','danbury','adel dental','bupa dental','cricklewood',
    'pearl dental','evo dental','excel dental','favero','salisbury implant',
    'brown','brigstock','damira','bristol dental','gm dental','dee dental','rit dental',
    'sync dental','perlan','stradbrook','sevenoaks dental','n7 dental','sophia dental',
    'sodc','sonria','regency','platinum dental','serenity','ilford dental','wallington',
    'lakeside','confidental','willesden','lodge dental','oraldent','walthamstow dental',
    'wapping dental','woolwich dental','newham','beaufort','sardinia','nabil','mint dental',
    'greenwich dental','olsens','bayswater dental','m&m dental','pura dental','w9 dental',
    'dental spa','forest dental','royal dental','kensington dental','haynes',
]

# Named dentist check (regex)
named_dr_re = re.compile(r'\bdr\s+[a-z]+\s+[a-z]+')
# Two-word name + dentist
named_dentist_re = re.compile(r'^([a-z]+)\s+([a-z]+)\s+dentist\b')
generic_prefix = {'the','best','cheap','good','local','private','nhs','emergency',
                  'cosmetic','family','kids','children','my','your','a','an','find',
                  'new','top','free','affordable','budget','uk','london','near'}

denture_words = {'denture','dentures','false teeth','false tooth','fake teeth','fake tooth',
                 'flipper','overdenture','partial denture','dental plate','dental plates',
                 'snap in','snap on','snap fit','clip in','clip on','plastic teeth',
                 'acrylic teeth','bolt in','bolted in','screw in teeth','ivoclar',
                 'set of teeth','silicone dentures','valplast','plateless','removable teeth',
                 'palateless','soft dentures'}
cheap_nhs = {'cheap','cheapest','cheaper','affordable','groupon','wowcher','free','grants','grant',
             'nhs','budget','inexpensive','pensioner','pensioners'}
non_dbd = {'extraction','extractions','root canal','filling','fillings','whitening',
           'gum disease','gum graft','gum grafting','gum restoration','gum recession',
           'receding gums','hair transplant','hair implants','periodontal','periodontitis',
           'orthognathic','hearing aids','decay','tooth decay','ozone therapy',
           'maxillofacial'}
brand_research = {'straumann','osstem','astra','dentium','biomet','neodent','alpha bio',
                  'nobel active','nobel teeth','nobel biocare','ivoclar','camlog',
                  'subperiosteal','mini implant','mini dental','basal','ceramic',
                  'zirconia','zirconium','emax','swiss implant','sirona','dentsply'}

blocks = {'1_word':[], '2_word':[], '3_word':[], '4_word':[], '5plus_word':[]}

for _, r in agg.iterrows():
    term = r['Search term']
    cost = r['Cost']
    words = term.split()
    wc = len(words)
    wset = set(words)
    raw = term

    has_london = 'london' in wset or any(w in wset for w in london_words) or any(lp in raw for lp in london_phrases)
    # Even if London, wrong-intent can still be blocked

    block = False
    reason = ''

    # Non-DBD service
    if any(w in raw for w in non_dbd):
        block = True; reason = 'non_dbd'
    # Denture
    elif any(w in raw for w in denture_words):
        block = True; reason = 'denture'
    # Cheap / NHS / free
    elif any(w in wset for w in cheap_nhs):
        block = True; reason = 'cheap_nhs'
    # Abroad
    elif any(w in wset for w in abroad):
        block = True; reason = 'abroad'
    # Brand research
    elif any(b in raw for b in brand_research):
        block = True; reason = 'brand_research'
    # Wrong UK (no London)
    elif any(w in wset for w in uk_outside) and not has_london:
        block = True; reason = 'wrong_uk'
    # Named dentist
    elif named_dr_re.search(raw):
        block = True; reason = 'named_dr'
    # (Removed overly-broad "X Y dentist" regex — false-positive on location names)
    # Competitor brand phrase
    else:
        for bp in brand_phrases:
            if bp in raw and 'dental by design' not in raw:
                block = True; reason = 'competitor'
                break

    if block:
        key = f'{wc}_word' if wc <= 4 else '5plus_word'
        blocks[key].append((term, cost, reason))

for k, items in blocks.items():
    print(f'{k}: {len(items)} terms')

# Save to file
with open('_apr13_blocks.txt','w',encoding='utf-8') as f:
    for key in ['1_word','2_word','3_word','4_word','5plus_word']:
        f.write(f'\n### {key} ({len(blocks[key])}) ###\n')
        for term, cost, reason in blocks[key]:
            f.write(f'[{term}]\n')
