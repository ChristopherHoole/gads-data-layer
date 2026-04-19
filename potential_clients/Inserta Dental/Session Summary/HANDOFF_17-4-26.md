# Dental by Design — Session Handoff
**Created:** 17 April 2026 (mid-session, context limit reached)
**Covering session:** Thursday 17 April AM (Day 4)
**Next session:** Thursday 17 April PM / Friday 18 April

---

## Where we are RIGHT NOW

**Mid-session** — we stopped at 93% context window. Morning session ran long due to negative keyword audit discovering major DBD-blocking errors across every list. Afternoon priorities confirmed but not yet started.

**Current account state: HEALTHY.** All 3 live campaigns running with proper bid strategies, geo targeting, ad schedules, and now a thoroughly cleaned negative keyword foundation.

---

## What was DELIVERED today (AM session)

### 1. 24hr performance check (Day 3 results)
- **Brand:** CPC £1.61, CPA £11.29, IS 92% (learning, trending well)
- **PMax:** CPA £25.18 (vs £67 baseline). Still flagged "asset groups limited by policy"
- **Dental Implants Intent:** £182 CPA day 1 (too early, expect improvement with new ads)

### 2. Website USP audit (dentalbydesign.co.uk + /services/)
Full service menu documented, pricing confirmed, 2 CRITICAL flags:
- "Free Consultation" in ads vs £95 on website (policy risk)
- "25+ Years" claim but clinic founded 2010

### 3. Client email sent
18 questions to Giulio + Tommaso. Priority: consultation pricing + experience claim. Awaiting response.

### 4. Dental Implants Intent rebuild plan approved
- Campaign architecture: 3 campaigns (Implants, Cosmetic, General), 36+ ad groups, ~700 keywords
- 20 of 25 implant ad groups built yesterday (AG1-20)
- **5 remaining: AG21-25** (Missing Teeth, Replace All, Reconstruction, vs Dentures, vs Bridges)

### 5. Daily search terms audit (Apr 15-16)
- 1,786 unique search terms analysed
- **934 blocks added** (v1 classifier had bug blocking "dental" — fixed)
- **93 additional blocks** from v2 tighter classifier
- **84 final confirmed** (after filtering DBD services)

### 6. Phrase-match extraction from exact lists
Converted specific exact negatives into broader phrase negatives:
- 5+ word list → extractions added
- 4 word list → extractions added
- 3 word list → extractions added
- 2 word list → extractions added

### 7. 🚨 MAJOR DISCOVERY: Negative keyword audit — DBD was blocking itself
User spotted `zirconia` blocked which blocks DBD's premium £9,990-£15,990 Vivo Bridge. Triggered full audit of EVERY list.

**Critical DBD-blocking terms found and REMOVED:**

