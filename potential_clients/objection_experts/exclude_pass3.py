import pandas as pd
import re
from collections import defaultdict

st = pd.read_csv('C:/Users/User/Desktop/gads-data-layer/potential_clients/Objection Experts/Search Terms/Search terms report Added-Excluded = none.csv', skiprows=2, thousands=',')
st['Search term'] = st['Search term'].astype(str).str.strip()
st = st[~st['Search term'].str.startswith('Total:')]
st['Cost'] = pd.to_numeric(st['Cost'], errors='coerce')
st['Clicks'] = pd.to_numeric(st['Clicks'], errors='coerce')
st['Conversions'] = pd.to_numeric(st['Conversions'], errors='coerce')
st['term_lower'] = st['Search term'].str.lower()

# Deduplicate
dedup = st.groupby('term_lower').agg({'Cost':'sum','Clicks':'sum','Conversions':'sum'}).reset_index()
converting = set(dedup[dedup['Conversions'] > 0]['term_lower'].values)
nonconv = dedup[dedup['Conversions'] == 0].copy()

print(f'Total unique: {len(dedup)}')
print(f'Converting (protected): {len(converting)}')
print(f'Non-converting to review: {len(nonconv)}')
print()

# Load 1-word phrase negatives for cross-reference
neg1 = pd.read_csv('C:/Users/User/Desktop/gads-data-layer/potential_clients/Objection Experts/Negative keyword lists/Negative keyword details report (1).csv', skiprows=2)
neg1['keyword'] = neg1['keyword_text'].astype(str).str.strip().str.lower()
phrase_negatives = set(neg1['keyword'].values)

# Also load 2-word and 3-word phrase negatives
neg3 = pd.read_csv('C:/Users/User/Desktop/gads-data-layer/potential_clients/Objection Experts/Negative keyword lists/Negative keyword details report (3).csv', skiprows=2)
neg3['keyword'] = neg3['keyword_text'].astype(str).str.strip().str.lower()
phrase_2word = set(neg3['keyword'].values)

neg5 = pd.read_csv('C:/Users/User/Desktop/gads-data-layer/potential_clients/Objection Experts/Negative keyword lists/Negative keyword details report (5).csv', skiprows=2)
neg5['keyword'] = neg5['keyword_text'].astype(str).str.strip().str.lower()
phrase_3word = set(neg5['keyword'].values)

neg7 = pd.read_csv('C:/Users/User/Desktop/gads-data-layer/potential_clients/Objection Experts/Negative keyword lists/Negative keyword details report (7).csv', skiprows=2)
neg7['keyword'] = neg7['keyword_text'].astype(str).str.strip().str.lower()
phrase_4word = set(neg7['keyword'].values)

print(f'Phrase negatives: {len(phrase_negatives)} x 1-word, {len(phrase_2word)} x 2-word, {len(phrase_3word)} x 3-word, {len(phrase_4word)} x 4-word')
print()

# PASS 1: Cross-reference against ALL phrase match negatives (1, 2, 3, 4 word)
def matches_phrase_negative(term):
    words = term.split()
    # Check 1-word phrase negatives
    for w in words:
        if w in phrase_negatives:
            return True, w
    # Check 2-word phrase negatives
    for i in range(len(words)-1):
        bigram = f'{words[i]} {words[i+1]}'
        if bigram in phrase_2word:
            return True, bigram
    # Check 3-word phrase negatives
    for i in range(len(words)-2):
        trigram = f'{words[i]} {words[i+1]} {words[i+2]}'
        if trigram in phrase_3word:
            return True, trigram
    # Check 4-word phrase negatives
    for i in range(len(words)-3):
        quad = f'{words[i]} {words[i+1]} {words[i+2]} {words[i+3]}'
        if quad in phrase_4word:
            return True, quad
    return False, None

