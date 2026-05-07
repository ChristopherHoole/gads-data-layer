# DBD Week Plan — 27 April – 1 May 2026

**Hours allocated:** 40h (subcontractor under DBD agreement signed 14 Apr 2026)
**OE this week:** 4h, handled in separate session.
**Plan variant:** Plan B (triage daily, big projects compress to 6h each).

Source for items: `SESSION_SUMMARY_24-4-26.md` + this morning's planning chat. No items added by guesswork.

---

## Daily breakdown

| Day | Time | Task | Source |
|---|---|---|---|
| **Mon 27 ✅ DONE** | 8h | LP #11–#25 build flow — all 15 LPs live at /google/. See `SESSION_SUMMARY_27-4-26.md` for commits + URLs. | Friday's session summary §6 — Monday's stated first task |
| **Tue 28 ✅ DONE** | ~10h | (1) Auth fix (`CLAUDE_CODE_OAUTH_TOKEN`), (2) Search Term Review wording polish shipped (`43aaf04` + `2e1157a`), (3) 400-Bookings Strategic Plan deck (15 slides) + Week 2 Report deck (9 slides) both built end-to-end, (4) emails sent to Tommaso + Giulio in prep for Wed call. Triage included (166 negs pushed). Conv action renames deferred to Wed/Thu (1h). See `SESSION_SUMMARY_28-4-26.md`. | actual |
| **Wed 29** | 2h | Daily search term triage | Chris |
|  | 6h | New "near me" campaign build — campaign + ad groups + ads + keywords + LPs | Chris |
| **Thu 30** | 2h | Daily search term triage | Chris |
|  | 6h | PMax overhaul | Chris |
| **Fri 1 May** | 2h | Daily search term triage | Chris |
|  | 6h | Buffer / finish overruns / wrap-up + week notes | — |

**Total:** 40h on the dot.

---

## Items confirmed dropped this week

- Dengro `treatment_amount` engagement with DBD sales team
- CallTrackingMetrics audit pending login

(Both reappear in next-week planning if still relevant.)

---

## Plan-A alternative (if scope shifts mid-week)

If Wed/Thu need to be true full-day projects, switch to Plan A:
- Mon: same
- Tue: same (Triage 2h · Report 2h · Renames 1h · 400-bookings 3h)
- Wed: Near-me **full 8h** (no triage)
- Thu: PMax **full 8h** (no triage)
- Fri: Triage catch-up 6h (Wed+Thu+Fri's accumulated) · wrap 2h

Trade-off: Friday becomes mostly triage. Plan B preferred.

---

## Open ACT items NOT in this week's plan

These run as side-effort during daily triage, not as scheduled blocks:
- Stage 11 (Pass 3 routing UI) live verification
- Stage 12 (end-to-end QA) — natural by-product of doing real triage with the AI tools

Both will surface bugs naturally during the 2h/day triage windows. Patch as needed.

---

## Friday's open items still relevant

From `SESSION_SUMMARY_24-4-26.md` §5:

**Monitoring (background, not scheduled):**
- Watch new ad group performance — revert trigger = CPA jumps >30% on 3-day rolling average
- Rebuild old ads if CPA tanks (paused, not deleted)

These don't take scheduled time but Chris keeps an eye on them.
