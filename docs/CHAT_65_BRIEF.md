# CLAUDE CODE BRIEF — Chat 65
# Website Leads → A.C.T Outreach (Google Sheets Sync)

## OBJECTIVE
When someone submits the contact form on christopherhoole.online, the lead gets written to Google Sheets (already working). Build a "Sync from Sheets" feature in A.C.T that pulls new leads from Google Sheets into the Outreach → Leads page.

---

## CONTEXT

### What already exists
- `christopherhoole.online` contact form POSTs to `api/leads.py` on Vercel
- `leads.py` writes successfully to Google Sheet ID: `1zRTPuzwvHDSq23RqJ9iiRaNZ8bSOMmndUzxiP_DW38I`
- Google Sheet columns (in order): Timestamp, Name, Email, Company, Role, Looking For, Phone, IP Address, User Agent, Status
- A.C.T has an existing Outreach → Leads page at `/outreach/leads`
- Leads are stored in `leads` table in `warehouse.duckdb`
- `google-credentials.json` already exists in the project for Sheets access

### Why Option A (Sheets sync) instead of webhook
A.C.T runs locally at `localhost:5000`. Vercel cannot reach it directly. Google Sheets acts as the bridge — Vercel writes to Sheets, A.C.T reads from Sheets.

---

## TASK

### 1. Check leads table schema first
Run against `warehouse.duckdb`:
```sql
DESCRIBE leads;
```
Note exact column names before writing any INSERT.

### 2. Add gspread dependency
Check if `gspread` and `google-auth` are already installed in the venv. If not:
```powershell
pip install gspread google-auth --break-system-packages
```

### 3. New Flask route — `POST /outreach/sync-from-sheets`
Add to `act_dashboard/routes/outreach.py`:

- Authenticate with Google Sheets using `google-credentials.json`
- Open sheet by ID: `1zRTPuzwvHDSq23RqJ9iiRaNZ8bSOMmndUzxiP_DW38I`
- Read all rows from sheet1
- For each row where Status = `'new'`:
  - Check if email already exists in `leads` table (deduplication)
  - If not exists: INSERT into `leads` table
  - Map fields: name, email, company, phone → leads table
  - Set `track = 'Direct'`, `status = 'New'`, `source = 'website'`
- Update sheet row Status from `'new'` to `'imported'` after successful insert
- Return JSON: `{"success": true, "imported": N, "skipped": N}`

### 4. Add "Sync from Sheets" button to Outreach → Leads page
Add to `act_dashboard/templates/outreach/leads.html`:

- Small button in the control bar area — label: "Sync from Sheets"
- On click: POST to `/outreach/sync-from-sheets` via JavaScript fetch
- Show toast on success: "Imported N new leads from website"
- Show toast on error: "Sync failed — check logs"
- Reload the leads table after successful sync (or full page reload is fine)

### 5. Credentials file path
The `google-credentials.json` file is used by `api/leads.py` on Vercel. A copy or symlink needs to be accessible from the A.C.T Flask app. Check if it already exists at:
- `C:\Users\User\Desktop\gads-data-layer\google-credentials.json`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\google-credentials.json`

If neither exists, flag to Christopher — he will need to copy it from:
`C:\Users\User\Desktop\act-website\google-credentials.json`

---

## ALSO NEEDED — Update `leads.py` on website

File: `C:\Users\User\Desktop\act-website\api\leads.py`

The simplified form no longer sends `role` or `looking_for`. Update `write_lead_to_sheet()` to write empty strings for those columns to keep sheet structure intact (columns 5 and 6):

```python
row = [
    timestamp,
    lead_data.get('name', ''),
    lead_data.get('email', ''),
    lead_data.get('company', ''),
    '',   # role — no longer collected, keep column for sheet compatibility
    '',   # looking_for — no longer collected, keep column for sheet compatibility
    lead_data.get('phone', ''),
    ip_address,
    user_agent[:500],
    'new'
]
```

Also fix `ContactForm.tsx` API URL — change hardcoded URL to relative path:
```
const API_URL = '/api/leads';
```
File: `C:\Users\User\Desktop\act-website\components\ContactForm.tsx`

---

## TESTING

### Test the sync:
1. Manually add a test row to the Google Sheet with Status = `'new'`
   - Values: `2026-03-06 12:00:00, Test Lead, test@example.com, Test Co, , , +44123, 127.0.0.1, test-agent, new`
2. Start Flask: `python act_dashboard/app.py`
3. Go to `http://localhost:5000/outreach/leads`
4. Click "Sync from Sheets"
5. Confirm "Test Lead" appears in the leads table
6. Confirm sheet row Status changed from `'new'` to `'imported'`
7. Click "Sync from Sheets" again — confirm no duplicate inserted

### Test deduplication:
- Click sync twice — count should not increase second time

### Test ContactForm fix:
1. Start `npm run dev` in `C:\Users\User\Desktop\act-website`
2. Submit a test form at `localhost:3000`
3. Confirm no error message
4. Confirm new row appears in Google Sheet

---

## DELIVERABLES

1. Updated `act_dashboard/routes/outreach.py` with `/outreach/sync-from-sheets` route
2. Updated `act_dashboard/templates/outreach/leads.html` with Sync button + toast
3. Updated `C:\Users\User\Desktop\act-website\api\leads.py` with blank role/looking_for columns
4. Updated `C:\Users\User\Desktop\act-website\components\ContactForm.tsx` with fixed API URL
5. Test confirmation — lead appears in Outreach → Leads after sync
6. Handoff notes

---

## KEY FILES TO READ FIRST

1. `act_dashboard/routes/outreach.py`
2. `act_dashboard/templates/outreach/leads.html`
3. `C:\Users\User\Desktop\act-website\api\leads.py`
4. Run `DESCRIBE leads;` against `warehouse.duckdb`
