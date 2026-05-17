# Section 8 - Search Terms Polish Audit (17 May 2026)

## Summary
- Pages audited: Term Review (Pass 1/2), Phrase Suggestions (Pass 3), Rejected Terms tab, Negative Keyword Lists tab, AI Co-pilot side panel, AI confirm modal, canned-reply pills, "Only unsure" empty banner, Pass 3 theme banner, Pass 3 failure banner.
- Issues found: 38
- Categorised by:
  - Sentence case violations: 10
  - Em-dash slip-ins: 6
  - Dark mode gaps: 7
  - Tooltip coverage: 3
  - Hover and focus states: 2
  - Vestigial / dead code: 2
  - Visual consistency vs Account: 2
  - Filter pill behaviour: 2
  - Alignment bugs: 1
  - Typography drift: 1
  - Sortable header glyphs: 1
  - Mobile / narrow viewport: 1

Two-thirds of the punch-list is "rules-of-the-road" cleanup (sentence case, em-dashes, dark mode). The other third is structural polish (focus rings, tooltips, pill consistency, dead-code removal).

## Issues

### [001] AI Verdict pill renders in ALLCAPS
- **Page:** Term Review (Pass 1/2)
- **Category:** Sentence case
- **Severity:** high
- **Current:** Pills show `BLOCK` / `DON'T BLOCK` / `UNSURE`. Driven by both a hardcoded label map in JS (`AI_VERDICT_LABEL`, line 624 of v2_search_term_review.js) and a `text-transform: uppercase` CSS rule on `.ai-verdict-pill` (line 601 of v2_search_term_review.css).
- **Suggested fix:** Switch the JS labels to `Block` / `Don't block` / `Unsure` (sentence case) and drop the `text-transform: uppercase` from the CSS rule. Update the column-header tooltip on line 288 of the template to match.
- **Effort:** 5 min

### [002] AI Confidence pill renders in ALLCAPS
- **Page:** Term Review (Pass 1/2)
- **Category:** Sentence case
- **Severity:** med
- **Current:** Pills show `HIGH` / `MEDIUM` / `LOW` because of `text-transform: uppercase` on `.ai-conf-pill` (line 616 of v2_search_term_review.css). The DB stores the value lowercase, so the source is already sentence case; only the CSS is forcing the change.
- **Suggested fix:** Drop the `text-transform: uppercase` line from `.ai-conf-pill`. No JS change needed.
- **Effort:** 2 min

### [003] AI chat verdict pills render in ALLCAPS
- **Page:** AI Co-pilot panel (markdown tables rendered by chat)
- **Category:** Sentence case
- **Severity:** med
- **Current:** Verdict pills inside chat markdown tables show `BLOCK` / `KEEP` / `UNSURE` via `text-transform: uppercase` on `.ai-chat-table td.verdict-cell .verdict-pill` (line 1235 of v2_search_term_review.css). Opus emits lowercase tokens (verified via `_classifyVerdict` in v2_search_term_review.js).
- **Suggested fix:** Drop the `text-transform: uppercase` from that rule.
- **Effort:** 2 min

### [004] AI Theme Summary banner title renders in ALLCAPS
- **Page:** Phrase Suggestions (Pass 3)
- **Category:** Sentence case
- **Severity:** med
- **Current:** The template writes `AI Theme Summary` (Title Case) but `.st-p3-theme-banner__title` (line 1341 of v2_search_term_review.css) applies `text-transform: uppercase`, so it renders `AI THEME SUMMARY`.
- **Suggested fix:** Drop `text-transform: uppercase` from that selector. Also change the template text from `AI Theme Summary` to `AI theme summary` to lock sentence case at source.
- **Effort:** 3 min

### [005] Action-bar button labels mix sentence case and Title Case
- **Page:** Term Review (Pass 1/2) + Phrase Suggestions (Pass 3)
- **Category:** Sentence case
- **Severity:** high
- **Current:**
  - `Don't Block` (template line 134) - "Block" capitalised mid-phrase
  - `AI Triage` (line 154) - "Triage" capitalised
  - `AI Route` (line 161) - same
  - `Push to GAds Neg Lists` (line 172) - "Neg" + "Lists" both capitalised
  - `Apply AI routing` (line 166) is already correct
