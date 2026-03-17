# MASTER CHAT 12.0 — LP BUILDER
## Context & Onboarding Brief
**Date:** 2026-03-16 | **Read this entire document before doing anything**

---

## 1. Who You Are Talking To

| Field | Value |
|-------|-------|
| Name | Christopher Hoole |
| Email | chris@christopherhoole.com |
| WhatsApp | +447999500184 |
| Website | https://www.christopherhoole.com |
| Expertise | Google Ads specialist — 16 years experience |
| Location | Brazil (UK passport, UK bank account) |
| Business goal | Build a client base for Google Ads freelance/agency business in the UK |

**Communication style — MANDATORY:**
- SHORT and DIRECT answers only. No waffle.
- Be PAINFULLY EXPLICIT about every recommendation.
- Always provide COMPLETE, READY-TO-USE FILES — never code snippets.
- Always use FULL Windows file paths — never partial paths.
- Christopher describes himself as NOT A CODER — needs exact instructions with clear expectations.
- Never ask clarifying questions before executing already-approved work.

---

## 2. The Website — christopherhoole.com

### Purpose
Marketing website for Christopher's Google Ads freelance and agency partnership business. Primary conversion goal: lead form submissions and WhatsApp contacts from UK businesses and agencies needing Google Ads management.

### Tech Stack

| Field | Value |
|-------|-------|
| Framework | Next.js 14 (App Router) |
| Styling | Tailwind CSS |
| Animation | Framer Motion |
| 3D Hero | Three.js WebGL (r128) |
| Hosting | Vercel — auto-deploys on git push origin master |
| Domain | christopherhoole.com (PRIMARY — NEVER use christopherhoole.online) |
| Repo | GitHub: ChristopherHoole/act-website |
| Branch | master |

### Project Location
`C:\Users\User\Desktop\act-website`

### Key Files

| File | Purpose |
|------|---------|
| app/layout.tsx | Root layout + Google tag |
| app/page.tsx | Homepage |
| components/ContactForm.tsx | Contact form component |
| app/globals.css | Global styles |
| tailwind.config.ts | Tailwind config |
| app/api/leads/route.ts | Lead capture API |

### Google Tag
`AW-18006514629` — already in `app/layout.tsx`. Do NOT change this. All new pages inherit it automatically via the root layout.

### Lead Capture
Contact form POSTs to `/api/leads` which writes to Google Sheets (ID: `1zRTPuzwvHDSq23RqJ9iiRaNZ8bSOMmndUzxiP_DW38I`). New landing pages must reuse the same ContactForm component or replicate its conversion tracking exactly.

### Conversion Tracking
Every lead form must fire this gtag conversion event on submit:
- `send_to: AW-18006514629/fxGxCNeunoYcEMW3lopD`
- `value: 40.00, currency: GBP`

Already implemented in `components/ContactForm.tsx` — reuse or replicate exactly.

### Design System

| Element | Value |
|---------|-------|
| Primary colour | #1e3a5f (dark navy) |
| Accent colour | #3b82f6 (blue) |
| Background | Dark — #0f172a or similar dark slate |
| Font family | Monospace (font-mono) for body, serif for headings |
| CTA style | Blue button, uppercase, tracking-widest |
| Trust signals | 16 years experience, Max 4 clients, AI-powered, No long-term contracts |

### Current Homepage Sections
- Hero — headline, subheadline, CTA, Three.js WebGL background
- Trust bar — key stats
- About — 16 years experience, senior not junior
- What A.C.T Does — AI platform explanation
- Services — campaign management, audits, strategy
- Work history / Experience
- FAQ
- Contact — WhatsApp primary CTA + lead form
- Footer

---

## 3. Why Landing Pages Are Being Built

Christopher is running Google Ads (account 487-268-1731) targeting UK businesses looking to hire a Google Ads specialist. The campaign has 5 ad groups:

- Google Ads Management
- Google Ads Consultant
- Google Ads Specialist / Expert
- PPC Freelancer
- Agency / White Label

