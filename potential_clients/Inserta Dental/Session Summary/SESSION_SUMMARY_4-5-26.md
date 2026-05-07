# DBD Session Summary — Mon 4 May 2026

## Headline
Full DBD Google Ads rebuild kicked off. **21 new exact-match ad groups + 21 new landing pages shipped to dentalbydesign.co.uk in one day** across 5 of the 27 planned parents. New campaign architecture: single big "Dental Implants Intent" campaign, exact-match-heavy, sub-grouped by intent dimension.

## Strategy locked (with Giulio)
- Single big DII campaign — phase out fragmented old structure
- Exact-match-heavy — new ad groups all `[ex]` prefixed
- Focus on single arch / double arch + closely related high-ticket procedures
- Phase out old phrase/exact ad groups gradually as new exact ones warm up

## Search-term audit
- 175,241 search-term rows loaded into `audit.duckdb` (Jan 2025 – May 2026)
- 26 parent regexes defined → ~70 sub-group ad groups planned
- Sub-group dimensions locked: CORE / COST / LOCATION / FINANCE / COMPARISON / INFO / BRAND / NHS
- Plan + data saved at `Campaigns/_PLAN_subgroups.md` + `_PLAN_subgroup_data.csv`

## Build conventions locked
- **Naming:** `[ex] {Parent} - {SUBGROUP}` for ad groups
- **Filter rules:** ≥30 impr / ≥1 click / ≤6 words / sort clicks-desc then impr-desc / cap 25 per ad group / no force-fill
- **Self-blocking filter:** drop keywords containing tokens that defensive negs would block (denture, veneer, etc)
- **Tourism filter:** drop tourism countries (lithuania, latvia, estonia added to extras)
- **Cross-parent filter:** General Implants excludes keywords matching specific-parent regexes (caught contamination bug mid-day)
- **Junk filter:** drop competitor names, "free", "no cost", "grants", clinical trials, etc
- **Description char range:** 75-87 chars (validator hard-enforces)
- **Headline char range:** ≤30 chars, target 12-13 of 15 with parent keyword anchor for Quality Score
- **Banned phrases:** £25 booking deposit, 60% off, Top 10 Europe, Best Clinic 2024, 99.12% (allowed only in disclaimer)
- **CSVs:** UTF-8 with BOM (`utf-8-sig`) to avoid £/em-dash encoding breakage
- **Negatives:** deferred to buffer day (existing shared lists provide baseline)
- **Campaigns folder:** all 27 parents renumbered with sequence prefixes 01-27

## Build progress (5 of 27 parents)
| # | Parent | Ad groups | Keywords | RSAs | LPs |
|---|---|---|---|---|---|
| 01 | All on 4 | 4 (CORE/COST/LOCATION/INFO) | 47 | 12 | 4 (+1 vs all-on-6) |
| 02 | Full Mouth | 3 (CORE/COST/LOCATION) | 54 | 9 | 3 |
| 03 | General Implants | 6 (CORE/COST/LOCATION/FINANCE/INFO/NHS) | 146 | 18 | 6 |
| 04 | New Teeth | 4 (CORE/COST/LOCATION/NHS) | 76 | 12 | 4 |
| 05 | Screwless | 4 (CORE/COST/LOCATION/INFO) | 23 | 12 | 4 |
| | **TOTAL** | **21** | **346** | **63** | **21** |

## LP build process (locked)
- All LPs are Astro pages in `C:\Users\User\Desktop\dentalbydesign-repo\apps\web\src\pages\google\`
- Local dev: `bun dev` on port 4321
- Preview: ngrok tunnel `https://intervalvular-rainily-shawna.ngrok-free.dev`
- Push to `main` triggers Cloudflare auto-deploy in ~60-90s
- Each LP has hero, FAQ accordion, price chart, lifetime warranty, comparison, doctors, reviews, video CTA, quiz CTAs

## Generator scripts (reusable templates)
- `generate_general_implants_uploads.py` — most complete (cross-parent + junk + defer filters)
- `generate_new_teeth_uploads.py` — has cross-parent + junk filters
- `generate_screwless_implants_uploads.py` — junk filter only (no cross-parent contamination risk for screwless-specific terms)
- All produce: markdown specs + ad groups CSV + keywords CSV + RSAs CSV (UTF-8 BOM)
- All hard-validate char ranges, paths, banned phrases, dups, zero-keyword groups

