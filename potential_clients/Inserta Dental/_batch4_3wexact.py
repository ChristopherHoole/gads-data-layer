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
tier4 = three[(three['Conversions']==0) & (three['Cost']>=3) & (three['Cost']<5)].sort_values('Cost', ascending=False)
print(f'Batch 4 (3 word, zero conv, L3-5): {len(tier4)} terms, L{tier4["Cost"].sum():.0f} waste')
print()
for _, r in tier4.iterrows():
    print(f'{r["Search term"]:<50} L{r["Cost"]:>5.1f}')
