# CHAT 107 FINAL BUG FIXES - AD GROUPS RULES & FLAGS

**Date:** 2026-03-21
**Priority:** MEDIUM
**Context:** 3 critical bugs fixed, 2 minor bugs remain

---

## BUGS TO FIX

### BUG 4: Toast appears at bottom of page instead of sliding in

**Problem:**
- On Ad Groups page, when saving/editing rules, toast notification appears at bottom of page
- On Campaigns page (and rest of app), toast slides in from top or corner
- Should use same toast system across all pages

**Location:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\ag_rules_flow_builder.html`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\ag_rules_flags_tab.html`

**Fix Required:**

**Check 1 - Toast function name:**
Verify JavaScript calls the correct toast function:
```javascript
// Should use existing global toast function (check campaigns.html for reference)
showToast('Rule saved successfully', 'success');
// NOT a custom local toast implementation
```

**Check 2 - Toast container:**
Verify the page uses the global toast container (likely in base_bootstrap.html):
```html
<!-- Should NOT have a duplicate toast container in ag_rules_flow_builder.html -->
<!-- Toast container should be in base template only -->
```

**Check 3 - Reference working implementation:**
Look at `campaigns.html` and `rules_flow_builder.html` to see how toast is called:
- Find the `showToast()` function calls
- Copy the exact same pattern for ad groups

**Verification:**
- Navigate to Ad Groups → Rules & Flags
- Edit a rule and save
- Toast should slide in from top-right corner (or wherever the app's toast normally appears)
- Should NOT appear at bottom of page

---

### BUG 5: Risk level always changes to "High" when editing

**Problem:**
- When editing an existing rule, the Risk level dropdown doesn't show the current value
- On save, risk level changes to "High" regardless of what it was before
- Example: Rule has risk="low" → Edit → Save → Now risk="high"

**Location:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\ag_rules_flow_builder.html`
- JavaScript section that loads rule data into modal for editing

**Fix Required:**

**Check 1 - Risk level population on edit:**
When loading a rule for editing, verify the risk level dropdown is set:

```javascript
function loadRuleForEdit(ruleData) {
    // ... other fields ...
    
    // MUST set risk level dropdown to current value:
    document.getElementById('risk-level-select').value = ruleData.risk_level;
    // or
    document.querySelector('#risk-level-select').value = ruleData.risk_level;
}
```

**Check 2 - Risk level in save payload:**
When saving, verify the risk level is read from dropdown (not hardcoded):

```javascript
function saveRule() {
    const payload = {
        // ... other fields ...
        risk_level: document.getElementById('risk-level-select').value,  // NOT hardcoded 'high'
    };
}
```

**Check 3 - Dropdown options:**
Verify dropdown has all 3 options with correct values:
```html
<select id="risk-level-select">
    <option value="low">Low</option>
    <option value="medium">Medium</option>
    <option value="high">High</option>
</select>
```

**Check 4 - Reference working implementation:**
Look at `rules_flow_builder.html` (Campaigns modal) to see how risk level is handled:
- How is it populated when editing?
- How is it read when saving?
- Copy the exact same pattern

**Verification:**
- Navigate to Ad Groups → Rules & Flags
- Find a rule with "Low" risk (should have green dot)
- Click Edit pencil
- Modal opens → Risk level dropdown should show "Low" selected
- Change another field (e.g., cooldown)
- Save
- Rule should STILL show "Low" risk (green dot)
- Repeat test with "Medium" and "High" risk rules

---

## TESTING CHECKLIST

After fixes:

**Toast test:**
- [ ] Edit any rule on Ad Groups page
- [ ] Save
- [ ] Toast slides in from top-right (same as Campaigns page)
- [ ] Toast does NOT appear at bottom of page

**Risk level test:**
- [ ] Edit a rule with "Low" risk → Save → Still shows "Low" (green dot)
- [ ] Edit a rule with "Medium" risk → Save → Still shows "Medium" (yellow dot)
- [ ] Edit a rule with "High" risk → Save → Still shows "High" (red dot)
- [ ] Create new rule → Set to "Low" → Save → Shows "Low"
- [ ] Edit the new rule → Change to "Medium" → Save → Shows "Medium"

**No regressions:**
- [ ] Modal still appears centered as popup
- [ ] Campaigns page still shows only campaign rules
- [ ] Ad Groups page still shows only ad group rules
- [ ] Zero console errors

---

## REFERENCE FILES

**For Bug 4 (Toast):**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\campaigns.html` — Working toast example
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\rules_flow_builder.html` — Working toast in Campaigns modal
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\ag_rules_flow_builder.html` — Fix here

**For Bug 5 (Risk level):**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\rules_flow_builder.html` — Working risk level example
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\ag_rules_flow_builder.html` — Fix here

---

## DELIVERABLES

1. Fixed toast system in Ad Groups modal
2. Fixed risk level dropdown population and save logic
3. Verification report confirming both bugs resolved

---

**Document Version:** 1.0
**Last Updated:** 2026-03-21
