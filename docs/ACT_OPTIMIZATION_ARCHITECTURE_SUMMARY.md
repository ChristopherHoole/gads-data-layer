# ACT Optimization Architecture — Project Summary

## Status: COMPLETE (v52)

## What Was Built

A comprehensive Google Ads optimization architecture document that replaces the original 75 rules and 99 flags with a structured, hierarchical decision engine across 6 levels.

## File Locations

- **Architecture Document (latest):** `docs/ACT_OPTIMIZATION_ARCHITECTURE_v52.html`
- **Standards Document:** `docs/ACT_ARCHITECTURE_STANDARDS.md`
- **This Summary:** `docs/ACT_OPTIMIZATION_ARCHITECTURE_SUMMARY.md`
- **All Versions:** `docs/ACT_OPTIMIZATION_ARCHITECTURE_v1.html` through `v52.html` (never overwritten)

## Pages Built (8 total)

### 1. Home Page
- ACT branding and elevator pitch
- The Problem / The Solution sections
- 6-Level Hierarchy visual (clickable navigation)
- 4 Action Categories (Act/Monitor/Investigate/Alert)
- Client Personas (Lead Gen / Ecommerce)
- How It Works (overnight execution flow)
- Navigation cards to all pages

### 2. Account Level — Budget Allocation & Health
- 2 client personas (Lead Gen CPA, Ecommerce ROAS)
- Target ranges with 3 zones (Outperforming/On Target/Underperforming)
- 5 campaign roles (BD, CP, RT, PR, TS) with naming conventions
- Budget allocation bands (min/max % per role, editable per client)
- Within-role budget competition (1/2/3+ campaign rules)
- Signal decomposition (CPC + CVR for Lead Gen, CPC + CVR + AOV for Ecommerce)
- Signal detection windows (CPC 7d, CVR 14d, AOV 30d)
- Performance scoring (7d 50%, 14d 30%, 30d 20% weighted blend)
- Budget shift cooldown: 72 hours per campaign
- Max overnight move: 10% of daily budget

### 3. Campaign Level — Optimization Within Each Campaign
- 5 Universal Levers: Negative Keywords, Device, Geo, Ad Schedule, Match Types
- 7 Strategy-Specific Levers: Manual CPC (universal levers only — keyword bids at Keyword Level), tCPA, tROAS, Maximize Conversions, Max Clicks (with/without cap), PMax, Standard Shopping
- 12 Mermaid flowcharts + 12 Detailed Reference decision trees
- Counter-intuitive tCPA/tROAS explanations (loosening = approval, tightening = auto)
- Modifier caps: Device -60%/+30%, Geo -50%/+30%, Schedule -50%/+25%
- Cooldowns: Device 7d, Geo 30d, Schedule 30d, tCPA/tROAS 14d, Max CPC cap 7d
- 14 guardrails

### 4. Ad Group Level — Outlier Detection & Structural Health
- 4 independent checks (run in parallel):
  1. Negative Performance Outliers (30% spend, 50%+ worse, structural health)
  2. Positive Performance Outliers (40%+ better → promote to standalone campaign)
  3. Budget Concentration Alerts (1/2/3+ active ad group context checks)
  4. Pause Recommendations (21+ days zero, 30+ days inactive, 30+ days despite optimizations)
- Monitoring/flagging only — no auto-execution at this level
- All flags require approval

### 5. Keyword Level — Performance, Bids, Search Terms & Quality
- 7 independent checks + Manual CPC bid management:
  1. Keyword Performance Monitoring (auto-pause at 1x target 0 conv 14d+)
  2. Search Term Mining — Negatives (auto-add [exact] match to 9-list structure)
  3. Search Term Mining — Keyword Discovery (add as phrase match, approval)
  4. Quality Score Monitoring (weekly scan, flag below 4)
  5. Keyword Status Monitoring (below first page bid, rarely shown)
  6. Keyword Conflicts & Cannibalisation (same ad group diff match = OK, diff ad groups/campaigns = flag)
  7. Keyword Pause Recommendations (dead 60d+, zero-converting 1x target 14d+)
