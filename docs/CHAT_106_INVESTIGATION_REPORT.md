# CHAT 106: INVESTIGATION REPORT — Rules & Flags Entity Expansion

**Date:** 2026-03-21
**Status:** Complete
**Purpose:** Document the full Campaigns Rules & Flags implementation to prepare for expansion to Ad Groups, Keywords, Ads, and Shopping.

---

## 1. FILE INVENTORY

### Templates (5 files)
| File | Lines | Purpose |
|------|-------|---------|
| `act_dashboard/templates/campaigns.html` | ~400+ | Main campaigns page. Includes Rules & Flags tab via `{% include 'components/rules_flags_tab.html' %}` (line 293). Loads `rules.css` + `recommendations.css`. Contains Recommendations tab with Pending/Monitoring/Successful/History/Flags sub-tabs. |
| `act_dashboard/templates/components/rules_flow_builder.html` | ~1180 | 5-step full-page overlay for creating/editing rules & flags. HTML (lines 1-388) + JS (lines 391-1180). Included at bottom of campaigns.html. |
| `act_dashboard/templates/components/rules_flags_tab.html` | ~700+ | Tab pane with Rules/Flags/Templates sub-tabs, filter pills, search, tables. HTML (lines 1-168) + JS (lines 169-700+). Data loaded via AJAX `GET /campaigns/rules`. |
| `act_dashboard/templates/components/rules_card.html` | 163 | Summary card showing active rules count by category, top 3 rules preview, action buttons. |
| `act_dashboard/templates/recommendations.html` | Large | Main Recommendations page. Reference for flags display pattern. |

### Routes (4 files)
| File | Purpose |
|------|---------|
| `act_dashboard/routes/campaigns.py` | Campaign CRUD routes + **Rules CRUD**: `GET /campaigns/rules`, `POST /campaigns/rules`, `PUT /campaigns/rules/<id>`, `DELETE /campaigns/rules/<id>`, `POST /campaigns/rules/<id>/toggle`, `POST /campaigns/rules/<id>/save-as-template` |
| `act_dashboard/routes/recommendations.py` | Flags routes: `GET /flags/cards`, `POST /flags/<id>/acknowledge`, `POST /flags/<id>/ignore`. Also contains `get_action_label()` with entity-aware action labels for campaign/keyword/shopping/ad_group. |
| `act_dashboard/routes/rules_api.py` | Legacy JSON-based rules API (`/api/rules`). Reads/writes `rules_config.json`. Not used by the flow builder UI. |
| `act_dashboard/routes/rule_helpers.py` | Parses rule function docstrings. Legacy helper for old rule module system. |

### CSS (2 files)
| File | Lines | Purpose |
|------|-------|---------|
| `act_dashboard/static/css/rules.css` | ~700+ | All rules/flags styling: flow overlay, progress bar, choice cards, condition builder, action builder, settings grid, summary box, footer, tables, type badges, risk dots, sidebar, sub-tabs. |
| `act_dashboard/static/css/recommendations.css` | Large | Recommendations + flags card styling. |

### Engine (2 files)
| File | Purpose |
|------|---------|
| `act_autopilot/recommendations_engine.py` | Main engine: `run_recommendations_engine()` + `_run_flag_engine()`. Already multi-entity capable with `ENTITY_TABLES`, `ENTITY_ID_COLUMNS`, entity-specific metric maps. |
| `act_autopilot/rules_config.json` | JSON config for non-campaign rules (keyword, ad_group, shopping). Campaign rules read from DB. Both merged at runtime. |

### Database (2 tables)
| Table | Purpose |
|-------|---------|
| `rules` | 20 columns, 51 rows. Stores all rules + flags + templates. Key columns: `id`, `client_config`, `entity_type`, `name`, `rule_or_flag`, `type`, `campaign_type_lock`, `entity_scope` (JSON), `conditions` (JSON), `action_type`, `action_magnitude`, `cooldown_days`, `risk_level`, `enabled`, `plain_english`, `is_template`. |
| `flags` | 17 columns, 2 rows. Generated flag instances. Key columns: `flag_id`, `rule_id`, `rule_name`, `entity_type`, `entity_id`, `entity_name`, `customer_id`, `status`, `severity`, `trigger_summary`, `plain_english`, `conditions`. |

