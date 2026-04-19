import pandas as pd
import re
from collections import defaultdict

st = pd.read_csv('C:/Users/User/Desktop/gads-data-layer/potential_clients/Objection Experts/weekly optimisations/Search terms report (4).csv', skiprows=2, thousands=',')
st['Search term'] = st['Search term'].astype(str).str.strip()
st = st[~st['Search term'].str.startswith('Total:')]
st['Cost'] = pd.to_numeric(st['Cost'], errors='coerce')
st['Clicks'] = pd.to_numeric(st['Clicks'], errors='coerce')
st['Conversions'] = pd.to_numeric(st['Conversions'], errors='coerce')
st['term_lower'] = st['Search term'].str.lower()

# Filter to Added/Excluded = none
none_terms = st[st['Added/Excluded'].isna() | (st['Added/Excluded'].str.strip() == 'None')].copy()
dedup = none_terms.groupby('term_lower').agg({'Cost':'sum','Clicks':'sum','Conversions':'sum'}).reset_index()
converting = set(dedup[dedup['Conversions'] > 0]['term_lower'].values)
nonconv = dedup[dedup['Conversions'] == 0].copy()

print(f'Total Added/Excluded = none: {len(dedup)}')
print(f'Converting (protected): {len(converting)}')
print(f'Non-converting to review: {len(nonconv)}')
print()

# Load all phrase match negatives for cross-reference
neg_dir = 'C:/Users/User/Desktop/gads-data-layer/potential_clients/Objection Experts/weekly optimisations'
neg1 = pd.read_csv(f'{neg_dir}/1 WORD phrase.csv', skiprows=2)
neg1['keyword'] = neg1['keyword_text'].astype(str).str.strip().str.lower()
phrase_1word = set(neg1['keyword'].values)

neg3 = pd.read_csv(f'{neg_dir}/2 WORDS phrase.csv', skiprows=2)
neg3['keyword'] = neg3['keyword_text'].astype(str).str.strip().str.lower()
phrase_2word = set(neg3['keyword'].values)

neg5 = pd.read_csv(f'{neg_dir}/3 WORDS phrase.csv', skiprows=2)
neg5['keyword'] = neg5['keyword_text'].astype(str).str.strip().str.lower()
phrase_3word = set(neg5['keyword'].values)

neg7 = pd.read_csv(f'{neg_dir}/4 WORDS phrase.csv', skiprows=2)
neg7['keyword'] = neg7['keyword_text'].astype(str).str.strip().str.lower()
phrase_4word = set(neg7['keyword'].values)

# Check which non-converting terms match phrase negatives
def matches_phrase(term):
    words = term.split()
    for w in words:
        if w in phrase_1word:
            return True
    for i in range(len(words)-1):
        if f'{words[i]} {words[i+1]}' in phrase_2word:
            return True
    for i in range(len(words)-2):
        if f'{words[i]} {words[i+1]} {words[i+2]}' in phrase_3word:
            return True
    for i in range(len(words)-3):
        if f'{words[i]} {words[i+1]} {words[i+2]} {words[i+3]}' in phrase_4word:
            return True
    return False

