# CHAT 26 HANDOFF — M5 Card-Based Rules Tab

**Date:** 2026-02-22
**Chat:** 26
**Status:** Complete — awaiting git commit approval from Master Chat

---

## GIT COMMIT COMMAND

```powershell
cd C:\Users\User\Desktop\gads-data-layer
git add .
git commit -m "Chat 26 (M5): Card-based Rules Tab + Rules API

- CREATE act_autopilot/rules_config.json (13 rules seeded)
- CREATE act_dashboard/routes/rules_api.py (GET/POST/PUT/DELETE + campaigns-list)
- MODIFY act_dashboard/routes/__init__.py (register rules_api blueprint)
- MODIFY act_dashboard/routes/campaigns.py (load rules_config, pass to template)
- MODIFY act_dashboard/templates/campaigns.html (3 tabs, inline SVG, rules badge)
- REPLACE act_dashboard/templates/components/rules_tab.html (M5 card UI + drawer)"
```

---

## FILES MODIFIED / CREATED

| File | Action | Notes |
|---|---|---|
| `act_autopilot/rules_config.json` | CREATED | 13 rules seeded in M5 data model |
| `act_dashboard/routes/rules_api.py` | CREATED | Full CRUD + `/api/campaigns-list` endpoint |
| `act_dashboard/routes/__init__.py` | MODIFIED | Registered rules_api blueprint |
| `act_dashboard/routes/campaigns.py` | MODIFIED | Imports `load_rules()`, passes `rules_config` to template |
| `act_dashboard/templates/campaigns.html` | MODIFIED | 3-tab structure, inline SVG icons, badge uses `rules_config\|length` |
| `act_dashboard/templates/components/rules_tab.html` | REPLACED | Full M5 card UI with drawer, filters, CRUD JS |

---

## CURRENT STATE OF RULES TAB

### What works
- 13 rule cards across 3 sections: Budget (6) / Bid (4) / Status (3)
- Summary strip with counts per type
- Filter bar: All / Budget / Bid / Status / Blanket only / Campaign-specific only / Active only
- Colour-coded 4px top border per rule type (blue=budget, green=bid, red=status)
- Toggle switches — enable/disable, persists to `rules_config.json`
- Add Rule drawer — 5-step form with live preview
- Edit Rule drawer — pre-fills from card data
- Delete Rule — with confirmation prompt
- Campaign-specific scope — picker populated from `ro.analytics.campaign_daily` via `/api/campaigns-list`
- Card shows campaign ID pill + OVERRIDES BLANKET tag for specific-scoped rules
- Recommendations placeholder tab (Chat 27 scope)
- No Bootstrap Icons CDN dependency — inline SVG only

### Architecture
- **UI config layer:** `rules_config.json` — CRUD via `rules_api.py`
- **Execution layer:** `act_autopilot/rules/*.py` — untouched, Python functions only
- These two layers are intentionally separate. UI edits JSON only, never Python.

---

## WHAT CHAT 27 NEEDS TO KNOW

### Recommendations tab
The Recommendations tab is a placeholder showing "Chat 27 scope — coming soon". It lives in `campaigns.html` as the third tab pane (`#recommendations-tab`). Chat 27 should replace the placeholder content with the actual recommendations UI.

### Rules → Recommendations connection
The rules in `rules_config.json` are the trigger definitions. The Autopilot engine reads `act_autopilot/rules/*.py` (execution layer) to generate recommendations. Chat 27 will need to surface those recommendations in the UI and allow Accept / Decline / Modify actions.

### Campaign name display
The campaign picker stores `campaign_id` in `rules_config.json` (not campaign name). Cards currently display the raw campaign ID in the scope pill. Chat 27 may want to resolve the name for display — query `ro.analytics.campaign_daily` where `campaign_id = ?` to get `campaign_name`.

### Tab badge
The Rules tab badge uses `{{ rules_config|length }}` (from `rules_config.json`). The Recommendations tab badge will need its own count passed from `campaigns.py`.

---

## KNOWN ISSUES

| Issue | Severity | Notes |
|---|---|---|
| Campaign ID shown in scope pill (not name) | Low | Cosmetic only. campaign_id is correct in JSON. Name resolution is Chat 27 scope. |
| `rules_config.json` rule numbering gaps | Low | After deletes, rule numbers are not re-sequenced (budget_7 deleted → next add becomes budget_8). Display names reflect this. Cosmetic only — rule_id is the true identifier. |
| favicon 500 errors in PowerShell | Pre-existing | `404.html` template missing. Unrelated to this chat's work. |
| Client YAML config validation errors | Pre-existing | Config schema mismatch. Unrelated to this chat's work. |

---

## DEPENDENCIES

- `rules_config.json` path: `act_autopilot/rules_config.json` (relative to project root)
- Path resolved in `rules_api.py` as: `Path(__file__).parent.parent.parent / 'act_autopilot' / 'rules_config.json'`
- Campaign picker calls: `GET /api/campaigns-list` → queries `ro.analytics.campaign_daily`
- All CRUD routes require `@login_required`
