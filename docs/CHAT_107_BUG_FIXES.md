# CHAT 107 BUG FIXES - AD GROUPS RULES & FLAGS

**Date:** 2026-03-21
**Priority:** HIGH
**Context:** Initial Ad Groups implementation complete, 3 bugs found during testing

---

## BUGS TO FIX

### BUG 1: Ad Groups rules showing on Campaigns page (CRITICAL)

**Problem:** 
- Campaigns Rules & Flags page shows ALL rules (campaigns + ad groups)
- Should only show rules with `entity_type='campaign'`

**Location:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\campaigns.py`

**Fix Required:**
Add `entity_type` filter to ALL rules queries in campaigns.py:

```python
# BEFORE (wrong):
SELECT * FROM rules WHERE is_template = FALSE

# AFTER (correct):
SELECT * FROM rules WHERE entity_type = 'campaign' AND is_template = FALSE
```

**Routes to fix:**
- GET `/campaigns/rules` - List rules
- GET `/campaigns/rules/<id>` - Get single rule
- Any other query that loads rules for display

**Verification:**
- Navigate to Campaigns → Rules & Flags
- Should see ONLY 19 campaign rules (13 Budget + 6 Bid)
- Should NOT see any ad group rules
- Navigate to Ad Groups → Rules & Flags
- Should see ONLY 12 ad group rules (8 Bid + 4 Status)

---

### BUG 2: Modal visible at bottom of page on load

**Problem:**
- When Ad Groups page loads, modal is visible at bottom of page
- Should be hidden by default

**Location:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\ag_rules_flow_builder.html`

**Fix Required:**
Add `style="display:none;"` to the overlay div:

```html
<!-- BEFORE (wrong): -->
<div id="ag-rules-flow-overlay">

<!-- AFTER (correct): -->
<div id="ag-rules-flow-overlay" style="display:none;">
```

**OR verify CSS is applied:**

Check `rules.css` has:
```css
#ag-rules-flow-overlay {
    display: none;  /* Hidden by default */
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    /* ... */
}

#ag-rules-flow-overlay.show {
    display: flex;  /* Visible when .show class added */
}
```

**Verification:**
- Navigate to Ad Groups → Rules & Flags
- Modal should NOT be visible
- Click "Add rule or flag" → Modal should appear as popup
- Click Close → Modal should disappear

---

### BUG 3: Modal appears at bottom of page instead of as popup

**Problem:**
- When clicking "Add rule or flag" or Edit button, modal appears at bottom of page
- Should appear centered as a popup overlay

**Location:** 
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\ag_rules_flow_builder.html`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\rules.css`

**Fix Required:**

**Check 1 - Overlay div ID:**
Verify the div has the correct ID:
```html
<div id="ag-rules-flow-overlay" class="rules-flow-overlay">
```

**Check 2 - CSS selector:**
Verify `rules.css` has this EXACT CSS:
```css
#ag-rules-flow-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(32, 33, 36, 0.45);
    z-index: 1050;
    display: none;
    align-items: center;
    justify-content: center;
    padding: 20px;
}

#ag-rules-flow-overlay.show {
    display: flex;
}
```

**Check 3 - JavaScript:**
Verify the JavaScript adds the `.show` class:
```javascript
function openAgRulesFlow() {
    document.getElementById('ag-rules-flow-overlay').classList.add('show');
}

function closeAgRulesFlow() {
    document.getElementById('ag-rules-flow-overlay').classList.remove('show');
}
```

**Possible causes:**
1. CSS selector doesn't match div ID
2. `position: fixed` missing or overridden
3. `.show` class not being added by JavaScript
4. CSS file not loaded or loading order issue

**Verification:**
- Click "Add rule or flag" button
- Modal should appear centered on screen as popup overlay
- Background should be dark (rgba overlay)
- Modal should be scrollable if content is tall
- Click Close or X → Modal should disappear

---

## TESTING CHECKLIST

After fixes:

**Campaigns page:**
- [ ] Rules tab shows ONLY campaign rules (19 total)
- [ ] Flags tab shows ONLY campaign flags (30 total)
- [ ] No ad group rules/flags visible

**Ad Groups page:**
- [ ] Rules tab shows ONLY ad group rules (12 total)
- [ ] Flags tab shows ONLY ad group flags (18 total)
- [ ] No campaign rules/flags visible
- [ ] Modal hidden on page load
- [ ] Click "Add rule or flag" → Modal appears centered as popup
- [ ] Modal overlay covers entire screen with dark background
- [ ] Click Close → Modal disappears
- [ ] Click Edit on any rule → Modal appears centered as popup

**Both pages:**
- [ ] Zero console errors in browser DevTools
- [ ] Zero Flask errors in terminal

---

## REFERENCE FILES

**For Bug 1 (Campaigns filtering):**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\campaigns.py`

**For Bug 2 & 3 (Modal CSS/HTML):**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\ag_rules_flow_builder.html`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\rules.css`
- Reference working example: `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\rules_flow_builder.html` (Campaigns modal)

---

## DELIVERABLES

1. Fixed `campaigns.py` with `entity_type` filters
2. Fixed `ag_rules_flow_builder.html` with correct modal CSS/HTML
3. Verification report confirming all 3 bugs resolved

---

**Document Version:** 1.0
**Last Updated:** 2026-03-21
