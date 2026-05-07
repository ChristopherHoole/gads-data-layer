# Cross-Level Negatives — Near Me Campaign

**Built:** Wed 29 Apr 2026
**Purpose:** Two layers of negative-keyword protection for the Near Me campaign.

---

## Layer 1 — Campaign-level negatives (junk filter)

Add these as **negatives at the campaign level** so they apply across all 7 ad groups. These are the off-not-advertised / wrong-intent / wrong-audience terms surfaced by April's data.

Match types as labelled. Add as one block to a new campaign-level negative list called **"Near Me — Campaign Junk"**.

### NHS / public / free-clinic intent (off-not-advertised)
DBD is private. NHS / free intent will not convert.

```
nhs                          [phrase]
free                         [phrase]
free dental                  [phrase]
free consultation            [phrase]
charity                      [phrase]
charities                    [phrase]
government                   [phrase]
public                       [phrase]
community                    [phrase]
dental school                [phrase]
dental schools               [phrase]
dental hospital              [phrase]
clinical trial               [phrase]
clinical trials              [phrase]
paid clinical                [phrase]
trial                        [phrase]
```

### Wrong-service / off-not-advertised (per `rule_7_exclude_tokens`)
Things DBD doesn't do.

```
sedation                     [phrase]
flipper                      [phrase]
fillings                     [phrase]
extraction                   [phrase]
extractions                  [phrase]
root canal                   [phrase]
braces                       [phrase]
invisalign                   [phrase]
aligners                     [phrase]
whitening                    [phrase]
hygienist                    [phrase]
cleaning                     [phrase]
gum graft                    [phrase]
gum grafting                 [phrase]
maxillofacial                [phrase]
orthodontic                  [phrase]
orthodontist                 [phrase]
orthodontists                [phrase]
periodontist                 [phrase]
periodontal                  [phrase]
emergency                    [phrase]
24 hour                      [phrase]
24/7                         [phrase]
denture repair               [phrase]
denture                      [phrase]   ← see note below
dentures                     [phrase]   ← see note below
mobile dentist               [phrase]
domiciliary                  [phrase]
veneers                      [phrase]
composite bonding            [phrase]
composite                    [phrase]
crown                        [phrase]
crowns                       [phrase]
teeth whitening              [phrase]
```

**Denture note:** Decide before launch — does DBD offer implant-supported dentures? If YES, only block `denture repair` / `cheap dentures` / `nhs dentures`, not the root word. If NO, block both.

### Wrong-audience
Children, students, very specific demographic intent.

```
children                     [phrase]
child                        [phrase]
kids                         [phrase]
student                      [phrase]
students                     [phrase]
seniors                      [phrase]
senior citizens              [phrase]
elderly                      [phrase]
mobile dentist for           [phrase]
in home dental               [phrase]
in home                      [phrase]
home visit                   [phrase]
```

### Wrong-location (NOT in DBD's targeted postcodes)
Pulled from April search-term junk. UK cities/towns DBD doesn't target.

```
crewe                        [exact]
newcastle                    [exact]
manchester                   [exact]
birmingham                   [exact]
liverpool                    [exact]
glasgow                      [exact]
edinburgh                    [exact]
bristol                      [exact]
leeds                        [exact]
sheffield                    [exact]
cardiff                      [exact]
belfast                      [exact]
```

**Removed from this list (locked Wed 29 Apr):** `hackney`, `uxbridge` — both inside M25, kept as targetable.

### Other junk
Branded competitors, navigational, clinical-trial seekers.

```
bupa                         [phrase]
denplan                      [phrase]
smilewhite                   [phrase]
dentaprime                   [phrase]
toothclub                    [phrase]
tooth club                   [phrase]
the tooth club               [phrase]
register                     [phrase]
registering                  [phrase]
register at                  [phrase]
sign up                      [phrase]
how to find                  [phrase]
who is the best              [phrase]
review                       [phrase]   ← optional, debatable. excludes "reviews of dental implants near me" which is legit
near me near me              [phrase]   ← Google's own broken parse, low quality
nearby near me               [phrase]
```

### Romanian / Polish / non-English-language searcher signals
Surfaced in April data — non-English-speaking searcher intent generally low-converting for DBD.

```
polski                       [phrase]
romanian dentist             [phrase]
turkish dentist              [phrase]
indian dentist               [phrase]
south african                [phrase]
clinica                      [phrase]
cerca de mi                  [phrase]
```

---

## Layer 2 — Ad-group-level negatives (cross-group shield)

These prevent the **catchall ad group** from cannibalising the **specific ad groups**. Add each specific ad group's defining tokens as negatives on the catchall ad group.

