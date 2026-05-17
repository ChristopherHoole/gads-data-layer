# Tier 2.1 Stage 12 - end-to-end QA report (17 May 2026)

## Scope

Stage 11 (Pass 3 AI routing UI) shipped this session as commit
`11b38f8`. Stage 12 is the QA pass against today's DBD Pass 3 backlog
plus a routing spot-check + a UX papercut list for Tier 2.2.

## Data snapshot at QA time

| Metric | Value |
|---|---|
| Latest `analysis_date` with phrase suggestions for DBD | `2026-05-12` (5 days ago) |
| Phrase suggestions on that date | 5 |
| All `review_status` | `pending` |
| Confidence breakdown | 3 high, 2 medium, 0 low |
| `manual_override = TRUE` | 0 |
| Pass 3 scheduler_runs rows since 12 May | 0 (no fresh PMax CSV ingest since then) |

No fresh DBD PMax CSV has landed since 2026-05-12, so there is no
"today's backlog" to triage in the literal sense. The brief was written
assuming today = a CSV-drop day. QA is therefore against the existing
5-row snapshot.

Decision (not in brief): do NOT re-run Pass 3 against 2026-05-12 with
`--force`. The cached results are already high quality (see spot-check
below); re-running would cost real Sonnet/Haiku tokens for no gain.

## Spot-check: all 5 phrase suggestions (the full corpus)

The brief asks for "20 random AI routings" - the corpus contains only 5
phrase suggestions, so this section is the full set rather than a
random sample.

| # | Fragment | Suggested role | Conf | Occ | Risk | Rationale |
|---|---|---|---|---|---|---|
| 1 | dentures | offered_not_advertised_phrase | high | 5 | high | Rule 3 - dentures explicitly in services_not_advertised; high-intent non-implant traffic. |
| 2 | dental bridge | offered_not_advertised_phrase | high | 3 | low | Rule 3 - dental bridge (non-implant) in services_not_advertised; implant bridges advertised instead. |
| 3 | smile makeover | offered_not_advertised_phrase | high | 1 | low | Rule 3 - smile makeover explicitly in services_not_advertised; cosmetic service not offered. |
| 4 | straight teeth | offered_not_advertised_phrase | medium | 1 | medium | Rule 3a - teeth straightening in services_not_advertised; signals orthodontic/cosmetic intent. |
| 5 | align teeth | offered_not_advertised_phrase | medium | 1 | medium | Rule 3a - teeth alignment (orthodontics) in services_not_advertised; non-implant intent signal. |

Verdict: every row references a real prompt rule (Rule 3 / 3a) and a
real services_not_advertised entry from the DBD client config. No
fabricated rules. No invented ad-group names. Routing is correct in
all 5 cases (`offered_not_advertised_phrase` is the canonical target
list for service-mismatch fragments).

## Historical routing spot-check - gloucester / k2

The brief mentions a historical bug: `gloucester` routed to
`1_word_phrase` (generic) instead of `location_phrase`; `k2` routed to
`1_word_phrase` instead of a review-hold state. Searched the
phrase_suggestions history across all dates:

| Date | Fragment | Routed to | Confidence |
|---|---|---|---|
| 2026-04-24 | gloucester | 1_word_phrase | (null) |
| 2026-04-24 | k2 | 1_word_phrase | (null) |
| 2026-04-24 | stafford | 1_word_phrase | (null) |

Confidence is NULL on all three because they were emitted by the OLD
rule-based engine that predates 2.1e (pass3_phrase.py). No AI engine
ever processed them.

The current pass3_ai.py engine + `search_terms_pass3_v2.txt` prompt has
explicit rules that fix this:

- Rule 4a (UK locations): "always-surface, exempt from cap" - keeps
  gloucester / stafford / etc. on the list with confident routing.
- Rule 4b (international locations): mirrored for non-UK city tokens.
- Rule 4c CRITICAL OVERRIDE for brands in services_advertised: ensures
  Nobel / Straumann / etc. are NOT blocked.

When gloucester / stafford appear again in a future PMax CSV they will
be re-processed by pass3_ai.py against the v4 prompt and should route
to `location_phrase` with high confidence. The k2 case (ambiguous
single token) routes to a review-hold path - the prompt downweights
2-character tokens explicitly.

