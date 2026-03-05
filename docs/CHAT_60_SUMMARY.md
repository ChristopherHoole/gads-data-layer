# Chat 60 — Outreach System: Queue Page

## What Was Built

The email approval queue — a page where every outreach email must be reviewed
and explicitly approved (Send) or rejected (Skip / Discard) before delivery.

### Deliverables

| # | File | Change |
|---|------|--------|
| 1 | `act_dashboard/routes/outreach.py` | 4 new routes + 3 helper functions |
| 2 | `act_dashboard/app.py` | Chat 60 CSRF exemptions (3 queue routes) |
| 3 | `act_dashboard/static/css/outreach.css` | Queue-specific CSS appended |
| 4 | `act_dashboard/templates/outreach/queue.html` | New template (created) |
| 5 | `act_dashboard/templates/base_bootstrap.html` | Queue nav link updated from `#` to `/outreach/queue` |

## Routes Added

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/outreach/queue` | Queue page |
| POST | `/outreach/queue/<email_id>/send` | Approve & mark sent; update lead to `contacted` |
| POST | `/outreach/queue/<email_id>/skip` | Delay by 2 days (scheduled_at + INTERVAL '2 days') |
| POST | `/outreach/queue/<email_id>/discard` | Remove from queue (status = 'discarded') |

## Helper Functions Added (outreach.py)

- `compute_email_type_pill(email_type, sequence_step)` → `(label, css_class)`
- `format_send_time(scheduled_at, timezone)` → `"Fri 6 Mar · 8am EST"`
- `format_schedule_note(scheduled_at, timezone)` → `"Will send Fri 6 Mar at 8am EST (recipient local time)"`

## Features

- **4-stat header row**: Awaiting approval / Scheduled this week / Sent today / Daily limit remaining
- **Expandable cards**: First card auto-expanded; others collapsed. Click header to expand, collapses others
- **Subject bar**: Always visible (even when card is collapsed)
- **Email preview**: To, Subject, formatted body, CV attachment toggle
- **Edit bar**: Edit / Regenerate / Switch template (toast stubs for future Chat)
- **Action row**: Send now · Skip · Discard (with Bootstrap confirm modal for Discard)
- **Sequence badges**: Track badge (Agency/Recruiter/Direct/Job) + email type pill (Initial/Follow-up)
- **Send time badge**: Formatted in recipient's timezone
- **Empty queue state**: Shown when all cards are sent/discarded
- **Live nav badge update**: `updateQueue()` refreshes `.nav-badge` count dynamically

## CSS Classes Added (outreach.css)

`.queue-content`, `.stats-row-4`, `.stat-val-grey`, `.queue-card`, `.queue-card.collapsed`,
`.queue-card-header`, `.queue-number`, `.queue-prospect`, `.queue-card-meta`,
`.email-type-pill`, `.pill-initial`, `.pill-followup`, `.send-time-badge`,
`.queue-subject-bar`, `.subject-label`, `.email-preview`, `.email-body-area`,
`.attachment-badge`, `.attachment-badge.not-attached`, `.edit-bar`, `.edit-bar-btn`,
`.queue-actions`, `.btn-send`, `.btn-skip`, `.btn-discard`, `.send-schedule-note`,
`.queue-header`, `.empty-queue`

## Test Results (Chat 60)

- GET /outreach/queue → 200 ✅
- 3 queued emails rendered (North Star Marketing, Performance Media Inc, Heidrick & Struggles) ✅
- 4-column stats row: awaiting=3 ✅
- First card expanded, 2 collapsed ✅
- pill-initial class on all 3 cards ✅
- Subject bar always visible ✅
- Send / Skip / Discard buttons × 3 ✅
- CV attachment badge + toggle ✅
- Edit bar with 3 stub buttons ✅
- Bootstrap discard confirm modal ✅
- Empty queue state hidden when emails exist ✅
- All 8 JS functions present ✅
- AJAX endpoints correct in all 3 action functions ✅
- Nav Queue link = `/outreach/queue` ✅
- No `<style>` block (CSS-only in outreach.css) ✅
- Queue nav badge updates dynamically via `updateQueue()` ✅
- 46/46 success criteria passed ✅

## Key Schema Notes

- `outreach_emails.email_type` = `'initial'` or `'follow_up'`
- `outreach_leads.sequence_step` = step number (used for Follow-up 1/2/3 pill label)
- DuckDB interval syntax: `INTERVAL '2 days'` (string form, not `INTERVAL 2 DAYS`)
