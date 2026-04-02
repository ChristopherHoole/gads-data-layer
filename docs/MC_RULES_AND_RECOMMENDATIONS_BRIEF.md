# MC Rules & Recommendations — Master Brief
**Session:** MC Rules & Recommendations
**Date:** 2026-03-23
**Objective:** Complete all Rules, Flags, Recommendations, and Radar work before transitioning to live API data.

---

## CRITICAL: BROWSER VERIFICATION REQUIRED

Every change made during this session MUST be visually verified in the browser before moving on. Do not batch up changes and check later. After each task:
- Run the Flask app and open the relevant page
- Visually confirm the UI renders correctly
- Test all interactions (click, open, close, submit, cancel)
- Check the browser console for JavaScript errors
- Confirm no regressions on other pages/tabs

If something looks wrong, fix it immediately before proceeding.

---

## CRITICAL: ONE TASK AT A TIME

Complete each task fully and get confirmation before starting the next. Do NOT work on multiple tasks simultaneously. Do NOT skip ahead. The task numbers are the execution order.

---

## TASK 1: Build Reusable Slide-In Panel Component
Build a single reusable slide-in panel component that animates in from the right side of the screen. This will replace all popup modals for rule/flag create and edit across the entire app. Must support: open, close, overlay click-to-close, cancel button, and hosting the existing flow builder form content inside it.
**Browser-verify:** The component renders, opens, closes, and animates correctly in isolation.

---

## TASK 2: Migrate Campaigns Rules/Flags to Slide-In
Replace all popup modals for creating and editing rules and flags on the Campaigns page with the new slide-in panel. All existing form fields, validation, save, cancel, and delete behaviour must carry over exactly. Remove the old modal code.
**Browser-verify:** Open Campaigns page > Rules tab. Create a rule, edit a rule, cancel, save, delete. Check flags create/edit. Zero console errors.

---

## TASK 3: Migrate Ad Groups Rules/Flags to Slide-In
Same as Task 2 but for the Ad Groups page. Replace all rule/flag modals with the slide-in panel. Remove old modal code.
**Browser-verify:** Open Ad Groups page > Rules tab. Create, edit, save, cancel, delete. Zero console errors.

---

## TASK 4: Migrate Keywords Rules/Flags to Slide-In
Same as Task 2 but for the Keywords page. Replace all rule/flag modals with the slide-in panel. Remove old modal code.
**Browser-verify:** Open Keywords page > Rules tab. Create, edit, save, cancel, delete. Zero console errors.

---

## TASK 5: Migrate Ads Rules/Flags to Slide-In
Same as Task 2 but for the Ads page. Replace all rule/flag modals with the slide-in panel. Remove old modal code.
**Browser-verify:** Open Ads page > Rules tab. Create, edit, save, cancel, delete. Zero console errors.

---

## TASK 6: Migrate Shopping Campaigns Rules/Flags to Slide-In
Same as Task 2 but for the Shopping page — Campaign rules/flags specifically. Replace all rule/flag modals with the slide-in panel. Remove old modal code.
**Browser-verify:** Open Shopping page > Rules tab > Campaign toggle. Create, edit, save, cancel, delete. Zero console errors.

---

## TASK 7: Migrate Shopping Products Rules/Flags to Slide-In
Same as Task 2 but for the Shopping page — Product rules/flags specifically. Replace all rule/flag modals with the slide-in panel. Remove old modal code.
**Browser-verify:** Open Shopping page > Rules tab > Product toggle. Create, edit, save, cancel, delete. Zero console errors.

---

## TASK 8: Ad Groups Recommendations Rollout
The recommendations engine works end-to-end on Campaigns (generate from rules, accept, decline, monitoring, cooldowns, changes audit). Wire this up for Ad Groups. Add the Recommendations tab if not present. Ensure accept/decline/monitoring/cooldowns/audit all work.
**Browser-verify:** Open Ad Groups page > Recommendations tab. Generate recommendations, accept one, decline one, check monitoring state, check changes audit.

---

## TASK 9: Keywords Recommendations Rollout
Same as Task 8 but for Keywords. Wire the keywords rules into the recommendations engine. Add Recommendations tab. Full accept/decline/monitoring/cooldowns/audit.
**Browser-verify:** Open Keywords page > Recommendations tab. Generate, accept, decline, monitor, check audit.

---

## TASK 10: Ads Recommendations Rollout
Same as Task 8 but for Ads. Wire the ads rules into the recommendations engine. Add Recommendations tab. Full accept/decline/monitoring/cooldowns/audit.
**Browser-verify:** Open Ads page > Recommendations tab. Generate, accept, decline, monitor, check audit.

---

