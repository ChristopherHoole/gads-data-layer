# CHAT 66 BRIEF — Add Client Modal + M9 Live Validation
**Project:** Ads Control Tower (A.C.T)
**Location:** `C:\Users\User\Desktop\gads-data-layer`
**Date:** 2026-03-07
**Priority:** High
**Estimated Time:** 6-10 hours

---

## OBJECTIVE

Two major deliverables in this chat:

1. **Build "Add Client" modal on the Settings page** — allows new clients to be added to A.C.T via the UI, creating a new YAML config file and immediately appearing in the client switcher without a Flask restart.
2. **Add Christopher's real Google Ads account as the first real client** using the new modal, then run M9 Live Validation (negative keyword blocking) against the real account in dry-run mode first, then live.

---

## BACKGROUND & CONTEXT

### How the client system works
- Flask scans `configs/client_*.yaml` on startup via `discover_clients()` in `act_dashboard/app.py`
- Each YAML file = one client
- `app.config["AVAILABLE_CLIENTS"]` = list of `(client_name, config_path)` tuples
- `app.config["DEFAULT_CLIENT"]` = config_path of first client found
- The client switcher in the nav reads from `AVAILABLE_CLIENTS`
- Currently there is ONE client: `Synthetic_Test_Client` (synthetic/fake data, customer ID `9999999999`)
- Christopher's real Google Ads account is customer ID `1254895944`
- The MCC (manager account) is `4434379827` — already set as `login_customer_id` in `act_dashboard/secrets/google-ads.yaml` — DO NOT CHANGE THIS

### Exact YAML file structure
The existing `configs/client_synthetic.yaml` is the definitive template. All new client YAMLs must include ALL of these fields:

