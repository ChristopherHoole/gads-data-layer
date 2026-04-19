import sys, io, pandas as pd, warnings, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings('ignore')
D = r"C:\Users\User\Desktop\gads-data-layer\potential_clients\Inserta Dental\data\Search terms"
st = pd.read_csv(f"{D}/Search terms last 60 days.csv", skiprows=2, thousands=',')
st = st[~st['Search term'].astype(str).str.startswith('Total') & st['Search term'].notna()]

# Every phrase I recommended — verify rigorously
check = [
    'on 4 teeth','4 teeth implants','in 4 dental','dental implants nhs','nhs dental implants',
    'i want all','want all my','same day dentures','same day teeth','dentist in london',
    'cost of implants','cost of teeth','cost of tooth','cost of an','smiles by the',
    'by the river','to get new','london smile clinic','where to get','how long do',
    'how to replace','replace a missing','what are the','best dentist for','get new teeth',
    'brighton implant clinic','harley street implant','harley street smile','dental implants reviews',
    'dental clinic reviews','before and after','what is a','smile by design','false teeth implants',
    'average price of','top rated dental','top rated dentist','top dental implant','who does dental',
    'for over 65','price list for','pros and cons','why are dental','implants in hungary',
    'why do dental','implants in poland','vs implants','price of a','implants vs','with no money',
    'mini dental implants','dentures vs','how long can','price of implants','price of dental',
    'how to find','i need teeth','by design dental','how to get','how to apply','dentist near me',
    'apply for dental','free dental implants','get free dental','pay monthly dental','no credit check',
    'implants over 60','with bad credit','how much a',
]

print(f"{'Phrase':<30} {'Terms':>5} {'Spend':>7} {'Conv':>4} {'Top converting term'}")
for p in check:
    mask = st['Search term'].astype(str).str.lower().str.contains(rf'\b{re.escape(p)}\b', regex=True, na=False)
    m = st[mask]
    if len(m) == 0: continue
    cost = m['Cost'].sum()
    conv = m['Conversions'].sum()
    conv_terms = m[m['Conversions']>0].sort_values('Conversions', ascending=False)
    if len(conv_terms) > 0:
        tc = conv_terms.iloc[0]['Search term'][:50]
        tn = conv_terms.iloc[0]['Conversions']
        # Check: is the top converter already blocked by existing negatives?
        top_term = conv_terms.iloc[0]['Search term'].lower()
        blocked_words = ['nhs','free','turkey','poland','hungary','abroad','trial','trials','grants','grant',
                          'denture','dentures','whitening','bonding','composite','crown','crowns','extraction',
                          'gum','disease','straumann','jaw','apply','credit','afford','fee','seniors','60s',
                          'money','check','low','fake','false','grinder','local']
        top_words = re.findall(r"[a-z0-9']+", top_term)
        already_blocked = any(w in blocked_words for w in top_words)
        marker = '  (blocked)' if already_blocked else '  [REAL INTENT]'
    else:
        tc = 'NONE'; tn = 0; marker = ' ZERO-CV'
    print(f"{p:<30} {len(m):>5} L{cost:>5,.0f} {conv:>4.0f}  [{tc}]({tn:.0f}){marker}")
