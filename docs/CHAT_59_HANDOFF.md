# Chat 59 — Handoff Notes

## Running the Server

```bash
# From project root
.venv/Scripts/python.exe run_server.py
# OR
python run_server.py  # if .venv is activated
```

Access at: http://localhost:5000
Login: admin / admin123
Outreach: http://localhost:5000/outreach/leads

## Architecture Notes

### DuckDB Connection
Outreach uses a DIRECT duckdb connection (not client-specific):
```python
_WAREHOUSE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "warehouse.duckdb")
)
def get_outreach_db():
    return duckdb.connect(_WAREHOUSE_PATH)
```
This keeps outreach data global (not per-client), which is correct since leads are
managed at the agency level.

### Context Processor
`@bp.app_context_processor inject_outreach_badge_counts` runs on every request
to provide `outreach_queue_count` and `outreach_replies_count` to all templates
for the nav sub-section badges.

### Data Flow
1. Route queries warehouse.duckdb → enriches rows → serialises to JSON strings
2. Template renders JSON as `LEADS_DATA` and `EMAILS_DATA` JS variables
3. All filtering, pagination, panel, modal interactions are client-side JS only

## Stub Routes (future Chats)
Queue, Sent, Replies, Templates, Analytics sub-items are `href="#"` stubs.
Implement as separate blueprints or additional routes on `outreach.bp`.

## Key Files to Know

```
act_dashboard/
  routes/
    outreach.py          # Blueprint, 3 routes, helpers
  templates/
    outreach/
      leads.html         # Full page: stats, filter, table, panel, modal, JS
  static/
    css/
      outreach.css       # All outreach styles incl. nav-sub, status dots, panel
tools/
  generate_outreach_data.py   # Re-run to reset/reseed data
docs/
  wireframes/
    wireframe_leads_v2.html   # Source of truth for UI
```

## Re-seeding Data
```bash
.venv/Scripts/python.exe tools/generate_outreach_data.py
```
This drops and recreates all 4 outreach tables with fresh synthetic data.

## Known Limitations / Next Steps
- PATCH `/outreach/leads/<id>/notes` saves notes to DB but does NOT reload LEADS_DATA in JS; notes are saved server-side but JS panel shows saved state inline
- Add Lead POST adds to DB but page requires manual refresh to show new lead in table (or implement AJAX row insertion)
- Status update buttons (Mark Won, Mark Lost) are UI stubs — need PATCH routes
- Edit Lead is a UI stub — needs a form/modal + PATCH route
- Queue Email button is a stub — will link to Queue feature in future Chat
