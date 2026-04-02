# Chat 115 Summary — Job Hunter Brief (Full Session)

**Date:** 2026-03-26 to 2026-03-27
**Brief:** `docs/MC_JOB_HUNTER_BRIEF.md` (10 tasks)
**Status:** ALL 10 TASKS COMPLETE

---

## Overview

This session implemented the full "Job Hunter" brief — a 10-task plan to build a job tracking system into ACT, update Christopher's CV, polish christopherhoole.com for a recruiter audience, and research job search API options.

---

## Task 1: Connect Indeed MCP ✅
**Type:** Manual (done by user)
**What:** Connected the Indeed MCP connector to claude.ai via the browser interface.
**Result:** Indeed job searches work in claude.ai. Tested with "Google Ads Manager jobs in the UK" — returned 8 relevant listings with titles, companies, salaries, and URLs.

---

## Task 2: Create Jobs Database Table ✅
**Type:** Code
**Files created:**
- `act_dashboard/routes/jobs.py` — Full route file with Blueprint `jobs`, all CRUD endpoints

**Database table:** `jobs` in `warehouse.duckdb`

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER | Auto-increment PK |
| title | VARCHAR | Job title |
| company | VARCHAR | Company name |
| location | VARCHAR | City, country |
| salary | VARCHAR | Free text (£45k, $60k-$80k, etc.) |
| job_url | VARCHAR | Link to original listing |
| source | VARCHAR | indeed, linkedin, other |
| status | VARCHAR | saved, applied, interview, offer, rejected, withdrawn |
| priority | VARCHAR | high, medium, low |
| description | TEXT | Full job description |
| notes | TEXT | Personal notes |
| contact_name | VARCHAR | Recruiter/hiring manager name |
| date_found | DATE | When job was posted |
| date_applied | DATE | When user applied |
| follow_up_date | DATE | Reminder date |
| date_updated | TIMESTAMP | When added to ACT (auto-set) |

**API endpoints:**
- `GET /jobs/` — Render jobs page
- `GET /jobs/data` — JSON API for all jobs
- `POST /jobs/create` — Create new job
- `PUT /jobs/<id>` — Update job
- `DELETE /jobs/<id>` — Delete job
- `POST /jobs/fetch-url` — URL auto-fill (scrape job details from URL)
- `POST /jobs/sync-sheet` — Google Sheet sync import

---

## Task 3: Build Job Tracker Page — Table View ✅
**Type:** Code
**Files created:**
- `act_dashboard/templates/jobs.html` — Full page template
- `act_dashboard/static/css/jobs.css` — All styles

**Files modified:**
- `act_dashboard/app.py` — Registered jobs blueprint, added CSRF exemptions
- `act_dashboard/routes/__init__.py` — Added jobs import
- `act_dashboard/templates/base_bootstrap.html` — Added Jobs to sidebar nav

**Features built:**
- Client-side JS table (Option B pattern, like Recommendations page)
- Status filter pills: All, Saved, Applied, Interview, Offer, Rejected (with counts)
- Column sorting (click any header)
- Keyword search box (instant filter)
- Status pill badges with colours (saved=grey, applied=blue, interview=amber, offer=green, rejected=red)
- Priority badges (high=red, medium=amber, low=grey)
- Source badges (Indeed=orange, LinkedIn=blue, Other=grey)
- Click row to expand/view full details (description, URL, contact, dates)
- Edit and Delete buttons in expanded row
- Pagination with rows-per-page selector
- "Added" column showing when job was added to ACT (default sort, newest first)
- Sidebar nav icon (briefcase) between Changes and Outreach

---

## Task 4: Add/Edit Job Slide-In Panel ✅
**Type:** Code
**Built into:** `jobs.html` template

**Features:**
- Slide-in panel (reuses existing ACT pattern from rules_flow_builder)
- Three sections: Basic Info, Details, Tracking
- All fields: title, company, location, salary, job_url, source, status, priority, description, notes, contact_name, date_found, date_applied, follow_up_date
- Works for both Add and Edit modes
- Toast notifications on save/error

