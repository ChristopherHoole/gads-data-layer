# Session Summary — Friday 24 April 2026

**Duration:** ~8 hours
**Client focus:** Dental by Design (DBD)
**Headline outcomes:** 10 new ad-group-matched landing pages shipped to production, full search-term triage, meaningful infrastructure fixes.

---

## 1. Ten new landing pages live

All deployed to `https://dentalbydesign.co.uk/google/` under a new URL structure (previously `/promo/google/`) so Chris can visually scan GAds Final URL column to distinguish new LPs from legacy.

| # | Ad group | URL |
|---|---|---|
| 1 | \*All on 4 Implants | https://dentalbydesign.co.uk/google/all-on-4-implants |
| 2 | \*All on 6 Implants | https://dentalbydesign.co.uk/google/all-on-6-implants |
| 3 | \*Best Dental Implants | https://dentalbydesign.co.uk/google/best-dental-implants |
| 4 | \*Dental Implant Specialist | https://dentalbydesign.co.uk/google/dental-implant-specialist |
| 5 | \*Dental Implants Cheapest UK | https://dentalbydesign.co.uk/google/dental-implants-cheapest-uk |
| 6 | \*Dental Implants Cost UK | https://dentalbydesign.co.uk/google/dental-implants-cost-uk |
| 7 | \*Dental Implants Finance | https://dentalbydesign.co.uk/google/dental-implants-finance |
| 8 | \*Dental Implants Hammersmith | https://dentalbydesign.co.uk/google/dental-implants-hammersmith |
| 9 | \*Dental Implants London | https://dentalbydesign.co.uk/google/dental-implants-london |
| 10 | \*Dental Implants Near Me | https://dentalbydesign.co.uk/google/dental-implants-near-me |

Each LP has 100% keyword coverage (every ad-group keyword appears ≥ 1× in visible body copy, post-deploy verified).

### Process established
1. Chris provides ad group name, keywords CSV, and current LP URL
2. Claude clones from LP #1 template and adapts copy
3. Draft shared via local ngrok tunnel with keyword coverage table
4. Chris reviews, flags changes
5. Claude does grammar/error/polish pass (fixes include spotting the wrong clinic address on Hammersmith LP)
6. `bun run build` locally to catch Cloudflare build errors pre-push
7. Push to `main` with standardised commit message `Add LP: [ad-group] → /google/[slug]`
8. Monitor waits for Cloudflare deploy (~3–5 min)
9. Post-deploy keyword coverage check against live URL
10. Chris copies ads in GAds with new Final URL
11. Full switch — old ads paused, new ads live (Option D: "full switch + extra caution")

Average time per LP: ~35 min end-to-end.

### Giulio's approval flow
- LP #1 previewed via ngrok Friday morning
- Giulio approved push-to-main for all LPs via WhatsApp
- Chris declined the suggested WhatsApp work channel — preference for email audit trail
- All commits direct to `main` with Cloudflare Pages auto-deploy

---

## 2. Search Terms triage (DBD)

Full flow completed for today's date (analysis_date = 2026-04-23, picker showed 24/4).

| Flow | Terms | Actions |
|---|---|---|
| Search > Block | 7 | Approve 5, Reject 2 |
| Search > Review | 24 | Approve 11, Reject 13 |
| PMax > Block | 68 | Approve 68 (all correct blocks) |
| PMax > Block > leak-exact | 18 | Approve 18 (residual pre-block serving — gone going forward) |
| PMax > Review (batch 1) | 50 | Approve 40, Reject 10 |
| PMax > Review (batch 2) | 50 | Approve 42, Reject 8 |
| Pass 3 phrase suggestions | 6 | Approve 5, Reject 1 ("k2" too ambiguous) |

**Total pushed to GAds today:** ~185 new negatives across Search and PMax.

Chris deliberately capped PMax Review at 100/day (of 303 pending) — stated concern: "pushing hundreds of negatives per day will shock the system".

