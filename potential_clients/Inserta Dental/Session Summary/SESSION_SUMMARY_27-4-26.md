# Session Summary — Monday 27 April 2026

**Client:** Dental by Design (DBD)
**Hours:** 8h DBD (subcontractor agreement signed 14 Apr 2026)
**Headline outcome:** All 15 remaining ad-group-matched landing pages (LP #11–#25) shipped live to production at https://dentalbydesign.co.uk/google/. The DBD LP build flow that started Friday 24 Apr is now complete — 25 ad-group-matched LPs total.

---

## 1. Fifteen new landing pages live

All deployed to `https://dentalbydesign.co.uk/google/` with auto-build on Cloudflare Pages. Each commit = one Cloudflare deploy (~2-3 min from push to HTTP 200).

| # | Ad group | URL | Commit |
|---|---|---|---|
| 11 | \*Front Tooth Implant | /google/front-tooth-implant | `ef071cf` |
| 12 | \*Full Arch Implants | /google/full-arch-implants | `7ce388e` |
| 13 | \*Full Mouth Implants | /google/full-mouth-implants | `b0094b9` |
| 14 | \*Full Mouth Implants Cost | /google/full-mouth-implants-cost | `c4a8095` |
| 15 | \*Full Set of Teeth | /google/full-set-of-teeth | `4002582` |
| 16 | \*Implants vs Bridges | /google/implants-vs-bridges | `1f32ebe` |
| 17 | \*Implants vs Dentures | /google/implants-vs-dentures | `6d19396` |
| 18 | \*Missing Teeth Solutions | /google/missing-teeth-solutions | `89f41f6` |
| 19 | \*Molar Implant | /google/molar-implant | `f72dc9e` |
| 20 | \*Pay Monthly Dental Implants | /google/pay-monthly-dental-implants | `0474d5d` |
| 21 | \*Replace All Teeth | /google/replace-all-teeth | `f2f770a` |
| 22 | \*Same Day Teeth | /google/same-day-teeth | `ed96d4f` |
| 23 | \*Single Tooth Implant | /google/single-tooth-implant | `74be8a3` |
| 24 | \*Single Tooth Implant Cost | /google/single-tooth-implant-cost | `5abe2f9` |
| 25 | \*Teeth Reconstruction | /google/teeth-reconstruction | `eadb78d` |

Every LP shipped with **100% keyword coverage on live HTML** — verified post-deploy by counting each ad-group keyword's occurrence in the live rendered page.

---

## 2. Process refinements made today

The protocol from Friday's summary §1 ran cleanly with three small additions Chris flagged:

1. **Pre-review must show the keyword coverage table.** From LP #12 onward, every pre-review post includes a per-keyword count + status table so Chris can see coverage gaps before approving the ngrok preview.
2. **Pre-review must show both URLs (preview + future live).** Both ngrok and live URLs listed at the table stage so Chris doesn't have to ask.
3. **Don't auto-fix-then-push.** When the smoke check finds a missing keyword (happened on LPs #16, #22), fix it and present the updated table — wait for "ngrok looks good" before running build/commit/push. The build session jumped this step on LP #22 once; flagged and corrected for the rest.

---

## 3. Hero-line conventions locked in

- **Two-line hero title** matching LP #1's rhythm. Line 1 anchors the topic + location; line 2 is a short value statement.
- **No specific prices in the hero** (Chris confirmed on LP #14 — "Full Mouth Implants Cost"). Numbers belong in the PriceChart section further down. Hero leans on "transparent pricing" / "up to 60% less" framing instead.
- **Consumer-facing intent words win the hero.** LP #17 "Tired of Dentures? Switch to Permanent Dental Implants" landed harder than the neutral "Implants vs Dentures" framing because the keyword set signalled emotional intent.

---

## 4. Per-LP topic-angle decisions

Each LP needed a distinct angle to avoid duplicate-content collisions across the 25 ad-group set:

- **#11 Front Tooth Implant** — anterior cosmetic precision (visible smile zone, shade match)
- **#12 Full Arch Implants** — single-arch / double-arch / upper-jaw / lower-jaw variants on the £6,995 / £10,995 anchor
- **#13 Full Mouth Implants** — full-mouth + complete-mouth + reconstruction terminology
- **#14 Full Mouth Implants Cost** — cost-only page (transparent pricing, all-on-4 / full-arch / full-set cost variants)
- **#15 Full Set of Teeth** — consumer "full set / new set / complete set / permanent teeth" framing of the same procedure
- **#16 Implants vs Bridges** — educational comparison; positions implants as the better choice (bone preservation, no grinding adjacent teeth)
- **#17 Implants vs Dentures** — emotional intent ("tired of dentures", "hate dentures") leaning into the switch-to-implants angle
- **#18 Missing Teeth Solutions** — research-stage; outlines all three options (implants, bridges, dentures), recommends implants
- **#19 Molar Implant** — back-tooth functional angle (bite force, durability, position-specific planning)
- **#20 Pay Monthly Dental Implants** — 0% finance / monthly payments / spread the cost
- **#21 Replace All Teeth** — action-oriented "I want new teeth" framing
- **#22 Same Day Teeth** — speed-of-treatment focus (immediate / one day / 48 hours)
- **#23 Single Tooth Implant** — generic single-tooth (any position), Hammersmith-specific keyword landing
- **#24 Single Tooth Implant Cost** — single-tooth cost variants (per tooth, individual, front vs molar)
- **#25 Teeth Reconstruction** — clinical-language angle (reconstruction / restoration / rehabilitation / rebuild)

---

## 5. Standard pipeline per LP (post-template)

For each LP today the build session ran:

1. Parse keywords CSV → unique normalised list
2. Cluster keywords into FAQ groups (5-7 FAQs per LP)
3. Write Astro file (cloned from LP #1 structure, ~265 lines)
4. **Pre-review**: keyword coverage table + ngrok URL + live URL → wait for "ngrok looks good"
5. Auto-fix any 0-count keywords that the first draft missed (happened twice — LP #16, LP #22)
6. Grammar pass (UK spelling sweep — `aging` → `ageing`, etc.)
7. `bun run build` locally (~150s; catches Cloudflare-build-breaking errors before push)
8. `git add` + `git commit` with `Add LP: *<ad-group> → /google/<slug>` message
9. `git pull --rebase` + `git push`
10. Poll Cloudflare deploy until HTTP 200 (~2-3 min)
11. Live keyword coverage check on the deployed HTML
12. Confirm 100% live coverage to Chris

Average end-to-end time per LP: ~30 minutes.

---

## 6. Open items

### For Chris (on his side)
- Copy the existing ads in each ad group, swap the Final URL to the new one
- Full switch (old ads paused, new ads live) per the Friday Option D protocol
- Watch new ad group performance over the next 3 days — revert trigger = CPA jumps >30% on 3-day rolling average for any ad group

### Not started today
Nothing slipped — the entire 8h block went on LP build. Per `WEEK_PLAN_27-4-26.md`, the rest of the week's items are scheduled Tue–Fri:
- Tuesday AM: triage + Week 2 report + conv action renames + 400-bookings strategic plan
- Wednesday: near-me campaign build (6h after triage)
- Thursday: PMax overhaul (6h after triage)
- Friday: triage + buffer/wrap

---

## 7. Process learnings (banked for tomorrow)

- **The build session must wait for "ngrok looks good"** before running checks/push. This was flagged once on LP #22 and corrected for the rest of the day.
- **Keyword coverage tables and URLs are required at the pre-review stage.** No exceptions.
- **First-draft keyword coverage misses ~6% of the time.** Two of fifteen LPs had a single keyword missing on first pass. Always re-check after writing.
- **Build time stays consistent at ~150s.** Reliable enough that a per-LP slot is ~30 min, including review iterations.
- **Cloudflare deploys reliably in 2-3 min.** Polling at 30s intervals catches it on try 4-7.

---

## 8. Tier 2.1 / ACT — no work today

Stages 0-10 + 1.6.1 already shipped (see `docs/TIER_2.1_BUILD_PLAN.md`). Stages 11 + 12 still pending — both will be exercised naturally during tomorrow's daily search-term triage in ACT.

---

## 9. Closing note

Monday's stated first task from Friday's summary §6 is complete. Tomorrow opens with daily triage in ACT (the first real-world test of the AI tools shipped over the weekend) plus Week 2 report and 400-bookings strategic plan.
