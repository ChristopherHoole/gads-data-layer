# CHAT 22 BRIEF — M1: Date Picker + Preset Buttons

**Chat:** 22  
**Module:** M1 — Date Range Picker  
**Part of:** Dashboard 3.0 Phase 1  
**Estimated Time:** 90–120 minutes  
**Pilot Page:** Campaigns (`/campaigns`)  
**Rollout Pages:** Dashboard, Ad Groups, Keywords, Ads, Shopping  

---

## MANDATORY FIRST STEPS

Before doing anything else, request these 3 uploads from Christopher:

1. **Codebase ZIP:** `C:\Users\User\Desktop\gads-data-layer`
2. **PROJECT_ROADMAP.md:** `C:\Users\User\Desktop\gads-data-layer\docs\PROJECT_ROADMAP.md`
3. **CHAT_WORKING_RULES.md:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_WORKING_RULES.md`

Do NOT proceed until all 3 are provided.

---

## MANDATORY WORKFLOW CONFIRMATION

After reading the codebase but BEFORE asking your 5 questions, you must post this confirmation:

```
WORKFLOW CONFIRMATION:
✅ Rule 1: I will request current file versions before editing any file
✅ Rule 2: I will use full Windows paths on every file reference
✅ Rule 3: One step at a time — I will complete and test each step before proceeding
✅ Rule 4: I will provide complete files as downloads, never code snippets in chat
✅ Rule 5: I will stop and escalate if going in circles (same error 3+ times)
✅ Pilot first: I will build and fully test on Campaigns before touching any other page
✅ No assumptions: I will request current file versions before editing, even if I just read them from the ZIP
```

Only after posting this confirmation should you ask your 5 questions.

---

## CONTEXT

Dashboard 3.0 is a multi-module overhaul of all dashboard pages. This is Module 1 (M1) — the date picker.

**Current state (what exists now):**
- The navbar (`components/navbar.html`) has a static non-functional date dropdown — it does nothing. It shows "Last 7 days" permanently.
- Each page has its own date buttons (7d/30d/90d) hardcoded inline in the page template, in different positions:
  - Campaigns: below metrics bar, left-aligned
  - Ad Groups: below metrics bar, left-aligned
  - Keywords: below metrics bar, left-aligned (moved there in Chat 21h)
  - Ads: inline filter row, left-aligned
  - Shopping: above tab nav, left-aligned (moved there in Chat 21h)
  - Dashboard: no page-level date buttons (relies on navbar only)
- All routes read `days` from `request.args` (URL parameter `?days=7`)
- No session persistence — selecting 30d on Campaigns doesn't carry to Keywords
- Default varies by page: Campaigns=7, Ad Groups=7, Keywords=7, Ads=30, Shopping=30, Dashboard=7

**Target state (what you're building):**
- Navbar date picker: REMOVED entirely
- New date filter component: top-right of every page, consistent position
- Component contains: Flatpickr custom date range picker + 7d / 30d / 90d preset buttons
- Selection persists globally across all pages via Flask session
- Default: 30d
- Custom range requires "Apply" button to fire
- When custom range is active, preset buttons are all deactivated (none highlighted)

---

## TECHNICAL ARCHITECTURE

### Date Filter Component

Create a new reusable component:
`C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\date_filter.html`

This component renders:
- A Flatpickr date range input (From → To)
- An "Apply" button (fires only when custom range is set)
- Three preset buttons: 7d | 30d | 90d
- Active state highlighting on whichever preset is selected (none highlighted when custom range is active)

The component accepts a Jinja2 variable `active_days` (7, 30, 90, or 0 for custom) and `date_from`, `date_to` for custom ranges.

### Session Storage

Create a new Flask route to handle date selection:
`POST /set-date-range`

This route:
- Accepts `range_type` (7, 30, 90, or 'custom')
- Accepts `date_from` and `date_to` (for custom ranges only)
- Stores selection in Flask session: `session['date_range'] = {'type': '30d', 'days': 30, 'date_from': None, 'date_to': None}`
- Returns JSON `{"success": true}`
- Redirects are handled client-side (JS reloads the current page after session is set)

### Shared Utility Function

Add a helper to `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\shared.py`:

```python
def get_date_range_from_session():
    """
    Returns (days, date_from, date_to) tuple from session.
    days = 7/30/90 for presets, 0 for custom range.
    date_from/date_to = None for presets, date strings for custom.
    Default: 30 days if nothing in session.
    """
