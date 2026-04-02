# Chat 113 — Slide-In Panel Migration Summary

## Overview
Migrated all 6 entity rule builders from a 5-step wizard modal to a long-scroll slide-in panel with a live summary sidebar. This is a UX overhaul that makes rule creation faster, more visible, and easier to review.

## What Changed

### Before (5-Step Wizard Modal)
- Centered 800px modal overlay
- 5 separate steps with Next/Back navigation
- Progress bar with circles (1-2-3-4-5)
- "Your choices" sidebar that only updated on step change
- Step 5 was a summary page — user had to click through 4 steps before seeing the full picture
- Large Rule/Flag and Type cards taking excess vertical space

### After (Long-Scroll Slide-In)
- 720px slide-in panel from the right edge
- All 5 sections visible in one scrollable view
- No step navigation — fill in top to bottom, save at bottom
- Live summary sidebar updates in real-time as you type/select
- Natural language sentence builds as you configure the rule
- Compact card layouts (icon + title on one line, description below)
- 2-row condition layout (metric + operator / value + reference)
- Sticky save footer always visible
- Close via X button, overlay click, or Escape key

## Files Modified

| File | Change |
|------|--------|
| `rules_flow_builder.html` | Campaigns — full rewrite to slide-in |
| `ag_rules_flow_builder.html` | Ad Groups — full rewrite to slide-in |
| `kw_rules_flow_builder.html` | Keywords — full rewrite to slide-in |
| `ad_rules_flow_builder.html` | Ads — full rewrite to slide-in |
| `shopping_campaign_rules_flow_builder.html` | Shopping Campaigns — partial rewrite (rules tab preserved) |
| `product_rules_flow_builder.html` | Shopping Products — partial rewrite (rules tab preserved) |
| `rules.css` | Removed all legacy centered-modal CSS, slide-in styles already existed |
| `wireframes/slide-in-panel.html` | Standalone wireframe prototype for design validation |

## Entity-Specific Notes

| Entity | Types (Rules) | Types (Flags) | Unique Features |
|--------|--------------|---------------|-----------------|
| Campaigns | Budget, Bid, Status | Performance, Anomaly, Technical | Strategy lock, campaign type badges |
| Ad Groups | Bid, Status | Performance, Anomaly, Technical | Impression share metrics |
| Keywords | Bid, Status | Performance, Anomaly, Technical | Quality Score metrics, bidding metrics |
| Ads | Status only | Performance, Anomaly, Technical | No magnitude (pause/enable only) |
| Shopping Campaigns | Budget, Bid, Status | Performance, Anomaly, Technical | Feed errors, out-of-stock metrics |
| Shopping Products | Feed Quality, Performance, Lifecycle, Stock | Same 4 types | Product-specific metrics (stock out, price mismatch, days live) |

## Architecture

All 6 flow builders follow the same pattern:
1. **HTML**: `flow-slide-overlay` > `flow-slide-panel` > header + body-wrap (form + sidebar) + footer
2. **CSS**: Shared classes in `rules.css` (`.rfb-section`, `.rfb-compact-card`, `.rfb-summary-card`, `.rfb-live-sentence`)
3. **JS**: Entity-prefixed functions (`rfb`, `agRfb`, `kwRfb`, `adRRfb`, `shCamRfb`, `prdRfb`) with identical structure

Key JS functions per entity:
- `[prefix]OpenRulesFlow(existingRow)` — open slide-in, populate if editing
- `[prefix]CloseRulesFlow()` — close slide-in
- `[prefix]RfbLiveSummary()` — update sidebar in real-time
- `[prefix]RfbSave()` — validate and POST/PUT to API
- `[prefix]RfbAutoRisk()` — calculate risk level from type + magnitude
- `[prefix]RfbAutoName()` — generate default name from action + metric

## Design Process
1. Created standalone wireframe (`wireframes/slide-in-panel.html`) matching live dashboard design
2. Iterated on wireframe based on visual comparison with live dashboard
3. Implemented long-scroll design on Campaigns first
4. Tested and confirmed by user
5. Rolled out to remaining 5 entities one at a time, testing each

## Commit
`d95697f` — Chat 113: Migrate all 6 rule builders from 5-step modal to long-scroll slide-in with live summary
