# CHAT 109: Ads Rules & Flags — Summary

**Date:** 2026-03-21
**Status:** Complete
**Entity:** Ads (entity_type='ad')

---

## What Was Built

Complete Rules & Flags for Ads. Key difference: Ads have ONLY Status rules (no Bid), so Step 3 shows only 1 type card.

## Files Created

| File | Purpose |
|------|---------|
| `templates/components/ad_rules_flags_tab.html` | Rules/Flags/Templates sub-tabs (Status only) |
| `templates/components/ad_rules_flow_builder.html` | 5-step flow builder (Status actions only) |
| `scripts/seed_ad_rules.py` | Seeds 8 rules + 15 flags |

## Files Modified

| File | Changes |
|------|---------|
| `templates/ads_new.html` | Added rules.css, replaced Rules tab, included flow builder |
| `routes/ads.py` | Added rfb_ads context, 6 CRUD routes |
| `static/css/rules.css` | Added `#adR-rules-flow-overlay` and `#adR-rules-toast-wrap` |
| `app.py` | Added CSRF exemptions for 6 ads rules routes |

## Database

- **23 rows**: 8 Status rules + 7 Performance + 4 Anomaly + 4 Technical flags
- Ad-specific: ad_strength (POOR/AVERAGE/GOOD/EXCELLENT), ad_status, creative fatigue detection

## Additional Fix

- Added `getCSRFToken` fallback in flow builder to handle script load order issue on the ads page

## Verification

| Test | Result |
|------|--------|
| Badge | 23 |
| Rules | 8 (Status only — 1 group) |
| Flags | 15 (Performance 7, Anomaly 4, Technical 4) |
| Step 3 type cards | Only "Status" (no Bid) |
| Create/Delete | Works, badge updates correctly |
| Modal | Fixed, centered popup |
| Console errors | 0 |
