import sys, io, pandas as pd, warnings, re
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings('ignore')
D = r'data/Search terms'
st = pd.read_csv(f'{D}/Search terms last 60 days.csv', skiprows=2, thousands=',')
st = st[~st['Search term'].astype(str).str.startswith('Total') & st['Search term'].notna()].copy()
st['Search term'] = st['Search term'].astype(str).str.lower().str.strip()
agg = st.groupby('Search term').agg({'Cost':'sum','Conversions':'sum'}).reset_index()

# Extract all 2-word phrases with their aggregated stats
bigram_stats = {}
for _, row in agg.iterrows():
    words = row['Search term'].split()
    for i in range(len(words)-1):
        bg = f"{words[i]} {words[i+1]}"
        if bg not in bigram_stats:
            bigram_stats[bg] = {'cost':0,'conv':0,'terms':0}
        bigram_stats[bg]['cost'] += row['Cost']
        bigram_stats[bg]['conv'] += row['Conversions']
        bigram_stats[bg]['terms'] += 1

# Top bigrams by spend with zero conversions
rows = []
for bg, s in bigram_stats.items():
    if s['cost'] >= 30 and s['conv'] == 0 and s['terms'] >= 3:
        rows.append((bg, s['terms'], s['cost'], s['conv']))
rows.sort(key=lambda x: -x[2])

print(f"{'Bigram':<30} {'Terms':>6} {'Spend':>8} {'Conv':>5}")
print('-' * 60)
for bg, terms, cost, conv in rows[:120]:
    print(f"{bg:<30} {terms:>6} L{cost:>6,.0f} {conv:>5.0f}")
print(f"\nTotal zero-conv 2-word phrases (L30+, 3+ terms): {len(rows)}")
