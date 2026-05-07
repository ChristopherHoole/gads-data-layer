"""Find phrase negs that would block new campaign keywords.
Phrase neg "X" blocks query "Y" iff X appears as a contiguous substring of Y.
"""
import duckdb, re
DB = r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb'
con = duckdb.connect(DB, read_only=True)

NEW_KWS = [
    "dental implant clinic near me","dental implants clinic near me","dental implant centre near me",
    "dental implant center near me","dental implant practice near me","implant clinic near me",
    "implant centre near me","implant dentist near me","best dental implant clinic near me",
    "dental implant specialists near me","dental implant surgeon near me","top rated implant dentist near me",
    "dental implant surgery near me","dental implant specialist near me","local implant dentist",
    "implant dentist nearby","local dental implant clinic","nearest dental implant clinic",
    "dental implant dentist near me",
    "full mouth dental implants near me","full mouth implants near me","full dental implants near me",
    "full arch dental implants near me","full mouth reconstruction near me","all on 4 dental implants near me",
    "all on 4 implants near me","all on four dental implants near me","all on 4 near me",
    "full set of teeth near me","replace all teeth near me","whole mouth implants near me",
    "same day dental implants near me","same day implants near me","same day implant near me",
    "one day dental implants near me","immediate dental implants near me","24 hour dental implants near me",
    "teeth in a day near me","same day tooth replacement near me",
    "tooth replacement near me","single tooth implant near me","single tooth replacement near me",
    "tooth implant near me","tooth implants near me","tooth implant dentist near me",
    "missing tooth replacement near me","front tooth implant near me","molar implant near me",
    "one tooth implant near me","replace one tooth near me","single dental implant near me",
    "pay monthly dental implants near me","dental implants on finance near me","dental implants payment plan near me",
    "dental implants 0 finance near me","finance dental implants near me","payment plans for dental implants near me",
    "dental implants monthly payments near me","spread the cost dental implants near me",
    "dentist with payment plans near me",
    "teeth fixing near me","fix my teeth near me","fix teeth near me","fixed teeth near me",
    "get my teeth fixed near me","fix my smile near me",
    "dental implants near me","dental implant near me","implants near me","teeth implants near me",
    "tooth implants near me","dental implants in my area","dental implants nearby",
    "dental implants close to me","local dental implants","affordable dental implants near me",
    "best dental implants near me","cheap dental implants near me","dental implants cost near me",
    "dental implant prices near me","dental implants UK near me",
    "dental implants local","dental implants closest to me",
]

# Pull unique phrase negs from linked lists
neg_rows = con.execute("""
    SELECT DISTINCT k.keyword_text, l.list_name
    FROM act_v2_negative_list_keywords k
    JOIN act_v2_negative_keyword_lists l ON k.list_id = l.list_id
    WHERE k.client_id='dbd001'
      AND k.match_type = 'PHRASE'
      AND l.is_linked_to_campaign = TRUE
""").fetchall()
print(f"Unique phrase negs in linked lists: {len(neg_rows)}")

# Group by phrase
phrase_to_lists = {}
for txt, lname in neg_rows:
    txt_l = (txt or '').strip().lower()
    if not txt_l: continue
    phrase_to_lists.setdefault(txt_l, set()).add(lname)

print(f"Unique phrases: {len(phrase_to_lists)}")

# For each new keyword, find phrase negs that are substrings (with word boundary)
print("\n" + "="*90)
print("REAL conflicts: phrase negs that are substrings of new campaign keywords")
print("="*90)

real_conflicts = []
for kw in NEW_KWS:
    kwl = kw.lower()
    for phrase, lists in phrase_to_lists.items():
        if not phrase or len(phrase) < 3: continue
        # Substring with word boundary
        if re.search(r'\b' + re.escape(phrase) + r'\b', kwl):
            real_conflicts.append((kw, phrase, lists))

if not real_conflicts:
    print("\n✅ ZERO real conflicts. New campaign keywords are NOT blocked by any account-level phrase neg.")
else:
    print(f"\n⚠️  {len(real_conflicts)} conflicts found:\n")
    by_neg = {}
    for kw, phrase, lists in real_conflicts:
        by_neg.setdefault(phrase, []).append((kw, lists))
    for phrase, items in sorted(by_neg.items()):
        kws = sorted(set(k for k,_ in items))
        lists = set()
        for _, ls in items: lists.update(ls)
        print(f"\n  NEG '{phrase}' (in: {', '.join(sorted(lists))})")
        print(f"    blocks {len(kws)} keyword(s):")
        for k in kws[:8]:
            print(f"      - {k}")
        if len(kws) > 8: print(f"      ... +{len(kws)-8} more")

con.close()
