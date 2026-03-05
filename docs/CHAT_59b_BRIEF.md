# CHAT 59b: OUTREACH LEADS — BUG FIXES

**Estimated Time:** 2-3 hours  
**Priority:** HIGH  
**Dependencies:** Chat 59 complete ✅  
**Location:** `C:\Users\User\Desktop\gads-data-layer`

---

## OBJECTIVE

Fix 7 specific issues on the Outreach Leads page. Two files only: `outreach.py` and `leads.html`. Nothing else is in scope.

---

## FIXES REQUIRED

### FIX 1 — Status column shows no dots or labels

**Problem:** The Status column in the table is empty. No dot, no label visible on any row.

**Expected:** Each row should show a coloured dot on the left of the Status cell with a text label next to it.

Status dot colours and labels:
- `cold` → grey `#9aa0a6` · "Cold"
- `queued` → blue `#1a73e8` · "Queued"
- `contacted` → blue `#1a73e8` · "Contacted"
- `followed_up` → yellow `#f9ab00` · "Followed Up"
- `replied` → green `#34a853` · "Replied"
- `meeting` → green `#34a853` · "Meeting"
- `won` → dark green `#137333` · "Won"
- `lost` → red `#ea4335` · "Lost"
- `no_reply` → grey `#9aa0a6` · "No Reply"

---

### FIX 2 — Country column shows "GB UK", "US USA" etc.

**Problem:** Country displays a 2-letter code prefix before the country name (e.g. "GB UK", "US USA", "AE UAE").

**Expected:** Country name only — "UK", "USA", "UAE", "Canada", "Australia". No code prefix. No flag emoji.

Fix wherever the country value is being rendered — either in the route or the template.

---

### FIX 3 — Actions dropdown has "Add lead" item

**Problem:** The Actions dropdown on each table row contains an "Add lead" option. This makes no sense contextually — you're already on a row for an existing lead.

**Expected:** Remove "Add lead" from the Actions dropdown entirely. It should not appear there.

---

### FIX 4 — Mark won / Mark lost are placeholder toasts

**Problem:** Clicking "Mark won" or "Mark lost" in the Actions dropdown shows a toast saying "Status update coming soon" instead of actually updating the lead.

**Expected:**
- Mark won → update `outreach_leads.status = 'won'` and `progress_stage = 8` for that lead_id in the database. Show success toast "Lead marked as won". Refresh the row in the table (or reload page).
- Mark lost → update `outreach_leads.status = 'lost'` and `progress_stage = 8` for that lead_id. Show success toast "Lead marked as lost". Refresh.

Same behaviour for the Mark won / Mark lost buttons inside the slide panel.

Add routes to `outreach.py`:
```
POST /outreach/leads/<lead_id>/mark-won
POST /outreach/leads/<lead_id>/mark-lost
```

Both return JSON `{"success": true}`. Add CSRF exemptions in `app.py` for both.

---

### FIX 5 — Update status is a placeholder toast

**Problem:** Clicking "Update status" in the Actions dropdown shows a toast "Status update coming soon".

**Expected:** Opens a small modal or inline dropdown letting the user pick a new status from the full list, then saves it to the database.

Implement as a simple modal with a select dropdown containing all status values:
- Cold · Queued · Contacted · Followed Up · Replied · Meeting · Won · Lost · No Reply

On save: update `outreach_leads.status` (and set `progress_stage` appropriately — see mapping below) for that lead_id. Show success toast "Status updated". Close modal. Refresh row.

Progress stage mapping:
- cold → 1
- queued → 2
- contacted → 3
- followed_up → 4
- replied → 6
- meeting → 7
- won → 8
- lost → 8
- no_reply → 5

Same behaviour for the Update status button inside the slide panel.

Add route to `outreach.py`:
```
POST /outreach/leads/<lead_id>/update-status
```
Accepts JSON body `{"status": "replied"}`. Returns `{"success": true}`. Add CSRF exemption in `app.py`.

