# DBD Session Summary — Thursday 23 April 2026 (Morning)

**Client:** Dental by Design
**Duration:** ~4 hours (morning session)
**Focus:** End-to-end tracking audit — complete the audit that was opened 22 April, diagnose root causes, apply fixes where possible, send deliverable to client.
**Afternoon session:** search terms + new landing pages (to be appended).

---

## The shift this session represents for DBD

Yesterday's audit was diagnostic but built on assumptions. Today's audit was **definitive** — full month of Dengro data (1,115 leads Apr 1–23), complete Zapier path-condition analysis, live cross-check against every GAds campaign conversion count. The work **reframed the earlier "tracking is broken" story into a precise diagnosis**: tracking is mostly working. Three of four structural issues fixed today. One open for tomorrow.

**Net impact for DBD:**
- Fixed an active leak that was losing ~43 Paid Search leads/week from GAds reporting — invisible until today
- Unblocked DII campaign optimisation (it had been throttled to £100/day because its leads weren't reaching GAds)
- Cleaned conversion reports from 23 actions → 13 meaningful ones
- Locked bidding strategy onto the correct signal (Leads primary, Bookings for manual weekly CPB)
- Renamed the misnamed "Dengro Offline Purchase" action so reports stop lying

---

## Client engagement today

### WhatsApp exchange with Giulio (12:50–13:00)

Confirmed three critical things that grounded the rest of the session:
- **Optimisation target = bookings** (not leads, not revenue)
- **Current CPB ≈ £400; target CPB to scale = £300**
- **Permission granted** to rename the "Dengro Offline Purchase" GAds action (it actually tracks bookings, which Giulio confirmed directly)
- Giulio committed to a follow-up meeting next week to discuss budgets + targets now that tracking is reliable

### Email sent to Giulio + Tommaso (end of session)

Attached: `DBD - Tracking Audit v5 1.pdf` (17 slides). Asked for:
1. Sales team to populate Dengro Treatment amount on every booked/completed lead
2. Awareness on Meta (Paid Social) underperformance — 0.9% vs Paid Search 9%
3. Meeting time next week
4. CallTrackingMetrics login (still pending)

---

## Investigation sequence (how the diagnosis was reached)

1. **Zapier audit — Booking zap first.** Screenshot revealed Path A only fires GAds conv if `Source = "Google"` AND email AND gclid. Also revealed the Booking zap writes to a GAds conversion called `Dengro Offline Purchase` — not a Booking action. Same for Purchase zap. So "Purchase" in GAds was actually tracking bookings.

2. **First detour.** Went too deep into booking value problems (£300 hardcoded, £1,700 Dengro default). Chris called it out — we're optimising for bookings count, not value, so value is irrelevant.

3. **WhatsApp to Giulio** confirmed optimisation target (bookings, CPB £300) and permission to rename the action. Reset the audit focus.

4. **Dengro CSV exported** — 1,115 leads Apr 1–23. Analysed by channel, source, campaign, gclid coverage, booking rate.

5. **Dengro vs GAds cross-check Apr 1–23 (Google-source only):**
   - Leads: Dengro 411 eligible → GAds 389.97 (within ~4%)
   - Bookings: Dengro 24 → GAds 26.44 (essentially matches)
   - Brand showed expected over-attribution (90-day lookback)

6. **Chris challenged the "19% gap" framing.** Re-queried the CSV — when filtered to leads actually meeting Zapier Path A conditions (Source="Google" exact + gclid + email), eligibility dropped to 384 and GAds count was 389.97 = **99% match**. The audit's real finding emerged: tracking works for leads that meet the criteria.

7. **45 blank-source Paid Search leads found.** Daily breakdown: 2 leads pre-15 April, 43 leads from 15 April onwards (spike to 19-31% daily). Pattern unmistakable.

8. **Chris's hypothesis confirmed**: new ads built 15 April are missing UTMs. Verified via GAds Ad report — **85 of 93 DII ads had no Final URL suffix.**

9. **Compounding consequence identified:** Chris had been throttling DII budget from £1,200/day → £100/day over the past week because the campaign looked dead in GAds. In reality it was producing leads, they just weren't reaching GAds reporting.

10. **Fix applied via Google Ads Editor:** Campaign-level Final URL suffix added to DII + Brand. PMax left alone (already working). Verified with GAds "Test tracking set-up" — UTMs now on URL. Test confirmed `utm-tracker.ts` captures UTMs to cookie then strips them from URL bar (expected behaviour — not a bug).

11. **Conversion action cleanup.** Removed 10 deprecated/noise actions:
    - 7 dead / superseded (old Booking, Request Callback, Submit Quiz, 2 Call Extensions, Call Tracking Lead, Refer a patient)
    - 3 Google Business Profile noise (Directions, Other engagements, Menu views)
    - 3 Google-hosted couldn't be removed, demoted to Secondary (Lead form Submit, YouTube subs, YouTube follow-on views)
    
    Renamed `Dengro Offline Purchase` → `Dengro Offline Booking*`. Value setting changed to "Don't use a value" (was "£300 default"). Net: 23 actions → 13 meaningful ones.

12. **Finding 3 surfaced:** GAds Diagnostics on the renamed Booking action showed 40% of events failing with "Unparseable gclid" error since ~20 April. Same timeline as Finding 1 — likely shared root cause. Deferred to tomorrow's investigation; today's UTM fix may incidentally resolve it.

13. **Saved audit summary** to `AUDIT_SUMMARY.md` — locked record of findings and decisions.

14. **Built deck** — 5 iterations (v1–v5). User feedback on each iteration:
    - v3: italics, grey text, missing context pill — rebuilt
    - v4: bullets not recognised as list, missing footer colour bar, italics still present — rebuilt with real `bullet: true` formatting, added thin Google bar above footer, killed italics, line spacing 1.15
    - v5: accepted, user tweaked alignment in Impress, exported PDF

15. **Email drafted and sent** with v5 PDF attached.

---

## Headline numbers

| Metric | Value |
|---|---|
| Dengro leads analysed (Apr 1–23) | 1,115 |
| Paid Search leads | 510 (46%) |
| Paid Social leads | 436 (39%) |
| Paid Search → Booking rate | 9.0% |
| Paid Social → Booking rate | 0.9% |
| Lead sync accuracy for eligible leads | 99% (384 → 389.97) |
| Paid Search leads lost from GAds (Apr 15–22) | ~43 |
| DII ads fixed with UTMs today | 85 of 93 |
| GAds conversion actions cleaned | 23 → 13 |
| Current CPB (confirmed by Giulio) | ~£400 |
| Target CPB to scale | £300 |
| Treatment amount populated (real £ values) | 12 of 1,115 (1%) |
| Unparseable gclid error rate (Apr 21) | 40% (6 of 15 events) |

---

## Fixed today (in GAds directly)

1. **DII + Brand Final URL suffix** added at campaign level — 85 previously untagged ads now inherit UTMs
2. **Renamed** `Dengro Offline Purchase` → `Dengro Offline Booking*`
3. **Value** on the renamed action changed to "Don't use a value" (stripped fake £300/£1,700)
4. **Removed 7 deprecated conversion actions** (old Booking, Request Callback, Submit Quiz, 2 Call Extensions, Call Tracking Lead, Refer a patient)
5. **Removed 3 Google Business Profile noise actions** (Directions, Other engagements, Menu views)
6. **Demoted 3 Google-hosted actions to Secondary** (Lead form — Submit, YouTube channel subs, YouTube follow-on views)
7. **Confirmed bidding strategy**: Dengro Offline Lead stays Primary + in goals; Dengro Offline Booking* stays Primary + NOT in goals (reporting only)

---

## Deliverables produced this session

1. **`AUDIT_SUMMARY.md`** — locked record of findings, fixes applied, open items, data sources consulted
2. **`DBD - Tracking Audit v5.pptx`** (17 slides) — includes:
   - Executive summary + 4 stat cards
   - Optimisation target (Giulio confirmed)
   - Tracking architecture flow diagram
   - Findings 1–4 (each on its own slide) + Findings 5–6 (combined) + Finding 7
   - Status summary (fixed / open)
   - Audit coverage table
   - Next steps
   - Appendix A1: full 23-action conversion table
   - Appendix A2: Zapier architecture
   - Appendix A3: Dengro lead data summary
3. **`DBD - Tracking Audit v5 1.pdf`** — user-finalised version sent to Giulio + Tommaso
4. **Email to Giulio + Tommaso** with deck + 4 explicit asks
5. **GAds configuration changes** as listed in "Fixed today" section
6. **Google Ads Editor changes** — campaign-level Final URL suffix on DII + Brand (PMax untouched)

---

## Session carryovers

### Tomorrow morning (24 April)

1. **Verify UTM fix** — pull Dengro Apr 24–25 Paid Search leads, confirm blank-source rate drops from 12–31% back to near 0%
2. **Verify gclid fix** — check GAds Dengro Offline Booking* Diagnostics, confirm parse error rate drops
3. **Finding 3 investigation** (only if verification fails or partial): surface malformed gclids from GAds Diagnostics, compare with well-formed, check Final URL suffix interaction with auto-tagging
4. **Rename remaining 13 conversion actions** with explicit source/meaning (e.g. "Website — Phone Click" vs "Ad — Brand Call") — this was flagged as an open item by Chris mid-session

### When Giulio replies / access arrives

5. **Sales team workflow update** for Dengro Treatment amount (Finding 4)
6. **CallTrackingMetrics audit** when login arrives
7. **Booking + Purchase zap double-count investigation** (both fire into the same `Dengro Offline Booking*` action on potentially the same event)
8. **Meta (Paid Social) deep-dive** if Giulio wants to investigate Finding 5

### Next week

9. **Budget + CPB targets meeting** with Giulio
10. **Deeper call-conversion audit** (suspected double-count between `Calls from the ads` and campaign-specific Call Extensions)

---

## Bugs / issues encountered this session

- Google-hosted conversion actions (`Lead form — Submit`, YouTube actions, `Clicks to call`) can't be removed from GAds — only demoted. Worked around by setting Secondary where possible. Two stayed stuck at Primary but are not in goals, so no bidding impact.
- My first build of the deck (v3/v4) used `•` characters inline rather than proper `bullet: true` text options — PowerPoint/Impress didn't recognise them as lists, so Chris had to redo bullets. Fixed in v5 using pptxgenjs's real bullet formatting.
- Early in the Zapier investigation I got tunnel-visioned on booking values; Chris caught the drift and redirected to the actual optimisation question. Kept the session on track.

---

---

# DBD Session Summary — Thursday 23 April 2026 (Afternoon)

**Duration:** ~4 hours
**Planned split:** 2 hrs search-terms + ACT upgrades, 2 hrs new DBD landing pages
**Actual:** the search-terms work extended beyond its slot and consumed the full 4 hours. Landing pages deferred to tomorrow morning's 4-hour session.

---

## The shift this session represents

This session turned the PMax side of the negatives system from "partially blind" to "fully sighted." Before today, PMax search terms arrived from the Google Ads API with **NULL cost, NULL conversions, NULL conversion value** — we could see which terms existed but not what they were costing us. Every day's Pass 1/2 review was flying half-blind, and ~80% of daily PMax "block" recommendations were repeat appearances of already-negated terms (the API's 56-day lookback surfacing historical data).