---

## 2. HOW THE 5-STEP MODAL FLOW WORKS

### Architecture
- **Overlay element**: `#rules-flow-overlay` — fixed position, z-index 1050, centered flex
- **Panel**: `.flow-panel` — 800px max-width, flex column, max-height 90vh
- **State variables**: `_rfbStep` (1-5), `_rfbEditId`, `_rfbHasPreload`, `_rfbIsTemplate`, `_rfbRoF` ('rule'/'flag'), `_rfbType` ('budget'/'bid'/'status'/'performance'/'anomaly'/'technical')

### Steps
| Step | ID | Content | Validation |
|------|----|---------|------------|
| 1 | `rfb-sc-1` | Campaign picker with search, select all/clear, strategy lock | Mixed strategies blocked |
| 2 | `rfb-sc-2` | Rule vs Flag choice cards (2-column grid) | Selection required |
| 3 | `rfb-sc-3` | Type selection cards (3-column grid, populated by `rfbRenderTypeStep()`) | Selection required |
| 4 | `rfb-sc-4` | Condition 1 (required) + Condition 2 (optional) + Action (rules only) + Settings (cooldown/risk) | Values required |
| 5 | `rfb-sc-5` | Rule name input + Summary box + Save button | Name required |

### Progress Bar
- IDs: `rfb-prog-1` through `rfb-prog-5` (circles) + `rfb-pline-1` through `rfb-pline-4` (lines)
- CSS classes: `.active` (blue), `.done` (green)
- Updated by `rfbRenderStep()` on each navigation

### Sidebar ("Your choices")
- IDs: `sb-val-1` through `sb-val-5`
- Updated by `rfbUpdateSidebar()` on every step change
- Shows: campaigns count, rule/flag, type, conditions + action, name

### Navigation
- `rfbNextStep()` → validates then increments `_rfbStep`
- `rfbPrevStep()` → decrements `_rfbStep`
- Step 5 "Save" → `rfbSave()` posts to `/campaigns/rules`

### Opening
- `openRulesFlow()` — new rule, starts at step 1
- `openRulesFlow(existingRow)` — edit mode, pre-fills from row data via `rfbPopulateFromRow()`

---

## 3. HOW RULES/FLAGS ARE STORED

### Database (`rules` table)
- **Primary storage** for campaign rules (entity_type='campaign')
- Schema includes `conditions` as JSON array: `[{metric, op, value, ref}, ...]`
- `entity_scope` as JSON: `{"scope":"all"}` or `{"scope":"specific","campaigns":["id1","id2"]}`
- `is_template` boolean separates templates from active rules
- `rule_or_flag` field: 'rule' or 'flag'
- `type` field: 'budget', 'bid', 'status' (rules) or 'performance', 'anomaly', 'technical' (flags)

### rules_config.json
- **Flat array** of rule objects for non-campaign entities (keyword, ad_group, shopping)
- Different schema: uses `condition_metric`, `condition_operator`, `condition_value`, `condition_unit` (flat fields, not nested JSON)
- Being phased out — campaign rules migrated to DB in Chat 95

### Dual schema note
- DB conditions use `op`/`ref` keys (new flow-builder format)
- JSON config uses `condition_operator`/`condition_unit` (old format)
- Engine normalizes both via `_normalise_operator()` and key fallbacks

---

## 4. HOW TEMPLATES WORK

- **Same table, boolean flag**: `is_template = TRUE` in `rules` table
- **Save as template**: `POST /campaigns/rules/<id>/save-as-template` duplicates row with `is_template=TRUE`, name gets " (template)" suffix
- **Use template**: Opens flow builder pre-filled with template data, but `id=null` so creates new rule
- **Edit template**: Opens flow builder with template's `id` so updates the template itself
- **UI display**: Separate "Templates" sub-tab in `rules_flags_tab.html`, renders via `rfRenderTemplates()`
- **Filter**: Templates excluded from Rules/Flags counts via `!r.is_template`

