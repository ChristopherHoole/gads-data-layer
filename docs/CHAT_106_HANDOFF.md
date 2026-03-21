# CHAT 106: HANDOFF — Ready for Entity Expansion

**Date:** 2026-03-21
**Status:** Investigation Complete
**Next:** Brief 2 — Ad Groups Implementation (Chat 107)

---

## INVESTIGATION SUMMARY

All Campaigns Rules & Flags files have been studied in detail. The system is well-architected for entity expansion:

- **Database**: `rules` table already has `entity_type` column (default 'campaign'). No schema changes needed.
- **Engine**: `recommendations_engine.py` is already multi-entity with `ENTITY_TABLES`, `ENTITY_ID_COLUMNS`, and per-entity metric maps.
- **Flags table**: Already has `entity_type`, `entity_id`, `entity_name` columns.
- **CSS**: Fully entity-agnostic. All badge classes, flow builder styles, and table styles work unchanged.
- **Action labels**: `recommendations.py` already has entity-aware labels for campaign, keyword, shopping, ad_group.

---

## EXPANSION PATTERN (Per Entity)

For each new entity (Ad Groups → Keywords → Ads → Shopping), the implementation follows this pattern:

### Files to CREATE (new per entity)
1. **Template**: `templates/components/rules_flow_builder_{entity}.html` — Copy flow builder, change:
   - Step 1: Entity picker (ad groups/keywords/ads/products instead of campaigns)
   - Step 3: Type cards (entity-specific categories)
   - Step 4: Metric options + action options (entity-specific)
   - Save payload: `entity_type: '{entity}'`
   - API URL: `/{entity-page}/rules` instead of `/campaigns/rules`

2. **Template**: `templates/components/rules_flags_tab_{entity}.html` — Copy tab, change:
   - Header text: "Ad group rules & flags" etc.
   - Filter pills: Entity-specific categories
   - Table columns: Entity name column
   - Action labels: Entity-specific

### Files to MODIFY (add routes)
3. **Route file**: `routes/{entity_page}.py` — Add CRUD routes:
   - `GET /{entity}/rules` — list rules for entity
   - `POST /{entity}/rules` — create
   - `PUT /{entity}/rules/<id>` — update
   - `DELETE /{entity}/rules/<id>` — delete
   - `POST /{entity}/rules/<id>/toggle` — toggle enabled
   - `POST /{entity}/rules/<id>/save-as-template` — save as template

4. **Entity page template**: Include the new tab components.

### Files that need NO changes
- `rules.css` — Entity-agnostic
- `recommendations.css` — Entity-agnostic
- `recommendations_engine.py` — Already multi-entity
- `rules` table schema — Already has `entity_type`
- `flags` table schema — Already has `entity_type`

---

## AD GROUPS SPECIFICS (Brief 2 Preview)

Based on `RULES_FLAGS_DESIGN_ALL_ENTITIES1.md`:

### Rules (12 total)
- **Bid (8 rules)**: CPC bid adjustments based on ROAS, CPA, impression share, CTR
- **Status (4 rules)**: Pause/enable based on ROAS, conversion performance, quality score
- **No Budget category** — ad groups inherit campaign budget

### Flags (18 total)
- **Performance (8)**: ROAS/CPA/CTR/CVR declines, cost increases, wasted spend
- **Anomaly (6)**: Cost/click spikes/drops, volatility detection
- **Technical (4)**: Impression share, optimization score, low data warnings

### Key differences from Campaigns
| Aspect | Campaigns | Ad Groups |
|--------|-----------|-----------|
| Categories (rules) | Budget, Bid, Status | Bid, Status only |
| Entity picker | Campaign list + strategy lock | Ad Group list (no strategy lock) |
| Actions | Budget increase/decrease, bid adjustments, pause | CPC bid increase/decrease, pause/enable |
| Metrics | Campaign-level aggregates | Ad group-level aggregates |
| Data table | `campaign_features_daily` | `ad_group_daily` |

---

## CRITICAL DECISIONS FOR BRIEF 2

1. **Separate files vs parameterised include?** — The flow builder is ~1180 lines. Recommend separate files per entity for maintainability, not a single parameterised template.

2. **Shared CSS or new CSS?** — Current `rules.css` is fully reusable. No new CSS file needed.

3. **API route namespace** — Each entity gets its own namespace: `/ad-groups/rules`, `/keywords/rules`, etc.

4. **rules_config.json migration** — Non-campaign rules currently in JSON should be migrated to DB as part of expansion. The engine loader needs a `_load_db_{entity}_rules()` function per entity (copy pattern from `_load_db_campaign_rules()`).

5. **Step 1 entity picker** — The campaign picker uses strategy lock (bid strategy filtering). Ad Groups don't need this — simplifies the picker.

---

## RISK AREAS

1. **Condition metric options** — Each entity has different available metrics. Must match what the engine's metric maps support.
2. **Action types** — Ad Groups have different action types than Campaigns (no budget actions, CPC bid instead of tROAS/tCPA).
3. **Entity scope JSON format** — Currently uses `{campaigns: [...]}`. Must use `{ad_groups: [...]}` for new entities. Engine and UI both need to handle this.
4. **Plain English text** — All plain English generators reference "campaign". Must be updated per entity.
5. **Duplicate detection** — Current check queries `WHERE client_config = ? AND type = ? AND action_type = ? AND ...`. Must also filter by `entity_type` to avoid cross-entity false positives.

---

## FILES STUDIED

Complete list of files investigated:
- `act_dashboard/templates/campaigns.html`
- `act_dashboard/templates/recommendations.html`
- `act_dashboard/templates/components/rules_flow_builder.html`
- `act_dashboard/templates/components/rules_flags_tab.html`
- `act_dashboard/templates/components/rules_card.html`
- `act_dashboard/routes/campaigns.py`
- `act_dashboard/routes/recommendations.py`
- `act_dashboard/routes/rules_api.py`
- `act_dashboard/routes/rule_helpers.py`
- `act_dashboard/static/css/rules.css`
- `act_dashboard/static/css/recommendations.css`
- `act_autopilot/recommendations_engine.py`
- `act_autopilot/rules_config.json`
- `warehouse.duckdb` (rules + flags table schemas)
- `docs/RULES_FLAGS_DESIGN_ALL_ENTITIES1.md`
- `docs/KNOWN_PITFALLS.md` (sections 13, 16)
- `docs/LESSONS_LEARNED.md` (lessons 35-37, 54-59, 71-75, 87-92)

---

**Ready for Brief 2 (Ad Groups Implementation).**

---

**Document Version:** 1.0
**Last Updated:** 2026-03-21
