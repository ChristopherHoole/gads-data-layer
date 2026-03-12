# CHAT 86: WHATSAPP UNIQUE MESSAGES + FLOATING BUTTON

**Date:** 2026-03-11
**Estimated Time:** 1–2 hours
**Priority:** HIGH
**Dependencies:** None

---

## CONTEXT

The website christopherhoole.online has 3 existing WhatsApp buttons — one in ContactForm.tsx and two in Footer.tsx. All 3 currently use the identical pre-filled message, making it impossible to track which button a lead clicked. A 4th floating button also needs to be added. Each button must have a unique message so Christopher can identify the source in WhatsApp.

## OBJECTIVE

Give each of the 3 existing WhatsApp buttons a unique pre-filled message and add a new fixed floating WhatsApp button in the bottom-right corner with its own unique message.

---

## BUILD PLAN

### Step 1 — Update ContactForm.tsx
Replace the existing `WA_URL` constant with the contact-section-specific message.

### Step 2 — Update Footer.tsx
The file currently has one `WA_URL` constant used by both footer buttons. Split into two separate constants — `WA_URL_BRAND` for the brand statement button and `WA_URL_FOOTER` for the Get in Touch column button. Update both usages accordingly.

### Step 3 — Create WhatsAppFloat.tsx
New component. Fixed position bottom-right. Green circle button with WhatsApp SVG icon. Links to floating button message. Subtle CSS pulse animation. Must sit above all other content (z-50 minimum).

### Step 4 — Update page.tsx
Import `WhatsAppFloat` and add `<WhatsAppFloat />` inside the `<main>` block.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\act-website\components\ContactForm.tsx` — MODIFY
   - Update `WA_URL` to contact form message

2. `C:\Users\User\Desktop\act-website\components\Footer.tsx` — MODIFY
   - Split single `WA_URL` into `WA_URL_BRAND` and `WA_URL_FOOTER`
   - Update both button usages

3. `C:\Users\User\Desktop\act-website\components\WhatsAppFloat.tsx` — CREATE
   - Fixed bottom-right floating button with floating message

4. `C:\Users\User\Desktop\act-website\app\page.tsx` — MODIFY
   - Import and render `<WhatsAppFloat />`

5. `C:\Users\User\Desktop\act-website\docs\CHAT_86_HANDOFF.md` — CREATE
6. `C:\Users\User\Desktop\act-website\docs\CHAT_86_SUMMARY.md` — CREATE

---

## REQUIREMENTS

### WhatsApp URLs (URL-encoded exactly as shown)

**ContactForm.tsx — WA_URL:**
```
https://wa.me/447999500184?text=Hi%20Christopher%2C%20I%20found%20your%20contact%20form%20and%20I%27d%20like%20to%20discuss%20my%20Google%20Ads.
```

**Footer.tsx — WA_URL_BRAND (brand statement button):**
```
https://wa.me/447999500184?text=Hi%20Christopher%2C%20I%20saw%20your%20website%20and%20I%27d%20like%20to%20discuss%20my%20Google%20Ads.
```

**Footer.tsx — WA_URL_FOOTER (Get in Touch column button):**
```
https://wa.me/447999500184?text=Hi%20Christopher%2C%20I%20found%20your%20details%20in%20the%20footer%20and%20I%27d%20like%20to%20discuss%20my%20Google%20Ads.
```

**WhatsAppFloat.tsx — floating button:**
```
https://wa.me/447999500184?text=Hi%20Christopher%2C%20I%27d%20like%20to%20discuss%20my%20Google%20Ads%20account.
```

### WhatsAppFloat.tsx design
- Fixed position: bottom-right, `bottom-6 right-6`
- Green circle: `bg-[#25D366]` hover `bg-[#1eb857]`
- Size: 56×56px (`w-14 h-14`)
- WhatsApp SVG icon in white, ~28px
- Pulse animation: subtle green ring using Tailwind `animate-ping` on an absolute pseudo-element
- `z-50`, `target="_blank"`, `rel="noopener noreferrer"`
- `"use client"` directive at top

### Technical
- All existing button text, styling and layout must remain unchanged — only the href URLs change
- `npm run build` must pass with zero errors
- Do not modify any CSS files or globals

---

## SUCCESS CRITERIA

- [ ] ContactForm WhatsApp button opens with contact form message
- [ ] Footer brand statement button opens with website message
- [ ] Footer Get in Touch button opens with footer message
- [ ] Floating button visible bottom-right on all sections
- [ ] Floating button opens with floating message
- [ ] Pulse animation visible on floating button
- [ ] `npm run build` completes with zero errors
- [ ] No existing styles or layouts broken

ALL must pass before reporting complete.

---

## REFERENCE FILES

- `C:\Users\User\Desktop\act-website\components\ContactForm.tsx` — Current contact form with existing WA_URL
- `C:\Users\User\Desktop\act-website\components\Footer.tsx` — Current footer with existing WA_URL used by 2 buttons
- `C:\Users\User\Desktop\act-website\app\page.tsx` — Add WhatsAppFloat import here

---

## TESTING

1. Run `npm run build` — paste output, must show zero errors
2. Run `npm run dev` and check all 4 buttons open WhatsApp with the correct unique message
3. Confirm floating button is visible in bottom-right on all scroll positions
4. Confirm pulse animation is visible
5. Report all 4 message texts confirmed
