# CLAUDE CODE BRIEF — /ppc-freelancer Landing Page QS Improvements
**Date:** 2026-03-19
**File:** `C:\Users\User\Desktop\act-website\app\ppc-freelancer\page.tsx`
**Estimated Time:** 1–2 hours
**Priority:** HIGH
**Goal:** Improve Google Ads Quality Score landing page experience rating from Below Average to Average or Above Average by increasing keyword density and content relevance.

---

## CONTEXT

The /ppc-freelancer page currently scores QS 3/10 on primary keywords. The landing page experience component is "Below average." Google's crawler needs to see the searched keyword reflected in the page body content. The page is strong for "PPC freelancer" in the H1 and title, but missing most keyword variants in body copy. This brief is targeted edits only — no redesign, no structural changes.

---

## OBJECTIVE

Add natural keyword mentions throughout existing page sections so Google's crawler sees clear relevance for all major keyword variants: PPC freelancer, Google Ads freelancer, freelance PPC manager, freelance PPC specialist, freelance PPC expert, freelance PPC consultant.

---

## DELIVERABLES

All changes are to ONE file:
`C:\Users\User\Desktop\act-website\app\ppc-freelancer\page.tsx`

---

## REQUIRED CHANGES

### Change 1 — Fix "Uk" capitalisation in hero tag
Find: `PPC Freelancer · Senior Level · Uk`
Replace with: `PPC Freelancer · Senior Level · UK`

---

### Change 2 — Update hero subtext
Find the paragraph below the H1 (starts with "16 years. £50M+ managed."):
```
16 years. £50M+ managed. Maximum 4 clients. No agencies, no juniors, no account managers. Just a senior specialist fully focused on your results.
```
Replace with:
```
Senior PPC freelancer and Google Ads specialist with 16 years experience. £50M+ managed. Maximum 4 clients. No agencies, no juniors. Just a dedicated freelance PPC expert fully focused on your results.
```

---

### Change 3 — Update "What you get" section intro paragraph
Find: `Not a retainer. Not a report. A senior specialist running your account every single week.`
Replace with: `Not a retainer. Not a report. A senior freelance PPC manager running your Google Ads account every single week.`

---

### Change 4 — Update "What you get" card headings and body copy

**Card 1 — Full PPC Campaign Management**
Keep heading as-is. Update body copy:
Find: `Search, Shopping, and Display campaigns managed end-to-end. Strategy, structure, keywords, bids, ads, and reporting — all handled.`
Replace with: `As your freelance PPC manager, I handle Search, Shopping, and Display campaigns end-to-end. Strategy, structure, keywords, bids, ads, and reporting — all handled.`

**Card 2 — Keyword Strategy & Negative Management**
Keep heading as-is. Update body copy:
Find: `Ongoing keyword expansion, match type optimisation, and negative keyword management to eliminate wasted spend every week.`
Replace with: `Ongoing keyword expansion, match type optimisation, and negative keyword management. As a specialist Google Ads freelancer, I eliminate wasted spend every single week.`

**Card 3 — Bid & Budget Optimisation**
Keep heading as-is. Keep body copy as-is.

**Card 4 — Monthly Reporting**
Keep heading as-is. Keep body copy as-is.

---

### Change 5 — Update "About me" section — first paragraph
Find: `Over 16 years I've worked across automotive (Lexus, Toyota), luxury travel, B2B (Virgin Media O2), ecommerce, property, and professional services. I've managed budgets from £5k to £400k per month and optimised 200+ accounts.`
Replace with: `As a freelance PPC consultant and Google Ads specialist, I've worked across automotive (Lexus, Toyota), luxury travel, B2B (Virgin Media O2), ecommerce, property, and professional services over 16 years. I've managed budgets from £5k to £400k per month and optimised 200+ accounts as a freelance PPC manager and specialist.`

---

### Change 6 — Update "About me" section — third paragraph
Find: `So I spent 18 months building my own Google Ads Ai engine called **A.C.T (Ads Control Tower)**. My approach: data-driven, explainable, guardrailed recommendations.`
Replace with: `So I spent 18 months building my own Google Ads AI engine called **A.C.T (Ads Control Tower)**. As a freelance PPC expert, my approach is data-driven, explainable, and guardrailed — not reckless automation.`

---

### Change 7 — Add new "Freelance PPC services" section