- **Suggested fix:** Sentence case: `Don't block`, `AI triage`, `AI route`, `Push to GAds neg lists`. Note: tab labels (`Term Review`, `Phrase Suggestions`, `Negative Keyword Lists`, `Rejected Terms`) were locked to Title Case by Chris in Section E and should stay as-is. Pass 3 / Pass 1 / Pass 2 are system names and stay capitalised.
- **Effort:** 3 min

### [006] AI Co-pilot panel title is Title Case
- **Page:** AI Co-pilot panel
- **Category:** Sentence case
- **Severity:** med
- **Current:** Header reads `AI Co-pilot` (template line 474). Project memory locked sentence case for ACT user-facing copy.
- **Suggested fix:** `AI co-pilot`.
- **Effort:** 1 min

### [007] Column headers `AI Verdict` / `AI Conf` are Title Case
- **Page:** Term Review (Pass 1/2)
- **Category:** Sentence case
- **Severity:** low
- **Current:** Template lines 288-289. Other column headers on the same table are sentence case (`Status`, `Reason`, `Target list`, `Match type`, `Added / Excl`, `Campaign`, `Campaign type`, `Cost`, `Impr`, `Clicks`, `Avg CPC`, `CTR`, `Conv`, `Cost/Conv`, `Conv rate`, `Push error`, `Explain`). The `AI` prefix is fine; just the second word capitalisation is the inconsistency.
- **Suggested fix:** `AI verdict` and `AI conf`. Also `AI Role` / `AI Conf` headers on the Pass 3 table (template lines 322-323) for symmetry.
- **Effort:** 2 min

### [008] Reason chip labels emit em-dashes throughout
- **Page:** Term Review (Pass 1/2)
- **Category:** Em-dash
- **Severity:** high
- **Current:** v2_search_term_review.js lines 73-120 produce reason labels like `Leak [em-dash] exact: <term>`, `Leak [em-dash] phrase`, `Mixed intent [em-dash] <detail>`, `Sticky rejected [em-dash] <detail>`, `Needs Review [em-dash] no phrase match` (with literal U+2014 characters in the source). Plus a `const EMDASH = '[em-dash]'` (literal em-dash) on line 248 is used to join detail fragments throughout the renderer.
- **Suggested fix:** Global swap em-dash to hyphen in every label literal in that section + change the EMDASH constant. Visual impact identical, rule compliance restored. While in the file, also fix the static reason map on lines 118-120.
- **Effort:** 10 min

### [009] Empty-cell placeholder uses em-dash
- **Page:** Every table in the module
- **Category:** Em-dash
- **Severity:** med
- **Current:** Empty cells render `[em-dash]` (em-dash) as a visual filler, both in HTML (`<span class="ai-verdict-empty">[em-dash]</span>`) and in many JS string defaults (`humanRole`, `formatCountdown`, `fmtDate`, etc.). About 10-15 occurrences across v2_search_term_review.js + v2_rejected_terms.js + v2_negative_lists.js.
- **Suggested fix:** Swap to hyphen `-` everywhere. Single grep + replace; no visual layout impact (cell still reads as "no value"). Consider whether Chris wants a softer placeholder like `[em-dash]` swap to something more neutral (e.g. a dot `·` or just empty) - flag as question.
- **Effort:** 10 min

### [010] Date picker tooltip uses em-dash inside user-facing copy
- **Page:** Topbar (all 4 tabs)
- **Category:** Em-dash
- **Severity:** med
- **Current:** Template line 22: `title="The picker shows analysis_date [em-dash] the date ACT analysed.&#10;Selected date X displays activity from date X-1...."`. Em-dash inside a hover tooltip the user reads.
- **Suggested fix:** Replace with hyphen and rephrase slightly so the sentence reads cleanly: `The picker shows analysis_date - the date ACT analysed.`
- **Effort:** 1 min

### [011] Pass 3 start toast uses em-dash
- **Page:** Phrase Suggestions (Pass 3)
- **Category:** Em-dash
- **Severity:** low
- **Current:** v2_search_term_review.js line 2094: `toast('Pass 3 AI started [em-dash] this can take 30s to 5min depending on dataset size.', 'info')`.
- **Suggested fix:** Swap em-dash to hyphen.
- **Effort:** 1 min

