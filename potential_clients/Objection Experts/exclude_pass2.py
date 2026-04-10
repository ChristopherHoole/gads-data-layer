import pandas as pd
import re
from collections import defaultdict

st = pd.read_csv('C:/Users/User/Downloads/Search terms report (3).csv', skiprows=2, thousands=',')
st['Cost'] = pd.to_numeric(st['Cost'], errors='coerce')
st['Clicks'] = pd.to_numeric(st['Clicks'], errors='coerce')
st['Conversions'] = pd.to_numeric(st['Conversions'], errors='coerce')
st['Search term'] = st['Search term'].str.strip()
st = st[~st['Search term'].str.startswith('Total:')]

converting = set(st[st['Conversions'] > 0]['Search term'].str.lower().values)
nonconv = st[st['Conversions'] == 0].copy()
nonconv['term_lower'] = nonconv['Search term'].str.lower()
nonconv_dedup = nonconv.groupby('term_lower').agg({
    'Cost': 'sum', 'Clicks': 'sum', 'Impr.': 'sum', 'Search term': 'first'
}).reset_index()
nonconv_dedup = nonconv_dedup[~nonconv_dedup['term_lower'].isin(converting)]
print(f'Non-converting unique: {len(nonconv_dedup)}')

exclude_patterns = [
    # Templates/samples/examples/format/wording (DIY)
    r'\btemplate\b', r'\bsample\b', r'\bexample\b', r'\bformat\b', r'\bwording\b',
    # How to write/draft (DIY)
    r'how to write', r'how to draft', r'writing a', r'write an objection',
    r'write a planning', r'letter of objection', r'letters of objection',
    r'sample letter', r'example letter',
    # Objection letter (DIY intent - writing their own)
    r'planning permission objection letter', r'planning application objection letter',
    r'objection letter to planning', r'objection letter for planning',
    r'letter.*opposing planning', r'letter opposing',
    r'objection letter$',
    # How many needed (informational)
    r'how many.*needed', r'how many.*to stop', r'how many.*refuse',
    r'how many objections', r'how many planning',
    # How long / timescale (informational)
    r'how long.*to object', r'how long.*have to', r'how long.*appeal',
    # Anonymously
    r'\banonymous',
    # View/see/check objections (applicants)
    r'can i see.*objection', r'can you see.*objection', r'can you view',
    r'view.*objection', r'read.*objection', r'check.*objection',
    # Who can object (informational)
    r'^who can object', r'^who can oppose',
    r'^can i object\b', r'^can you object\b',
    r'^can neighbours? object', r'^can a neighbour object',
    # What grounds/reasons (informational research)
    r'^what are valid', r'^what are.*reasons', r'^what grounds',
    r'^what reasons', r'^on what grounds', r'^what is a valid',
    r'^what is a holding', r'^what can you object', r'^what can i object',
    # Valid/legitimate/best/successful (informational research)
    r'^valid reasons', r'^valid objections',
    r'^legitimate.*objection', r'^legitimate.*planning',
    r'^best objections',
    r'^successful.*objection', r'^successful.*planning',
    # Reasons/grounds for objecting (informational)
    r'^reasons for objecting', r'^reasons to object',
    r'^reasons for planning objection', r'^reasons for planning objections',
    r'^grounds for objecting', r'^grounds for planning',
    r'^grounds to object', r'^grounds for opposing',
    # How to block/fight (vague, not seeking professional help)
    r'how to block', r'how to fight',
    # Planning consultants/agents/solicitors/lawyers
    r'\bplanning consultant', r'\bplanning consultants',
    r'\bplanning agent', r'\bsolicitor\b', r'\bsolicitors\b',
    r'\blawyer\b', r'\blawyers\b',
    # Specific council/area searches (looking at council not service)
    r'\bribble valley\b', r'\bwmdc\b', r'\brct\b', r'\bepping forest\b',
    r'\bamber valley\b', r'\btrafford\b', r'\bdoncaster\b', r'\bpeak park\b',
    r'\brbwm\b', r'\bsolihull\b', r'\bcamden\b(?!.*objection)',
    r'\bbromley\b(?!.*objection)', r'\bharingey\b',
    r'\bnorwich\b(?!.*objection)', r'\bpembrokeshire\b',
    r'\bwalsall\b(?!.*objection)', r'\bwoking\b',
    r'\bwandsworth\b(?!.*objection)', r'\bwarwickshire\b(?!.*objection)',
    r'\bpeterborough\b(?!.*objection)', r'\byorkshire\b(?!.*objection)',
    r'\bcambridgeshire\b(?!.*objection)', r'\bdorset\b(?!.*objection)',
    r'\bcornwall\b(?!.*objection)', r'\bsuffolk\b(?!.*objection)',
    r'\bliverpool\b(?!.*objection)', r'\bleeds\b(?!.*objection)',
    r'\bbristol\b(?!.*objection)', r'\bcambridge\b(?!.*objection)',
    r'\bherefordshire\b(?!.*objection)', r'\bbrighton\b(?!.*objection)',
    r'\bmarket drayton\b', r'\bnorth wales\b(?!.*objection)',
    # Cost/fees
    r'how much.*cost', r'how much.*charge', r'how much is',
    r'\bcost of\b', r'\bfees?\b(?!.*objection)',
    # Commenting
    r'\bcomment\b.*planning', r'\bcommenting\b', r'\bcomments\b.*planning',
    # Enforcement/breach
    r'\benforcement\b', r'\bbreach\b',
    # Building regs/portal
    r'\bbuilding reg', r'\bplanning portal\b',
    # Pre-app
    r'\bpre.?application\b',
    # Retrospective (applying not objecting)
    r'retrospective planning permission(?!.*object)', r'apply.*retrospective',
    # Do I need planning / how to get planning (applicant)
    r'do i need planning', r'do you need planning', r'need planning permission',
    r'how to get planning', r'how to apply.*planning', r'how to win planning',
    r'how to get around',
    # Material considerations (informational)
    r'\bmaterial.*objection', r'\bmaterial.*consideration', r'\bmaterial.*planning',
    # Visual/residential amenity (informational)
    r'\bvisual amenity\b', r'\bresidential amenity\b', r'\bamenity\b',
    # Light pollution / loss of light (informational)
    r'\blight pollution\b', r'loss of light',
    # Overlooking (informational)
    r'\boverlooking\b',
    # Overdevelopment
    r'\boverdevelopment\b', r'\bover development\b',
    # Overbearing (informational)
    r'\boverbearing\b',
    # Other businesses
    r'\basbri\b', r'\bplanning voice\b', r'\bet planning\b', r'\bplande\b',
    # Specific structures
    r'\bconservatory\b', r'\bloft\b', r'\bdormer\b', r'\bcaravan\b',
    r'\bshed\b', r'\bgarden room\b',
    # Wiki/forum/blog/pdf
    r'\bwiki', r'\bforum\b', r'\bblog\b', r'\bpdf\b', r'\bdownload\b',
    # S78/non-determination
    r'\bsection 78\b', r'\bs78\b', r'\bnon.?determination\b',
    # Certificate/ownership/resubmission
    r'\bcertificate\b', r'\bownership\b', r'\bresubmission\b',
    # Neighbours objecting/commenting (informational about process)
    r'^neighbours? objecting', r'neighbours? comments?\b',
    # Once/after granted
    r'once.*granted', r'after.*granted',
    # How to object (bare - informational not service-seeking)
    r'^how to object to planning$',
    r'^how to object to a planning application$',
    r'^how do i object to a planning application$',
    r'^how to oppose planning application$',
    # Making/lodging (process info)
    r'how to make.*objection', r'how to lodge', r'making an objection',
    # Planning objections + specific topic (informational)
    r'planning objections?\s+overlooking', r'planning objections?\s+garden',
    r'planning objections?\s+material', r'planning objections?\s+reasons',
    # Specific vague terms
    r'^objections to planning$', r'^objecting to planning$',
    r'^objection to planning$', r'^planning objections$',
    r'^planning application$', r'^planning permission$',
    r'^planning applications objections$',
    # HMO objection letter (DIY)
    r'hmo objection letter',
    # Fighting planning (vague)
    r'^fighting planning',
    # Contest planning permission (bare)
    r'^contest planning permission$',
    # Stop planning permission (bare)
    r'^stop planning permission$',
    # Challenging a planning decision (more appeal territory)
    r'challenging a planning decision',
    # Neighbours extensions (informational)
    r'valid objections.*neighbour', r'neighbour.*extension',
    # Planning permission denied
    r'\bdenied\b',
    # Objecting to planning permission uk (too vague)
    r'^objecting to planning permission uk$',
    r'^objecting to a planning application uk$',
    # How to object a planning application (vague)
    r'^how to object a planning application$',
    # How do you object (informational)
    r'^how do you object',
    r'^how do i object to planning permission$',
    r'^how do i oppose',
    # How to contest (vague)
    r'^how to contest',
    # How to challenge planning permission (vague)
    r'^how to challenge planning permission$',
    # Oppose (bare terms)
    r'^how to oppose planning permission$',
    r'^how to oppose a planning application$',
    # Letters (DIY)
    r'^planning objection letters$',
    r'^objection letter for planning permission$',
    r'^objection letter to planning applications$',
    r'^writing an objection to a planning application$',
    r'^planning objection letter$',
]

def should_exclude(term):
    for pattern in exclude_patterns:
        if re.search(pattern, term, re.IGNORECASE):
            return True
    return False

nonconv_dedup['exclude'] = nonconv_dedup['term_lower'].apply(should_exclude)
nonconv_dedup['word_count'] = nonconv_dedup['term_lower'].str.split().apply(len)

exclude = nonconv_dedup[(nonconv_dedup['exclude'] == True) & (nonconv_dedup['word_count'] <= 10)]
exclude = exclude[~exclude['term_lower'].isin(converting)]

print(f'EXCLUDE: {len(exclude)} terms')
print(f'KEEP: {len(nonconv_dedup) - len(exclude)} terms')
print()

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