---

## 5. HOW FILTER PILLS WORK

### Rules sub-tab
```html
<button class="filter-tab" data-rf-filter="budget" onclick="rfSetRuleFilter(this,'rules')">Budget</button>
<button class="filter-tab" data-rf-filter="bid" onclick="rfSetRuleFilter(this,'rules')">Bid</button>
<button class="filter-tab" data-rf-filter="status" onclick="rfSetRuleFilter(this,'rules')">Status</button>
```
- Stores filter in `_rfRuleFilter` variable
- `rfRenderRules()` filters rows by `r.type === _rfRuleFilter`

### Flags sub-tab
```html
<button class="filter-tab" data-rf-filter="performance" onclick="rfSetRuleFilter(this,'flags')">Performance</button>
<button class="filter-tab" data-rf-filter="anomaly" onclick="rfSetRuleFilter(this,'flags')">Anomaly</button>
<button class="filter-tab" data-rf-filter="technical" onclick="rfSetRuleFilter(this,'flags')">Technical</button>
```
- Same mechanism, stored in `_rfFlagFilter`

---

## 6. HOW THE ENGINE WORKS

### Rules Engine (`run_recommendations_engine()`)
1. **Load rules**: Campaign rules from DB (`_load_db_campaign_rules()`), others from `rules_config.json`
2. **Group by entity_type** using `_detect_entity_type()` (parses rule_id prefix)
3. **Query entity data**: Uses `ENTITY_TABLES` mapping (campaign_features_daily, keyword_daily, ad_group_daily, shopping_campaign_daily, ad_daily)
4. **Evaluate conditions**: `_evaluate_condition()` checks metric against threshold
5. **Generate recommendation**: Inserts into `recommendations` table with entity metadata

### Flags Engine (`_run_flag_engine()`)
1. **Load flag rules**: From DB where `rule_or_flag='flag'` and `enabled=TRUE`
2. **Group by entity_type**
3. **Check duplicates**: Skip if active/snoozed flag already exists for same rule+entity
4. **Evaluate conditions** against latest snapshot data
5. **Insert flags**: Bulk insert into `flags` table with UUID flag_id

### Entity-specific mappings (already in place)
```python
ENTITY_TABLES = {
    "campaign": "ro.analytics.campaign_features_daily",
    "keyword":  "ro.analytics.keyword_daily",
    "ad_group": "ro.analytics.ad_group_daily",
    "shopping": "ro.analytics.shopping_campaign_daily",
    "ad":       "ro.analytics.ad_daily",
}
ENTITY_ID_COLUMNS = {
    "campaign": ("campaign_id", "campaign_name"),
    "keyword":  ("keyword_id", "keyword_text"),
    "ad_group": ("ad_group_id", "ad_group_name"),
    "shopping": ("campaign_id", "campaign_name"),
    "ad":       ("ad_id", "ad_name"),
}
```

---

## 7. CSS PATTERNS

### Badge classes (type badges)
```css
.badge-type-budget      { background: #e8f0fe; color: #1558d6; }
.badge-type-bid         { background: #e6f4ea; color: #137333; }
.badge-type-status      { background: #fff3e0; color: #b45309; }
.badge-type-performance { background: #f3e8fd; color: #7b2fa8; }
.badge-type-anomaly     { background: #ffc107; color: #212529; }
.badge-type-technical   { background: #6c757d; color: #fff; }
```

### Rule/Flag badges
```css
.badge-rof-rule  { ... }
.badge-rof-flag  { ... }
```

### Risk dots
```css
.risk-dot-low    { color: green dot }
.risk-dot-medium { color: amber dot }
.risk-dot-high   { color: red dot }
```

