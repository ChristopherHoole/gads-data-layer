# MC Job Hunter — Master Brief
**Session:** MC Job Hunter
**Date:** 2026-03-25
**Objective:** Build a job hunting system into ACT to find PPC/Google Ads roles, track applications, polish CV and website.

---

## CRITICAL: BROWSER VERIFICATION REQUIRED

Every change made during this session MUST be visually verified in the browser before moving on. After each task:
- Run the Flask app and open the relevant page
- Visually confirm the UI renders correctly
- Test all interactions (click, open, close, submit, cancel)
- Check the browser console for JavaScript errors
- Confirm no regressions on other pages/tabs

If something looks wrong, fix it immediately before proceeding.

---

## CRITICAL: ONE TASK AT A TIME

Complete each task fully and get confirmation before starting the next. Do NOT work on multiple tasks simultaneously. Do NOT skip ahead. The task numbers are the execution order.

---

## TASK 1: Connect Indeed MCP Connector
This is a manual task for the user — not a code task. Connect the Indeed MCP connector in Claude Desktop settings (Customize > Connectors > Indeed > Connect). Once connected, the `search_jobs` and `get_job_details` tools become available in Claude conversations.
**Verify:** Ask Claude to search for "Google Ads Manager UK" and confirm job results come back.

---

## TASK 2: Create Jobs Database Table
Create a new DuckDB table to store job listings and application tracking. The table should include:
- job_id (auto-increment primary key)
- source (indeed, linkedin, other)
- title
- company
- location
- salary (text, as listed)
- job_url (link to original listing)
- description (full job description text)
- status (saved, applied, interview, offer, rejected, withdrawn)
- notes (free text)
- date_found
- date_applied
- date_updated
- contact_name
- contact_email
- follow_up_date
- priority (high, medium, low)
**Browser-verify:** Confirm table exists in DuckDB with correct schema.

---

## TASK 3: Build Job Tracker Page — Table View
Create a new "Jobs" page in ACT accessible from the sidebar navigation. Build a data table showing all saved jobs with columns: Title, Company, Location, Salary, Source, Status, Priority, Date Applied, Follow-up Date. Include:
- Status filter buttons (All, Saved, Applied, Interview, Offer, Rejected)
- Sort by any column
- Search/filter by keyword
- Status pill badges with colours (saved=grey, applied=blue, interview=amber, offer=green, rejected=red, withdrawn=muted)
- Priority badges (high=red, medium=amber, low=grey)
- Click row to expand/view details
**Browser-verify:** Page loads, table renders, filters work, sorting works. Zero console errors.

---

## TASK 4: Build Job Tracker Page — Add/Edit Job
Add the ability to manually add a new job and edit existing jobs. Use a slide-in panel (matching the existing ACT slide-in pattern from rules). Fields:
- Title, Company, Location, Salary, Job URL, Source (dropdown: Indeed/LinkedIn/Other)
- Status (dropdown), Priority (dropdown)
- Description (textarea)
- Contact Name, Contact Email
- Follow-up Date (date picker)
- Notes (textarea)
- Date Applied (date picker)
Include Save, Cancel, and Delete buttons.
**Browser-verify:** Add a test job, edit it, delete it. All fields save and load correctly. Slide-in opens and closes cleanly.

---

## TASK 5: Build Job Tracker Page — Pipeline/Kanban View
Add a toggle to switch between Table view and Pipeline view. The pipeline view shows jobs as cards in columns by status: Saved → Applied → Interview → Offer. Rejected/Withdrawn shown in a collapsed section below. Each card shows: Title, Company, Salary, Priority badge, days since last update.
**Browser-verify:** Toggle between table and pipeline views. Cards appear in correct columns. Both views show the same data.

---

## TASK 6: Build Indeed Import Helper
Add a button "Import from Indeed" on the Jobs page. This opens a slide-in with a single text input for an Indeed job URL. When submitted, the system extracts what it can from the URL and pre-fills the Add Job form with: Title, Company, Location, Salary, Job URL, Source (auto-set to "indeed"). The user reviews and clicks Save.
**Browser-verify:** Paste an Indeed job URL, confirm fields pre-fill, save the job, confirm it appears in the table.

---

## TASK 7: Job Tracker — Stats Header
Add a stats header row at the top of the Jobs page showing:
- Total Jobs Saved
- Applications Sent
- Interviews Scheduled
- Offers Received
- Response Rate (applied → interview %)
- Cards should update automatically based on table data.
**Browser-verify:** Add a few test jobs in different statuses, confirm stats are accurate.

---

## TASK 8: CV Update
Update the CV file at `C:\Users\User\Desktop\act-website\best_so_far_Christopher_Hoole_CV_March_2026.html`:
- Fix website URL: change all instances of `christopherhoole.online` to `christopherhoole.com`
- Update ACT stats: change "41 optimisation rules" to "75 optimisation rules"
- Update ACT stats: change "1,492 active recommendations" to current accurate number
- Update flags count: add "99 monitoring flags" to the ACT description
- Review any other outdated information
**Browser-verify:** Open the CV HTML file in browser, confirm all changes render correctly, check no layout breaks.

---

## TASK 9: ChristopherHoole.com Website Polish
Review the current ChristopherHoole.com website and make improvements so it works effectively as a portfolio/CV landing page for job applications. Consider:
- Is the ACT dashboard featured prominently as a portfolio piece?
- Are the key metrics and achievements from the CV visible?
- Is there a clear CTA for recruiters/hiring managers?
- Does the site load fast and look professional on mobile?
- Read the current site code first, then propose specific improvements.
**Browser-verify:** Check the site locally, test on mobile viewport, confirm all changes look good.

---

## TASK 10: LinkedIn Job Search Research
Research and document options for pulling LinkedIn job listings. Investigate:
- Any unofficial LinkedIn MCP connectors
- LinkedIn job search APIs (official or third-party)
- Adzuna API (aggregates LinkedIn + others, free tier)
- JSearch via RapidAPI (aggregates LinkedIn, Indeed, Glassdoor)
- Any other viable options
Document findings with pros/cons/pricing for each option. Save to docs/LINKEDIN_JOB_RESEARCH.md.
**No browser-verify needed** — this is a research task.

---

## SESSION SUMMARY

| # | Task | Category |
|---|------|----------|
| 1 | Connect Indeed MCP connector | Setup (manual) |
| 2 | Create jobs database table | Backend |
| 3 | Build Job Tracker page — table view | Frontend |
| 4 | Build Job Tracker page — add/edit job | Frontend |
| 5 | Build Job Tracker page — pipeline/kanban view | Frontend |
| 6 | Build Indeed import helper | Feature |
| 7 | Job Tracker — stats header | Frontend |
| 8 | CV update | Content |
| 9 | ChristopherHoole.com website polish | Website |
| 10 | LinkedIn job search research | Research |

**TOTAL: 10 tasks, executed in order, one at a time.**

---

**END OF BRIEF**
