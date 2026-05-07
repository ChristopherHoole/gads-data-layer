# Session Summary — Tuesday 28 April 2026

**Client:** Dental by Design (DBD)
**Hours:** ~10h DBD (subcontractor agreement)
**Headline outcomes:**
1. **166 search-term negatives pushed to DBD GAds** during the day's triage (full Search Block + Search Review + PMax Block + PMax Review flows) — single biggest single-day push since system went live
2. **400-Bookings Strategic Plan deck shipped** — 15 slides covering 16-week channel mix, CPA economics, lead-to-booking lag, scaling model, 6-month budget ramp, monthly deliverables, recommendations
3. **Week 2 Report shipped** — 9 slides covering CPA down 36% W-o-W, tracking fix story, campaign breakdown, work delivered, Week 3 plan
4. **ACT Search Terms UX polish** — terminology aligned across the module (Block in GAds / Don't Block / BLOCK / UNSURE pills), Push button renamed, validated end-to-end against today's real triage data

---

## 1. Day's actual flow (vs the planned schedule)

The week plan had today as: 2h triage + 2h Week 2 report + 1h conv action renames + 3h 400-bookings strategic plan.

Actual:
- AM ~30 min: search term triage attempted, hit `CLAUDE_CODE_OAUTH_TOKEN` auth issue → resolved via `claude setup-token` + Windows User env var
- AM ~2h: ACT Search Term Review terminology polish (button renames + AI Verdict pill rename + push button rename) shipped to `origin/main`
- AM ~30 min: real triage on PMax + Search flows, validated terminology fix worked end-to-end
- AM ~30 min: Pass 3 partial test — found gaps (only 1-word fragments generated, all defaulted to wrong target list) — logged for tomorrow's work
- PM ~5h: 400-bookings strategic plan deck (15 slides) — data analysis (channel mix, lag, gap math, scaling) + python-pptx build + iterative review
- Evening ~2h: Week 2 Report deck (9 slides) — built on top of v8 Week 1 template, full sweep + reformat
- Email drafted + sent to Tommaso + Giulio in prep for Wed 29 Apr call

The strategic deck took longer than planned (5h vs 3h scoped) because the data analysis surfaced more nuance than expected (Source breakdown within Paid Search, the 47-lead GCLID-gap reclamation discussion, channel-attribution rules locking).

---

## 2. ACT Search Terms — terminology polish shipped

Three commits during the morning:
- `43aaf04` — rename "Approve selected" → "Block in GAds", "Reject selected" → "Don't Block", status pills (Approved → Approved to Block, Pushed → Pushed to Neg Lists, Rejected → Didn't Block), hide Push error column via CSS display:none
- `2e1157a` — AI Verdict pills (`approve` / `reject` / `unsure` → `BLOCK` / `DON'T BLOCK` / `UNSURE` display labels via const map; CSS class hooks unchanged) + Push button rename ("Push approved to Google Ads" → "Push to GAds Neg Lists" / "Push N to GAds Neg Lists")
- (Local table-color fix on the strategic deck — not committed since it's a docs change)

Pause-gate brief pattern worked cleanly. Build 2 confirmed Pause 1 + Pause 2 each time, no rework needed.

Real-world validation: Search Block/Review flows + PMax Block/Review flows all triaged with new wording. End-of-day counters: 166 pushed to neg lists, 59 didn't block.

---

## 2.5 Daily search-term triage — 166 pushed to neg lists

End-of-day ACT counters:
- **Pushed to Neg Lists: 166**
- **Didn't Block: 59**
- **Approved to Block (in queue, not yet pushed): minor remainder**

Flows worked through (all using the new Block in GAds / Don't Block terminology):
1. **Search > Block** — first batch of 21 terms via AI Triage; agreed all, clicked Block in GAds, pushed live
2. **Search > Review** — 69 terms; AI Triage'd in batches of ~10, applied DON'T BLOCK on legitimate intent queries
3. **PMax > Block** — bulk of the day's volume after PMax CSV upload + reclassify (jumped to 380 PMax search terms after CSV ingest)
4. **PMax > Review** — handled in same pass

Validation outcomes:
- New wording (Block in GAds / Don't Block / BLOCK / UNSURE) read naturally during triage — no confusion vs the old Approve/Reject framing
- AI Triage button worked first-try after the CLAUDE_CODE_OAUTH_TOKEN auth fix
- "Apply high-conf" button delivered the expected one-click bulk action on high-confidence rows
- 95%+ same-day booking pattern (per yesterday's lag analysis) means today's pushes will start showing impact in tomorrow's data

This is the largest single-day push to DBD's neg lists since the automation went live (20 Apr). Cumulative ACT-driven negatives now well into the 5,000+ range across all DBD lists.

---

## 3. Auth fix — CLAUDE_CODE_OAUTH_TOKEN setup

When AI Triage was called, GAds-side auth was missing because:
- `claude` CLI subscription auth (interactive) was working
- But non-interactive `claude -p` mode (used by Flask subprocess) needs `CLAUDE_CODE_OAUTH_TOKEN`
- Token wasn't set in user env vars

Resolution: Chris ran `claude setup-token`, obtained long-lived 1-year OAuth token, set as Windows User env var. Flask restart picked it up. AI Triage worked first try after restart.

**Memory item locked**: ACT auth on a fresh server requires `CLAUDE_CODE_OAUTH_TOKEN` set as User env var, not just `claude` interactive subscription auth. Document this in onboarding.

---

## 4. Pass 3 partial test — gaps logged for tomorrow

Stage 11 wiring works (button fires, AI Route runs, data populates). But the underlying engine has 2 issues:
1. **Only 1-word fragments generated** — no 2/3-word phrases. Engine threshold/multi-word logic likely too strict.
2. **All fragments default to `1_word_phrase`** target list — they should auto-route to `Loc 1 word phrase` for location terms (bangor, cheltenham, oldham, etc.) per Stage 11 Pass 3 routing prompt.

Both confirm the **2.1e (intent-based Pass 3 routing engine fix)** backlog item is needed. Marked for Wed/Thu work.

---

## 5. 400-Bookings Strategic Plan deck (15 slides)

**Path:** `potential_clients/Inserta Dental/End-of-week reports/DentalByDesign.co.uk - 400 Bookings Strategic Plan v1.pptx`

**Slides:**
1. Cover — Path to 400 Bookings/Month
2. Executive Summary — 5,070 leads / 620 bookings / £237k spend / £383 blended CPB
3. Methodology & Data — sources, channel definitions, caveats
4. Channel Mix Overview — 7-channel master table
5. GAds Channel Performance — week-by-week + lag + insights
6. Print/Metro Channel Performance
7. Paid Social Channel Performance
8. Organic Search Channel Performance
9. Direct Channel Performance
10. Bing + Other (combined)
11. Lead-to-Booking Lag — cross-channel finding (95% same-day across paid)
12. The 400-Bookings Model — channel-by-channel scaling plan to close +245/mo gap
13. Recommended 6-Month Budget Split — month-by-month spend ramp
14. Channel Deliverables — month-by-month spend + leads + bookings per channel
15. Recommendations & Next Steps — 3-column (decisions / our team / cadence)

**Key narrative:** GAds is the workhorse (65% leads, 53% bookings). Post-tracking-fix DII Search converts at £50 CPA vs PMax £65 — sets up Search migration. Plan is **paid-ads-led** (GAds + Meta carry +178/mo of the +245 gap), Print/Metro modest 2× scaling, Direct/Organic brand-halo growth. Spend ramps from £60k/mo to £142k/mo over 6 months.

**Key data analysis files** (in `potential_clients/Inserta Dental/data/400 bookings per month/`):
- `_FINAL_channels.py` — canonical 7-channel rule script
- `_master_week_channel.csv` — clean weekly data
- `gads 5-1-26 to 26-4-26.csv` — GAds source data
- 16 weekly Dengro CSVs

---

## 6. Week 2 Report deck (9 slides)

**Path:** `potential_clients/Inserta Dental/End-of-week reports/DentalByDesign.co.uk - Week 2 Report 20-26 April 2026-v1.pptx`

**Slides:**
1. Cover — CPA down 36% headline, £46
2. Executive Summary — movement stats (-20% / +26% / +27% / -37%)
3. 8-Week Context — Week 2 at best CPA of 8-week window
4. Campaign Performance — Brand / DII / PMax W1 vs W2 with DII tracking-broken caveat
5. Dengro Performance — GAds funnel
6. Tracking Audit & The CPA Drop — what was broken / fixed / impact
7. Work Delivered — Mon-Fri 3-column (Automation / Tracking / Pages+Tracking shipped)
8. Week 3 Plan + Strategic Forward Look — daily plan + 400-bookings reference
9. What's Next — rolling priorities + Coming Next card

**Key headlines:** GAds CPA £82 → £46 (-36%) on 20% less spend. Bookings up 27%. Tracking fix on Fri 24 Apr was the catalyst.

---

## 7. Process learnings banked

- **Token economy:** python-pptx is verbose; iterating slide layouts costs heavily. The plan worked: structure content in markdown → python-pptx pass for boxes/colors → Chris hand-finalises layout in Impress. Avoided burning tokens on pixel-perfect placement.
- **Cloning slides** in python-pptx via `deepcopy` of element XML works but brings broken image references. Solution: detect + remove picture shapes from clones, then re-add logo from a known-good slide using `slide.shapes.add_picture(io.BytesIO(blob), ...)` with the embedded image blob.
- **`set_text_keep_format` patterns** lose run formatting when paragraph text is cleared via `.text = ''`. Right approach: capture rPr XML before removing runs, re-attach after.
- **Channel attribution rules** are easy to over-engineer. Best to lock simple rules ("if Channel=Paid Search and Source≠Bing → GAds") and stick to them throughout the analysis. Mixing definitions (GAds CSV Conversions vs Dengro Paid Search lead count) creates inconsistencies that have to be unwound.

---

## 8. Open items

### For Chris's side
- Wait for reply from Tommaso + Giulio on the two emails (400-bookings deck + Week 2 report)
- Wed 29 Apr call walks through both decks
- Outstanding data to chase: Meta Ads spend, Bing/Microsoft Ads spend, Sun/Metro tracking-link history

### For ACT (build queue)
- **2.1e** — AI-driven Pass 3 target-list assignment (Pass 3 engine intent-based routing) — confirmed needed today
- Stage 11 + 12 still partly pending — UI wired, Pass 3 engine output insufficient for full live test
- 1.1 scheduler pipeline truncation, 1.2 CHECK constraint, 1.3 rate limiter IP exemption — Tier 1 backlog quick wins

### Tomorrow (Wed 29 Apr) per WEEK_PLAN_27-4-26.md
- 2h daily search term triage (real Pass 3 test once today's blocks are pushed)
- 6h new "near me" campaign build — first of the structured Search campaigns the strategic deck commits to
- Possibly: strategic call with Giulio (depending on his reply to today's email)

---

## 9. Closing note

Productive day. Two complete decks shipped. Strategic case for paid-ads-led growth made with data. Tracking-fix story tells well. Search migration positioned as ACT's purpose-built advantage.

Wednesday 29 April starts the operational pivot: PMax → Search migration begins, first new Search campaign builds.
