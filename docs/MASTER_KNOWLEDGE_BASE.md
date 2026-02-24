# MASTER KNOWLEDGE BASE - ADS CONTROL TOWER (A.C.T)

**Version:** 10.0
**Created:** 2026-02-19
**Updated:** 2026-02-24
**Purpose:** Complete project context for Master Chat coordination

---

## EXECUTIVE SUMMARY

### Current State (Feb 24, 2026)
- **Overall Completion:** ~99%
- **Phase:** Marketing Website ✅ COMPLETE | Dashboard 3.0 M9 ✅ COMPLETE (Both Phases)
- **Active Development:** Ready for Phase 3 (Future-Proofing)
- **Marketing Website:** Live at https://www.christopherhoole.online
- **Templating:** Jinja2 Macros (metrics_section M2 + performance_chart M3)

### Tech Stack

**A.C.T Dashboard:**
- **Backend:** Python 3.11, Flask
- **Database:** DuckDB (warehouse.duckdb)
- **API:** Google Ads API (v15)
- **Frontend:** Bootstrap 5.3, Chart.js 4.4, Vanilla JS, Flatpickr
- **Templating:** Jinja2 Macros (metrics_section macro from M2)

**Marketing Website:**
- **Framework:** Next.js 14
- **Styling:** Tailwind CSS
- **Animation:** Framer Motion
- **Components:** shadcn/ui
- **Hero:** Three.js WebGL (r128)
- **Hosting:** Vercel
- **Domain:** christopherhoole.online (GoDaddy DNS)

---

## COMPLETE CHAT HISTORY

### Phase 0: Foundation (Chats 1-17) ✅
- Chats 1-11: Flask app, DuckDB, auth, multi-client YAML
- Chat 12: Shopping module (14 rules, 4-tab UI, 3,800 lines)
- Chat 13.1: Constitution execution engine (safety guardrails, dry-run + live)
- Chat 14: Dashboard execution UI (buttons, toasts, change history)
- Chat 17: Architecture refactor — unified recommendation system

### Phase 1: Code Cleanup ✅
- 16/16 routes → 8 modular blueprints
- Input validation, rate limiting, logging, cache, error handling

### Phase 2: Polish ✅
- DRY helpers, type hints, config validation

### Chat 21: Dashboard UI Overhaul ✅
All 6 pages rebuilt with Bootstrap 5:
- 21a: Bootstrap foundation + base_bootstrap.html (commit 5789628)
- 21b: Main dashboard + Chart.js trend (commit 4976a29)
- 21c: Campaigns + Rule Visibility System (commit 3ab82a2)
- 21d: Keywords + QS distribution (commit f0fbd15)
- 21e: Ad Groups
- 21f: Ads
- 21g: Shopping (4 tabs)
- 21h: Polish

Key outputs: base_bootstrap.html, rule_helpers.py, rules_sidebar/tab/card components, dynamic category detection (regex: r'_\d{3}(?:_|$)')

### Chat 22 — M1: Date Range Picker ✅
**Date:** 2026-02-19 | **Commits:** a644fdd + 25c7af5
- Flatpickr replacing URL-parameter system
- Session-based persistence across all 6 pages
- Preset (7d/30d/90d) + custom date range

### Chat 23 — M2: Metrics Cards ✅
**Date:** 2026-02-20 | **Commit:** Approved, pending push

Jinja2 macro system on all 6 pages:
- Financial row (8 cards) + collapsible Actions row (8 cards)
- Sparklines on date-range pages (Dashboard/Campaigns/Ad Groups)
- Change % vs prior period on date-range pages
- Session-persisted collapse state (7 page IDs)
- IS metrics added to schema (4 new columns)
- Synthetic data to today (dynamic date.today())

Card layouts:
| Page | Financial (8) | Actions (8) |
|------|---------------|-------------|
| Dashboard/Campaigns/Ad Groups/Keywords | Cost\|Revenue\|ROAS\|Wasted Spend\|Conv\|CPA\|CVR\|blank | Impr\|Clicks\|CPC\|CTR\|Search IS\|Top IS\|Abs Top IS\|Click Share |
| Ads | Cost\|Revenue\|ROAS\|blank\|Conv\|CPA\|CVR\|blank | Impr\|Clicks\|CPC\|CTR\|Ad Strength\|blank x3 |
| Shopping (Campaigns) | Cost\|Conv Value\|ROAS\|blank\|Conv\|Cost/Conv\|CVR\|blank | Impr\|Clicks\|CPC\|CTR\|blank x4 |
| Shopping (Products) | Cost\|ROAS\|blank\|Out of Stock\|Conv\|blank x3 | Products\|Feed Issues\|blank x6 |