| List | Terms removed |
|---|---|
| 1 WORD "phrase" | 18 (bonding, composite, crown, makeover, whitening, etc.) |
| Location 1 WORD "phrase" | 2 (northwood, gloucester) |
| 2 WORDS "phrase" | 24 |
| 2 WORDS [exact] | 33 |
| 3 WORDS "phrase" | 26 (incl. "same day teeth" — DBD's core USP) |
| 3 WORDS [exact] | 18 |
| Competitors "phrase" | 10 |
| Competitors [exact] | 2 (incl. `[allon4]` — DBD's service) |
| 4 WORDS [exact] | 11 |
| 5+ WORDS [exact] | 29 |
| **TOTAL** | **173** |

Plus 20 zirconia-related errors unblocked earlier in session.

### 8. Legacy lists detached
- `DBD Negs` — detached from all campaigns (not deleted)
- `KMG | Invisalign` — detached (Invisalign deprioritised)

---

## What's OUTSTANDING for today's afternoon session

| # | Task | Est time | Why priority |
|---|---|---|---|
| 1 | **Build AG21-25** (last 5 DII ad groups) | 2 hrs | Completes the DII campaign rebuild |
| 2 | **PMax asset audit + rebuild** | 2 hrs | "Asset groups limited by policy" flag for days — active revenue issue |
| 3 | **Ad extensions** (sitelinks, callouts, snippets) across all campaigns | 1 hr | Applies across all 3 campaigns |
| 4 | **Friday end-of-week report** for Giulio + Tommaso | 1 hr | Friday = tomorrow, client expects it |
| 5 | Session summary | 15 min | Standard wrap |

**User was leaning Option A: Build AG21-25 today + start PMax, Friday report tomorrow morning.**

---

## KEY CONTEXT for continuity

### Client: Dental by Design (DBD)
- **Location:** 45 Beadon Road, Hammersmith, London W6 0BT
- **Contacts:** Giulio + Tommaso (awaiting email response to 18 questions)
- **Founded:** 2010 (16 years, NOT 25+ as current ads claim)

### DBD services (CORE — never block)
```
Vivo Crown® Single Tooth Implant  — from £1,695
Vivo Bridge® Single Arch (Nano)    — from £6,995
Vivo Bridge® Single Arch (Zirconia) — from £9,990
Vivo Bridge® Full Mouth (Nano)     — from £10,995
Vivo Bridge® Full Mouth (Zirconia) — from £15,990
Porcelain Veneers                  — from £950
Composite Bonding                  — from £250
Teeth Whitening                    — from £395
Smile Makeover                     — from £2,400
Laser Gum Contouring               — from £250
Invisalign® (deprioritised by user — low margin)
Crowns & Bridges                   — from £900
```

### DBD USPs (never block)
- Same day / 48 hour permanent teeth
- Vivo Bridge® / Vivo Crown® / Vivo Guided Technology™
- Lifetime warranty on zirconia arches
- 0% finance, £28/month single implant, £95/month full arch
- Free consultation (PENDING GIULIO'S CONFIRMATION — website says £95!)
- In-house dental laboratory
- 4.8/5 Google rating (401+ reviews)
- Best Implant Clinic UK 2024 (Association of Dental Implantology) — PENDING VERIFICATION
- 99.12% success rate — PENDING VERIFICATION

### Current campaign state
- **Brand** — tIS 95% / max CPC £1.50 / 266 postcodes / 42-cell schedule / 3 RSAs
- **PMax** — tCPA £60 / 270 postcodes / 42-cell schedule / POLICY ISSUES flagged
- **Dental Implants Intent** — tCPA £75 / 270 postcodes / 42-cell schedule
  - 20 new ad groups built (AG1-20), 60 RSAs, 537 keywords
  - 4 legacy ad groups paused
  - 60 low-volume keywords paused
  - **AG21-25 still needed**
- **Demand Gen** — paused permanently

### AG21-25 details (ready to build)
Keywords and RSA templates already drafted in `CAMPAIGN_REBUILD_PLAN.md`:
- AG21: Missing Teeth Solutions
- AG22: Replace All Teeth
- AG23: Teeth Reconstruction
- AG24: Implants vs Dentures
- AG25: Implants vs Bridges

### Negative keyword lists — POST AUDIT
Clean across all 11 lists. Structure:
```
1 WORD "phrase" + Location 1 WORD "phrase"
1 WORD [exact]
2 WORDS "phrase" + 2 WORDS [exact]
3 WORDS "phrase" + 3 WORDS [exact]
4 WORDS [exact]
5+ WORDS [exact]
Competitors & Brands "phrase" + [exact]
(DBD Negs + KMG | Invisalign — detached)
```

---

## CRITICAL LESSONS from this session (carry forward)

### Negative keyword rules
1. **Never block DBD service words** — bonding, composite, crown, makeover, whitening, gum, hygienist, warranty
2. **Never block brand review patterns** — review, reviews, trustpilot
3. **Never block DBD USP words** — zirconia, zirconium, titanium, straumann, nobel biocare, 48 hour, same day
4. **Never block brand-adjacent words** — design (DBD IS "Dental by Design")
5. **Never block "local" / "near me"** in 1-word form — blocks buying intent
6. **Never block DBD catchment areas** — hammersmith, chiswick, fulham, ravenscourt, w6 etc.
7. **Test phrase match:** "Could this phrase appear in a DBD buying-intent search?" If yes, skip.

### RSA ad strength rules (learned yesterday)
1. Headlines 1-10 = LITERAL keyword phrases from ad group
2. Max 4-5 headlines starting with same words (uniqueness check)
3. Include 2-3 broader popular keywords (dental implants, teeth implants)
4. Each description starts with different keyword phrase
5. Descriptions 75-86 chars (tight zone for good score)
6. Headlines strict ≤30 chars
7. Pin Headline 1 only (position 1), leave rest unpinned

---

## KEY FILES

### Session docs
- `Session Summary/SESSION_SUMMARY_14-4-26.md` — Day 1 negative keyword overhaul
- `Session Summary/SESSION_SUMMARY_15-4-26_AM.md` — Day 2 AM Brand rebuild
- `Session Summary/SESSION_SUMMARY_15-4-26_PM.md` — Day 2 PM account-wide
- `Session Summary/SESSION_SUMMARY_16-4-26.md` — Day 3 DII rebuild (20/25 ad groups)
- `Session Summary/HANDOFF_17-4-26.md` — THIS FILE

### Reference docs
- `CAMPAIGN_REBUILD_PLAN.md` — full plan with AG21-25 keywords ready
- `DENTAL_IMPLANTS_KEYWORDS.md` — complete keyword lists for all 25 ad groups
- `QUESTIONS_FOR_GIULIO_16-4-26.md` — questions sent to client
- `EMAIL_GIULIO_TOMMASO_16-4-26.md` — email sent

### Data folders
- `data/Search terms/` — historical + daily search term exports
- `data/Dental Implants Intent/` — ad group performance reports
- `data/Negative list/` — exported negative keyword lists for audits
- `data/All Campaigns/` — account-wide performance reports
- `data/Brand Campaign/` — Brand-specific reports
- `data/PMAX Campaign/` — PMax data (yet to be audited)

### Python analysis scripts (for reference — reusable)
- `_apr13_v3.py` — negative keyword classifier (v3, latest)
- `_apr14_v3.py` / `_apr14_2nd.py` / `_apr15_16_classify.py` — daily audit scripts
- `_batch5_v2.py` — bulk search term classification

---

## PENDING CLIENT ANSWERS (block some ad revisions)

Awaiting reply from Giulio/Tommaso on 18 questions. Priority:
- **Q1: Free consultation vs £95?** — Affects every ad currently running
- **Q2: 25+ years vs 16 years (founded 2010)?** — Affects every ad
- Q3-7: Claims verification (Best Implant Clinic UK 2024, 99.12% success, etc.)
- Q8-14: Business data (lead-to-patient %, top services, patient journey)

---

## NEXT SESSION: Recommended start

1. **Read this handoff file**
2. **Check email** — has Giulio responded? If yes, update ads accordingly (critical fixes first)
3. **Confirm user's preference:**
   - Build AG21-25 first (completes DII rebuild)?
   - Or tackle PMax (revenue-limiting policy issue)?
   - Or write Friday report (client deliverable due tomorrow)?
4. **Run 24hr performance check** on all 3 campaigns to see if today's negative cleanup improved metrics

### If user says "finish what we started": AG21-25 build
Keywords ready in `CAMPAIGN_REBUILD_PLAN.md`. Use same format as AG1-20:
- Phrase + exact keywords per ad group
- 3 RSAs per ad group (15 headlines + 4 descriptions each)
- Landing page mapped to existing URLs (dedicated pages build next week)
- Character limits: headlines ≤30, descriptions 75-86 chars
- Remember the ad strength rules

### If user says "PMax is bleeding": Asset audit
- Data in `data/PMAX Campaign/` (user uploaded Tuesday)
- Expected issues: policy-flagged assets (headlines/descriptions with unverified claims, borderline images)
- Strip: "99.12% Success Rate", "Voted #1 UK Implant Centre", "Save 60%" from all assets
- Rewrite with user-preferred premium angle

### If user says "Friday report first": Client report
- Running totals of work delivered
- Early results (Brand CPC -50%, PMax CPA -62%, DII pending)
- Next week's plan (AG21-25 if not built today, Cosmetic campaign, landing pages, conversion tracking)
- Keep concise — user explicitly said they want to manage expectations

---

## USER PREFERENCES (observed patterns)

- Always "I" never "we" in client comms
- One keyword per line in negative lists, no commas or brackets
- Descriptions 75-86 chars (strict)
- Headlines strict ≤30 chars
- Prefers building NEW ads over editing existing (preserves performance history)
- Questions decisions and tests logic — don't be sloppy, show reasoning
- Doesn't want emojis in files unless explicitly asked
- Session summaries go in `Session Summary/` folder
- Exports done files as CSV in `data/Negative list/` for audits

---

## CONTEXT FOR THE NEW SESSION

This has been a highly productive week (4 days of 4-8hr sessions). The account has been transformed from chaotic pre-Chris state into a tightly-controlled premium implant clinic campaign. Christopher Hoole is the solo manager, working on this as his first paying client after signing DBD (Dental by Design / Prodent Group) on 14 April 2026.

The big strategic focus is getting DBD profitable on paid search to prove ACT's methodology, which is the core product Chris is building (ACT = Ad Control Tower).
