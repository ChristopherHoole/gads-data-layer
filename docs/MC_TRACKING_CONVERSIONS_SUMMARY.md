# MC Tracking & Conversions — Session Summary
**Session:** MC Tracking & Conversions
**Date:** 2026-04-02
**Duration:** ~2 hours
**Site:** ChristopherHoole.com (Next.js + Tailwind, Vercel)
**Source code:** `C:\Users\User\Desktop\act-website`

---

## Objective

Audit and perfect all tracking across ChristopherHoole.com. Set up GTM, migrate GA4, configure conversion tracking for Google Ads, and meet the R$700 promo requirements before 1 May 2026.

---

## What Was Done — 7 Tasks Completed

### Task 1: Audit Current GA4 Setup
**Status:** Complete

Audited the entire act-website codebase and verified against live GA4/Google Ads dashboards.

**Findings:**
- GA4 (`G-YK75LP5620`) was installed via hardcoded `<Script>` tags in `app/layout.tsx`
- Google Ads (`AW-18006514629`) also hardcoded alongside GA4
- 4 custom events already coded: `whatsapp_click`, `form_submit`, `phone_click`, `conversion`
- Google Ads conversion tracking existed in code for form submit (`AW-18006514629/fxGxCNeunoYcEMW3lopD`, GBP 40 value)
- LinkedIn Insight Tag (partner ID: 9697497) also present
- No GTM — everything was hardcoded, requiring code deploys for any tracking changes
- GA4 enhanced measurement was ON (page views, scrolls, outbound clicks + more)
- GA4 ↔ Google Ads link was active (since 19 Mar 2026)
- 2 existing Google Ads conversion actions — both showing 0 conversions, "Submit lead form" status "Needs attention"
- No WhatsApp conversion action existed in Google Ads

---

### Task 2: Create GTM Container and Install on Site
**Status:** Complete

**What was done:**
- Created GTM account: `ChristopherHoole.com`
- Container ID: **GTM-5LCX83NS**
- Installed `@next/third-parties` npm package (v16.2.2) — the official Next.js GTM integration
- Added `<GoogleTagManager gtmId="GTM-5LCX83NS" />` to `app/layout.tsx`
- Added `<noscript>` iframe fallback inside `<body>`
- Kept existing hardcoded GA4/Google Ads tags during transition

**Commits:**
- `19cf3c1` — Add GTM container GTM-5LCX83NS via @next/third-parties

**Verification:** GTM Preview confirmed container loading, all lifecycle events firing (Consent Initialisation → Initialisation → Container loaded → DOM Ready → Window Loaded).

---

### Task 3: Migrate GA4 Tag into GTM
**Status:** Complete

**What was done in GTM:**
- Created `Google Ads - Config` tag (Google Tag, AW-18006514629, All Pages trigger)
- Created `GA4 - Config` tag (Google Tag, G-YK75LP5620, All Pages trigger)
- Published GTM container

**What was done in code:**
- Removed hardcoded GA4/Google Ads `<Script>` tags from `app/layout.tsx`
- LinkedIn Insight Tag remained hardcoded (not managed via GTM)
- Existing `gtag()` calls in components continue to work via GTM's Google tag

**Commits:**
- `88129eb` — Remove hardcoded GA4/Google Ads tags — now managed via GTM

**Verification:** GTM Preview confirmed both tags firing from GTM (not hardcoded). GA4 real-time showed page views flowing. No duplicate events detected.

---

### Task 4: Set Up Form Submission Tracking
**Status:** Complete

**What was done in code:**
- Replaced all direct `gtag('event', 'form_submit', ...)` and `gtag('event', 'conversion', ...)` calls with `dataLayer.push({ event: 'form_submit', ... })`
- Updated 9 files total:
  - `components/ContactForm.tsx`
  - `app/ppc-freelancer/page.tsx`
  - `app/ppc-freelancer1/page.tsx`
  - `app/ppc-google-ads-agency/page.tsx`
  - `app/ppc-google-ads-agency-partner/page.tsx`
  - `app/ppc-google-ads-management-manager/page.tsx`
  - `app/ppc-google-adwords-consultant/page.tsx`
  - `app/ppc-specialist-expert/page.tsx`
  - `app/white-label-outsource-google-ads-ppc/page.tsx`