### [012] AI chat empty-state copy uses em-dash
- **Page:** AI Co-pilot panel
- **Category:** Em-dash
- **Severity:** low
- **Current:** Template line 491: `Ask me anything about the rows you're triaging [em-dash] patterns, clusters, specific terms, anomalies.`
- **Suggested fix:** Swap em-dash to hyphen or rephrase as two sentences.
- **Effort:** 1 min

### [013] AI panel context empty placeholder uses em-dash
- **Page:** AI Co-pilot panel
- **Category:** Em-dash
- **Severity:** low
- **Current:** Template line 481: `<span class="ai-panel-context-empty">[em-dash]</span>`. Same em-dash filler as the table cells.
- **Suggested fix:** Swap to hyphen (or pair with [009] as a single sweep).
- **Effort:** 1 min

### [014] Dead `.neg-sync-pill` CSS still present
- **Page:** Module-wide CSS
- **Category:** Vestigial / dead code
- **Severity:** med
- **Current:** v2_search_term_review.css lines 503-512 still define `.neg-sync-pill` + four `.neg-sync--*` colour variants. The pill element was removed from the template in the Section E IA refactor (14 May) and replaced by the shared `.act-last-ran` badge. Comments in the JS + template both acknowledge the removal. CSS was missed.
- **Suggested fix:** Delete lines 503-512 of v2_search_term_review.css. Confirmed no other file references `.neg-sync-pill`.
- **Effort:** 2 min

### [015] Dead `loadSyncPill()` comments + unreachable banner-empty CSS block
- **Page:** Module-wide
- **Category:** Vestigial / dead code
- **Severity:** low
- **Current:** Several long comment blocks in v2_search_term_review.js (lines 2460-2495 area) describe the removed neg-sync-pill flow. Useful as audit trail, but a one-line "removed in Section E" comment would do.
- **Suggested fix:** Trim comments to a single line referencing the IA refactor commit. Optional, low impact.
- **Effort:** 3 min