### Negatives on Ad Group 7 — Catchall

So that searches matching Ad Groups 1-6 fall to those ad groups, not the catchall.

```
clinic                       [phrase]   ← shields AG1 (Implant Clinic)
centre                       [phrase]   ← shields AG1
center                       [phrase]   ← shields AG1
practice                     [phrase]   ← shields AG1
specialists                  [phrase]   ← shields AG1
surgeon                      [phrase]   ← shields AG1
full mouth                   [phrase]   ← shields AG2 (Full Mouth)
full arch                    [phrase]   ← shields AG2
full dental                  [phrase]   ← shields AG2
full set                     [phrase]   ← shields AG2
all on 4                     [phrase]   ← shields AG2
all on four                  [phrase]   ← shields AG2
all-on-4                     [phrase]   ← shields AG2
whole mouth                  [phrase]   ← shields AG2
replace all                  [phrase]   ← shields AG2
reconstruction               [phrase]   ← shields AG2
same day                     [phrase]   ← shields AG3 (Same Day)
one day                      [phrase]   ← shields AG3
immediate                    [phrase]   ← shields AG3
teeth in a day               [phrase]   ← shields AG3
single tooth                 [phrase]   ← shields AG4 (Single Tooth)
one tooth                    [phrase]   ← shields AG4
tooth replacement            [phrase]   ← shields AG4
missing tooth                [phrase]   ← shields AG4
front tooth                  [phrase]   ← shields AG4
molar                        [phrase]   ← shields AG4
pay monthly                  [phrase]   ← shields AG5 (Finance)
finance                      [phrase]   ← shields AG5
0 finance                    [phrase]   ← shields AG5
payment plan                 [phrase]   ← shields AG5
payment plans                [phrase]   ← shields AG5
monthly payment              [phrase]   ← shields AG5
monthly payments             [phrase]   ← shields AG5
spread the cost              [phrase]   ← shields AG5
teeth fixing                 [phrase]   ← shields AG6 (Teeth Fixing)
fix my teeth                 [phrase]   ← shields AG6
fix teeth                    [phrase]   ← shields AG6
fix my smile                 [phrase]   ← shields AG6
get my teeth fixed           [phrase]   ← shields AG6
```

### Negatives on Ad Groups 1-6 (specific) — none cross-group

The specific ad groups don't need negatives against each other because their keywords are specific enough that intent doesn't bleed (e.g. someone searching "same day implants near me" won't accidentally trigger Full Mouth's "full mouth dental implants near me"). Match-type discipline (Phrase + Exact only) handles it.

**Exception — Single Tooth (AG4) needs to shield against Full Mouth (AG2):**
Add to AG4 only:
```
full mouth                   [phrase]
full arch                    [phrase]
all on 4                     [phrase]
```
Reason: "tooth replacement near me" could be misread by Google as relevant to "full mouth tooth replacement" — block that path.

---

## Layer 3 — Account-level negatives (already in place)

Don't re-add these here. They're already on the account-level neg lists from Pass 1+2 daily triage:

- Domain rule: brand competitors, clinic-name searches
- Location-check rule: anything outside DBD's 270-postcode target list
- The 5,000+ negs accumulated since 20 Apr automation went live

These flow through automatically.

---

## Implementation order

1. **First:** create campaign-level negative list "Near Me — Campaign Junk" in Google Ads. Paste Layer 1 in.
2. **Second:** attach the list to the new Near Me campaign.
3. **Third:** at the catchall ad group (AG7), add Layer 2 negatives directly (not via shared list — these are catchall-specific).
4. **Fourth:** at AG4 (Single Tooth), add the 3-line full-mouth shield directly.

## Decisions locked Wed 29 Apr

1. **Denture word:** OPEN — bringing to 16:30 call with Giulio. Until confirmed, don't block `denture` / `dentures` root words. Only block `denture repair` / `mobile dentist` / `nhs dentures` (already in list).
2. **Hackney / Uxbridge:** both inside M25 — KEEP (targetable, not blocked).
3. **`review` / `reviews`:** KEEP (don't block — commercial intent on review-stage queries).
4. **`cheap` / `cheapest`:** KEEP (don't block — April data shows them converting; tCPA filters the rest).

---

## Total counts

- Layer 1 (campaign): ~95 negatives
- Layer 2 (catchall ad group): 38 shields
- Layer 2 (AG4 single-tooth): 3 shields
- **Net new add: 136 negatives**

This is a one-time setup. Day-2 onwards, fresh negatives flow through normal Pass 1+2 triage.
