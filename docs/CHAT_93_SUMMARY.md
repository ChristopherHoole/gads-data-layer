# CHAT 93 SUMMARY: Templates Tab — Table Redesign + Save As Template

**Date:** 2026-03-15
**Status:** Complete

---

## What Was Done

### 1. Migration — `scripts/add_is_template_col.py`
- Added `is_template BOOLEAN DEFAULT FALSE` to the `rules` table in `warehouse.duckdb`
- Script is safe to re-run
- `warehouse_readonly.duckdb` has no `rules` table (reporting-only DB) — expected

### 2. Backend — `act_dashboard/routes/campaigns.py`
- `_serialize_rule()`: added `d['is_template'] = bool(d.get('is_template', False))` for consistent JS typing
- `create_rule()`: added `is_template` to INSERT column list and params
- `update_rule()`: added `is_template` to UPDATE SET and params
- New route: `POST /campaigns/rules/<rule_id>/save-as-template`
  - Fetches original row, duplicates it with `is_template=TRUE`, `enabled=FALSE`, `entity_scope='{"scope":"all"}'`
  - Appends ` (template)` to name unless name already ends with it
  - Returns `{'success': True, 'data': new_row}`

### 3. App factory — `act_dashboard/app.py`
- Added CSRF exemption for `campaigns.save_as_template` (Chat 93 block)

### 4. Frontend — `act_dashboard/templates/components/rules_flags_tab.html`
- **Templates sub-tab button**: added badge `<span id="rf-badge-templates">0</span>`
- **Templates pane**: replaced 6 hardcoded cards with a live `<table id="rf-templates-table">`
  - 9 columns: Name, Rule/Flag, Type, Campaign type, Plain English, Conditions, Action, Cooldown, Use template
  - Grouped by type order: Budget → Bid → Status → Performance → Anomaly → Technical
  - Alphabetical within each group
  - Read-only (no edit/delete/toggle)
- **rfRenderRules()**: filters `!r.is_template` so templates don't appear in the Rules tab
- **rfRenderFlags()**: filters `!r.is_template` so templates don't appear in the Flags tab
- **rfUpdateBadges()**: updated to also set `rf-badge-templates` count; main badge now counts non-template rows only
- **rfLoadData()**: calls `rfRenderTemplates()` after data loads
- **rfRenderTemplates()**: new function renders templates table with group headers and "Use template" buttons
- **rfUseTemplate(ruleId)**: opens flow builder pre-filled from template (clears id, entity_scope, sets enabled=true)
- **rfSaveAsTemplate(ruleId)**: POSTs to save-as-template route, shows toast, refreshes data
- **Save-as-template button**: added `bookmark_add` icon button to every row in both Rules and Flags tables

### 5. CSS — `act_dashboard/static/css/rules.css`
- Added `.btn-save-template` and `.btn-save-template:hover` styles

---

## Success Criteria Status

- [x] Migration script runs cleanly on warehouse.duckdb
- [x] `is_template` column exists in rules table
- [x] Templates tab shows a table (not cards)
- [x] Templates tab only shows rows where is_template = TRUE
- [x] Templates table groups by type, sorted alphabetically within groups
- [x] "Use template" button opens flow builder pre-filled, creates new rule on save
- [x] "Save as template" button appears on every Rules row
- [x] "Save as template" button appears on every Flags row
- [x] Clicking save-as-template creates a new template row in the DB
- [x] Toast confirms save-as-template success
- [x] Templates tab badge shows correct count
- [x] Existing 57 rules/flags are unaffected (is_template = FALSE by default)
- [x] Flask CSRF exempt for new route

---

## Files Changed

| File | Change |
|------|--------|
| `scripts/add_is_template_col.py` | Created |
| `act_dashboard/routes/campaigns.py` | Modified — serialize, create, update, new route |
| `act_dashboard/app.py` | Modified — CSRF exemption |
| `act_dashboard/templates/components/rules_flags_tab.html` | Modified — templates table, save-as-template button, new JS functions |
| `act_dashboard/static/css/rules.css` | Modified — .btn-save-template styles |
| `docs/CHAT_93_SUMMARY.md` | Created |
| `docs/CHAT_93_HANDOFF.md` | Created |
