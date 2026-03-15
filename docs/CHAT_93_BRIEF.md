# CHAT 93: TEMPLATES TAB — TABLE REDESIGN + SAVE AS TEMPLATE

**Date:** 2026-03-15
**Estimated Time:** 2–3 hours
**Priority:** HIGH
**Dependencies:** Chat 91 complete ✅, Chat 92 complete ✅

---

## CONTEXT

The Rules & Flags tab has 3 sub-tabs: Rules, Flags, Templates. The Templates sub-tab currently shows a hardcoded card grid with 6 example templates. This needs to be replaced with a proper table (same design as Rules and Flags tabs) driven by real DB data. Every rule and flag should be saveable as a template via a new button on each row.

---

## OBJECTIVE

Replace the hardcoded template cards with a live data-driven table. Add a "save as template" button to every rule and flag row. Templates are stored as regular rules/flags rows with `is_template = TRUE`.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\scripts\add_is_template_col.py` — CREATE
   - Migration script: adds `is_template BOOLEAN DEFAULT FALSE` to rules table
   - Run against both warehouse.duckdb and warehouse_readonly.duckdb
   - Safe to re-run

2. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\campaigns.py` — MODIFY
   - Add `is_template` to INSERT fields in `create_rule()`
   - Add `is_template` to UPDATE fields in `update_rule()`
   - Add new route: `POST /campaigns/rules/<int:rule_id>/save-as-template`
   - Add CSRF exemption for new route in app.py

3. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — MODIFY
   - Add CSRF exemption for `campaigns.save_as_template`

4. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\rules_flags_tab.html` — MODIFY
   - Replace hardcoded template cards with live data table
   - Add save-as-template button to every Rules row
   - Add save-as-template button to every Flags row
   - Add template count badge to Templates tab button

5. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\rules.css` — MODIFY
   - Add save-as-template button style

6. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_93_HANDOFF.md` — CREATE
7. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_93_SUMMARY.md` — CREATE

---

## REQUIREMENTS

### Migration script

```python
import duckdb

for db_path in [
    r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb',
    r'C:\Users\User\Desktop\gads-data-layer\warehouse_readonly.duckdb'
]:
    conn = duckdb.connect(db_path)
    try:
        conn.execute("ALTER TABLE rules ADD COLUMN is_template BOOLEAN DEFAULT FALSE")
        print(f"{db_path}: column added")
    except Exception as e:
        print(f"{db_path}: {e} (safe to ignore if column exists)")
    conn.close()
```

### New backend route: save-as-template

`POST /campaigns/rules/<int:rule_id>/save-as-template`

Logic:
1. Fetch the original rule row by ID
2. Duplicate it as a new INSERT with:
   - `is_template = TRUE`
   - `enabled = FALSE`
   - `entity_scope = '{"scope": "all"}'` (clear campaign selection)
   - `name = original name + ' (template)'` if name doesn't already end in '(template)'
   - All other fields copied exactly
3. Return `{'success': True, 'data': new_row}`

### GET /campaigns/rules response

`is_template` is already returned via `SELECT *` once the column exists. No change to the GET route needed.

### POST/PUT routes

Add `is_template` to the fields read from request data:
```python
is_template = bool(data.get('is_template', False))
```
Include in INSERT and UPDATE statements.

### Templates table — structure

Filter: `r.is_template === true` in JS

Columns (in order):
- Name
- Rule/Flag badge
- Rule type badge
- Campaign type badge
- Plain English
- Conditions
- Action
- Cooldown
- "Use template" button

Group rows by type: Budget → Bid → Status → Performance → Anomaly → Technical
Alphabetical within each group.
Group header colspan = 9.

No edit button. No delete button. No toggle. Read-only table.

### "Use template" button behaviour

When clicked, call `openRulesFlow(row)` BUT clear the ID so it creates a new rule:
```javascript
function rfUseTemplate(row) {
    var copy = Object.assign({}, row);
    copy.id = null;  // forces POST not PUT
    copy.entity_scope = {scope: 'all'};
    copy.enabled = true;
    openRulesFlow(copy);
}
```

### "Save as template" button

Add to every row in both Rules and Flags tables, alongside the existing edit/delete buttons.
Use Material Symbol icon `bookmark_add`.
On click: `POST /campaigns/rules/<id>/save-as-template`
On success: show toast "Saved as template", refresh `rfLoadData()`

```javascript
function rfSaveAsTemplate(ruleId) {
    fetch('/campaigns/rules/' + ruleId + '/save-as-template', {method: 'POST'})
        .then(function(r) { return r.json(); })
        .then(function(d) {
            if (d.success) {
                rfShowToast('Saved as template.', 'success');
                rfLoadData();
            } else {
                rfShowToast('Error: ' + (d.error || 'Unknown error'), 'danger');
            }
        });
}
```

### Templates tab badge

Update the Templates tab button to show a live count badge, same pattern as Rules and Flags badges:
```html
<button ... id="rf-tab-templates">Templates <span id="rf-templates-count" class="badge ...">0</span></button>
```
Update count in `rfRenderTemplates()` at the end:
```javascript
document.getElementById('rf-templates-count').textContent = templateRows.length;
```

### Existing template cards — REMOVE

The current hardcoded template cards HTML (6 cards in a grid) must be completely removed and replaced with the new table structure. The instructional text "Pick a template to pre-fill the rule builder..." can be kept as a subtitle above the table.

### Rules engine exclusion

The recommendations engine already filters by `client_config` and `enabled`. Templates have `enabled = FALSE` so they are automatically excluded from rule evaluation. No changes to recommendations_engine.py needed.

### CSS for save-as-template button

Add to rules.css:
```css
.btn-save-template {
    color: #5f6368;
    background: none;
    border: none;
    padding: 4px;
    cursor: pointer;
}
.btn-save-template:hover {
    color: #1558d6;
}
```

---

## SUCCESS CRITERIA

- [ ] Migration script runs cleanly on both databases
- [ ] `is_template` column exists in rules table
- [ ] Templates tab shows a table (not cards)
- [ ] Templates tab only shows rows where is_template = TRUE
- [ ] Templates table groups by type, sorted alphabetically within groups
- [ ] "Use template" button opens flow builder pre-filled, creates new rule on save
- [ ] "Save as template" button appears on every Rules row
- [ ] "Save as template" button appears on every Flags row
- [ ] Clicking save-as-template creates a new template row in the DB
- [ ] Toast confirms save-as-template success
- [ ] Templates tab badge shows correct count
- [ ] Existing 57 rules/flags are unaffected (is_template = FALSE)
- [ ] Flask starts cleanly with no errors

---

## REFERENCE FILES

- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\campaigns.py` — existing create_rule() and update_rule() patterns
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\rules_flags_tab.html` — existing Rules and Flags table render functions (rfRenderRules, rfRenderFlags) — Templates table should follow same pattern
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\rules.css` — existing button styles
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — CSRF exemption pattern

---

## TESTING

1. Run migration script first:
   `python C:\Users\User\Desktop\gads-data-layer\scripts\add_is_template_col.py`

2. Start Flask:
   `python act_dashboard/app.py`

3. Open Rules & Flags tab → Templates sub-tab — confirm table renders (will be empty initially)

4. Click "Save as template" bookmark icon on any rule row — confirm toast appears

5. Click Templates sub-tab again — confirm the saved template now appears in the table

6. Click "Use template" on that row — confirm flow builder opens pre-filled

7. Complete the flow and save — confirm a new rule appears in the Rules tab (not a duplicate template)

8. Confirm the original 27 rules and 30 flags are unchanged

9. Report Flask log output for the save-as-template POST call
