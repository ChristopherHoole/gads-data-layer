import sys, io, pandas as pd, warnings, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings('ignore')
D = r'data/Search terms'
st = pd.read_csv(f'{D}/Search terms last 60 days.csv', skiprows=2, thousands=',')
st = st[~st['Search term'].astype(str).str.startswith('Total') & st['Search term'].notna()].copy()
st['Search term'] = st['Search term'].astype(str).str.lower().str.strip()
agg = st.groupby('Search term').agg({'Cost':'sum','Impr.':'sum','Clicks':'sum','Conversions':'sum'}).reset_index()
agg['wc'] = agg['Search term'].str.split().str.len()
three = agg[agg['wc']==3].copy()
tier3 = three[(three['Conversions']==0) & (three['Cost']>=5) & (three['Cost']<10)].sort_values('Cost', ascending=False)
print(f'Batch 3 (3 word, zero conv, L5-10): {len(tier3)} terms, L{tier3["Cost"].sum():.0f} waste')
print()
for _, r in tier3.iterrows():
    print(f'{r["Search term"]:<50} L{r["Cost"]:>5.1f}')
