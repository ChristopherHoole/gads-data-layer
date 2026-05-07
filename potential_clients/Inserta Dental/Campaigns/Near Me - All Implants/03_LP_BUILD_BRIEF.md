# LP Build Brief — Near Me Campaign (7 LPs)

**For:** LP build session
**Client:** DBD
**Repo:** dentalbydesign.co.uk Astro (same one used for LP #1-#25 Mon 27 Apr)
**Pipeline:** identical to Monday's protocol (parse keywords → cluster FAQs → write Astro from LP #1 template → ngrok pre-review with keyword coverage table + both URLs → wait for "ngrok looks good" → bun build → commit/push → Cloudflare deploy → live HTML keyword check → confirm 100% coverage)

**Total to build today:** 7 LPs — 3 net-new + 4 clone-and-respin from existing.

---

## Universal "Near Me" treatment (applies to all 7)

Every LP in this batch reinforces **location** alongside service intent. Differences from Mon's 25 LPs:

1. **Hero block adds explicit location signal.** Always reference West London / Hammersmith. Hero title two-line pattern stays (per Mon convention).
2. **Map block above the fold** — Google Maps embed showing practice location. Place between hero and first content section.
3. **Address + opening hours visible without scrolling** — small strip beneath hero ("Hammersmith · 5 mins from Hammersmith tube · Mon-Fri 09:00-18:00, Sat 09:00-13:00")
4. **Trust block emphasising local** — "Serving West London since [year confirmed by Giulio]" / "Patients from across [postcodes]"
5. **FAQ block adds at least one location-specific Q** — e.g. "Where are you based?" / "Do you treat patients from [common postcodes]?" / "How do I get to the clinic?"
6. **No specific prices in hero** (per Mon convention)

---

## LP 1 — Dental Implant Clinic Near Me (NEW) ⭐ PRIORITY

**Slug:** `/google/dental-implant-clinic-near-me`
**Why priority:** highest-converter ad group (£980 spend / 22 conv last month). Build this one first.

**Hero direction:** "West London's Dental Implant Clinic" / "Trusted by patients from across [postcodes]". Lead with credentials + locality, not pricing.

**Keyword set to cover (count exact occurrences in live HTML):**
```
dental implant clinic near me
dental implants clinic near me
dental implant centre near me
dental implant center near me
dental implant practice near me
implant clinic near me
implant centre near me
implant dentist near me
best dental implant clinic near me
dental implant specialists near me
dental implant surgeon near me
top rated implant dentist near me
```

**Topic angle:** clinic credentials, surgeon expertise, technology stack, sterilisation/safety standards, patient testimonials, location convenience. Position as the local destination clinic for implant work, not a generic dentist.

---

## LP 2 — Full Mouth Implants Near Me (CLONE LP #13)

**Slug:** `/google/full-mouth-implants-near-me`
**Source:** clone LP #13 Full Mouth Implants → apply Universal Near Me treatment + slug change.

**Keyword set to cover:**
```
full mouth dental implants near me
full mouth implants near me
full dental implants near me
full arch dental implants near me
full mouth reconstruction near me
all on 4 dental implants near me
all on 4 implants near me
all on four dental implants near me
all on 4 near me
full set of teeth near me
replace all teeth near me
whole mouth implants near me
```

**Adjustments to existing #13:** add "near me" / "in West London" to H1 + intro paragraph; reinforce All-on-4 terminology in FAQ; keep £6,995 single-arch / £10,995 double-arch pricing anchors (in PriceChart, not hero).

---

## LP 3 — Same Day Implants Near Me (CLONE LP #22)

**Slug:** `/google/same-day-implants-near-me`
**Source:** clone LP #22 Same Day Teeth → apply Universal Near Me treatment.

**Keyword set:**
```
same day dental implants near me
same day implants near me
same day implant near me
one day dental implants near me
immediate dental implants near me
24 hour dental implants near me
teeth in a day near me
same day tooth replacement near me
```

**Adjustments:** speed-of-treatment + locality combined. "From consultation to teeth in one visit — at our West London clinic." Reinforce Same Day = literal same-day capability, not 24/7 emergency.

---

## LP 4 — Single Tooth / Tooth Replacement Near Me (CLONE LP #23)

**Slug:** `/google/single-tooth-implant-near-me`
**Source:** clone LP #23 Single Tooth Implant → apply Universal Near Me treatment.

**Keyword set:**
```
tooth replacement near me
single tooth implant near me
single tooth replacement near me
tooth implant near me
tooth implants near me
tooth implant dentist near me
missing tooth replacement near me
front tooth implant near me
molar implant near me
one tooth implant near me
replace one tooth near me
single dental implant near me
```

**Adjustments:** broaden from "single tooth implant" framing to "single tooth replacement" so the page also captures `tooth replacement near me` (£68, 24 clicks last month). Cover anterior + molar variants in FAQ.

---

## LP 5 — Pay Monthly / Finance Implants Near Me (CLONE LP #20)

**Slug:** `/google/pay-monthly-implants-near-me`
**Source:** clone LP #20 Pay Monthly Dental Implants → apply Universal Near Me treatment.

**Keyword set:**
```
pay monthly dental implants near me
dental implants on finance near me
dental implants payment plan near me
dental implants 0 finance near me
finance dental implants near me
payment plans for dental implants near me
dental implants monthly payments near me
spread the cost dental implants near me
dentist with payment plans near me
```

**Adjustments:** lead with finance + locality combined. "0% finance dental implants in West London — spread the cost." Reinforce that finance is offered at the local clinic (not a finance company elsewhere).

---

## LP 6 — Teeth Fixing Near Me (NEW)

**Slug:** `/google/teeth-fixing-near-me`
**Why new:** no existing LP matches the "fix my teeth" emotional intent — closest is #21 Replace All Teeth which is too final. This needs softer "we'll fix what you've got" framing.

**Keyword set:**
```
teeth fixing near me
fix my teeth near me
fix teeth near me
fixed teeth near me
get my teeth fixed near me
fix my smile near me
```

**Hero direction:** emotional opener — "Fix your teeth without hiding your smile." Lead with the problem (broken / damaged / loose / chipped) → solution menu (implants, bridges, crowns, all-on-4 depending on case) → free consultation CTA. NOT a single-procedure page — this is a "we'll figure out what you need" page.

**Topic angle:** consultation-led. Less procedure-specific, more reassurance-led. Position the clinic as the place you go when you don't know exactly what you need yet.

---

## LP 7 — Catchall — Dental Implants Near Me (NEW)

**Slug:** `/google/dental-implants-near-me`
**Why new:** no existing LP is a generic "dental implants near me" — Mon's 25 LPs are all sub-segments. This is the broad-intent capture page for the catchall ad group.

**Keyword set:**
```
dental implants near me
dental implant near me
implants near me
teeth implants near me
tooth implants near me
dental implants in my area
dental implants nearby
dental implants close to me
local dental implants
affordable dental implants near me
best dental implants near me
cheap dental implants near me
dental implants cost near me
dental implant prices near me
dental implants UK near me
```

**Hero direction:** "Dental Implants in West London" / "Trusted local clinic, transparent pricing." This is a broad-intent landing — the visitor doesn't know exactly which procedure they want yet.

**Topic angle:** broad implants overview. Show the full procedure menu (single tooth → full mouth → all-on-4 → same day) with internal links to the more specific LPs (#23 single tooth, #13 full mouth, etc.) as natural deep-links. Trust signals + locality. Free consultation CTA.

---

## Build order

1. **LP 1 first** (highest-converter, NEW, deserves most care)
2. **LP 7 second** (NEW catchall — needs to internal-link to other LPs once they're up)
3. **LP 6 third** (NEW Teeth Fixing — different framing from any existing LP)
4. **LP 2-5 in parallel** (clones — fastest because base structure exists)

## Process protocol (locked from Mon 27)

- Pre-review must include keyword coverage table + ngrok URL + live URL
- Do NOT auto-fix-then-push — fix, present updated table, wait for "ngrok looks good"
- UK spelling sweep (`aging` → `ageing`, etc.)
- Build locally with `bun run build` before commit
- Commit message: `Add LP: <ad-group-name> → <slug>` for new builds, `Clone+respin LP #N → <slug> (near-me variant)` for clones
- Confirm 100% live keyword coverage post-deploy

## Time budget

7 LPs × 30min average = 3.5h. Push for 4h total wall time including review iterations.

## Final URLs to feed back to PM

Once each LP is live, paste back:
- Slug
- Live URL
- Cloudflare commit
- Live keyword coverage % (must be 100)

I'll plug these into the campaign config.

---

**Pause-gate check before starting:** confirm understanding of the Universal Near Me treatment + the build order + the 4-clone vs 3-new split.
