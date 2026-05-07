# Session Summary — Wednesday 29 April 2026

**Client:** Dental by Design (DBD)
**Hours:** 8h DBD (subcontractor)

## Time breakdown

- **1.0h** — Strategic call with Tommaso + Giulio (Week 2 end-of-week report + 400 Bookings Strategic Plan walkthrough)
- **0.5h** — Call with Giulio + DBD's Google rep
- **0.5h** — PMax API search-term ingestion killed (Build 2 brief, n7 migration, 1089 ghost rows deleted, CSV ingest verified)
- **1.0h** — Daily search-term triage (122 pushed to neg lists, Pass 3 retest, broken-engine evidence captured)
- **0.5h** — Pass 3 rebuild brief drafted (`docs/SCOPE_2.1e_AI_PASS_3.md`) for Sunday
- **4.5h** — Near Me search campaign built end-to-end (7 LPs, 7 ad groups, 21 RSAs, 6 sitelinks, ad strength audit + replacements, account-level negs attached)

## Headline outcomes
1. **PMax API search-term ingestion killed** — CSV is now sole source. Migration `n7` deleted 1089 API-ghost rows.
2. **Daily search-term triage — 122 pushed** to neg lists (within 100-150 daily target).
3. **Near Me search campaign built end-to-end and live** — 7 ad groups, 7 new LPs, 21 RSAs, 6 sitelinks, account-level negs attached. Ad strength audit + replacement headlines/descriptions delivered for all 21 ads.
4. **Pass 3 confirmed broken** on real DBD data. Sunday rebuild brief drafted (`docs/SCOPE_2.1e_AI_PASS_3.md`).
5. **Strategic call with Tommaso + Giulio (1h)** — walkthrough of Week 2 EOW report + 400 Bookings Strategic Plan deck.
6. **Call with Giulio + DBD's Google rep (30min)** — separate slot.

---

## 1. PMax search-term API ingestion — killed

**Why:** ACT was still pulling PMax search terms via the Google Ads `campaign_search_term_insight` API every overnight ingestion, despite our agreement weeks ago that Chris's daily PMax CSV is the sole source. The API call was never disabled. Result: 179 stale "ghost" rows for DBD on 4-28 with `cost = NULL` polluting the Search Term Review UI.

**Fix:** Build 2 commit `02e99db` — modified `ingest_pmax_search_terms` in `act_dashboard/data_pipeline/google_ads_ingestion.py` to keep the API call (still feeds `act_v2_pmax_other_bucket` aggregate) but skip the per-term `INSERT INTO act_v2_search_terms`. Plus migration `migrate_n7_drop_api_pmax_search_terms.py`.

**Migration result:**
- 1089 API-ghost rows deleted (DBD-only)
- 2655 CSV-derived rows preserved
- Delta = 0 (no false positives)

**Verification:** today's CSV ingest landed cleanly, populated 403 rows for 4-28 with cost £731.22 / 11 conv. Pre-migration would have been mixed. Now CSV is the only source for per-term PMax data.

---

## 2. Daily triage — 122 pushed

End-of-day counters (cross-tab Search + PMax):
- **Pushed to Neg Lists: 122**
- Didn't Block: 59
- Pending: 277

Channel split: 67 Search push + 55 PMax push.

Within Chris's 100-150 daily cap. Sticky-rejection cycle worked correctly across PMax. AI Verdict pills (BLOCK / DON'T BLOCK / UNSURE) read naturally during triage.

---

## 3. Pass 3 retest — confirmed broken

Pass 3 ran on the 122 pushed terms, returned 7 fragments:
- 5 stopword junk: `can`, `can you`, `you get`, `can you get`, `can you get veneers`
- 1 location mis-routed: `crewe` → generic `1 WRD ph` (should be `Loc 1 word ph`)
- 1 borderline OK: `you get veneers` → `Off Not Adv ph`

Real off-not-advertised tokens visible in the day's Search/PMax data — `sedation`, `flipper`, `fillings` — were missed entirely.