- 9 standardised negative keyword lists (organised by word count + match type)
- ACT only adds [exact] match negatives; phrase match is human-managed
- Keyword bids: 10%/cycle, 72hr cooldown, 30% 7-day cap (Manual CPC only)
- 10 guardrails

### 6. Ad Level — Creative Performance & Health
- 6 independent checks:
  1. Ad Strength Monitoring (flag below "Good")
  2. RSA Asset Performance (flag "Low" rated 30+ days)
  3. Ad Count per Ad Group (minimum 3 live ads)
  4. Ad Performance Comparison (30%+ worse, 21d+ live, 100+ impressions, skip under 14d)
  5. Ad Disapprovals (daily scan, flag immediately)
  6. Ad Extensions Monitoring (sitelinks 4+, callouts 4+, snippets 1+, call if tracking)
- All approval-based — ACT cannot write ad copy or create extensions
- Weekly scan (editable), except disapprovals which are daily
- 8 guardrails

### 7. Shopping Level — Product Performance, Search Terms & Exclusions
- Standard Shopping ONLY — no PMax
- 4 independent checks:
  1. Shopping Search Term Mining (same 9-list negative keyword structure)
  2. Product Performance Tiers (best sellers top 20%, mid-range, underperformers, losers)
  3. Product Exclusion Recommendations (zero converters + low ROAS, all approval)
  4. Best Seller Budget Maximisation (raise bids, check IS lost to budget)
- Multi-window weighted blend (7d 50%, 14d 30%, 30d 20%) for tier evaluation
- Product group bids: 10%/cycle, 72hr cooldown, 30% 7-day cap
- Configurable spend threshold (default £50)
- Tier percentages editable per client
- 8 guardrails

### 8. Client Configuration
- 7 sections organised by level:
  1. Account-Level Settings (8 settings)
  2. Campaign-Level Settings (13 settings + modifier caps table)
  3. Keyword-Level Settings (6 settings)
  4. Ad Group-Level Settings (4 settings)
  5. Ad-Level Settings (6 settings)
  6. Shopping-Level Settings (4 settings)
  7. Client Onboarding Checklist (auto-creation of 9 negative keyword lists, campaign role detection, default settings)
- 40+ configurable settings per client

## Key Design Decisions

1. **Two personas:** Lead Gen (CPA) and Ecommerce (ROAS) — determines all optimization logic
2. **Budget allocation is Account Level only** — Campaign Level pulls levers within campaigns
3. **Keyword bids are at Keyword Level** — not Campaign Level (even for Manual CPC)
4. **Product exclusions are at Shopping Level** — not Campaign Level
5. **Loosening always requires approval, tightening auto-executes** — universal principle
6. **4 action categories:** Act (green), Monitor (blue), Investigate (amber), Alert (red)
7. **Every section is self-contained** — no cross-references between sections
8. **9 standardised negative keyword lists** per client — ACT adds [exact] only, phrase is human-managed
9. **Overnight execution with morning review** — ACT acts overnight, human reviews in morning
10. **All thresholds editable per client** via Client Configuration tab

## Technical Features

- Light/dark theme with animated sun/moon toggle
- Mermaid.js flowcharts with deferred rendering (data-mermaid approach for hidden tabs)
- Collapsible sections with expand/collapse all
- ACT logo branding throughout
- Responsive design
- 52 versioned iterations (never overwritten)

## Audit Status

All 8 pages have been deep audited for:
- Content accuracy and completeness
- Naming consistency (Core Logic / Mermaid / Detailed Reference)
- Table standards (5 columns, monitor rows, explicit responses)
- Colour coding consistency (Act/Monitor/Investigate/Alert)
- Cross-reference violations (none found)
- Guardrail completeness
- Footer presence on all pages
