# CHAT 31 BRIEF — Marketing Website (christopherhoole.online)

**Module:** Marketing Website
**Scope:** Complete 1-page marketing site for Christopher Hoole (CV/portfolio angle)
**Tech Stack:** Next.js 14, Tailwind CSS, Framer Motion, shadcn/ui, Three.js (hero only)
**Hosting:** Vercel
**Domain:** christopherhoole.online
**Last Updated:** 2026-02-23

---

## 🚨 MANDATORY FIRST STEP

Before doing anything, request 4 uploads from Christopher:

```
Before I begin, I need 4 mandatory uploads:

1. CHAT_31_BRIEF.md (this file)
   Complete specifications for the website

2. CHAT_31_WIREFRAME_LIGHTWEIGHT.html
   Design reference with all content

3. chris_headshot_1.jpg
   Christopher's professional photo

4. ACT_headshot_1.jpg
   A.C.T robot image

Note: CHAT_WORKING_RULES.md is optional for this chat (building new project, not modifying ACT)
```

**After all 4 uploaded:**
1. Read CHAT_31_BRIEF.md completely
2. Open CHAT_31_WIREFRAME_LIGHTWEIGHT.html to see structure/content
3. Note: Images are provided as JPEG files (not base64)
4. THEN proceed to 5 Questions (Rule 5)

---

## 📋 CONTEXT

Christopher Hoole is a Senior Google Ads Specialist with 16 years of experience. He's built a proprietary AI engine called "Ads Control Tower (A.C.T)" that automates Google Ads optimization.

This website serves as:
- **Personal portfolio/CV site** (not a corporate SaaS site)
- **Lead generation** for agency partnerships and direct clients
- **Gateway to live Google Ads testing** (real traffic → real data → validates A.C.T)

**Target audience:** Digital marketing agencies (B2B outreach angle)

**Positioning:** "I'm Christopher Hoole, 16-year specialist who built my own AI engine because most managers work the same way"

---

## 🎯 WHAT CHAT 31 BUILDS

### **Deliverables:**

1. **Next.js 14 project** with App Router
2. **13-section single-page site** (see wireframe reference)
3. **Three.js interactive hero** (headshot ↔ robot reveal on hover)
4. **Contact form** that POSTs to A.C.T `/api/leads` endpoint
5. **Production-ready deployment** to Vercel
6. **Domain connection guide** for christopherhoole.online

---

## 🔒 APPROVED WIREFRAME

**Reference file:** `CHAT_31_WIREFRAME_LIGHTWEIGHT.html`

This is the lightweight version (images removed to save context space).
Actual images are provided as JPEG files: `chris_headshot_1.jpg` and `ACT_headshot_1.jpg`.

**This is the locked design specification.**

**Do NOT deviate from:**
- Section order (1-13)
- Content structure
- Hero Three.js implementation
- Form fields
- Visual style (dark hero, professional, Option A from scoping)

---

## 🏗️ TECH STACK (NON-NEGOTIABLE)

### **Framework:**
- Next.js 14 (App Router)
- TypeScript
- React 18

### **Styling:**
- Tailwind CSS (primary)
- Framer Motion (scroll animations only)
- shadcn/ui components (optional, use sparingly)

### **Hero Effect:**
- Three.js r128 (CDN: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js)
- WebGL shaders (exact implementation in wireframe)

### **Hosting:**
- Vercel (free tier initially)
- GitHub repo for version control

### **Domain:**
- christopherhoole.online (Christopher owns this)
- DNS setup instructions required

---

## 📐 SITE STRUCTURE (13 SECTIONS)

### **S1: Hero** (Dark background #0f172a)
- **Layout:** Side-by-side (text left, image right)
- **Text content:**
  - Eyebrow: "Senior Google Ads Specialist"
  - H1: "I'm Christopher Hoole" (blue accent)
  - H2: "Google Ads, Managed with AI Precision."
  - Body: "16 years of paid ads experience. One proprietary AI engine. Most managers work the same way, so I built my own AI engine."
  - CTAs: "Let's Discuss Your Paid Ads" (primary) + "See How It Works ↓" (secondary)
  - Footer: "Maximum 4 clients. Currently accepting agency partnerships."
- **Hero effect:**
  - 380x460px container
  - Three.js WebGL canvas
  - Default: Christopher's headshot
  - On hover: Brush reveal effect shows A.C.T robot
  - Exact implementation in wireframe (copy verbatim)
  - **Images:** Extract base64 strings from `CHAT_31_FINAL_WIREFRAME.html` (see instructions below)