Invert colours (red when rising): Cost, Cost/Conv, Wasted Spend
Ad Strength: Actions row ONLY. Format: "240/983" label, "129 Poor" sub_label.
Shopping: Two independent macro calls (shopping_campaigns, shopping_products).

IS columns added: search_impression_share, search_top_impression_share, search_absolute_top_impression_share, click_share

Data types:
- Date-range (Dashboard/Campaigns/Ad Groups): change indicators + sparklines
- Windowed (Keywords/Ads/Shopping): dash indicators, no sparklines

Files modified (17): warehouse_duckdb.py, generate_synthetic_data_v2.py, base_bootstrap.html, macros/metrics_cards.html, shared.py, all 6 route files, all 6 template files

### Chat 25 — M4: Table Overhaul ✅
**Date:** 2026-02-21 | **Commit:** pending

Full Google Ads UI column sets across all 5 pages, server-side sort, sticky first column:

Column specs (locked — do not change without Master Chat approval):
| Page | Cols | Sticky |
|---|---|---|
| Campaigns | 24 | Campaign name |
| Ad Groups | 26 | Ad Group name |
| Keywords | 17 | Keyword |
| Ads | 24 | Ad (final_url) |
| Shopping | 24 | Campaign name |

### Chat 26 — M5: Card-Based Rules Tab ✅
**Date:** 2026-02-22 | **Commit:** 025986a

Replaced dense table-based Rules tab with fully interactive card-based UI on Campaigns page (pilot).

**Architecture — dual-layer (critical — do not break):**
- `act_autopilot/rules_config.json` — UI config layer (CRUD via rules_api.py)
- `act_autopilot/rules/*.py` — execution layer (untouched, Python functions only)
- These layers are intentionally separate. JSON edits never touch Python execution files.

**rules_config.json data model (18 fields per rule):**
```
rule_id, rule_type, rule_number, display_name, name
scope (blanket/specific), campaign_id
condition_metric, condition_operator, condition_value, condition_unit
condition_2_metric, condition_2_operator, condition_2_value, condition_2_unit
action_direction, action_magnitude, risk_level, cooldown_days, enabled
monitoring_days, monitoring_minutes
created_at, updated_at
```

**rules_api.py routes:**
| Route | Method | Purpose |
|---|---|---|
| `/api/rules` | GET | Return all rules |
| `/api/rules/add` | POST | Add rule |
| `/api/rules/<id>/update` | PUT | Edit rule |
| `/api/rules/<id>/toggle` | PUT | Toggle enabled |
| `/api/rules/<id>` | DELETE | Delete rule |
| `/api/campaigns-list` | GET | Campaign names from warehouse |

### Chat 27 — M6: Recommendations Engine + UI ✅
**Date:** 2026-02-22

- recommendations table in warehouse.duckdb (19 cols) + 22 historical rows seeded
- recommendations_engine.py: reads rules_config.json, evaluates campaign_features_daily, inserts pending recs
- Duplicate prevention on (campaign_id, rule_id)
- /recommendations/cards JSON endpoint for JS-rendered inline cards
- Global /recommendations page: Pending (48 cards) / Monitoring / History
- Campaigns → Recommendations tab: 2-col card grids

**Engine proxy column mappings:**
| Needed | Proxy |
|---|---|
| target_roas | Fallback 4.0 (column missing) |
| budget_micros | cost_micros_w7_mean |
| cost_spike_confidence | anomaly_cost_z >= 2.0 |
| pace_over_cap_detected | pacing_flag_over_105 |
| ctr_drop_detected | ctr_w7_vs_prev_pct < -20 |
| cvr_drop_detected | cvr_w7_vs_prev_pct < -20 |

**Card anatomy (locked):**
1. 4px coloured top bar (blue=budget, green=bid, red=status)
2. Header: rule tag + campaign name + status pill
3. Change block FIRST (gradient bg by type)
4. Trigger block SECOND (grey bg, "Why this triggered")
5. Footer: confidence badge + source pill + age
6. Action buttons: Modify / Decline / Accept

**Status pills:** Pending=blue / Monitoring=purple / Successful=green / Reverted=red / Declined=grey

