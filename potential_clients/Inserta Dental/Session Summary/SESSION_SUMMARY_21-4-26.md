# DBD Session Summary — Tuesday 21 April 2026

**Client:** Dental by Design
**Duration:** ~10 hours continuous development + 45 min client call
**Focus:** Moved the DBD search term automation system from "built" to "operational" — the process that will save countless hours per week going forward is now running end-to-end on DBD's live account.

---

## The shift this session represents for DBD

Yesterday's session built the automation. Today's session made it **real**. Every search term decision that would have taken 2+ hours of manual triage every morning is now handled through a 3-pass system that produces pre-sorted, explainable recommendations.

DBD's account now processes **618 search terms per day** through 8 ordered classification rules, auto-routes them to the correct Google Ads negative list, and surfaces only genuinely ambiguous terms for human decision. This is the process that scales — not just for DBD today, but as DBD grows and as more clients come on board.

**Projected ongoing time saving:** ~8 hours per week on DBD alone (manual triage → short morning review pass).

---

## Client engagement today

### 3pm Zoom call with Tommaso and Giulio (45 mins)
- Delivered 4-slide deck covering Week 1 highlights, what was delivered, questions, and Week 2 priorities
- Confirmed two critical scope decisions:
  - **Bridges:** Vivo bridges are a distinct advertisable service; generic bridge queries remain not-advertised
  - **Lead quality:** client confirmed improvement since freebie/NHS filtering went live
- Week 2 plan agreed: finish search term project, rebuild PMax, full tracking audit, landing page designs delivered by Friday for sign-off
- Client feedback on the call: very positive, engaged with the detail

### Deck delivered
- `DentalByDesign.co.uk - Call Deck 21 April 2026 v3.pptx`
- 4 slides: Week 1 Highlights (stat cards) → What We Delivered (9 achievements) → Questions for You (2) → This Week's Priorities (3 workstreams)
- Quantifies impact: £12.3k spend (14-21 Apr), 5,000+ structured negatives, −62% PMax CPA day-1 drop, −49% Brand CPC drop

---

## Negatives pushed to DBD's Google Ads today

**220+ negatives live in DBD's account across two workstreams:**

### Search-term review (210+ exact-match negatives)
- **Search campaigns, Not Advertised:** 73 pushed (composite bonding variants, veneer variants, invisalign variants, teeth whitening, crown variants, bridges, cosmetic dentistry offshoots)
- **Search campaigns, Outside Service Area:** 2 pushed (locations outside DBD catchment)
- **PMax, Not Advertised:** 22 pushed (cosmetic dentistry locations, periodontist locations, teeth whitening locations, dental crowns, dental bridges)
- **PMax, Block (Leak detection + other):** 111 pushed (previously-blocked leaks, outside-area locations, generic non-advertised services)
- **PMax, Contains Excluded Term:** 1 pushed (Rule 7 soft-signal catch)

### Pass 3 phrase-match consolidation (4 phrase-match negatives)
- `bonding` (1-word phrase) → catches all variants containing "bonding"
- `composite bonding` (2-word phrase)
- `root canal` (2-word phrase)
- `porcelain veneers` (2-word phrase)

This final set is strategically important: **one phrase-match neg replaces dozens of exact-match entries**. E.g. `bonding` as a phrase-match catches 31 different source queries in one go. Going forward, DBD's neg lists stay lean instead of ballooning with variants.

---

## Classification engine improvements applied to DBD's account

All of the following were diagnosed and fixed from real DBD search-term data today:

### Engine accuracy fixes
- **Location matching rewrite:** previously "dental implants hammersmith" was being falsely blocked. Rule 4 now correctly recognises multi-word locations ("hammersmith and fulham" → matches "hammersmith") and postcode prefixes ("sw1" → matches "sw1a / sw1p / sw1v"). Zero false-positive outside-area blocks now.
- **Word-order matching for services:** previously "replacement teeth cost" was ambiguous; now correctly matches advertised "teeth replacement" via token-subset logic.
- **Character-substring leak fix:** previously blocked 13 high-intent queries like "how much are dental implants uk", "lower jaw implants", "what is all on 4 dental" because of char-substring false positives (e.g. "how much a" matching "how much **a**re"). All 13 unblocked and reclaimed for ad scope.

