import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load v3 blocks (new, aggressive)
with open('_apr13_v3.txt','r',encoding='utf-8') as f:
    v3 = f.read()
# Load prior blocks that user already added (apr13 first version)
with open('_apr13_final.txt','r',encoding='utf-8') as f:
    prior = f.read()

def extract_by_cat(text):
    out = {'1_word':[], '2_word':[], '3_word':[], '4_word':[], '5plus_word':[]}
    cur = None
    for line in text.splitlines():
        m = re.match(r'### (\S+)', line)
        if m:
            cur = m.group(1) if m.group(1) in out else None
            continue
        m = re.match(r'\[([^\]]+)\]', line)
        if m and cur:
            out[cur].append(m.group(1))
    return out

v3_b = extract_by_cat(v3)
prior_b = extract_by_cat(prior)

for k in ['1_word','2_word','3_word','4_word','5plus_word']:
    prior_set = set(prior_b[k])
    new_adds = [t for t in v3_b[k] if t not in prior_set]
    print(f'\n### {k}: {len(new_adds)} NEW additions ###')
    for t in new_adds:
        print(f'[{t}]')

total_new = sum(len([t for t in v3_b[k] if t not in set(prior_b[k])]) for k in ['1_word','2_word','3_word','4_word','5plus_word'])
print(f'\nTOTAL NEW: {total_new}')
