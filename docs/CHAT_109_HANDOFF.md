# CHAT 109: HANDOFF — Ads Rules & Flags Complete

**Date:** 2026-03-21
**Status:** Complete
**Next:** Chat 110 — Shopping Rules & Flags (Brief 5, final entity)

---

## All Entities Complete So Far

| Entity | Chat | Rules | Flags | Total |
|--------|------|-------|-------|-------|
| Campaigns | 91-101 | 18+ | 30 | 51 |
| Ad Groups | 107 | 12 | 18 | 30 |
| Keywords | 108 | 12 | 20 | 32 |
| Ads | 109 | 8 | 15 | 23 |

## Remaining

| Entity | Chat | Status |
|--------|------|--------|
| Shopping | 110 | Final entity |

## Notes for Shopping (Chat 110)

- Shopping uses `entity_type='shopping'`
- Prefix: `sh` for JS/CSS
- Shopping has Bid + Status rules (like Ad Groups)
- Shopping-specific metrics: product feed, product coverage, product disapprovals
- Follow same pattern; add `getCSRFToken` fallback in flow builder

## Additional Bug Fixed in Chat 109

**getCSRFToken not defined**: The ads page's `extra_js` block script wasn't making `getCSRFToken` available to the flow builder component. Fixed by adding a fallback definition at the top of the flow builder's `<script>` tag. This pattern should be applied to Shopping as well.

---

**Ready for Brief 5 (Shopping implementation).**
