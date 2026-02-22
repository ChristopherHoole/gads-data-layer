# CHAT 28 BRIEF — M7: Accept / Decline / Modify Wiring

**Date:** 2026-02-22
**Status:** Ready to start
**Depends on:** Chat 27 (M6) — COMPLETE ✅ commit 86b20ec

---

## ⚠️ MANDATORY WORKFLOW — READ BEFORE DOING ANYTHING

This chat follows the 15-step worker chat process. Steps must not be skipped.

**YOU ARE AT STEP 3.**

Steps 1 and 2 are already complete:
- ✅ Step 1: Master has written this brief
- ✅ Step 2: Brief + all project docs + codebase ZIP have been uploaded to this chat

**Your next actions (Steps 3–4):**
1. Read this brief AND all uploaded documents thoroughly
2. Produce exactly **5 clarifying questions** — specific, not vague
3. **STOP. Do not write any code or build plan yet.**
4. Send the 5 questions to Christopher so he can take them to Master Chat for answers

After Master Chat answers (Step 5), you will:
- Step 6: Write a detailed build plan and send to Master for review
- Step 7: Wait for Master approval before touching any code
- Step 8: Begin implementation only after approval
- Step 9: Work 1 step at a time, 1 file at a time — request current file versions before editing, return complete files with full Windows paths and fresh PowerShell commands where testable
- Step 10: Write detailed completion summary when done
- Step 11: Send summary to Master for review
- Step 12: If approved, write CHAT_28_DETAILED_SUMMARY.md + CHAT_28_HANDOFF.md
- Step 13: Send both docs to Master for approval
- Steps 14–15: Master updates project docs and commits (not your responsibility)

---

## Objective

Activate the 3 action buttons on recommendation cards. All infrastructure is in place from Chat 27 — cards render, buttons exist but are disabled. Chat 28 wires them up end-to-end.

---

## Context

Chat 27 built:
- `recommendations` table in `warehouse.duckdb` — 48 pending + 4 monitoring rows
- Global `/recommendations` page (3 tabs: Pending / Monitoring / History)
- Campaigns → Recommendations tab (inline card grid)
- 3 action buttons on every pending card: **Modify / Decline / Accept**
- Buttons are currently: `opacity:0.5; cursor:not-allowed; pointer-events:none`
- Amber note on each card: "Buttons active in Chat 28"

Chat 28 removes the disabled state and wires everything up.

---

## Deliverables

### 1. Backend — 3 new POST routes in `recommendations.py`

**POST `/recommendations/<id>/accept`**
- Load recommendation row by id from `warehouse.duckdb`
- Check status is `pending` (reject if not)
- Check `monitoring_days` on matching rule from `rules_config.json`:
  - If `monitoring_days > 0`: set status → `monitoring`, set `monitoring_start_date` = today, `monitoring_total_days` = value from config
  - If `monitoring_days = 0`: set status → `successful`
- Set `acted_at` = now
- Write audit row to `changes` table
- Return JSON `{success: true, new_status: 'monitoring'|'successful', message: '...'}`

**POST `/recommendations/<id>/decline`**
- Load recommendation row by id
- Check status is `pending`
- Set status → `declined`, set `acted_at` = now
- Return JSON `{success: true, message: 'Recommendation declined'}`
- No changes table entry needed for decline

**POST `/recommendations/<id>/modify`**
- Accept JSON body: `{new_value: <float>}`
- Load recommendation row by id
- Update `value_label` field with new value
- Then proceed exactly as Accept (monitoring or successful transition)
- Write audit row to `changes` table with `justification` = "Modified before accepting"
- Return JSON `{success: true, new_status: '...', message: '...'}`

