# Chat 66 Technical Handoff — Add Client Modal + M9 Live Validation

**Date:** 2026-03-07
**Commits:** `claude/gallant-dewdney` branch (modal) + `main` (YAML + validator fix)

---

## Files Created or Modified

| File | Change |
|------|--------|
| `act_dashboard/templates/settings.html` | Add Client button + modal HTML + JS |
| `act_dashboard/templates/base.html` | `id="nav-client-switcher"` wrapper for hot-reload |
| `act_dashboard/routes/settings.py` | `add_client` route + imports |
| `act_dashboard/app.py` | CSRF exemption for `settings.add_client` |
| `act_dashboard/config_validator.py` | Fixed required fields + valid enum values |
| `configs/client_christopher_hoole.yaml` | New — Christopher Hoole real account |

Full Windows paths: all under `C:\Users\User\Desktop\gads-data-layer\`

---

## Add Client Route

**Endpoint:** `POST /settings/add-client`
**Blueprint:** `settings` (function name: `add_client`)
**File:** `act_dashboard/routes/settings.py`

### Imports Added

```python
from flask import ..., jsonify, current_app
from pathlib import Path
import glob, os, re, yaml
```

### Validation Logic (in order)

1. **client_name** — required, non-empty after `.strip()`
2. **customer_id** — strip hyphens and spaces via `re.sub(r'[-\s]', '', ...)`, then `.isdigit()` check. Allows `125-489-5944` → `1254895944`.
3. **daily_cap / monthly_cap** — cast to `float`, must be > 0
4. **Duplicate customer_id** — loops all `configs/client_*.yaml`, loads each, strips and compares `customer_id`. Returns: `"A client with this Customer ID already exists"`
5. **Duplicate filename** — slug generated from name; checks `os.path.exists(filename)`. Returns: `"A client with this name already exists"`

### Slug Generation

```python
slug = re.sub(r'[^a-z0-9]+', '_', client_name.lower()).strip('_')
filename = f'configs/client_{slug}.yaml'
```

`"Christopher Hoole"` → `client_christopher_hoole.yaml`

### YAML Structure Written

Top-level key order (via `sort_keys=False`):

```
client_name → customer_id → client_type → primary_kpi → google_ads →
targets → conversion_sources → currency → timezone → automation_mode →
risk_tolerance → spend_caps → protected_entities → exclusions → email_alerts
```

**Hardcoded (never from form):**
- `google_ads.mcc_id: '4434379827'`
- `email_alerts`: smtp_host, smtp_port, smtp_user, smtp_password, recipient, daily_summary_time

**conversion_sources.include by client_type:**
- `lead_gen` → `['contact_form']`
- `ecom` → `['purchase']`
- `mixed` → `['contact_form', 'purchase']`

**customer_id** is stored as a Python string. PyYAML quotes all-digit strings automatically, producing `customer_id: '1254895944'` in the output file.

**target_roas / target_cpa** — `None` if field is blank, `float` otherwise. PyYAML writes `None` as `null`.

**Write call:**
```python
with open(filename, 'w') as f:
    yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)
```

### Hot-Reload Mechanism

After writing the YAML, the route rescans `configs/client_*.yaml` and replaces `AVAILABLE_CLIENTS` in the live app config:

```python
new_clients = []
for config_file in sorted(glob.glob('configs/client_*.yaml')):
    with open(config_file) as f:
        cfg = yaml.safe_load(f)
    new_clients.append((cfg.get('client_name', Path(config_file).stem), config_file))
current_app.config['AVAILABLE_CLIENTS'] = new_clients
```

Same pattern as `discover_clients()` in `app.py`. No restart needed.

### JSON Response

```json
// Success
{
  "success": true,
  "client_name": "Christopher Hoole",
  "config_path": "configs/client_christopher_hoole.yaml",
  "all_clients": [["Synthetic_Test_Client", "configs/client_synthetic.yaml"],
                  ["Christopher Hoole", "configs/client_christopher_hoole.yaml"]]
}

// Error
{"success": false, "error": "A client with this Customer ID already exists"}
```

---

## Client Switcher Hot-Reload (JavaScript)

**Location:** `settings.html`, `<script>` block at end of `{% block content %}`

**Anchor in base.html:**
```html
<div id="nav-client-switcher" data-current-config="{{ current_client_config or '' }}">
    {% if available_clients and available_clients|length > 1 %}
    <!-- dropdown -->
    {% else %}
    <span>{{ client_name }}</span>
    {% endif %}
</div>
```

**`updateClientSwitcher(allClients)` function:**
1. Reads `data-current-config` from `#nav-client-switcher` (set by Jinja2 at page load)
2. Finds the active client name by matching config path
3. Rebuilds the full dropdown HTML (button + items) and sets `innerHTML`
4. Handles single→multi transition (the `{% if %}` switch from span to dropdown happens via JS rebuild)

Items use `/switch-client/<index>` URLs where index = position in `all_clients` array.

---

## CSRF Exemption

**Location:** `act_dashboard/app.py`, after Chat 65 block

