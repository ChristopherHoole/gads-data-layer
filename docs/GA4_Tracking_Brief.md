# CLAUDE CODE BRIEF — GA4 + WhatsApp + Phone + Form Tracking
**Date:** 2026-03-19
**Priority:** HIGH
**Estimated Time:** 1–2 hours

---

## CONTEXT

GA4 account just created. Measurement ID is G-YK75LP5620. The existing Google Ads tag (AW-18006514629) is already in layout.tsx but GA4 needs its own separate tag added. We also need to track WhatsApp button clicks, phone number clicks, and form submissions as events — both in GA4 and as Google Ads conversions.

---

## OBJECTIVE

Add GA4 tracking to the website and fire click/submission events on all conversion points so we can attribute enquiries to specific traffic sources and buttons.

---

## FILES TO EDIT

- `C:\Users\User\Desktop\act-website\app\layout.tsx` — add GA4 tag
- `C:\Users\User\Desktop\act-website\app\page.tsx` — homepage WhatsApp + phone tracking
- `C:\Users\User\Desktop\act-website\app\ppc-freelancer\page.tsx` — PPC freelancer page WhatsApp + phone + form tracking

---

## CHANGE 1 — Add GA4 tag to layout.tsx

The existing layout.tsx already has the Google Ads tag loading via Next.js Script component. Find the existing google-ads-gtag script block which contains:
```
gtag('config', 'AW-18006514629');
```

Add one line to also configure GA4:
```javascript
gtag('config', 'AW-18006514629');
gtag('config', 'G-YK75LP5620');
```

That's the only change to layout.tsx.

---

## CHANGE 2 — WhatsApp click tracking helper function

In BOTH page.tsx files (homepage and ppc-freelancer), add this helper function at the top of the component:

```javascript
const trackWhatsApp = (label: string) => {
  if (typeof window !== 'undefined' && (window as any).gtag) {
    (window as any).gtag('event', 'whatsapp_click', {
      event_category: 'engagement',
      event_label: label,
    });
    (window as any).gtag('event', 'conversion', {
      send_to: 'AW-18006514629/whatsapp_click',
      event_label: label,
    });
  }
};
```

---

## CHANGE 3 — Add onClick to every WhatsApp link on ppc-freelancer/page.tsx

There are 4 WhatsApp links on the ppc-freelancer page. Add onClick to each with a unique label:

1. Hero section WhatsApp button — `'ppc-freelancer - hero'`
2. Contact section green WhatsApp button — `'ppc-freelancer - contact'`
3. Floating WhatsApp button (fixed bottom right) — `'ppc-freelancer - floating'`
4. Footer WhatsApp button — `'ppc-freelancer - footer'`

For each link add:
```jsx
onClick={() => trackWhatsApp('ppc-freelancer - contact')}
```
Changing the label per button as listed above.

---

## CHANGE 4 — Add onClick to every WhatsApp link on homepage (page.tsx)

Same pattern. Find all WhatsApp links on the homepage and add onClick with these labels:
1. Hero WhatsApp button — `'homepage - hero'`
2. Contact section WhatsApp button — `'homepage - contact'`
3. Floating WhatsApp button — `'homepage - floating'`
4. Footer WhatsApp button — `'homepage - footer'`
5. Any additional WhatsApp buttons — label them logically by section

---

## CHANGE 5 — Phone number click tracking

Add this helper in both page files:

```javascript
const trackPhone = (page: string) => {
  if (typeof window !== 'undefined' && (window as any).gtag) {
    (window as any).gtag('event', 'phone_click', {
      event_category: 'engagement',
      event_label: page,
    });
  }
};
```

Find every phone number link on both pages and add onClick:
```jsx
onClick={() => trackPhone('ppc-freelancer')}
```
Use `'homepage'` for homepage phone links.

---

## CHANGE 6 — Form submission tracking on ppc-freelancer/page.tsx

Add this handler:

```javascript
const trackFormSubmit = () => {
  if (typeof window !== 'undefined' && (window as any).gtag) {
    (window as any).gtag('event', 'form_submit', {
      event_category: 'conversion',
      event_label: 'ppc-freelancer - contact form',
    });
    (window as any).gtag('event', 'conversion', {
      send_to: 'AW-18006514629/fxGxCNeunoYcEMW3lopD',
      value: 40.0,
      currency: 'GBP',
    });
  }
};
```

Add `onSubmit={trackFormSubmit}` to the form element.

---

## SUCCESS CRITERIA

- [ ] `gtag('config', 'G-YK75LP5620')` present in layout.tsx
- [ ] All 4 WhatsApp buttons on ppc-freelancer have onClick with unique labels
- [ ] All WhatsApp buttons on homepage have onClick with unique labels
- [ ] Phone links have onClick tracking on both pages
- [ ] Contact form has onSubmit tracking
- [ ] No console errors
- [ ] Pages load correctly
- [ ] No TypeScript errors

---

## AFTER BUILD

Christopher confirms in Opera, then:
```powershell
cd C:\Users\User\Desktop\act-website
git add .
git commit -m "Add GA4 tracking + WhatsApp click events + phone + form tracking"
git push origin master
```