### **S2: About Me** (Dark #0f172a)
- Eyebrow: "About Me"
- H2: "I've managed Google Ads accounts since 2009."
- 4 paragraphs (see wireframe for exact copy)

### **S3: The Problem** (Light #ffffff)
- Eyebrow: "The Problem"
- H2: "Most Google Ads management looks the same."
- 3-card grid (icons + titles + descriptions)

### **S4: The Difference** (Dark #0f172a)
- Eyebrow: "The Difference"
- H2: "16 years operator judgment + proprietary AI = your edge."
- 3 paragraphs

### **S5: Work History** (Light #ffffff)
- Eyebrow: "Work History"
- H2: "16 years across agencies, in-house, and my own consultancy."
- Timeline layout (7 roles, 2009-2025)
- Each entry: Year | Title | Company | Description

### **S6: Skills & Platforms** (Dark #0f172a)
- Eyebrow: "Skills & Platforms"
- H2: "Technical expertise across the full paid ads stack."
- 8-card grid (4 columns × 2 rows)
- Categories: Paid Advertising, Analytics, CRM, E-commerce, AI, Budget Management, Industries, Languages

### **S7: What A.C.T Does** (Light #ffffff)
- Eyebrow: "What A.C.T Does"
- H2: "Four AI-powered modules. All features live and operational."
- 4 module cards (2×2 grid)
  - Lighthouse (Diagnostics & Insights)
  - Radar (Monitoring & Protection)
  - Flight Plan (Experiments & Testing)
  - Autopilot (AI-Powered Optimization)
- Additional capabilities box below

### **S8: How I Work** (Dark #0f172a)
- Eyebrow: "How I Work"
- H2: "10-hour blocks. Maximum 4 clients. Senior attention only."
- 4-card grid (2×2)

### **S9: What You Get Each Week** (Light #ffffff)
- Eyebrow: "What You Get Each Week"
- H2: "Clear deliverables. No jargon. Full transparency."
- 6 day blocks (Monday-Friday + Monthly)

### **S10: Why I'm Different** (Light alt #f1f5f9)
- Eyebrow: "Why I'm Different"
- H2: "Explainability by default. Not by request."
- 16 USP cards (3-column grid)

### **S11: FAQ** (Light #ffffff)
- Eyebrow: "FAQ"
- H2: "Common questions."
- 10 Q&A pairs (single column list)

### **S12: CTA + Contact Form** (Dark #0f172a)
- Eyebrow: "Let's Talk"
- H2: "Let's Discuss Your Paid Ads"
- Layout: 2-column (form left, next steps right)
- **Form fields:**
  1. Name * (text input)
  2. Company Name * (text input)
  3. Role * (dropdown: Agency owner / PPC lead / Marketing director / Other)
  4. Looking for * (dropdown: Freelancer / Partner / White-label / Consultation)
  5. Email * (email input)
  6. Phone number (optional) (tel input)
- Submit button: "Submit Application"
- **Form action:** POST to A.C.T API `/api/leads`
  - Endpoint: `{ACT_API_URL}/api/leads` (env var)
  - Local dev: http://localhost:5000/api/leads
  - Production: Christopher will provide URL
- Next steps: 3-step visual (numbered circles with descriptions)

### **S13: Footer** (Dark #0a0a1a)
- Minimal layout
- Left: "Christopher Hoole · © 2026"
- Right: "LinkedIn · chrishoole101@gmail.com · Built with A.C.T"

---

## 🎨 DESIGN SYSTEM

### **Colors:**
```
Primary Blue: #2563eb
Dark BG: #0f172a
Darker BG: #0a0a1a
Light BG: #ffffff
Light Alt BG: #f1f5f9
Text Light: #f1f5f9
Text Dark: #0f172a
Text Muted Light: #94a3b8
Text Muted Dark: #64748b
Border Light: #e2e8f0
Border Dark: #334155
```

### **Typography:**
- **Headings:** Georgia, serif (or similar display serif)
- **Body:** System font stack or DM Sans
- **Monospace:** Courier New (for labels, eyebrows, CTAs)

### **Spacing:**
- Section padding: 80px vertical
- Max content width: 1200px
- Container padding: 80px horizontal (desktop), 24px (mobile)

### **Responsive:**
- Desktop: 1200px+ (default)
- Tablet: 768px-1199px (2-col → 1-col grids)
- Mobile: <768px (all single column, nav hamburger)

---

## 🔧 TECHNICAL REQUIREMENTS

### **Three.js Hero Implementation:**

**CRITICAL:** Copy the exact script from `CHAT_31_WIREFRAME_LIGHTWEIGHT.html` verbatim.