Acceptance: cannot fully verify the gloucester / k2 fix without fresh
data hitting the v4 prompt. Banked for the next PMax CSV drop -
auto-trigger (Part C of this same brief) will fire Pass 3 within 2
minutes and the cost banner will show the run details.

## AI cost across the QA pass

No fresh AI calls were made for QA - the 5-row corpus was read from
cache. Cost = £0.00 / $0.00.

Last successful Pass 3 run on this client predates the
`details_json` cost-logging that landed during the kw_history work, so
no historical cost figure is available for the 2026-05-12 run.

## Stage 11 UI smoke (template render only - cannot drive browser from this shell)

Template renders cleanly with:
- `#stP3CostBanner` markup in place (hidden until first successful run).
- `#stP3CostText` populated by `hydrateP3CostBanner()` on Pass 3 tab
  activation.
- `btnAIRouteP3` label reads `Route phrases by intent` with the
  Material `route` icon.
- `manual_override` flag returns in the `/phrase-suggestions/<client>`
  payload; pencil icon renders muted on every row (none currently
  manually edited).
- Em-dash count module-wide: 0.

A live browser screenshot of the cost banner + manual-flag pencil is
banked for Chris's next session - the harness can't drive the browser
from a cold Flask boot without grabbing the DB lock.

## UX papercuts surfaced for Tier 2.2

The list below is appended to `docs/TIER_2.1_BUILD_PLAN.md` as the
Tier 2.2 polish backlog.

1. **Cost banner is reference-only** - it shows the LAST run but
   there's no way to drill in. Click-to-expand would surface
   per-batch cost / failed-batch detail / model version. Low priority.

2. **Manual override is read-only-ish** - the pencil indicator turns
   on when Chris swaps the dropdown, but there's no "revert to AI
   suggestion" button. Cheap add: extra link "[revert]" next to the
   manual flag that POSTs target_list_role_override = ai_target_list_role
   and resets manual_override to FALSE. Medium priority.

3. **No bulk "approve AI high-confidence" action** scoped to Pass 3.
   Term Review has `Apply high-conf` (removed in Section 8a anyway);
   Pass 3 doesn't. Low priority - 5-row days don't need bulk.

4. **Pass 3 row count doesn't surface anywhere obvious** - tab badge
   shows `phrase_suggestions_count` (correct) but no per-status
   breakdown like the Term Review Status pills. If volume grows
   (post-auto-trigger world), pill counts would help. Medium.

5. **Cost banner format is single-line** - on narrow viewports it
   either wraps awkwardly or scrolls horizontally. Could move to a
   grid layout with labels above each number. Low.

6. **`hydrateP3CostBanner` always re-fetches on tab switch** - cheap
   call but redundant if already loaded. Cache the result for the
   page session. Low.

7. **Gloucester / k2 cannot be verified without fresh data** - need
   a synthetic test fixture or a "run prompt on these 3 terms"
   sandbox endpoint. Medium-high priority for confident regression
   testing of prompt revisions.

8. **`ai_target_list_role` column shows the SAME data as the live
   `target_list_role` dropdown** in the API response. Whenever the
   AI is the source of truth, the two columns are duplicates. The
   "Apply AI routing" button is a no-op against this shape. Either
   (a) split the columns so AI suggestion is read-only and the
   dropdown represents the live state, or (b) drop the AI Role
   column entirely. Decision needed - flag for Chris. High priority
   because it confuses the UI semantics.

9. **No surface for "show only manually-overridden rows"** - useful
   for end-of-day review of where Chris diverged from the AI. Low.

10. **Pass 3 cost banner sits BELOW the theme banner** - might read
    better at the top as the first thing the eye lands on. Visual
    micro-decision; defer to Chris's preference.

Suggested fix order for Tier 2.2:

| Bucket | Items |
|---|---|
| Must-fix | (none - Stage 11 is functionally complete) |
| Should-fix | #2 (revert button), #4 (Pass 3 status pills), #7 (prompt regression sandbox), #8 (AI-Role vs live-Role semantics decision) |
| Nice-to-have | #1, #3, #5, #6, #9, #10 |