```

### Route Changes (all 6 routes)

Each route currently reads `days = request.args.get('days', default, type=int)`.

Change each route to:
1. Call `get_date_range_from_session()` first
2. Fall back to URL param `?days=X` only if session has nothing (backward compatibility)
3. Pass `active_days`, `date_from`, `date_to` to the template

### SQL Query Changes

Current queries use:
```sql
AND snapshot_date >= CURRENT_DATE - INTERVAL '{days} days'
```

For custom date ranges, change to:
```sql
AND snapshot_date >= '{date_from}'
AND snapshot_date <= '{date_to}'
```

All routes need to handle both preset (days integer) and custom (date_from/date_to strings) query modes.

---

## FLATPICKR INTEGRATION

Load Flatpickr from CDN. Add to `base_bootstrap.html` `{% block extra_css %}` and `{% block extra_js %}` — OR load only in the date_filter component itself using inline `<link>` and `<script>` tags (preferred — keeps it self-contained).

Flatpickr CDN:
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
<script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
```

Flatpickr config for date range:
```javascript
flatpickr("#date-range-input", {
    mode: "range",
    dateFormat: "Y-m-d",
    maxDate: "today",
    onChange: function(selectedDates, dateStr) {
        if (selectedDates.length === 2) {
            // Enable Apply button
        }
    }
});
```

---

## STEP-BY-STEP IMPLEMENTATION

Work in this exact order. Complete and test each step before proceeding.

---

### STEP 1: Remove navbar date picker

**File:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\navbar.html`

Remove the entire `<!-- Date Range Picker (Static Placeholder) -->` div block from the navbar. Leave the client selector and user menu intact.

**Test:** Restart server. Confirm navbar no longer shows the date dropdown. All pages load without errors.

---

### STEP 2: Create date_filter component

**File (new):** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\date_filter.html`

Build the component with:
- Flatpickr CSS/JS loaded inline (self-contained)
- Date range input field (triggers Flatpickr calendar)
- Apply button (disabled until both dates selected)
- 7d / 30d / 90d buttons using Bootstrap `btn-group`
- Active button highlighted with `btn-primary`, inactive with `btn-outline-secondary`
- When custom range active: all 3 preset buttons show `btn-outline-secondary` (none active)
- Preset buttons fire `POST /set-date-range` via fetch(), then `location.reload()`
- Apply button fires `POST /set-date-range` with custom dates via fetch(), then `location.reload()`

Component variables it expects:
- `active_days` — integer (7, 30, 90) or 0 for custom
- `date_from` — string or None
- `date_to` — string or None

**Test:** Not yet — needs route changes first.

---

### STEP 3: Add session utility to shared.py

