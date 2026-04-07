# MC ACT Prototype — Page 2: Client Configuration
**Session:** MC ACT Prototype (continued)
**Date:** 2026-04-06
**Objective:** Build an interactive HTML prototype of the Client Configuration page. This page contains all 40+ configurable settings that control how ACT optimises each client's account.

---

## IMPORTANT: FOLLOW EXISTING STANDARDS

Read `docs/ACT_PROTOTYPE_STANDARDS.md` before starting. All patterns, colours, font sizes, spacing, and component styles established in Page 1 (Morning Review) must be followed exactly. No new colours, no new font sizes, no all-caps.

---

## Context

Read the Client Configuration tab in `docs/ACT_OPTIMIZATION_ARCHITECTURE_v54.html` to understand every setting, its default value, its options, and which level it belongs to. This is your source of truth for what goes on this page.

Also read the existing Morning Review prototype (`index-v7.html`) to match the app shell, sidebar, top bar, and client switcher exactly.

---

## Page Structure

### App Shell
Same as Page 1 — same sidebar (with Client Config highlighted as active), same top bar with client switcher, same dark/light toggle. Reuse the shell from v7.

### Page Header
- Page title: "Client Configuration"
- Subtitle: "Settings for [Client Name]" (pulled from client switcher)
- A "Save Changes" button (top right, primary green) and "Reset to Defaults" button (secondary, outline)
- Show last saved timestamp: "Last saved: 6 Apr 2026, 09:15 AM"

### Navigation Within the Page
The page has 7 sections with 40+ settings. This is a lot of content. Use **vertical tabs on the left side of the content area** (not the sidebar — a secondary nav within the page content) to switch between sections:

1. Account Settings
2. Campaign Settings
3. Keyword Settings
4. Ad Group Settings
5. Ad Settings
6. Shopping Settings
7. Onboarding Checklist

Each tab shows only that section's settings. The tab labels should use the v54 level colours as left-border accents (Account = blue #3b82f6, Campaign = green #10b981, etc.).

---

## Section 1: Account Settings (8 settings)

From v54, these include:
- Client persona (Lead Gen CPA / Ecommerce ROAS) — dropdown
- Target CPA or Target ROAS — number input (depends on persona)
- Monthly budget — currency input
- Budget allocation mode (automatic / manual) — toggle
- Budget shift cooldown — number input (hours, default 72)
- Max overnight budget move — percentage input (default 10%)
- Performance scoring weights (7d/14d/30d) — three number inputs that must sum to 100%
- Signal detection windows (CPC/CVR/AOV days) — number inputs

**For each setting show:**
- Setting name (14px, bold)
- Description explaining what it does (14px, regular)
- The input control (dropdown, number, toggle, etc.)
- Default value shown as placeholder or helper text
- Current value (use Objection Experts sample data: Lead Gen CPA, target CPA £25, budget £1,500/month)

---

## Section 2: Campaign Settings (13 settings + modifier caps table)

From v54, these include:
- Device modifier caps (min/max for mobile, desktop, tablet) — table with number inputs
- Geo modifier caps (min/max) — number inputs
- Ad schedule modifier caps (min/max) — number inputs
- tCPA adjustment cooldown — number input (days, default 14)
- tROAS adjustment cooldown — number input (days, default 14)
- Max CPC cap cooldown — number input (days, default 7)
- Device bid cooldown — number input (days, default 7)
- Geo bid cooldown — number input (days, default 30)
- Schedule bid cooldown — number input (days, default 30)
- Max single tCPA move — percentage input
- Max single tROAS move — percentage input
- Match type migration enabled — toggle
- Search Partners opt-out check — toggle

**Modifier caps table:** Show as a proper table with columns: Modifier Type, Min Cap, Max Cap, Cooldown. Rows: Device, Geo, Ad Schedule. Editable inline.

---

## Section 3: Keyword Settings (6 settings)

