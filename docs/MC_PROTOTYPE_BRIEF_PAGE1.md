# MC ACT Prototype — Page 1: Morning Review Dashboard
**Session:** MC ACT Prototype
**Date:** 2026-04-05
**Objective:** Build an interactive HTML prototype of the new ACT optimization engine, starting with the Morning Review dashboard. One page at a time — learn, document standards, carry forward.

---

## IMPORTANT: THIS IS A PROTOTYPE SESSION

- Build standalone HTML/CSS/JS files — NOT integrated into the Flask app
- Use Bootstrap 5 (same as the real ACT app) so the prototype looks like the real thing
- Every interactive element should work (clicks, dropdowns, expand/collapse, tabs) using JavaScript — but with hardcoded sample data, no backend
- The prototype will later be evolved into real templates during build sessions
- Use Claude Preview to serve and test the prototype throughout

---

## CRITICAL: ONE PAGE AT A TIME

This brief covers Page 1 only (Morning Review dashboard). Do NOT build other pages. We will learn from this first page, document standards, then brief the next page separately.

---

## Setup Tasks (Do First)

### 1. Create Prototype Folder Structure
```
act_dashboard/prototypes/
  index.html          (Morning Review — Page 1)
  css/
    prototype.css     (custom styles on top of Bootstrap)
  js/
    prototype.js      (interactions, sample data)
  components/
    nav.html          (reusable nav partial — or inline in each page)
```

### 2. Establish the App Shell
Before building the Morning Review content, build the shell that all pages will share:

**Top Bar:**
- ACT logo/name on the left
- Client switcher dropdown on the right (e.g., "Objection Experts ▼" with dropdown showing other clients)
- Current date display
- User name/avatar placeholder

**Sidebar Navigation:**
- Morning Review (home icon)
- Account Level
- Campaign Level
- Ad Group Level
- Keyword Level
- Ad Level
- Shopping Level
- Client Configuration
- Divider
- Jobs (existing — just a nav link, no prototype needed)
- Outreach (existing — just a nav link, no prototype needed)
- Changes (existing — just a nav link, no prototype needed)

**Match the existing ACT design language:**
- Read the existing sidebar in `act_dashboard/templates/base_bootstrap.html` for reference
- Read `act_dashboard/static/css/` for existing colour palette, spacing, typography
- The prototype should feel like it belongs in the current app — not a different product

### 3. Create Standards Document
Create `docs/ACT_PROTOTYPE_STANDARDS.md` with initial decisions:
- Colour palette used
- Typography (font family, sizes for headers/body/labels)
- Spacing system (margins, padding)
- Component patterns (cards, tables, badges, buttons)
- Action category colours: Act (green), Monitor (blue), Investigate (amber), Alert (red)
- Slide-in panel specs (width, animation, overlay)

Update this document as you build and discover new patterns. This becomes the design system for all future pages.

---

## Page 1: Morning Review Dashboard

### Purpose
This is the page the user sees every morning. It answers: "What happened overnight? What needs my attention? What's ACT monitoring?"

The user should be able to review and approve everything in under 5 minutes for a small account, under 15 minutes for a large account.

### Layout Structure (Top to Bottom)

#### Section A: Status Header
A row of summary cards across the top showing overnight activity at a glance:

| Card | Content | Colour |
|------|---------|--------|
| Actions Executed | Count of auto-executed changes overnight | Green |
| Awaiting Approval | Count of items needing human review | Amber (or red if urgent) |
| Monitoring | Count of items in active monitoring/cooldown | Blue |
| Alerts | Count of guardrail breaches or anomalies | Red |

Each card is clickable — scrolls to or filters the relevant section below.

#### Section B: Awaiting Approval (Most Important)
This section demands attention first. These are loosening changes and flagged items that ACT identified but cannot auto-execute.