- Each dataLayer push includes: `event`, `form_location` (page-specific label), `form_value` (40.00), `form_currency` (GBP)

**What was done in GTM:**
- Created trigger: `Form Submit - Custom Event` (Custom Event, event name: `form_submit`)
- Created variable: `DLV - form_location` (Data Layer Variable)
- Created tag: `GA4 - Form Submit` (GA4 Event, measurement ID G-YK75LP5620, event name `form_submit`, parameter `form_location`)
- Created tag: `Google Ads - Form Submit Conversion` (Conversion Tracking, ID: 18006514629, Label: `fxGxCNeunoYcEMW3lopD`, Value: 40, Currency: GBP)
- Created tag: `Conversion Linker` (All Pages) — required for Google Ads click attribution via gclid cookie

**What was done in GA4:**
- `form_submit` marked as a **key event**

**Commits:**
- `f618426` — Migrate form_submit tracking to dataLayer push for GTM

**Verification:** GTM Preview confirmed both `GA4 - Form Submit` and `Google Ads - Form Submit Conversion` tags fire on form submission. GA4 real-time showed `form_submit` events and key events counting.

---

### Task 5: Set Up WhatsApp Button Click Tracking
**Status:** Complete

**What was done in code:**
- Replaced all direct `gtag('event', 'whatsapp_click', ...)` and `gtag('event', 'conversion', ...)` calls with `dataLayer.push({ event: 'whatsapp_click', ... })`
- Updated 11 files total:
  - `components/WhatsAppFloat.tsx`
  - `components/ContactForm.tsx`
  - `components/Footer.tsx`
  - `app/ppc-freelancer/page.tsx`
  - `app/ppc-freelancer1/page.tsx`
  - `app/ppc-google-ads-agency/page.tsx`
  - `app/ppc-google-ads-agency-partner/page.tsx`
  - `app/ppc-google-ads-management-manager/page.tsx`
  - `app/ppc-google-adwords-consultant/page.tsx`
  - `app/ppc-specialist-expert/page.tsx`
  - `app/white-label-outsource-google-ads-ppc/page.tsx`
- Each dataLayer push includes: `event`, `click_location` (button-specific label, e.g. "homepage - floating", "homepage - footer")

**WhatsApp buttons tracked across the site:**
- Floating green button (bottom-right, all pages)
- Contact form section CTA
- Footer brand link
- Footer contact details WhatsApp link
- Footer mobile CTA
- PPC landing page hero, section, contact, sticky, and footer buttons

**What was done in Google Ads:**
- Created new conversion action: `WhatsApp Click` under "Contact" goal
  - Conversion ID: `18006514629`
  - Conversion Label: `hBelCOmpsZQcEMW3lopD`
  - Value: GBP 10
  - Count: Every
  - Click-through window: 30 days
  - Attribution: Data-driven
  - Action optimisation: Primary

**What was done in GTM:**
- Created trigger: `WhatsApp Click - Custom Event` (Custom Event, event name: `whatsapp_click`)
- Created variable: `DLV - click_location` (Data Layer Variable)
- Created tag: `GA4 - WhatsApp Click` (GA4 Event, measurement ID G-YK75LP5620, event name `whatsapp_click`, parameter `click_location`)
- Created tag: `Google Ads - WhatsApp Click Conversion` (Conversion Tracking, ID: 18006514629, Label: `hBelCOmpsZQcEMW3lopD`, Value: 10, Currency: GBP)

**What was done in GA4:**
- `whatsapp_click` marked as a **key event**