### Key recurring themes in today's triage
- **Finance-intent queries** keep surfacing under Dental Implants Intent — flagged for possible dedicated Finance ad group + LP (which we then built as LP #7)
- **Location leaks** dominated Pass 3 suggestions (6/6 were geography outside service area)
- **Competitor brand terms** — large proportion of PMax noise
- **Crown/veneer/bridge tangential queries** captured correctly by `services_not_advertised` rule

### Configuration changes made
- Extended `neg_pass3_stopwords` with 13 new tokens: `clinic, care, practice, dentists, treatment, does, front, surgery, dr, gap, gum, private, work` — materially reduced Pass 3 noise
- Confirmed (from yesterday) `rule_7_exclude_tokens` now includes `implantologist, prosthodontist`

---

## 3. Infrastructure + bug fixes shipped

1. **PMax CSV pipeline working end-to-end** (continued from yesterday) — 582 terms ingested for 23/4 with real cost data via `python -m act_dashboard.data_pipeline.pmax_csv_ingest --client-id dbd001 --file "..."`. Handles both UTF-8/CSV and UTF-16/TSV formats.

2. **Google Ads Python library installed** — `pip install google-ads` resolved `No module named 'google.ads'` error blocking overnight scheduler for both DBD and OE.

3. **Flask rate limiter bumped** from 50/hour to 2000/hour — was blocking rapid-fire search term triage. Proper fix (IP exemption for localhost) flagged for Build 2.

4. **Cloudflare sitemap filter updated** — added `/google/` to the exclusion list in `apps/web/astro.config.ts` so new paid LPs don't leak into the sitemap.

5. **Overnight scheduler run manually** — first production run of F1 scheduler on Chris's Windows machine (Task Scheduler wiring still pending). Ingested 23/4 data for both DBD and OE. Engine ran for both. One lingering bug surfaced — CHECK constraint error on `act_v2_scheduler_runs.phase` value at end of cycle (non-critical, data lands correctly).

6. **Dev-env quirks documented:**
   - Cloudflare `imageService: "compile"` fails on SVG in dev mode → logo doesn't render on local `bun run dev` but works in production build. Not fixable from our side without changing Giulio's astro.config.
   - Vite dep cache occasionally goes stale (Wistia player bundle missing) → breaks videos. Fix = stop dev server, delete `apps/web/node_modules/.vite`, restart.
   - Astro's dev server rejects requests from non-localhost hostnames → ngrok needs `--host-header=rewrite` flag.

---

## 4. Lessons learned (quality-of-work feedback loop)

Chris pushed back hard on early LP work. Lessons banked:
- **Do real work, don't claim it.** Early LP #1 had 4/27 keyword coverage when claimed done. Subsequent LPs verified with a script that counts each keyword in the rendered page before delivery.
- **Natural English beats keyword stuffing.** Parenthetical synonym dumps ("Also known as X, Y, or Z") read as SEO spam. Rewrote to flow naturally.
- **No plasters — only proper fixes.** When hit by a DuckDB constraint issue, chose to brief Build 2 for a real fix rather than a workaround.
- **Sanity-check claims with specifics.** On the Hammersmith LP I initially wrote "Hammersmith Broadway" — the actual address is 45 Beadon Road. Quick curl of live site caught it before push.
- **Build locally before pushing.** `bun run build` catches Cloudflare-build-breaking errors (e.g. relative-import paths) in 2 min vs waiting 5 min for Cloudflare to fail.
- **Verify HTTP 200 + content match, not content alone.** A Monitor that greps for content in a redirect chain can false-positive when a 307 returns an empty body. Use `-L` on curl or explicit redirect handler.

---

## 5. Open items going into weekend

### Monitoring (Chris)
- **Watch new ad group performance** over the weekend — revert trigger = CPA jumps >30% on 3-day rolling average for any ad group. 30 new ads live (10 × 3 per ad group).
- **Rebuild the old ads in each ad group** if CPA tanks — they're paused, not deleted.

### Flagged to Build 2 (ACT team)
- Scheduler pipeline truncation (skips neg_stale_cleanup / neg_pass1/2/3 phases)
- CHECK constraint error on `act_v2_scheduler_runs.phase` at cycle end
- Task Scheduler wiring for 6:30 AM daily overnight run
- Flask rate limiter IP exemption for localhost (proper fix)
- Auto-watch Downloads for new PMax CSV files
- Row-number drift UX in Pass 1/2 review UI

### Dental by Design — operational
- Week 2 report now reverted to Monday delivery (was Friday) to use full previous-week data
- Google Ads conversion action rename — 13 remaining actions still need explicit source/meaning
- Engage DBD sales team on Dengro treatment_amount population
- CallTrackingMetrics audit pending login

---

## 6. Monday's first task

Continue LP build flow: LP #11 through LP #25, in this order:
11. \*Front Tooth Implant
12. \*Full Arch Implants
13. \*Full Mouth Implants
14. \*Full Mouth Implants Cost
15. \*Full Set of Teeth
16. \*Implants vs Bridges
17. \*Implants vs Dentures
18. \*Missing Teeth Solutions
19. \*Molar Implant
20. \*Pay Monthly Dental Implants
21. \*Replace All Teeth
22. \*Same Day Teeth
23. \*Single Tooth Implant
24. \*Single Tooth Implant Cost
25. \*Teeth Reconstruction

At ~35 min per LP, realistic to finish in a second 8-hour session.

---

## 7. Commits shipped today (DBD repo `main`)

```
0a331d7  Add LP: *All on 4 Implants (initial, /promo/google/)
c55b4c1  LP #1 move to /google/ + sitemap filter
3f692bc  LP #1 fix import paths after move
42c113f  LP #2 *All on 6 Implants
f5301d4  LP #2 keyword fix (all on 6 teeth visible)
dc61c51  LP #3 *Best Dental Implants
b35ce5a  LP #4 *Dental Implant Specialist
4392f21  LP #5 *Dental Implants Cheapest UK
4e5add5  LP #6 *Dental Implants Cost UK
a53c69a  LP #6 keyword fix (how much are dental implants uk)
8571b35  LP #7 *Dental Implants Finance
93afc03  LP #8 *Dental Implants Hammersmith (correct address)
aede74e  LP #9 *Dental Implants London
de715dc  LP #10 *Dental Implants Near Me
```

14 commits. Every commit = one Cloudflare Pages build.

---

## Closing note

Tomorrow/over the weekend Chris will work on ACT. A full ACT backlog prepared in `ACT_BACKLOG_24-4-26.md` (separate file) covering short-term fixes → long-term projects.
