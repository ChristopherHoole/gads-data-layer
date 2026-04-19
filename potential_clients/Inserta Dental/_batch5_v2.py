import sys, io, pandas as pd, warnings, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings('ignore')
D = r'data/Search terms'
st = pd.read_csv(f'{D}/Search terms last 60 days.csv', skiprows=2, thousands=',')
st = st[~st['Search term'].astype(str).str.startswith('Total') & st['Search term'].notna()].copy()
st['Search term'] = st['Search term'].astype(str).str.lower().str.strip()
agg = st.groupby('Search term').agg({'Cost':'sum','Conversions':'sum'}).reset_index()
agg['wc'] = agg['Search term'].str.split().str.len()
three = agg[agg['wc']==3].copy()
tier5 = three[(three['Conversions']==0) & (three['Cost']>=1) & (three['Cost']<3)].sort_values('Cost', ascending=False).copy()

# Greater London boroughs / areas - KEEP (but strip out contexts)
london_areas = set("""
hammersmith chiswick fulham kensington chelsea westminster mayfair marylebone
camden islington hackney shoreditch bermondsey brixton clapham putney
wandsworth battersea wimbledon balham streatham tooting earlsfield mitcham
sutton croydon bromley lewisham greenwich woolwich bexleyheath bexley
dartford erith catford forest_hill sydenham dulwich peckham deptford
rotherhithe stratford leyton walthamstow chingford edmonton enfield barnet
finchley hendon harrow ruislip uxbridge hillingdon hayes southall ealing
acton shepherds_bush hanwell greenford perivale wembley kilburn willesden
cricklewood golders_green muswell_hill hornsey tottenham haringey highgate
archway holloway kentish_town pimlico bayswater paddington notting_hill
knightsbridge belgravia soho bloomsbury covent_garden holborn barbican
clerkenwell aldgate whitechapel mile_end bow stepney bethnal_green
stoke_newington dalston hoxton wapping limehouse poplar barking dagenham
romford ilford redbridge wanstead havering upminster hornchurch rainham
kingston richmond teddington twickenham hampton feltham hounslow brentford
isleworth heston cranford colindale neasden mill_hill whetstone southgate
palmers_green winchmore_hill crouch_end harlesden wealdstone stanmore
edgware canons_park burnt_oak colliers_wood morden worcester_park new_malden
surbiton tolworth thames_ditton beckenham penge anerley thornton_heath
purley coulsdon selhurst crystal_palace mottingham eltham charlton blackheath
plumstead abbey_wood welling sidcup orpington chislehurst elmers_end shirley
addiscombe sanderstead kenley whyteleafe carshalton chessington surbiton
wimbledon wapping sheen kew chadwell_heath walworth
""".replace('_',' ').split())

# Multi-word London areas
london_phrases = {'forest hill','golders green','muswell hill','notting hill','kentish town',
                  'covent garden','shepherds bush','mile end','bethnal green','stoke newington',
                  'chadwell heath','abbey wood','crystal palace','crouch end','colliers wood',
                  'worcester park','new malden','thames ditton','palmers green','winchmore hill',
                  'canons park','burnt oak','mill hill','elmers end','potters bar','hinchley wood',
                  'ponders end','new addington','hackney wick','south woodford',
                  'west london','north london','east london','south london',
                  'harley street','west drayton','south norwood','thornton heath'}

abroad = set("""
turkey turkish poland polish hungary hungarian spain spanish albania albanian
croatia croatian romania romanian bulgaria bulgarian thailand thai india indian
mexico mexican egypt germany german italy italian france french portugal portuguese
dubai uae emirates saudi qatar lebanon europe european abroad switzerland swiss
cyprus armenia armenian moldova moldovan ukraine ukrainian lithuania lithuanian
latvia estonia slovakia slovenia slovenian serbia serbian bosnia czech
istanbul antalya bodrum izmir ankara marmaris warsaw krakow budapest sofia
plovdiv bucharest prague zagreb split ljubljana tirana bangkok phuket
mumbai delhi bangalore chennai cancun cairo dublin cork lisbon porto
barcelona madrid milan rome venice amsterdam berlin munich paris vienna
zurich brussels copenhagen helsinki oslo stockholm manila jakarta lahore
cebu benidorm toronto tijuana casablanca hurghada ghana londra londone
londonban londyn
""".split())

