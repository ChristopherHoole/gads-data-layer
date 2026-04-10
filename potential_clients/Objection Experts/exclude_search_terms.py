import pandas as pd
import re
from collections import defaultdict

st = pd.read_csv('C:/Users/User/Downloads/Search terms report (2).csv', skiprows=2, thousands=',')
st['Cost'] = pd.to_numeric(st['Cost'], errors='coerce')
st['Clicks'] = pd.to_numeric(st['Clicks'], errors='coerce')
st['Conversions'] = pd.to_numeric(st['Conversions'], errors='coerce')
st['Impr.'] = pd.to_numeric(st['Impr.'], errors='coerce')
st['Search term'] = st['Search term'].str.strip()
st = st[~st['Search term'].str.startswith('Total:')]

converting = set(st[st['Conversions'] > 0]['Search term'].str.lower().values)

nonconv = st[st['Conversions'] == 0].copy()
nonconv['term_lower'] = nonconv['Search term'].str.lower()
nonconv_dedup = nonconv.groupby('term_lower').agg({
    'Cost': 'sum', 'Clicks': 'sum', 'Impr.': 'sum', 'Search term': 'first'
}).reset_index()
nonconv_dedup = nonconv_dedup[~nonconv_dedup['term_lower'].isin(converting)]

print(f'Total non-converting unique terms: {len(nonconv_dedup)}')

irrelevant_patterns = [
    # Appeals
    r'appeal', r'appealing', r'appeals',
    # Refused/rejected
    r'\brefused\b', r'\brefusal\b', r'\brejected\b', r'\breject\b',
    # Complaints
    r'\bcomplaint\b', r'\bcomplaints\b', r'\bcomplain\b', r'\bcomplaining\b',
    # Solicitors/lawyers (wrong service unless with objection)
    r'\bsolicitors?\b(?!.*objection)', r'\blawyers?\b', r'\bbarrister\b',
    # Planning consultants/agents (wrong service)
    r'\bplanning consultants?\b(?!.*objection)', r'\bplanning agents?\b',
    # Ombudsman
    r'\bombudsman\b',
    # Petition
    r'\bpetitions?\b',
    # Comments on planning
    r'\bcomments?\b.*planning', r'planning.*\bcomments?\b',
    r'\bcommenting\b',
    # Retrospective (applying not objecting)
    r'retrospective planning permission(?!.*object)',
    # Applicant intent
    r'how to.*\bwin\b.*planning', r'how to.*\bget\b.*planning',
    r'how to.*\bapply\b.*planning', r'\bapply for planning\b',
    r'\bapplication form\b',
    # Costs/fees (applicants)
    r'planning permission cost', r'planning permission fee',
    r'cost of planning', r'how much.*planning permission',
    # Overturning
    r'\boverturn', r'\boverturned\b',
    # Dispute
    r'\bdisputes?\b',
    # TPO/trees
    r'\btree preservation\b', r'\btpo\b',
    # Council admin
    r'\bcouncil tax\b', r'\bcouncil meeting\b',
    # Wrong intent completely
    r'\bdrugs?\b', r'\bnoise\b(?!.*planning)', r'\bparking\b(?!.*planning)',
    # Enforcement/breach
    r'\bplanning enforcement\b', r'\benforcement\b(?!.*objection)',
    r'\bplanning breach\b', r'\bbreach of planning\b',
    # Building regs
    r'\bbuilding regulations\b', r'\bbuilding control\b',
    # Planning portal
    r'\bplanning portal\b',
    # Pre-app
    r'\bpre.?application\b', r'\bpre.?app\b',
    # DIY/template
    r'\btemplate\b', r'\bsample\b(?!.*objection)',
    # Anonymously
    r'\banonymous',
    # How many needed
    r'how many.*needed', r'how many.*to stop', r'how many objections.*stop',
    r'how many objections.*refuse',
    # Timescales
    r'\btimescale\b', r'\btime limit\b', r'\btime frame\b',
    r'how long.*to object', r'how long.*have to',
    # View/check objections (applicants)
    r'can i see.*objection', r'view.*objection', r'check objection',
    r'see objections.*my', r'read.*objection',
    # Granted/approved (too late)
    r'\bgranted\b', r'\bapproved\b(?!.*object)',
    # Jobs
    r'\bjobs?\b', r'\bcareer\b', r'\bsalary\b',
    # Bare planning terms
    r'^planning permission$', r'^planning application$', r'^planning$',
    # Specific non-relevant structures
    r'\bconservatory\b', r'\bloft conversion\b', r'\bdormer\b',
    r'\bsolar panel', r'\bsatellite dish\b', r'\bcaravan\b',
    r'\bgarden room\b', r'\bsummer house\b', r'\bshed\b(?!.*objection)',
    # Other businesses
    r'\bplanning voice\b', r'\basbri planning\b', r'\bet planning\b',
    # Overdevelopment (informational)
    r'^over.?development',
    # Specific councils (not seeking service)
    r'\bribble valley\b(?!.*objection)', r'\bwmdc\b',
    r'\brct\b(?!.*objection)', r'\bepping forest\b(?!.*objection)',
    r'\bamber valley\b(?!.*objection)', r'\btrafford\b(?!.*objection)',
    # What is/what does (informational)
    r'^what is\b', r'^what does\b', r'^what are\b(?!.*valid)',
    # Do i need planning
    r'do i need planning', r'need planning permission',
    # Neighbour dispute (not planning objection)
    r'\bneighbour dispute\b', r'\bboundary dispute\b', r'\bfence dispute\b',
    # Correctly (informational)
    r'how to correctly',
    # Definition
    r'\bdefinition\b', r'\bmeaning\b',
    # Forum/blog
    r'\bforum\b', r'\bblog\b',
    # Wikipedia
    r'\bwikipedia\b', r'\bwiki\b',
    # PDF/download
    r'\bpdf\b', r'\bdownload\b',
    # Near me (often too vague)
    r'^planning near me$', r'^planning permission near me$',
]

def should_exclude(term):
    for pattern in irrelevant_patterns:
        if re.search(pattern, term, re.IGNORECASE):
            return True
    return False

nonconv_dedup['exclude'] = nonconv_dedup['term_lower'].apply(should_exclude)
exclude = nonconv_dedup[nonconv_dedup['exclude'] == True].copy()
exclude = exclude[~exclude['term_lower'].isin(converting)]  # Safety

print(f'EXCLUDE: {len(exclude)} terms')
print(f'KEEP: {len(nonconv_dedup) - len(exclude)} terms')
print()

# Organise by word count
exclude['word_count'] = exclude['term_lower'].str.split().apply(len)

lists = defaultdict(list)
for _, r in exclude.iterrows():
    wc = r['word_count']
    if wc == 2:
        lists['2 words'].append(r['term_lower'])
    elif wc == 3:
        lists['3 words'].append(r['term_lower'])
    elif wc == 4:
        lists['4 words'].append(r['term_lower'])
    else:
        lists['5+ words'].append(r['term_lower'])

for key in ['2 words', '3 words', '4 words', '5+ words']:
    terms = sorted(set(lists.get(key, [])))
    print(f'=== {key} [exact] ({len(terms)} keywords) ===')
    print()
    for t in terms:
        print(f'[{t}]')
    print()
