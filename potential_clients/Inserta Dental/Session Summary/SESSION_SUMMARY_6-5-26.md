# DBD Session Summary — Wed 6 May 2026

## Headline
Continued GAds rebuild + ad audit. Split New Teeth CORE into 3 (added Tooth Replacement + Teeth Replacement parents). 5 more ad groups audited. Daily PMax→DII redirect + search-term triage live as routine.

## PMax → DII redirect (Day 2)
- Yesterday's PMax search-term CSV (5 May data) processed
- 14 terms total had matching `[ex]` keywords across the full DII campaign — only 5 had cost > £0.57
- High-cost matches added to PMax-only neg list:
  - [full teeth replacement cost], [i want to fix my teeth], [screwless dental implant cost], [screwless dental implants uk cost]
- Plus 10 zero-cost matches negged defensively (anything covered by DII gets blocked from PMax regardless of cost)
- ~£104 of 1-day PMax spend redirected (mostly the £100 `i want to fix my teeth` match)

## Daily search-term triage
- 189 negs pushed today (snapshot 5/5, analysis 6/5)

## GAds rebuild — 2 new parents shipped (split from New Teeth CORE)
- **05_Tooth_Replacement** (NEW) — 1 ad group, 10 keywords, 3 RSAs, 1 LP at /google/tooth-replacement
- **06_Teeth_Replacement** (NEW) — 1 ad group, 10 keywords, 3 RSAs, 1 LP at /google/teeth-replacement
- Folder structure: all 28 prior parents renumbered (everything 05+ shifted down by 2). Sequence is now 01-30.
- 20 keywords manually moved in GAds UI from `[ex] New Teeth - CORE` → 10 to `[ex] Tooth Replacement - CORE`, 10 to `[ex] Teeth Replacement - CORE`
- `[ex] New Teeth - CORE` now has 8 keywords (down from 28) — much easier to score Excellent on re-audit

**Cumulative build totals: 36 LPs / 33 ad groups across 8 parents (01-12 sequence, with 06 Vivo skipped).**

## Ad audit — 5 more ad groups done today
The "every keyword in headlines (or descriptions for too-long kws)" rule continues. Per ad: 15 new headlines + 4 new descriptions. Chris swaps in via GAds UI until ad strength flips Excellent.

**Critical learning today:** Chris flagged that descriptions were keyword-stuffed. Locked rule: descriptions must read **naturally** with keywords woven in organically — not stuffed. Quality Score values keyword presence but Google Ads Editor's "natural language" check matters too.

✅ Done today (5):
1. Fix My Teeth - LOCATION (3 ads, 4 kws)
2. General Implants - COST (3 ads, 26 kws — too many to fit per-ad, used SHARED 15 HLs + per-ad descs to cover ad-group level)
3. General Implants - FINANCE (3 ads, 21 kws — same approach)
4. Smile - LOCATION (3 Average ads, 5 kws)
5. Screwless - INFO (3 Average ads, 5 kws — 4 too long for HLs, all covered in descs)

**Cumulative ad audit done: 17 of 28+ ad groups across 2 days.**

⏳ Remaining for next session:
- All on 4 - INFO (Average — only 1 ad needs work)
- New Teeth - CORE (post-split, 8 kws — needs re-audit)
- New Teeth - COST (Average — needs re-audit after split)
- Tooth Replacement - CORE (NEW — built today, ad audit pending)
- Teeth Replacement - CORE (NEW — built today, ad audit pending)
- Full Mouth - LOCATION (Good x2 — upgrade to Excellent)
- General Implants - INFO (Average/Good)
- General Implants - LOCATION (Good/Average)
- General Implants - NHS (Good x1)
- Screwless - CORE (Good/Average)
- Screwless - COST (Good x3)
- Screwless - LOCATION (Good/Poor)

## Files updated
- `Campaigns/05_Tooth_Replacement/` (NEW)
- `Campaigns/06_Teeth_Replacement/` (NEW)
- All 28 prior folders renumbered (everything 05+ shifted)
- New generator: `data/search_terms_audit_2026/generate_tooth_teeth_replacement_uploads.py`

## Hours
~6h AM session

---

# AFTERNOON SESSION — Build Wave 1 COMPLETE

## Headline
First wave of the GAds rebuild done. Final cumulative: **60 LPs / 57 ad groups / 23 parents built.** 5 parents pending Giulio sign-off, 3 strategically skipped.

