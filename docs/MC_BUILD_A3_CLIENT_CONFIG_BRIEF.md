# MC Build A3 — Client Configuration Page
**Session:** MC Build A3 — Client Configuration
**Date:** 2026-04-13
**Objective:** Build the Client Configuration page as a real Flask page with the new ACT v2 sidebar/nav structure. This is the first page in the new layout — every subsequent page will reuse the base template built here.

---

## CONTEXT

Sessions A1 (Schema) and A2 (API Pipeline) are complete:
- 13 `act_v2_*` tables in `warehouse.duckdb`
- 71 settings seeded for Objection Experts (client_id='oe001')
- 6 level states (all 'off')
- 9 negative keyword lists
- 90 days of real Google Ads data from Objection Experts
- 35 checks defined

**This session builds TWO things:**
1. The new base template (sidebar, top bar, client switcher, dark/light toggle) — reused by ALL future pages
2. The Client Configuration page — first page using the new template

**Source of truth:**
- Prototype: `act_dashboard/prototypes/client-config-v3.html` — the exact UI to replicate
- Prototype CSS: `act_dashboard/prototypes/css/client-config-v3.css` and `css/prototype-v7.css`
- Prototype JS: `act_dashboard/prototypes/js/client-config-v3.js`
- Design standards: `docs/ACT_PROTOTYPE_STANDARDS.md`
- Database schema: `docs/ACT_V2_SCHEMA.md`

---

## CRITICAL RULES

1. **Match the prototype EXACTLY.** The prototype `client-config-v3.html` has been through extensive review and is signed off. The Flask page must look identical — same layout, same colours, same interactions.

2. **Build the new nav structure alongside the old one.** The existing Flask app with its old sidebar must continue working. The new ACT v2 pages will use a NEW base template (`base_v2.html`) that doesn't interfere with the old `base_bootstrap.html`.

3. **Read from real database.** All settings displayed on the Client Config page must be read from `act_v2_client_settings`, `act_v2_clients`, `act_v2_client_level_state`, `act_v2_campaign_roles`, and `act_v2_negative_keyword_lists`. No hardcoded values.

4. **Write to real database.** Save button must persist changes to the database. Reset button must restore defaults.

5. **Do NOT modify existing Flask routes, templates, or static files.** Create new files for ACT v2.

6. **DuckDB concurrency:** Flask's development server is single-threaded, so a single DuckDB connection can handle both reads and writes within the same process. Do NOT open multiple connections. Use one connection per request (open at start of request, close at end), or a single shared connection. Check how existing routes handle this. The "stop Flask" rule from A1/A2 only applies to EXTERNAL scripts (migrations, ingestion) — Flask itself can read and write.

7. **Reuse prototype CSS as much as possible.** Copy and adapt the prototype's CSS rather than rewriting from scratch.

---

## TASK 1: Read the Prototype

Before writing any code, read and understand these files thoroughly:

1. `act_dashboard/prototypes/client-config-v3.html` — the complete page HTML
2. `act_dashboard/prototypes/css/prototype-v7.css` — base styles (sidebar, topbar, cards, dark mode)
3. `act_dashboard/prototypes/css/client-config-v3.css` — page-specific styles
4. `act_dashboard/prototypes/js/client-config-v3.js` — interactions (tabs, toggles, validation, save/reset, persona switch, dark mode)
5. `docs/ACT_PROTOTYPE_STANDARDS.md` — all design standards

Also read the existing Flask app to understand patterns:
6. `act_dashboard/app.py` — Flask app factory, blueprint registration
7. `act_dashboard/templates/base_bootstrap.html` — existing base template (to understand what NOT to change)
8. Any existing route file (e.g., `act_dashboard/routes/outreach.py`) — to understand Flask route patterns used in this project

Confirm you understand the prototype structure and the existing Flask patterns.

---

## TASK 2: Create the New Base Template