**Changes table audit row fields:**
```
customer_id     — from session current client
campaign_id     — from recommendation row
campaign_name   — from recommendation row
rule_id         — from recommendation row
action_type     — 'budget_change' | 'bid_change' | 'status_change'
old_value       — current value (parse from trigger_summary if available)
new_value       — proposed value from recommendation
justification   — recommendation action_label field
executed_by     — 'user_accept' or 'user_modify'
executed_at     — now
dry_run         — False
status          — 'completed'
```
⚠️ Verify the actual `changes` table schema in warehouse.duckdb before writing — do not assume column names.

---

### 2. Modify Modal — Bootstrap modal in both templates

One modal per page (not per card). Scoped to the card via `data-rec-id`.

**Modal structure:**
- Title: "Modify Recommendation"
- Body: Rule name + campaign name (read-only), current proposed value (read-only), new value input (number, pre-filled with current proposed value)
- Footer: Cancel button + "Accept with Changes" button

**Important:** Use `data-rec-id`, `data-rec-rule`, `data-rec-campaign`, `data-rec-value` attributes on the Modify button to populate the modal. Do NOT create a separate modal per card.

---

### 3. JS updates — in both `recommendations.html` and `campaigns.html`

**Remove disabled state:**
- Remove `opacity:0.5; cursor:not-allowed; pointer-events:none` from buttons
- Remove amber "Buttons active in Chat 28" note from card footers

**Accept:**
- POST `/recommendations/<id>/accept`
- On success: animate card out (fade + slide, ~300ms), remove from DOM, decrement pending badge, green toast
- On error: red toast

**Decline:**
- POST `/recommendations/<id>/decline`
- On success: animate card out, remove from DOM, decrement badge, muted toast
- On error: red toast

**Modify:**
- Populate modal from `data-*` attributes, open Bootstrap modal
- On "Accept with Changes": POST `/recommendations/<id>/modify` with `{new_value: <input>}`
- On success: same as Accept
- On error: red toast, keep modal open

**Badge count update:**
- Decrement summary strip Pending count
- Decrement section header badge
- If section reaches 0: show empty state "No pending recommendations"

---

## Files to Edit

| File | Full Path |
|---|---|
| recommendations.py | `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\recommendations.py` |
| recommendations.html | `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\recommendations.html` |
| campaigns.html | `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\campaigns.html` |

⚠️ Request current versions of ALL 3 files from Christopher before editing any of them (Rule 2).

---

## Critical Rules

- Write to `warehouse.duckdb` only — NEVER `ro.analytics.*`
- Verify `changes` table schema before writing — do not assume column names
- One modal per page — scoped via `data-rec-id`
- Card removal is client-side only — do NOT reload the full page
- `acted_at` set on accept — engine checks this for cooldown on next run
- Monitoring transition: check `monitoring_days` in `rules_config.json` per rule
- ALWAYS request current file versions before editing (Rule 2)
- ALWAYS return complete files — never snippets
- ALWAYS use full Windows paths

---

## Success Criteria

- [ ] Accept button works, card animates out, badge decrements, green toast shows
- [ ] Accepted rules with `monitoring_days > 0` → `monitoring` status
- [ ] Accepted rules with `monitoring_days = 0` → `successful` status
- [ ] Decline works, card animates out, badge decrements, toast shows
- [ ] Modify button opens modal pre-filled with current value
- [ ] Modify + Accept with Changes works end-to-end
- [ ] Audit row written to `changes` table on Accept and Modify
- [ ] All actions work on both `/recommendations` page AND Campaigns tab
- [ ] Badge counts accurate after multiple actions without page reload
- [ ] Empty state shows when all cards in a section are actioned
- [ ] No full page reloads
- [ ] All pages regression-free (no HTTP 500s)

---

## Estimated Time

~2.5 hours

---

## Handoff Requirements

- `CHAT_28_DETAILED_SUMMARY.md` → `C:\Users\User\Desktop\gads-data-layer\docs\`
- `CHAT_28_HANDOFF.md` → `C:\Users\User\Desktop\gads-data-layer\docs\`
- Git commit message: `Chat 28 (M7): Accept/Decline/Modify wiring - recommendation actions live`