**Key specifications:**
- Container: 380×460px
- POINTER_RADIUS: 0.28
- POINTER_DURATION: 2.5s
- Mouse tracking: `getBoundingClientRect()` for accurate offset
- Ping-pong render targets (not FramebufferTexture)
- Organic brush with noise-based edges
- 3 layers: base image (always visible) → liquid background (reveal zone) → robot image (reveal zone)

**Images:**

Christopher has provided 2 JPEG image files:
- `chris_headshot_1.jpg` - Christopher's professional headshot photo
- `ACT_headshot_1.jpg` - A.C.T robot image (blue-eyed robot)

**For the Hero component Three.js implementation:**

Save both JPEG files to `public/` in your Next.js project, then reference them in your Three.js code:

```typescript
const imgChris = new Image()
imgChris.src = '/chris_headshot_1.jpg'

const imgRobot = new Image()  
imgRobot.src = '/ACT_headshot_1.jpg'
```

This is the simplest approach and avoids base64 entirely. The images will load from the public directory.

### **Form Integration:**

**IMPORTANT:** The `/api/leads` endpoint does NOT exist yet. For this chat:
- Build the complete form UI with validation
- On submit: `console.log(formData)` and show success message
- Add TODO comment: `// TODO: POST to /api/leads when endpoint is ready`
- Christopher will build the actual API endpoint later in the A.C.T codebase

**Future API Endpoint Specification:**
```
POST {ACT_API_URL}/api/leads
Content-Type: application/json

Request body:
{
  "name": "string",
  "company_name": "string",
  "role": "string",
  "looking_for": "string",
  "email": "string",
  "phone": "string" // optional
}

Success response (200):
{
  "success": true,
  "lead_id": "uuid"
}

Error response (400/500):
{
  "success": false,
  "error": "message"
}
```

**Environment Variables:**
```
NEXT_PUBLIC_ACT_API_URL=http://localhost:5000 (dev)
NEXT_PUBLIC_ACT_API_URL=https://api.christopherhoole.online (prod - TBD)
```

**Form behavior:**
- Client-side validation (all required fields)
- Loading state on submit (disable button, show spinner)
- Success: Show inline message "Application received! I'll be in touch within 48 hours."
- Error: Show error message + fallback email link (chrishoole101@gmail.com)
- No redirect (stay on page)

### **Navigation:**

**Desktop:**
- Fixed top nav (56px height)
- Logo left: "Christopher Hoole"
- Links right: About | A.C.T | Experience | FAQ | CTA button
- Smooth scroll to sections (scroll-behavior: smooth or Framer Motion)
- Backdrop blur + semi-transparent background

**Mobile (<768px):**
- Hamburger menu icon
- Slide-in drawer or dropdown
- Links stack vertically

### **Animations:**

Use Framer Motion sparingly:
- Fade-up on scroll (section headings only)
- No heavy parallax or complex animations
- Performance > fancy effects

### **SEO & Meta:**

```html
<title>Christopher Hoole - Senior Google Ads Specialist</title>
<meta name="description" content="16 years of Google Ads experience with a proprietary AI engine (A.C.T). Maximum 4 clients. Agency partnerships available." />

<!-- Open Graph -->
<meta property="og:title" content="Christopher Hoole - Senior Google Ads Specialist" />
<meta property="og:description" content="16 years of Google Ads experience with a proprietary AI engine." />
<meta property="og:type" content="website" />
<meta property="og:url" content="https://christopherhoole.online" />

<!-- Favicon -->
<!-- Christopher will provide or use initials -->
```

---

## 📦 PROJECT STRUCTURE

```
act-website/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page (all 13 sections)
│   ├── globals.css         # Tailwind imports
│   └── api/
│       └── contact/
│           └── route.ts    # Proxy to A.C.T API (optional)
├── components/
│   ├── Hero.tsx            # S1 with Three.js
│   ├── AboutMe.tsx         # S2
│   ├── TheProblem.tsx      # S3
│   ├── TheDifference.tsx   # S4
│   ├── WorkHistory.tsx     # S5
│   ├── Skills.tsx          # S6
│   ├── WhatACTDoes.tsx     # S7
│   ├── HowIWork.tsx        # S8
│   ├── WeeklyDeliverables.tsx # S9
│   ├── WhyDifferent.tsx    # S10
│   ├── FAQ.tsx             # S11
│   ├── ContactForm.tsx     # S12
│   ├── Footer.tsx          # S13
│   └── Navigation.tsx      # Fixed nav
├── public/
│   ├── headshot.png        # (or base64 embedded)
│   └── robot.png           # (or base64 embedded)
├── lib/
│   └── utils.ts            # Helpers
├── tailwind.config.ts
├── next.config.js
├── package.json
└── .env.local              # NEXT_PUBLIC_ACT_API_URL
```