### [016] AI confidence pill colours have no dark-mode variants
- **Page:** Term Review (Pass 1/2)
- **Category:** Dark mode
- **Severity:** high
- **Current:** v2_search_term_review.css lines 619-621 define `.ai-conf-high` (#d1fae5 / #065f46), `.ai-conf-medium` (#fef3c7 / #92400e), `.ai-conf-low` (#fee2e2 / #991b1b). Hardcoded greens/ambers/reds with no `[data-theme="dark"]` overrides. In dark mode the pill backgrounds will be too bright for the dark surface.
- **Suggested fix:** Add `[data-theme="dark"] .ai-conf-*` rules with the same colour-token pattern KW History uses (rgba(... ,0.18) backgrounds + lighter foreground).
- **Effort:** 5 min

### [017] AI chat verdict pill colours have no dark-mode variants
- **Page:** AI Co-pilot panel
- **Category:** Dark mode
- **Severity:** med
- **Current:** v2_search_term_review.css lines 1239-1247 set `.verdict-block` / `.verdict-keep` / `.verdict-unsure` with hardcoded hex. Same pattern as [016].
- **Suggested fix:** Add dark-mode variants matching [016].
- **Effort:** 5 min

### [018] Status badges `.st-status--rejected` / `.st-status--expired` lack dark-mode variants
- **Page:** Term Review (Pass 1/2)
- **Category:** Dark mode
- **Severity:** med
- **Current:** v2_search_term_review.css lines 411-412. Hardcoded `#f3f4f6` grey background + `#6b7280` / `#9aa0a6` foreground. In dark mode the grey-on-white pill is invisible.
- **Suggested fix:** Add `[data-theme="dark"]` overrides using existing tokens.
- **Effort:** 3 min

### [019] `.st-risk--low` lacks dark-mode variant
- **Page:** Phrase Suggestions (Pass 3) - risk column
- **Category:** Dark mode
- **Severity:** med
- **Current:** v2_search_term_review.css line 422. Same hardcoded grey-on-white as [018].
- **Suggested fix:** Add dark-mode variant.
- **Effort:** 2 min

### [020] `.btn-act--ai:hover` uses hardcoded `#1d4ed8`
- **Page:** Action bar (multiple buttons)
- **Category:** Dark mode
- **Severity:** med
- **Current:** v2_search_term_review.css line 677. Hardcoded blue hover with no dark-mode override. Same hardcoded value reappears in `.ai-panel-strip:hover` (line 981) and `.ai-confirm-ok--primary:hover` (line 825).
- **Suggested fix:** Either swap to a `var(--act-primary-hover)` token (introducing it in v2_base.css with both light + dark values) or add explicit `[data-theme="dark"]` overrides for each rule. Token approach is cleaner.
- **Effort:** 8 min

### [021] `.ai-confirm-ok--danger:hover` uses hardcoded `#dc2626`
- **Page:** AI confirm modal
- **Category:** Dark mode
- **Severity:** low
- **Current:** v2_search_term_review.css line 830. No dark-mode variant.
- **Suggested fix:** Same approach as [020] - token or explicit override.
- **Effort:** 2 min

### [022] Confirm-modal accent rules use hardcoded colours
- **Page:** AI confirm modal + filter modal
- **Category:** Dark mode
- **Severity:** low
- **Current:** `.act-confirm__ok` `#0b8a3e`, `.act-confirm__change` `#1e40af`, `.act-confirm__add` `#6b7280` (lines 534-536). No dark-mode variants.
- **Suggested fix:** Add `[data-theme="dark"]` variants for each (use the `#34d399` / `#93c5fd` / muted-white pattern used elsewhere in the module).
- **Effort:** 3 min

### [023] Pass 3 column headers have no tooltips for jargon terms
- **Page:** Phrase Suggestions (Pass 3)
- **Category:** Tooltips
- **Severity:** med
- **Current:** Template lines 311-323. Headers `Fragment` / `Words` / `Target list` / `Occ` / `Risk` / `Status` / `Source terms` / `Push error` / `AI Role` / `AI Conf` carry no `title=""`. `Occ` and `Risk` in particular are abbreviations a new user won't decode.
- **Suggested fix:** Add `title=""` tooltips on every Pass 3 header that isn't self-explanatory. Suggested wording (sentence case, hyphens):
  - `Words`: `Word count in the fragment.`
  - `Occ`: `Occurrence count - how many distinct search terms this fragment covers today.`
  - `Risk`: `AI risk rating for this fragment (low / med / high).`
  - `Source terms`: `Up to 3 search terms this fragment was derived from.`
  - `Push error`: `Error message from Google Ads if the push failed.`
  - `AI Role`: `AI-suggested target list role for this fragment.`
  - `AI Conf`: `AI confidence in the suggested role (high / medium / low).`
- **Effort:** 10 min

### [024] Rejected Terms stat tiles have no tooltips
- **Page:** Rejected Terms tab
- **Category:** Tooltips
- **Severity:** low
- **Current:** Template lines 369-372. Stat tiles `Active rejections` / `Expired (last 30d)` / `Total cycles recorded` / `Avg cycles / term` have no `title=""`. KW & ST History applied tooltips to every stat tile (round 3) so this is a consistency gap.
- **Suggested fix:** Add `title=""` tooltips matching the KW History pattern. Suggested wording:
  - `Active rejections`: `Sticky rejections still in their cool-down window.`
  - `Expired (last 30d)`: `Sticky rejections whose cool-down expired in the last 30 days.`
  - `Total cycles recorded`: `Lifetime count of approve - reject - re-approve cycles.`
  - `Avg cycles / term`: `Average number of cycles per rejected term.`
- **Effort:** 3 min

### [025] Negative Lists stat tiles have no tooltips
- **Page:** Negative Keyword Lists tab
- **Category:** Tooltips
- **Severity:** low
- **Current:** Rendered by v2_negative_lists.js render(). Stats are `Total lists` / `Total keywords` / `Snapshot date` / `Last synced`. None carry `title=""`.
- **Suggested fix:** Add tooltips. Suggested wording:
  - `Total lists`: `Number of negative-keyword lists in the latest GAds snapshot.`
  - `Total keywords`: `Sum of negative keywords across all lists.`
  - `Snapshot date`: `Date the snapshot was taken in GAds.`
  - `Last synced`: `Last time ACT refreshed the snapshot.`
- **Effort:** 3 min

### [026] No keyboard focus rings on `.pill-btn`, `.btn-act`, `.st-tab`
- **Page:** Every page in the module
- **Category:** Hover / focus
- **Severity:** med
- **Current:** Default browser outline is either left alone (most buttons) or actively suppressed (`outline: none` in `.st-date-help` line 25, `.pmax-info-icon` line 114). Only `.ai-confirm-ok:focus-visible` defines an explicit ring (line 831). Means keyboard users get inconsistent focus feedback.
- **Suggested fix:** Add a shared `:focus-visible` ring to `.pill-btn`, `.btn-act`, `.st-tab` (in v2_shared.css alongside the existing `.pill-btn` rules). Use `outline: 2px solid var(--act-primary); outline-offset: 2px;`. Decision needed: does Chris want focus rings everywhere or only on tabs and modal CTAs?
- **Effort:** 15 min

### [027] `.st-date-help` and `.pmax-info-icon` suppress focus outline
- **Page:** Topbar info icon + Pass 1/2 PMax info icon
- **Category:** Hover / focus
- **Severity:** low
- **Current:** Both rules end with `outline: none;` on `:focus`. They use `cursor: help` so they're tabbable, but the focus ring is removed without a visual replacement.
- **Suggested fix:** Replace `outline: none` with the shared focus-visible ring from [026], or move `tabindex="0"` to `-1` if these aren't meant to be focusable (currently `tabindex="0"` on the date-help span).
- **Effort:** 3 min

### [028] Pass 3 wrap-cells vertical-align top while everything else is middle
- **Page:** Phrase Suggestions (Pass 3)
- **Category:** Alignment bugs
- **Severity:** low
- **Current:** v2_search_term_review.css line 282: `.st-table td.wrap-cell { ... vertical-align: top; }`. Term Review table was migrated to `vertical-align: middle` in Section 2 (matches Account .data-table). Pass 3's `wrap-cell` class was missed. Pass 3 rows with wrapping cells (Source terms, Push error) sit top-aligned next to middle-aligned numeric cells.
- **Suggested fix:** Change `vertical-align: top` to `middle` on line 282. Visual scan to confirm no Pass 1/2 cell currently relies on top-align for very-long Reason text - if it does, scope this fix to Pass 3 only via `#stP3Table td.wrap-cell` selector.
- **Effort:** 5 min

### [029] Rejected Terms status pill order has `All` last
- **Page:** Rejected Terms tab
- **Category:** Filter pill behaviour
- **Severity:** med
- **Current:** Template lines 380-382 render `[Active] [Expired] [All]`. Convention everywhere else (Term Review, KW History, Negative Lists) puts `All` first. Also the default-selected pill is `Active` not `All`, which is intentional (sticky rejections workflow defaults to "show me what's currently blocking") but the All-at-the-end placement breaks the visual rhythm.
- **Suggested fix:** Reorder to `[All] [Active] [Expired]` with `Active` still default-selected (so the workflow keeps its current default). Or accept the deviation and document it.
- **Effort:** 3 min

### [030] Rejected Terms pills lack count badges
- **Page:** Rejected Terms tab
- **Category:** Filter pill behaviour
- **Severity:** low
- **Current:** Pills show just labels (`Active` / `Expired` / `All`). KW History pills carry `.pill-btn__count` badges showing how many rows are in each bucket. Term Review pills also carry counts. Rejected Terms is the odd one out.
- **Suggested fix:** Render `.pill-btn__count` badges populated from the stats payload already returned by `/v2/api/sticky-rejections`. Same pattern as KW History round 3.
- **Effort:** 10 min

### [031] Search Terms uses `.act-card`; Account uses `.acct-section` - documented deviation
- **Page:** Module-wide
- **Category:** Visual consistency
- **Severity:** low
- **Current:** Account is the gold standard but uses `.acct-section` / `.acct-section__header` / `.acct-section__body` with an `<h3 class="acct-section__title">` per section. Search Terms (post Section 2 polish) uses the sibling `.act-card` primitive in v2_shared.css with no card title. Visual rules are mirrored, class names diverge. Flagged at the time as "deviation: mirror visuals via .act-card rather than rename Account's .acct-section".
- **Suggested fix:** Question for Chris - does he want to converge? Two options:
  - Option A: leave as-is (acct-section + act-card both alive, both styled to look identical).
  - Option B: migrate Account to `.act-card` so the codebase has one primitive (~30 min, touches Account template + CSS).
- **Effort:** 0 min (question) or 30 min if Option B is chosen

### [032] No `<h3>` heading on Search Terms cards
- **Page:** Module-wide
- **Category:** Visual consistency / Typography
- **Severity:** low
- **Current:** Account .acct-section has an h3 title at the top of each section ("Performance", "Budget Allocation", etc.). Search Terms .act-card has no h3 - the tab row is the only heading. Hierarchy is "page title (h1) → tab row → card body" with no h2/h3 in between.
- **Suggested fix:** Question for Chris - does the tab row serve the heading role well enough? If yes, leave as-is. If not, consider an h3 sub-heading per tab body (e.g. "Term review", "Phrase suggestions") which would also help screen readers.
- **Effort:** 0 min (question) or 10 min if added

### [033] Pass 3 table headers have no sort glyphs
- **Page:** Phrase Suggestions (Pass 3)
- **Category:** Sortable header glyphs
- **Severity:** low
- **Current:** Pass 3 headers carry no `.st-sortable` class and no `unfold_more` Material Icon. Term Review headers do. Deliberate per the comment ("Pass 3 has no client-side sort wiring") but visually inconsistent.
- **Suggested fix:** Question for Chris - does he want client-side sort wired on Pass 3 (cost / impressions / clicks columns) or does he want Pass 3 to stay un-sorted because the AI's row order is already the recommended priority? If wiring is wanted, ~30 min to add client-side sort to Pass 3. If not, leave as-is.
- **Effort:** 0 min (question) or 30 min if wired

### [034] No `@media` queries below 1024px
- **Page:** Module-wide
- **Category:** Mobile / narrow viewport
- **Severity:** low
- **Current:** Only one `@media (max-width: 1023px)` block in v2_search_term_review.css. The Pass 1/2 wide table relies on horizontal scroll, the AI panel collapses below 1024px, but stat tiles, action bar, and pager don't gracefully reflow. Account page also has no media queries, so this is consistent across ACT.
- **Suggested fix:** Question for Chris - is mobile / tablet support in scope for ACT? If no, document the desktop-only assumption and skip. If yes, ~1-2h to add responsive treatments across the module.
- **Effort:** 0 min (question) or 1-2h if responsive treatment is wanted

### [035] Action-bar emoji-prefix buttons feel different from Account
- **Page:** Term Review action bar
- **Category:** Visual consistency
- **Severity:** low
- **Current:** Buttons `🤖 AI triage`, `🤖 AI route`, `✅ Apply AI routing`, `♻️ Reclassify today's terms`, `🔍 Explain` (per-row), `💬` empty-state, `🗑️ Clear`, `🤖<br>Expand` strip. Account page buttons use Material Symbols icons instead (e.g. `<span class="material-symbols-outlined">refresh</span>`). KW History export buttons followed Account's pattern. Module looks "playful" next to the rest of ACT.
- **Suggested fix:** Question for Chris - swap to Material Icons? `🤖` → `auto_awesome`, `✅` → `check_circle`, `♻️` → `refresh`, `🔍` → `search`, `💬` → `chat`, `🗑️` → `delete`. ~20 min sweep across template + JS.
- **Effort:** 0 min (question) or 20 min if swapped

### [036] Reason filter row lacks "multi-select" affordance
- **Page:** Term Review (Pass 1/2)
- **Category:** Filter pill behaviour
- **Severity:** low
- **Current:** Status pill row is single-select (one active at a time). Reason pill row directly below it is multi-select. Both look identical - no visual cue that Reason behaves differently. New users may not realise they can toggle multiple Reason pills.
- **Suggested fix:** Add a small hint in the Reason filter-bar label - either "Reason (any)" or "Reason (pick one or more)". Or rely on a tooltip on the row label.
- **Effort:** 2 min

### [037] AI action badge count uses parenthesised format `(0 pending)`
- **Page:** Term Review action bar
- **Category:** Typography drift
- **Severity:** low
- **Current:** `🤖 AI triage (0 pending)`, `🤖 AI route (0 pending)`, `✅ Apply AI routing (0)`. Inconsistent: two say `(0 pending)`, one just `(0)`. Tab badges and status pills use the `.pill-btn__count` chip-style badge instead. Two different badge conventions in the same action bar.
- **Suggested fix:** Pick one. Either move the per-button counts into `.pill-btn__count`-style chips for consistency, or drop the words ("(0 pending)" → "(0)") so all three buttons match each other.
- **Effort:** 5 min

### [038] Pass 1/2 table empty-state copy uses a colspan-23 ellipsis row
- **Page:** Term Review (Pass 1/2)
- **Category:** Loading + empty states
- **Severity:** low
- **Current:** Template line 294: `<tr><td colspan="23" class="st-loading">Loading…</td></tr>`. Pass 3 line 327 has a better one: `Run Pass 3 to generate suggestions`. Term Review's loading state is plain "Loading…" with no spinner or skeleton. Account page uses `<tr class="loading-row">` with a spinner via CSS. Mild inconsistency.
- **Suggested fix:** Optional - add a Material Icon spinner glyph (`progress_activity`) with a slow rotate animation. Or accept the plain text. Question for Chris.
- **Effort:** 0 min (question) or 10 min if spinner added

---

## Recommended fix order

### Must-fix (visual bugs, broken states, accessibility failures)
Sentence-case violations and dark-mode gaps are rule violations Chris already locked in writing. Focus rings are an a11y baseline.
- [001] AI Verdict pill ALLCAPS
- [002] AI Confidence pill ALLCAPS
- [003] AI chat verdict pills ALLCAPS
- [004] AI Theme Summary ALLCAPS
- [005] Action-bar button labels Title Case
- [006] AI Co-pilot panel title Title Case
- [008] Reason chip em-dashes
- [009] Empty-cell em-dash placeholder
- [014] Dead .neg-sync-pill CSS
- [016] AI confidence pill no dark mode
- [017] AI chat verdict no dark mode
- [018] Status badges no dark mode
- [019] .st-risk--low no dark mode
- [020] .btn-act--ai:hover hardcoded
- [026] No keyboard focus rings on key controls

**Subtotal: 15 issues, ~75 min**

### Should-fix (consistency wins, polish that affects daily UX)
Tooltip gaps and pill-behaviour issues hurt the daily workflow but aren't bugs.
- [007] AI Verdict / AI Conf column header Title Case
- [010] Date picker tooltip em-dash
- [011] Pass 3 start toast em-dash
- [012] AI chat empty-state em-dash
- [013] AI panel context empty em-dash
- [021] Confirm-danger hover hardcoded
- [022] Confirm-modal accent hardcodes
- [023] Pass 3 column tooltips
- [024] Rejected Terms stat tooltips
- [025] Negative Lists stat tooltips
- [028] Pass 3 vertical-align top vs middle
- [029] Rejected Terms pill order
- [030] Rejected Terms pill count badges
- [037] AI action badge format inconsistency

**Subtotal: 14 issues, ~65 min**

### Nice-to-have (subtle refinements, low impact)
Mostly questions for Chris + low-impact cleanup.
- [015] Trim dead-code comments
- [027] Tabindex on `.st-date-help`
- [031] .act-card vs .acct-section convergence (question)
- [032] No h3 on Search Terms cards (question)
- [033] Pass 3 sortable headers (question)
- [034] @media coverage (question)
- [035] Emoji-prefix buttons vs Material Icons (question)
- [036] Reason multi-select affordance
- [038] Loading-state spinner

**Subtotal: 9 issues, ~20 min for cleanup items, the questions need Chris's call before estimating.**

---

**Total effort if every fixable item shipped: ~160 min (~2h 40min) of focused work**, excluding the open questions ([031], [032], [033], [034], [035], [038]) which together could add another 2-3h if all answered "yes".

Recommended sequencing for one focused session: Must-fix first (single commit of ~75 min), Should-fix second (single commit of ~65 min), then surface the questions for Chris before touching anything in Nice-to-have.