uk_outside = set("""
birmingham manchester liverpool leeds sheffield bristol newcastle nottingham
leicester coventry cardiff belfast glasgow edinburgh aberdeen swansea
oxford cambridge brighton bournemouth portsmouth southampton plymouth norwich
york reading swindon hull stoke derby wolverhampton bath exeter bradford
blackpool preston doncaster sunderland middlesbrough northampton peterborough
gloucester worcester colchester ipswich chester warrington blackburn bolton
burnley carlisle lancaster stockport wigan rotherham barnsley wakefield
huddersfield halifax scunthorpe grimsby lincoln mansfield kettering corby
rugby tamworth burton walsall dudley sandwell solihull redditch kidderminster
telford shrewsbury hereford bangor wrexham newport
inverness stirling perth paisley dundee derry sedgefield nuneaton
surrey sussex kent hampshire essex hertfordshire berkshire oxfordshire
buckinghamshire cambridgeshire bedfordshire norfolk suffolk devon cornwall
dorset somerset wiltshire gloucestershire worcestershire warwickshire
northamptonshire leicestershire nottinghamshire derbyshire staffordshire
shropshire cheshire lancashire yorkshire durham cumbria lincolnshire
scotland wales ireland midlands england britain
camberley chelmsford maidstone guildford woking reigate watford luton
slough basingstoke stevenage welwyn hitchin braintree harlow southend rochester
chatham gillingham tunbridge tonbridge sevenoaks canterbury margate ramsgate
ashford folkestone dover horsham crawley worthing chichester bognor aldershot
farnham farnborough leatherhead dorking redhill gatwick eastbourne hastings
hove lewes windsor eton bedford grantham brentwood dorchester fareham medway
wimborne cobham egham chertsey petersfield weybridge cheshunt hawick
wandsworth clacton beaconsfield bushey borehamwood elstree radlett caterham
loughton epping harrogate stafford magherafelt barnstaple devizes
esher byfleet rochdale stroud pontypridd datchet hook benfleet redruth
cirencester daventry maidenhead ascot
kidbrooke whitstable
""".split())

brand_marker_words = {'clinic','clinics','studio','studios','practice','practices',
                      'centre','center','centres','centers','surgery','surgeries',
                      'house','spa','group','lounge','wellness','aesthetics',
                      'specialists','specialist','suite','emporium','boutique',
                      'gallery','artistry','institute','rooms','office','arts'}

brand_phrases = [
    'dental clinic','dental practice','dental centre','dental center','dental studio',
    'dental surgery','dental house','dental group','dental lounge','dental arts',
    'dental care','dental beauty','dental spa','dental suite','dental emporium',
    'dental office','dental services','dental experts','dental experts',
    'smile clinic','smile studio','smile centre','smile spa','implant centre',
    'implant clinic','co uk','co. uk','dental com','dental reviews','uk reviews',
    'bad reviews','trustpilot','dental photos','dental plc','dental gallery',
    'dental department','dental hospital','pearl dental','truly dental',
    'love teeth','21d','21 dental','dentaprime','evo dental','banning dental',
    'bupa dental','dawood','bond dental','vital europe','kreativ','dentakay',
    'perfect smile','complete smiles','smile solutions','smile savers',
    'smile makers','smile stories','magic smile','hollywood smile','ten dental',
    'whites dental','white dental','acton vale','baker street','park lane',
    'shirland road','thayer street','cannon street','cannon st','hertford road',
    'walworth road','hammersmith road','knightsfield','clocktower','kirby',
    'dove dental','pinn dental','pearl dental','apple dental','eco dent',
    'portman dental','coleman dental','care dental','advance dental','chrome dental',
    'chelsea dental','chelsea green','green dental','blue dental','blue bird',
    'blue pearl','blue care','smile white','true smile','true smiles','new smile',
    'faces & smiles','a r smiles','smile aesthetica','smile aesthetic',
    'genix','ikon dental','aqua dental','nova dental','nova smiles','trinity dental',
    'forma dental','focus dental','eagle brow','siha dental','claradent',
    'cap city','tdc','mcr implant','s3 dental','dentakay','sevil smile',
    'hospident','atrium clinic','sona dental','luna dental','bankview',
    'pristine','aesthetika','waldron','forest ray','queens dental','zen dental',
    'welling dental','sandford bexleyheath','smilecare','smile studios',
    'student dental','barbican dental','imperial dental','stunning smile',
    'harley street','dent1st','care dental','synergy','abbey dental','ark dental',
    'dental lounge','london dental','vivadent','nobel biocare','osstem','straumann',
    'astra','dentium','biomet','neodent','alpha bio','nobel active','nobel teeth',
    'colosseum','dental harmony','dental prime','dental design','design dental',
    'infinity dental','envy smile','unique dental','angel smile','space dental',
    'aliadent','knightsfield','se1 dental','tml smile','1 kings','southgate dental',
    'pinner dental','pinner green','eva dental','brighton implant','cobham abc',
    'abc dental','bupa','simply teeth','billericay','haringey','streatham dental',
    'i smile','junction dental','enfield dental','b dental','banning','dent1st',
    'sensu','impress','impress dental','ivy dentistry','sweet tooth','92 dental',
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
    'smile implant','dental emporium','dental artistry','dental art','jubilee dental',
    'lakeside dental','bupa cosmetic','aviva cosmetic','biomimetic','love teeth',
    'cosmo','beaconsfield dentist','bluebell','anna peterson','e14 9pa','w9 dental',
    'ardent smile','true life','ivory','dentaprime','buckingham gate','holistic',
    'digismile','dct zero','dct dental','advance dental','eco dent','inspire dental',
    'dental excellence','n6 dental','biomimetic','ascot dental','kew dental',
    'kew road','ikon','implantly','implanty','market square','crowborough',
    'chrysanth','infident','simplyteeth','islington beauty','islington dental',
    'dental beauty','harley st','chadwell heath','abbey wood dental','chadwell',
    'walworth','guys dental','ucl implant','face & smiles',
]