---

### FIX 6 — Delete is a placeholder toast

**Problem:** Clicking "Delete" in the Actions dropdown shows a toast "Delete coming soon".

**Expected:** Shows a confirmation dialog ("Are you sure you want to delete this lead? This cannot be undone.") with Cancel and Delete buttons. On confirm: deletes the row from `outreach_leads` and any associated rows in `outreach_emails` and `outreach_tracking_events`. Removes the row from the table without full page reload. Shows success toast "Lead deleted".

Add route to `outreach.py`:
```
POST /outreach/leads/<lead_id>/delete
```
Returns `{"success": true}`. Add CSRF exemption in `app.py`.

Use a Bootstrap modal for the confirmation dialog — not a browser `confirm()` dialog.

---

## FILES TO MODIFY

| File | Changes |
|------|---------|
| `act_dashboard/templates/outreach/leads.html` | Fixes 1, 2, 3 — template rendering + status modal + delete confirm modal |
| `act_dashboard/routes/outreach.py` | Fixes 4, 5, 6 — new routes for mark-won, mark-lost, update-status, delete |
| `act_dashboard/app.py` | CSRF exemptions for new routes |

No other files. Do not touch any other outreach files or dashboard files.

---

## TECHNICAL CONSTRAINTS

- Bootstrap 5 only — no jQuery
- No inline styles — all styles already in `outreach.css`. If new styles are needed, add them to `outreach.css`
- CSRF exemptions required for all new POST routes — follow existing pattern in `app.py` lines 186-191
- Delete must cascade — remove from `outreach_emails` and `outreach_tracking_events` as well as `outreach_leads`
- Row refresh after status changes: simplest acceptable approach is `location.reload()` after success response — no need for complex DOM manipulation

---

## SUCCESS CRITERIA

- [ ] Status column shows coloured dot + label on every row
- [ ] Status dot colours match spec (cold=grey, queued/contacted=blue, followed_up=yellow, replied/meeting=green, won=dark green, lost=red, no_reply=grey)
- [ ] Country column shows "UK", "USA", "UAE", "Canada", "Australia" — no code prefix
- [ ] "Add lead" item removed from Actions dropdown
- [ ] Mark won updates database, shows success toast, refreshes table
- [ ] Mark lost updates database, shows success toast, refreshes table
- [ ] Mark won / Mark lost in slide panel also work correctly
- [ ] Update status opens modal with all 9 status options
- [ ] Update status saves to database, updates progress_stage, shows success toast, refreshes table
- [ ] Update status in slide panel also works correctly
- [ ] Delete shows Bootstrap confirm modal (not browser confirm)
- [ ] Delete removes lead from database (cascade delete), removes row from table, shows success toast
- [ ] Zero console errors after all fixes
- [ ] Page loads under 3 seconds

**All criteria must pass before this chat is marked complete.**

---

## TESTING PROTOCOL

1. Fresh PowerShell session
2. `cd C:\Users\User\Desktop\gads-data-layer`
3. `.\.venv\Scripts\Activate.ps1`
4. `python act_dashboard/app.py`
5. Open Opera → `http://localhost:5000/outreach/leads`
6. F12 → Console — zero errors
7. Test each fix systematically

---

## CHECKPOINTS

1. ✅ Fix 1 + 2 + 3 complete — visual fixes, status dots showing, country correct, Add lead removed
2. ✅ Fix 4 complete — Mark won/lost working in table and slide panel
3. ✅ Fix 5 complete — Update status modal working
4. ✅ Fix 6 complete — Delete confirm modal working, cascade delete confirmed

---

## REFERENCE FILES

- `act_dashboard/templates/outreach/leads.html` — request current version before editing
- `act_dashboard/routes/outreach.py` — request current version before editing
- `act_dashboard/app.py` — check CSRF exempt list pattern before modifying
- `act_dashboard/static/css/outreach.css` — add any new styles here only
