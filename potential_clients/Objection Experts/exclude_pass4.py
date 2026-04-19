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

dedup = st.groupby('term_lower').agg({'Cost':'sum','Clicks':'sum','Conversions':'sum'}).reset_index()
converting = set(dedup[dedup['Conversions'] > 0]['term_lower'].values)
nonconv = dedup[dedup['Conversions'] == 0].copy()

print(f'Non-converting unique terms: {len(nonconv)}')

# Very aggressive exclusion patterns
# Everything that isn't a clear "I want to hire someone to object for me" intent
exclude_patterns = [
    # How to write/draft/letter (DIY)
    r'how to write', r'how to draft', r'writing a', r'write an objection',
    r'letter of objection', r'letters of objection', r'objection letter',
    r'letter.*objecting', r'letter.*opposing', r'letter.*object',
    r'planning objection letter', r'planning permission objection letter',
    r'objection.*letter', r'letter.*objection',
    # Template/sample/example/format
    r'\btemplate\b', r'\bsample\b', r'\bexample\b', r'\bformat\b',
    # How many/how long (informational)
    r'how many', r'how long',
    # What grounds/reasons/valid (informational research)
    r'\bgrounds\b', r'\breasons\b', r'\bvalid\b', r'\blegitimate\b',
    r'\bbest\b.*objection', r'\bsuccessful\b.*objection',
    r'\bgood\b.*objection', r'\bgood\b.*reason',
    r'\bmaterial\b.*objection', r'\bmaterial\b.*consideration',
    # Who can object / can I object (informational)
    r'^who can', r'^can i object', r'^can you object', r'^can anyone',
    r'^can neighbours', r'^can a neighbour', r'^can objections',
    # What happens (informational)
    r'^what happens', r'^what is\b', r'^what are\b', r'^what can',
    r'^on what grounds', r'^what grounds',
    # How to object/oppose/fight/block/challenge/contest (DIY intent)
    r'^how to object', r'^how to oppose', r'^how to fight',
    r'^how to block', r'^how to challenge', r'^how to contest',
    r'^how to stop', r'^how to successfully',
    r'^how do i object', r'^how do i oppose', r'^how do you object',
    r'^how can i object', r'^how can i oppose',
    # Making/lodging/submitting (process info)
    r'\bmaking\b.*objection', r'\blodging\b', r'\bsubmitting\b.*objection',
    # Opposing/objecting + specific (DIY wording)
    r'^opposing\b', r'^objecting\b',
    # Objections to/for (informational phrasing)
    r'^objections to\b', r'^objections for\b',
    r'^objection to\b',
    # Planning objection + topic (informational)
    r'planning objection.*\b(grounds|reasons|overlooking|privacy|light|amenity|example)',
    r'planning objections.*\b(grounds|reasons|overlooking|privacy|light|amenity|example|material|from neighbours)',
    # Council + objections (looking at council site)
    r'\bcouncil\b.*objection', r'objection.*\bcouncil\b',
    # Specific councils/areas (not service-seeking)
    r'\bwest lancs\b', r'\bwest berkshire\b', r'\buttlesford\b',
    r'\bbromley\b', r'\belmbridge\b', r'\bpeak\b.*planning',
    r'\bdoncaster\b', r'\btrafford\b', r'\bribble\b', r'\bambr\b',
    r'\brbwm\b', r'\brct\b', r'\bwmdc\b', r'\bepping\b',
    # Planning permit (Australian term)
    r'planning permit',
    # How to object to planning application uk (generic)
    r'how to.*planning application uk',
    # Neighbours objecting/planning from neighbours
    r'neighbours?.*objecting', r'objecting.*neighbours?',
    r'from neighbours', r'against neighbours',
    # How to object to neighbours (DIY)
    r'object.*neighbour', r'neighbour.*object',
    # Planning application objections valid reasons
    r'planning application objections valid',
    # Loss of privacy/light/view
    r'loss of privacy', r'loss of light', r'loss of view',
    # Overlooking
    r'\boverlooking\b',
    # Overbearing
    r'\boverbearing\b',
    # Visual/residential amenity
    r'\bamenity\b',
    # Overdevelopment
    r'\boverdevelopment\b', r'\bover development\b',
    # Challenging planning (not service-seeking)
    r'^challenging\b',
    # Contesting planning (bare)
    r'^contesting\b',
    # Fighting planning
    r'^fighting\b',
    # Housing development objections
    r'housing development',
    # Retrospective
    r'\bretrospective\b',
    # Stop planning
    r'^stop planning',
    # Free
    r'\bfree\b',
    # Anonymously
    r'\banonymous',
    # Once granted / after granted
    r'once.*granted', r'after.*granted',
    # Appeal
    r'\bappeal',
    # Dispute
    r'\bdispute\b',
    # Complaint
    r'\bcomplaint',
    # Enforcement/breach
    r'\benforcement\b', r'\bbreach\b',
    # Ombudsman
    r'\bombudsman\b',
    # Petition
    r'\bpetition\b',
    # Overturn
    r'\boverturn',
    # Granted/approved/denied/refused/rejected
    r'\bgranted\b', r'\bapproved\b', r'\bdenied\b', r'\brefused\b', r'\brejected\b',
    # Planning consultant/agent/solicitor/lawyer
    r'\bplanning consultant', r'\bplanning agent', r'\bsolicitor', r'\blawyer',
    # Commenting
    r'\bcommenting\b',
    # Portal
    r'\bplanning portal\b',
    # Pre-app
    r'\bpre.?application',
    # Do i need / how to get planning
    r'do i need planning', r'how to get planning', r'how to apply.*planning',
    # Non-determination / section 78
    r'\bnon.?determination', r'\bsection 78\b', r'\bs78\b',
    # Specific businesses
    r'\baardvark\b', r'\bobjector ai\b',
    # Advice on objecting (could be service-seeking but often informational)
    r'^advice on objecting',
]

def should_exclude(term):
    for pattern in exclude_patterns:
        if re.search(pattern, term, re.IGNORECASE):
            return True
    return False

exclude = []
keep = []
for _, r in nonconv.iterrows():
    term = r['term_lower']
    if should_exclude(term):
        exclude.append(term)
    else:
        keep.append(term)

print(f'EXCLUDE: {len(exclude)}')
print(f'KEEP: {len(keep)}')
print()

# Show what we're keeping (to check nothing wrong)
print(f'=== KEEPING ({len(keep)} terms) ===')
for t in sorted(keep):
    print(f'  "{t}"')
print()

# Organise exclusions by word count
all_exclude = [t for t in sorted(set(exclude)) if len(t.split()) <= 10]

lists = defaultdict(list)
for term in all_exclude:
    wc = len(term.split())
    if wc == 2:
        lists['2 words'].append(term)
    elif wc == 3:
        lists['3 words'].append(term)
    elif wc == 4:
        lists['4 words'].append(term)
    else:
        lists['5+ words'].append(term)

total = 0
for key in ['2 words', '3 words', '4 words', '5+ words']:
    terms = sorted(set(lists.get(key, [])))
    total += len(terms)
    if terms:
        print(f'=== {key} [exact] ({len(terms)} keywords) ===')
        print()
        for t in terms:
            print(f'[{t}]')
        print()

print(f'TOTAL to exclude: {total}')
