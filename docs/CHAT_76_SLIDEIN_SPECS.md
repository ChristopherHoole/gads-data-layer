# SLIDEIN SPECS — Ads Control Tower Outreach System

**Version:** 1.0
**Date:** 2026-03-08
**Applies to:** Leads, Replies, Sent page slideins

---

## UNIVERSAL RULES (ALL SLIDEINS)

- Width: 500px, fixed right, full viewport height
- Reply composer: ALWAYS at top, always visible
- Conversation thread: below composer, chronological (oldest at top, newest at bottom)
- Quoted original email in replies: collapsed by default, expandable via "..." button (Gmail style)
- Outbound emails shown in thread: right-aligned bubble, blue/grey background
- Inbound replies shown in thread: left-aligned bubble, white/light green background
- Thread scrolls independently of composer and header
- Header is fixed (does not scroll)
- All slideins close via × button top-right

---

## SLIDEIN 1 — LEADS PAGE

### Header (fixed)
- Lead name + company (bold)
- Email address
- Track badge (Agency / Direct / Recruiter / Job)
- Source badge (website / apollo / manual)
- Status dot + label (Cold / Queued / Contacted / Replied / Won / Lost)
- Type score badge (Cold / Warm / Medium / Hot)
- Timezone (GMT+X)
- Progress bar (6 stages: Cold → Queued → Contacted → Replied → Meeting → Won)

### Body (scrollable)
**Section 1 — Reply Composer** (always at top)
- "Write a reply..." textarea
- Formatting buttons: B / I / Attach (paperclip) / + Signature toggle
- Send Reply button (primary blue)

**Section 2 — Conversation Thread**
- All outbound emails + all inbound replies in chronological order
- Each item shows: direction label (Sent / Reply), timestamp, subject (outbound only), body
- Quoted text in replies collapsed by default — "..." expands inline
- Empty state: "No emails yet — queue an email to start the conversation"

**Section 3 — Notes**
- Collapsible section below thread
- Edit button to modify notes inline

### Footer (fixed)
- Queue Email | Edit Lead | Mark Won | Mark Lost | Update Status

---

## SLIDEIN 2 — REPLIES PAGE

### Header (fixed)
- Lead name · company
- Email address · Track badge
- Status dot + label
- Timestamp of latest reply

### Body (scrollable)
**Section 1 — Reply Composer** (always at top)
- "Write a reply..." textarea
- Formatting buttons: B / I / Attach / + Signature / AI draft toggle
- Send Reply button (primary blue)

**Section 2 — Conversation Thread**
- All outbound emails + all inbound replies in chronological order
- Quoted text collapsed by default
- Each reply shows: "Reply" label (green badge), sender name, timestamp, body
- Each outbound shows: "Sent" label (grey badge), timestamp, subject, body

### Footer (fixed)
- Mark as Won | Book Meeting | Update Status | Mark as Lost

---

## SLIDEIN 3 — SENT PAGE

### Header (fixed)
- Lead name · company
- Email address · Track badge
- Status dot + label

### Body (scrollable)
**Section 1 — Reply Composer** (always at top)
- "Write a reply..." textarea
- Same formatting controls as above
- Send Reply button

**Section 2 — Conversation Thread**
- Full thread: all outbound + all inbound chronological
- Quoted text collapsed by default

### Footer (fixed)
- Queue Follow-up | Update Status | Mark Won | Mark Lost

---

## CONVERSATION THREAD — ITEM DESIGN

### Outbound email item
- Alignment: full width
- Header row: grey "SENT" badge (left) + timestamp (right)
- Subject line (bold, smaller font)
- Body text (collapsed to 3 lines if long, "Show more" expands)
- Background: #f8f9fa (light grey)
- Left border: 3px solid #4285F4 (blue)

### Inbound reply item
- Alignment: full width
- Header row: green "REPLY" badge (left) + sender name + timestamp (right)
- Body text
- Quoted original: collapsed "..." button — expands inline
- Background: #f0fdf4 (light green)
- Left border: 3px solid #34A853 (green)

---

## COMPONENT RULES

| Element | Value |
|---------|-------|
| Slidein width | 500px |
| Header padding | 20px |
| Section padding | 16px 20px |
| Composer textarea min-height | 80px |
| Thread item padding | 12px 16px |
| Thread item gap | 8px |
| Badge border-radius | 4px |
| Font family | Arial, sans-serif |
| Body font size | 13px |
| Header name font size | 15px bold |
| Timestamp font size | 11px, color #6b7280 |
| Divider | 1px solid #e5e7eb |

---

## COLOUR PALETTE

| Use | Hex |
|-----|-----|
| Outbound border | #4285F4 (ACT Blue) |
| Inbound border | #34A853 (ACT Green) |
| Outbound bg | #f8f9fa |
| Inbound bg | #f0fdf4 |
| Sent badge bg | #e5e7eb |
| Sent badge text | #374151 |
| Reply badge bg | #dcfce7 |
| Reply badge text | #15803d |
| Composer border | #d1d5db |
| Composer focus border | #4285F4 |
| Footer bg | #ffffff |
| Footer border-top | 1px solid #e5e7eb |
| Slidein overlay | rgba(0,0,0,0.3) |
| Slidein bg | #ffffff |
| Header bg | #ffffff |

---

**Next step:** Wireframe HTML artifact for visual review, then CSS doc for Claude Code.
