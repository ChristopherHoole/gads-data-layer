# CHAT 107: HANDOFF — Ad Groups Rules & Flags Complete

**Date:** 2026-03-21
**Status:** Complete, verified, ready for next entity
**Next:** Chat 108 — Keywords Rules & Flags (Brief 3)

---

## What's Done

Ad Groups now has a full Rules & Flags system matching the Campaigns pattern:
- 5-step flow builder modal (ad group picker, rule/flag selection, type, conditions, save)
- Rules/Flags/Templates sub-tabs with search, filter pills, grouped tables
- Full CRUD: create, edit, delete, toggle, save-as-template
- 30 seeded rules/flags (12 rules + 18 flags)

## Pattern Established for Next Entities

The Ad Groups implementation establishes a clear copy pattern for Keywords, Ads, and Shopping:

### Per-entity files to create:
1. `templates/components/{prefix}_rules_flags_tab.html` — Copy from `ag_rules_flags_tab.html`
2. `templates/components/{prefix}_rules_flow_builder.html` — Copy from `ag_rules_flow_builder.html`
3. `scripts/seed_{entity}_rules.py` — Seed script

### Per-entity modifications:
1. Entity page template — Add rules.css, replace Rules tab, include new components
2. Entity route file — Add rfb_{entities} to context, add 6 CRUD routes
3. `app.py` — Add CSRF exemptions for new routes

### Entity-specific changes per file:
- JS function prefix (ag → kw, ad, sh)
- Element ID prefix (ag- → kw-, ad-, sh-)
- API endpoint (/ad_groups/rules → /keywords/rules)
- entity_type in save payload
- Step 1 entity picker
- Step 3 type cards (categories vary per entity)
- Step 4 metrics and actions (match entity's metric map)
- Filter pills (categories vary)

## Prefixes for Remaining Entities

| Entity | File prefix | JS prefix | Element ID prefix | Route prefix |
|--------|-------------|-----------|-------------------|--------------|
| Keywords | `kw_` | `kw` | `kw-` | `/keywords/rules` |
| Ads | `ad_` | `adR` | `adr-` | `/ads/rules` |
| Shopping | `sh_` | `sh` | `sh-` | `/shopping/rules` |

## Test Checklist (reuse for each entity)

- [ ] Rules tab badge shows correct total
- [ ] Rules table shows correct rule count and groups
- [ ] Flags table shows correct flag count and groups
- [ ] Filter pills work (entity-specific categories)
- [ ] Create new rule → saves with correct entity_type
- [ ] Edit rule → pre-fills correctly
- [ ] Delete rule → removes and updates badge
- [ ] Toggle → flips enabled
- [ ] Save as template → creates template copy
- [ ] Flow builder Step 1 → shows correct entities (not campaigns)
- [ ] Flow builder Step 3 → shows correct categories
- [ ] Flow builder Step 4 → shows correct metrics and actions
- [ ] Zero console errors
- [ ] Zero server errors

---

**Ready for Brief 3 (Keywords implementation).**