### Chat 28 — M7: Accept/Decline/Modify Wiring + 4-Tab UI ✅
**Date:** 2026-02-22

- Accept / Decline / Modify POST routes — fully wired
- `changes` audit table created in warehouse.duckdb
- `monitoring_days: 0` added to all 13 rules in rules_config.json
- Card fade+slide animations, badge decrements, toast confirmations
- 4-tab UI: Pending / Monitoring / Successful / Declined
- Both /recommendations and /campaigns updated

**Architecture decisions:**
- recommendations.html: server-side Jinja passes all groups, JS shows/hides divs
- campaigns.html: JS fetch from /recommendations/cards (pre-existing pattern maintained)

### Chat 29 — M8: Changes + Radar Monitoring ✅
**Date:** 2026-02-23

**Files created:**
- `act_autopilot/radar.py` — background daemon thread (60s cycle), evaluates monitoring recs, auto-resolves to successful or reverted
- `act_dashboard/routes/changes.py` — new blueprint, /changes route

**Files modified:**
- `act_autopilot/rules_config.json` — added `monitoring_minutes` to all 13 rules
- `act_dashboard/routes/recommendations.py` — removed /changes, added reverted_recs, monitoring_minutes support, last_run fix
- `act_dashboard/routes/__init__.py` — registered changes blueprint
- `act_dashboard/templates/recommendations.html` — 5 tabs (added Reverted)
- `act_dashboard/templates/campaigns.html` — 5 inner tabs + 5 summary cards
- `act_dashboard/templates/changes.html` — full Bootstrap 5 rewrite

**Key technical decisions:**
- DuckDB connection pattern for Radar: `duckdb.connect('warehouse.duckdb')` + `ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)`. **This is now the established pattern for any component needing both read and write access.**
- JOIN strategy for changes → recommendations: no recommendation_id FK exists — use `campaign_id + rule_id` with `QUALIFY ROW_NUMBER() OVER (PARTITION BY campaign_id, rule_id ORDER BY generated_at DESC) = 1`
- System Changes tab is currently a table (ro.analytics.change_log data) — will be converted to cards in a future chat
- Radar revert is DB-only in this chat — no Google Ads API rollback call yet

**executed_by values in changes table:**
| Value | Meaning |
|---|---|
| `user_accept` | User clicked Accept |
| `user_modify` | User modified value then accepted |
| `user_decline` | User clicked Decline |
| `radar_resolved` | Radar: monitoring complete, KPI held |
| `radar_revert` | Radar: KPI degraded, auto-reverted |

**monitoring_minutes:**
All 13 rules now have `monitoring_minutes`. When > 0, takes priority over `monitoring_days`. Default 0 = disabled, uses monitoring_days. Fast-test values: Budget 1→1min, Budget 2→2min, Bid 1→2min, all others→0.

**Test results:** 0 Pending / 1 Monitoring / 57 Successful / 4 Reverted / 8 Declined ✅ All pages confirmed ✅


### Chat 30a: M9 Phase 1 — Search Terms Table + Negative Keyword Suggestions ✅
**Date:** 2026-02-24
**Summary:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_30A_SUMMARY.md`
**Handoff:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_30A_HANDOFF.md`

- Search Terms tab added to Keywords page (Bootstrap 5)
- 16-column data table from `ro.analytics.search_term_daily`
- Advanced filtering: campaign, status, match type dropdowns + client-side search
- Server-side pagination (10/25/50/100 rows per page)
- Negative keyword flagging logic (3 automated criteria):
  1. 0% CVR + ≥10 clicks
  2. ≥£50 cost + 0 conversions
  3. CTR <1% + ≥20 impressions
- Row-level + bulk "Add as Negative" buttons (UI only, no live execution)
- Bootstrap 5 modal for action preview
- All 16 success criteria passing
- Performance: <2s load, <1s filter, 0 JS errors
- Deferred to Phase 2: Live Google Ads API execution, keyword expansion

**Files modified:**
- `routes/keywords.py` (431 lines) - `load_search_terms()` rewrite, flagging logic
- `templates/keywords_new.html` (216 lines) - new tab, table, filters, modal, JS

**Key technical decisions:**
- Used session date range from M1 (not hardcoded 30 days)
- Used `cost` column (DOUBLE) vs `cost_micros` (already in client currency)
- Separate `flag_negative_keywords()` function for clean separation
- Client-side search (instant) vs server-side (cross-page would require reload)
- Bulk selection tracked in JavaScript array for cross-page persistence