## Bugs caught + fixed mid-build
- **Cross-parent regex contamination:** General Implants regex was hoovering keywords like `all on 4 dental implants` because `dental implants` matched. Fixed by adding `belongs_to_specific_parent()` exclusion check. Now applied to all subsequent parent generators.
- **NHS hero copy issue:** Original "Dental Implants on the NHS / What's Available" sounded like we offered NHS implants. Reworded to "NHS Won't Cover Dental Implants? / Private Implants from £1,695 — 0% Finance" across both NHS LPs (General Implants + New Teeth).
- **Folder structure:** All 27 Campaign parent folders renamed with sequence prefixes (01_All_on_4 through 27_NHS_Implants) for build sequence clarity.

## DII campaign audit (end of day)
- Pulled 30-day DII keyword report
- Mapped 14 old `*` ad groups that now have `[ex]` exact-match equivalents
- **Chris manually paused all duplicated exact-match keywords across the old `*` ad groups, kept all phrase matches running** — phrase catches the long-tail variants the new exact ad groups won't catch
- Old `*` ad groups still running for parents not yet built (Same Day Teeth, All on 6, Full Arch, Front Tooth Implant, Molar Implant, Implants vs Dentures, Implants vs Bridges, all "Near Me [...]" catch-alls)

## What's pending (Tommaso/Giulio approvals)
- Implant Denture (Day 5 build) — confirm whether to advertise (~12 negs would lift to start)
- Implant brands beyond Nobel (Straumann, Osstem, Dentsply, etc.) — Nobel confirmed
- Zygomatic / Pterygoid implants — confirm whether DBD offers
- DBD founding year (for "Since YYYY" claims)
- Ceramic / zirconia implants — confirm whether offered
- £995 vs £1,695 single implant pricing mismatch (live ad vs LP)

## Tomorrow / next session
- Continue parent builds: **06 Vivo Bridge** next (single sub-group), then 07 Permanent Teeth 48h
- Day 2-10 plan: New Teeth ✅ done. Vivo, Permanent Teeth 48h, Same Day Teeth, Smile in a Day, All on 6, Single Arch, Double Arch, Full Arch, Upper Jaw, Lower Jaw, Implants for Elderly, Hybrid Bridge, Implant Clinic, Bone Graft, Failed Implants, Nobel Biocare, Fixed Teeth, Comparison Shoppers
- Day 5 (pending Tommaso/Giulio approvals): Implant Denture, Zygomatic, Straumann, NHS Implants
- Final day = buffer day: comprehensive negative audit across all live ad groups, neg-list updates, ad scheduling Phase 1 (block 6pm-midnight + weekends per Maximising Bookings deck)

