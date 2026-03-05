# CHAT 60: OUTREACH SYSTEM — QUEUE PAGE

**Estimated Time:** 4-5 hours  
**Priority:** HIGH  
**Dependencies:** Chat 59 complete ✅  
**Location:** `C:\Users\User\Desktop\gads-data-layer`

---

## OBJECTIVE

Build the Queue page for the outreach system. This page shows emails awaiting approval before sending. One page, fully complete and tested.

---

## WIREFRAME

`C:\Users\User\Desktop\gads-data-layer\docs\wireframes\wireframe_queue.html`

Read this file in full before writing a single line of code. It is the source of truth for every layout, interaction, colour, and spacing decision.

---

## DELIVERABLES

| File | Action |
|------|--------|
| `act_dashboard/routes/outreach.py` | Add queue routes |
| `act_dashboard/templates/outreach/queue.html` | Create queue template |
| `act_dashboard/static/css/outreach.css` | Add any missing queue styles |
| `act_dashboard/app.py` | CSRF exemptions for new routes |
| `docs/CHAT_60_SUMMARY.md` | Summary doc |
| `docs/CHAT_60_HANDOFF.md` | Technical handoff |

No other files. Do not touch the leads page, leads route, or any other dashboard files.

---

## BUILD ORDER

---

### STEP 1 — Queue data check

Before building anything, query `warehouse.duckdb` and confirm how many rows exist in `outreach_emails` with `status = 'queued'`. Report the count.

If count is 0 or too low to demonstrate the page properly (need at least 3), update the `generate_outreach_data.py` script to ensure at least 3 queued emails exist with realistic data and re-run it.

---

### STEP 2 — Queue routes

Add to `act_dashboard/routes/outreach.py`:

**GET `/outreach/queue`**

Query `warehouse.duckdb` for all emails where `status = 'queued'`. Join with `outreach_leads` to get company, contact name, role, email address, city_state, country, track, timezone. Order by `scheduled_at ASC`.

Pass to template:
- `queued_emails` — list of queued email dicts
- `stats` — dict with: `awaiting` (count of queued), `scheduled_this_week` (count scheduled in next 7 days), `sent_today` (count sent today), `daily_limit_remaining` (hardcoded 50 minus sent today)

**POST `/outreach/queue/<email_id>/send`**

Update `outreach_emails SET status = 'sent', sent_at = NOW()` for that email_id. Also update `outreach_leads SET status = 'contacted', progress_stage = 3, last_activity = NOW()` for the associated lead (if lead currently has status 'cold' or 'queued' — do not downgrade status if already higher). Return `{"success": true}`.

**POST `/outreach/queue/<email_id>/skip`**

Update `outreach_emails SET scheduled_at = scheduled_at + INTERVAL 2 DAYS` for that email_id. Return `{"success": true}`. (Moves it to the back of the queue by bumping the scheduled date.)

**POST `/outreach/queue/<email_id>/discard`**

Update `outreach_emails SET status = 'discarded'` for that email_id. Return `{"success": true}`.

Add CSRF exemptions for all three POST routes in `app.py`.

---

### STEP 3 — Queue template

Create `act_dashboard/templates/outreach/queue.html`. Extend `base_bootstrap.html`. Link `outreach.css`. No inline styles. No `<style>` block.

#### Top navbar
- Left: "Outreach — Queue"
- Right: client selector only (no Add Lead button on this page)

#### Stats row — 4 cards

| Icon | Value | Label |
|------|-------|-------|
| pending | awaiting count | Awaiting approval |
| schedule | scheduled_this_week | Scheduled this week |
| send | sent_today | Sent today |
| block | daily_limit_remaining | Daily limit remaining |

Daily limit remaining value: grey colour `#5f6368` (not black). Match wireframe.

#### Queue header

```
X emails awaiting your approval
Review each email before it sends. Click Send to approve, Skip to delay by one cycle, or Discard to remove.
```

X is the live count. Updates as cards are sent/discarded.

#### Queue cards

One card per queued email. First card expanded, all others collapsed.

**Card structure (per wireframe exactly):**

**Card header** (always visible, click to expand/collapse):
- Left: numbered circle (blue `#1a73e8` when expanded, grey `#5f6368` when collapsed) + company name bold + contact name grey + sub-line with email address · city/state · country
- Right: track badge + email type pill (Initial email = blue, Follow-up 1/2/3 = orange) + send time badge (clock icon + "Tue 11 Mar · 8:30am EST")

Email type pill label logic:
- `sequence_step = 1` → "Initial email" (blue pill)
- `sequence_step = 2` → "Follow-up 1" (orange pill)
- `sequence_step = 3` → "Follow-up 2" (orange pill)
- `sequence_step = 4` → "Follow-up 3" (orange pill)

Send time display: format `scheduled_at` as "Tue 11 Mar · 8:30am [TZ]" where TZ is the timezone abbreviation (EST, CST, GMT, etc.) derived from the lead's `timezone` field.

**Subject bar** (always visible even when collapsed):
- Grey "SUBJECT" label + email subject text

**Email preview area** (hidden when collapsed):
- To field: recipient email address (blue)
- Subject field: email subject
- Email body: scrollable area, max-height 220px, `white-space: pre-line`
- CV attachment badge: shows "Christopher_Hoole_CV.pdf · attached ✕" in blue. Clicking toggles to "not attached +" in grey. This controls whether `cv_attached` is true/false when sending. Clicking toggles state visually and updates a local JS variable — no server call needed until Send is clicked.