### Chat 30b: M9 Phase 2 — Live Execution + Keyword Expansion ✅
**Date:** 2026-02-24
**Summary:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_30B_SUMMARY.md`
**Handoff:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_30B_HANDOFF.md`
**Time:** 4 hours actual (53% of 7-9h estimated)

- Live Google Ads API execution for negative keyword blocking
- Campaign-level + ad-group-level negative keyword support
- Keyword expansion opportunities flagging (4 criteria: CVR ≥5%, ROAS ≥4.0x, Conv. ≥10, NOT exists)
- "Add as Keyword" buttons on flagged rows with match type + bid suggestions
- Dry-run mode for safe testing (validates without executing)
- Changes table audit logging for both actions
- Row-level + bulk selection support
- Match type override dropdowns (EXACT/PHRASE/BROAD)
- Bid override inputs (£0.10 minimum)
- Toast notifications (success/error)
- All 16 success criteria passing (dry-run validated)

**Files modified:**
- `google_ads_api.py` (+84 lines) - Added `add_adgroup_negative_keyword()` function
- `routes/keywords.py` (+456 lines) - Added 2 POST routes + 2 helper functions:
  - `/keywords/add-negative` - Execute negative keyword blocking
  - `/keywords/add-keyword` - Execute keyword expansion
  - `check_keyword_exists()` - Duplicate prevention
  - `flag_expansion_opportunities()` - 4-criteria flagging logic
- `templates/keywords_new.html` (~400 lines) - Updated table + 2 modals + JavaScript

**Key technical decisions:**
- **Dry-run first architecture** - Check dry_run flag BEFORE loading Google Ads client (enables testing without credentials)
- **Google Ads config path detection** - Try 3 locations (root, configs/, secrets/) with clear error if not found
- **Expansion criteria thresholds** - CVR ≥5% (conservative, 2x industry average), ROAS ≥4.0x (highly profitable), Conv. ≥10 (statistical significance)
- **Match type suggestions** - EXACT→EXACT, PHRASE→PHRASE, BROAD→PHRASE (conservative tightening)
- **Sequential execution** - One-by-one (not batched) for simpler error handling, sufficient for <10 items
- **Partial success support** - Continue on failures, report at end (user gets maximum value)
- **Campaign-level default** - Safer starting point for negative keywords, user can opt-in to ad-group-level

**Production readiness:**
- Code complete, dry-run validated, ready for live testing with real Google Ads account
- Deferred: Batching for >10 items, CSRF protection, undo/rollback functionality

### Marketing Website — ChristopherHoole.online ✅
**Date:** 2026-02-23
**Chat 31:** Wireframe creation (13 sections designed, 306KB with base64 images)
**Master Chat 4.0:** Full rebuild + deployment

**Tech Stack:**
- Next.js 14 (React framework)
- Tailwind CSS (utility-first styling)
- Framer Motion (animations)
- shadcn/ui (component library)
- Three.js WebGL r128 (interactive hero shader)
- Vercel (hosting + deployment)
- GoDaddy DNS → Vercel custom domain

**Completed Sections (11/13):**
1. ✅ **S1: Hero** — Three.js interactive liquid shader, 20px h1, centered layout, scroll indicator
   - User hovers over image to reveal A.C.T version
   - Custom shader with angle-based noise for organic liquid effect
   - Two-layer image system (Christopher base + A.C.T reveal)
2. ✅ **S2: About Me** — Dark bg, 4 paragraphs, blue highlights on key phrases, bullet points
3. ✅ **S3: The Problem** — White bg, 3-column card grid, 20px titles, 19px content
4. ✅ **S4: The Difference** — Dark bg, 3 paragraphs with blue highlights
5. ✅ **S5: Work History** — White bg, vertical timeline, 7 positions, 16px titles
6. ✅ **S6: Skills & Platforms** — Dark bg, 4-column grid (responsive), 8 cards
   - Card titles: 20px bold blue sentence case
   - Card content: 16px pure white
   - Categories: Paid Advertising, Analytics, CRM, E-commerce, AI, Budget Mgmt, Industries, Languages
7. ✅ **S7: What A.C.T Does** — White bg, 2×2 module grid + capabilities box
   - 4 modules: Lighthouse, Radar, Flight Plan, Autopilot
   - Module titles: 20px bold black, subtitles: 18px blue
   - Bullet lists: 16px pure black with visible bullets
