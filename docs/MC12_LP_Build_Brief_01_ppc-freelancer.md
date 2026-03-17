# BUILD BRIEF #1 — /ppc-freelancer
## PPC Freelancer Landing Page
**Date:** 2026-03-16 | **Priority:** HIGH | **Ad group:** PPC Freelancer

---

## Overview

| Field | Value |
|-------|-------|
| URL | https://www.christopherhoole.com/ppc-freelancer |
| File to create | C:\Users\User\Desktop\act-website\app\ppc-freelancer\page.tsx |
| Ad group | PPC Freelancer |
| Current QS | 3/10 — landing page experience: Below Average |
| Goal | Improve QS by matching page content to keyword intent |
| Primary conversion | Lead form submission |
| Secondary conversion | WhatsApp message |

---

## Keywords This Page Must Match

The H1 and page copy must prominently feature this language:
- ppc freelancer
- ppc freelancer uk
- freelance ppc specialist
- freelance ppc expert
- freelance ppc consultant
- freelance ppc manager
- google ads freelancer uk

---

## Copy — Headlines & Messaging

### H1 — Required
Must contain the words "PPC Freelancer" exactly.

**Suggested:** Senior PPC Freelancer UK — 16 Years Experience

### Subheadline
Not an agency. A dedicated PPC freelancer with proprietary AI technology and a maximum of 4 clients.

### CTA Button Text
Get a Free PPC Audit

### Trust Bar — 4 Items
- 16 Years PPC Experience
- Maximum 4 Clients
- AI-Powered Optimisation
- No Long-Term Contracts

### Value Proposition — 4 Bullets
- Full Google Ads campaign management — search, shopping, display
- Keyword research, match type strategy and negative keyword management
- Bid management and budget optimisation
- Monthly performance reporting with clear, jargon-free insights

### Why a PPC Freelancer Beats an Agency — 3 Points
- You work directly with a senior specialist — not a junior account manager
- Maximum 4 clients means your account gets genuine focus and attention
- No contracts, no lock-in — stay because of results, not obligations

### How It Works — 3 Steps
- Step 1: Free Audit — I review your current campaigns and identify quick wins
- Step 2: Strategy — We agree on goals, budget, and a clear plan of action
- Step 3: Ongoing Management — Monthly optimisation, reporting, and communication

---

## Page Sections — Build in This Order

| Section | Content |
|---------|---------|
| 1. Nav | Same as homepage — reuse existing nav component |
| 2. Hero | H1, subheadline, "Get a Free PPC Audit" button, dark background |
| 3. Trust bar | 4 trust signals in a horizontal bar |
| 4. Value proposition | 4 bullet points on what's included |
| 5. Why freelancer beats agency | 3 points with icons |
| 6. How it works | 3 numbered steps |
| 7. Lead form | Name, email, company, phone (optional), monthly budget dropdown |
| 8. WhatsApp CTA | Green WhatsApp block — same style as homepage |
| 9. Footer | Same as homepage — reuse existing footer component |

### Lead Form — Budget Dropdown Options
- Under £1,000/month
- £1,000 – £5,000/month
- £5,000 – £10,000/month
- Over £10,000/month

---

## Technical Spec

### File
Create: `C:\Users\User\Desktop\act-website\app\ppc-freelancer\page.tsx`

Single file — all JSX, Tailwind classes, and logic in one file.

### Conversion Tracking
On form submit, fire this gtag event — same as ContactForm.tsx:
```javascript
window.gtag('event', 'conversion', {
  send_to: 'AW-18006514629/fxGxCNeunoYcEMW3lopD',
  value: 40.00,
  currency: 'GBP'
});
```

### Rules
- Tailwind CSS only — no inline styles except where unavoidable
- Mobile first — must look correct at 375px minimum width
- No new npm dependencies
- Do NOT modify app/layout.tsx
- Do NOT modify app/globals.css
- Match christopherhoole.com design system exactly
- Check codebase first — reuse existing nav and footer components if they exist

---

## Success Criteria

All of the following must pass before reporting complete:

- [ ] Page loads at christopherhoole.com/ppc-freelancer
- [ ] H1 contains the words "PPC Freelancer"
- [ ] Page looks correct on mobile at 375px
- [ ] Lead form submits without errors
- [ ] Conversion tracking fires on form submit
- [ ] WhatsApp button opens correct wa.me link
- [ ] No console errors
- [ ] Design matches christopherhoole.com exactly

---

## After Build — Christopher's Actions

Once confirmed live in Opera:

1. Run git commit and push:
```powershell
cd C:\Users\User\Desktop\act-website
git add .
git commit -m "Add ppc-freelancer landing page"
git push origin master
```

2. In Google Ads → PPC Freelancer ad group → all keywords → change Final URL from `https://www.christopherhoole.com` to `https://www.christopherhoole.com/ppc-freelancer`

3. Monitor Quality Score over next 7 days — expect improvement from 3/10