### Task 4b: URL Auto-Fill (Enhancement) ✅
**Added to slide-in panel — "Quick-fill from URL" section at top**

**How it works:**
1. User pastes a job URL (LinkedIn, Indeed, Reed, etc.)
2. Clicks "Fetch" button
3. Backend (`POST /jobs/fetch-url`) fetches the page HTML
4. Parses structured data: JSON-LD first, then Open Graph meta tags, then HTML fallback
5. Returns extracted data → JS auto-fills all form fields
6. Source auto-detected from URL domain

**LinkedIn crawler specifics:**
- Extracts title, company, location, salary from JSON-LD `JobPosting` schema
- Extracts full job description
- Extracts hiring person name from `<a>` tags with `hiring-team-member` class
- Works on public LinkedIn job URLs (no auth required)

**Limitations:**
- Indeed returns 403 (bot detection) — gracefully sets URL + source, asks user to fill rest
- LinkedIn description truncated in meta tags, but JSON-LD has full text
- Some sites render client-side (React/SPA) so server-side fetch gets limited data

---

## Task 5: Build Job Tracker Page — Pipeline/Kanban View ✅
**Type:** Code
**Built into:** `jobs.html` template

**Features:**
- Toggle buttons (table icon / kanban icon) in page header
- 4 columns: Saved, Applied, Interview, Offer
- Job cards showing: title, company, salary, priority badge, days since added
- Column headers with job counts
- Click card to open Edit slide-in
- "Rejected & Withdrawn" collapsible section at bottom
- Both views share same data from `GET /jobs/data`
- View preference persists during session

---

## Task 6: Google Sheet Sync ✅
**Type:** Code
**Built into:** `jobs.py` route + `jobs.html` template

**Pipeline architecture:**
```
User prompts claude.ai → Indeed MCP searches → claude.ai writes to Google Sheet → ACT syncs from Google Sheet
```

**Google Sheet setup:**
- Sheet: "Indeed Job Feed" (user created)
- Published as CSV: `https://docs.google.com/spreadsheets/d/e/2PACX-1vT09o_5t5ErKufpIJXw2cCNmDXHAKyH9xis6BwsvZQ_QxohjS6HGeVHa-OhzEoGGDcZmwGEUqa_LeIK/pub?output=csv`
- Auto-republish on changes enabled
- Columns: title, company, location, salary, job_url, source, description

**ACT sync features:**
- "Sync from Sheet" button on Jobs page header
- Backend fetches published CSV URL
- Parses CSV with Python `csv` module
- Skips header row and empty rows
- Duplicate detection by `job_url` (skips already imported jobs)
- Toast summary: "Imported X new jobs, Y duplicates skipped"
- Sheet URL stored in `jobs.py` route (hardcoded constant)

---

## Task 7: Stats Header ✅
**Type:** Code
**Built into:** `jobs.html` template

**5 stat cards displayed above filter pills:**

| Stat | Calculation |
|------|-------------|
| Total Jobs | Count of all jobs |
| Applications Sent | Count where status = 'applied' or further |
| Interviews Scheduled | Count where status = 'interview' |
| Offers Received | Count where status = 'offer' |
| Response Rate | (applied + interview + offer) / total × 100% |

---

## Task 8: CV Update ✅
**Type:** Content/Design
**Files created:** 13 CV iterations (V12 through V25) in `act-website/CVs/`
**Final output:** `chrishoolecv26-3-26.pdf` (2-page A4 PDF)

