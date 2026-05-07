# DBD Session Summary — Wednesday 22 April 2026

**Client:** Dental by Design
**Duration:** Full day — AM search-terms session (~4hr) + PM tracking audit session (~4hr)
**Focus:** Made DBD's negatives module **trustworthy end-to-end**, then opened the DBD **tracking audit** end-to-end (Google Ads conversions, site code, GTM, GA4, webhook architecture, Zapier pipeline).

---

## The shift this session represents for DBD

Yesterday made the negatives system operational. Today made it **reliable** — and then exposed how much of DBD's Google Ads tracking is silently broken. Three structural problems in the negatives system were fixed before lunch. In the afternoon, six additional structural problems in DBD's conversion tracking were diagnosed, documented, and captured in a deck + email ready to go to Giulio.

Going into this session, DBD's account was running on a conversion-tracking stack that wasn't producing trustworthy revenue data — which is why Week 1's report used "All conv" instead of specific actions, and why we told the client we'd do a tracking audit. Going out of it, we know where every gap is, who owns each fix, and what's blocked on access.

**Projected ongoing time saving:** ~10 hours per week on DBD (negatives workflow) — unchanged from yesterday, because the AM work consolidated what was built rather than expanding it.

**Projected additional impact once tracking fixes ship:** unblocks ROAS bidding, unblocks Search campaign attribution, restores reportable revenue numbers. Can't be quantified until Dengro + Zapier access arrives.

---

## AM Session — Negatives system upgrades

### Engine trust repair — the hidden sync bug

The most important fix of the day. Not visible to DBD but would have cost them money every week if left in place.

**What was wrong:** The classification engine was reading every historic snapshot of Google Ads negative lists instead of just the latest one. Negatives removed from Google Ads continued to block search terms forever. Example: `over 60s` removed from DBD's 2-word phrase list, engine kept using it.

**What was fixed:**
- Engine now queries only the latest `snapshot_date` per client (critical SQL filter added in `pass1.py` + `pass3.py`)
- "Refresh Neg Lists from GAds" button on Search Terms page pulls current state on demand
- "Reclassify today's terms" button re-runs Pass 1 + Pass 2 instantly
- Negative Lists viewer inside ACT (Client Config → new tab)
- Last-synced pill on Search Terms page, colour-coded
- Regression test added

**Verified:** after fix, reclassify showed Block count drop 114 → 111 and Leak-phrase count drop by exactly 4, matching the 4 phrase negs removed that morning.

### Sticky Rejections — no more daily re-litigation

A full sticky-rejection system with 60-day expiry cycle:
- Reject a term → hidden from Pending queue for 60 days
- After 60 days, auto-reappears for review
- Cycle counter increments on each re-rejection
- Permanent history — every event kept forever
- New **Rejected Terms** page with stat cards, live countdown timer, cycle-history drill-down, Unreject button

### Mixed Intent engine fix

Engine had rule-ordering bug: when search term contained BOTH an advertised service ("dental implant") AND a not-advertised service ("crown"), not-advertised rule fired first → auto-blocked. 5 documented false-positives in 3 days.

New Rule 5 precedence: if not-advertised match found AND query contains advertised token, downgrade Block → Review with reason `Mixed intent`.

### Daily triage UX improvements

- Native browser `confirm()` replaced with custom ACT-styled modal
- In-place table refresh after reclassify (toast visible, no full reload)
- Row number column on all 3 tables
- Button labels standardised
- Reclassify progress feedback in toast

### Negatives pushed today

**168 live exact-match negatives + 1 phrase-match consolidation pushed.** Running 2-day total: **388 negatives applied** to DBD's account.

Plus 1 sticky rejection recorded (will reappear 21 Jun 2026 unless re-rejected).

---

## PM Session — DBD Tracking Audit (end-to-end)

### What we audited

| Phase | Scope | Status |
|---|---|---|
| 1. Google Ads conversion actions | 23 actions inventoried, categorised, statuses logged | ✓ Done |
| 2. Site code — GitHub repo | track-conversion.ts, utm-tracker.ts, both layouts | ✓ Done |
| 3. GTM container | GTM-KBPKCLKB — 3 tags, 2 triggers, 1 variable, templates | ✓ Done |
| 4. Webhook architecture | API endpoints, Dengro schema, 3 Zapier hooks | ✓ Done |
| 5. GA4 property | Settings, streams, events, key events, linking | ✓ Done |
| 6. Dengro CRM | Gclid coverage, pipeline stages, booking break | Awaiting login |
| 7. Zapier account 23529592 | 3 zap run histories, Booking fix | Awaiting access |
| 8. CallTrackingMetrics | Discovered via CTM_Activity event in GA4 | Awaiting login |
| 9. Live page testing | GTM Preview + GA4 DebugView tests | Awaiting access |

### Headline findings

**Good news — foundations are sound:**
- `utm-tracker.ts` captures `gclid, gbraid, wbraid, fbclid, msclkid` + all UTMs into 30-day cookie. Robust.
- Enhanced Conversions (hashed email, phone, address) implemented in `track-conversion.ts`
- Server-side webhook architecture: API receives Dengro webhooks, sends Meta Conversions API directly + Google Ads via Zapier
- GTM (GTM-KBPKCLKB) correctly loads Google Tag + GA4 + Microsoft UET
- Call tracking via CallTrackingMetrics (confirmed by `CTM_Activity` event in GA4)

**Bad news — six structural breaks:**