## Parents built this afternoon (10)
- **14_Single_Arch** (1 ag, 4 kws) — thin parent, mostly invisalign noise stripped
- **15_Double_Arch** (1 ag, 5 kws)
- **16_Full_Arch** (3 ag CORE/COST/LOCATION, 30 kws)
- **17_Upper_Jaw** (2 ag CORE/COST, 39 kws — top kw `dental implant upper teeth` 66 clicks!)
- **18_Lower_Jaw** (2 ag CORE/COST, 28 kws)
- **19_Implants_for_Elderly** (4 ag CORE/COST/LOCATION/NHS, 30 kws — explicit "we are private clinic" positioning to set price expectations against £6,995). Top kw `dental implants cost for seniors uk` 385 clicks / £261 — biggest single LOCATION kw in the audit DB.
- **20_Implant_+_Bridge** (3 ag CORE/COST/LOCATION, 44 kws) — **renamed from Hybrid_Bridge** to be explicit about the implant+bridge combo. Folder name uses literal `+` symbol per Chris.
- **21_Implant_Clinic** (2 ag CORE/LOCATION, 34 kws) — top kw `dental implant clinic near me` 385 clicks / £1,305 spend (biggest single LOCATION kw in entire audit). **478 competitor brand kws stripped** (brighton/chiswick/dental art/harley street/etc.) for separate competitor wave (needs Giulio sign-off).
- **22_Bone_Graft** (3 ag CORE/COST/LOCATION, 53 kws)
- **23_Implant_Replacement** (1 ag, 23 kws) — **renamed from Failed_Implants** for action-oriented user search intent. Bundles CORE + LOCATION + COST since volume too thin to split.
- **30_NHS_Implants** (2 ag CORE/COST, 28 kws) — Giulio signed off mid-afternoon. Replaces existing `[ex] General Implants - NHS` ad group (which only had 25 kws and missed ~£1,500 of NHS volume including `how to apply for dental implants on nhs` 510 clicks).

## Skipped strategic decisions (3 parents)
- **25_Fixed_Teeth** — heavy overlap with other parents + top kw `fixed teeth solutions` is a competitor brand
- **26_Comparison_Shoppers** — 1199 kws all competitor brands (dentaprime/banning/etc.). Bank for competitor wave.
- **08_Vivo_Bridge** — already skipped earlier per Giulio

## Pending Giulio sign-off (4 parents — banked for email tomorrow AM)
- **24_Nobel_Biocare** (LP file built, not pushed live, ready when approved)
- **27_Implant_Denture**
- **28_Zygomatic_Pterygoid**
- **29_Straumann**

## NEW LOCKED RULES (this session)

### Rule: No em-dashes
**No em-dashes (`—`) anywhere in LP copy, ad headlines, descriptions, or CSVs — only regular hyphens (`-`).** Em-dashes are an AI-generated tell. Going forward, all new content uses regular hyphens. **Retro-fix audit banked for tomorrow (Thu 7 May) AM after search-term triage**: sweep `apps/web/src/pages/google/*.astro` + all `Campaigns/*/_csv_*.csv` + all GAds ad audit headline/description files for `—` and replace with `-`.

### Rule: RSA count validation
Every RSA must have exactly 15 headlines + 4 descriptions. Caught a bug in Implant Clinic LOCATION RSA3 where 16 HLs caused the 16th to overflow into Description 1 column. Added count validation to all generators going forward.

### Rule: Competitor brand bidding (banked)
Bidding on competitor clinic names (brighton implant clinic / chiswick dental / dental art / harley street / fixed teeth solutions / dentaprime / banning) requires separate ad group structure + Giulio sign-off. Bank for "competitor wave" — discuss with Giulio first.

### Rule: Tooth_Replacement / Teeth_Replacement / Implant_+_Bridge / Implant_Replacement
Folder/ad group naming convention extended:
- `20_Implant_+_Bridge` (folder uses literal `+` to make implant+bridge combo explicit in GAds UI)
- `23_Implant_Replacement` (renamed from Failed_Implants to be action-oriented)

## Manual GAds UI steps banked for tomorrow AM (after triage)

1. **Delete `[ex] General Implants - NHS` ad group** (25 kws). 5 missing kws need to be added to new 30_NHS_Implants CSV before importing:
   - **CORE**: `implants teeth nhs`, `nhs dental implants near me`, `nhs dental implant eligibility`
   - **COST**: `nhs dental implants cost`, `teeth implants cost uk nhs`
2. **Import all 23 new parent CSV bundles** (`Campaigns/01-23` + `30_NHS_Implants/_csv_*.csv`)

## Other tomorrow AM tasks banked
- Email Giulio for sign-off on 4 pending brand parents (24/27/28/29)
- Em-dash retro-fix audit
- **Legacy DII keyword audit**: sweep existing ad groups in DII campaign for any kws not yet covered by the new structure (Chris flagged this is the next priority after build complete)

