# Session Summary — Sun 3 May 2026

**Client:** Dental by Design (DBD) + ACT
**Hours:** ~6h (PM session)

## Headline outcomes

1. **ACT 2.1e AI Pass 3 SHIPPED to origin/main** — commit `422ce6b`. Replaces rule-based fragment generator with AI-driven full-dataset routing.
2. **Maximising Bookings deck shipped** (7 slides) — Sales response speed analysis for Tommaso/Giulio.
3. **Customer Match BLOCKED** at GAds account level — UK Health policy. Apply via Google rep.
4. **April invoice sent to Tommaso** — £3,000 / 100h.
5. **PROBLEM SURFACED**: Pass 3 button click on Sunday's data did not write fragments — needs debug.

---

## 1. ACT 2.1e AI Pass 3 build (~3h)

Builder session via Pause-gate pattern (1/2/3). Brief at `docs/BRIEF_2.1e_BUILD_3-5-26.md`. Original scope at `docs/SCOPE_2.1e_AI_PASS_3.md`.

**Resolved 4 open questions before build:**
- Table name: reuse `act_v2_phrase_suggestions` (not new table as scope guessed)
- Rule-based engine path: `act_dashboard/engine/negatives/pass3.py` — keep as fallback
- Themes: separate table `act_v2_pass3_themes`
- AI re-rank Pass 1+2: NO, strictly downstream

**Files shipped:**
- NEW: `act_dashboard/engine/pass3_ai.py` (orchestrator)
- NEW: `act_dashboard/ai/prompts/search_terms_pass3_v2.txt` (with Rule 3a — industry-knowledge fallback for off-not-adv)
- NEW: `act_dashboard/db/migrations/migrate_n8_pass3_ai.py` (4 cols + themes table)
- NEW: `act_dashboard/routes/v2_search_terms_api.py` (new endpoint `/v2/api/search-terms/run-pass3-ai`)
- MODIFIED: prompts `__init__.py`, routes `__init__.py`, app.py CSRF exempt, search_term_review.html (theme banner), search_term_review.js (button URL swap + theme hydration), CSS

**Pause 2 tests on DBD 2026-04-28 dataset:**
- Attempt 1: missed `flipper` (not in services_not_advertised list)
- After Rule 3a added: **4-of-4 hits** — sedation (iv sedation), flipper, fillings, crewe
- 24 fragments, 4 themes, zero stopword junk

**Pause 3 end-to-end run (DBD 2026-04-28):**
- 58 pending fragments + 8 pushed preserved + 4 themes landed
- Cost ~$0.99/run on Opus (rationale capped, source_terms ≤3 items)
- Wall time 309s

