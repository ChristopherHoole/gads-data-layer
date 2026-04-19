import sys, io, pandas as pd, warnings, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings('ignore')
D = r'data/Search terms'
st = pd.read_csv(f'{D}/Search terms last 60 days.csv', skiprows=2, thousands=',')
st = st[~st['Search term'].astype(str).str.startswith('Total') & st['Search term'].notna()].copy()
st['Search term'] = st['Search term'].astype(str).str.lower().str.strip()
agg = st.groupby('Search term').agg({'Cost':'sum','Conversions':'sum'}).reset_index()

uk_outside_london = [
    'birmingham','manchester','liverpool','leeds','sheffield','bristol','newcastle','nottingham',
    'leicester','coventry','cardiff','belfast','glasgow','edinburgh','aberdeen','dundee','swansea',
    'oxford','cambridge','brighton','bournemouth','portsmouth','southampton','plymouth','norwich',
    'york','reading','swindon','hull','stoke','derby','wolverhampton','bath','exeter','bradford',
    'blackpool','preston','doncaster','sunderland','middlesbrough','northampton','peterborough',
    'gloucester','worcester','colchester','ipswich','chester','warrington','blackburn','bolton',
    'burnley','carlisle','lancaster','salford','stockport','wigan','rotherham','barnsley',
    'wakefield','huddersfield','halifax','scunthorpe','grimsby','lincoln','mansfield',
    'kettering','corby','rugby','tamworth','burton','walsall','dudley','sandwell','solihull',
    'redditch','kidderminster','stourbridge','telford','shrewsbury','hereford','bangor','wrexham',
    'newport','merthyr','barry','caerphilly','neath','llanelli','rhyl','inverness','stirling',
    'perth','paisley','kilmarnock','ayr','greenock','motherwell','hamilton','dunfermline',
    'kirkcaldy','livingston','falkirk','bracknell',
    'surrey','sussex','kent','hampshire','essex','hertfordshire','berkshire','oxfordshire',
    'buckinghamshire','cambridgeshire','bedfordshire','middlesex','norfolk','suffolk','devon',
    'cornwall','dorset','somerset','wiltshire','gloucestershire','worcestershire','warwickshire',
    'northamptonshire','leicestershire','nottinghamshire','derbyshire','staffordshire','shropshire',
    'cheshire','lancashire','yorkshire','durham','northumberland','cumbria','lincolnshire',
    'rutland','merseyside','staffs','yorks','lancs','notts','bucks','herts','berks','hants',
    'scotland','wales','ireland','midlands',
    'camberley','dartford','chelmsford','maidstone','guildford','woking','reigate','watford',
    'luton','slough','basingstoke','milton','keynes','stevenage','welwyn','hitchin','hemel',
    'hempstead','braintree','harlow','southend','rochester','chatham','gillingham','tunbridge',
    'tonbridge','sevenoaks','canterbury','margate','ramsgate','ashford','folkestone','dover',
    'horsham','crawley','worthing','chichester','bognor','aldershot','farnham','farnborough',
    'epsom','leatherhead','dorking','redhill','gatwick','eastbourne','hastings','hove','lewes',
    'potters','borehamwood','elstree','radlett','bushey',
]

abroad = [
    'turkey','poland','hungary','spain','portugal','germany','france','italy','netherlands',
    'belgium','austria','switzerland','czech','slovakia','slovenia','croatia','serbia','bosnia',
    'romania','bulgaria','greece','albania','macedonia','montenegro','moldova','ukraine',
    'belarus','russia','finland','sweden','norway','denmark','iceland','estonia','latvia',
    'lithuania','dubai','uae','emirates','qatar','bahrain','saudi','india','pakistan',
    'bangladesh','thailand','vietnam','cambodia','indonesia','malaysia','singapore','philippines',
    'china','japan','korea','taiwan','mexico','cuba','brazil','argentina','chile',
    'colombia','peru','venezuela','ecuador','morocco','tunisia','egypt','kenya','nigeria',
    'africa','canada','australia','usa','europe','asia','abroad',
    'istanbul','ankara','izmir','antalya','bodrum','marmaris','kusadasi',
    'warsaw','krakow','gdansk','wroclaw','poznan',
    'budapest','debrecen','szeged',
    'madrid','barcelona','valencia','seville','malaga','alicante','marbella',
    'berlin','munich','frankfurt','hamburg','cologne','dusseldorf',
    'paris','lyon','marseille','nice','bordeaux',
    'rome','milan','naples','turin','venice','florence',
    'amsterdam','rotterdam','hague',
    'sofia','plovdiv','varna','burgas',
    'bucharest','cluj','brasov',
    'prague','brno',
    'zagreb','split','dubrovnik','rijeka','pula',
    'ljubljana','maribor',
    'tirana','durres',
    'athens','thessaloniki',
    'lisbon','porto','faro',
    'bangkok','phuket','pattaya','krabi',
    'mumbai','delhi','bangalore','chennai','hyderabad','kolkata','pune','ahmedabad','jaipur','goa',
    'cancun','tijuana','guadalajara',
    'cairo','alexandria','hurghada',
    'casablanca','marrakech',
    'dublin','cork','galway',
    'vienna','salzburg',
    'zurich','geneva','basel',
    'brussels','antwerp',
    'copenhagen','stockholm','helsinki','oslo',
    'sharjah','doha','riyadh','jeddah',
]

all_locs = sorted(set(uk_outside_london + abroad))
hits = []
for loc in all_locs:
    mask = agg['Search term'].str.contains(rf'\b{re.escape(loc)}\b', regex=True, na=False)
    m = agg[mask]
    if len(m)==0: continue
    cost = m['Cost'].sum()
    conv = m['Conversions'].sum()
    if cost < 3: continue
    hits.append((loc, cost, conv))

hits.sort(key=lambda x: -x[1])
print(f"{'Location':<20} {'Spend':>8} {'Conv':>5}")
print('-' * 40)
for loc, cost, conv in hits:
    print(f"{loc:<20} L{cost:>6,.0f} {conv:>5.0f}")
print(f"\nTOTAL locations with spend >= L3: {len(hits)}")
