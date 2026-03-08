# CHAT 76 HANDOFF — Outreach Slidein Redesign

**Status:** COMPLETE
**Date:** 2026-03-08

---

## What Chat 76 Delivered

Full rebuild of the Outreach slidein panels (Leads, Replies, Sent) to match the approved wireframe. All panels now use a consistent structure with fixed header, scrollable body (Composer → Notes → Thread), and fixed footer.

---

## Files Changed

```
act_dashboard/static/css/outreach-slidein.css  ← NEW
act_dashboard/templates/base_bootstrap.html    ← MODIFIED (fonts + CSS link)
act_dashboard/routes/outreach.py               ← MODIFIED (thread helper, status migration, thread_json)
act_dashboard/templates/outreach/leads.html    ← MODIFIED (si-panel HTML + JS)
act_dashboard/templates/outreach/replies.html  ← MODIFIED (si-panel HTML + JS)
act_dashboard/templates/outreach/sent.html     ← MODIFIED (si-panel HTML + JS)
```

---

## Known Limitations / Next Steps

1. **Composer "Send Reply" on Leads + Sent pages** — shows `showToast('Reply sending coming soon')`. Needs backend endpoint to send reply email from those pages (Replies page already has `/outreach/replies/<id>/send-reply`).

2. **AI Draft button (Replies page)** — shows toast "coming soon". Could integrate with Claude API for draft generation.

3. **Signature toggle** — CSS toggle pip is rendered but not wired to append/remove signature from composer. Wire `siSigPip` click to toggle signature text in textarea.

4. **Quoted text "..." expand** — CSS classes exist (`si-quoted-toggle`, `si-quoted-content`) but no quoted-text parsing is done in `build_thread_by_lead()`. The `email_replies` `body` field may contain quoted original text delimited by `--` or `>` lines; parsing and splitting would make this work.

5. **`build_thread_by_lead` lead_ids type** — passes `str` IDs but DuckDB placeholders expect UUID. Currently working because DuckDB auto-casts; monitor if issues arise.

6. **Notes on Replies page** — reads from `r.notes` (populated via SQL in replies() route). If notes column is NULL for existing records, it shows "No notes yet" correctly.

---

## CSS Class Reference (si-*)

| Class | Use |
|-------|-----|
| `.si-panel` | Root panel container (fixed right, 500px) |
| `.si-overlay` | Dark overlay behind panel |
| `.si-open` | Added to both to show panel |
| `.si-header` | Fixed header section |
| `.si-name`, `.si-email` | Header name + email |
| `.si-badges` | Badge row container |
| `.si-badge-{type}` | Track/status/TZ badge colours |
| `.si-progress` | 6-stage progress bar row |
| `.si-prog-stage.done/.active` | Bar segment states |
| `.si-body` | Scrollable content area |
| `.si-composer` | Reply composer box |
| `.si-notes` | Notes section (amber background) |
| `.si-thread` | Thread section |
| `.si-thread-item.outbound/.inbound` | Thread bubble with left border |
| `.si-thread-badge.sent/.reply-received` | SENT/REPLY badge |
| `.si-footer` | Fixed footer with action buttons |
| `.si-footer-btn.primary/.success/.danger` | Footer button variants |

---

## JS Function Reference (si-*)

| Function | Use | Pages |
|----------|-----|-------|
| `openPanel(id)` | Open slidein for a lead/email | All |
| `closePanel()` | Close slidein | All |
| `siRenderNotes(text)` | Render notes display | All |
| `siStartEditNotes()` | Switch to textarea edit mode | All |
| `siCancelNotes()` | Revert to display mode | All |
| `siSaveNotes()` | PATCH /outreach/leads/<id>/notes | All |
| `siRenderThread(items)` | Build thread from THREAD_DATA[id] | All |
| `siToggleBody(btn, id)` | Expand/collapse long body text | All |
| `siMarkWon()` | Mark lead won via fetch | Leads, Replies, Sent |
| `siMarkLost()` | Mark lead lost via fetch | Leads, Replies, Sent |
| `siSendReply()` | Send reply (wired on Replies page) | All |
| `siBookMeeting()` | Book meeting via fetch | Replies |
| `siQueueFollowup()` | Delegates to queueFollowup() | Sent |
