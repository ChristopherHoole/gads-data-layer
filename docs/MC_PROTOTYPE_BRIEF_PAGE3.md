# MC ACT Prototype — Page 3: Account Level
**Session:** MC ACT Prototype (continued)
**Date:** 2026-04-06
**Objective:** Build an interactive HTML prototype of the Account Level page. This page shows budget allocation across campaigns, campaign roles, performance scoring, and signal decomposition.

---

## IMPORTANT: FOLLOW EXISTING STANDARDS

Read `docs/ACT_PROTOTYPE_STANDARDS.md` before starting. All patterns from Pages 1-2 must be followed exactly.

---

## Context

Read the Account Level section in `docs/ACT_OPTIMIZATION_ARCHITECTURE_v54.html` — this is your source of truth for everything on this page.

Reuse the app shell from the previous pages (sidebar with Account Level highlighted, top bar, client switcher, dark/light toggle).

---

## Page Structure

### Page Header
- Page title: "Account Level"
- Subtitle: "Budget Allocation & Health"
- Level colour accent: blue (#3b82f6) — use as a top border or subtle indicator
- Client name and persona badge: "Objection Experts — Lead Gen (CPA)"
- Key metrics visible: Monthly Budget (£1,500), Target CPA (£25), Current CPA (£19.50)

---

## Section A: Account Health Summary

A row of cards showing the account's current state at a glance:

| Card | Content | Detail |
|------|---------|--------|
| Monthly Budget | £1,500 | Daily: £50 |
| Current CPA | £19.50 | Target: £25 (22% below — Outperforming) |
| Budget Used (MTD) | £823 / £1,500 | 55% — with a progress bar |
| Conversions (MTD) | 42 | Projected: 77 at current rate |

The "Current CPA" card should show the performance zone:
- Green indicator + "Outperforming" if CPA is significantly below target
- Neutral/blue if on target
- Red/amber if underperforming

---

## Section B: Campaign Roles & Budget Allocation

This is the core of the Account Level page — showing how budget is distributed across campaigns.

### Campaign Role Table

A table showing all campaigns with their assigned roles and budget allocation:

| Column | Content |
|--------|---------|
| Campaign Name | Campaign name (clickable — could link to Campaign Level page in future) |
| Role | Badge showing role: BD (Business Development), CP (Core Performance), RT (Retargeting), PR (Prospecting), TS (Testing). Use a colour-coded badge per role. |
| Daily Budget | Current daily budget (£) |
| Budget Share | Percentage of total budget allocated — shown as number + visual bar |
| Min/Max Band | The allowed min/max % for this role (from Client Config) |
| 7d CPA | Last 7 days CPA |
| 14d CPA | Last 14 days CPA |
| 30d CPA | Last 30 days CPA |
| Performance Score | Weighted blend score (7d 50% + 14d 30% + 30d 20%) — shown as a number with colour (green/amber/red) |
| Status | Outperforming / On Target / Underperforming badge |
| Cooldown | If in budget shift cooldown, show time remaining. If not, show "Ready" |

### Sample Data (Objection Experts)

Since Objection Experts only has 1 active campaign, create 4 campaigns for the prototype to show the full functionality:

| Campaign | Role | Daily Budget | Share | 7d CPA | 14d CPA | 30d CPA | Score | Status |
|----------|------|-------------|-------|--------|---------|---------|-------|--------|
| GLO Campaign — Core | CP | £30 | 60% | £18.50 | £19.50 | £22.00 | 82 | Outperforming |
| GLO Campaign — Retargeting | RT | £10 | 20% | £12.00 | £14.50 | £16.00 | 91 | Outperforming |
| Brand — Objection Experts | BD | £5 | 10% | £8.00 | £9.00 | £10.50 | 95 | Outperforming |
| Testing — New Keywords | TS | £5 | 10% | £35.00 | £32.00 | £28.00 | 38 | Underperforming |

---

## Section C: Budget Allocation Visualisation

A visual representation of how budget is distributed and how it should shift based on performance.

**Show a horizontal stacked bar** with each campaign as a segment, sized by budget share. Colour each segment by performance score (green for high, amber for mid, red for low).

Below the bar, show ACT's budget recommendation:
- "ACT recommends: Shift 5% from Testing — New Keywords (underperforming) to GLO Campaign — Core (outperforming)"
- Show the proposed new allocation vs current
- This should match the Morning Review approval items — this is where those budget shift recommendations originate

---

## Section D: Signal Decomposition

Show how ACT breaks down performance signals for each campaign.

**For Lead Gen (CPA) persona:**
- CPC signal (7-day window)
- CVR signal (14-day window)
- Combined signal: CPA = CPC / CVR

**Show as a table or card grid per campaign:**

| Campaign | CPC (7d) | CPC Trend | CVR (14d) | CVR Trend | CPA | CPA vs Target |
|----------|----------|-----------|-----------|-----------|-----|---------------|
| GLO — Core | £2.10 | ↓ 5% | 11.4% | ↑ 2% | £18.50 | 26% below |
| GLO — Retargeting | £1.80 | → flat | 15.0% | ↑ 8% | £12.00 | 52% below |
| Brand | £0.95 | → flat | 11.8% | → flat | £8.00 | 68% below |
| Testing | £3.50 | ↑ 12% | 10.0% | ↓ 6% | £35.00 | 40% above |

Trend arrows should be colour-coded:
- ↓ CPC = green (good — costs going down)
- ↑ CPC = red (bad — costs going up)
- ↑ CVR = green (good — conversion rate improving)
- ↓ CVR = red (bad — conversion rate declining)
- → flat = neutral/blue

---

## Section E: Performance Scoring Breakdown

Show how the weighted performance score is calculated for each campaign.

**For each campaign, show a breakdown card:**

```
GLO Campaign — Core: Score 82
├── 7-day:  CPA £18.50 (26% below target) — weight 50% → 50 pts
├── 14-day: CPA £19.50 (22% below target) — weight 30% → 27 pts
└── 30-day: CPA £22.00 (12% below target) — weight 20% → 5 pts
```

This can be a collapsible section — show the final score prominently, expand to see the breakdown.

---

## Section F: Budget Shift History

A small table showing recent budget shifts ACT has made:

| Date | Campaign | Change | Reason |
|------|----------|--------|--------|
| 5 Apr | GLO — Core | £28 → £30 (+7%) | Outperforming, score 82 |
| 3 Apr | Testing — New Keywords | £7 → £5 (-29%) | Underperforming, score 38 |
| 1 Apr | GLO — Retargeting | £9 → £10 (+11%) | Outperforming, score 91 |

Show the last 10 shifts. Collapsible by default.

---

## Section G: Guardrails Summary

Show the active guardrails for Account Level:

- Max overnight budget move: 10% of daily budget
- Budget shift cooldown: 72 hours per campaign
- Min/max allocation bands per role (from Client Config)
- Total daily budget must equal monthly budget / days in month

Show as a simple list or card with the current values. Link mentally to Client Config (but don't cross-reference — keep self-contained).

---

## Interactive Behaviours

1. **Campaign role table** — sortable by any column
2. **Performance score** — click to expand scoring breakdown
3. **Budget allocation bar** — hover shows exact values per segment
4. **Signal decomposition** — trend arrows with tooltips showing the % change
5. **Budget shift history** — collapsible, expanded on click
6. **Guardrails** — static display, links to Client Config for editing
7. **ACT recommendation** — Approve/Decline buttons (matching Morning Review pattern)

---

## Browser Verification

1. Serve via Claude Preview
2. Test table sorting
3. Test score breakdown expand/collapse
4. Test budget bar hover
5. Test recommendation Approve/Decline
6. Check dark mode
7. Save screenshots to `act_dashboard/prototypes/screenshots/`

---

## Deliverables

1. `act_dashboard/prototypes/account-level.html` — working interactive Account Level page
2. Updated `docs/ACT_PROTOTYPE_STANDARDS.md` with any new component patterns
3. Screenshots saved to folder

---

**END OF BRIEF**