## Files of note
- Generators: `potential_clients/Inserta Dental/data/search_terms_audit_2026/generate_*_uploads.py`
- Specs + CSVs: `potential_clients/Inserta Dental/Campaigns/{01_All_on_4 ... 27_NHS_Implants}/`
- Audit DB: `potential_clients/Inserta Dental/data/search_terms_audit_2026/audit.duckdb`
- LP repo: `C:\Users\User\Desktop\dentalbydesign-repo\apps\web\src\pages\google\`
- Master URL plan: `Campaigns/_LP_URLS.md`
- Tourism negs: `Campaigns/_TOURISM_NEGS.md`

## Late-night addition: ACT Pass 3 AI debug + prompt hardening (post-midnight Mon→Tue)

After wrapping the GAds build at ~22:30, ran a full end-to-end Search Term triage in ACT to validate Pass 3 in production. Hit multiple bugs + iteratively hardened the prompt.

### Bugs fixed (commit `eda0296`)
1. **DuckDB BinderException** — `act_dashboard/engine/pass3_ai.py:431` was comparing `snapshot_date` (DATE) with `analysis_date` (VARCHAR), causing 500 on every Pass 3 click. Fix: `CAST(? AS DATE)`.
2. **409 lock contention** — first Pass 3 click was actually running (~30-90s for Haiku) but no UI feedback, so user clicked again and hit the per-client lock. Confused user.
3. **AI Role + AI Conf columns showing "—"** — endpoint at `act_dashboard/routes/v2_negatives_api.py:748` was reading `ai_target_list_role`/`ai_confidence` from `act_v2_ai_classifications` (old table), but new Pass 3 AI engine writes directly to `act_v2_phrase_suggestions` (n8 cols `confidence`/`rationale`). Fix: read direct columns + bucket DOUBLE confidence into high/medium/low pills.
4. **AI suggesting `_exact` target lists for phrase-match-only Pass 3** — `_load_target_lists` returned all linked lists. Fix: filter `WHERE list_role LIKE '%_phrase'` so AI only sees phrase-match options.

### UX fix: Run Pass 3 button now shows live state
- Click → button disabled, label `⏳ Pass 3 running… Ns` (live counter via setInterval)
- Toast on start: "Pass 3 AI started — this can take 30s to 5min"
- Toast on finish: success with timing/cost/fragment count, or error
- File: `act_dashboard/static/js/v2_search_term_review.js:1952`

### Prompt iteration (4 passes, file `act_dashboard/ai/prompts/search_terms_pass3_v2.txt`)
Iterated tonight to make Pass 3 output airtight:

| Pass | Issues found | Fixes |
|---|---|---|
| 1 | Rule 4 only covered UK locations; no rule for competitor brands; Rule 8 themes→fragments contract was soft | Added 4b (international), 4c (competitor brands), tightened Rule 8 |
| 2 | Rule 3 said "1-word" only (mismatch with 3a multi-word); Rule 4 header misleading; Rule 5 cap interaction with exempt unclear; risk-level guidance for 4b/4c missing | Rule 3 now 1-4 word; renamed Rule 4 header; added Rule 5 ORDERING WHEN AT CAP; risk = "low" for 4b + 4c |
| 3 | Nobel hard-listed in 4c (DBD uses Nobel); Rule 5 cap inconsistent with 4a; Rule 6b said "Yesterday's"; Rule 1 stopword logic ambiguous | Rule 4c CRITICAL OVERRIDE for `services_advertised`; clarified ordering; "recently pushed"; rewrote Rule 1 with 1a/1b split + 4 examples |
| 4 | Rule 4 header still listed 4a as exempt (wrong); CRITICAL OVERRIDE wording inconsistent w/ Rule 7; JOB section themes 1-4 vs output 0-4 | All consistency fixes |
| late | Themes hallucinating examples not in data — turned out to be in data, but were on suppression list (Rule 6) so couldn't be fragments. Rule 8 violated | Added "suppressed terms cannot be named in themes either" to Rule 8 |

### Pass 3 quality progression on DBD snapshot 2026-05-03 (1097 search terms)
- Initial run (broken AI table read): 14 fragments, all routed to wrong (`_exact`) lists
- After phrase-only filter: 9 fragments, all routed correctly to `_phrase` lists, but missed locations + competitors
- After Rules 4b + 4c + 5 cap exemption: 13 fragments — locations (barbados, lahore, morocco) + competitors (straumann, megagen, dio implant) all surfaced
- After Rule 8 + 9 tightening: 11 fragments — same quality, themes now grounded in real data

### Quality verdict end-of-night
✅ Engine now reliably produces:
- Off-not-adv: dentures, veneers, bridges, crowns, smile makeover, periodontist (when present)
- Locations: international cities/countries always surfaced
- Competitors: implant-brand competitors always surfaced
- All routed to correct phrase-match lists
- All AI metadata visible in UI

⚠️ Open issue: Haiku **still occasionally names suppressed terms in theme summary** even after Rule 8 update (e.g. names "Bangkok, Sri Lanka" in tourism theme but they're already on neg lists so no fragment). Soft constraint — Haiku not strictly enforcing. To investigate next session — possibly needs a hard-coded post-process check or a switch to Sonnet for theme generation.

### User actions tonight
- Pushed select phrase-match fragments to neg lists (locations + competitors first; held off on dentures/veneers/etc until validating not already covered)
- Reviewed full prompt 4 times collaboratively before approving each change

## Hours
~14h (extended into early hours of 5/5 for Pass 3 debug)