Insert this AFTER the "What you get" section and BEFORE the "About me" section. This is a new dark-background section. Match the exact visual style of the existing dark sections (bg-[#0f172a], same padding, same typography patterns).

Section heading tag: `Freelance PPC services`
Section H2: `What a freelance PPC specialist does differently`
Section intro paragraph: `Hiring a freelance PPC manager means your account gets senior attention every day — not handed to a junior exec at an agency.`

Four bullet points (use the same arrow → style as the About me section):
1. `As your freelance PPC consultant, I audit, restructure, and optimise your Google Ads account from day one.`
2. `Every change is logged. Every decision is explained. No black box — you always know what your freelance Google Ads manager is doing and why.`
3. `From keyword research to bid strategy, a dedicated freelance PPC expert handles the full account — not just the easy parts.`
4. `Unlike agencies that rotate staff, you always work directly with the same senior PPC freelancer.`

CTA button below the bullets: `Get a free PPC audit →` linking to `#audit`

---

### Change 8 — Update "Why not an agency" section heading
Find: `Why a senior PPC freelancer beats an agency`
Replace with: `Why a senior PPC freelancer and Google Ads specialist beats an agency`

---

### Change 9 — Add keyword-rich content to FAQ answers

The FAQ items currently only show questions. Each FAQ item needs a visible answer paragraph added inside it. These answers must be rendered in the HTML (not loaded dynamically after click) so Google can crawl them. The existing accordion/toggle behaviour can remain, but the answer text must exist in the DOM on page load.

Add these answers to the existing FAQ questions:

**What size accounts do you work with?**
`I work with UK businesses spending between £2,000 and £100,000 per month on Google Ads. As a freelance PPC manager, I focus on accounts where senior specialist attention makes a meaningful difference to results.`

**What do you not do?**
`I don't manage Meta Ads, TikTok, or programmatic as a primary service. I'm a Google Ads freelancer — Search, Shopping, and Performance Max is my focus. I don't work with accounts spending under £2,000/month.`

**How is this different from hiring an agency?**
`At an agency, your account is managed by a junior PPC executive handling 30+ accounts. As a freelance PPC consultant, I personally manage every account I take on. Maximum 4 clients. Senior expertise on every account, every day.`

**Is A.C.T a SaaS product I can buy?**
`No. A.C.T is my proprietary Google Ads AI engine — it's my competitive advantage as a freelance PPC specialist, not a product for sale. Every client benefits from it, but it's not available separately.`

**Can I see A.C.T in action?**
`Yes — I demo A.C.T live on every fit call. You'll see the dashboard, the recommendations, and the reasoning behind every change. It's one of the key differences between working with a freelance Google Ads manager like me versus a standard agency.`

**What if my performance drops while working with you?**
`A.C.T has automatic rollback triggers — if KPIs degrade by 15% or more, the system flags it immediately. As your freelance PPC expert, I review every alert and act fast. You're never left wondering what happened.`

**Can you take over an existing account or do you start from scratch?**
`Both. Most clients come to me with existing Google Ads accounts. As a freelance PPC consultant, I start with a 2-week onboarding audit — fixing tracking, restructuring where needed, and building a clear optimisation plan before making any changes.`

**Can you work with my existing agency or team?**
`Yes. Some clients use me as their dedicated Google Ads freelancer while keeping their broader agency for other channels. I can work alongside existing teams with clear scope separation.`

**What's the minimum commitment?**
`There's no minimum contract. I don't believe in locking clients in. As a freelance PPC manager, I'd rather earn your trust month by month. Most clients stay long-term because the results speak for themselves.`

---

## SUCCESS CRITERIA

- [ ] "Uk" → "UK" in hero tag
- [ ] Hero subtext contains "Google Ads freelancer" and "freelance PPC expert"
- [ ] "What you get" intro contains "freelance PPC manager"
- [ ] Card 1 body contains "freelance PPC manager"
- [ ] Card 2 body contains "Google Ads freelancer"
- [ ] About me paragraph 1 contains "freelance PPC consultant" and "freelance PPC manager"
- [ ] About me paragraph 3 contains "freelance PPC expert"
- [ ] New "Freelance PPC services" section visible between "What you get" and "About me"
- [ ] New section contains: freelance PPC manager, freelance PPC consultant, freelance Google Ads manager, freelance PPC expert, PPC freelancer
- [ ] "Why not an agency" H2 updated
- [ ] All 9 FAQ answers present in DOM on page load (not dynamically injected)
- [ ] Page loads without errors
- [ ] No console errors
- [ ] Mobile layout correct

---

## AFTER BUILD

Christopher to confirm in Opera, then run:
```powershell
cd C:\Users\User\Desktop\act-website
git add .
git commit -m "Improve ppc-freelancer QS — keyword density, new services section, FAQ answers"
git push origin master
```
