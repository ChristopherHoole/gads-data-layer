# Dental by Design — AG21-25 Build + Ad Strength Audit
**Session date:** Friday 17 April 2026 (afternoon, ~5 hours)
**Scope:** Finish Dental Implants Intent campaign build (AG21-25), then audit Ad Strength across all 25 DII ad groups

---

## Headline
Completed the Dental Implants Intent campaign rebuild — all 25 ad groups now live with 75 RSAs. Then ran an Ad Strength audit across AG1-AG21 (63 RSAs), pushing most from Good/Poor toward Excellent via keyword-density swaps. AG22-25 are pending Google approval so audit resumes Tuesday.

---

## By the numbers

| Metric | Count |
|---|---|
| New ad groups built | 5 (AG21-25) |
| New keywords added | ~105 phrase + 25 exact |
| New RSAs created | 15 (3 per ad group × 5 groups) |
| New headlines written | 225 (15 per RSA) |
| New descriptions written | 60 (4 per RSA) |
| Ad groups audited | 21 of 25 (AG1-AG21) |
| Ads audited | 63 of 75 |
| Pending Google approval | 12 ads (AG22-25) |

---

## Work delivered

### 1. AG21-25 build
Five ad groups built sequentially to complete the 25-group Dental Implants Intent campaign:

- **AG21** Missing Teeth Solutions — 21 phrase + 5 exact keywords, LP `/promo/google/teeth-implants`
- **AG22** Replace All Teeth — 22 phrase + 5 exact, LP `/dental-implants/vivo-bridge-full-mouth`
- **AG23** Teeth Reconstruction — 21 phrase + 5 exact, LP `/dental-implants/vivo-bridge-full-mouth`
- **AG24** Implants vs Dentures — 21 phrase + 5 exact, LP `/promo/google/teeth-implants`
- **AG25** Implants vs Bridges — 19 phrase + 5 exact, LP `/promo/google/teeth-implants`

Each ad group: 3 RSAs × 15 headlines + 4 descriptions, H1 pinned, display paths varied per RSA (category anchor `Dental-Implants` + unique Path 2 per ad).

### 2. Ad Strength audit — AG1 through AG21
Audited 63 RSAs across 21 ad groups against the two CSV exports in `data/Dental Implants Intent/`. Per ad group:

- Read current headlines, descriptions, Ad Strength score, Google improvement suggestions, Quality Score per keyword
- Identified issues (non-ad-group keywords, duplicate description start words, weak USPs)
- Produced swap tables: Current | Replace with | Chars | Reason

### 3. Audit methodology refined mid-session
Multiple rounds of learning:
- Initial approach swapped in broader dental implant keywords (e.g. "Dental Implants London") to a "Best Dental Implants" ad group — wrong. Google wants THIS ad group's literal keywords, not cross-campaign ones.
- Rebuilt approach: pack 10-11 literal AG keyword headlines + 4-5 USPs per RSA. Each description must contain 2+ literal keywords from the ad group's own keyword list. Descriptions should cover keywords NOT in headlines.
- Description character limit confirmed as 90 (not 86 as originally assumed from Day 3 notes). Don't force swap on 87-89 chars.

### 4. Ad strength results from audit
Of the 63 audited ads:
- **Already Excellent** before audit: ~8 ads (untouched)
- **Pushed toward Excellent** via swaps: ~55 ads (user applies swaps one at a time until live score flips, then saves)
- **Specific problem ads needed full rewrites:** ~4 ads where description keyword packing alone wasn't enough

### 5. Display path clashes flagged
Three ad groups had two ads sharing identical display paths (making them indistinguishable in the UI):
- AG3 Full Mouth Implants: AD A + AD C both `full-mouth / implants`
- AG17 Dental Implants Hammersmith: AD A + AD C both `hammersmith / implants`
- AG18 Dental Implants Near Me: AD B + AD C both `implants / near-me`

Suggested Path 2 changes in each audit to differentiate.

---

## Outstanding

### Tuesday (22 April) — audit resume
Once AG22-25 ads clear Google's "Pending" review, audit those 12 RSAs using same keyword-packing approach.

### Monday (21 April) — tracking audit (priority)
User has flagged a full end-to-end tracking audit on all Search campaign landing pages. Goal: confirm conversions actually fire reliably before we draw any conclusions from CPA data. Planning this tomorrow morning.

### PMax vs Search CPA investigation — blocked
User pushed back on speculative answers. Before resuming this, need to learn DBD's actual tracking setup from scratch — conversion actions, GTM config, offline import, real CPA numbers. User to brief me before I suggest anything.