**Content changes from V11:**
- "I've pre-managed Google Ads" → "I've managed Google Ads"
- Virgin Media O2: added "(18 month contract via agency)"
- TMW Unlimited: added "(6 month contract)", dates changed to "May 2020 – Feb 2022"
- Pod Digital: changed to "Nov 2023 – Feb 2026", added "(Contractor)"
- Removed MarisaPeer.com section entirely (freed space)
- "75 optimisation rules, 99 monitoring flags, generating 507 live recommendations"
- "16 Years, Zero Fluff" → "16 Years"
- "Continued — Key Achievements & Capabilities" → "Continued"
- Taboola/Outbrain/Content Syndication → pill badges
- DataFeedWatch/Shoptimised/Google Merchant Centre → pill badges
- Photoshop/MS Office/Google Workspace/Dropbox → pill badges

**Design changes:**
- Name on 1 line (was 2)
- Standardised font sizes: 10px body, 11px pills, 12px section headings
- Reduced headshot size to fit header
- Reduced bullet point line spacing (1.6 → 1.45)
- Each page built as separate HTML file for clean A4 PDF export
- "Why I'm Different" section made full-width at bottom of page 2

**Approach:**
- Built each page as standalone HTML with exact A4 dimensions (210mm × 297mm)
- User exported to PDF manually from browser
- Always created new version files (never overwrote existing)

---

## Task 9: ChristopherHoole.com Website Polish ✅
**Type:** Content/Design/Code
**Project:** `C:\Users\User\Desktop\act-website` (Next.js + Tailwind)

### Pages created:
- `/hp-copy-1` — Archive of original homepage (standalone components in `components/archive/`)
- `/recruiter-audience` — Working copy for edits (then copied to homepage)

### Archive components created (13 files in `components/archive/`):
- AboutMeOriginal.tsx, ContactFormOriginal.tsx, FAQOriginal.tsx, FooterOriginal.tsx, HeroOriginal.tsx, NavigationOriginal.tsx, SkillsOriginal.tsx, TheDifferenceOriginal.tsx, TheProblemOriginal.tsx, WhatACTDoesOriginal.tsx, WhatsAppFloatOriginal.tsx, WhyDifferentOriginal.tsx, WorkHistoryOriginal.tsx

### Section-by-section changes:

**CV PDF:**
- Updated download link to `chrishoolecv26-3-26.pdf` (was V11)

**Hero:**
- CTA: "Let's Discuss Your Paid Ads" → "Get in Touch"
- Mobile: Static headshot shown instead of Three.js canvas (no hover on touch)
- "Scroll" indicator hidden on mobile
- Download CV button points to latest PDF

**Navigation:**
- CTA: "Let's Discuss Your Paid Ads" → "Get in Touch"

**About Me:**
- Removed: "Over the past few years I noticed something..." paragraph
- Changed: "So I spent 18 months building..." → "Most recently I built A.C.T — a proprietary AI-powered Google Ads optimisation platform that generates bid, budget and keyword recommendations across 5 campaign types."
- Changed: "200+ accounts" → "100+ accounts"
- Changed bullet section to "What I bring:" with 4 recruiter-focused bullets
- Never says "automates" (says "generates" instead)

**Work History:**
- Removed MarisaPeer.com entry
- TMW dates: 2021-2022 → May 2020 – Feb 2022
- All roles now show abbreviated months (Nov 2023 – Feb 2026, etc.)
- Added Apple Copywriting Agency (Jan 2009 – Mar 2014) and SixStarHolidays (Jul 2014 – Oct 2015)
- Company names bolded
- Font changed to monospace for job titles

**Skills:**
- Updated stats: 40+ rules → 75 rules, added 99 flags, 507 recommendations
- Removed "Coaching" from Industries
- Light cards on dark background (was dark cards on dark bg)
- Blue left border on cards (consistent with other sections)

**TheProblem:**
- Removed entirely from recruiter page

**TheDifference:**
- Changed from dark background to light background (maintains alternation pattern)

**WhatACTDoes:**
- Heading: removed "All features live and operational"
- Intro: "It's not a product for sale" → "it's what sets me apart from other candidates"
- Updated Autopilot stats: "40+ optimization rules" → "75 optimisation rules"
- Trimmed each card from 5 bullets to 3-4
- Removed "Additional Capabilities" box
- Dark background with light cards