**Commits:**
- `8026fe5` — Migrate whatsapp_click tracking to dataLayer push for GTM

**Verification:** GA4 real-time confirmed `whatsapp_click` events appearing and counting as key events.

---

### Task 6: Verify Google Ads Conversion Import + Promo Requirements
**Status:** Complete (pending 24h processing)

**Google Ads conversion actions (final state):**

| Goal | Conversion Action | Source | Primary | Value | Count | Status |
|------|------------------|--------|---------|-------|-------|--------|
| Submit lead forms | Submit lead form | Website | Yes | GBP 40 | Every | Pending (was "Needs attention") |
| Submit lead forms | Lead form - Submit | Google hosted | Yes | 1 | One | No recent conversions |
| Contact | WhatsApp Click | Website | Yes | GBP 10 | Every | New — no recent conversions |

**Fixes applied:**
- "Submit lead form" value changed from R$1 (Brazilian Real) to GBP 40
- Enhanced conversions disabled on "Submit lead form" (was causing "Needs attention" warning)
- Payment method fixed (was showing "can't be charged" banner)

**Promo requirements status:**
- Requirement 1 (Google tag placed): **Met** — GTM installed and firing
- Requirement 2 (1 conversion before 1 May): **Pending** — test conversions fired today, need 24h for Google Ads processing. Real conversions from ad-clicking users will count once campaigns serve.

**GA4 ↔ Google Ads link:** Active since 19 Mar 2026, personalised advertising enabled, 5 user access roles configured.

---

### Task 7: End-to-End Test
**Status:** Complete

**Test performed in incognito window:**

| Check | Result |
|-------|--------|
| Page views tracking | `page_view`: 5 events in GA4 real-time |
| WhatsApp click tracking | `whatsapp_click`: 6 events, counting as key events |
| Form submit tracking | `form_submit`: 3 events, counting as key events |
| Enhanced measurement | `click`, `scroll`, `user_engagement`, `first_visit`, `session_start` all firing |
| GTM tags firing | All 7 tags fire correctly (2 config + conversion linker + 2 GA4 events + 2 Google Ads conversions) |
| Console errors | None reported |
| Site performance | No degradation noticed |

---

## Architecture — Before vs After

### Before (hardcoded)
```
app/layout.tsx
  └── <Script> gtag.js (AW-18006514629)
  └── <Script> gtag('config', 'AW-18006514629')
  └── <Script> gtag('config', 'G-YK75LP5620')
  └── <Script> LinkedIn Insight Tag

components/ContactForm.tsx
  └── gtag('event', 'form_submit', ...)
  └── gtag('event', 'conversion', { send_to: 'AW-.../fxGx...' })

components/WhatsAppFloat.tsx
  └── gtag('event', 'whatsapp_click', ...)
  └── gtag('event', 'conversion', { send_to: 'AW-.../whatsapp_click' })

[Same pattern in Footer.tsx + 8 PPC landing pages]
```

### After (GTM-managed)
```
app/layout.tsx
  └── <GoogleTagManager gtmId="GTM-5LCX83NS" />  (@next/third-parties)
  └── <noscript> GTM iframe fallback
  └── <Script> LinkedIn Insight Tag (still hardcoded)

GTM Container (GTM-5LCX83NS)
  ├── Tags
  │   ├── Google Ads - Config (AW-18006514629) → All Pages
  │   ├── GA4 - Config (G-YK75LP5620) → All Pages
  │   ├── Conversion Linker → All Pages
  │   ├── GA4 - Form Submit → form_submit trigger
  │   ├── Google Ads - Form Submit Conversion → form_submit trigger
  │   ├── GA4 - WhatsApp Click → whatsapp_click trigger
  │   └── Google Ads - WhatsApp Click Conversion → whatsapp_click trigger
  ├── Triggers
  │   ├── Form Submit - Custom Event (event: form_submit)
  │   └── WhatsApp Click - Custom Event (event: whatsapp_click)
  └── Variables
      ├── DLV - form_location
      └── DLV - click_location

components/ContactForm.tsx
  └── dataLayer.push({ event: 'form_submit', form_location, form_value, form_currency })

components/WhatsAppFloat.tsx
  └── dataLayer.push({ event: 'whatsapp_click', click_location })

[Same dataLayer pattern in Footer.tsx + 8 PPC landing pages]
```

