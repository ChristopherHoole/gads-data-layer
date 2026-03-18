# CHAT 97: Fix Recommendations Table Column Widths

**Date:** 2026-03-17
**Priority:** HIGH
**Dependencies:** None

---

## CONTEXT

The recommendations table on both the Campaigns page (recommendations tab) and the full Recommendations page has no column width constraints. The checkbox column stretches to fill available space. The Rules & Flags table (`rules_flags_tab.html`) already has working column widths using a simple inline style approach — copy that exact approach.

---

## OBJECTIVE

Make the recommendations table columns work exactly like the Rules & Flags table columns — using inline `style="width:Xpx"` on `<th>` elements and matching CSS classes for min/max widths on other columns.

---

## HOW THE RULES TABLE WORKS (copy this approach)

In `rules_flags_tab.html`:
- `<th style="width:50px;">` on the first column `<th>`
- No width on `<td>` cells in JS row builder
- CSS classes like `.rules-plain-english { min-width:280px; max-width:460px; }` for other columns

---

## DELIVERABLES

### 1. Read these files first (do not edit yet):
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\rules_flags_tab.html`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\campaigns.html`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\recommendations.html`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\recommendations.css`

### 2. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\campaigns.html` — MODIFY
- Find all `<th>` elements in the recommendations tab tables (id: cam-pending-table, cam-monitoring-table, cam-successful-table, cam-history-table)
- Add `style="width:Xpx"` inline to each `<th>` using these widths:
  - Col 1 checkbox: 50px
  - Col 2 Campaign name: 160px
  - Col 3 Rule name: 160px
  - Col 4 Plain English: 220px
  - Col 5 Rule/Flag: 80px
  - Col 6 Rule type: 80px
  - Col 7 Conditions: 180px
  - Col 8 Action: 180px
  - Col 9 Risk: 70px
  - Col 10 Age: 60px
  - Col 11 Actions: 130px
- Remove ALL existing inline width styles from these `<th>` elements (width:36px, width:1px etc)
- Remove ALL inline width styles from `<td>` elements in the JS row builder for these tables
- Remove ALL width-related class attributes from `<td>` elements (`rec-col-cb` etc can stay for non-width purposes)

### 3. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\recommendations.html` — MODIFY
- Find all `<th>` elements in the 4 tables (rec-pending-table, rec-monitoring-table, rec-successful-table, rec-history-table)
- Add `style="width:Xpx"` inline to each `<th>` using these widths:
  - Col 1 checkbox: 50px
  - Col 2 Type: 90px
  - Col 3 Name: 140px
  - Col 4 Campaign/s name: 140px
  - Col 5 Rule name: 160px
  - Col 6 Plain English: 220px
  - Col 7 Rule/Flag: 80px
  - Col 8 Rule type: 80px
  - Col 9 Conditions: 180px
  - Col 10 Action: 180px
  - Col 11 Risk: 70px
  - Col 12 Age: 60px
  - Col 13 Actions: 130px
- Remove ALL existing inline width styles from these `<th>` elements
- Remove ALL inline width styles from `<td>` elements in the JS row builder

### 4. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\recommendations.css` — MODIFY
- Remove ALL `!important` from width/min-width/max-width rules on `.rec-col-cb`
- Remove ALL nth-child width rules that were added (lines 400+ — the big block added in Master Chat 12)
- Keep all other rules untouched

---

## REQUIREMENTS

- Do NOT touch any Python files
- Do NOT touch table-styles.css, custom.css, rules.css
- Do NOT add colgroup elements
- Do NOT add table-layout:fixed
- Keep it simple — inline style on th, matching CSS class min/max on columns
- After editing, verify by reading back the changed sections

---

## SUCCESS CRITERIA

- [ ] Every `<th>` in all 8 recommendation tables has an explicit `style="width:Xpx"`
- [ ] No `<td>` in JS row builders has inline width styles
- [ ] No `!important` on width rules in recommendations.css for rec-col-cb
- [ ] Flask starts cleanly
- [ ] Report back exact th elements changed

