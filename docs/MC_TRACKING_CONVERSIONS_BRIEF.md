# MC Tracking & Conversions — Master Brief
**Session:** MC Tracking & Conversions
**Date:** 2026-04-02
**Objective:** Audit and perfect all tracking across ChristopherHoole.com. Set up GTM, migrate GA4, configure conversion tracking for Google Ads, and meet the R$700 promo requirements before 1 May 2026.

---

## CRITICAL: BROWSER VERIFICATION REQUIRED

Every change must be verified by testing on the live/preview site. Confirm events fire in GA4 real-time reports and Google Ads conversion tracking before moving on.

---

## CRITICAL: ONE TASK AT A TIME

Complete each task fully and get confirmation before starting the next.

---

## Key Details

- **Site:** ChristopherHoole.com
- **Source code:** `C:\Users\User\Desktop\act-website` (Next.js + Tailwind, deployed via Vercel)
- **GA4 Property:** 529098983 (already linked to Google Ads)
- **Google Ads Account:** 487-268-1731
- **Current setup:** GA4 tag installed directly on site (no GTM)
- **Conversion actions needed:** Form submissions, WhatsApp button clicks
- **Promo deadline:** Log at least 1 conversion before 1 May 2026

---

## TASK 1: Audit Current GA4 Setup

Before changing anything, understand what's currently in place.

**Check:**
- How is the GA4 tag currently installed? (inline script, next/script, _app.js, layout.tsx?)
- What events are currently firing? (page_view, any custom events?)
- Is enhanced measurement enabled in GA4? (scroll, outbound clicks, site search, etc.)
- Are there any existing conversion actions in the Google Ads account?
- Is the GA4 ↔ Google Ads link active and working?
- Any existing remarketing tags?

**Output:** A clear list of what exists, what's working, what's missing.

**Browser-verify:** Open the site, check GA4 real-time reports to see what's firing right now.

---

## TASK 2: Create GTM Container and Install on Site

Set up Google Tag Manager and install it on ChristopherHoole.com.

**Steps:**
- Create a GTM container (or use existing if one exists)
- Install GTM on the Next.js site — this needs to handle client-side navigation properly
- For Next.js, use the `@next/third-parties` Google Tag Manager component or a similar approach that works with the App Router
- GTM snippet must go in the `<head>` (script) and after `<body>` (noscript)
- Verify GTM is loading by checking GTM preview mode

**Important:** Do NOT remove the existing GA4 tag yet. We'll migrate it in the next task. Both can coexist briefly during testing.

**Browser-verify:** Open the site, open GTM preview mode, confirm the container is loading and firing.

---

## TASK 3: Migrate GA4 Tag into GTM

Move the GA4 tracking from the hardcoded site tag into GTM.

**Steps:**
- Create a GA4 Configuration tag in GTM with measurement ID for property 529098983
- Set trigger to fire on All Pages
- Publish the GTM container
- Remove the old hardcoded GA4 tag from the Next.js source code
- Deploy the site update

**Verify carefully:** There must be zero gap in tracking. Check GA4 real-time reports before and after to confirm page views continue flowing.

**Browser-verify:** Navigate around the site, check GA4 real-time shows page views, confirm no duplicate events (which would mean old tag wasn't removed).

---

## TASK 4: Set Up Form Submission Tracking

Track when someone submits the contact/enquiry form on ChristopherHoole.com.

**Steps:**
- Identify how the form currently works (what happens on submit? redirect? AJAX? thank-you page?)
- Create a custom event in GTM that fires on successful form submission
- Push a `form_submit` (or similar) event to the dataLayer on successful submission
- Create a GA4 Event tag in GTM that sends this event to GA4
- Mark this event as a conversion in GA4
- Create a matching Google Ads conversion action in account 487-268-1731
- Add a Google Ads Conversion Tracking tag in GTM for this action

**Browser-verify:** Submit a test form. Check:
1. GA4 real-time → event appears
2. GA4 conversions → marked as conversion
3. Google Ads → conversion action shows "Recording" status (may take a few hours)

---

## TASK 5: Set Up WhatsApp Button Click Tracking

Track when someone clicks the WhatsApp button on ChristopherHoole.com.

**Steps:**
- Identify the WhatsApp button element (class, ID, or href pattern like `wa.me` or `api.whatsapp.com`)
- Create a GTM trigger that fires on clicks matching the WhatsApp button
- Create a GA4 Event tag that sends a `whatsapp_click` event
- Mark this event as a conversion in GA4
- Create a matching Google Ads conversion action in account 487-268-1731
- Add a Google Ads Conversion Tracking tag in GTM for this action

**Browser-verify:** Click the WhatsApp button. Check:
1. GTM preview mode shows the trigger fired
2. GA4 real-time → `whatsapp_click` event appears
3. Google Ads → conversion action shows "Recording" status

---

## TASK 6: Verify Google Ads Conversion Import and Promo Requirements

Make sure everything is connected and the R$700 promo conditions are met.

**Check:**
- GA4 property 529098983 is linked to Google Ads account 487-268-1731
- Both conversion actions (form submit + WhatsApp click) are visible in Google Ads → Goals → Conversions
- At least one conversion action is set as Primary (for bidding)
- Google tag is placed (via GTM) — this satisfies promo requirement 1
- Test that a real conversion logs — this satisfies promo requirement 2 (must happen before 1 May 2026)

**Browser-verify:** Submit a form or click WhatsApp, wait for it to appear in Google Ads conversion tracking.

---

## TASK 7: End-to-End Test

Full test of everything working together.

**Test sequence:**
1. Open ChristopherHoole.com in an incognito window
2. Navigate to 2-3 pages (confirm page_view events in GA4 real-time)
3. Click the WhatsApp button (confirm whatsapp_click event in GA4)
4. Submit the contact form (confirm form_submit event in GA4)
5. Check GTM preview mode — all tags fired correctly
6. Check Google Ads conversions — both actions show data
7. Confirm no console errors on the site
8. Confirm site performance hasn't degraded (GTM shouldn't slow things down noticeably)

**Browser-verify:** Everything fires, no errors, no performance issues.

---

## SESSION SUMMARY

| # | Task | Category |
|---|------|----------|
| 1 | Audit current GA4 setup | Audit |
| 2 | Create GTM container and install on site | Setup |
| 3 | Migrate GA4 tag into GTM | Migration |
| 4 | Form submission conversion tracking | Tracking |
| 5 | WhatsApp button click tracking | Tracking |
| 6 | Verify Google Ads conversion import + promo | Verification |
| 7 | End-to-end test | Testing |

**TOTAL: 7 tasks, executed in order, one at a time.**

**Promo deadline: 1 conversion must log before 1 May 2026.**

---

**END OF BRIEF**
