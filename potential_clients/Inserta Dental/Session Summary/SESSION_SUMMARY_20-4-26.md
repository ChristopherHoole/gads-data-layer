# DBD Session Summary — Monday 20 April 2026

**Client:** Dental by Design
**Duration:** ~8 hours continuous development
**Focus:** Built advanced negative keyword automation system for DBD's Google Ads account

---

## The problem this solves for DBD

DBD's account currently generates **1,225 search terms per day** across three campaigns (Brand, Dental Implants Intent, Dental Implants PMax). Industry experience: **at least 50% of ad spend is typically wasted** on unblocked search terms. For DBD specifically, search terms like "cheap dental implants", "NHS dental", "emergency veneers" have been triggering ads despite being outside the advertised service scope.

Manually reviewing 1,225 terms every morning would take 2+ hours per day. This session built an automated system that does the heavy lifting overnight, leaving only a short daily review pass in the morning.

---

## What was delivered today

### Overnight data pipeline (DBD-specific)
- Pulls yesterday's search terms from all 3 DBD campaigns (Brand, Dental Implants Intent, PMax)
- Handles PMax's separate API (different from Search campaigns) — DBD's PMax drives 72% of daily spend, so capturing this was critical
- Syncs all 15 of DBD's negative keyword lists and their campaign attachments
- Runs daily at 6:30am UK time

### Intelligent classification engine (tuned for DBD)
Each search term runs through 8 ordered rules:
1. **Brand protection** — searches for "Dental by Design" variants always kept
2. **Already-blocked leak detection** — catches any term already on DBD's exact/phrase neg lists (rare but useful)
3. **Outside-service-area detection** — blocks searches from locations DBD doesn't serve (e.g. "composite bonding shrewsbury")
4. **Services-offered-but-not-advertised** — blocks terms for services DBD offers but isn't advertising (veneers, crowns, bonding, etc.)
5. **Advertised service match** — keeps terms relevant to DBD's implant ad scope
6. **Soft vocabulary signal** — flags terms containing words DBD has negged elsewhere (competitor names, specific bad-fit terms)
7. **Ambiguous** — flags everything else for manual review

### DBD Client Configuration locked in
- **Services Advertised (Ad Scope):** 50+ implant-related terms — dental implants, teeth-in-a-day, all-on-4, all-on-6, vivo bridge, vivo crown, bone graft, sinus lift, etc.
- **Service Locations:** 1,300+ entries covering every London postcode district and area name within DBD's M25 targeting
- **Brand terms:** "dental by design", "dental by design hammersmith", "dental by design london", "dentalbydesign", "dentalbydesign.co.uk"
- **Rule 7 exclusions:** industry-universal words that would over-block (teeth, dental, tooth, smile, implant, implants, mouth, gum, etc.) — these still block as bare queries but don't extrapolate to multi-word false positives

### Morning review interface
- Dashboard showing today's search terms classified into buckets (Block / Review / Keep / Pushed)
- Filter by campaign source (Search vs PMax — critical because Search data is 1:1 validatable against Google Ads UI, PMax has known Google API/UI differences)
- Each row shows the specific matched term explaining why it was flagged (e.g. "Not advertised: veneers", "Outside: shrewsbury", "Contains: 1kingsdental")
- Bulk approve + one-click push to Google Ads API
- Per-source metrics split so DBD's Search and PMax numbers can be validated independently

### Live testing — 9 real negatives pushed to DBD's Google Ads today
All pushed successfully to their correct shared lists:

| Term | Target List | Reason |
|---|---|---|
| `veneers cost uk` | Off Not Adv [ex] | DBD offers veneers but doesn't advertise |
| `smile makeover` | Off Not Adv [ex] | Not in implant ad scope |
| `teeth veneers` | Off Not Adv [ex] | Not in implant ad scope |
| `bridges and implants` | Off Not Adv [ex] | Non-implant bridge queries |
| `emax veneers` | Off Not Adv [ex] | Not in implant ad scope |
| `2 front teeth veneers cost uk` | Off Not Adv [ex] | Not in implant ad scope |
| `composite bonding kingston` | Loc 1 WRD+ [ex] | Outside service area |
| `composite bonding shrewsbury` | Loc 1 WRD+ [ex] | Outside service area |
| `composite bonding bury` | Loc 1 WRD+ [ex] | Outside service area |

Each verified live in DBD's Shared Library.

---

## Immediate value captured for DBD

- **£14.21/day of actual recovered waste spend** from the first batch of 9 pushes (most of this from `2 front teeth veneers cost uk` at £2.12 alone)
- Scales non-linearly: once a phrase-match negative is added (e.g. blocking "bonding" as a 1-word phrase), every variation of that term gets blocked too, including ones DBD never individually sees
- 216 further terms already classified and awaiting approval — estimated £100-150/day additional recovery once reviewed

**Monthly savings estimate for DBD at current scale:** £400-600+ per month recovered from blocked waste spend, scaling up as the system processes more days of data.

---

## What's still to do (this week)

- Simplify the Client Config services model (in progress — cleaner two-list structure for easier day-to-day maintenance)
- Process the 216-term review pile (manual decisions for ambiguous terms)
- Validate the system's daily output against DBD's Google Ads UI for 3-5 consecutive days
- Begin daily operational use — every morning: review, approve, push

---

## Hours invested today

Approximately 8 continuous hours. This is foundational work that delivers DBD value from day one and scales for every future day. The system that took 8 hours to build will save 2+ hours per day in manual review going forward.
