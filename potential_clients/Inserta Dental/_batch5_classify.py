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

# Greater London boroughs & common areas (KEEP these locations)
london = set("""
london hammersmith chiswick fulham kensington chelsea westminster mayfair
marylebone camden islington hackney shoreditch bermondsey brixton clapham
putney wandsworth battersea wimbledon balham streatham tooting earlsfield
mitcham sutton croydon bromley lewisham greenwich woolwich bexleyheath
bexley dartford erith catford forest hill sydenham dulwich peckham
deptford rotherhithe canary wharf stratford leyton walthamstow
chingford edmonton enfield barnet finchley hendon harrow ruislip
uxbridge hillingdon hayes southall ealing acton shepherds bush hanwell
greenford perivale wembley kilburn willesden cricklewood golders green
muswell hill hornsey tottenham haringey highgate archway holloway kentish
pimlico bayswater paddington notting hill knightsbridge belgravia soho
bloomsbury covent garden holborn barbican clerkenwell aldgate whitechapel
mile end bow stepney bethnal green stoke newington dalston hoxton
wapping limehouse poplar barking dagenham romford ilford redbridge
wanstead havering upminster hornchurch rainham kingston richmond
teddington twickenham hampton feltham hounslow brentford isleworth
heston cranford colindale neasden mill hill whetstone southgate
palmers green winchmore hill crouch end harlesden wealdstone stanmore
edgware canons park burnt oak colliers wood morden worcester park
new malden surbiton epsom tolworth thames ditton hinchley wood
beckenham penge anerley thornton heath purley coulsdon selhurst
crystal palace mottingham eltham charlton blackheath plumstead abbey wood
erith belvedere welling sidcup orpington chislehurst elmers end shirley
addiscombe sanderstead kenley whyteleafe nw1 se1 n21 e1 e14 e17
west london north london east london south london south east london south west london
""".split())

abroad = set("""
turkey turkish poland polish hungary hungarian spain spanish albania albanian
croatia croatian romania romanian bulgaria bulgarian thailand thai india indian
mexico mexican egypt germany german italy italian france french portugal portuguese
dubai uae emirates saudi qatar lebanon europe european abroad
istanbul antalya bodrum izmir ankara marmaris warsaw krakow budapest sofia
plovdiv bucharest prague zagreb split ljubljana tirana bangkok phuket
mumbai delhi bangalore chennai cancun cairo dublin cork lisbon porto
barcelona madrid milan rome venice amsterdam berlin munich paris vienna
zurich brussels copenhagen helsinki oslo dublin stockholm
ghana manila jakarta lahore
""".split())

uk_outside_london = set("""
birmingham manchester liverpool leeds sheffield bristol newcastle nottingham
leicester coventry cardiff belfast glasgow edinburgh aberdeen swansea
oxford cambridge brighton bournemouth portsmouth southampton plymouth norwich
york reading swindon hull stoke derby wolverhampton bath exeter bradford
blackpool preston doncaster sunderland middlesbrough northampton peterborough
gloucester worcester colchester ipswich chester warrington blackburn bolton
burnley carlisle lancaster stockport wigan rotherham barnsley wakefield
huddersfield halifax scunthorpe grimsby lincoln mansfield kettering corby
rugby tamworth burton walsall dudley sandwell solihull redditch kidderminster
telford shrewsbury hereford bangor wrexham newport cardiff swansea
inverness stirling perth paisley dundee
surrey sussex kent hampshire essex hertfordshire berkshire oxfordshire
buckinghamshire cambridgeshire bedfordshire norfolk suffolk devon cornwall
dorset somerset wiltshire gloucestershire worcestershire warwickshire
northamptonshire leicestershire nottinghamshire derbyshire staffordshire
shropshire cheshire lancashire yorkshire durham cumbria lincolnshire
scotland wales ireland cornwall midlands england
camberley dartford chelmsford maidstone guildford woking reigate watford
luton slough basingstoke milton keynes stevenage welwyn hitchin hemel
hempstead braintree harlow southend rochester chatham gillingham tunbridge
tonbridge sevenoaks canterbury margate ramsgate ashford folkestone dover
horsham crawley worthing chichester bognor aldershot farnham farnborough
leatherhead dorking redhill gatwick eastbourne hastings hove lewes
windsor eton bedford grantham brentwood dorchester fareham medway
wimborne cobham egham chertsey petersfield weybridge cheshunt hawick
wandsworth clacton beaconsfield bushey borehamwood potters bar elstree
radlett caterham chislehurst loughton epping harrogate harrogate
stafford bedford lincoln magherafelt barnstaple devizes wimborne
derby esher byfleet ipswich byfleet stockport halifax carmarthen
norfolk northampton wigan wiltshire dorset coventry carlisle
coulsdon
""".split())