---

## Key learnings (carry forward)

### Ad Strength packing rules (refined)
1. Every headline not a USP should contain a LITERAL keyword from THIS ad group's keyword list (not broader dental implant terms from other ad groups)
2. Target: 10-11 keyword headlines + 4-5 USPs per RSA
3. Each of the 4 descriptions must contain 2+ literal ad-group keywords
4. Descriptions should cover keywords NOT in headlines (net-new coverage = Google sees more of the ad group's pool)
5. Description start words must be unique across all 4 descriptions in an RSA
6. Headline start words: max 4-5 sharing same opener is workable (6+ triggers "not unique" flag)

### Workflow rules established this session
- User applies swap suggestions one at a time, stops when live Ad Strength indicator flips to Excellent, saves. Over-supply swaps, don't minimise.
- Descriptions up to 90 chars are legal (90 hard limit, not 86). Don't force swap on 87-89 chars.
- Always show swap tables as: `H#/D# | Current | Replace with | Chars | Reason`
- Identify ads by display path (`Path1 / Path2`), never "Ad 1/2/3"
- Always use full absolute URLs for landing pages (https://dentalbydesign.co.uk/path)
- Every RSA needs Path 1 + Path 2 (≤15 chars each)
- User doesn't read long responses — keep strategic/planning replies tight

### DBD tracking — NEEDS LEARNING
I (Claude) made multiple wrong assumptions about DBD's tracking setup (incorrectly applied ChristopherHoole.com's form_submit £40 / whatsapp_click £10 conversion config to DBD, which is not the same). User to brief me from scratch on Monday before any conversion analysis.

---

## Files modified / created this session

### Built in Google Ads
- AG21 Missing Teeth Solutions (+ 3 RSAs, keywords, display paths, LP)
- AG22 Replace All Teeth (+ 3 RSAs)
- AG23 Teeth Reconstruction (+ 3 RSAs)
- AG24 Implants vs Dentures (+ 3 RSAs)
- AG25 Implants vs Bridges (+ 3 RSAs)
- Ad Strength swaps applied to ~55 RSAs across AG1-AG21

### Data reviewed
- `data/Dental Implants Intent/Dental Implants Intent - All Ads.csv` (81 rows)
- `data/Dental Implants Intent/Dental Implants Intent - All Keywords.csv` (617 rows)

### Reference docs used (not modified)
- `CAMPAIGN_REBUILD_PLAN.md` — landing page mapping for AG21-25
- `DENTAL_IMPLANTS_KEYWORDS.md` — full keyword lists
- `Session Summary/HANDOFF_17-4-26.md` — context for this session

---

## Saturday 18 April — Week 1 client report
User decided to defer the end-of-week report to Saturday morning so full Friday (17 April) performance data has landed. Report covers **Mon 14 → Fri 17 April**. Campaign data to be exported by user into `data/All Campaigns/` for drafting.

**Report structure agreed:**
1. Cover — Week 1 Report, 14-17 April
2. Executive summary — what was done, early signal, what's next
3. Work delivered (by day)
4. Cumulative numbers — 546 positive keywords, 75 RSAs, ~5,000 negatives, 810 geo targets
5. Early results with caveats (4 days of data only, full signal needs 14-21 days)
6. 2 items needing Giulio/Tommaso's decision (consultation pricing, 25+ years claim)
7. Next week plan
8. Outstanding client questions

Templates in `reports/` are pitch decks not weekly reports — reuse branding, new structure.

---

## Monday 20 April — tracking audit (priority)
Full end-to-end verification of conversion tracking on every Search campaign landing page. Must be done before any CPA analysis — prior assumptions about DBD's tracking setup (form_submit £40, whatsapp_click £10) were wrong and came from memory pollution between clients. User to brief Claude from scratch on DBD's actual conversion actions, GTM setup, CRM integration before Claude suggests anything.

---

## Tuesday 21 April — resume audit
Resume Ad Strength audit on AG22-25 once Google clears Pending status. Second pass on any AG1-AG21 ads that didn't flip to Excellent.

---

## Blocked / deferred
- **PMax vs Search CPA investigation** — deferred until tracking audit is complete and Claude is briefed on DBD's actual tracking setup
- **Friday report (Week 1)** — deferred to Saturday 18 April so Friday performance data is included
- **Giulio + Tommaso reply** — 18 questions still outstanding from Wed 15 April