### Flow builder key classes
- `.flow-panel`, `.flow-overlay-header`, `.flow-progress-bar`
- `.flow-prog-step`, `.flow-prog-circle`, `.flow-prog-line`
- `.flow-choice-grid`, `.flow-choice-card`
- `.flow-cat-grid`, `.flow-cat-card`
- `.flow-cond-box`, `.flow-cond-row`, `.flow-cond-select`, `.flow-cond-input`
- `.flow-action-box`, `.flow-action-row`
- `.flow-settings-grid`, `.flow-settings-field`
- `.flow-summary-box`, `.flow-summary-line`
- `.flow-footer`, `.flow-sidebar`
- `.flow-body-wrap`, `.flow-body`

---

## 8. JAVASCRIPT PATTERNS

### Data flow
1. Page loads → `rfLoadData()` fetches `GET /campaigns/rules`
2. Response stored in `_rfData` array
3. Three render functions: `rfRenderRules()`, `rfRenderFlags()`, `rfRenderTemplates()`
4. Each filters `_rfData` by `rule_or_flag` + `is_template`
5. Groups rows by type, renders group headers + data rows

### Key JS functions
| Function | Purpose |
|----------|---------|
| `rfLoadData()` | AJAX load all rules/flags from API |
| `rfRenderRules()` | Render rules table with group headers |
| `rfRenderFlags()` | Render flags table with group headers |
| `rfRenderTemplates()` | Render templates table |
| `rfShowSubTab(tab)` | Switch rules/flags/templates sub-tabs |
| `rfSetRuleFilter(btn, context)` | Set filter pill + re-render |
| `rfPlainEnglish(row)` | Generate plain English for rules |
| `rfFlagPlainEnglish(row)` | Generate plain English for flags |
| `rfCondText(row)` | Format conditions for display |
| `rfFlagCondText(row)` | Format flag conditions with direction |
| `rfActionCell(row)` | Format action with arrow icons |
| `rfGuardrail(row)` | Determine guardrail label |
| `rfToggle(id, el)` | Toggle enabled via `POST .../toggle` |
| `rfEditRule(id)` | Open flow builder in edit mode |
| `rfDeleteRule(id)` | Delete via `DELETE .../rules/<id>` |
| `rfSaveAsTemplate(id)` | Save as template via `POST .../save-as-template` |

### Flow builder JS functions
| Function | Purpose |
|----------|---------|
| `openRulesFlow(existingRow)` | Open overlay, optionally pre-fill |
| `closeRulesFlow()` | Close overlay with transition |
| `rfbResetForm()` | Clear all form state |
| `rfbPopulateFromRow(row)` | Pre-fill from existing rule data |
| `rfbRenderStep()` | Update visibility, progress, sidebar |
| `rfbNextStep()` / `rfbPrevStep()` | Navigate steps |
| `rfbValidateStep(step)` | Per-step validation |
| `rfbSave()` | Build payload + POST/PUT to API |
| `rfbRenderCampList(filter)` | Render campaign picker |
| `rfbUpdateStrategyLock()` | Check/display strategy lock |
| `rfbRenderTypeStep()` | Render type selection cards |
| `rfbShowStep4ForRoF()` | Show/hide action section for rules vs flags |
| `rfbUpdateActionTypeOptions()` | Populate action dropdown per type |
| `rfbAutoName()` | Auto-generate rule name |
| `rfbAutoRisk()` | Auto-calculate risk level |
| `rfbBuildSummary()` | Build step 5 summary |
| `rfbUpdateSidebar()` | Update "your choices" sidebar |

### Save payload structure
```javascript
{
  name: "...",
  rule_or_flag: "rule" | "flag",
  type: "budget" | "bid" | "status" | "performance" | "anomaly" | "technical",
  campaign_type_lock: "troas" | "tcpa" | "max_clicks" | "all",
  entity_scope: {scope: "all"} | {scope: "specific", campaigns: [...]},
  conditions: [{metric, op, value, ref}, ...],
  action_type: "increase_budget" | "decrease_budget" | ... | null,
  action_magnitude: 10 | null,
  cooldown_days: 7 | 14 | 30,
  risk_level: "low" | "medium" | "high",
  entity_type: "campaign",  // HARDCODED — must change per entity
  enabled: true,
  is_template: false
}
```

---

