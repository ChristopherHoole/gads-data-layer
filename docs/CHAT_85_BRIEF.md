# CHAT 85: SEO — META TAGS, OPEN GRAPH, SITEMAP, ROBOTS

**Date:** 2026-03-11
**Estimated Time:** 1–2 hours
**Priority:** HIGH
**Dependencies:** None

---

## CONTEXT

The marketing website christopherhoole.online is live on Vercel (Next.js 14). It currently has no meta tags, no Open Graph data, no sitemap and no robots.txt. Sharing the URL on LinkedIn or WhatsApp shows a broken preview card. Google has no structured way to crawl the site. This task adds all SEO foundations in one pass.

## OBJECTIVE

Add meta tags, Open Graph preview, Twitter card, sitemap.xml and robots.txt to christopherhoole.online so the site ranks and previews correctly.

---

## BUILD PLAN

### Step 1 — Create OG image
Use Python + Pillow to load `public/chris_headshot_1.jpg`, crop/resize to exactly 1200×630px, save as `public/og-image.jpg`. Centre the crop on the face.

### Step 2 — Update layout.tsx
Add `Metadata` import from `"next"`. Add `metadata` export object above the default export with: title, description, metadataBase, openGraph (title, description, url, siteName, images, type), twitter card fields.

### Step 3 — Create app/sitemap.ts
Next.js 14 native sitemap file. Returns one entry for the homepage with `changeFrequency: "monthly"` and `priority: 1`.

### Step 4 — Create app/robots.ts
Next.js 14 native robots file. Allows all crawlers (`*`), points to sitemap at `https://www.christopherhoole.online/sitemap.xml`.

### Step 5 — Verify
Run `npm run build` — must complete with zero errors. Confirm sitemap and robots routes resolve.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\act-website\public\og-image.jpg` — CREATE
   - 1200×630px crop of chris_headshot_1.jpg, face centred

2. `C:\Users\User\Desktop\act-website\app\layout.tsx` — MODIFY
   - Add Metadata import and metadata export with all OG + Twitter fields

3. `C:\Users\User\Desktop\act-website\app\sitemap.ts` — CREATE
   - Next.js 14 native sitemap, single homepage entry

4. `C:\Users\User\Desktop\act-website\app\robots.ts` — CREATE
   - Next.js 14 native robots, allow all, link to sitemap

5. `C:\Users\User\Desktop\act-website\docs\CHAT_85_HANDOFF.md` — CREATE
   - Technical handoff document

6. `C:\Users\User\Desktop\act-website\docs\CHAT_85_SUMMARY.md` — CREATE
   - Executive summary

---

## REQUIREMENTS

### Metadata values
- **Title:** `Christopher Hoole — Senior Google Ads Specialist`
- **Description:** `Senior Google Ads Specialist with 16 years experience. Builder of A.C.T — an AI-powered Google Ads optimisation platform.`
- **metadataBase:** `https://www.christopherhoole.online`
- **OG image:** `/og-image.jpg` — 1200×630, alt: `Christopher Hoole — Senior Google Ads Specialist`
- **OG type:** `website`
- **OG siteName:** `Christopher Hoole`
- **Twitter card:** `summary_large_image`

### Technical
- Use Next.js 14 native `Metadata` type — no third-party libraries
- `sitemap.ts` and `robots.ts` go in `app/` directory (not `pages/`)
- OG image created with Pillow — install if not present
- `npm run build` must pass with zero errors before reporting complete
- Do NOT modify any component files — layout.tsx only for the metadata

### Constraints
- Website uses Next.js 14, Tailwind CSS, deployed on Vercel
- Repo is at `C:\Users\User\Desktop\act-website`
- Do not touch `components/` files
- Do not touch `next.config.js` unless build fails and it is the only fix

---

## SUCCESS CRITERIA

- [ ] `npm run build` completes with zero errors
- [ ] `https://www.christopherhoole.online/sitemap.xml` resolves after deploy
- [ ] `https://www.christopherhoole.online/robots.txt` resolves after deploy
- [ ] Pasting URL into https://www.opengraph.xyz shows correct title, description and headshot image
- [ ] `og-image.jpg` exists in `public/` at 1200×630px
- [ ] No existing page layout or styling broken

ALL must pass before reporting complete.

---

## REFERENCE FILES

- `C:\Users\User\Desktop\act-website\app\layout.tsx` — Current layout, add metadata here
- `C:\Users\User\Desktop\act-website\public\chris_headshot_1.jpg` — Source image for OG crop

---

## TESTING

1. Run `npm run build` — paste the output. Must show zero errors.
2. Confirm `app/sitemap.ts` and `app/robots.ts` exist.
3. Confirm `public/og-image.jpg` exists and is 1200×630px.
4. Report the exact metadata object added to layout.tsx.