## Other still-banked from earlier sessions
- Resume ad audit on remaining 12 ad groups (Tooth/Teeth Replacement CORE post-rebuild, New Teeth post-split CORE/COST, All on 4 INFO, Full Mouth LOCATION, General Implants INFO/LOCATION, Screwless CORE/COST/LOCATION)
- Pricing confirmations needed from Giulio: implant bridge tiers (£4,500 / £5,500 / £6,500 estimates used), bone graft (£400-£1,500), sinus lift (£900-£2,000), implant replacement (£695 crown only / £1,695 full)

## Files updated
- `Campaigns/14_Single_Arch/`, `15_Double_Arch/`, `16_Full_Arch/`, `17_Upper_Jaw/`, `18_Lower_Jaw/`, `19_Implants_for_Elderly/`, `20_Implant_+_Bridge/` (renamed), `21_Implant_Clinic/`, `22_Bone_Graft/`, `23_Implant_Replacement/` (renamed), `30_NHS_Implants/` — all NEW
- `Campaigns/_PLAN_subgroups.md`, `_LP_URLS.md`, `_MORNING_REVIEW.md` — updated for renames
- 10 new generator scripts in `data/search_terms_audit_2026/generate_*_uploads.py`
- 25 new LPs in `dentalbydesign-repo/apps/web/src/pages/google/*.astro` (1 unpushed: nobel-biocare-dental-implants.astro)

## Hours total today
~12h (6h AM + 6h PM)

---

# EVENING / PAST MIDNIGHT — Keyword audit + Poor ad audit (same continuous session, ran past midnight)

## Headline
After build wave 1 wrapped, did big legacy keyword audit (mapped 720+ kws from 4 CSV exports against new [ex] structure), restructured Campaigns folder, and started Poor ad audit (13 of 32 ads done).

## 5. 30_NHS_Implants parent build (built late afternoon, but logging here for completeness)
- 2 ad groups: `[ex] NHS Implants - CORE` (18 kws) + `[ex] NHS Implants - COST` (10 kws)
- 1 new LP `/google/dental-implants-nhs-cost` (CORE reuses existing `/google/dental-implants-nhs`)
- Generator + 3 CSVs
- Replaces existing `[ex] General Implants - NHS` ad group (manual GAds UI cleanup banked for tomorrow AM)
- "Not published" awkward phrasing in 4 descriptions rewritten to natural prose

## 6. Legacy keyword audits — 4 CSVs against new [ex] structure
Goal: ensure every kw from paused legacy DII ad groups is either added to [ex] OR banked for new ad group. No shoe-horning.

**CSV 39** — 204 rows / 81 unique kws (`Implants Cost Google`, `Dental Implants Google`, `All on 4 Google`, `Implants Cost`, `Dental Implants Hammersmith`, `Financing`, `Dental Implants`, `All on 4`)
- 66 fit existing [ex] / 12 banked for NEW Affordable Implants / 4 banked for 27 Implant Denture (pending) / 3 banked for new sub-groups / 7 no-fit

**CSV 40** — 160 rows / 123 unique kws (6 paused ad groups incl. `[paused] *Dental Implants Near Me`, `[paused] All on 4 Implants`, `[paused] Full Mouth Implants`, etc.)
- 5 NHS kws confirmed missing from new 30_NHS_Implants ad groups (added to backlog)

**CSV 41** — 800 [ex] keywords across 47 ad groups dumped to `/tmp/ex_kws.txt` for substring matching reference

**CSV 42** — 151 rows / 81 unique kws (all "near me" themed)
- 71 to existing LOCATION / NEW Tooth Replacement - LOCATION (8) / NEW Affordable Implants - LOCATION (4) / 4 no-fit

**CSV 43** — 555 rows / 434 unique kws (21 themed paused ad groups: `*Best Dental Implants`, `*Implants vs Dentures`, `*Molar Implant`, `*Dental Implants Finance`, etc.)
- Heavy banking: NEW Affordable Implants (~16), NEW Molar Replacement (~16), NEW Hate Dentures (~17), NEW Dental Reconstruction (~14), NEW Missing Teeth (~8)
- ~17 banked as comparison/review

## 7. Keyword additions to existing [ex] ad groups — ~150+ kws
Notable expansions:
- 03 General Implants: 35 FINANCE + 32 LOCATION + 6 COST kws (biggest expansion)
- 21 Implant Clinic: ~25 LOCATION + 1 CORE kws
- 02 Full Mouth: ~17 CORE + ~6 COST + ~9 LOCATION kws
- 01 All on 4: 14 kws across CORE/COST/LOCATION
- 13 All on 6: 14 kws across CORE/COST/LOCATION (full sub-group expansion)
- 30 NHS Implants: 6 missing kws added during build
- Plus smaller additions to 04, 05, 06, 09, 10, 12, 14, 16, 17, 18, 23

