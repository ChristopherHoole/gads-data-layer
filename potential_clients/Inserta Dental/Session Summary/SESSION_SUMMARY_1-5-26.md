# Session Summary — Friday 1 May 2026

**Client:** Dental by Design (DBD)
**Hours:** ~8h DBD

## Time breakdown

- **2h** — Negative keyword list audit (continuation from yesterday) + Near Me search-term audit
- **3h** — PMax campaign deep-dive + asset cleanup + sitelink drafting
- **1h** — Audience manager + GTM/GA4 tag investigation
- **2h** — Dengro 16-week lead-to-booking investigation

## Headline outcomes

1. **Negative list audit complete** — ~160 implant-blocking negatives removed today across 7 lists (on top of yesterday's audit). Audit cycle done for now.
2. **PMax throttling diagnosed + cleanup executed** — root cause = Custom Interest audience signal added 30 Apr (was previously empty) + 7 stacked changes same day. Cleanup removed 17 Google AI assets, 3 YT videos with policy flags, edited 2 policy-flagged copy assets, added 6 new sitelinks, turned off auto-asset feeders.
3. **Audience + tag setup verified working** — GTM `GTM-KBPKCLKB` confirmed installed (first-party mode), publishes `AW-478734574` (Google Ads) + `G-TX9XP8RLZ7` (GA4). Google Signals turned ON in GA4 (was off).
4. **Dengro investigation: SMOKING GUN identified** — calling Paid Search leads within 1 hour produces a 22.6% book rate vs 5.5% if called 12h+ later. 4x conversion difference. Single sales agent owns inbound Metro AND all outbound Paid Search = bottleneck.

---

## 1. Negative keyword list audit (continued)

Completing the multi-day audit started yesterday. Today's removals:

### 3 WRDS "ph" (34 entries)
**Removed 3:**
- `for over 65` (older patients are core implant demo)
- `average price of` (research-stage but high intent)
- `how to get` (could catch finance-intent)

### 4 WRDS [ex] (752 entries, 2 pages)
**Removed 31 definite** including:
- Cheap/finance: `affordable dental implants london`, `cheap dental implants uk`, `cheap implants near me`, `cheapest dental implants london/uk`, `dental implant consultation free`, `dental implants for pensioners`, `dental implants uk cheapest`, `dental plan for implants`, `deals on dental implants`, `low cost dental implants`, `replace missing teeth cheap`, `dentist that do implants`
- High-intent: `i have missing teeth`, `i want new teeth`, `implant clinic near me`, `implant specialist near me`, `missing front tooth replacement`, `missing teeth in adults`, `missing teeth options uk`, `options for missing teeth`, `options for tooth loss`, `replacements for missing teeth`, `replacing missing teeth cost`, `teeth removal and implants`, `tooth removal and replacement`
- Free consult (DBD offers): `free dental consultation london`

**Pending Giulio:** 29 items (denture/brand/ceramic).

### 5+ WRDS [ex] (590 entries, 2 pages)
**Removed 121 definite** — all high-intent / cheap / DBD-offered queries (full list in script `_5word_neg_audit.py`). Patterns: cheap/finance variations, free consultation variations, "how long do dental implants last/take" research questions, missing-teeth options, implant cost queries, bone-loss + sinus lift questions, full-set / arch queries, single-implant queries.

**Pending Giulio:** 23 items.

### Com & Bran "ph" (189 entries)
**Removed:** `forever` (too generic — blocks "dental implants forever" etc.)
**Flagged for review:** other generic single-word phrase negs (`flash`, `embrace`, `aspire`, `infinity`, `mona`, `waterfall`, etc.) — held for now.

### Com & Bran [ex] (45 entries)
**Removed:** `inplants` (typo of "implants" — not a competitor brand).

### Loc 1 WRD "ph" (226 entries)
**Removed 4 inside-M25 locations:**
- `bushey` (Hertfordshire, south of M25)
- `borehamwood` (Hertfordshire, just south of M25 J23)
- `radlett` (Hertsmere, ~1 mile south of M25)
- `chigwell` (Essex, west of M25 J26)

DBD's confirmed catchment: **inside the M25**.

### Total today: ~160 negatives removed across 7 lists.

Combined with yesterday: ~235 implant-blocking negatives removed across the audit cycle.

---

## 2. PMax campaign deep-dive

### Diagnosis

PMax spend collapsed over 5 days:
- 27 Apr: £1,143
- 28 Apr: £1,348 (peak)
- 29 Apr: £1,110
- 30 Apr: £653 (-41%)
- 1 May: £384 (still going)

`implants-giulio` impressions cliff: 290k → 18k → 5k in 3 days post-30 Apr.

**Channel mix flip vs last week (20-26 Apr):**
- Search Partners: 51% → 71%
- YouTube: 33% → 18% (absolute spend £399/day → £164/day, CPA £63→£117)
- Google Search: 16% → 10%

**Investigation findings:**
- Asset library audit (142 assets across account/campaign/asset-group levels): **ZERO disapproved**. All "Limited" status = UK Health in personalised advertising regulatory ceiling — not fixable, not the cause.
- Real cause = compound 30 Apr changes: Custom Interest audience signal added (was previously empty), logo swap at campaign level, asset edits to giulio, 9 phrase negs added (`near me`, `local`, etc.), 18 search themes added, tCPA cut £59→£58, budget cut £1,150→£1,100, new asset group `implants-pay-monthly` created. Seven simultaneous changes = PMax learning reset.

### Cleanup executed today

**Removed from `implants-giulio` asset group:**
- 14 Google AI auto-generated images (zero conv) — list in `_dengro` analysis
- 3 Google AI logos at campaign level (zero conv)
- 3 YouTube videos flagged "Negative events and imagery": 345716928404, 343654142501, 345806307106

**Edited (not removed — were converting):**
- Headline "Permanent Teeth in 48 Hours" — Clickbait flag — needs rewrite
- Long headline + Description "Revolutionary 48-Hour Permanent Teeth. Skip Months of Temps. 99.12% Success Rate" — Financial services UK flag (the 99.12% claim) — replaced with:
  - LH: "Permanent Teeth in 48 Hours. Lifetime Warranty Included. Free Consultation Available."
  - D: "Skip months of temporary teeth. Permanent implants in 48 hours, lifetime warranty."
  - Plus 2nd variant LH/D drafted for variety
- Description "Award-Winning Team. Vivo Bridge® Technology. Final Teeth in 2 Visits" — Financial services UK flag — replaced with:
  - LH: "Permanent Implants. Award-Winning Team. Free Initial Consultation in West London."
  - D: "West London implant clinic. Award-winning team. Free 3D consultation included."

**Added 6 new campaign-level sitelinks (URLs verified live):**
1. Lifetime Warranty → `https://dentalbydesign.co.uk/dental-implants/lifetime-warranty`
2. Vivo Bridge® Tech → `https://dentalbydesign.co.uk/dental-implants/vivo-bridge`
3. Patient Reviews → `https://dentalbydesign.co.uk/dental-by-design-reviews`
4. Pay Monthly Plans → `https://dentalbydesign.co.uk/dental-implants/monthly-payments`
5. Award-Winning Team → `https://dentalbydesign.co.uk/about-us`
6. Contact Us → `https://dentalbydesign.co.uk/contact-us/`
7. Implant Pricing → `https://dentalbydesign.co.uk/dental-implants/pricing/`

(Original sitelink #4 "Single Implant £1,695" replaced after Chris flagged it. £1,695 vs live ad £995 mismatch banked for Giulio question.)

**Turned OFF:**
- Image Enhancement (account level) — Google AI was modifying uploaded images
- Landing Page Images (account level) — Google AI was scraping LP for images
- Brand guidelines logos in PMax — even uploaded clean account logo got Health flag, account-level logo only

**Set:**
- Display path: `dental-implants` / `in-48-hours`
- Target CPA reset £58 → £60

**Held paused:** new asset group `implants-pay-monthly` (waiting for stabilisation before launch).

---

## 3. Audience + tag setup investigation

### Audience CSV findings
- 3 audiences "Disabled due to policy violation" (UK Health) — `Google-engaged audiences` (3,200), `All converters` (0), `All visitors (Google Ads)` (0). All from Nov 2020/2024.
- 2 GA-source audiences at size 0 — `Purchasers` + `All Users of dentalbydesign.co.uk` (Sept 2025).

### Tag investigation
- Initial curl missed GTM container in HTML (loaded via first-party server-side mode, hence not in static HTML).
- Confirmed: GTM container `GTM-KBPKCLKB` IS installed and published. Loadable at HTTP 200, 349KB.
- Container publishes:
  - **Google Ads tag: `AW-478734574`**
  - **GA4: `G-TX9XP8RLZ7`**
- Setup is correct. Tags fire after Advertisement consent.

### Actions taken
- Built audience: `All visitors, last 540 days` (Open, populating).
- Turned ON Google Signals in GA4 (was OFF — explains zero GA-source audience size).
- Increased GA4 event data retention 2 months → 14 months.

### Remaining caveat
- 3 disabled audiences will stay disabled (UK Health policy) regardless of Google Signals being on. Customer Match (uploaded converted bookings) bypasses this — most reliable audience source for DBD.

---

## 4. Dengro 16-week lead-to-booking investigation

### Data
- Loaded 6,174 leads (Jan 5 → Apr 26) from 16 weekly Dengro CSVs into DuckDB.
- DB: `potential_clients/Inserta Dental/data/400 bookings per month/dengro_investigation.duckdb`
- Scripts: `_load_dengro.py`, `_dengro_q1_q2_q3.py`, `_dengro_pivot_v2.py`, `_dengro_paid_search_weekly.py`, `_dengro_call_speed_buckets.py`, `_dengro_pct_by_bucket.py`

### THE SMOKING GUN — call speed vs booking rate

**Paid Search overall (16 weeks combined):**

| Bucket | Leads | Booked | Book % |
|---|---|---|---|
| **0-1h** | 1,001 | 226 | **22.6%** |
| 1-3h | 277 | 46 | 16.6% |
| 3-6h | 229 | 20 | 8.7% |
| 6-12h | 338 | 13 | 3.8% |
| 12+h | 2,308 | 127 | **5.5%** |
| Never | 21 | 0 | 0.0% |

**Calling within 1 hour produces 4x the booking rate of calling 12+ hours later.**

### Recent weeks anomaly

| Week | Leads | % called 0-1h | % called 12+h | Book % |
|---|---|---|---|---|
| Mar 9 (best) | 151 | 30% | 47% | 17.9% |
| Apr 6 | 136 | 26% | 46% | 11.0% |
| **Apr 13** | **180** | **12%** | **61%** | **6.1%** |
| **Apr 20** | **227** | **26%** | **52%** | **6.2%** + 11 leads NEVER contacted (4.8%) |

Weekly avg time-to-first-contact on Paid Search jumped from 11h (Apr 6) → 18h (Apr 13) → 16h (Apr 20). Confirms Dengro dashboard's "+58.63%" alert.

### Other findings

**Sales agent breakdown (booked_by, GAds Paid Search leads only, 16 weeks):**
- `feria@` — 271 (dominant, but volumes dropped sharply Mar onwards)
- `patrycja@` — 111
- `angelica@` — 18
- `livi@` — 16
- `birsu@` — **6 — first appears Apr 13 (NEW agent)**
- `tommaso@` — 2

**Critical context (revealed end of session):** Single sales agent owns inbound Metro leads (high-priority phone) AND all outbound Paid Search calling. Inbound calls always win → outbound queue stretches → Paid Search 12+h waits. **This is the structural cause of slower call response.**

**YouTube source mis-tagging check:** Searched all fields across 16 weeks (Source, Channel, UTM source/medium/campaign). **ZERO matches** for YouTube/YT/video. Either the mis-tagging happens in a Dengro field not in this export, or it's been corrected, or it's somewhere else (e.g. GAds attribution panel).

---

## 5. Process learnings banked

- **Phrase neg `forever` is too generic** — blocks any query containing "forever". Audit all single-word competitor/brand phrase negs for this risk.
- **PMax "Limited" status is regulatory, not violation** — UK Health in personalised advertising affects every dental advertiser. Don't try to "fix" Limited assets — they're working as designed.
- **Disapproved ≠ Limited.** True disapprovals are rare; Limited just caps audience features.
- **GTM first-party server-side tagging won't show in HTML grep** — loaded via JS injection post-consent. Always check the published container at `googletagmanager.com/gtm.js?id=XXX` directly.
- **Google Signals is OFF by default in GA4** — must be explicitly enabled for GA4 audiences to flow into GAds for remarketing.
- **PMax algorithm needs 7-14 days to recover after major changes.** Stack 7+ changes on one day = guaranteed extended learning reset.
- **DBD catchment = inside M25.** Use this when auditing geo neg lists.
- **Single-agent inbound+outbound bottleneck** is structural — no amount of GAds optimisation can fix call response speed if same person is on both queues.

---

## 6. Open / pending

### Pending Giulio decisions
- Implant-supported dentures — affects ~12 negs across lists
- Implant brands DBD uses — Nobel Biocare confirmed; Straumann (already unblocked), Osstem, Megagen, MIS, Medentika, Neoss, Biohorizon, Hiossen, Neodent, Mini, Zygomatic, Pterygoid, Basal, Screwless TBC
- DBD founding year — LP placeholder "for over a decade"
- Ceramic/zirconia implants — does DBD offer?
- **£995 vs £1,695 single implant pricing mismatch** — live ad headline says From £995, LP says From £1,695

### Pending image policy reviews (carried)
- 2nd Brand image (face portrait test)
- 3 videoframe images on DII (pending policy)
- 3 videoframe images on Near Me (pending policy)
- New PMax asset group `implants-pay-monthly` (held until giulio recovers)

### Outstanding ACT work
- 2.1e — AI-driven Pass 3 (`docs/SCOPE_2.1e_AI_PASS_3.md`) — Sunday rebuild target
- Customer Match upload (Dengro converted-bookings → PMax audience signal score 1/2 → 2/2)

### Pending Tommaso/Giulio
- Sales team structure: 1 agent on inbound Metro + outbound Paid Search = bottleneck. Recommendation: separate queues OR add capacity.

---

## 7. Tomorrow (Sat 2 May)

**Primary task:** 5-slide deck for Tommaso + Giulio with Dengro lead-response findings.

**Slide outline:**
1. **Headline finding** — calling within 1h → 22.6% book; calling 12h+ → 5.5%. **4x difference.**
2. **The bottleneck** — one agent owns inbound Metro AND all outbound Paid Search.
3. **Trend that triggered investigation** — Avg time-to-contact +58.6% on Dengro dashboard; weekly book rate halved 11% → 6% in Apr.
4. **Per-week proof** — % called 0-1h dropped to 12% week of Apr 13; 12+h jumped to 61%. 11 leads never contacted week of Apr 20.
5. **Recommendation** — separate inbound + outbound queues OR add capacity. Don't waste paid-ads spend on leads nobody calls.

**Watch for tomorrow:**
- Giulio asset group impressions recovery (was 5k/day yesterday)
- If still suppressed by tomorrow afternoon → discuss removing Custom Interest audience signal

---

## 8. Closing note

Major day. Three big jobs finished/advanced:
1. Multi-day neg audit cycle complete (~235 implants unblocked across 2 days)
2. PMax cleanup executed + diagnosed correctly (audience signal + compounding changes, not policy violations as initially feared)
3. Dengro investigation surfaced the smoking gun — sales response speed, not media — which is exactly the kind of finding that protects DBD's spend and builds trust with Tommaso/Giulio when delivered cleanly tomorrow.