---

## 🧪 TESTING REQUIREMENTS

### **Before reporting complete:**

1. **Visual testing:**
   - Screenshot all 13 sections (desktop)
   - Screenshot mobile view (at least hero + form)
   - Confirm Three.js hero works (hover effect)

2. **Functional testing:**
   - Navigation links scroll to correct sections
   - Form validation works (required fields)
   - Form submission (test with console.log initially)
   - Responsive breakpoints (768px, 1200px)

3. **Browser testing:**
   - Opera (primary)
   - Chrome (fallback)

4. **Performance:**
   - Lighthouse score >90 (Performance)
   - First Contentful Paint <1.5s
   - Total page size <3MB

---

## 🚀 DEPLOYMENT WORKFLOW

### **Step 1: Local Development**

Christopher will run:
```powershell
cd C:\Users\User\Desktop\act-website
npm install
npm run dev
```

Open http://localhost:3000

### **Step 2: Vercel Deployment**

Provide exact commands:
```powershell
npm i -g vercel
vercel login
vercel
vercel --prod
```

### **Step 3: Domain Connection**

**DNS Records (Christopher's registrar):**
```
Type: A
Host: @
Value: 76.76.21.21

Type: CNAME
Host: www
Value: cname.vercel-dns.com
```

**In Vercel Dashboard:**
1. Project → Settings → Domains
2. Add: christopherhoole.online
3. Add: www.christopherhoole.online
4. Wait for SSL (automatic)

### **Step 4: Environment Variables**

In Vercel Dashboard → Settings → Environment Variables:
```
NEXT_PUBLIC_ACT_API_URL = https://api.christopherhoole.online (TBD)
```

---

## 📝 DELIVERABLES CHECKLIST

### **Code:**
- [ ] Complete Next.js 14 project
- [ ] All 13 sections implemented
- [ ] Three.js hero working (exact wireframe code)
- [ ] Contact form with A.C.T API integration
- [ ] Responsive (desktop + tablet + mobile)
- [ ] Navigation (fixed + smooth scroll)
- [ ] SEO meta tags
- [ ] Favicon (or placeholder)

### **Documentation:**
- [ ] README.md with setup instructions
- [ ] Environment variables documented
- [ ] Deployment guide (Vercel + domain)
- [ ] DNS configuration guide

### **Testing:**
- [ ] Desktop screenshots (all sections)
- [ ] Mobile screenshots (hero + form minimum)
- [ ] Browser testing (Opera + Chrome)
- [ ] Form submission tested
- [ ] Navigation tested
- [ ] Performance validated

---

## 🚨 CRITICAL CONSTRAINTS

### **DO:**
- ✅ Copy Three.js code from wireframe EXACTLY
- ✅ Use full Windows paths when referencing files
- ✅ Provide complete files (not code snippets)
- ✅ Test everything before reporting complete
- ✅ Match wireframe design precisely
- ✅ Use Tailwind for all styling
- ✅ Keep dependencies minimal

### **DO NOT:**
- ❌ Change section order or content
- ❌ Add features not in the brief
- ❌ Use different tech stack
- ❌ Skip responsive design
- ❌ Skip form integration
- ❌ Use jQuery or other heavy libraries
- ❌ Modify Three.js implementation (copy as-is)

---

## 🎯 SUCCESS CRITERIA

**This chat is complete when:**

1. ✅ Full Next.js project created
2. ✅ All 13 sections match wireframe
3. ✅ Three.js hero works on hover
4. ✅ Contact form POSTs to A.C.T API
5. ✅ Responsive on all breakpoints
6. ✅ Tested in Opera
7. ✅ Deployed to Vercel (or ready to deploy)
8. ✅ Domain connection guide provided
9. ✅ All files in outputs directory
10. ✅ Screenshots confirm visual accuracy

---

## 📞 QUESTIONS FOR MASTER CHAT

After reading all docs, send exactly 5 questions to Master Chat following Rule 5 format:

```
5 QUESTIONS FOR MASTER CHAT

Q1. [CATEGORY] Question text here?
Q2. [CATEGORY] Question text here?
Q3. [CATEGORY] Question text here?
Q4. [CATEGORY] Question text here?
Q5. [CATEGORY] Question text here?

Waiting for Master Chat answers before proceeding.
```

**Example categories:** [IMAGES], [API], [DEPLOYMENT], [DESIGN], [SCOPE]

---

**Version:** 1.0
**Last Updated:** 2026-02-23
**Approved by:** Christopher Hoole (Master Chat 4.0)

**END OF BRIEF**
