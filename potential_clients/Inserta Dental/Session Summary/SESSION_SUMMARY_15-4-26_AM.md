# Dental by Design — Brand Campaign Overhaul
**Session date:** 15 April 2026 (morning, 12:10–16:10)
**Duration:** 4 hours
**Scope:** Complete rebuild of Brand campaign settings, keywords, geo, scheduling and ads

---

## Headline
Rebuilt DBD's Brand campaign from a misconfigured generic-match setup into a tightly-controlled brand-only campaign. Expected immediate impact: ~50% reduction in brand CPC (£3.18 → ~£1.50 cap) while maintaining conversion volume.

---

## The problem (baseline)

| Metric | March 2025 | March 2026 | Change |
|---|---|---|---|
| Avg CPC | £1.52 | £3.18 | **+109%** |
| CPA | £13.20 | £25.44 | **+93%** |
| Monthly spend | £343 | £1,862 | +443% |
| Conversions | 26 | 73 | +181% |

The campaign was paying premium prices for brand traffic. Cause: Max Conversion Value with tROAS bidding let Google bid aggressively; close-variant matching let 611 non-brand search terms leak into the brand campaign, inflating auction signals.

---

## Work delivered

### 1. Marketing Objective set
Changed from unset → **Leads** (matches DBD's form_submit + whatsapp_click conversions).

### 2. Bid strategy switched
- **From:** Max Conversion Value, tROAS 10%
- **To:** Target Impression Share, Absolute Top, 90% target, **max CPC £1.50**

Hard CPC ceiling eliminates runaway bidding. Month-on-month plan: push ceiling down as auctions confirm true brand CPC (probably well below £1.50).

### 3. Negative keywords — 2-part job
- **Initial audit:** 21 high-spend non-brand terms added at campaign level
- **Full review:** 98 additional negatives from the updated search terms report (any non-brand term with ≥1 click or ≥3 impressions)
- **Total campaign-level negatives:** 119

Combined with yesterday's shared-list work (~4,000 account-level negatives already attached to this campaign), brand is now heavily isolated from generic/competitor traffic.

### 4. Brand keyword variants added (exact match only)
User preference: no phrase match on brand campaigns (prevents drift). Added 9 exact-match variants:
```
[dentalbydesign]
[dentist by design]
[dentistry by design]
[dental by design hammersmith]
[dental by design london]
[dental by design near me]
[dental y design]
[by design dental]
[design by dentistry]
```

### 5. Geo targeting — postcode structure built (NEW master list)
Replaced single 25-mile radius (covers Reading to Romford) with **266 Greater London postcodes** structured for monthly performance analysis. Tiers:

- **Tier 1 (DBD core):** W6, W4, W12, W14, SW6
- **Tier 2 (West/Central premium):** 19 postcodes
- **Tier 3 (Wider Greater London):** ~130 postcodes
- **Tier 4 (Outer Greater London boroughs):** BR, CR, DA, EN, HA, IG, KT, RM, SM, TW, UB + Westminster + City of London boroughs as fillers

Critical issues fixed: removed rogue Pakistan location (E-7, Islamabad), removed old 25-mile radius. Known central London sub-district gaps acknowledged (W1, WC1/2, EC1-4 no longer exist as single districts in Google Ads — covered via Westminster + City of London borough targets).

**This postcode list becomes the reusable master** — exportable via Ads Editor for every future DBD campaign. Weekly gap-filling to evolve it.

### 6. Ad scheduling structure
6 time segments per day × 7 days = **42-cell schedule** configured:
- 12:00 AM – 6:00 AM
- 6:00 AM – 9:00 AM
- 9:00 AM – 12:00 PM
- 12:00 PM – 2:00 PM
- 2:00 PM – 6:00 PM
- 6:00 PM – 12:00 AM

No bid adjustments applied — campaign runs 24/7 but reports now segment by block. **Review in 3 weeks** once real data accumulates.

### 7. Two new RSA ads built
Existing Ad 1 preserved (user preference: build new ads rather than edit existing — protects performance history).

**Ad 2 — Service breadth focus:** Pushes Invisalign, veneers, cosmetic, full-mouth care alongside implants. Highlights Hammersmith location, book-online-60-seconds CTA.

**Ad 3 — Trust & expertise focus:** London's most trusted, 25+ years, 2,500+ patients, lifetime guarantee, judgement-free care.

Both ads: 15 headlines, 4 descriptions (max capacity), descriptions 73-84 chars (near 90 ceiling for best Ad Strength). Headline 1 pinned to position 1 on both = brand always shows first.

---

## Expected impact (next 30 days)

- Brand CPC collapses toward £1.50 ceiling (vs £3.18 March average)
- Brand CPA drops proportionally
- Conversions hold or grow (bid cap doesn't limit converting traffic — brand auctions are thin)
- ~£700-£900 of monthly brand campaign waste eliminated (based on March 2026 spend minus expected rebalance)
- Clean 30-day dataset by location and time segment enables next round of optimisation

---

## Known to revisit next week

- Postcode gap-filling (a handful of neighbourhood-level gaps in outer London)
- Ad assets: sitelinks, callouts, images, videos (deferred — focus first on settings, then decorate)
- Segment-level bid adjustments once 3 weeks of data are in
- Ad Strength score verification across all 3 RSAs

---

## Method notes (for ACT build)

- The "default block unless clearly a DBD client" logic proved essential when classifying 611 non-brand terms for a brand campaign
- Location targeting needs post-code tier logic with borough fallbacks (some GB postcode districts no longer exist as single codes)
- Brand campaigns need phrase-match explicitly disabled and rely on exact + negatives only — a pattern ACT should codify
- Keyword growth for brand = exact variants only; shared lists catch the drift