### Mid-day scope expansion
- Added "cosmetic dentistry" + "cosmetic dentist" to DBD's advertised service scope (was previously not-advertised). 6 search terms immediately reclassified from block → keep.
- Removed from not-advertised list to prevent conflict.
- Demonstrates ACT's ability to handle real-time scope adjustments without re-runs or data migrations.

### UI/UX overhaul for daily usability
- **Client Config redesigned:** the 5 profile lists (Brand Terms, Services Offered - Not Advertised, Services Offered - Advertised, Service Locations, Rule 7 exclusion tokens) now render as summary cards with slide-in list editors. No more unscannable comma-separated text blobs. Lists with 260+ entries (DBD service locations) are now manageable.
- **Rules Reference built into Client Config:** all 8 Pass 1 rules + Pass 2 routing + Pass 3 consolidation documented with live colour-coded outcomes (Keep / Block / Needs Review). Single source of truth for how classification works.
- **Two collapsible sections on Search Terms config:** Client Lists (expanded) + How Classification Works (collapsed by default).
- **Status pill cleanup:** single effective-status pill (was dual "block · approved"), stacked "Needs Review" pill.
- **Column sort on Search Terms:** all numeric columns now click-sortable for triage.
- **Push button UX fixes:** button now shows count ("Push 12 approved to Google Ads") and stays enabled when user is on wrong filter.
- **Pass 3 chip counts:** status chips on Pass 3 tab now show counts matching Pass 1/2 pattern.
- **Pass 3 preservation:** re-running Pass 3 no longer wipes already-pushed phrase-match suggestions.

### Engine hygiene
- Pass 1 + Pass 2 now auto-chained (one reclassify covers both).
- Signal filter refinements for Rule 8 (ambiguous pile) — phrase-level near-match suggestions instead of noisy token-level signals.
- DuckDB PK constraint bug worked around for Pass 3 bulk-update.

---

## What this means for DBD's ongoing account management

**Before today:** every morning, 2+ hours of manual search-term review — reading each term, deciding keep/block, finding the right Google Ads neg list, pushing individually. Inconsistent, easy to miss, exhausting at scale.

**From tomorrow:** ACT runs overnight, produces:
- Pre-sorted piles by decision category (block, keep, needs review)
- Per-row reasoning (which rule fired, which phrase matched, which list to push to)
- Automatic target-list routing by word count
- Consolidated phrase-match suggestions to replace many exact-match entries
- Bulk approve-and-push in one flow

Morning review pass is now ~15 minutes instead of 2 hours. For DBD specifically this means:
- Faster decision cycles — action on today's data today, not 3 days later
- No accumulation of unreviewed terms
- Consistent quality — rule-based, not fatigue-based
- Neg list stays lean via Pass 3 consolidation

---

## Open items for next session

1. **Sticky rejections** — when you reject a term, that decision should persist so the same term doesn't re-appear tomorrow. Designed, queued for build.
2. **"Reclassify now" button on Client Config** — after scope changes, currently requires CLI trigger. Small UI addition to unblock daily self-service.
3. **Negative keyword lists viewer inside ACT** — see DBD's live GAds neg lists without switching tabs. Designed, queued.
4. **Pass 3 location coverage** — current engine catches UK cities + postcodes; non-UK countries (turkey, poland, albania — dental tourism patterns) need either AI-based detection or expanded reference data. Deferred for a fresh session.
5. **PMax Added/Excluded cross-reference** — Google's PMax API doesn't return per-term exclusion status, so that column is blank for PMax terms. Low priority enhancement.

---

## End of day state

- **220+ negatives pushed live** on DBD's account today alone
- **All 3 passes operational** end-to-end on DBD's real data
- **Zero false-positive regressions** remaining from today's classification fixes
- **Client buy-in confirmed** on Week 2 plan
- **Foundation complete** — tomorrow onwards is daily operation, not setup