## TASK 11: Shopping Campaigns Recommendations Rollout
Same as Task 8 but for Shopping Campaigns. Wire the shopping campaign rules into the recommendations engine. Add Recommendations tab. Full accept/decline/monitoring/cooldowns/audit.
**Browser-verify:** Open Shopping page > Recommendations tab (campaign view). Generate, accept, decline, monitor, check audit.

---

## TASK 12: Shopping Products Recommendations Rollout
Same as Task 8 but for Shopping Products. Wire the shopping product rules into the recommendations engine. Add Recommendations tab. Full accept/decline/monitoring/cooldowns/audit.
**Browser-verify:** Open Shopping page > Recommendations tab (product view). Generate, accept, decline, monitor, check audit.

---

## TASK 13: Fix Trigger Summary Label (Rule 19)
Rule 19 (Loosen tCPA Target) shows "ROAS" label instead of "CPA" in the trigger summary. Fix the label mapping in recommendations.py.
**Browser-verify:** Generate a recommendation from rule 19 and confirm the trigger summary shows CPA.

---

## TASK 14: Fix Any Bugs Found During Tasks 1-12
Fix all bugs discovered during the slide-in migration and recommendations rollout work. Do not leave any broken functionality behind.
**Browser-verify:** Re-check all pages touched during this session.

---

## TASK 15: Radar — Monitor Performance After Acceptance
Build the monitoring system that tracks metric performance after a recommendation is accepted. Define what metrics to track, how often, and for how long (based on the rule's monitoring_days).
**Browser-verify:** Accept a recommendation, confirm it enters monitoring state with tracked metrics.

---

## TASK 16: Radar — Auto-Rollback on Performance Degradation
Build the detection logic that identifies when monitored metrics have degraded beyond a defined threshold, and automatically reverts the accepted action.
**Browser-verify:** Simulate degradation and confirm rollback triggers correctly.

---

## TASK 17: Radar — Cooldown Reset on Rollback
When a rollback is triggered, reset the rule's cooldown so it doesn't immediately re-fire the same recommendation.
**Browser-verify:** After rollback, confirm the rule respects the reset cooldown period.

---

## TASK 18: Radar — User Alert on Rollback
Notify the user when an auto-rollback occurs. In-app notification (toast/banner) on next page load.
**Browser-verify:** Trigger a rollback, reload the dashboard, confirm the alert appears.

---

## TASK 19: Radar — Rollback Audit Trail
Log all rollback events in the changes table with full context (what was rolled back, why, when, which rule).
**Browser-verify:** Trigger a rollback, check the Changes page for the rollback entry.

---

## TASK 20: Radar — Monitoring UI
Build a UI section showing all currently monitored items, their status (healthy/degrading/rolled-back), time remaining, and metrics being tracked.
**Browser-verify:** Open the Radar UI, confirm it shows monitored items with correct statuses.

---

## TASK 21: Rules Strategic Review
Review all 75 rules across all 6 entities. For each rule check: are thresholds realistic for real Google Ads data? Are cooldowns appropriate? Are conditions using correct metrics? Are risk levels accurate? Is the plain English clear? Make any adjustments in the database. Document rules that need real-data validation.
**Browser-verify:** After any rule changes, confirm they render correctly on their entity page.

---

## SESSION SUMMARY

| # | Task | Category |
|---|------|----------|
| 1 | Build reusable slide-in panel component | Slide-In |
| 2 | Migrate Campaigns to slide-in | Slide-In |
| 3 | Migrate Ad Groups to slide-in | Slide-In |
| 4 | Migrate Keywords to slide-in | Slide-In |
| 5 | Migrate Ads to slide-in | Slide-In |
| 6 | Migrate Shopping Campaigns to slide-in | Slide-In |
| 7 | Migrate Shopping Products to slide-in | Slide-In |
| 8 | Ad Groups recommendations rollout | Recommendations |
| 9 | Keywords recommendations rollout | Recommendations |
| 10 | Ads recommendations rollout | Recommendations |
| 11 | Shopping Campaigns recommendations rollout | Recommendations |
| 12 | Shopping Products recommendations rollout | Recommendations |
| 13 | Fix trigger summary label (rule 19) | Bug Fix |
| 14 | Fix any bugs found during tasks 1-12 | Bug Fix |
| 15 | Radar — monitor performance after acceptance | Radar |
| 16 | Radar — auto-rollback on degradation | Radar |
| 17 | Radar — cooldown reset on rollback | Radar |
| 18 | Radar — user alert on rollback | Radar |
| 19 | Radar — rollback audit trail | Radar |
| 20 | Radar — monitoring UI | Radar |
| 21 | Rules strategic review | Review |

**TOTAL: 21 tasks, executed in order, one at a time.**

---

**END OF BRIEF**