8. ❌ **S8: How I Work** — REMOVED (not needed for initial launch)
9. ❌ **S9: What You Get Each Week** — REMOVED (not needed for initial launch)
10. ✅ **S10: Why I'm Different** — Light gray bg, 3-column grid (responsive), 16 USP cards
    - Card titles: 20px bold pure black
    - Card content: 16px pure black
    - Emoji icons: 28px
11. ✅ **S11: FAQ** — White bg, 10 collapsible questions, max-width 800px
    - Questions: 20px bold black clickable
    - Answers: 16px gray
    - Accordion style (one open at a time, all closed by default)
    - Plus (+) when closed, Minus (−) when open
12. ✅ **S12: Contact Form** — Dark bg, 2-column layout (form + what happens next)
    - 6 fields (Name, Company, Role, Looking for, Email, Phone)
    - Frontend validation complete
    - Backend: POST to /api/leads (pending — will integrate with A.C.T dashboard)
13. ✅ **S13: Footer** — Very dark bg, 18px pure white monospace
    - Left: "Christopher Hoole · © 2026"
    - Right: "LinkedIn · chrishoole101@gmail.com · Built by Christopher Hoole 2026"
14. ✅ **Navigation** — Fixed top, dark bg with backdrop blur
    - Left: A.C.T logo (32×32) + "Christopher Hoole" (20px bold white)
    - Right: About - Experience - A.C.T links (18px pure white, sentence case) + CTA button (14px)

**Typography System:**
```css
.text-body-dark { font-mono, 18px, white, line-height: 1.75 }
.text-body-light { font-mono, 18px, #0f172a, line-height: 1.75 }
```
- Section eyebrows: 20px bold blue uppercase with 24px blue line prefix
- Section headings: 36px bold serif (Georgia)
- Card titles: 20px bold (increased from initial 14-18px)
- Card content: 16px (standard across all card-based sections)
- Navigation links: 18px pure white

**Color Palette:**
- Primary blue: #2563eb (links, accents, buttons)
- Dark background: #0f172a
- White background: #ffffff
- Light gray background: #f1f5f9 (Why I'm Different section)
- Pure white text on dark: #ffffff
- Pure black text on light: #0f172a

**Layout Patterns:**
- Content max-width: 1020px for text sections
- Card grids: 3-4 columns on desktop, responsive on mobile/tablet
- Consistent padding: py-20 px-6 md:px-20

**Deployment:**
- Built successfully (Next.js build, no errors)
- Deployed to Vercel: https://act-website-fawn.vercel.app
- Primary URL: https://www.christopherhoole.online ✅ (DNS propagated)
- Root URL: https://christopherhoole.online ⏳ (DNS propagating)
- GitHub: https://github.com/ChristopherHoole/act-website
- Git commit: 35 files changed, 3,299 insertions

**Key Technical Decisions:**
1. Single-file artifacts — HTML, CSS, JS all in one .tsx/.jsx file (Next.js components)
2. Three.js colorSpace compatibility — removed `t.colorSpace = THREE.SRGBColorSpace` for r128 compatibility
3. No Bootstrap — pure Tailwind CSS with utility classes
4. Contact form — frontend complete, backend deferred (will connect to A.C.T /api/leads)
5. Removed S8/S9 — cleaner initial launch, may add later
6. Navigation sentence case — more readable than ALL CAPS
7. FAQ accordion — one open at a time, all closed by default for compact initial state
8. Logo integration — A.C.T concentric circles (blue, red, yellow, green center)

**Files Delivered:**
- 12 component files (Hero.tsx, AboutMe.tsx, TheProblem.tsx, TheDifference.tsx, WorkHistory.tsx, Skills.tsx, WhatACTDoes.tsx, WhyDifferent.tsx, FAQ.tsx, ContactForm.tsx, Footer.tsx, Navigation.tsx)
- page.tsx (main page, HowIWork and WeeklyDeliverables removed)
- globals.css (with text-body-dark and text-body-light classes)
- act_logo.svg + favicon.ico (in public folder)
- All files ready for production, mobile responsive

---

## CURRENT STATUS

### Overall: ~99% Complete

