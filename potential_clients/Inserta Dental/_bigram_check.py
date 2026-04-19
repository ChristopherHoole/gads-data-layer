import sys, io, pandas as pd, warnings, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings('ignore')

D = r"C:\Users\User\Desktop\gads-data-layer\potential_clients\Inserta Dental\data\Search terms"
st = pd.read_csv(f"{D}/Search terms last 60 days.csv", skiprows=2, thousands=',')
st = st[~st['Search term'].astype(str).str.startswith('Total') & st['Search term'].notna()]

candidates = [
    'fake tooth','fake teeth','dental veneers','teeth veneers','veneers london','dental aligners','aligners london','composite veneers','porcelain veneers',
    'smile makeover','dental makeover','new teeth','get new','fix my','fix teeth','fix bad',
    'replacement teeth','teeth replacement','tooth replacement','replace all','replace missing',
    'missing tooth','missing teeth',
    'teeth straightening','teeth aligner','clear aligners','tooth straightening',
    'best value','value dental','the cheapest','cheapest uk','price of','the cost','the price',
    'cheap all','cheap near','cheap teeth','cheap dental','cheap implant','cheap implants','cheap tooth','cheap full',
    'get cheap','find cheap',
    'the best','is the','are the','the price','how long','does it','what is','what are','is it','is there',
    'pros and','side effects','vs dental','vs implant','versus implant','vs dentures','vs bridge',
    'or dentures','or bridge','or veneers','or crown','or dental',
    'before and','and after','before photos','after photos','before after','transformation photos',
    'no money','without money','cant afford','can not','need dental','need help',
    'gum disease','gum treatment','teeth whitening','root canal','canal treatment','wisdom tooth','wisdom teeth',
    'tooth extraction','tooth decay','tooth filling','filling cost','teeth cleaning','dental cleaning',
    'teeth gap','gap teeth','chipped tooth','broken tooth','cracked tooth','loose tooth','pulled tooth',
    'tooth pain','mouth pain','jaw pain','dental pain','tooth abscess','dental abscess',
    'emergency dental','out of','24 hour','24 hours','same day','dental emergency',
    'dental hospital','dental centre','dental office','dental surgery','dental practice','dental school','dental group',
    'dental care','care dental','dentist for','dentist in','dentist near','private dentist','nhs dentist',
    'kids dental','children dental','childrens dental','kids dentist','paediatric dental','pediatric dental',
    'baby teeth','teen dental','young dental',
    'for pensioners','for elderly','elderly care','care home','nursing home','home visit',
    'on benefits','universal credit','pension credit','disability living','council tax','disability benefits',
    'in turkey','in poland','in hungary','in spain','in india','in mexico','in thailand','in germany',
    'in dubai','in egypt','in croatia','in slovenia','in bulgaria','in romania','in portugal','in albania',
    'in europe','dental turkey','dental hungary','dental poland','dentist turkey','dentist abroad',
    'europe dental','abroad dental',
    'dental implants birmingham','dental implants bristol','dental implants leeds','dental implants manchester',
    'dental implants glasgow','dental implants edinburgh','dental implants newcastle','dental implants liverpool',
    'dental implants sheffield','dental implants nottingham','dental implants cardiff','dental implants belfast',
    'dental implants brighton','dental implants oxford','dental implants cambridge','dental implants york',
    'dental implants reading','dental implants swindon','dental implants plymouth','dental implants norwich',
    'dental implants southampton','dental implants bournemouth','dental implants portsmouth','dental implants hull',
    'dental implants stoke','dental implants derby','dental implants coventry','dental implants leicester',
    'dental implants wolverhampton','dental implants aberdeen','dental implants dundee',
    'dental clinic','dental clinics','dental company','dental companies','dental website','dental app',
    'dental information','dental advice','dental consultation','dental education','dental history',
    'at home','do it','make own','diy dental','home remedy','natural teeth','natural remedy',
    'london smile','smiles by','the river','dental beauty','dental reviews','clinic reviews','dental hammersmith','hammersmith reviews',
    'top rated','best rated','highly rated','google rating','trustpilot',
    'uk reviews','london reviews','implant monthly','implant finance','with financing','finance options','finance plans',
    'dental jobs','dentist jobs','dental career','dental course','dental training','dental degree','dental salary',
    'dental apprenticeship','become dentist','dentist training',
    'osstem implant','straumann implant','nobel implant','zirkonzahn implant','mis implant',
    'implant failure','failed implant','implant infection','implant problems','implant pain','implant aftercare',
    'implant removal','remove implant',
    'best price','lowest price','lowest cost','best cost','compare dental','compare implant','compare prices',
]
candidates = list(dict.fromkeys(candidates))

results = []
for phrase in candidates:
    mask = st['Search term'].astype(str).str.lower().str.contains(rf'\b{re.escape(phrase)}\b', regex=True, na=False)
    matching = st[mask]
    if len(matching) == 0: continue
    cost = matching['Cost'].sum()
    conv = matching['Conversions'].sum()
    if cost < 5: continue
    conv_terms = matching[matching['Conversions']>0].sort_values('Conversions', ascending=False)
    top_conv = conv_terms.iloc[0]['Search term'][:55] if len(conv_terms) > 0 else 'NONE'
    top_conv_n = conv_terms.iloc[0]['Conversions'] if len(conv_terms) > 0 else 0
    results.append((phrase, len(matching), cost, conv, top_conv, top_conv_n))

results.sort(key=lambda x: -x[2])
print(f"{'Phrase':<30} {'Terms':>6} {'Spend':>8} {'Conv':>6} {'Top Converting'}")
for phrase, terms, cost, conv, top_conv, top_conv_n in results:
    marker = 'SAFE' if conv == 0 else 'CHECK' if conv < 3 else 'SKIP'
    print(f"{marker:5s} {phrase:<28} {terms:>6} L{cost:>6,.0f} {conv:>6.0f}   [{top_conv}] ({top_conv_n:.0f})")