```python
# Chat 66: CSRF exemption for add-client (JSON API, no CSRF tokens sent)
# POST /settings/add-client is a JSON API called from JavaScript
# Protected by @login_required decorator instead
if 'settings.add_client' in app.view_functions:
    csrf.exempt(app.view_functions['settings.add_client'])
    print("✅ [Chat 66] CSRF exempted: settings.add_client")
else:
    print("⚠️  [Chat 66] Route not found (skipping): settings.add_client")
```

Uses the `if/else` guard pattern (same as Chat 65) because exemptions run post-`register_blueprints`.

---

## Config Validator Changes

**File:** `act_dashboard/config_validator.py`

### Before → After

| Setting | Before | After |
|---------|--------|-------|
| `REQUIRED_FIELDS` | `client_id`, `customer_id`, `db_path` | `customer_id` only |
| `customer_id` lookup | top-level only | top-level OR `google_ads.customer_id` fallback |
| `VALID_CLIENT_TYPES` | no `mixed` | added `mixed` |
| `VALID_AUTOMATION_MODES` | `suggest`, `auto_approve`, `full_auto` | added `insights`, `auto_low_risk`, `auto_expanded` |
| `VALID_RISK_TOLERANCES` | no `balanced` | added `balanced` |
| `db_path` existence check | present | removed |

### Why These Fields Were Wrong

`client_id` and `db_path` are not fields in the `configs/client_*.yaml` schema. They appear to be from an older schema design. The actual required identifier is `customer_id`, which for legacy configs may be nested under `google_ads:` rather than at top level.

### Fallback Logic

```python
value = config.get('customer_id')
if value is None and field == 'customer_id':
    value = (config.get('google_ads') or {}).get('customer_id')
```

Matches `DashboardConfig._get_customer_id()` exactly.

---

## Christopher Hoole YAML

**Path:** `configs/client_christopher_hoole.yaml`

```yaml
client_name: Christopher Hoole
customer_id: '1254895944'          # quoted string — top-level location
client_type: lead_gen
primary_kpi: conversions
google_ads:
  mcc_id: '4434379827'             # real MCC — hardcoded
  customer_id: '1254895944'        # quoted string — nested location
targets:
  target_roas: null
  target_cpa: 5.0
conversion_sources:
  include: [contact_form]          # lead_gen → contact_form
  exclude: []
currency: GBP
timezone: Europe/London
automation_mode: insights          # read-only, no auto-changes
risk_tolerance: conservative
spend_caps:
  daily: 10.0
  monthly: 300.0
protected_entities:
  brand_is_protected: true
  entities: []
exclusions:
  campaign_types_ignore: []
email_alerts:
  enabled: true
  smtp_host: smtp.gmail.com
  smtp_port: 587
  smtp_user: chrishoole101@gmail.com
  smtp_password: ridp widp evgg agjc
  recipient: chrishoole101@gmail.com
  daily_summary_time: 08:00
```

---

## M9 Validation Status

### How M9 Targets the Right Account

`get_current_config()` reads `session["current_client_config"]`. When the user switches to Christopher Hoole, this is set to `configs/client_christopher_hoole.yaml`. `DashboardConfig.customer_id` returns `'1254895944'`. This value is passed directly to all Google Ads API calls.

Confirmed via:
```python
config = DashboardConfig('configs/client_christopher_hoole.yaml')
config.customer_id  # → '1254895944'
```

### Dry-Run Behaviour

`POST /keywords/add-negative` with `dry_run=True`:
```python
if dry_run:
    # Skips Google Ads client loading entirely
    successes = [term.get('search_term', '') for term in search_terms]
    return jsonify({'success': True, 'message': f'Dry-run: Would add {len(successes)} negatives', ...})
```
No API calls made. Safe to test at any time.

### Live Run Behaviour

`dry_run=False` calls `add_negative_keyword()` or `add_adgroup_negative_keyword()` from `act_autopilot.google_ads_api`, then logs to the `changes` table in DuckDB.

### Phase 3 Completion Steps

1. Start server from main repo: `python run_server.py`
2. Log in, switch to "Christopher Hoole" client
3. Go to `/keywords` → Search Terms tab (requires search term data in DuckDB for customer `1254895944`)
4. Select flagged terms → click "Add as Negatives" → confirm dry_run is checked
5. Verify success response, no API errors in logs
6. If dry-run passes: repeat with dry_run unchecked for ONE campaign
7. Verify change appears in `/changes` and in Google Ads account change history

---

## Known Limitations

1. **Search term data** — Keywords page reads from DuckDB. If no search term rows exist for `1254895944`, the tab will be empty. Data must be imported before M9 can run.

2. **YAML `target_roas`** — The user may have set this to `3.0` after the initial creation. The route always writes `null` if the field is blank on the form.

3. **Switcher index stability** — Client switcher URLs use `/switch-client/<index>`. Indices are based on sorted filename order. Adding a new client changes indices of clients that sort after it. This is pre-existing behaviour, not introduced in Chat 66.

4. **Legacy client configs** — `client_001`, `client_001_mcc`, `client_002` appear in the switcher but likely point to non-existent databases. They should be removed when no longer needed.