**WhyDifferent:**
- Complete rewrite — removed accordions, comparison tables, emojis
- 4 clean cards in 2x2 grid:
  1. 16 Years Senior Experience
  2. Proprietary AI Engine
  3. Full Accountability
  4. Full-Stack Paid Media Expertise
- "the entire impression-to-sale journey" (not "lead-to-sale")
- No mention of "Maximum 4 clients"

**FAQ:**
- Complete rewrite — 11 new recruiter-focused FAQs:
  1. What type of role are you looking for?
  2. What's your availability?
  3. Do you work in-house or remotely?
  4. What size budgets have you managed?
  5. What industries have you worked in?
  6. What campaign types do you cover?
  7. Do you only do Google Ads?
  8. Can you work alongside an existing team?
  9. How do you communicate and report?
  10. Can I see A.C.T in action?
  11. What makes A.C.T different from other AI tools?

**Contact Form:**
- Heading: "Let's Discuss Your Paid Ads" → "Get in Touch"
- Subheading: recruiter-focused copy
- Removed 3-step process entirely
- White text on dark background

**Footer Banner:**
- Removed "Maximum 4 clients. Currently accepting new partnerships."
- New text: "16 years. / 100+ accounts. / £50M+ managed. / Available now." (stacked lines)
- CTAs: "Get in Touch" + "Download My CV"

**Footer:**
- Removed "Maximum 4 clients" tagline
- Updated all grey text to white

**Font System:**
- Added Inter (Google Font) for body text
- 3-tier system: 36px serif headings / 20px monospace subheadings / 16px Inter body
- Removed all grey font colours — pure black, pure white, or blue only
- Company names in Work History bolded

### Deployment:
- All changes committed and pushed to GitHub
- Vercel auto-deploys from main branch
- Live URLs:
  - `christopherhoole.com` — new recruiter-focused homepage
  - `christopherhoole.com/hp-copy-1` — original homepage archive
  - `christopherhoole.com/recruiter-audience` — working copy for future edits

---

## Task 10: LinkedIn Job Search Research ✅
**Type:** Research (no code)
**Output:** `docs/LINKEDIN_JOB_RESEARCH.md`

### 6 options evaluated:

| Option | Type | Cost | Verdict |
|--------|------|------|---------|
| LinkedIn MCP Server | Local scraper | Free | High risk of account issues |
| **JobSpy** ⭐ | Python library | Free | **Best option** — multi-board, integrates into Flask |
| JSearch API | REST API (RapidAPI) | Free tier (limited) | Good stable fallback |
| Adzuna API | REST API | Free tier | Good UK coverage |
| Indeed MCP | Already working | Free | Keep as primary source |
| Apify | Cloud scrapers | $49+/mo | Overkill for personal use |

### Recommendation:
- **Immediate:** Keep Indeed MCP → Google Sheet → ACT pipeline
- **Short-term:** Integrate JobSpy into ACT backend (search Indeed + LinkedIn + Glassdoor from Jobs page)
- **Medium-term:** Register JSearch + Adzuna APIs as fallbacks

---

## Files Modified Summary

### ACT Dashboard (gads-data-layer)

| File | Change |
|------|--------|
| `act_dashboard/routes/jobs.py` | **NEW** — Full jobs route (CRUD, fetch-url, sync-sheet) |
| `act_dashboard/templates/jobs.html` | **NEW** — Jobs page (table, kanban, slide-in, stats) |
| `act_dashboard/static/css/jobs.css` | **NEW** — All jobs page styles |
| `act_dashboard/app.py` | **MODIFIED** — Registered jobs blueprint, CSRF exemptions |
| `act_dashboard/routes/__init__.py` | **MODIFIED** — Added jobs import |
| `act_dashboard/templates/base_bootstrap.html` | **MODIFIED** — Added Jobs to sidebar |
| `docs/LINKEDIN_JOB_RESEARCH.md` | **NEW** — Task 10 research output |
| `docs/CHAT_115_SUMMARY.md` | **NEW** — This document |