# Competitor brand patterns (contains these + clinic-like words)
brand_markers = {
    'clinic','studio','practice','centre','center','surgery','house','spa',
    'group','lounge','wellness','aesthetics','specialists','specialist',
    'implant centre','dental care','dental beauty','uk reviews','trustpilot'
}
# Signals of buying intent
buying = {
    'cost','costs','price','prices','pricing','finance','financing','payment','pay monthly',
    'near me','how much','quote','book','consultation','specialist','private'
}
# Denture/fake signals
denture_words = {'denture','dentures','false teeth','false tooth','fake teeth','fake tooth',
                 'flipper','clips','clip on','clip in','overdenture','partial dentures',
                 'plates','plate','snap in'}
# Cheap / NHS / free
cheap_nhs = {'cheap','cheapest','cheaper','affordable','groupon','wowcher','free','grants','grant',
             'nhs','budget','inexpensive'}
# Non-DBD services
non_dbd = {'extraction','root canal','filling','fillings','whitening','gum disease','gum graft',
           'gum grafting','hair transplant','hair implants','periodontal','periodontitis',
           'orthognathic'}

blocks = {'competitor': [], 'named_dr': [], 'abroad': [], 'wrong_uk': [],
          'denture': [], 'cheap_nhs': [], 'non_dbd': [], 'keep': []}

for _, r in tier5.iterrows():
    term = r['Search term']
    cost = r['Cost']
    words = set(term.split())
    raw = term

    # Named dentist
    if raw.startswith('dr ') or raw.startswith('mr ') or raw.startswith('dr.') or ' dentist' in raw and any(raw.startswith(p) for p in ['dr ','mr ']):
        blocks['named_dr'].append((term, cost)); continue
    # Check dr. pattern anywhere
    if re.search(r'\bdr\s+[a-z]+\s+[a-z]+', raw) or re.search(r'\bdr\s+[a-z]+\s+dentist', raw):
        blocks['named_dr'].append((term, cost)); continue

    # Non-DBD service
    if any(w in raw for w in non_dbd):
        blocks['non_dbd'].append((term, cost)); continue

    # Cheap/NHS/free
    if any(w in words for w in cheap_nhs) or any(phrase in raw for phrase in ['cheap ','cheapest','affordable','groupon','wowcher','nhs ']):
        blocks['cheap_nhs'].append((term, cost)); continue

    # Denture intent
    if any(w in raw for w in denture_words):
        blocks['denture'].append((term, cost)); continue

    # Abroad
    if any(w in words for w in abroad):
        blocks['abroad'].append((term, cost)); continue

    # Wrong UK location (must not also be London)
    has_london = any(w in words for w in london) or any(phrase in raw for phrase in london if ' ' in phrase)
    has_uk_outside = any(w in words for w in uk_outside_london)
    if has_uk_outside and not has_london:
        blocks['wrong_uk'].append((term, cost)); continue
    # Handle multi-word UK locations
    for loc in ['milton keynes','potters bar','hemel hempstead','milton keynes','west london','north london','east london','south london']:
        if loc in raw:
            if loc in ['west london','north london','east london','south london']:
                # London - keep
                pass
            else:
                if not has_london:
                    blocks['wrong_uk'].append((term, cost))
                    break
    else:
        # Competitor brand detection (3-word term with brand marker + non-London word)
        has_brand = any(w in words for w in brand_markers) or any(p in raw for p in ['dental studio','dental clinic','dental practice','dental centre','dental center','dental surgery','dental house','dental spa','dental group','dental lounge','implant centre','smile studio','smile clinic','smile centre','dental beauty','dental care','dental specialists'])
        # If has brand marker AND not a DBD-identity term (hammersmith related)
        is_dbd_location = 'hammersmith' in raw
        if has_brand and not is_dbd_location:
            blocks['competitor'].append((term, cost))
        else:
            blocks['keep'].append((term, cost))

for cat in ['competitor','named_dr','abroad','wrong_uk','denture','cheap_nhs','non_dbd','keep']:
    items = blocks[cat]
    total = sum(c for _,c in items)
    print(f"\n=== {cat.upper()}: {len(items)} terms, L{total:.0f} ===")
    for term, cost in items[:500]:
        print(f"  [{term}]  L{cost:.2f}")