End of session: DBD's PMax pipeline now ingests the GAds UI CSV export (cost, conversions, value per term — everything the API omits), feeds that into the existing review engine, defaults its sort to Cost DESC so money-leakers surface first, and correctly separates first-time blocks from historical replays. **366 PMax negatives pushed today** — far more than any previous session — and the visible leak rate on the dashboard dropped from 80% "already-negated repeats" to ~3%.

---

## Major workstreams

### 1. PMax CSV pipeline — end-to-end build (Build 2 commits N4a + N4b)

Root cause proven earlier in the day: Google's `campaign_search_term_insight` API returns PMax search terms but strips per-term cost/conversion metrics. The UI's scheduled "Search terms report" CSV export contains all the missing metrics. Validated against the UI totals — match to the penny.

Chris + Build 2 shipped in one afternoon:
- New DB table `raw_pmax_search_term_csv` (19 columns, PK on `(client_id, snapshot_date, search_term)`)
- CLI ingestion: `python -m act_dashboard.data_pipeline.pmax_csv_ingest --client-id dbd001 --file "<path>"`
- Encoding detection (UTF-8-CSV vs UTF-16-TSV — the scheduled-email link delivers UTF-16 TSV)
- Upsert into `act_v2_search_terms` for PMax rows only (Search untouched)
- Upsert into `act_v2_pmax_other_bucket` from the "Total: Other search terms" row — cost column now populated on that table too
- Idempotent: re-running doesn't duplicate
- Ingested 22 April's CSV (641 rows, £398.32 total PMax search-attributable cost), verified Dengro vs GAds, all reconciles

