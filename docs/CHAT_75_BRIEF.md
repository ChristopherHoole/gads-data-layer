# CHAT 75: LEADS PAGE — QUEUE EMAIL + EDIT LEAD BUTTONS

**Date:** 2026-03-08
**Estimated Time:** 2–3 hours
**Priority:** HIGH
**Dependencies:** Chat 68 complete (live email sending working)

---

## CONTEXT

The Leads page slide-out panel has 4 action buttons. Mark Won and Mark Lost work. Queue Email and Edit Lead both show "coming soon" toasts and do nothing. This blocks the end-to-end outreach workflow — a new lead cannot be queued for outreach from the Leads page.

## OBJECTIVE

Wire up Queue Email and Edit Lead so both are fully functional.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — MODIFY
   - `POST /outreach/leads/<lead_id>/queue-email` — insert Step 1 email into outreach_emails as queued
   - `PUT /outreach/leads/<lead_id>/edit` — update lead record fields

2. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\leads.html` — MODIFY
   - Wire Queue Email button to new route
   - Add Edit Lead modal with form fields
   - Wire Edit Lead button to open modal and submit to new route

3. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — MODIFY
   - CSRF exempt both new routes

4. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_75_HANDOFF.md` — CREATE
5. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_75_SUMMARY.md` — CREATE

---

## REQUIREMENTS

### Queue Email
- Read the lead's `track` value (e.g. 'Direct', 'Agency', 'Recruiter', 'Job')
- Look up Step 1 template for that track from `email_templates` table
- Substitute variables: `{{first_name}}`, `{{company}}` etc using lead record
- Insert row into `outreach_emails`:
  - `lead_id`, `template_id`, `subject`, `body`, `status='queued'`, `sequence_step=1`, `progress_stage='step_1'`
- If a queued or sent Step 1 already exists for this lead, return error toast: "Email already queued or sent for this lead"
- On success: green toast "Email queued — go to Queue page to send"
- Update lead `status` to `'queued'` if currently `'cold'`

### Edit Lead
- Modal fields: First Name, Last Name, Company, Email, City, Country, Track (dropdown), Type Score (dropdown: Cold/Warm/Hot/Medium), Source
- Pre-populate all fields from current lead data
- `PUT` to `/outreach/leads/<lead_id>/edit`
- On success: green toast "Lead updated", slide panel refreshes with new data

### Constraints
- Track dropdown must match exact values used elsewhere: Agency, Recruiter, Direct, Job
- Type score dropdown: Cold, Warm, Medium, Hot
- Check `email_templates` table structure before writing queue logic — confirm column names
- Check existing `add_lead` route for the correct INSERT pattern for outreach_emails

---

## SUCCESS CRITERIA

- [ ] Queue Email button queues Step 1 email for the lead's track
- [ ] Queued email appears on Queue page immediately
- [ ] Attempting to queue a second time shows error toast
- [ ] Lead status updates from Cold to Queued after queueing
- [ ] Edit Lead button opens modal pre-populated with lead data
- [ ] Saving edit updates the lead and refreshes the panel
- [ ] Both buttons show correct success/error toasts
- [ ] No console errors
- [ ] Flask starts cleanly

---

## REFERENCE FILES

- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — existing routes, especially `add_lead()` and `mark_won()`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\leads.html` — current button stubs and slide panel structure

---

## TESTING

1. Start Flask
2. Open Leads page — click lead to open slide panel
3. Click Queue Email — confirm green toast and email appears on Queue page
4. Click Queue Email again — confirm error toast (already queued)
5. Click Edit Lead — confirm modal opens with correct pre-populated data
6. Change company name, save — confirm panel shows updated name
7. Confirm no Flask errors in terminal
8. Report Flask log output for both actions
