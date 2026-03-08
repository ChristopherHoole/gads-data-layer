# CHAT 76: SLIDEIN REDESIGN — LEADS, REPLIES, SENT

**Date:** 2026-03-08
**Estimated Time:** 4–6 hours
**Priority:** HIGH
**Dependencies:** Chats 69–75 complete

---

## CONTEXT

The Leads, Replies, and Sent pages each have a slide-out panel. Currently all three are inconsistent — different headers, different layouts, notes in wrong positions, thread order wrong, terminology inconsistent. A full design spec and approved wireframe have been produced. This chat implements that spec across all three pages.

## OBJECTIVE

Rebuild all three slideins to match the approved wireframe and CSS spec exactly.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\outreach-slidein.css` — CREATE
   - All slidein CSS from SLIDEIN_CSS_SPEC.md

2. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\leads.html` — MODIFY
   - Rebuild slidein to match spec

3. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\replies.html` — MODIFY
   - Rebuild slidein to match spec

4. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\sent.html` — MODIFY
   - Rebuild slidein to match spec

5. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\base_bootstrap.html` — MODIFY
   - Add DM Sans + DM Mono Google Fonts import
   - Add outreach-slidein.css link

6. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — MODIFY
   - Leads slidein data: fetch full conversation thread (outbound emails + inbound replies) ordered by timestamp DESC
   - Replies slidein data: same full thread
   - Sent slidein data: same full thread
   - Update any status values: `replied` → `reply_received` in DB queries and inserts
   - Update progress stage labels to: Cold, Queued, Contacted, Reply Received, Meeting, Won

7. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_76_HANDOFF.md` — CREATE
8. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_76_SUMMARY.md` — CREATE

---

## REQUIREMENTS

### Structure (all 3 slideins — identical layout)

```
┌─────────────────────────────┐
│ HEADER (fixed)              │
│  • Lead name · Company      │
│  • Email · GMT offset       │
│  • Badge row                │
│  • Progress bar (6 stages)  │
├─────────────────────────────┤
│ BODY (scrollable)           │
│  ├─ Reply Composer          │
│  ├─ Notes                   │
│  └─ Conversation Thread     │
│     (newest first)          │
├─────────────────────────────┤
│ FOOTER (fixed)              │
│  • Page-specific buttons    │
└─────────────────────────────┘
```

### Reply Composer
- Always at top of body
- Textarea min-height 80px
- Toolbar: B / I / 📎 / Signature toggle / Send reply button
- Replies page only: add 🤖 AI draft button
- Placeholder text includes recipient email on Leads page

### Notes section
- Directly below composer, above thread
- Background: #fffbeb (amber tint)
- Shows current notes text, Edit button
- Empty state: italic "No notes yet — click Edit to add"

### Conversation thread
- ORDER: newest item at top, oldest at bottom (DESC)
- Outbound emails: blue left border (#4285F4), light grey bg (#f8f9fa), "SENT" badge
- Inbound replies: green left border (#34A853), light green bg (#f0fdf4), "REPLY RECEIVED" badge
- Long bodies clamped to 3 lines with "Show more" toggle
- Quoted text in replies: collapsed by default, "··· Show original" expands inline
- Empty state: "No emails yet"

### Thread data requirements
- Each slidein must fetch BOTH outbound emails (from outreach_emails) AND inbound replies (from email_replies) for the lead
- Merge and sort by timestamp DESC before rendering
- Outbound: use sent_at or created_at, subject, body, status
- Inbound: use received_at or created_at, body, sender_name

### Progress bar
- 6 stages: Cold → Queued → Contacted → Reply Received → Meeting → Won
- Done stages: green (#34A853)
- Active stage: blue (#4285F4)
- Future stages: grey (#e5e7eb)
- Stage determined by lead's current status

### Terminology (exact — update everywhere)
- "Replied" → "Reply Received" (all badges, labels, status displays)
- DB status value update: where status='replied' → status='reply_received'
- Verb use only: "Write a reply..." (composer placeholder) — lowercase fine

### Footer buttons per page
- **Leads:** `+ Queue email` (primary blue) · `Edit lead` · `✓ Mark won` (green) · `✕ Mark lost` (danger red) · `Update status`
- **Replies:** `✓ Mark as won` (green) · `📅 Book meeting` · `Update status` · `✕ Mark as lost` (danger red)
- **Sent:** `+ Queue follow-up` (primary blue) · `Update status` · `✓ Mark won` (green) · `✕ Mark lost` (danger red)

### Font
- Import DM Sans + DM Mono from Google Fonts into base_bootstrap.html
- Apply DM Sans as body font, DM Mono for timestamps only
- See SLIDEIN_CSS_SPEC.md for exact import string

### CSS
- All slidein styles go in outreach-slidein.css (new file)
- Use CSS class prefix `si-` for all slidein elements to avoid conflicts
- Full CSS in SLIDEIN_CSS_SPEC.md — follow exactly

---

## CONSTRAINTS

- Do NOT break any existing outreach routes or functionality
- Do NOT change any existing working buttons (mark won, mark lost, book meeting etc) — only restyle them
- Check actual DB column names before writing queries — do not assume
- If status='replied' exists in DB, write a migration to update to 'reply_received' AND update all route references
- outreach-slidein.css must not affect non-outreach pages

---

## SUCCESS CRITERIA

- [ ] All 3 slideins match the approved wireframe (ACT_SLIDEIN_WIREFRAME_v2.html)
- [ ] Header identical across all 3 pages: name, email, badges, progress bar
- [ ] Reply composer always at top of body
- [ ] Notes section directly below composer on all 3 pages
- [ ] Conversation thread shows both outbound and inbound items
- [ ] Thread is newest first
- [ ] Quoted text collapses by default with "··· Show original" toggle
- [ ] "Reply Received" used everywhere (no "Replied" or "Reply" as status label)
- [ ] Progress bar shows correct active stage per lead status
- [ ] DM Sans font applied, DM Mono on timestamps
- [ ] No console errors
- [ ] Flask starts cleanly

---

## REFERENCE FILES

Read these before starting:

- `ACT_SLIDEIN_WIREFRAME_v2.html` — approved visual reference (provided alongside this brief)
- `SLIDEIN_CSS_SPEC.md` — complete CSS spec (provided alongside this brief)
- `SLIDEIN_SPECS.md` — full structural spec (provided alongside this brief)
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\leads.html` — current leads template
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\replies.html` — current replies template
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\sent.html` — current sent template
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — all outreach routes

---

## TESTING

1. Start Flask
2. Open Leads page — click a lead — confirm slidein matches wireframe
3. Confirm composer at top, notes below it, thread below notes
4. Confirm thread is newest first
5. Expand "··· Show original" on a reply — confirm it works
6. Open Replies page — confirm identical header structure and full thread
7. Open Sent page — confirm identical header structure and full thread
8. Confirm DM Sans font rendering (compare to wireframe)
9. Confirm "Reply Received" shown — no "Replied" anywhere
10. No console errors in Flask terminal
11. Report Flask log on startup