```yaml
client_name: Christopher Hoole
customer_id: '1254895944'
client_type: lead_gen
primary_kpi: conversions
google_ads:
  mcc_id: '4434379827'
  customer_id: '1254895944'
targets:
  target_roas: null
  target_cpa: 5.00
conversion_sources:
  include:
  - contact_form
  exclude: []
currency: GBP
timezone: Europe/London
automation_mode: insights
risk_tolerance: conservative
spend_caps:
  daily: 10.00
  monthly: 300.00
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

**Critical YAML rules:**
- `customer_id` must be quoted string in BOTH locations: top-level AND inside `google_ads` section
- `google_ads.mcc_id` must always be `'4434379827'` — hardcode this, never expose as form field
- `currency: GBP` for UK clients
- `timezone: Europe/London` for UK clients
- `email_alerts` smtp credentials are the same for all clients — hardcode these in the route, do not expose as form fields
- Do not omit any section — even `exclusions` and `conversion_sources` must be present with defaults

### Settings page current state
- `act_dashboard/templates/settings.html` — extends `base.html` (NOT `base_bootstrap.html` — this page predates the Bootstrap migration). Do NOT change the base template.
- `act_dashboard/routes/settings.py` — handles GET/POST for `/settings`
- The Settings page currently edits the ACTIVE client's YAML only
- There is NO "Add Client" button or modal yet

### Key files
- `act_dashboard/app.py` — Flask app factory, `discover_clients()`, CSRF exemptions
- `act_dashboard/routes/settings.py` — settings route
- `act_dashboard/templates/settings.html` — settings template
- `act_dashboard/routes/shared.py` — `get_available_clients()`, `get_current_config()`
- `act_dashboard/config.py` — `DashboardConfig` class with `.save()` method
- `configs/client_synthetic.yaml` — existing client (reference only — do not modify)

---

## PHASE 1: ADD CLIENT MODAL

### 1.1 Settings page changes (`act_dashboard/templates/settings.html`)

Add an "Add Client" button in the page header area next to the `<h1>Settings</h1>` heading. Style consistently with the existing Save Settings button.

Add a modal with the following fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| Client Name | text input | Yes | Used to generate filename slug |
| Customer ID | text input | Yes | Strip hyphens on submit |
| Client Type | select | Yes | ecom / lead_gen / mixed |
| Primary KPI | select | Yes | roas / cpa / conversions |
| Target ROAS | number input | No | Leave blank if not applicable |
| Target CPA | number input | No | Leave blank if not applicable |
| Daily Spend Cap | number input | Yes | |
| Monthly Spend Cap | number input | Yes | |
| Automation Mode | select | Yes | insights / suggest / auto_low_risk / auto_expanded |
| Risk Tolerance | select | Yes | conservative / balanced / aggressive |
| Currency | select | Yes | GBP / USD / EUR — default GBP |
| Timezone | select | Yes | Europe/London / America/New_York / America/Los_Angeles / UTC — default Europe/London |
| Brand Protected | checkbox | No | Default: checked |

Modal behaviour:
- Opens on "Add Client" button click
- Submits via JavaScript fetch POST to `/settings/add-client` as JSON
- On success: show success message, close modal, update client switcher with new client — no page reload
- On error: show error message inside modal, keep modal open

### 1.2 New route (`act_dashboard/routes/settings.py`)

Add: `POST /settings/add-client`

Steps this route must perform:

1. **Parse JSON body** — all fields listed above

2. **Validate:**
   - `client_name` — required, non-empty
   - `customer_id` — strip hyphens, must be numeric only after stripping
   - `daily_cap`, `monthly_cap` — required, positive numbers
   - Check all existing `configs/client_*.yaml` files — if any contain matching `customer_id` → return error: `"A client with this Customer ID already exists"`
   - If generated filename already exists → return error: `"A client with this name already exists"`

3. **Generate slug:** lowercase, spaces → underscores, strip special chars. `"Christopher Hoole"` → `client_christopher_hoole.yaml`

4. **Build full YAML dict** with ALL fields as shown in the template above:
   - Both `customer_id` (top-level) and `google_ads.customer_id` = submitted customer ID
   - `google_ads.mcc_id` = `'4434379827'` (hardcoded)
   - `email_alerts` section hardcoded with Christopher's smtp details
   - `conversion_sources.include` = `['contact_form']` for lead_gen, `['purchase']` for ecom, `['contact_form', 'purchase']` for mixed
   - `currency` and `timezone` from form
   - `targets.target_roas` = null if blank, float if provided
   - `targets.target_cpa` = null if blank, float if provided

5. **Write YAML** to `configs/client_[slug].yaml` using `yaml.dump(data, f, default_flow_style=False, sort_keys=False)`

6. **Hot-reload:** rescan `configs/client_*.yaml`, update `current_app.config["AVAILABLE_CLIENTS"]` in place

7. **Return JSON:**
   - Success: `{"success": true, "client_name": "...", "config_path": "..."}`
   - Error: `{"success": false, "error": "..."}`

### 1.3 CSRF exemption (`act_dashboard/app.py`)

Follow the exact established comment pattern:

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

### 1.4 Client switcher hot-reload

After successful add, JavaScript must update the client switcher dropdown in the nav with the new client without a page reload. Read the base template to understand the current switcher structure and update accordingly.

---

## PHASE 2: ADD CHRISTOPHER'S REAL ACCOUNT

After Phase 1 is built and tested, use the modal to add:

- Client Name: `Christopher Hoole`
- Customer ID: `1254895944`
- Client Type: `Lead Generation`
- Primary KPI: `Conversions`
- Target ROAS: (leave blank)
- Target CPA: `5.00`
- Daily Spend Cap: `10.00`
- Monthly Spend Cap: `300.00`
- Automation Mode: `Insights Only`
- Risk Tolerance: `Conservative`
- Currency: `GBP`
- Timezone: `Europe/London`
- Brand Protected: checked

Verify after submission:
- `configs/client_christopher_hoole.yaml` created with ALL fields
- Both `customer_id` and `google_ads.customer_id` = `'1254895944'`
- `google_ads.mcc_id` = `'4434379827'`
- `currency: GBP`, `timezone: Europe/London`
- `email_alerts` section present
- Client appears in switcher immediately
- Settings page shows correct values when switched to this client
- `Synthetic_Test_Client` still works when switched back

---

## PHASE 3: M9 DRY-RUN VALIDATION

### Background
M9 was built in Chat 30b. The negative keyword blocking execution code is somewhere in `act_dashboard/routes/` — Claude Code must locate the exact file. It uses `get_google_ads_client()` from `act_dashboard/routes/shared.py` which loads credentials from `act_dashboard/secrets/google-ads.yaml`.

`google-ads.yaml` contains:
- `login_customer_id: 4434379827` (MCC — DO NOT CHANGE)
- Real API credentials — correct as-is, do not modify

The `customer_id` for API calls comes from the active client's YAML. Switching to `Christopher Hoole` client targets `1254895944`.

### Steps

1. **Confirm correct customer ID targeted:**
   Trace through code: `get_current_config()` → `config.customer_id` → passed to Google Ads API. Verify `1254895944` not `9999999999`.

2. **Dry-run negative keyword blocking:**
   - Navigate to `http://localhost:5000/keywords` → Search Terms tab
   - Confirm `dry_run=True` is the default
   - Trigger negative keyword analysis
   - Verify completes without API errors
   - Verify NO live changes made to Google Ads account
   - Confirm logs show customer ID `1254895944`