# Additional patterns
exclude_patterns = [
    r'appeal', r'appealing', r'appeals',
    r'\brefused\b', r'\brefusal\b', r'\brejected\b',
    r'\bcomplaint', r'\bcomplain', r'\bombudsman\b',
    r'\bpetition', r'\bdispute', r'\boverturn',
    r'\bgranted\b', r'\bapproved\b', r'\bdenied\b',
    r'\bplanning consultant', r'\bplanning agent',
    r'\bsolicitor', r'\blawyer',
    r'\bcommenting\b', r'\bcomments?\b.*planning',
    r'\benforcement\b', r'\bbreach\b',
    r'\bplanning portal\b', r'\bpre.?application',
    r'retrospective planning(?!.*object)',
    r'do i need planning', r'do you need planning',
    r'how to get planning', r'how to apply.*planning', r'how to win planning',
    r'\btemplate\b', r'\bsample\b', r'\bexample\b',
    r'\banonymous', r'how many', r'how long.*to object', r'how long.*have to',
    r'can i see.*objection', r'view.*objection', r'check.*objection',
    r'^what are valid', r'^what grounds', r'^on what grounds',
    r'^valid reasons', r'^valid objections', r'^legitimate', r'^best objections',
    r'^successful.*objection', r'^reasons for objecting', r'^reasons to object',
    r'^grounds for objecting', r'^grounds for planning', r'^grounds to object',
    r'^grounds for opposing', r'^who can object', r'^can i object\b',
    r'^can you object\b', r'^can neighbours? object', r'^can anyone object',
    r'^what happens', r'^what is\b', r'^what are\b', r'^what can',
    r'^how to object', r'^how to oppose', r'^how to fight',
    r'^how to block', r'^how to challenge', r'^how to contest',
    r'^how to stop', r'^how to successfully',
    r'^how do i object', r'^how do i oppose', r'^how do you object',
    r'^how can i object', r'how to write', r'how to draft',
    r'writing a', r'write an objection', r'letter of objection',
    r'letters of objection', r'objection letter',
    r'\bgrounds\b', r'\breasons\b', r'\bvalid\b',
    r'\bmaterial.*objection', r'\bmaterial.*consideration',
    r'\boverlooking\b', r'\boverbearing\b', r'loss of light', r'loss of privacy',
    r'\bamenity\b', r'\boverdevelopment\b',
    r'^opposing\b', r'^objecting\b', r'^objections to\b', r'^objection to\b',
    r'^challenging\b', r'^contesting\b', r'^fighting\b',
    r'\bcouncil\b.*objection', r'objection.*\bcouncil\b',
    r'housing development', r'\bretrospective\b',
    r'^stop planning', r'\bfree\b', r'once.*granted', r'after.*granted',
    r'^can objections', r'\bnon.?determination', r'\bsection 78\b',
    r'^neighbours? objecting', r'^what happens if.*neighbour',
    r'making an objection', r'how to make.*objection', r'how to lodge',
    r'planning permit', r'letter.*opposing', r'letter.*object',
    r'^advice on objecting',
    r'planning objections?\s+(overlooking|garden|material|reasons|example|privacy|light)',
    r'hmo objection letter', r'change of use application',
    r'^good reasons', r'\baardvark\b', r'\bobjector ai\b',
    r'planning permission for extension', r'outbuilding planning',
    r'supporting.*planning', r'amending.*planning', r'renew.*planning',
    r'reapply.*planning', r'lapsed planning',
]

def should_exclude(term):
    if matches_phrase(term):
        return True
    for pattern in exclude_patterns:
        if re.search(pattern, term, re.IGNORECASE):
            return True
    return False

exclude = []
keep = []
for _, r in nonconv.iterrows():
    term = r['term_lower']
    wc = len(term.split())
    if wc > 10:
        keep.append(term)
        continue
    if should_exclude(term):
        exclude.append(term)
    else:
        keep.append(term)

print(f'EXCLUDE: {len(exclude)}')
print(f'KEEP: {len(keep)}')
print()

# Organise by word count
lists = defaultdict(list)
for term in sorted(set(exclude)):
    wc = len(term.split())
    if wc == 2:
        lists['2 words'].append(term)
    elif wc == 3:
        lists['3 words'].append(term)
    elif wc == 4:
        lists['4 words'].append(term)
    else:
        lists['5+ words'].append(term)

for key in ['2 words', '3 words', '4 words', '5+ words']:
    terms = sorted(set(lists.get(key, [])))
    if terms:
        print(f'=== {key} [exact] ({len(terms)} keywords) ===')
        print()
        for t in terms:
            print(f'[{t}]')
        print()
