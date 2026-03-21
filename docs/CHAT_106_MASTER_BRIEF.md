# CHAT 106: RULES & FLAGS ENTITY EXPANSION — MASTER BRIEF

**Date:** 2026-03-21
**Estimated Time:** 1 hour (investigation only)
**Priority:** HIGH
**Dependencies:** Campaigns Rules & Flags complete (Chat 101)

---

## CONTEXT

Campaigns Rules & Flags is complete and working (Chat 101). The system has:
- 19 campaign rules (13 Budget, 6 Bid)
- 30 campaign flags (16 Performance, 8 Anomaly, 6 Technical)
- Full 5-step modal flow for creating/editing rules and flags
- Templates tab with save-as-template functionality
- Rules/Flags/Templates sub-tabs with filter pills
- Recommendations engine integration
- Flags engine integration

We now need to expand Rules & Flags to 4 additional entities: **Ad Groups, Keywords, Ads, Shopping**.

This will be done sequentially, one entity at a time:
1. Ad Groups (Brief 2 — coming next)
2. Keywords (Brief 3 — after Ad Groups complete)
3. Ads (Brief 4 — after Keywords complete)
4. Shopping (Brief 5 — after Ads complete)

---

## OBJECTIVE

Investigate and analyze the complete Campaigns Rules & Flags implementation to prepare for entity expansion.

---

## DELIVERABLES

1. Investigation report documenting:
   - All files involved in Campaigns Rules & Flags
   - How the modal flow works (5 steps)
   - How rules/flags are stored (database + rules_config.json)
   - How the templates system works
   - How the engine integration works
   - CSS patterns and styling
   - JavaScript patterns

2. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_106_INVESTIGATION_REPORT.md` — CREATE

3. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_106_HANDOFF.md` — CREATE

---

## REQUIREMENTS

### Investigation Scope

**YOU MUST STUDY THESE FILES IN DETAIL:**

**Templates:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\campaigns.html` — Campaigns page with Rules & Flags tab
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\recommendations.html` — Main Recommendations page (reference for Flags tab)
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\rules_flow_builder.html` — 5-step modal (1014+ lines)
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\rules_flags_tab.html` — Tab pane with tables and JS
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\rules_card.html` — Summary card component

**Routes:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\campaigns.py` — Campaign rules CRUD routes
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\recommendations.py` — Flags routes (/flags/cards, /flags/<id>/acknowledge, /flags/<id>/ignore)

**CSS:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\rules.css` — All rules/flags styling (modal, progress bar, badges, tables)
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\recommendations.css` — Recommendations/flags styling

**Engine:**
- `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py` — Rules engine + flags engine (_run_flag_engine)
- `C:\Users\User\Desktop\gads-data-layer\act_autopilot\rules_config.json` — Rules UI config layer

**Database:**
- Study the `rules` table schema in warehouse.duckdb
- Study the `flags` table schema in warehouse.duckdb

### What to Document

For each file, document:
1. **Purpose** — What does this file do?
2. **Key patterns** — What are the repeating patterns (e.g., modal step structure, badge CSS classes)?
3. **Entity-specific code** — What code will need to change per entity (e.g., "campaign" → "ad_group")?
4. **Reusable code** — What code can be copied exactly as-is?

### Critical Understanding Required

You MUST understand:
- How the 5-step modal flow works (step navigation, progress bar, sidebar)
- How rules/flags are saved to the database vs rules_config.json
- How templates work (is_template flag)
- How the filter pills work (data-rule-type / data-flag-type attributes)
- How the engine reads rules and generates recommendations
- How the flags engine reads flags and generates alerts
- CSS class naming patterns (badge-type-bid, badge-type-status, etc.)

---

## SUCCESS CRITERIA

- [ ] All Campaigns Rules & Flags files studied and documented
- [ ] Investigation report complete with file inventory
- [ ] Clear understanding of what code to copy vs what to adapt
- [ ] Ready to receive Brief 2 (Ad Groups implementation)

**DO NOT START BUILDING ANYTHING YET.**

This chat is investigation only. Brief 2 will contain the Ad Groups implementation instructions.

---

## REFERENCE FILES

All files listed in "Investigation Scope" section above.

Additionally, reference:
- `C:\Users\User\Desktop\gads-data-layer\docs\RULES_FLAGS_DESIGN_ALL_ENTITIES1.md` — Contains all 12 Ad Groups rules + all 18 Ad Groups flags (CORRECTED VERSION)
- `C:\Users\User\Desktop\gads-data-layer\docs\KNOWN_PITFALLS.md` — Rules & Flags pitfalls (sections 13, 16)
- `C:\Users\User\Desktop\gads-data-layer\docs\LESSONS_LEARNED.md` — Rules & Flags lessons (lessons 35-37, 54-59, 71-75, 87-92)

---

## TESTING

Investigation only — no testing required for this chat.

Testing will occur in Briefs 2-5 (entity implementations).

---

## NEXT STEPS

After completing this investigation:
1. Report back with investigation summary
2. Wait for Brief 2 (Ad Groups implementation)
3. Do NOT start building until Brief 2 is received

---

**CRITICAL REMINDER:**

This is a **4-step sequential project**:
- Chat 106 (this chat): Investigation only
- Chat 107: Ad Groups implementation (Brief 2)
- Chat 108: Keywords implementation (Brief 3)
- Chat 109: Ads implementation (Brief 4)
- Chat 110: Shopping implementation (Brief 5)

Do ONE entity at a time. Do NOT try to do all 4 at once.

---

**Document Version:** 1.0
**Last Updated:** 2026-03-21