3. **Stop immediately if any of these errors occur:**
   - `CUSTOMER_NOT_FOUND`
   - `PERMISSION_DENIED`
   - `DEVELOPER_TOKEN_NOT_APPROVED`
   - Any other Google Ads API error
   - Report full error to Master Chat. Do NOT attempt workarounds.

4. **Only if dry-run succeeds with zero errors:**
   - Run ONE live execution on a single campaign
   - Verify change in Changes table at `http://localhost:5000/changes`
   - Verify change in Google Ads account `1254895944` change history

### Safety rules
- Dry-run FIRST — always
- Stop on any API error — no workarounds
- Do not modify `google-ads.yaml`
- `login_customer_id` stays `4434379827`
- Maximum one live change for initial validation

---

## TESTING CHECKLIST

**Phase 1 — Add Client Modal:**
- [ ] "Add Client" button visible on Settings page
- [ ] Modal opens on button click
- [ ] All fields present with correct types, options, defaults
- [ ] Validation: empty client name → error
- [ ] Validation: non-numeric customer ID → error
- [ ] Validation: duplicate customer ID → error
- [ ] Validation: duplicate client name → error
- [ ] Successful submit creates `configs/client_[slug].yaml`
- [ ] YAML contains ALL fields (google_ads, conversion_sources, currency, timezone, exclusions, email_alerts)
- [ ] Both customer_id locations populated correctly
- [ ] New client in switcher immediately (no restart)
- [ ] CSRF exemption in `app.py`
- [ ] Synthetic client still works

**Phase 2 — Christopher's Account:**
- [ ] `configs/client_christopher_hoole.yaml` exists with all fields correct
- [ ] `customer_id` quoted string in both locations
- [ ] `currency: GBP`, `timezone: Europe/London`
- [ ] Client in switcher without restart
- [ ] Settings page correct when switched to this client
- [ ] Synthetic client still works

**Phase 3 — M9 Validation:**
- [ ] Dry-run targets `1254895944` confirmed in logs
- [ ] Dry-run completes without API errors
- [ ] Results display in dashboard
- [ ] If live run: change in Changes table

---

## KNOWN PITFALLS

1. **Never edit `act_dashboard/secrets/google-ads.yaml`**
2. **`customer_id` must be quoted string** in both YAML locations
3. **YAML must include ALL fields** — use `client_synthetic.yaml` as the complete template
4. **Settings page extends `base.html`** — do not change to `base_bootstrap.html`
5. **Route decorator immediately adjacent to function** — no helpers between decorator and def
6. **CSRF exemption goes in `app.py`** — not the route file
7. **Hot-reload updates `current_app.config["AVAILABLE_CLIENTS"]` in place**
8. **Strip hyphens from customer ID input** — `125-489-5944` → `1254895944`
9. **`google_ads.mcc_id` is hardcoded `4434379827`** — never a form field
10. **`email_alerts` smtp details are hardcoded** — never form fields

---

## DELIVERABLES

1. Updated `act_dashboard/templates/settings.html`
2. Updated `act_dashboard/routes/settings.py`
3. Updated `act_dashboard/app.py`
4. `configs/client_christopher_hoole.yaml` created via modal, all fields correct
5. M9 dry-run confirmed against `1254895944` with no API errors
6. Git commit: `"Chat 66: Add Client modal + Christopher Hoole account + M9 live validation"`

---

## FULL WINDOWS FILE PATHS

- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\settings.py`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\settings.html`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\shared.py`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\config.py`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\secrets\google-ads.yaml` (read only — do not modify)
- `C:\Users\User\Desktop\gads-data-layer\configs\client_synthetic.yaml` (reference only — do not modify)
- `C:\Users\User\Desktop\gads-data-layer\configs\client_christopher_hoole.yaml` (to be created)

---

## DOCUMENTATION (MANDATORY — DO NOT SKIP)

After all phases are complete and tested, Claude Code MUST produce two documents and save them to `C:\Users\User\Desktop\gads-data-layer\docs\`:

### 1. Executive Summary — `CHAT_66_SUMMARY.md`

Short, non-technical summary covering:
- What was built and why
- The 3 phases and what each delivered
- Any issues encountered and how they were resolved
- Current state after this chat

### 2. Technical Handoff — `CHAT_66_HANDOFF.md`

Detailed technical document covering:
- All files created or modified (full Windows paths)
- The Add Client route — how it works, validation logic, YAML generation, hot-reload mechanism
- The exact YAML structure written for new clients
- How `AVAILABLE_CLIENTS` hot-reload works in `app.py`
- CSRF exemption added and why
- M9 validation results — customer ID confirmed, dry-run output, live run result (if performed)
- Any deviations from the brief and why
- Known limitations or follow-up items

Both files must be committed as part of the final git commit.

---

**Version:** 1.2 | **Created:** 2026-03-07 | **Chat:** 66