## 8. Strict substring rule reinforced
Pulled up multiple times for force-fitting kws into wrong ad groups (e.g. "implant dentist" doesn't fit Implant Clinic; "front tooth implant" doesn't fit Tooth Replacement; "best implant dentist" doesn't fit Implant Clinic CORE). **Locked rule**: kws must contain parent's anchor word as substring (clinic for Implant Clinic, replace for Tooth/Teeth Replacement, full mouth/mouth for Full Mouth, same day for Same Day Teeth, etc.). When in doubt, BANK rather than force-fit. **Don't fabricate prices** in ad copy — only confirmed anchors (£1,695 single tooth, £6,995 arch, £10,995 full mouth).

## 9. Folder restructure
**Renamed 6 on-hold parents** (removed order number, added `[on hold]` prefix):
- `24_Nobel_Biocare` → `[on hold] Nobel_Biocare`
- `25_Fixed_Teeth` → `[on hold] Fixed_Teeth`
- `26_Comparison_Shoppers` → `[on hold] Comparison_Shoppers`
- `27_Implant_Denture` → `[on hold] Implant_Denture`
- `28_Zygomatic_Pterygoid` → `[on hold] Zygomatic_Pterygoid`
- `29_Straumann` → `[on hold] Straumann`

**Created 5 new parent folders** (slotted into 24-28 numbered positions):
- `24_Affordable_Implants`
- `25_Molar_Replacement`
- `26_Hate_Dentures`
- `27_Dental_Reconstruction`
- `28_Missing_Teeth`

30_NHS_Implants stays at position 30 (built).

## 10. Poor ad audit started — 13 of 32 done
Per Poor ad: 15 new headlines (≤30 char) + 4 new descriptions (75-87 char), distinct themes per ad, all kws covered as substring at ad-group level. NO em-dashes (regular hyphens only).

✅ **Done (13 of 32):**
1. [ex] Bone Graft - CORE (1 ad)
2. [ex] Bone Graft - COST (3 ads)
3. [ex] Fix My Teeth - COST (3 ads)
4. [ex] Implant Clinic - CORE (3 ads)
5. [ex] Implant Clinic - LOCATION (3 ads)

**Path tweak**: Bone Graft - COST Ad 2 path `bone-graft / from-400` → `bone-graft / cost` (price not confirmed).

⏳ **Remaining Poor ads (19) — for tomorrow:**
- [ex] Implant Replacement - CORE (3)
- [ex] NHS Implants - COST (3)
- [ex] New Teeth - CORE (3)
- [ex] New Teeth - LOCATION (3)
- [ex] New Teeth - NHS (3)
- [ex] Screwless - LOCATION (1)
- [ex] Tooth Replacement - CORE (3)

## Banked for tomorrow morning (after triage)

### Manual GAds UI tasks
1. **Delete `[ex] General Implants - NHS` ad group** (25 kws). Add 5 missing kws to new 30_NHS_Implants CSV before importing:
   - **CORE**: `implants teeth nhs`, `nhs dental implants near me`, `nhs dental implant eligibility`
   - **COST**: `nhs dental implants cost`, `teeth implants cost uk nhs`
2. **Import legacy keyword additions** to all the existing [ex] ad groups

### Email Giulio for sign-off on 4 pending brand parents
- 24 Nobel Biocare / 27 Implant Denture / 28 Zygomatic Pterygoid / 29 Straumann

### Em-dash retro-fix audit
- `—` → `-` across all `apps/web/src/pages/google/*.astro` LPs + all `Campaigns/*/_csv_*.csv` + all GAds ad audit headline/description files

### Continue Poor ad audit (19 remaining)
### Then Average + Good ads
### Then build 5 new parents (24-28) + 6 new sub-groups

## NEW ad groups to build (next session)

### NEW parent folders to populate (5)
- **24_Affordable_Implants** (~16 kws) — lowest UK private prices, NOT free/grants/charity
- **25_Molar_Replacement** (~16 kws) — back/molar/premolar/rear tooth, single-tooth focus
- **26_Hate_Dentures** (~17 kws) — implants vs dentures, denture-converter angle
- **27_Dental_Reconstruction** (~14 kws) — full mouth makeover/restoration angle
- **28_Missing_Teeth** (~8 kws) — solution-finder educational, funnels to Tooth/Teeth Replacement

### NEW sub-groups (add to existing parents, no new folders)
- 05 Tooth Replacement - LOCATION (~9 kws)
- 05 Tooth Replacement - COST (~13 kws)
- 06 Teeth Replacement - LOCATION (~3 kws)
- 14 Single Arch - COST (1 kw)
- 17 Upper Jaw - LOCATION (1 kw)
- 18 Lower Jaw - LOCATION (1 kw)

## Hours (full session, AM through past midnight)
~22h total