**For each item show:**
- Which level it came from (Account / Campaign / Keyword / etc.) — as a badge
- What the check found (plain English summary)
- What ACT recommends (the specific action)
- Action category badge (Investigate or Alert)
- Approve / Decline buttons
- "View Details" expand to see the full decision tree reasoning
- Bulk approve option for low-risk items

**Sample data to use:** Create 4-6 realistic approval items, e.g.:
- "Campaign 'GLO Campaign': Loosen tCPA target from £30 to £33 — CPA is 22% below target for 14 days" (Campaign Level, Investigate)
- "Keyword 'planning objection specialist': Add as phrase match keyword — discovered from search terms with 8 conversions at £18 CPA" (Keyword Level, Investigate)
- "Ad Group 'Planning Objections': Budget concentration alert — this ad group consumes 95% of campaign spend" (Ad Group Level, Alert)

#### Section C: Actions Executed Overnight
A log of everything ACT did automatically (tightening actions that don't need approval).

**For each item show:**
- Timestamp
- Level badge
- What was done (plain English)
- Before → After values
- Action category badge (Act)
- "Undo" button (in case something looks wrong)

**Sample data:** Create 5-8 realistic auto-executed items, e.g.:
- "Added [planning permission disputes] to negative keyword list '3 WORDS [exact]'" (Keyword Level, Act)
- "Reduced Sunday bid adjustment from +0% to -25%" (Campaign Level, Act)
- "Paused keyword 'neighbour planning permission' — 0 conversions, £77.90 spend, 14+ days" (Keyword Level, Act)

#### Section D: Currently Monitoring
Items that ACT is watching but hasn't acted on yet (in cooldown, or gathering more data).

**For each item show:**
- Level badge
- What's being monitored
- Time remaining (e.g., "3 days left in 7-day cooldown")
- Current status (Healthy / Trending Down / Trending Up)
- Progress bar or countdown visual
- Action category badge (Monitor)

**Sample data:** Create 3-5 monitoring items, e.g.:
- "Campaign 'GLO Campaign': Budget shift cooldown — increased from £45/day to £50/day. 48 hours remaining" (Account Level, Monitor)
- "Keyword 'challenge planning permission': Bid decreased 10% from £3.20 to £2.88. Monitoring for 72 hours" (Keyword Level, Monitor)

#### Section E: Recent Alerts (Last 7 Days)
A collapsible history of alerts that have already been addressed or dismissed.

**For each item show:**
- Date
- Level badge
- Alert description
- Resolution (Approved / Declined / Auto-resolved)
- Action category badge

### Interactive Behaviours

1. **Status header cards** — clicking filters the page to show only that category
2. **Approval items** — Approve/Decline buttons with a confirmation toast
3. **Bulk approve** — checkbox on each approval item, "Approve Selected" button
4. **Expand/collapse** — "View Details" on each item expands to show reasoning
5. **Sections collapsible** — each section (B, C, D, E) can collapse/expand
6. **Client switcher** — dropdown changes the client name in the header (just visual swap for prototype)

### Sample Client Data
Use Objection Experts as the sample client throughout:
- Client: Objection Experts
- Persona: Lead Gen CPA
- Target CPA: £25
- Monthly budget: £1,500
- Campaign: GLO Campaign (Search, Maximise Conversions)
- Ad Group: Planning Objections
- Keywords: planning objection, challenge planning permission, etc.

---

## Browser Verification

After building the page:
1. Serve via Claude Preview
2. Screenshot the full page
3. Test all interactive elements (clicks, dropdowns, expand/collapse, approve/decline)
4. Check mobile responsiveness
5. Compare visual feel against existing ACT pages — it should feel like the same app
6. Update the standards document with all patterns established

---

## Deliverables

1. `act_dashboard/prototypes/index.html` — working interactive Morning Review page
2. `docs/ACT_PROTOTYPE_STANDARDS.md` — design standards documented from this first page
3. Screenshots of the finished page for review

---

**END OF BRIEF**
