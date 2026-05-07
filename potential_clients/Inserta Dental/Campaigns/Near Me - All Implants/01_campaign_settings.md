# Campaign Settings — Search - Near Me - All Implants

**Built:** Wed 29 Apr 2026
**Client:** Dental by Design (DBD)
**Customer ID:** 5380281688

---

## Campaign-level

| Setting | Value |
|---|---|
| Campaign name | `Search - Near Me - All Implants` |
| Type | Search |
| Networks | Google Search only — **uncheck Search Partners + Display Network** |
| Locations | Existing 270-postcode London target list (use the saved location list — same as Brand + DII campaigns) |
| Location options | "Presence: People in or regularly in your targeted locations" (NOT "interested in") |
| Languages | English |
| Bidding | Maximise Conversions with **target CPA = £60** |
| Conversion goals | Account-default (**Dengro Lead primary** — bidding signal, **Dengro Offline Booking secondary** — reporting). Per MEMORY 23 Apr lock: Lead = primary because it's higher-volume signal for auto-bidder, Booking = reporting metric. |
| Daily budget | £100/day (scale up once data lands — likely £150-200/day within 7-14 days) |
| Delivery | Standard |
| Ad rotation | Optimise (default) |
| Ad schedule | All hours, all days. Adjust later from segment data. |
| Devices | All. Mobile bid adjustment 0% to start. |
| Start date | Today (Wed 29 Apr 2026) |
| End date | None |
| Final URL expansion | **OFF** (we control LPs explicitly) |
| Dynamic Search Ads | **OFF** |
| Audience targeting | Observation mode only — add "All Visitors" + "Past Converters" remarketing lists for bid adjustments later |

## Match-type policy

- **Specific ad groups (1-6):** Phrase + Exact only. No Broad. Broad on near-me intent burns budget on cleaning queries.
- **Catchall ad group (7):** Phrase only on short-root keywords. No Broad, no Exact. Phrase catches long tail without exact-match rigidity.

## Conversion settings

- Primary: `Dengro Lead` (higher-volume signal — what bidding optimises toward)
- Secondary: `Dengro Offline Booking*` (reporting metric — what we measure success against)
- All other goals: secondary / observation
- Locked Wed 29 Apr per `MEMORY.md` 23 Apr note

## Initial guardrails to set in Campaign settings

- Maximum CPC bid limit: **£8** (safety cap — implants CPCs go high, we don't want a £30 click on day one)
- Reset target CPA after 14 days based on actual data

## Asset extensions (campaign-level)

Reuse account-level assets where they exist. Otherwise add at campaign level:

- **Sitelinks (4):** Free Consultation · Patient Reviews · Finance Options · Find Us
- **Callouts (6+):** £25 booking deposit · Free initial consultation · 25+ years expertise · Implants from £995 · 0% finance available · Located in West London
- **Structured snippets:**
  - Services: Single Tooth Implants, Full Mouth Implants, All-on-4, Same Day Teeth, Pay Monthly Implants
  - Brands: Straumann, Nobel Biocare (only if accurate — confirm with Giulio if unclear)
- **Call extension:** practice phone number, Mon-Fri 09:00-18:00, Sat 09:00-13:00
- **Location extension:** linked Google Business Profile

## Why these specific choices

- **Search Partners OFF** — unaccountable inventory, drains budget
- **"Presence" not "Interested in"** — near-me intent = literal local searcher. People "interested in" London from Manchester are not who we want
- **tCPA £60 not £75** — Chris's call. DBD's Search-side CPA on DII is hitting £50 post-tracking-fix; £60 is a credible stretch target
- **Final URL Expansion OFF** — we built specific LPs per ad group; don't let Google rewrite them
- **No Broad match** — too risky on local intent. Phrase + Exact gives us volume without the cleanup cost
- **CPC cap £8** — sanity guardrail for first 14 days, can lift after

---

## Negative keywords

See `02_cross_level_negatives.md` for the full negative shield strategy and lists.
