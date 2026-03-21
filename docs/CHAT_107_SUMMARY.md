# CHAT 107: Ad Groups Rules & Flags — Summary

**Date:** 2026-03-21
**Status:** Complete
**Entity:** Ad Groups (entity_type='ad_group')

---

## What Was Built

Complete Rules & Flags system for Ad Groups, matching the Campaigns pattern (5-step flow builder modal, rules/flags/templates sub-tabs, full CRUD).

## Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `act_dashboard/templates/components/ag_rules_flags_tab.html` | ~800 | Rules/Flags/Templates sub-tabs with tables, filters, search |
| `act_dashboard/templates/components/ag_rules_flow_builder.html` | ~1100 | 5-step modal for creating/editing rules & flags |
| `scripts/seed_ad_group_rules.py` | ~200 | Database seeder: 12 rules + 18 flags |

## Files Modified

| File | Changes |
|------|---------|
| `act_dashboard/templates/ad_groups.html` | Added rules.css link, replaced old Rules tab with Rules & Flags tab, included new components |
| `act_dashboard/routes/ad_groups.py` | Added rfb_ad_groups to template context, added 6 CRUD routes (list/create/update/delete/toggle/save-as-template) |
| `act_dashboard/app.py` | Added CSRF exemptions for 6 new ad_groups rules routes |

## Database

- **30 rows** seeded into `rules` table with `entity_type='ad_group'`
- **12 rules**: 8 Bid + 4 Status
- **18 flags**: 8 Performance + 6 Anomaly + 4 Technical
- All with `client_config='client_christopher_hoole'`

## Key Design Decisions

1. **Separate component files** — `ag_rules_flags_tab.html` and `ag_rules_flow_builder.html` are standalone copies adapted from campaign components, not shared parameterized templates
2. **JS namespace isolation** — All functions/variables prefixed with `ag` to avoid collision with campaign rules on the same page load
3. **No Budget category** — Ad Groups only have Bid + Status rules (budget is campaign-level)
4. **No strategy lock** — Ad group picker doesn't filter by bid strategy (unlike campaigns)
5. **entity_type filter** — All CRUD queries include `WHERE entity_type='ad_group'`

## Verification Results

| Test | Result |
|------|--------|
| Rules tab badge | 30 (correct) |
| Rules table | 12 rules in 2 groups: Bid (8), Status (4) |
| Flags table | 18 flags in 3 groups: Performance (8), Anomaly (6), Technical (4) |
| Filter pills | All/Bid/Status for rules, All/Performance/Anomaly/Technical for flags |
| Create rule | Saves with entity_type='ad_group', badge updates to 31 |
| Toggle rule | Flips enabled, info text updates |
| Delete rule | Removes row, badge updates |
| Edit rule | Pre-fills flow builder correctly |
| Save as template | Creates template copy, templates badge updates |
| Flow builder Step 1 | Shows 16 ad groups (not campaigns) |
| Flow builder Step 3 | Shows only Bid + Status (no Budget) |
| Flow builder Step 4 | Ad group metrics + actions (no budget actions) |
| Console errors | 0 |
| Server errors | 0 |