**File:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\shared.py`

Add `get_date_range_from_session()` function as described above. Default return: `(30, None, None)`.

---

### STEP 4: Add /set-date-range route

Add this route to an appropriate place — either `shared.py` blueprint or a new entry in `app.py`. The route must:
- Accept POST with JSON or form data
- Validate inputs
- Store in session
- Return `{"success": true, "days": X}`

---

### STEP 5: Update Campaigns route + template (PILOT)

**Files:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\campaigns.py`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\campaigns.html`

**Route changes:**
- Import `get_date_range_from_session` from shared
- Replace `days = request.args.get('days', 7, type=int)` with session-based lookup
- Update SQL to handle both preset and custom date modes
- Pass `active_days`, `date_from`, `date_to` to template

**Template changes:**
- Remove existing inline date buttons (7d/30d/90d) from wherever they currently sit
- Add `{% include 'components/date_filter.html' %}` in the **top-right of the page header**, inside a `d-flex justify-content-between` row with the page title on the left and the date filter on the right

**Test:**
1. Load `/campaigns` — confirm date filter appears top-right
2. Click 7d → page reloads → data changes → 7d button highlighted
3. Click 30d → page reloads → data changes → 30d button highlighted  
4. Navigate to `/ad-groups` → confirm STILL shows 30d selected (session persisting) 
5. Navigate back to `/campaigns` → still 30d
6. Select custom date range → Apply → data updates → no preset button highlighted
7. Confirm no date picker in navbar

---

### STEPS 6–11: Rollout to remaining pages

Only begin rollout AFTER Campaigns is fully tested and working.

Apply identical changes to each page in this order:

**Step 6:** Dashboard (`dashboard.py` + `dashboard_new.html`)  
**Step 7:** Ad Groups (`ad_groups.py` + `ad_groups.html`)  
**Step 8:** Keywords (`keywords.py` + `keywords_new.html`)  
**Step 9:** Ads (`ads.py` + `ads_new.html`)  
**Step 10:** Shopping (`shopping.py` + `shopping_new.html`)  

For each page:
- Update route to use session-based date range
- Remove existing inline date buttons
- Add `{% include 'components/date_filter.html' %}` top-right of page header
- Test: date filter appears, selection works, session persists across navigation

**Step 11:** Final cross-page session persistence test
- Set 7d on Dashboard → navigate to Campaigns → confirm 7d
- Set 30d on Keywords → navigate to Shopping → confirm 30d
- Set custom range on Campaigns → navigate to Ad Groups → confirm custom range shown

---

## FILES TO CREATE/MODIFY

| # | File | Action |
|---|---|---|
| 1 | `act_dashboard/templates/components/navbar.html` | Remove date picker block |
| 2 | `act_dashboard/templates/components/date_filter.html` | CREATE NEW |
| 3 | `act_dashboard/routes/shared.py` | Add get_date_range_from_session() |
| 4 | `act_dashboard/routes/shared.py` OR `app.py` | Add /set-date-range route |
| 5 | `act_dashboard/routes/campaigns.py` | Update date handling |
| 6 | `act_dashboard/templates/campaigns.html` | Add component, remove old buttons |
| 7 | `act_dashboard/routes/dashboard.py` | Update date handling |
| 8 | `act_dashboard/templates/dashboard_new.html` | Add component, remove old buttons |
| 9 | `act_dashboard/routes/ad_groups.py` | Update date handling |
| 10 | `act_dashboard/templates/ad_groups.html` | Add component, remove old buttons |
| 11 | `act_dashboard/routes/keywords.py` | Update date handling |
| 12 | `act_dashboard/templates/keywords_new.html` | Add component, remove old buttons |
| 13 | `act_dashboard/routes/ads.py` | Update date handling |
| 14 | `act_dashboard/templates/ads_new.html` | Add component, remove old buttons |
| 15 | `act_dashboard/routes/shopping.py` | Update date handling |
| 16 | `act_dashboard/templates/shopping_new.html` | Add component, remove old buttons |

---

## KNOWN GOTCHAS

1. **Database queries use `ro.analytics.*` prefix** — all SQL queries must use `ro.analytics.campaign_daily` not `analytics.campaign_daily`. Check every query you touch.

2. **Custom date range + SQL injection** — never interpolate user-supplied dates directly into SQL strings. Use parameterised queries or validate date format strictly before use.

3. **Shopping page has active_tab** — the shopping route already uses `&tab={{ active_tab }}` to preserve tab on date change. Make sure the new date filter component preserves this for the Shopping page. The component may need to accept an optional `extra_params` variable to append to the reload URL.

4. **ads_new.html whitespace gap** — there is a known pre-existing cosmetic issue in `ads_new.html` (rules_tab outside tab-content). Do NOT fix this in Chat 22 — it is out of scope.

5. **Default days inconsistency** — currently Campaigns/Ad Groups/Keywords default to 7d, while Ads/Shopping default to 30d. After Chat 22, ALL pages default to 30d via session. This is intentional.

6. **Template base** — ALL templates MUST extend `base_bootstrap.html`, not `base.html`. Verify before editing.

---

## TESTING CHECKLIST

Before declaring complete, ALL of the following must pass:

- [ ] Navbar date picker is gone on every page
- [ ] Date filter component appears top-right on all 6 pages
- [ ] 30d is the default on first load (no session set)
- [ ] Clicking 7d highlights 7d button, data updates
- [ ] Clicking 30d highlights 30d button, data updates  
- [ ] Clicking 90d highlights 90d button, data updates
- [ ] Custom range: selecting dates enables Apply button
- [ ] Custom range: clicking Apply updates data, no preset highlighted
- [ ] Session persists: set 30d on Campaigns, navigate to Keywords → still 30d
- [ ] Session persists: set custom range on Campaigns, navigate to Ad Groups → custom range shown
- [ ] Shopping tab preserved: changing date on Shopping Feed Quality tab stays on Feed Quality tab
- [ ] All 6 pages load without errors in PowerShell
- [ ] No regressions on existing page functionality

---

## HANDOFF REQUIREMENTS

On completion, create:
`C:\Users\User\Desktop\gads-data-layer\docs\CHAT_22_HANDOFF.md`

Include:
- All files changed with exact paths
- Any deviations from this brief and why
- Confirmed test checklist results
- Any issues found and how resolved
- Git commit message ready for Master Chat approval

Do NOT create handoff until all tests pass.

---

## SUCCESS CRITERIA

Chat 22 is complete when:
- ✅ Flatpickr date range picker + 7d/30d/90d presets working on all 6 pages
- ✅ Consistent top-right position on every page
- ✅ Global session persistence confirmed across all page combinations
- ✅ Navbar date picker removed
- ✅ Default is 30d
- ✅ Custom range requires Apply button
- ✅ All 13 checklist items pass
- ✅ Handoff doc created and approved by Master Chat
