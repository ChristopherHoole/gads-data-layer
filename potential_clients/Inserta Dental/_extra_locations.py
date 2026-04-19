import sys, io, pandas as pd, warnings, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings('ignore')
D = r'data/Search terms'
st = pd.read_csv(f'{D}/Search terms last 60 days.csv', skiprows=2, thousands=',')
st = st[~st['Search term'].astype(str).str.startswith('Total') & st['Search term'].notna()].copy()
st['Search term'] = st['Search term'].astype(str).str.lower().str.strip()
agg = st.groupby('Search term').agg({'Cost':'sum','Conversions':'sum'}).reset_index()

# Additional locations surfaced in 3-word exact lists
candidates = [
    # UK towns outside Greater London
    'bedford','windsor','grantham','brentwood','dorchester','fareham','medway',
    'wimborne','cobham','egham','chertsey','kettering','petersfield','weybridge',
    'cheshunt','hawick','wandsworth','twickenham',
    # Nationality/language forms (not caught by country names)
    'turkish','swiss','hungarian','polish','romanian','bulgarian','croatian',
    'albanian','thai','indian','lithuanian','greek','mexican','spanish','czech',
    'ukrainian','german','french','italian','slovenian','moldovan','armenian',
    # Abroad cities
    'dublin','ghana',
    # Foreign language words for London (non-English spellings)
    'londra','londone','londonban','londyn',
]
# Remove dupes, sort
candidates = sorted(set(candidates))
hits = []
for loc in candidates:
    mask = agg['Search term'].str.contains(rf'\b{re.escape(loc)}\b', regex=True, na=False)
    m = agg[mask]
    if len(m) == 0: continue
    cost = m['Cost'].sum()
    conv = m['Conversions'].sum()
    if cost < 2: continue
    hits.append((loc, cost, conv, len(m)))

hits.sort(key=lambda x: -x[1])
print(f"{'Location':<20} {'Spend':>8} {'Conv':>5} {'Terms':>6}")
print('-' * 45)
for loc, cost, conv, terms in hits:
    print(f"{loc:<20} L{cost:>6,.0f} {conv:>5.0f} {terms:>6}")
print(f"\nTotal: {len(hits)}")