**3 quality fixes baked in before commit:**
- Sanitise-and-drop bad fragments (don't nuke whole batch on 1 invalid item)
- Filter `occurrence_count==0` (no hallucinations outside dataset)
- Dedup by (fragment, target_list_role) before INSERT (handles dup AI returns)

**Banked follow-ups:**
- Sonnet 4.6 A/B experiment (cost reduction from $0.99 → $0.05-0.10)
- Volume-floor tightening if production exceeds 50 fragments/100 pushed terms
- Retry-attempt drift watch (attempt 2 returned 97 fragments vs attempt 1)

---

## 2. Maximising Bookings on Current Spend deck (~2h, Sat 2 May)

7 slides. Saved as `End-of-week reports/DentalByDesign.co.uk - Maximising Bookings on Current Spend v1.pptx`.

**Slide structure:**
1. Cover with hero stats
2. 5.5x headline finding (0-15m → 28.2% book vs 12+h → 5.1%)
3. Week-by-week GAds with active agents + notes (16 weeks)
4. Outbound queue trend (Paid Search + Paid Social, 7 weeks)
5. Time-of-day factor (7 buckets — 8-18 wd books at 15-18%, dead zones at 5-7%)
6. Quick win = GAds schedule shift to Mon-Fri 8-6 (+25-40% on same spend)
7. Structural fix = SDR + Closer split with warm transfer

**Title decision:** rejected "Sales Response Speed Analysis" (sounded blame-y), locked "Maximising Bookings on Current Spend" — matches Tommaso's "more juice from current spend" framing.

**Dengro data correction (Sat 2 May):** Discovered the existing CSV `dengro-lead-export-2-2-26 to 8-2-26.csv` actually contains 5 weeks of data, not 1. Was causing 873-row over-count (4,172 vs deck's 3,299). Fixed by adding dedupe on `DenGro Unique ID` to load script. Re-loaded → matches the 400 Bookings deck exactly (3,297 leads, 332 booked).

---

## 3. Customer Match + GA4 audience push (~30min)

**Built CSV:** `customer_match_dbd_converted_bookings.csv` — 623 booked leads with email + phone + name + postcode (E.164 phone format).

**Upload BLOCKED:** GAds shows "Your account is currently not eligible to use Customer Match." — UK Health policy.

**GA4 audiences also blocked:**
- 3 older audiences (Nov 2020 / Sept 2025 vintage) showing "Closed — Not eligible due to sharing/privacy/policy"
- New `All visitors, last 540 days` (built 1 May) showing "Too small to serve"
- "Personalized advertising" link enabled in GA4 ↔ GAds, but audiences not pushing

**Test underway:** built distinctively-named audience `*Chris - Landing page + query string contains /` (13k users, 540d membership) in GA4. Wait 24-48h to see if it appears in GAds Audience Manager.

**Banked:** get Google rep contact from Giulio for Customer Match eligibility request. Likely declined for health vertical but worth trying.

---

## 4. PMax + DII campaign restructure (~30min, Sat)

**Diagnosed**: DII spend collapsed since splitting out `[All Implants] Near Me` campaign. New campaign Status: Eligible (Learning), spending only £40-115/day, 2 conv in 4 days at £114 CPA. DII budget £400 not being hit (spending £100-280/day).

**Recommendation accepted by Chris:**
- Pause `[All Implants] Near Me` campaign
- Copy 7 ad groups into DII (Catchall, Single Tooth, Full Mouth, Pay Monthly, Same Day, Dental Implant Clinic, Teeth Fixing)
- Remove 9 near-me phrase negs from DII
- Hold budget at £400 — only lift to £600 once spending close to £400

**Watch criteria for next 3-5 days:**
- DII trending toward £400/day spend
- Status reason returns to "Eligible (Limited) — limited by budget"
- CPA stable in £30-50 range

**Plan locked:** ad scheduling fix Phase 1 first (Mon 4 May earliest), SDR+Closer Phase 2 only after volume validation.

---

## 5. Catch-up ingestion (Sun 3 May, ~30min)

**Issue discovered:** Search Term Review blank for today (2026-05-03).

**Root cause:** Windows Task Scheduler task `ACT Overnight Run` is configured with `MSFT_TaskLogonTrigger` (runs 2 min after user logon), NOT a daily timer. If PC wakes from sleep without a fresh logon event, scheduler doesn't fire. Today's PC wake apparently didn't trigger it.

**Manual catch-up:** ran `.venv\Scripts\python.exe -m act_dashboard.scheduler.overnight_run`. Ingested 2026-05-02 data (296 Search + later 844 PMax via watcher).

**Banked fix:** add daily trigger at 7am + WakeToRun=True alongside existing logon trigger.

---

## 6. Pass 3 LIVE TEST FAILED (end of day, ~30min)

After Flask restart + reclassify (Pass 1+2 covered all 1,140 terms), clicked "Run Pass 3" on 2026-05-03 analysis_date.

**Result:** ZERO fragments + ZERO themes written to DB.
- `act_v2_phrase_suggestions WHERE client_id='dbd001' AND analysis_date='2026-05-03'` = 0 rows
- `act_v2_pass3_themes WHERE client_id='dbd001' AND analysis_date='2026-05-03'` = 0 rows
- No active Opus subprocess running
- No errors in dashboard.log (filtered to startup events only)
- act_v2_ai_errors empty for today

**Need to debug — Network tab evidence + console errors required from Chris's UI to know:**
- Did the request hit `/v2/api/search-terms/run-pass3-ai` (new) or `/v2/api/negatives/run-pass3` (old)?
- HTTP status code returned
- Response body
- Any browser console errors

---

## 7. April invoice sent

`DentalByDesign.co.uk -  April 2026 - Quote.pdf` sent to Tommaso. £3,000 / 100h covering 14-30 Apr. Bullet recap of April wins included in email.

---

## 8. Open / pending tomorrow (Mon 4 May)

### Immediate priorities
1. **Debug the Pass 3 button failure** — get UI Network tab + console evidence, route to build session if it's a code bug
2. **Watch DII recovery** — if spending close to £400/day, lift budget to £600
3. **Consider applying GAds ad scheduling Mon-Fri 8-6 to DII** if Day 1 of recovery looks good
4. **Live test Pass 3 on Mon morning data** once scheduler fires properly

### Banked decisions/asks for Tommaso/Giulio
- Implant-supported dentures (~12 negs)
- Implant brands DBD uses (Nobel confirmed; Straumann/Osstem/Megagen/MIS/Medentika/Neoss/Biohorizon/Hiossen/Neodent/Mini/Zygomatic/Pterygoid/Basal/Screwless TBC)
- DBD founding year (LP placeholder)
- Ceramic/zirconia implants offered?
- £995 vs £1,695 single implant pricing mismatch (live ad vs LP)
- **Get Google rep contact** for Customer Match eligibility request

### Banked tooling fixes
- Add daily 7am trigger + WakeToRun=True to Task Scheduler
- Sonnet A/B for Pass 3 (cost reduction)
- Volume-floor tightening on Pass 3 prompt if production exceeds 50/100
