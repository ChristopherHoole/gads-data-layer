# Chat 60 — Handoff Notes

## Running the Server

```bash
# From project root
.venv/Scripts/python.exe run_server.py
# OR
python run_server.py  # if .venv is activated
```

Access at: http://localhost:5000
Queue page: http://localhost:5000/outreach/queue

## Architecture Notes

### Queue Page Data Flow
1. GET `/outreach/queue` → queries `outreach_emails JOIN outreach_leads WHERE e.status = 'queued'`
2. Builds `stats` dict + `queued_emails` list (with pre-formatted send_time, schedule_note, pill label)
3. Template renders cards with Jinja loop; first card expanded, rest collapsed
4. User clicks Send/Skip/Discard → JavaScript POSTs to respective endpoint
5. On success: JS animates card removal (Send/Discard) or moves to bottom (Skip)
6. `updateQueue()` refreshes heading count, re-numbers circles, updates nav badge

### DuckDB Connection
All outreach routes use `get_outreach_db()` which opens `warehouse.duckdb` read-write.
The database path resolves relative to `outreach.py`:
```
act_dashboard/routes/outreach.py  →  ../../warehouse.duckdb  →  <project_root>/warehouse.duckdb
```

### CSRF Exemptions (app.py)
The 3 POST action routes are AJAX JSON endpoints, exempt from CSRF.
Protected by `@login_required` instead.

```python
queue_routes = [
    'outreach.queue_send',
    'outreach.queue_skip',
    'outreach.queue_discard',
]
```

### Card Collapse Logic
- `.queue-card` = expanded (email-preview, edit-bar, queue-actions visible)
- `.queue-card.collapsed` = only header + subject-bar visible
- CSS hides `.email-preview`, `.edit-bar`, `.queue-actions` when `.collapsed`
- JS `toggleCard()` collapses all, then expands the clicked one

### CV Attachment Toggle
Client-side only. `cvAttached[emailId]` tracks state in JS dict (initialized from Jinja).
Does NOT persist to DB. When Send is clicked, `cv_attached` DB column is NOT updated by
the JS toggle — future Chat should send the attachment state to the send endpoint.

### Send Action: Lead Status Update
On send, the lead's `status` is updated to `'contacted'` and `progress_stage` set to `3`,
but ONLY if the lead's current status is `'cold'` or `'queued'`. Leads already at
higher stages (replied, meeting, won) are not downgraded.

## Key Files

```
act_dashboard/
  routes/
    outreach.py              # All outreach routes incl. 4 queue routes
  templates/
    outreach/
      leads.html             # Leads page (Chat 59)
      queue.html             # Queue page (Chat 60) ← NEW
    base_bootstrap.html      # Nav — Queue link updated
  static/
    css/
      outreach.css           # All outreach styles (Leads + Queue sections)
docs/
  wireframes/
    wireframe_queue.html     # Source of truth for queue UI
```

## Stub Features (future Chats)

- **Edit this email**: button shows toast "coming soon"
- **Regenerate with AI**: button shows toast "coming soon"
- **Switch template**: button shows toast "coming soon"
- **CV attachment toggle**: client-side only, not persisted to DB or sent with email
- **Sent sub-nav**: `href="#"` stub
- **Replies sub-nav**: `href="#"` stub
- **Templates sub-nav**: `href="#"` stub
- **Analytics sub-nav**: `href="#"` stub

## Re-seeding / Resetting Queue Data

To add more queued emails, update `warehouse.duckdb` directly:
```sql
UPDATE outreach_emails SET status = 'queued', scheduled_at = NOW() + INTERVAL '1 hour'
WHERE email_id = '<id>';
```

Or re-run the generator:
```bash
.venv/Scripts/python.exe tools/generate_outreach_data.py
```

## Worktree Notes

When running from a git worktree, `warehouse.duckdb` in the worktree directory
is an empty file (not tracked by git, not copied by `git worktree add`).
Copy from main repo before testing:
```bash
cp warehouse.duckdb .claude/worktrees/<name>/warehouse.duckdb
```