### ChristopherHoole.com (act-website)

| File | Change |
|------|--------|
| `app/page.tsx` | **MODIFIED** — Homepage now uses recruiter-focused components |
| `app/hp-copy-1/page.tsx` | **NEW** — Original homepage archive |
| `app/recruiter-audience/page.tsx` | **NEW** — Working copy page |
| `app/recruiter-audience/layout.tsx` | **NEW** — Layout for working copy |
| `app/globals.css` | **MODIFIED** — Inter font, colour overrides |
| `app/layout.tsx` | **MODIFIED** — Font configuration |
| `components/AboutMe.tsx` | **MODIFIED** — Recruiter copy |
| `components/ContactForm.tsx` | **MODIFIED** — Recruiter messaging |
| `components/FAQ.tsx` | **MODIFIED** — 11 new FAQs |
| `components/Footer.tsx` | **MODIFIED** — Updated messaging |
| `components/Hero.tsx` | **MODIFIED** — CTA, mobile responsive |
| `components/Navigation.tsx` | **MODIFIED** — CTA update |
| `components/Skills.tsx` | **MODIFIED** — Stats, light cards |
| `components/TheDifference.tsx` | **MODIFIED** — Light background |
| `components/WhatACTDoes.tsx` | **MODIFIED** — Tightened content |
| `components/WhyDifferent.tsx` | **MODIFIED** — Complete rewrite |
| `components/WorkHistory.tsx` | **MODIFIED** — Dates, entries, styling |
| `tailwind.config.ts` | **MODIFIED** — Config updates |
| `public/Christopher_Hoole_CV_March_2026.pdf` | **NEW** — Latest CV PDF |
| `components/archive/*.tsx` (13 files) | **NEW** — Original component backups |

### CV Files (act-website/CVs/)

| File | Notes |
|------|-------|
| V12.html through V25.html | 13 iterations during Task 8 |
| V20-V23 Page1/Page2 variants | Split-page approach |
| `chrishoolecv26-3-26.pdf` | Final 2-page A4 PDF |

---

## Google Sheet Configuration

| Setting | Value |
|---------|-------|
| Sheet name | Indeed Job Feed |
| Published CSV URL | `https://docs.google.com/spreadsheets/d/e/2PACX-1vT09o_5t5ErKufpIJXw2cCNmDXHAKyH9xis6BwsvZQ_QxohjS6HGeVHa-OhzEoGGDcZmwGEUqa_LeIK/pub?output=csv` |
| Auto-republish | Enabled |
| Columns | title, company, location, salary, job_url, source, description |

---

## Key Architectural Decisions

1. **Client-side JS table** (not server-side Jinja) — faster filtering/sorting for small dataset
2. **URL auto-fill via server-side scraping** — JSON-LD first, Open Graph fallback, HTML fallback
3. **Google Sheet as bridge** — claude.ai writes, ACT reads via published CSV
4. **Separate CV pages** — each A4 page as standalone HTML for clean PDF export
5. **Archive components** — original homepage preserved with standalone component copies
6. **Inter font for body** — monospace kept for headings, Inter for readability
7. **No grey text** — pure black, white, or blue only across website
8. **"Generates" not "automates"** — messaging principle for A.C.T descriptions

---

## Future Work / Recommendations

1. **Integrate JobSpy** into ACT backend — "Search Jobs" button on Jobs page
2. **Register for JSearch + Adzuna APIs** — free tier fallbacks
3. **Task 9 continued** — further A/B testing of recruiter page vs original
4. **CV cleanup** — delete intermediate V12-V24 files, keep only V11 (original) and V25 (latest)
5. **Mobile testing** — full responsive audit of all website sections beyond hero