**Sunday rebuild brief:** `docs/SCOPE_2.1e_AI_PASS_3.md` drafted. New approach: AI-driven Pass 3 fed the **full day's** Search + PMax dataset (not just pushed terms) + client profile + history. Returns ranked fragments + target-list assignments + theme summary. Cost ~$0.10/client/day. Build target Sunday 3 May.

---

## 4. Strategic call — Tommaso + Giulio (1h)

Walkthrough of the two decks emailed yesterday:
- **Week 2 End-of-Week Report** (9 slides) — CPA £82 → £46 (-36%), bookings +27%, leads +26%, tracking-fix story, work delivered.
- **400-Bookings Strategic Plan** (15 slides) — 6-month path from current ~155 bookings/mo to 400/mo, channel-by-channel scaling, paid-ads-led narrative, £60k → £142k/mo budget ramp.

Outcomes / follow-ups TBD — capture in tomorrow's session.

## 5. Call — Giulio + DBD's Google rep (30min)

Separate 30-minute call with Giulio and their Google account rep. Specific agenda + outcomes TBD — capture in tomorrow's session.

## 6. Job applications

While daily triage ran, replied to two LinkedIn posts from Sphere London recruiters:
- **Jaquarn Nelson** — 2-day part-time Paid Media Manager contract, £200/day outside IR35, fully remote. Sent CV.
- **Andrew Morrison** — programmatic-led contract with YouTube/Demand Gen requirement. Sent honest email flagging programmatic gap; played the relationship-building angle (same agency as Jaquarn).

---

## 7. Near Me search campaign — built end-to-end

The 6h project from this week's plan, executed in one sitting.

### Campaign settings
- **Name:** `Search - Near Me - All Implants`
- **Bidding:** Max Conversions, tCPA £60
- **Budget:** £100/day, scale up
- **Locations:** existing 270-postcode London target list
- **Conversion goals:** Dengro Lead primary (bidding signal), Dengro Offline Booking secondary (reporting)
- **Networks:** Search only — no partners, no display
- **Match-type policy:** Phrase + Exact on AG1-6, Phrase only on AG7 catchall

### 7 ad groups + 7 live LPs

| AG | Name | LP URL | Commit |
|---|---|---|---|
| 1 | Dental Implant Clinic Near Me | `/google/dental-implant-clinic-near-me` | `2564143` |
| 2 | Full Mouth Implants Near Me | `/google/full-mouth-implants-near-me` | `0226113` |
| 3 | Same Day Implants Near Me | `/google/same-day-implants-near-me` | `4fba77d` |
| 4 | Single Tooth Near Me | `/google/single-tooth-implant-near-me` | `0f15d6b` |
| 5 | Pay Monthly Implants Near Me | `/google/pay-monthly-implants-near-me` | `bb369cf` |
| 6 | Teeth Fixing Near Me | `/google/teeth-fixing-near-me` | `f9a1a32` |
| 7 | Catchall Dental Implants Near Me | `/google/dental-implants-near-me` | `77e5cb3` *(rewrite-in-place)* |

All 7 LPs:
- Monday's exact format (no Map block, no Address strip — the "Universal Near Me" treatment in my original brief was over-engineered, removed)
- Clean English in body copy, no keyword stuffing
- Keyword density via H1, slug, SEO meta, FAQ questions, FAQ section heading
- Each AG keyword visible at least once organically

### 21 RSAs (cleaned)

- **No £25 deposit** anywhere (was 41 instances)
- **No jargon** (no ADI/CBCT/GDC/Immediate Loading/Protocol)
- **No per-implant pricing** in headlines or descriptions (Chris flagged this misleads patients)
- All headlines ≤30 chars, all descriptions ≤90 chars
- Each ad group has 3 ads with strong AG keyword anchoring
- Each ad has a unique Path 2 (e.g. `implant-clinic / specialist`, `implant-clinic / near-you`, `implant-clinic / hammersmith`) so they're distinguishable in GAds reports

### 6 sitelinks (campaign-level)