---

## Git Commits (act-website repo)

| Commit | Message |
|--------|---------|
| `19cf3c1` | Add GTM container GTM-5LCX83NS via @next/third-parties |
| `88129eb` | Remove hardcoded GA4/Google Ads tags — now managed via GTM |
| `f618426` | Migrate form_submit tracking to dataLayer push for GTM |
| `8026fe5` | Migrate whatsapp_click tracking to dataLayer push for GTM |

---

## Key IDs Reference

| Item | ID |
|------|-----|
| GA4 Property | 529098983 |
| GA4 Measurement ID | G-YK75LP5620 |
| GA4 Stream ID | 14048087982 |
| Google Ads Account | 487-268-1731 |
| Google Ads Conversion ID | 18006514629 (AW-18006514629) |
| GTM Container | GTM-5LCX83NS |
| Form Submit Conversion Label | fxGxCNeunoYcEMW3lopD |
| WhatsApp Click Conversion Label | hBelCOmpsZQcEMW3lopD |
| LinkedIn Partner ID | 9697497 |

---

## Files Modified

All changes in `C:\Users\User\Desktop\act-website`:

| File | Change |
|------|--------|
| `package.json` | Added `@next/third-parties` dependency |
| `app/layout.tsx` | Replaced hardcoded GA4/Google Ads scripts with GTM component + noscript fallback |
| `components/ContactForm.tsx` | form_submit + whatsapp_click → dataLayer.push() |
| `components/WhatsAppFloat.tsx` | whatsapp_click → dataLayer.push() |
| `components/Footer.tsx` | whatsapp_click → dataLayer.push() |
| `app/ppc-freelancer/page.tsx` | form_submit + whatsapp_click → dataLayer.push() |
| `app/ppc-freelancer1/page.tsx` | form_submit + whatsapp_click → dataLayer.push() |
| `app/ppc-google-ads-agency/page.tsx` | form_submit + whatsapp_click → dataLayer.push() |
| `app/ppc-google-ads-agency-partner/page.tsx` | form_submit + whatsapp_click → dataLayer.push() |
| `app/ppc-google-ads-management-manager/page.tsx` | form_submit + whatsapp_click → dataLayer.push() |
| `app/ppc-google-adwords-consultant/page.tsx` | form_submit + whatsapp_click → dataLayer.push() |
| `app/ppc-specialist-expert/page.tsx` | form_submit + whatsapp_click → dataLayer.push() |
| `app/white-label-outsource-google-ads-ppc/page.tsx` | form_submit + whatsapp_click → dataLayer.push() |

---

## Follow-Up Actions

### Immediate (within 24 hours)
- [ ] Check Google Ads conversions — verify "Submit lead form" and "WhatsApp Click" show "Recording" or "Active" status
- [ ] Confirm at least 1 conversion registers from a real ad-clicking user

### Before 1 May 2026 (promo deadline)
- [ ] Ensure at least 1 Google Ads conversion is logged (from ad traffic, not direct)
- [ ] Campaigns must be active and serving for conversions to count

### Optional future improvements
- [ ] Move LinkedIn Insight Tag into GTM (currently still hardcoded)
- [ ] Add `phone_click` event tracking via GTM (exists in ppc-freelancer page but not GTM-managed)
- [ ] Consider adding enhanced conversions once conversion volume grows
- [ ] Set up Google Ads remarketing audiences via GTM
- [ ] Clean up unused "Lead form - Submit" (Google hosted) conversion action if not needed

---

**END OF SUMMARY**