**Out-of-scope / follow-up:** auto-watch Downloads folder (Chris clicks the GAds email link manually each morning for now — the link requires his Google login, not automatable).

### 2. Default sort — Cost DESC (Build 2 commit N4c)

Chris's UX problem: ACT's default sort didn't match how he wanted to triage (money-leakers first), so he was Ctrl+F'ing individual terms. Build 2 changed the default `ORDER BY` on the Search Term Review and Pass 3 Suggestions pages to `Cost DESC, Impressions DESC, search_term ASC`. Click-column-header override still works.

### 3. DuckDB UPDATE-on-UNIQUE bug fix (Build 2 commit N4d)

Bug surfaced when Chris tried to approve 3 Pass 3 suggestions (bracknell, gateshead, widnes) after changing their target_list_role from `1_word_phrase` to `location_phrase`. `act_v2_phrase_suggestions` has UNIQUE on `(client_id, analysis_date, fragment, target_list_role)` — DuckDB 1.1.0 throws a false-positive PK error on UPDATEs that modify a UNIQUE column.

Fix: DELETE + INSERT pattern, executed in autocommit with a compensating re-insert on failure. Transaction wrapping doesn't work here — DuckDB 1.1.0 retains the deleted row's PK slot within a transaction's index view and trips the same false positive. Build 2 verified this empirically and deviated from the brief's pseudocode accordingly (good catch).