1. **First-touch attribution is stealing credit from new Search campaigns.** `utm-tracker.ts` only stores the FIRST gclid per 30-day window. If user visits DBD via PMax first, then clicks a Search ad later, lead is attributed to PMax. Explains why 22 of 25 new Search ad groups show 0 conversions.

2. **Dengro Offline Booking broken since 5 Jan 2026.** Lead and Purchase pipelines still firing, but the Booking-stage webhook/Zap is dead. Specific Zapier webhook suspected: `hooks.zapier.com/hooks/catch/23529592/u9v9qg1/`

3. **Purchase value defaulting to £300.** Real DBD implants are £3k-15k. Average conversion value £342 proves no real revenue data is flowing through. Either Dengro isn't sending values or Zapier isn't mapping them.

4. **Purchase excluded from account-level goals.** Even if we fix values, Google's bidder can't see them until this flag flips.

5. **GA4 has zero conversion events.** Only 8 events registered — all GA4 Enhanced Measurement defaults. No custom events for form_submit, phone_click, booking_click. GA4 is blind to the funnel.

6. **InvisalignLayout has no GTM.** 4 Invisalign pages are untracked (no PPC impact today, but organic invisible).

### Deliverables produced this session

1. **Tracking Audit deck v2** — `potential_clients/Inserta Dental/Tracking Audit/DBD - Tracking Audit v2.pptx` — 16 slides (9 main + 7 appendix). **Needs visual polish** (see Handoff section below).

2. **Giulio email draft** — `potential_clients/Inserta Dental/Tracking Audit/email_to_giulio_DRAFT.md` — 8 questions covering attribution model, Booking break, Purchase values, GTM container, server-side tracking, Bing, call tracking, access requests.

3. **DBD repo cloned locally** — `C:/Users/User/Desktop/dentalbydesign-repo/` — full monorepo for read-only code inspection during ongoing audit. **Do NOT push any changes** — Giulio owns deployment.

4. **Image resize utility** — `potential_clients/Inserta Dental/Tracking Audit/_resize.py` — downsizes screenshots to max 1500px, run after each batch of screenshots.

5. **Audit folder populated** — `potential_clients/Inserta Dental/Tracking Audit/` contains all supporting screenshots from GAds, GTM, plus the deck + email.

### Proposed fixes (prioritised in deck)

**P0 (blocking):**
- Switch paid click IDs to last-touch in `utm-tracker.ts`
- Fix Dengro Booking Zap (account 23529592, webhook u9v9qg1)

**P1 (high impact):**
- Clean up GAds conversions (1 primary lead + 1 primary purchase, demote rest)
- Pass real sale values to GAds (map Dengro `confirmed_amount` → Zapier → GAds)
- Add GA4 conversion events (form_submit, phone_click, booking_click, quiz_complete)

**P2 (polish):**
- Add GTM to InvisalignLayout
- Resolve "Google Tag Gateway: Incomplete" flag
- Link BigQuery for advanced analysis

### Blockers for next session

- **Dengro login** — critical for gclid coverage audit (the first-touch theory needs validation)
- **Zapier access (account 23529592)** — critical for Booking break diagnosis
- **CallTrackingMetrics login** — call attribution audit
- **Cloudflare logs** (optional) — webhook delivery error rates

---

## Session carryovers

### For tomorrow's session (PM 3 or user)

1. **Deck visual polish** — v2 built with structure + content, but needs design clean-up per user feedback:
   - Match v8 footer exactly (ACT logo + Chris + christopherhoole.com + Confidential + slide number)
   - Match v8 colours exactly: navy `#1A237E`, red `#EA4335`, pure black `#000000`, pure white, no greys, light border `#E2E8F0`, blue pill bg `#E8F0FE`
   - Add blue "context pill" box in top-right corner (matching v8 style)
   - Subtitle beneath title should be **pure black, not red, not bold**
   - No small text (min 11pt)
   - Use bullet points properly (not text blocks)
   - Fix table styling (proper borders, header row, alternating rows — not a coloured rectangle overlay)
   - Fonts: Arial for body, Calibri for headings

2. **Send Giulio email** — question list in `email_to_giulio_DRAFT.md`. User reviewing before send.

3. **Audit remaining phases** (when access arrives):
   - Dengro: query leads by gclid population — what % have attribution?
   - Zapier: inspect 3 zaps' run histories, find Booking failure point
   - CTM: audit DNI config and GAds-conversion flow

4. **Decision needed** on a few attribution questions before touching `utm-tracker.ts`:
   - First-touch or last-touch for UTMs?
   - How to handle user who clicks GAds then Bing — who gets credit?
   - 30-day window — is this right for DBD's sales cycle?

### Bugs / issues to watch for

- Accumulated image reads in this Claude Code session hit an image-token limit mid-afternoon. Session continued working for text/CSV but image uploads failed. Fresh session required for image-heavy audit work.
- Opera screenshots save at retina resolution (2x DPI); `_resize.py` downscales them before upload.
- User found deck v2 visually unpolished — structure + content correct, but colour/font/table/footer choices didn't match DBD v8 standard. Handoff includes full v8 specs.

---

## Next morning

User resuming with fresh session + MC - Project Manager 3. Focus:
1. Polish tracking audit deck to match v8 standard
2. Send Giulio email once polished deck is ready
3. Start answering Giulio's likely replies while awaiting Dengro/Zapier logins
4. Continue negatives triage for 23/4 daily search terms as normal morning review