Create `act_dashboard/templates/v2/base_v2.html` — the new base template for ALL ACT v2 pages.

**This template must include:**

### Sidebar Navigation
Copy the sidebar structure from the prototype (`client-config-v3.html` lines 15-40). The sidebar has:
- ACT brand logo + "Ads Control Tower / Optimization Engine" text
- REVIEW section: Morning Review
- OPTIMIZATION section: Account Level, Campaign Level, Ad Group Level, Keyword Level, Ad Level, Shopping Level
- SETTINGS section: Client Config
- Divider
- Jobs, Outreach, Changes (links to existing pages)

**Navigation links:**
- Client Config → `/v2/config` (the page we're building)
- Morning Review → `/v2/morning-review` (not built yet — link but disable/grey out)
- Account/Campaign/Ad Group/Keyword/Ad/Shopping Level → `/v2/account`, `/v2/campaign`, etc. (not built yet — grey out)
- Jobs → `/outreach/jobs` (existing page)
- Outreach → `/outreach/` (existing page)
- Changes → `/changes` (existing page)

To mark the active nav item, pass an `active_page` variable from the route (e.g., `active_page='config'`) and use `{% if active_page == 'config' %}active{% endif %}` in the base template's nav items. More flexible than a block.

### Top Bar
- Page title: `{% block page_title %}{% endblock %}`
- Client switcher dropdown (reads from `act_v2_clients` — pass client list as template context). When a different client is selected, reload the page with `?client=<id>` query parameter.
- Dark/light mode toggle (animated sun/moon from prototype)
- User avatar "CH"

### Content Area
- `{% block content %}{% endblock %}` — where page content goes
- Correct CSS grid layout: sidebar 220px fixed, content area fills remaining width, top bar 52px fixed

### CSS and JS
- Include Bootstrap 5.3.2 CDN
- Include Material Symbols Outlined font
- Include DM Mono font
- Include the base v2 CSS (copy from `prototype-v7.css` and adapt for Flask static paths)
- Include dark mode CSS variables and toggle logic
- `{% block page_css %}{% endblock %}` for page-specific CSS
- `{% block page_js %}{% endblock %}` for page-specific JS

### File structure:
```
act_dashboard/
  templates/
    v2/
      base_v2.html          ← new base template
      client_config.html    ← Client Config page (extends base_v2)
  static/
    css/
      v2_base.css           ← base styles (from prototype-v7.css)
      v2_client_config.css  ← page styles (from client-config-v3.css)
    js/
      v2_base.js            ← dark mode toggle, client switcher, common interactions
      v2_client_config.js   ← page-specific interactions
```

---

## TASK 3: Create the Client Config Route

Create `act_dashboard/routes/v2_config.py` — a new Flask Blueprint for the Client Config page.

```python
from flask import Blueprint, render_template, request, jsonify
import duckdb

v2_config_bp = Blueprint('v2_config', __name__, url_prefix='/v2')

@v2_config_bp.route('/config')
def client_config():
    """Render the Client Configuration page."""
    # Get client_id from query param, default to 'oe001'
    # e.g., /v2/config?client=oe001
    client_id = request.args.get('client', 'oe001')
    # Read client list from act_v2_clients
    # Read current client's settings from act_v2_client_settings WHERE client_id = client_id
    # Read level states from act_v2_client_level_state
    # Read campaign roles from act_v2_campaign_roles
    # Read negative keyword lists from act_v2_negative_keyword_lists
    # Pass all data to template
    return render_template('v2/client_config.html', ...)

@v2_config_bp.route('/config/save', methods=['POST'])
def save_settings():
    """Save all settings for the current client. Called via AJAX."""
    # JSON body must include 'client_id' plus all settings/levels
    # Update act_v2_client_settings rows (SET updated_at = CURRENT_TIMESTAMP)
    # Update act_v2_clients (persona, target_cpa, target_roas, monthly_budget, updated_at)
    # Update act_v2_client_level_state (updated_at)
    # Return JSON {success: true, saved_at: '13 Apr 2026, 14:30 PM'}

@v2_config_bp.route('/config/reset', methods=['POST'])
def reset_settings():
    """Reset settings to defaults (NOT level states). Called via AJAX."""
    # JSON body must include 'client_id'
    # Delete all act_v2_client_settings WHERE client_id = X
    # Re-insert default values from act_dashboard/db/defaults.py
    # Do NOT reset act_v2_client_level_state (level states are operational, not settings)
    # Do NOT reset act_v2_clients (persona/budget/targets are client-specific)
    # Return JSON {success: true}

```

Note: A `/config/clients` AJAX endpoint is NOT needed — the client list is passed as template context from the main route and rendered server-side in the dropdown. The client switcher navigates to `?client=<id>` which is a full page reload.

**Register the blueprint in `act_dashboard/app.py`:**
Add `from act_dashboard.routes.v2_config import v2_config_bp` and `app.register_blueprint(v2_config_bp)` in the `create_app()` function. Also add CSRF exemption for the JSON API routes.

**Database connection pattern:** Check how existing routes connect to DuckDB (look at `act_dashboard/routes/outreach.py` or similar). Use the same pattern — likely `duckdb.connect('warehouse.duckdb')` with the path derived from the app config.

---

## TASK 4: Build the Client Config Template

Create `act_dashboard/templates/v2/client_config.html` extending `base_v2.html`.

**This template must replicate the prototype `client-config-v3.html` EXACTLY** — same layout, same settings, same tabs, same interactions. The key difference: instead of hardcoded values, all settings are populated from the database via Jinja2 template variables.

### Template variables needed (passed from route):
```python
{
    'client': {id, name, persona, monthly_budget, target_cpa, target_roas, active},
    'clients': [{id, name}, ...],  # for client switcher
    'level_states': {account: 'off', campaign: 'off', ...},
    'settings': {setting_key: {value, type, level}, ...},  # all 71 settings
    'campaign_roles': [{campaign_id, campaign_name, role}, ...],
    'neg_keyword_lists': [{list_id, list_name, word_count, match_type, keyword_count}, ...],
    'last_saved': '6 Apr 2026, 09:15 AM'  # MAX(updated_at) from act_v2_client_settings for this client, or None if never saved
}
```

### Tabs and Settings
Each tab (Account, Campaign, Ad Group, Keyword, Ad, Shopping, Onboarding) should render its settings from the `settings` dict. Use the setting_key to look up the value.

Example Jinja2 for a setting:
```html
<input type="number" class="config-input" 
       value="{{ settings.budget_shift_cooldown_hours.value }}" 
       data-key="budget_shift_cooldown_hours"
       min="1">
```

The `data-key` attribute lets the JavaScript collect all changed values for the save request.

### Save Functionality
The Save button should:
1. Collect all input/select/toggle values from the page
2. Send a POST to `/v2/config/save` with JSON body:
```json
{
    "client_id": "oe001",
    "client": {
        "persona": "lead_gen_cpa",
        "monthly_budget": 1500.00,
        "target_cpa": 25.00,
        "target_roas": null
    },
    "level_states": {
        "account": "off",
        "campaign": "monitor_only",
        "ad_group": "off",
        "keyword": "off",
        "ad": "off",
        "shopping": "off"
    },
    "settings": {
        "budget_shift_cooldown_hours": "72",
        "max_overnight_budget_move_pct": "10",
        ...all 71 settings as key:value pairs...
    }
}
```
3. On success: show toast "Settings saved", update the "Last saved" timestamp, disable the Save button
4. On error: show error toast with the error message from the response

### Reset Functionality
The Reset button should:
1. Show confirmation dialog: "This will reset all settings to defaults. Level states (Off/Monitor/Active) will NOT be changed. Continue?"
2. Send a POST to `/v2/config/reset` with `{client_id: 'oe001'}`
3. On success: reload the page (which will load fresh default values)

Note: Reset only resets `act_v2_client_settings` to defaults. It does NOT reset level states (`act_v2_client_level_state`) — those are operational controls that should only be changed deliberately.

### Level Toggle Functionality
The Off/Monitor Only/Active toggles should:
1. Update visually immediately on click
2. Enable the Save button (changes are pending)
3. On Save, the level states are included in the POST body

### Persona Switcher
When the persona select changes from Lead Gen to Ecommerce (or vice versa):
- Show/hide Target CPA vs Target ROAS fields
- Enable the Save button

---

## TASK 5: Wire Up Static Assets

Copy and adapt CSS/JS from the prototype:

1. **`act_dashboard/static/css/v2_base.css`** — copy from `prototype-v7.css`, update any file paths (fonts, icons should use CDN so no changes needed). This covers: sidebar, topbar, cards, dark mode variables, spacing, typography.

2. **`act_dashboard/static/css/v2_client_config.css`** — copy from `client-config-v3.css`. Covers: tabs, setting rows, input groups, toggles, caps table, checklist, validation messages.

3. **`act_dashboard/static/js/v2_base.js`** — dark mode toggle, client switcher dropdown. Extract from prototype JS.

4. **`act_dashboard/static/js/v2_client_config.js`** — tab switching, persona switcher, scoring weight validation, save/reset AJAX calls, level toggle interactions, setting change detection (enable Save button when something changes). Adapt from prototype JS to use real AJAX instead of mock toasts.

---

## TASK 6: Test Everything

Start the Flask app and test:

1. Navigate to `http://localhost:5000/v2/config`
2. Verify the page loads with real data from the database
3. Verify all 71 settings display correct values from `act_v2_client_settings`
4. Verify level toggles show correct states from `act_v2_client_level_state`
5. Verify campaign roles show in the Onboarding Checklist
6. Verify 9 negative keyword lists show in the Onboarding Checklist
7. Verify tab switching works
8. Verify persona switcher shows/hides CPA vs ROAS fields
9. Verify scoring weights validation (must sum to 100%)
10. Verify Save button is disabled by default, enables on change
11. **Test Save:** Change a setting → click Save → verify the value persists in the database → reload page → verify the new value loads
12. **Test Reset:** Click Reset → confirm → verify defaults are restored
13. Verify dark mode toggle works
14. Verify the OLD Flask pages still work (visit `/outreach/`, `/outreach/jobs`, etc.)
15. Check browser console for errors — must be zero

---

## TASK 7: Document and Commit

1. Update `docs/ACT_PROTOTYPE_STANDARDS.md` — add a section about the Flask v2 template structure
2. Git commit with clear message

---

## DELIVERABLES

1. `act_dashboard/templates/v2/base_v2.html` — new base template
2. `act_dashboard/templates/v2/client_config.html` — Client Config page
3. `act_dashboard/static/css/v2_base.css` — base styles
4. `act_dashboard/static/css/v2_client_config.css` — page styles
5. `act_dashboard/static/js/v2_base.js` — base interactions
6. `act_dashboard/static/js/v2_client_config.js` — page interactions
7. `act_dashboard/routes/v2_config.py` — Flask routes
8. `act_dashboard/db/defaults.py` — shared default settings module
9. Updated `act_dashboard/app.py` — blueprint registered
10. Updated `act_dashboard/db/migrations/seed_objection_experts.py` — imports defaults from shared module
11. All settings read from/written to database
12. Old Flask pages still work
13. Git commit

---

## EXECUTION ORDER

1. Read prototype and existing Flask code (Task 1)
2. Copy and adapt CSS/JS static assets (Task 5) — these must exist before templates reference them
3. Create base template `base_v2.html` (Task 2) — use `{{ url_for('static', filename='css/v2_base.css') }}` for asset paths
4. Create defaults module `act_dashboard/db/defaults.py` — extract 71 defaults from seed script into importable dict
5. Create Flask routes `v2_config.py` (Task 3) — register blueprint, add CSRF exemptions following existing pattern in app.py (see lines ~368-371)
6. Create Client Config template (Task 4) — handle NULL setting values with `{{ settings.key.value or '' }}`
7. Test everything (Task 6) — including Save verification via DB query
8. Document and commit (Task 7)

---

## VERIFICATION CHECKLIST

- [ ] Page loads at `/v2/config` with correct data
- [ ] All 71 settings display values from database
- [ ] Level toggles show correct states
- [ ] Campaign roles and negative keyword lists show in Onboarding
- [ ] Tab switching works (all 7 tabs)
- [ ] Persona switcher toggles CPA/ROAS fields
- [ ] Save persists changes to database (verify: change a value, save, then query `SELECT setting_value FROM act_v2_client_settings WHERE client_id='oe001' AND setting_key='<changed_key>'` to confirm the new value is stored)
- [ ] Reset restores defaults (verify: after reset, query the same setting and confirm it matches the default from `defaults.py`)
- [ ] Dark mode toggle works
- [ ] Save button disabled by default, enabled on change
- [ ] Client switcher dropdown shows all clients
- [ ] Old Flask pages (`/outreach/`, `/outreach/jobs`) still work
- [ ] Zero browser console errors
- [ ] Git commit created

---

## IMPORTANT NOTES

- The prototype HTML/CSS/JS can be COPIED and adapted — don't rewrite from scratch
- The new template uses `/v2/` URL prefix to avoid conflicts with existing routes
- All JSON API routes (`/v2/config/save`, `/v2/config/reset`) need CSRF exemption
- DuckDB read/write within Flask works fine (single process). Only EXTERNAL scripts need Flask stopped.
- The `act_v2_clients` table stores persona, budget, and targets — these are NOT in `act_v2_client_settings`
- When saving, update BOTH `act_v2_clients` (for persona/budget/targets) AND `act_v2_client_settings` (for everything else)
- When saving, set `updated_at = CURRENT_TIMESTAMP` on all updated rows
- **Defaults module:** Extract the 71 default settings from the seed script into a shared module (`act_dashboard/db/defaults.py`). Both the seed script and the reset endpoint should import defaults from this single source. Do NOT duplicate the defaults list in two places.
- **Base CSS scoping:** The `prototype-v7.css` contains styles for the Morning Review page too (approval items, executed actions, monitoring sections). When copying to `v2_base.css`, only include the truly shared styles: sidebar, topbar, typography, dark mode variables, spacing, cards, buttons, toasts, inputs. Leave page-specific styles for page-specific CSS files.
- **Client switcher:** When user selects a different client from the dropdown, the page should navigate to `/v2/config?client=<selected_client_id>`. This is a full page reload, not an AJAX swap.
- **AJAX requests:** The save/reset JS must set `Content-Type: application/json` header and use `JSON.stringify()` for the body. The Flask route reads with `request.get_json()`.
- **Flask `url_for()`:** All CSS/JS/asset references in the base template must use `{{ url_for('static', filename='css/v2_base.css') }}` — NOT hardcoded paths. This is standard Flask practice.
- **NULL settings:** Some settings (like `tcpa_absolute_floor`) have NULL values in the database. The Jinja2 template must handle this: use `{{ settings.key.value or '' }}` or `{{ settings.key.value if settings.key.value is not none else '' }}` to avoid rendering "None" as text.
- **Onboarding Checklist "API connected" item:** Check if `act_v2_snapshots` has any rows for this client. If yes → show as connected. If no → show as pending.
- **CSRF exemption pattern:** Look at `act_dashboard/app.py` around lines 368-371 to see the existing pattern for exempting JSON API routes. Follow the same pattern for `/v2/config/save` and `/v2/config/reset`.

---

**END OF BRIEF**