denture_patterns = {'denture','dentures','false teeth','false tooth','fake teeth','fake tooth',
                    'flipper','clips','overdenture','partial denture','dental plate',
                    'snap in','snap on','clip in','clip on','plastic teeth','acrylic teeth',
                    'bolt in','bolted in','screw in teeth','ivoclar'}
cheap_nhs = {'cheap','cheapest','cheaper','affordable','groupon','wowcher','free','grants','grant',
             'nhs','budget','inexpensive','low cost','lowcost','benefits','pensioner'}
non_dbd = {'extraction','extractions','root canal','filling','fillings','whitening',
           'gum disease','gum graft','gum grafting','gum restoration','gum recession',
           'receding gums','hair transplant','hair implants','periodontal','periodontitis',
           'orthognathic','hearing aids','braces for','decay','tooth decay','cleaning'}
price_brand_research = {'straumann','osstem','astra','dentium','biomet','neodent','alpha bio',
                        'nobel active','nobel teeth','nobel biocare','ivoclar','zirconium',
                        'porcelain dental implants','basal','ceramic','zirconia','subperiosteal',
                        'dentsply','sirona','southern implants','mini implant','mini dental'}

blocks = {'competitor': [], 'named_dr': [], 'abroad': [], 'wrong_uk': [],
          'denture': [], 'cheap_nhs': [], 'non_dbd': [], 'brand_research': [],
          'keep': []}

for _, r in tier5.iterrows():
    term = r['Search term']
    cost = r['Cost']
    words = term.split()
    wset = set(words)
    raw = term

    # Check if London mentioned - protects from wrong-location block
    has_london = 'london' in wset or any(la in wset for la in london_areas) or \
                 any(lp in raw for lp in london_phrases)

    # Named dentist
    if re.match(r'^dr\s+', raw) or re.search(r'\bdr\s+[a-z]+\s+[a-z]+', raw) or \
       re.search(r'\b(dentist|dr)\b.*\b(dentist|dr)\b', raw) and any(k in raw for k in ['dr ','mr ']):
        blocks['named_dr'].append((term, cost)); continue
    # Named dentist - two words before "dentist"
    m = re.match(r'^([a-z]+)\s+([a-z]+)\s+dentist$', raw)
    if m and m.group(1) not in ['the','best','cheap','good','local','private','nhs','emergency','cosmetic','family','kids','children','my','your','a','an']:
        blocks['named_dr'].append((term, cost)); continue

    # Non-DBD service
    if any(w in raw for w in non_dbd):
        blocks['non_dbd'].append((term, cost)); continue

    # Cheap/NHS/free (word match)
    if any(w in wset for w in cheap_nhs):
        blocks['cheap_nhs'].append((term, cost)); continue

    # Denture
    if any(w in raw for w in denture_patterns):
        blocks['denture'].append((term, cost)); continue

    # Brand research (Straumann etc. without London context)
    if any(b in raw for b in price_brand_research):
        blocks['brand_research'].append((term, cost)); continue

    # Abroad
    if any(w in wset for w in abroad):
        blocks['abroad'].append((term, cost)); continue

    # Wrong UK outside London
    if any(w in wset for w in uk_outside) and not has_london:
        blocks['wrong_uk'].append((term, cost)); continue

    # Competitor brand phrase match
    is_brand = any(bp in raw for bp in brand_phrases)
    # Protect DBD identity terms
    if 'dental by design' in raw: is_brand = False
    if is_brand:
        blocks['competitor'].append((term, cost)); continue

    blocks['keep'].append((term, cost))

# Output
with open('_batch5_out.txt','w',encoding='utf-8') as f:
    for cat in ['competitor','named_dr','abroad','wrong_uk','denture','cheap_nhs','non_dbd','brand_research','keep']:
        items = blocks[cat]
        total = sum(c for _,c in items)
        f.write(f"\n=== {cat.upper()}: {len(items)} terms, L{total:.0f} ===\n")
        for term, cost in items:
            f.write(f"  [{term}]  L{cost:.2f}\n")

# Print summary
for cat in ['competitor','named_dr','abroad','wrong_uk','denture','cheap_nhs','non_dbd','brand_research','keep']:
    items = blocks[cat]
    total = sum(c for _,c in items)
    print(f"{cat.upper():<20} {len(items):>5} terms, L{total:>6.0f}")
