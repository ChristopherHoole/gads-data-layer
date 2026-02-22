# CHAT 26 DETAILED SUMMARY — M5 Card-Based Rules Tab

**Date:** 2026-02-22
**Chat:** 26
**Scope:** Replace dense table-based Rules tab with M5 card-based UI

---

## WHAT WAS BUILT

### Overview
Replaced the existing Rules tab (a dense read-only table pulled from Python docstrings) with a fully interactive card-based UI backed by a new JSON config layer. Rules are now editable, toggleable, and deletable through the UI.

### Data Layer
Created `act_autopilot/rules_config.json` — a new UI config layer containing 13 rules in the M5 data model. Fields per rule:

```
rule_id, rule_type, rule_number, display_name, name
scope (blanket/specific), campaign_id
condition_metric, condition_operator, condition_value, condition_unit
condition_2_metric, condition_2_operator, condition_2_value, condition_2_unit
action_direction, action_magnitude
risk_level, cooldown_days, enabled
created_at, updated_at
```

The 13 rules were derived from existing Python docstrings in `act_autopilot/rules/*.py` — translated to the M5 model as approximations.

### API Layer
Created `act_dashboard/routes/rules_api.py` — Flask Blueprint with 6 routes:

| Route | Method | Purpose |
|---|---|---|
| `/api/rules` | GET | Return all rules |
| `/api/rules/add` | POST | Add new rule |
| `/api/rules/<id>/update` | PUT | Update rule fields |
| `/api/rules/<id>/toggle` | PUT | Toggle enabled/disabled |
| `/api/rules/<id>` | DELETE | Delete rule |
| `/api/campaigns-list` | GET | Return campaign names from warehouse |

### UI Layer
Replaced `rules_tab.html` entirely. Key features:

- 2-column card grid per rule type section
- 4px colour-coded top border (blue=budget, green=bid, red=status)
- Each card shows: conditions, action pill, cooldown, scope pill, risk badge, toggle, edit, delete
- Add/Edit drawer (slides in from right, 480px wide)
- 5-step drawer form: Rule Type → Scope → Condition → Action → Settings
- Live preview panel in drawer updates as form is filled
- Campaign picker dropdown — fetches live from `/api/campaigns-list`
- Campaign-specific rules show campaign ID pill + OVERRIDES BLANKET tag
- Filter bar: All / Budget / Bid / Status / Blanket only / Campaign-specific only / Active only
- Summary strip: count badges per type + total active counter

### campaigns.html changes
- Added third tab: Recommendations (placeholder, Chat 27 scope)
- Replaced Bootstrap Icons `<i>` tags with inline SVG (no CDN dependency)
- Rules badge now uses `rules_config|length` (from JSON) not old `rules|length`

---

## DECISIONS MADE

### Dual-layer architecture
The JSON config layer (`rules_config.json`) and Python execution layer (`act_autopilot/rules/*.py`) are intentionally separate. The UI only reads/writes JSON. The Python functions that actually execute changes are never touched by the UI. This was a Master Chat architectural decision made before Chat 26 started.

### No Bootstrap Icons CDN
Previous implementation used `<i class="bi bi-...">` tags requiring Bootstrap Icons CDN. Replaced with inline SVG throughout to eliminate the external dependency.

### campaign_id stored, not campaign_name
The picker stores `campaign_id` in JSON (not the name). Names can change; IDs are stable. The card displays the raw ID in the scope pill. Name resolution for display is deferred to Chat 27.

### Rule numbering not re-sequenced on delete
When a rule is deleted, subsequent rules keep their numbers. `budget_7` deleted → next add is `budget_8`. The display name reflects this gap. This is intentional — `rule_id` is the true identifier, not the number.

### `Path(__file__).parent.parent.parent` fix
Initial path resolution used `.parent.parent` which resolved to inside `act_dashboard/`, missing the project root. Fixed to `.parent.parent.parent` to correctly reach `gads-data-layer/act_autopilot/rules_config.json`.

---

## BUGS FOUND AND FIXED

### 1. "budget budget" double word
**Location:** `rules_tab.html` JavaScript, `actionTarget` variable
**Cause:** `${typeLabel.toLowerCase()} budget` — for budget rules this produced "budget budget"
**Fix:** Replaced with explicit mapping: `{ budget: 'daily budget', bid: 'bid target', status: 'campaign status' }`
**Result:** Cards now show "Increase by 10% daily budget", "Decrease by 5% bid target" etc.

### 2. Drawer visible on page load
**Location:** `rules_tab.html`, drawer `<div>` inline style
**Cause:** Both `display:none` and `display:flex` in same style string — `flex` wins in CSS cascade
**Fix:** Removed `display:flex` from inline style, kept `display:none`. JS adds flex via `openDrawer()` function.

### 3. rules_config.json path wrong
**Location:** `rules_api.py`, `RULES_CONFIG_PATH`
**Cause:** `Path(__file__).parent.parent` resolves to `act_dashboard/`, not project root
**Fix:** `Path(__file__).parent.parent.parent` to reach `gads-data-layer/`

### 4. Campaign picker empty
**Location:** `rules_tab.html`, `setScopeCard()` function
**Cause:** No fetch call existed — dropdown was a static empty `<select>`
**Fix:** Added fetch to `/api/campaigns-list` on scope card click, populates dropdown dynamically. Pre-selects saved `campaign_id` when editing existing rules.

---

## CRUD TEST RESULTS

All 7 tests passed on `Synthetic_Test_Client`:

| Test | Pass |
|---|---|
| Add Rule → new card appears | ✅ |
| Edit Rule → card updates | ✅ |
| Delete Rule → removed + persists on reload | ✅ |
| Toggle off → persists on reload | ✅ |
| Campaign-specific → picker populated, card shows ID + OVERRIDES BLANKET | ✅ |
| Filter Active only → disabled card hidden | ✅ |
| Filter Campaign-specific only → only specific-scoped cards shown | ✅ |

---

## LESSONS LEARNED

### Always check path depth when building API modules
Files in `act_dashboard/routes/` are 3 levels deep from project root. `.parent.parent.parent` needed to reach `gads-data-layer/`. Easy to miss.

### Inline styles with duplicate properties — last one wins
`display:none; display:flex` — the browser ignores the first. Can't use inline styles for show/hide if you also need flex layout. Solution: set `display:none` inline for initial hide, use JS to set `display:flex` explicitly on open.

### Campaign picker must be wired before campaign-specific rules are useful
An empty picker silently saves `null` as `campaign_id`. This means campaign-specific rules look correct in JSON but apply to nothing at execution time. Always wire the picker to a real data source before declaring feature complete.

### Rule numbering gaps are acceptable
The `rule_id` (e.g. `budget_7`) is the unique identifier used by all API routes. Display name gaps after deletes are cosmetic. Don't re-sequence — it risks collisions and confusion.

### Dual-layer separation must be maintained
The rules_config.json is UI-only. Any future work that tries to sync JSON back to Python execution files would break the architecture. If a rule in JSON has no matching Python function, it simply won't execute — it won't cause errors.