# PASS 2: Additional patterns for non-converting terms not caught by phrase negatives
exclude_patterns = [
    # Appeals
    r'appeal', r'appealing', r'appeals',
    # Refused/rejected
    r'\brefused\b', r'\brefusal\b', r'\brejected\b',
    # Complaints
    r'\bcomplaint', r'\bcomplain',
    # Ombudsman
    r'\bombudsman\b',
    # Petition
    r'\bpetition',
    # Dispute
    r'\bdispute',
    # Overturn
    r'\boverturn',
    # Granted/approved/denied
    r'\bgranted\b', r'\bapproved\b', r'\bdenied\b',
    # Planning consultants/agents
    r'\bplanning consultant', r'\bplanning agent',
    # Solicitors/lawyers
    r'\bsolicitor', r'\blawyer',
    # Commenting
    r'\bcommenting\b', r'\bcomments?\b.*planning',
    # Enforcement/breach
    r'\benforcement\b', r'\bbreach\b',
    # Portal
    r'\bplanning portal\b',
    # Pre-app
    r'\bpre.?application\b',
    # Retrospective
    r'retrospective planning(?!.*object)',
    # Do I need planning
    r'do i need planning', r'do you need planning',
    # How to get/apply/win
    r'how to get planning', r'how to apply.*planning', r'how to win planning',
    # Anonymously
    r'\banonymous',
    # How many needed
    r'how many.*needed', r'how many.*to stop', r'how many objections',
    # How long
    r'how long.*to object', r'how long.*have to', r'how long.*appeal',
    # View/see/check objections
    r'can i see.*objection', r'view.*objection', r'check.*objection',
    # What grounds/reasons (informational)
    r'^what are valid', r'^what grounds', r'^what reasons', r'^on what grounds',
    r'^what can you object', r'^what can i object',
    # Valid/legitimate/best (informational)
    r'^valid reasons', r'^valid objections', r'^legitimate', r'^best objections',
    r'^successful.*objection',
    # Reasons/grounds for (informational)
    r'^reasons for objecting', r'^reasons to object', r'^grounds for objecting',
    r'^grounds for planning', r'^grounds to object', r'^grounds for opposing',
    # How to write/draft/letter of objection (DIY)
    r'how to write', r'how to draft', r'writing a', r'write an objection',
    r'letter of objection', r'letters of objection',
    # Template/sample/example
    r'\btemplate\b', r'\bsample\b', r'\bexample\b',
    # How to block/fight
    r'how to block', r'how to fight',
    # Specific councils (looking at council not service)
    r'\bcouncil\b.*\bobjection', r'\bobjection.*\bcouncil\b',
    # Material considerations (informational)
    r'\bmaterial.*objection', r'\bmaterial.*consideration',
    # Overlooking/overbearing/loss of light (informational)
    r'\boverlooking\b', r'\boverbearing\b', r'loss of light', r'loss of privacy',
    # Visual/residential amenity
    r'\bvisual amenity\b', r'\bresidential amenity\b', r'\bamenity\b',
    # Overdevelopment
    r'\boverdevelopment\b',
    # Who can object (informational)
    r'^who can object', r'^can i object\b', r'^can you object\b',
    r'^can neighbours? object', r'^can anyone object',
    # Neighbours objecting (informational about process)
    r'^neighbours? objecting', r'^what happens if.*neighbour',
    # Once granted
    r'once.*granted', r'after.*granted',
    # How to object (bare informational)
    r'^how to object to planning$',
    r'^how to object to a planning application$',
    r'^how do i object to a planning application$',
    # Making/lodging (process info)
    r'how to make.*objection', r'how to lodge', r'making an objection',
    # Can objections stop
    r'can objections stop',
    # Planning objection + topic (informational)
    r'planning objections?\s+(overlooking|garden|material|reasons|example)',
    # HMO objection letter (DIY)
    r'hmo objection letter',
    # Objecting to planning permission + location (looking at council)
    r'^objecting to planning permission uk$',
    # Non determination
    r'\bnon.?determination\b',
    # Section 78
    r'\bsection 78\b', r'\bs78\b',
    # Good reasons to object (informational)
    r'^good reasons',
    # Specific other businesses/names
    r'\baardvark\b', r'\bobjector ai\b',
]

def should_exclude_pattern(term):
    for pattern in exclude_patterns:
        if re.search(pattern, term, re.IGNORECASE):
            return True
    return False

# Process all non-converting terms
exclude_phrase = []  # Matched by phrase negatives
exclude_pattern = []  # Matched by additional patterns
keep = []

for _, r in nonconv.iterrows():
    term = r['term_lower']

    # Check phrase negatives first
    matched, neg_word = matches_phrase_negative(term)
    if matched:
        exclude_phrase.append(term)
        continue

    # Check additional patterns
    if should_exclude_pattern(term):
        exclude_pattern.append(term)
        continue

    keep.append(term)

print(f'=== RESULTS ===')
print(f'Excluded by phrase negatives: {len(exclude_phrase)}')
print(f'Excluded by additional patterns: {len(exclude_pattern)}')
print(f'Keep (relevant objection terms): {len(keep)}')
print(f'Converting (protected): {len(converting)}')
print()

# Combine all exclusions
all_exclude = sorted(set(exclude_phrase + exclude_pattern))

# Filter to max 10 words
all_exclude = [t for t in all_exclude if len(t.split()) <= 10]

# Organise by word count
lists = defaultdict(list)
for term in all_exclude:
    wc = len(term.split())
    if wc == 1:
        lists['1 word'].append(term)
    elif wc == 2:
        lists['2 words'].append(term)
    elif wc == 3:
        lists['3 words'].append(term)
    elif wc == 4:
        lists['4 words'].append(term)
    else:
        lists['5+ words'].append(term)

for key in ['1 word', '2 words', '3 words', '4 words', '5+ words']:
    terms = sorted(set(lists.get(key, [])))
    if terms:
        print(f'=== {key} [exact] ({len(terms)} keywords) ===')
        print()
        for t in terms:
            print(f'[{t}]')
        print()