1. Free 3D Consultation → `/dental-implants/free-3d-consultation`
2. Patient Reviews → `/dental-by-design-reviews`
3. 0% Finance Plans → `/dental-implants/monthly-payments`
4. Lifetime Warranty → `/dental-implants/lifetime-warranty`
5. Implant Pricing Guide → `/dental-implants/cost-and-information-guide`
6. Find Our Clinic → `/contact-us`

### Negatives

Attached the 15 active account-level negative lists to the new campaign. Skipped my originally-proposed "shield" ad-group negatives — overengineered and would have blocked legitimate intent. Will revisit only if cannibalization shows in search-term data after a week.

### Ad strength audit

Initial scores from CSV:
- AG1: Average × 3
- AG2: Good × 3
- AG3: Good × 1, Average × 2
- AG4: Poor × 3
- AG5: Average × 3
- AG6: Good × 3
- AG7: Poor × 3

Delivered keyword-saturated replacement headlines + descriptions for all 21 ads, ordered for swap-until-Excellent flow. Chris worked through each AG sequentially, replacing 1 by 1 in GAds Editor until each ad hit Excellent.

---

## 8. Process learnings banked

- **AI Verdict pills + sticky-rejection cycles working** in the live triage flow.
- **Pass 3 needs total rebuild** — rule-based n-gram generator surfaces stopwords, misses real intent. AI-driven Sunday work is the right move.
- **PMax CSV pipeline now clean** — single source of truth, no API ghosts.
- **LP build session approach was over-engineered** — delegating to a separate Build session was slower than building the LPs directly. Final 6 LPs built sequentially in this session — faster, cleaner, same Monday format applied consistently.
- **"Near me" intent doesn't fit 3rd-person body copy** — fundamentally a 1st-person search modifier. Keyword density goes in H1, slug, FAQ questions, SEO meta. Body copy reads as natural English.
- **Headline rules locked:** no banned claims (no 99.12%, no Save 60%, no Top 10 Europe), no £25 deposit, no per-implant pricing, no jargon (no ADI/CBCT/GDC).
- **Display path doubles as ad ID** — assigning a unique Path 2 per ad inside an ad group (e.g. `implant-clinic / specialist` vs `implant-clinic / near-you`) gives Chris a clean way to identify ads in GAds reports without relying on Google's auto-numbering.

---

## 9. Open items

### For Chris (his side)
- **Capture outcomes from today's two calls** (Tommaso + Giulio strategic call, and Giulio + Google rep call) into tomorrow's session.
- Once campaign is unpaused, **monitor first 7 days** for cannibalization in AG7 search terms — if specific-AG queries are slipping into Catchall, add targeted negs then (not now).
- Outstanding data chases: Meta Ads spend, Bing/Microsoft Ads spend, Sun/Metro tracking-link history.
- Confirm DBD's founding year (placeholder "for over a decade" used on LPs).
- Confirm whether DBD offers implant-supported dentures (still open from yesterday for `denture` neg-keyword decision).

### For ACT (build queue)
- **2.1e — AI-driven Pass 3** — Sunday rebuild. Brief: `docs/SCOPE_2.1e_AI_PASS_3.md`.
- Stage 11 + 12 final QA — pending real-world test once Pass 3 rebuild ships.
- Tier 1 backlog quick wins: 1.1 scheduler pipeline truncation, 1.2 CHECK constraint, 1.3 rate limiter IP exemption.

### Tomorrow (Thu 30 Apr) per `WEEK_PLAN_27-4-26.md`
- 2h daily search term triage
- 6h PMax overhaul
- Watch new Near Me campaign performance once unpaused

---

## 10. Closing note

Big delivery day. PMax pipeline cleaned up properly, near-me campaign built end-to-end (was budgeted as 6h, came in close to that), Pass 3 backlog item properly scoped for Sunday. The Near Me campaign is the first structured Search campaign committed to in the 400-Bookings strategic deck — it's now ready to launch. Tomorrow's PMax overhaul is the second move in the PMax → Search migration narrative.