What's working:
- **Marketing Website:** Live at https://www.christopherhoole.online, 11 sections, fully responsive
- All 6 dashboard pages with real/synthetic data
- Metrics cards: Financial + Actions on every page
- Performance chart: dual-axis, 4 toggleable metrics, session-persisted, all 6 pages
- Sparklines + change indicators on date-range pages
- Session-based date picker
- M5 card-based Rules tab on Campaigns page
- rules_config.json + rules_api.py CRUD
- M6 Recommendations Engine + global page + Campaigns tab
- M7 Accept/Decline/Modify action buttons — live POST routes
- M7 5-tab Recommendations UI on /recommendations + /campaigns (Pending/Monitoring/Successful/Reverted/Declined)
- M8 Radar background job — auto-resolves monitoring recommendations
- M8 Changes page — My Actions card grid + System Changes table
- M8 Reverted tab on both recommendation pages
- M9 Phase 1 Search Terms tab with negative keyword flagging
- M9 Phase 2 Live execution — negative keyword blocking + keyword expansion (dry-run validated)
- changes audit table in warehouse.duckdb
- Authentication + client switching
- Constitution execution engine
- M4 tables: full Google Ads column sets on all 5 pages
- Server-side sort on all sortable columns

Pending:
- **Website:** Connect contact form to /api/leads endpoint (integrate with A.C.T dashboard)
- **Website:** Optional SEO improvements (meta tags, OpenGraph images, sitemap)
- **Website:** Root domain DNS propagation (https://christopherhoole.online without www)
- M9 Live validation with real Google Ads account
- System Changes tab → card grid (deferred from Chat 29)
- M5 Rules tab rollout to Ad Groups, Keywords, Ads, Shopping
- Campaign scope pill name resolution
- All Conv. pipeline
- Shopping IS/Opt. Score (columns exist but NULL)
- Config YAML validation errors (pre-existing, non-blocking)

---

## FUTURE ROADMAP

Immediate:
- Phase 3: Future-Proofing (unit tests, job queue, DB indexes, CSRF)
- System Changes tab → card grid
- M9 live validation with real Google Ads account

Short-term:
- Email Reports (SMTP)
- Smart Alerts (anomaly detection)
- M5 Rules tab rollout to remaining pages

Medium-term:
- Keywords Enhancement (search terms → keyword suggestions)
- Onboarding Wizard
- Documentation

---

## LESSONS LEARNED

1. Always extend base_bootstrap.html (never base.html)
2. Always use ro.analytics.* prefix for read queries
3. Request current file before editing — never cached
4. Route decorator quote style matters for string replacement
5. Shopping: compute_campaign_metrics() must include total_clicks
6. Session state > URL params for picker/collapse
7. Jinja2 macros: pilot-then-rollout pattern is efficient
8. Mandatory codebase upload saves hours in worker chats
9. Files in routes/ are 3 levels deep from project root — use `.parent.parent.parent`
10. `display:none` + `display:flex` in same inline style — browser uses last one; keep none, let JS add flex
11. Dual-layer architecture: JSON config (UI) and Python functions (execution) must remain separate
12. Campaign picker must be wired to real data before declaring campaign-specific scope complete
13. New /recommendations/cards JSON endpoint pattern — JS rendering of inline cards without page reload
14. recommendations table must live in writable warehouse.duckdb — never in readonly analytics DB
15. Engine proxy columns must be logged when used — do not silently substitute
16. Duplicate prevention: always check (campaign_id, rule_id) before insert
17. Verify actual DB column names before writing routes — brief column names may differ from schema
18. Tab switching approach depends on page: recommendations.html uses server-side Jinja + JS show/hide; campaigns.html uses JS fetch from /cards endpoint
19. Datetime fields from DuckDB can be Python datetime objects or ISO strings — use `| string | truncate(10, True, '')` in Jinja
20. NULL dates on old synthetic rows are expected — document clearly
21. DuckDB Radar connection pattern: open warehouse.duckdb as read-write + ATTACH warehouse_readonly.duckdb as ro. Never open with read_only=True if writes are needed. Never open same file twice with different configs.
22. changes table has no recommendation_id FK — JOIN to recommendations using campaign_id + rule_id + QUALIFY ROW_NUMBER()
23. System Changes tab from ro.analytics.change_log — will be empty in synthetic environment until Autopilot runs live
24. **Marketing Website:** Single-file artifacts work best for Next.js components — all HTML/CSS/JS in one .tsx file
25. **Marketing Website:** Three.js version matters — r128 doesn't support `colorSpace` property, must be removed for compatibility
26. **Marketing Website:** Vercel deployment requires clean Next.js build — test `npm run build` before deploying
27. **Marketing Website:** DNS propagation: CNAME (www) propagates faster than A record (root domain) — expect 5-60 min delay
28. **Marketing Website:** GoDaddy DNS: Remove old A records before adding new ones to avoid conflicts
29. **Marketing Website:** Contact form backend should integrate with A.C.T dashboard /api/leads endpoint for unified lead management
30. **Marketing Website:** Typography consistency matters — standardize all card titles/content at project start (20px titles, 16px content)
31. **Marketing Website:** FAQ accordion: all closed by default = cleaner initial page load, better UX
32. **Search Terms Tab:** Client-side search (filters visible rows only) acceptable for Phase 1 — instant feedback more valuable than cross-page search which requires server round-trip
33. **Negative Keyword Thresholds:** Industry-standard thresholds (10 clicks, £50 cost, 1% CTR, 20 impressions) work well for Phase 1 — can move to rules_config.json for per-client customization in future
34. **Bulk Selection Persistence:** JavaScript array tracking selected IDs across pages provides good UX without session storage complexity
35. **Dry-Run First Architecture:** Check dry_run flag BEFORE loading Google Ads client — enables testing without API credentials, faster response times, production-safe validation
36. **Expansion Criteria Thresholds:** Conservative thresholds (CVR ≥5%, ROAS ≥4.0x, Conv. ≥10) reduce false positives — only flag highest-confidence opportunities (10-15% of search terms)
37. **Sequential vs. Batch Execution:** Sequential execution (one-by-one) acceptable for <10 items — simpler error handling, clear per-item results, sufficient performance. Add batching only if >10 items becomes common use case.
38. **Google Ads Config Path Detection:** Try multiple fallback paths (root, configs/, secrets/) with clear error message — flexible deployment across environments while maintaining security (secrets/ is git-ignored)


---

## KNOWN PITFALLS

| Problem | Fix |
|---------|-----|
| Template CSS missing | Must extend base_bootstrap.html, not base.html |
| DB query fails | Use ro.analytics.* not analytics.* |
| Route replacement fails | Match exact quote style of @bp.route decorator |
| Shopping metrics missing | Add total_clicks to compute_campaign_metrics() |
| Collapse state lost | POST to /set-metrics-collapse |
| Rules showing 0 | Use r'_\d{3}(?:_|$)' regex |
| Ad group table empty | Use cpc_bid_micros not bid_micros |
| Sort not working on full dataset | Must be SQL-side ORDER BY, not Python-side |
| New sort column not working | Must add to ALLOWED_*_SORT whitelist in route |
| Jinja template 500 error | Validate with jinja2 Environment before deploying |
| rules_config.json not found | Path needs `.parent.parent.parent` — routes/ is 3 levels from project root |
| Drawer visible on page load | Remove flex from inline style, let JS add it |
| Campaign picker empty | Fetch from `/api/campaigns-list` on scope card click |
| "budget budget" double word | Use explicit type→label map |
| Blueprint not registered | New blueprints MUST be added to __init__.py |
| Radar "ro catalog does not exist" | Must ATTACH warehouse_readonly.duckdb in radar connection |
| Radar read-write conflict | Never open warehouse.duckdb with read_only=True if writes needed |
| changes JOIN to recommendations | No recommendation_id — use campaign_id + rule_id + QUALIFY |
| **Website:** Three.js colorSpace error | Remove t.colorSpace line for r128 compatibility |
| **Website:** Next.js build fails | Check all imports, remove unused components, validate syntax |
| **Website:** Vercel deployment 404 | Ensure domain DNS configured correctly (A + CNAME records) |
| **Website:** www works but root doesn't | Root domain A record takes longer to propagate (5-60 min) |
| **Search Terms:** Dry-run still loading API | Move dry_run check to FIRST thing after request parsing — before client loading |
| **Search Terms:** google_ads_config_path attribute error | Config doesn't have this attribute — manually detect with 3 fallback paths (root, configs/, secrets/) |
| **Search Terms:** Expansion flags in wrong column | Remove old "Flag" header, update colspan to 17 (was 16) |

---

**Version:** 10.0 | **Last Updated:** 2026-02-24
**Next Step:** Phase 3 Future-Proofing (unit tests, job queue, CSRF) | Website: Connect contact form to A.C.T dashboard
