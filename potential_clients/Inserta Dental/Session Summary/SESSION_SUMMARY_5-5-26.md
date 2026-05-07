# DBD Session Summary — Tue 5 May 2026

## Headline
Massive DBD day. PMax→DII redirect went live. Ad scheduling tightened to working hours. 4 new parent ad-group builds shipped (10 LPs). Ad audit started — 11 of 28 ad groups done with new keyword-saturation rule locked.

## Email to Giulio
Sent rebuild plan email — 27 parent themes split by intent (CORE/COST/LOCATION/FINANCE/INFO/NHS), 5 done so far, building 4-7 per day, pending his sign-off on Implant Dentures, Zygomatic, Straumann, NHS Implants.

## PMax → DII redirect program — LIVE
- Created `potential_clients/Inserta Dental/DAILY_MORNING_ROUTINE.md` documenting the full daily cadence (Steps 1-7) including new **Step 5: PMax → DII redirect**
- Created folder `potential_clients/Inserta Dental/PMax_Redirect_CSVs/` for daily search-term CSV drops
- 25 PMax search terms added to new PMax-only **exact-match** neg list — these are terms now covered by live `[ex]` ad groups in DII
- PMax daily budget cut £950 → ~£550-600/day to match negged volume
- DII budget held at £400/day (will scale up); DII tCPA raised £65 → £70
- Verified all 25 negs are live + Enabled exact-match keywords in `[ex]` ad groups before pushing

## Ad scheduling shift — LIVE on both PMax + DII
- **PMax + DII** now run Mon-Fri 08-18, Saturday 08-14, Sunday OFF
- Implements Phase 1 of "Maximising Bookings on Current Spend" deck (Sat 2 May)
- Eliminates ~57% of spend that was buying leads in dead zones (eve, night, weekend)

## Weekly report data prep
- Pulled GAds rolling 8-week comparison from Campaign report (9).csv
- Ran Dengro Paid Search-only weekly breakdown for last 8 weeks using same column format as Maximising Bookings deck slide 5
- **Headline finding**: last week (27/04 - 03/05) had **18 never-contacted Paid Search leads, ALL from Sun 3/5 (~£790 wasted)** — 3.5% book rate (worst in 8 weeks)
- Schedule shift addresses root cause
- Tommaso/Giulio not contacted re: weekly catchup yet — likely skip this week, will report next week with hopefully better numbers post-shift

## Daily search-term triage
- Snapshot 04/05 (analysis 05/05) — 263 negs pushed total
  - Pass 1/2: 229 negs
  - Pass 3 AI: 34 negs (out of 40 fragments shown — 6 held back for being too risky)

## GAds rebuild Day 2 — 4 new parents shipped
- **06_Vivo_Bridge: SKIPPED** — zero volume in audit DB (only 119 impr, £33 spend, 0 bookings) per Giulio's call
- **07_Permanent_Teeth — 1 ad group, 5 keywords, 3 RSAs, 1 LP** at /google/permanent-teeth (renamed from Permanent Teeth 48h since "48h" had no volume)
- **08_Same_Day_Teeth — 3 ad groups (CORE/COST/LOCATION), 24 keywords, 9 RSAs, 3 LPs**
- **09_Smile — 3 ad groups (broadened from Smile in a Day), 16 keywords, 9 RSAs, 3 LPs** at /google/smile-makeover
- **10_Fix_My_Teeth (NEW PARENT slotted in) — 3 ad groups, 15 keywords, 9 RSAs, 3 LPs** at /google/fix-my-teeth — built because `i want to fix my teeth` cluster was the biggest unhandled PMax search term (£2,095 over audit period)

Cumulative across both days: **34 LPs / 31 ad groups**.

## CRITICAL RULE LOCKED for ad audit
**Every keyword in ad group must appear (as exact substring) in headlines for Quality Score / Ad Strength to flip Excellent.**

- Substring overlap allowed: "Single Tooth Implant" headline covers both `tooth implant` AND `single tooth implant` keywords
- Keywords too long for headlines (>30 chars) must appear in descriptions instead (90 char limit)
- Validate every ad: if any keyword is missing from headlines+descriptions across the ad group, ad strength caps at "Average" or "Poor"

## Ad audit progress (11 of 28 ad groups done today)
For each Poor ad: write 15 new headlines + 4 new descriptions, Chris swaps in via GAds UI one-by-one until ad strength flips Excellent.

✅ Done:
1. All on 6 - CORE (3 ads, 5 keywords)
2. All on 6 - COST (3 ads, 2 keywords)
3. General Implants - CORE (3 ads, 16 keywords)
4. Same Day Teeth - CORE (3 ads, 11 keywords)
5. Same Day Teeth - COST (3 ads, 2 keywords)
6. Same Day Teeth - LOCATION (3 ads, 11 keywords)
7. Smile - CORE (3 ads, 9 keywords)
8. Smile - COST (3 ads, 2 keywords)
9. Permanent Teeth - CORE (3 ads, 5 keywords)
10. Fix My Teeth - CORE (3 ads, 8 keywords)
11. Fix My Teeth - COST (3 ads, 3 keywords)

⏳ Remaining (tomorrow):
- Fix My Teeth - LOCATION (3 Poor)
- General Implants - COST (3 Poor)
- General Implants - FINANCE (3 Poor)
- All on 4 - INFO (mixed)
- Full Mouth - LOCATION (Good x2)
- Smile - LOCATION (Average x3)
- General Implants - INFO (Average/Good)
- General Implants - LOCATION (Good/Average)
- General Implants - NHS (Good x1)
- New Teeth - COST (Average x2) — SKIP (will be redone after split)
- Screwless - CORE/COST/INFO/LOCATION (mixed)
- Plus the 4 new ad groups built tomorrow (CORE for Tooth Replacement + Teeth Replacement, plus reaudit New Teeth - CORE)

## NEW PARENTS to build FIRST THING TOMORROW
Discovered while auditing New Teeth - CORE that 28 keywords across 3 distinct intents was too broad — Quality Score capped at Poor. Split decided:

**Tomorrow's #1 task:**
1. Insert 2 new parents into Campaigns sequence (everything 05+ shifts by 2):
   - **Tooth Replacement** (10 keywords — single-tooth replacement intent)
     - Build LP at https://dentalbydesign.co.uk/google/tooth-replacement
   - **Teeth Replacement** (10 keywords — multiple/full arch replacement intent)
     - Build LP at https://dentalbydesign.co.uk/google/teeth-replacement
2. In GAds UI: move the 20 keywords out of `[ex] New Teeth - CORE` into the 2 new ad groups
3. New Teeth - CORE drops to 8 keywords (much easier to score Excellent)
4. Resume ad audit

## Files updated
- `potential_clients/Inserta Dental/DAILY_MORNING_ROUTINE.md` (NEW)
- `potential_clients/Inserta Dental/PMax_Redirect_CSVs/` (NEW folder)
- `potential_clients/Inserta Dental/Campaigns/07_Permanent_Teeth/` (NEW — renamed from 07_Permanent_Teeth_48h)
- `potential_clients/Inserta Dental/Campaigns/08_Same_Day_Teeth/` (NEW)
- `potential_clients/Inserta Dental/Campaigns/09_Smile/` (renamed from 09_Smile_in_a_Day)
- `potential_clients/Inserta Dental/Campaigns/10_Fix_My_Teeth/` (NEW — slotted in, 11+ shifted)
- 4 new generator scripts in `data/search_terms_audit_2026/`

## Hours
~12h