Currently all 5 ad groups point to the homepage. Google is rating landing page experience as Below Average and giving Quality Scores of 3/10 on key keywords — because the homepage does not prominently feature the exact language searchers used (e.g. "PPC freelancer", "PPC consultant").

The fix: one dedicated landing page per ad group. Each page must use the exact keyword language of that ad group in the H1 and throughout. This improves Quality Score, lowers CPCs, and improves conversion rate.

---

## 4. Landing Page Standards — Apply to Every Page

### URL Structure
- Each page: `christopherhoole.com/[page-slug]`
- File location: `app/[page-slug]/page.tsx` — single file

### Required Sections on Every Page

| Section | Content |
|---------|---------|
| 1. Hero | H1 containing the exact ad group keyword, subheadline, primary CTA button |
| 2. Trust bar | 16 years experience, Max 4 clients, AI-powered, No long-term contracts |
| 3. Value proposition | 3-4 bullet points — what the service includes |
| 4. Why Christopher beats agencies | 3 points addressing the agency frustration angle |
| 5. How it works | 3 steps: Free Audit → Strategy → Ongoing Management |
| 6. Lead form | Name, email, company, phone (optional), monthly Google Ads budget (dropdown) |
| 7. WhatsApp CTA | Secondary contact — wa.me/447999500184 |
| 8. Footer | Same as homepage |

### CTA Button Text
Always: **Get a Free [Service Type] Audit**

### Tone
Direct, confident, senior. Not salesy. No fluff. Speaks to someone frustrated with agencies who wants a senior individual focused entirely on their account.

### Must Include on Every Page
- Exact ad group keyword in H1
- "16 years" prominently
- "Maximum 4 clients" — scarcity signal
- "AI-powered" or "A.C.T" — technology differentiator
- "Free audit" offer — lowest barrier CTA
- WhatsApp number: +447999500184

### Must Avoid on Every Page
- Mentioning pricing or rates
- Generic PPC advice content
- Agency language or positioning
- Keyword stuffing

### Technical Rules
- Single file: `app/[slug]/page.tsx` — no separate CSS files
- Tailwind CSS only — no inline styles except where unavoidable
- Mobile first — must look correct at 375px minimum width
- No new npm dependencies — use what is already installed
- NEVER modify `app/layout.tsx`
- NEVER modify `app/globals.css`
- NEVER modify `components/ContactForm.tsx` — create a variant if needed
- NEVER use christopherhoole.online — always christopherhoole.com

---

## 5. Deployment Workflow

After every build, Christopher runs these commands in PowerShell:

```powershell
cd C:\Users\User\Desktop\act-website
git add .
git commit -m "Add [page name] landing page"
git push origin master
```

Vercel auto-deploys within 1-2 minutes. Christopher tests in Opera browser.

After confirming live — Christopher updates the Final URL in Google Ads for the relevant ad group keywords.

**NEVER ask Claude Code to run git commands — git commits are Christopher's job in PowerShell.**

---

## 6. Build Queue — All 5 Pages

Pages are briefed and built one at a time in this order. Each page is confirmed live before the next brief is issued.

| Priority | Page | Ad Group |
|----------|------|----------|
| 1 | /ppc-freelancer | PPC Freelancer — FIRST BUILD |
| 2 | /google-ads-consultant | Google Ads Consultant |
| 3 | /google-ads-management | Google Ads Management |
| 4 | /google-ads-specialist | Google Ads Specialist / Expert |
| 5 | /white-label-ppc | Agency / White Label |

Each page brief is delivered as a separate document — it will be handed to you after you confirm you have read and understood this context brief.

---

## 7. Key Rules — Never Violate

- Always provide COMPLETE, READY-TO-USE files — never code snippets or partial files
- Always use full Windows paths — never partial paths
- One page at a time — complete and confirm before moving to next
- Never commit before Christopher confirms in Opera
- Mobile first — every page must look perfect at 375px
- Match the existing design system exactly — no creative deviations
- Never use christopherhoole.online as the primary domain
- Never modify layout.tsx, globals.css, or ContactForm.tsx

---

**When ready: confirm you have read this document, then wait for the first page brief.**