### 4. Client config updates (direct SQL, not via UI)

Two cleanups pushed directly into `act_v2_clients`:

- **`services_advertised`** gained: `vivo bridges`, `abutments`, `implant consultations` (plural forms that were missing)
- **`rule_7_exclude_tokens`** gained: `implantologist`, `prosthodontist` — stops Rule 7 from auto-blocking queries that contain implant-specialist terms (those terms are in the 1-word exact neg list but shouldn't cascade-block multi-word queries)

Side benefit: the stale memory note about Vivo Bridge needing to be added to advertised was resolved (it was already there — the note was outdated).

### 5. Today's triage outcomes

| Action | PMax | Search |
|---|---|---|
| Auto-blocks pushed (Pass 1/2) | 61 | 8 |
| Review → Approved (pushed as neg) | 305 | 0 |
| Review → Rejected (kept, sticky for 60 days) | 58 | 0 |
| Pending at session end | 3 | 30 |

**Pass 3 (phrase suggestions):** 16 generated, 13 rejected (all too-broad 1-word fragments — "clinic", "treatment", "private", etc), 3 approved as `location_phrase` negs (bracknell, gateshead, widnes).

**Total negatives pushed to DBD GAds today: 374** (366 PMax + 8 Search). By far the biggest single-day push since the system went operational.

**Running 3-day total across 21/22/23 Apr: ~762 negatives pushed.**

### 6. Workflow finding worth flagging

The Pass 1/2 Review UX has a **row-number drift problem**: when Chris actions 50 terms (some approve, some reject), the numbering shifts in real time as rows leave the queue. Working around it by splitting my analysis into "reject these 2-15 specifically, then bulk-approve everything else" kept the session moving, but it's a real UX pain. Logged for tomorrow's work.

---

## Build 2 commits landed today (all pushed to origin/main)

```
c1f05e9  N4d: fix bulk-update target-role change via DELETE+INSERT (DuckDB PK workaround)
eef4789  N4c: default search-term-review sort to Cost DESC
bb3fa38  N4b: pmax CSV ingestion CLI — encoding/delimiter detection, upsert 3 tables
4303d75  N4a: migration — raw_pmax_search_term_csv table + index
```

---

## Carryovers into tomorrow

**Tomorrow morning (24 April — 4-hour session):**
1. Verify UTM fix + gclid-parse-error fix against Apr 24–25 Dengro data
2. Finish Search Review (30 pending)
3. Run Pass 3 again and work through today's remainders
4. Extend `neg_pass3_stopwords` config with today's 13 over-broad terms
5. Build first LP for `*All on 4 Implants` ad group — to push via PR to DBD Astro repo (pending Giulio's OK on the git workflow, WhatsApp to go out tonight/morning)

**Tomorrow afternoon (24 April — 4-hour session):**
1. Mass-produce remaining LPs off the template built in the morning
2. Week 2 Report for DBD (due EoD Friday)

**Build 2 backlog (filed today, not done):**
- Auto-watch Downloads folder for PMax CSV
- Scheduler pipeline truncation bug (neg phases silently skipped this morning)
- Relax rate limit on internal localhost endpoints (hit 429 mid-triage)
- Rename remaining 13 GAds conversion actions with explicit source/meaning
- Review queue UX — row-number drift fix
- Audit `1 WRD [ex]` / `2 WRDS [ex]` neg lists for other overly-aggressive tokens

**For Giulio (tonight / tomorrow):**
- WhatsApp: permission to push new LP to a branch on the Astro repo via PR
- Confirm whether "inserta dental" is a legacy/parent brand term (surfaced as a search term today)

---

## Bugs / issues encountered this session

- **DuckDB 1.1.0 transaction-scope PK retention**: wrapping DELETE + INSERT in a transaction re-triggers the false-positive PK error this bug works around. Autocommit + compensating re-insert is the working pattern. Worth documenting more broadly for the codebase.
- **Flask rate limiter** threw 429s mid-triage after rapid-fire approve/reject calls. Restarting Flask cleared it. Internal-use endpoints shouldn't be rate-limited.
- **Overnight scheduler truncated** today — only ran `ingestion` + `engine` phases, skipped `neg_stale_cleanup`, `neg_pass1`, `neg_pass2`, `neg_sticky_expiry`. Worked around with manual Reclassify click. Root cause unknown, needs investigation.
- **Review queue row-number drift** — significant UX pain when working batches of 50 with mixed approve/reject. Current workaround of "reject-smaller-list-first, then bulk-approve-rest" is functional but fragile.
- **Terminology confusion**: ACT uses "Approve" to mean "approve as a block / push as negative" and "Reject" to mean "reject the block / keep running." Inverted from colloquial usage. Documented here so future PM sessions don't relearn it.

---

## Two moments worth naming

1. **The PMax CSV plan came from Chris, not me.** I had been working around API limits with proxy estimates. Chris's instinct — "if Google Ads will email me the CSV, ACT can read the CSV" — turned a platform-ceiling into a pipeline. This is the kind of thinking that makes ACT genuinely differentiated.

2. **"We only do proper fixes, never plasters."** Flagged when I suggested a workaround for the DuckDB UPDATE bug. This is a durable rule — saved for the next PM session.