From v54:
- Keyword bid adjustment per cycle — percentage input (default 10%)
- Keyword bid cooldown — number input (hours, default 72)
- Keyword bid 7-day cap — percentage input (default 30%)
- Auto-pause spend threshold — currency input (default 1x target CPA)
- Auto-pause days threshold — number input (default 14)
- Quality Score alert threshold — number input (default 4)

---

## Section 4: Ad Group Settings (4 settings)

From v54:
- Negative outlier spend threshold — percentage input (default 30%)
- Negative outlier performance threshold — percentage input (default 50%)
- Positive outlier performance threshold — percentage input (default 40%)
- Pause recommendation inactive days — number input (default 30)

---

## Section 5: Ad Settings (6 settings)

From v54:
- Ad scan frequency — dropdown (daily/weekly, default weekly)
- Ad strength minimum — dropdown (Poor/Average/Good/Excellent, default Good)
- RSA asset low-rated days threshold — number input (default 30)
- Minimum ads per ad group — number input (default 3)
- Ad performance comparison threshold — percentage input (default 30%)
- Ad minimum days live — number input (default 14)

---

## Section 6: Shopping Settings (4 settings)

From v54:
- Product spend threshold — currency input (default £50)
- Product bid adjustment per cycle — percentage input (default 10%)
- Product bid cooldown — number input (hours, default 72)
- Product bid 7-day cap — percentage input (default 30%)

---

## Section 7: Onboarding Checklist

This is different from the other sections — it's a setup checklist for new clients, not ongoing settings.

**Show as a checklist with status indicators:**
1. Client persona selected — ✅ or ❌
2. Target CPA/ROAS set — ✅ or ❌
3. Monthly budget set — ✅ or ❌
4. Campaign roles assigned (BD, CP, RT, PR, TS) — ✅ or ❌ with list of campaigns and their assigned roles
5. 9 negative keyword lists created — ✅ or ❌ with list showing all 9 lists and their status:
   - 1 Word "phrase"
   - 1 Word [exact]
   - 2 Words "phrase"
   - 2 Words [exact]
   - 3 Words "phrase"
   - 3 Words [exact]
   - 4 Words "phrase"
   - 4 Words [exact]
   - 5+ Words [exact]
6. Default settings applied — ✅ or ❌
7. Google Ads API connected — ✅ or ❌

**Include a "Run Onboarding" button** that would (in the real build) auto-create the 9 negative keyword lists and apply default settings.

For the prototype, use Objection Experts sample data showing most items checked off.

---

## Interactive Behaviours

1. **Vertical section tabs** — clicking switches the visible section
2. **All inputs editable** — dropdowns, number inputs, toggles all functional
3. **Save Changes button** — shows a success toast "Settings saved"
4. **Reset to Defaults** — shows a confirmation dialog, then resets all values to defaults
5. **Persona switcher** — changing from Lead Gen to Ecommerce should swap "Target CPA" to "Target ROAS" (and vice versa)
6. **Performance scoring weights** — show a validation message if the three weights don't sum to 100%
7. **Onboarding checklist items** — clickable to expand details
8. **Run Onboarding button** — shows a toast "Onboarding complete — 9 negative keyword lists created"

---

## Sample Data

Use Objection Experts throughout:
- Persona: Lead Gen CPA
- Target CPA: £25
- Monthly budget: £1,500
- Budget allocation: Automatic
- Most settings at defaults
- Onboarding: all items checked except "Campaign roles assigned" (show as pending)

---

## Browser Verification

1. Serve via Claude Preview
2. Test all 7 section tabs switch correctly
3. Test form inputs are editable
4. Test Save/Reset buttons
5. Test persona switcher changes Target CPA ↔ Target ROAS
6. Test weight validation
7. Check dark mode
8. Screenshot the page for review

---

## Deliverables

1. `act_dashboard/prototypes/client-config.html` — working interactive Client Configuration page
2. Updated `docs/ACT_PROTOTYPE_STANDARDS.md` with any new component patterns (form inputs, tabs, settings layout, checklist)
3. Screenshots saved to `act_dashboard/prototypes/screenshots/`

---

**END OF BRIEF**
