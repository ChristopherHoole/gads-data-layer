# Dental by Design — Negative Keyword Deep Audit (Day 4 AM)
**Session date:** 17 April 2026 (morning, ~3 hours)
**Scope:** Daily search terms, phrase-match extractions, and deep negative keyword audit across all 11 lists

---

## Headline
Discovered and removed 173 critical DBD-blocking negative keywords across all 11 negative lists, triggered by spotting that "zirconia" was blocking DBD's premium £9,990-£15,990 Vivo Bridge® service. The audit revealed that the account had been unknowingly blocking its own services, USPs, brand review searches, and catchment areas — most built up incrementally over prior days as part of aggressive negative keyword work. Account is now on a clean, properly-tested negative foundation.

---

## The catalyst

While scanning for new additions, Chris spotted this in the negative lists:

```
"zirconia" in 1 WORD "phrase"
[zirconia implants]
[zirconia crown]
[zirconia bridge]
+ 17 other zirconia/zirconium variants
```

Problem: **Zirconia is DBD's premium implant material** — their highest-ticket service:
- Vivo Bridge® Single Arch (Zirconia): £9,990
- Vivo Bridge® Full Mouth (Zirconia): £15,990

Blocking "zirconia" phrase meant blocking every premium buyer search. This prompted Chris to ask: "I think we need to check every negative keyword list for potential client blocking terms right?"

The audit that followed was the most important piece of work this week.

---

## Work delivered (in order)

### 1. 24-hour performance check (Day 3 results)
First full day after Wednesday's 20 new ad groups went live:

| Campaign | CPC | CPA | IS | Status |
|---|---|---|---|---|
| Brand | £1.61 | £11.29 | 92% | Learning — trending well |
| PMax | £2.30 | £25.18 | 11.58% | Excellent CPA, but "asset groups limited by policy" |
| Dental Implants Intent | £6.77 | £182.70 (2 conv) | 62.86% | Too early, 1-day noise |

**PMax policy flag** queued for next session — actively limiting reach.

### 2. Website USP audit (dentalbydesign.co.uk + /services/)
Full services page walked. Documented:
- 3 implant services (Vivo Crown, Vivo Bridge Single Arch, Vivo Bridge Full Mouth)
- 6 cosmetic services (veneers, Invisalign, whitening, bonding, smile makeover, gum contouring)
- 9 general dentistry services (hygiene, fillings, crowns, root canal, extractions, etc.)

**Two critical flags to client:**
- "Free Consultation" on every ad vs £95 consultation on website → potential Google Ads misleading pricing violation
- "25+ Years of Expertise" on ads vs clinic founded 2010 (16 years) → inaccurate

### 3. Client questions email (sent to Giulio + Tommaso)
18 questions grouped by urgency. Two urgent (consultation pricing + experience claim), plus claims verification and business data requests. Friday end-of-week report expectation set. Awaiting reply.

### 4. Daily search terms audit (April 15-16)
1,786 unique search terms analysed.

**Two passes:**
- **First pass:** 934 blocks across 5 exact-match lists (1/2/3/4/5+ word)
- **Second pass:** Caught 84 additional blocks after Chris spotted obvious misses. v1 classifier had a catastrophic bug — accidentally put "dental" in the FOREIGN_WORDS set, which was filtering every dental search out before it could be classified. Bug fixed in v2.

Total: **1,018 new negatives** added from two daily reports.

### 5. Phrase-match extraction from exact lists
Systematic extraction of shorter phrase-match negatives from existing exact lists. Each phrase-match entry catches wider patterns than the specific exact term it came from.

| Source list | Extractions proposed |
|---|---|
| 5+ WORDS [exact] | 110 candidates (62 one-word + 48 two-word) |
| 4 WORDS [exact] | 106 candidates (34 one-word + 72 two-word) |
| 3 WORDS [exact] | 87 candidates (51 one-word + 36 two-word) |
| 2 WORDS [exact] | 57 candidates (51 one-word + 6 two-word) |

**Key lesson:** The first pass on the 4-word list had dangerous suggestions ("dental practice", "dental clinic", "dental surgery", "implant centre", "implant clinic", "implant specialist", "dental design") — all of which would block DBD-describing terms. Chris caught them. Methodology tightened: every phrase must pass the test "Could this phrase appear in a DBD buying-intent search?" If yes, skip.

### 6. 🚨 THE BIG ONE: Full negative keyword audit