## 9. ENTITY-SPECIFIC CODE vs REUSABLE CODE

### What MUST change per entity

| Component | What changes | Example |
|-----------|-------------|---------|
| **Step 1 label** | "Select campaigns" → "Select ad groups" | `rfb-subtitle`, progress bar labels |
| **Step 1 picker** | Campaign list → Ad Group list | `_rfbAllCampaigns` → `_rfbAllAdGroups`, picker rendering |
| **Step 1 strategy lock** | May not apply to Keywords/Ads | Strategy lock logic |
| **Step 3 type cards** | Different categories per entity | `RFB_TYPE_FOR_ROF` object |
| **Step 4 metrics** | Different condition metrics per entity | `<select id="rfb-cond1-metric">` options |
| **Step 4 actions** | Different action types per entity | `RFB_ACTION_OPTIONS` object |
| **Summary labels** | "Pause campaign" → "Pause ad group" | `rfbBuildSummary()` |
| **Save payload** | `entity_type: 'campaign'` → `entity_type: 'ad_group'` | Line 1137 in flow builder |
| **API endpoints** | `/campaigns/rules` → `/ad-groups/rules` | URL in `rfbSave()` |
| **Route handlers** | New blueprint routes per entity | `campaigns.py` → new `ad_groups.py` etc |
| **Table headers** | "Campaigns" column → "Ad Groups" | `rules_flags_tab.html` |
| **Filter pills** | Budget/Bid/Status → Bid/Status (ad groups have no budget) | Filter buttons |
| **Plain English** | Entity-specific wording | `rfPlainEnglish()`, `rfFlagPlainEnglish()` |
| **Action labels** | Entity-specific labels | `ACTION_LABELS`, `rfActionCell()` |
| **Entity scope JSON** | `{campaigns: [...]}` → `{ad_groups: [...]}` | `entity_scope` field |

### What can be REUSED as-is

| Component | Why reusable |
|-----------|-------------|
| **CSS** (`rules.css`) | All classes are entity-agnostic. Badge types, flow builder styles, table styles work unchanged. |
| **5-step structure** | Same step flow, same overlay, same sidebar, same footer. |
| **Progress bar** | Same 5 circles + lines, same CSS classes. |
| **Condition builder** | Same dual-condition UI, same operator/ref selectors. |
| **Rule settings** | Same cooldown/risk selectors. |
| **Save/summary pattern** | Same payload structure (just swap entity_type). |
| **Table rendering pattern** | Same group-by-type → group header + data rows pattern. |
| **Sub-tab pattern** | Same Rules/Flags/Templates sub-tabs with same switching logic. |
| **Toast system** | Same `rfbShowToast()` / `rfShowToast()`. |
| **Database schema** | `rules` table already has `entity_type` column. No schema changes needed. |
| **Engine** | Already multi-entity. `ENTITY_TABLES`, `ENTITY_ID_COLUMNS`, metric maps all in place. |
| **Flags table** | Already has `entity_type`, `entity_id`, `entity_name` columns. |
| **Duplicate detection** | Same pattern: match on `type + action_type + first condition metric`. |

---

## 10. KNOWN PITFALLS (from docs)

1. **Apostrophes in JS strings** — Use HTML entities or escape properly. Unescaped apostrophes crash entire script blocks silently.
2. **Condition schema duality** — Always handle both `op`/`ref` (new) and `operator`/`unit` (old) formats.
3. **vs_prev_pct thresholds** — Store as decimals (-0.30), not whole numbers (-30).
4. **JS state variable order** — Set `_rfbIsTemplate`, `_rfbEditId`, `_rfbHasPreload` AFTER `rfbResetForm()`, not before.
5. **stopPropagation blocks delegation** — Don't use on `<td>` elements if using document-level event listeners.
6. **Functions in IIFE not global** — Expose all onclick handlers via `window.fnName = function(...)`.
7. **Bootstrap dropdown reinit** — Use document-level event delegation for dynamically rendered dropdowns.

---

**Document Version:** 1.0
**Last Updated:** 2026-03-21