**Edit bar** (hidden when collapsed):
- ✏ Edit this email — placeholder, show toast "Email editor coming soon"
- 🔄 Regenerate with AI — placeholder, show toast "AI regeneration coming soon"  
- 📋 Switch template — placeholder, show toast "Template switcher coming soon"

**Action row** (hidden when collapsed):
- Send now button (blue) — POSTs to `/outreach/queue/<email_id>/send`, animates card out, opens next card, updates counts
- Skip button (grey outline) — POSTs to `/outreach/queue/<email_id>/skip`, moves card to bottom of list visually, updates numbering
- Schedule note: ℹ "Will send [date] at 8:30am [TZ] (recipient local time)"
- Discard button (red outline, right-aligned) — shows Bootstrap confirm modal ("Remove this email from the queue? This cannot be undone."), on confirm POSTs to `/outreach/queue/<email_id>/discard`, animates card out, updates counts

**Card animations:**
- Sending or discarding: fade out + collapse height to 0 + remove from DOM (match wireframe JS pattern)
- Next collapsed card automatically expands after current card is removed

**Collapsed state:**
- Only header + subject bar visible
- Click anywhere on header to expand
- Only one card expanded at a time

#### Empty queue state

When all cards are sent/discarded, show:
```
[inbox icon large grey]
Queue is empty
All emails have been sent or discarded. Add more leads to generate new emails.
```

White card, centred, matches wireframe `.empty-queue` styles.

#### Card numbering

Cards are numbered 1, 2, 3... in order. After send/discard/skip, numbers update dynamically in JavaScript.

---

## JAVASCRIPT BEHAVIOUR

All card interactions are client-side JavaScript (no page reload). AJAX POST calls for send/skip/discard.

Key functions to implement (follow wireframe JS closely):
- `toggleCard(id)` — expand one, collapse all others, update number circle colours
- `sendCard(id)` — POST to send route, animate out, auto-expand next
- `skipCard(id)` — POST to skip route, move card to bottom of DOM, re-number, auto-expand next
- `discardCard(id)` — show confirm modal, POST to discard route, animate out, auto-expand next
- `removeCard(id, callback)` — fade + collapse height animation, then remove from DOM
- `updateQueue()` — update header count, nav badge count, stat card count, re-number circles
- `toggleAttachment(id)` — toggle CV attached state visually

On page load: auto-expand first card.

---

## TECHNICAL CONSTRAINTS

- Bootstrap 5 only — no jQuery
- Extend `base_bootstrap.html` — never `base.html`
- Link `outreach.css` — no inline styles, no `<style>` block
- All queue styles go into `outreach.css` (extract from wireframe)
- Content area max-width: 900px (narrower than leads page — match wireframe)
- CSRF exemptions required for all three POST routes
- Discard confirm: Bootstrap modal, not browser `confirm()`

---

## SUCCESS CRITERIA

- [ ] `/outreach/queue` loads HTTP 200, zero console errors
- [ ] Stats row shows 4 cards with correct values
- [ ] Queue header shows correct count
- [ ] At least 3 queue cards visible
- [ ] First card expanded on page load, others collapsed
- [ ] Card header shows company, contact, email, city, track badge, email type pill, send time
- [ ] Subject bar visible on collapsed and expanded cards
- [ ] Email body visible when expanded, hidden when collapsed
- [ ] CV attachment badge toggles between attached/not attached
- [ ] Edit/Regenerate/Switch template show placeholder toasts
- [ ] Send now POSTs, animates card out, next card expands, counts update
- [ ] Skip POSTs, moves card to bottom, re-numbers, next card expands
- [ ] Discard shows Bootstrap confirm modal, on confirm POSTs, animates out, counts update
- [ ] Nav Queue badge count updates after send/discard
- [ ] Empty queue state shows when all cards removed
- [ ] Queue active in nav sub-items
- [ ] Page loads under 3 seconds

**All criteria must pass before this chat is marked complete.**

---

## TESTING PROTOCOL

1. Fresh PowerShell session
2. `cd C:\Users\User\Desktop\gads-data-layer`
3. `.\.venv\Scripts\Activate.ps1`
4. `python act_dashboard/app.py`
5. Open Opera → `http://localhost:5000/outreach/queue`
6. F12 → Console — zero errors
7. Test each success criterion

---

## CHECKPOINTS

1. ✅ Data confirmed — at least 3 queued emails in database
2. ✅ Routes added — GET queue, POST send/skip/discard all returning correct responses
3. ✅ Template complete — all visual elements matching wireframe
4. ✅ All interactions working — send, skip, discard, toggle, animations, empty state

---

## REFERENCE FILES

Read before starting:
- `C:\Users\User\Desktop\gads-data-layer\docs\wireframes\wireframe_queue.html` — approved wireframe
- `act_dashboard/routes/outreach.py` — existing routes (request current version before editing)
- `act_dashboard/templates/outreach/leads.html` — existing outreach template pattern
- `act_dashboard/static/css/outreach.css` — existing outreach styles (request current version before editing)
- `act_dashboard/app.py` — CSRF exempt list (request current version before editing)

---

## DOCUMENTATION

**`docs/CHAT_60_SUMMARY.md`:** What was built, files modified, testing results, issues and fixes.

**`docs/CHAT_60_HANDOFF.md`:** Route map, JS architecture, send/skip/discard logic, database updates per action, git commit strategy.