Every one of the 11 live negative lists audited against DBD's services, USPs, brand, and catchment.

**Critical DBD-blocking terms removed:**

| List | Terms | Key examples |
|---|---|---|
| 1 WORD "phrase" | 18 | `bonding`, `composite`, `crown`, `crowns`, `makeover`, `gum`, `hygienist`, `jaw`, `whitening`, `fixed`, `warranty`, `review`, `reviews`, `trustpilot`, `dalston`, `local`, `dental`*, (*was causing classifier bug, not in list) |
| Location 1 WORD "phrase" | 2 | `northwood` (Greater London), `gloucester` (ambiguous with Gloucester Road) |
| 2 WORDS "phrase" | 24 | `dental hammersmith`, `hammersmith reviews`, `emergency dental`, `gum treatment`, `dental hygienist`, `chipped tooth`, `tooth repair`, `check up`, `tooth replacement`, `broken tooth`, `loose tooth`, `tooth loss`, `front teeth`, `my teeth`, `need dental`, `fix my`, `one day`, `top rated`, `titanium vs`, `straumann implant`, `refer a`, `dental care`, `dental centre`, `dental office` |
| 2 WORDS [exact] | 33 | Including `dental hammersmith`, `hammersmith dental`, `dentist hammersmith`, `dental bridge`, `dental crown`, `dental veneers`, `dental hygiene`, `smile makeover`, `porcelain veneers`, `straumann implants`, `nobel biocare`, `titanium implants`, etc. |
| 3 WORDS "phrase" | 26 | Including `same day teeth` (DBD's core USP!), `in one day`, `on 4 teeth`, `4 teeth implants`, `in 4 dental`, `dental implants reviews`, brand review searches, cost/price buying intent, positioning phrases |
| 3 WORDS [exact] | 18 | DBD area, premium brand research, free consultation USP, missing teeth buying intent |
| Competitors "phrase" | 10 | `hammersmith dental care`, `chiswick dental`, `fulham dental`, `ravenscourt dental`, `my dentist`, plus 5 overly-broad phrases |
| Competitors [exact] | 2 | `[allon4]` (!!), `[dentalondon]` |
| 4 WORDS [exact] | 11 | Premium research, DBD USPs, buying intent actions |
| 5+ WORDS [exact] | 29 | Problem-state DBD prospects ("my tooth is falling out", "all my teeth are rotten what can i do"), All-on-X buying, finance/free consult USPs |
| **TOTAL** | **173** | |

**Plus:** 20 zirconia/zirconium/premium material terms unblocked earlier in the session (the catalyst).

### 7. Legacy lists detached
Two legacy broad-match negative lists still attached to campaigns:
- **DBD Negs** — Chris's pre-takeover list
- **KMG | Invisalign** — previous agency's Invisalign-focused list

Both **detached from all campaigns** (not deleted — kept for history). Reasoning:
- Broad match is the most dangerous type — could be silently wrecking the account
- We now have 11 properly-structured phrase + exact lists with ~5,000+ negatives
- Chris has deprioritised Invisalign (low margin, high competition)
- Legacy lists had no documented audit trail

### 8. Handoff document created
Full handoff saved to `Session Summary/HANDOFF_17-4-26.md` with:
- Current account state
- All work delivered across the week
- Outstanding priorities for next session
- Critical lessons learned (negative keyword rules, RSA ad strength rules)
- DBD services list (never block these)
- File locations
- User preferences
- Pending client answers

---

## Cumulative account progress (Days 1-4)

| Day | Session | Key deliverables |
|---|---|---|
| Day 1 (Mon) | 4hrs | Negative keyword overhaul: ~4,700 structured negatives across 11 shared lists |
| Day 2 (Tue AM) | 4hrs | Brand campaign rebuilt: bid strategy, geo, schedule, 2 RSAs, 9 brand keywords |
| Day 2 (Tue PM) | 4hrs | Account-wide: auto-apply off, PMax tCPA £60, DII tCPA £75, 356 negatives, 8 RSAs, geo + schedules copied |
| Day 3 (Wed) | 8hrs | DII campaign rebuilt: 20 ad groups, 537 keywords, 60 RSAs, legacy paused |
| Day 4 AM (Thu) | 3hrs | **Daily audit + 173 DBD-blocking negatives removed + legacy lists detached** |

**Running totals:**
- Total new keywords live: 546 positive + ~5,000 negative
- Total new RSAs: 70
- Total headlines written: 1,050
- Total descriptions written: 280
- Total geo targets: 810 (270 × 3 campaigns)
- **Critical DBD-blocking terms caught and removed this session: 173**
- **Plus zirconia/premium unblocked: 20 terms**
- **Legacy lists detached: 2**

---

## Key lessons (for ACT build)

### Negative keyword rules — added this session

1. **Phrase-match negatives block the phrase wherever it appears in a search term.** Every phrase candidate must be tested against: "Could this phrase appear in a DBD buying-intent search?" If yes, skip.

2. **Never block DBD service words** — even as part of broader cleanup:
   - Services: bonding, composite, crown, crowns, veneer, veneers, makeover, gum (contouring), hygienist, whitening, bridge, bridges
   - Materials: zirconia, zirconium, titanium (DBD uses these in Vivo Bridge), nanohybrid, ceramic
   - Premium brand research: straumann, nobel biocare, osstem (DBD's implant brands)

3. **Never block brand review patterns** — `review`, `reviews`, `trustpilot` block brand-specific review searches ("Dental By Design reviews", "DBD trustpilot").

4. **Never block brand-adjacent words** — `design` would block DBD's own brand "Dental by Design".

5. **Never block generic buying qualifiers** — `local`, `near me` (in 1-word form), `top rated`, `best dentist`. These are exactly how buyers search.

6. **Never block catchment-area words** — hammersmith, chiswick, fulham, ravenscourt, w6, dalston, forest hill, golders green, muswell hill, etc.

7. **Never block USP words** — warranty (lifetime warranty), same day, 48 hour, permanent teeth.

8. **Never block problem-state words** — "my tooth is falling out", "all my teeth are rotten", "my teeth are a mess" ARE buying-intent searches for DBD (they describe the customer's need for implants).

### Classifier bugs found and fixed

1. **FOREIGN_WORDS set accidentally contained "dental"** → blocked every dental search. Caught when user flagged obvious misses in output.
2. **1-word phrase "design"** in lists → would block DBD brand searches. Caught in audit.
3. **1-word phrase "specialist"** suggested by Claude → would block DBD's own specialist ad group. Caught by user challenge.

### Methodology lesson

When Claude suggests phrase-match negatives, Claude must apply this strict filter before presenting:
- Could this phrase appear in a DBD buying-intent search? → Skip
- Does this phrase describe DBD itself (clinic, practice, specialist, etc.)? → Skip
- Is this a specific competitor brand name or clear wrong-intent phrase? → Safe

Broad suggestions like "dental practice" / "dental clinic" / "dental surgery" felt like competitor-brand catches but actually block DBD-descriptive language. Claude was too cavalier. User rightly pushed back.

---

## Critical items pending

1. **Awaiting client reply** — Giulio + Tommaso still have 18 questions. Urgent: consultation pricing conflict (free in ads vs £95 on website), and "25+ years" claim accuracy.

2. **AG21-25 not built** — Last 5 ad groups of DII rebuild. Keywords drafted in `CAMPAIGN_REBUILD_PLAN.md`. 2-hour job.

3. **PMax policy issue** — "Asset groups limited by policy" flagged for days. Needs rebuild with premium-positioned assets (no "99.12% success", no "Save 60%", no "Voted #1 UK"). Data uploaded by user Tuesday.

4. **Ad extensions** — Not yet built across campaigns. Sitelinks, callouts, structured snippets.

5. **Friday end-of-week client report** — Due tomorrow (18 April). Should summarise week's work and early results.

---

## Next session priorities

Context window hit 93% mid-session. Handoff document created. Recommended start:

1. Read `HANDOFF_17-4-26.md` first
2. Read all 4 prior session summaries to understand full trajectory
3. Check for Giulio/Tommaso email reply
4. Run 24hr performance check (was today's negative cleanup effective?)
5. User's lean was **Option A: Build AG21-25 + start PMax today + Friday report tomorrow**

---

## Honest assessment

This was quiet, unglamorous work but arguably the most important 3 hours of the week. The account was silently blocking its own premium buyers — zirconia research, same-day teeth searches, "fix my teeth" prospects, missing teeth replacement, All-on-X buyers. Every one of those blocks was costing real revenue daily.

The zirconia discovery was the canary — Chris spotting ONE blocked word triggered an audit that caught 172 more. Without this audit, those errors would have persisted indefinitely, with the account slowly bleeding high-value search traffic that got progressively worse as more negative keywords were added in future sessions.

Methodology updated. Won't happen again.
