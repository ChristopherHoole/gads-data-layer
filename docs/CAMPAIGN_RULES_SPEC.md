# CAMPAIGN RULES & FLAGS SPECIFICATION
**Version:** 1.0
**Created:** 2026-03-12
**Master Chat:** 11.0
**Status:** Design phase — pre-build

---

## ARCHITECTURE DECISIONS

### Confirmed Flows

**Rule Flow:**
Campaign Selection → Rule or Flag → Rule Type → Conditions → Action

**Flag Flow:**
Campaign Selection → Rule or Flag → Flag Type → Conditions → (Alert raised, no action)

### Key Architectural Rules

| Rule | Detail |
|------|--------|
| Mixed strategies blocked | Rules cannot be attached to campaigns with different bidding strategies |
| Strategy auto-detected | System detects bidding strategy from campaign data automatically |
| Flag before Pause | No pause recommendation fires without a Flag being raised first |
| Human confirmation | ALL campaign-level actions require human confirmation — no exceptions |
| Keyword automation | Only keyword-level recommendations can be fully automated |
| Strategy lock | First campaign selected locks the rule to that bidding strategy |
| Mixed strategies in Flags | Allowed — flags are read-only, no action taken |

### Campaign Types in Scope
- Target ROAS (tROAS)
- Max Conversion Value
- Target CPA (tCPA)
- Max Clicks

### Rule Types
- Budget
- Bid
- Status

### Flag Types
- Performance
- Anomaly
- Technical

---

## CLIENT SETTINGS — GUARDRAILS

These are set once per client in client settings and apply automatically across all rules.

| Guardrail | Applies To | Description |
|-----------|-----------|-------------|
| Absolute Max CPA | tCPA campaigns | System never raises tCPA target above this |
| Minimum tROAS | tROAS campaigns | System never lowers tROAS target below this |
| Max CPC ceiling | Max Clicks campaigns | System never raises CPC cap above this |
| Min CPC floor | Max Clicks campaigns | System never lowers CPC cap below this |
| Max budget increase per change | All campaigns | System never increases budget more than X% in one change |
| Max budget decrease per change | All campaigns | System never decreases budget more than X% in one change |

---

## UI COMPONENTS

| Component | Purpose |
|-----------|---------|
| Flow Builder | 5-step guided rule/flag creation. Filters options at each step. |
| Rules/Flags Table | View all existing rules and flags grouped by type. Edit and delete inline. |
| Templates | Pre-built common rules/flags. Pre-fills flow builder. Christopher sets thresholds only. |
| Search & Filter | Filter by campaign, type, action, status (enabled/disabled). |

**Three views on Campaign Rules page:**
1. Table view — see all existing rules and flags
2. Template picker — start from a pre-built template
3. Flow builder — build or edit step by step

---

## SYSTEM SIGNALS (BUILT)

| Signal | What it detects | How |
|--------|----------------|-----|
| cost_spike_confidence | Abnormal cost spike | Cost z-score ≥ 2.0 |
| cost_drop_detected | Abnormal cost drop | Cost z-score ≤ -2.0 |
| pace_over_cap_detected | Spending over monthly cap | pacing_flag_over_105 = true |
| ctr_drop_detected | CTR dropped >20% WoW | ctr_w7_vs_prev_pct < -20% |
| cvr_drop_detected | CVR dropped >20% WoW | cvr_w7_vs_prev_pct < -20% |

## SYSTEM SIGNALS (NEEDS BUILDING)

| Signal | What it detects |
|--------|----------------|
| pace_under_cap_detected | Spend tracking under monthly cap |
| click_z_score | Statistical deviation in click volume |
| impression_z_score | Statistical deviation in impression volume |
| conv_tracking_loss_detected | Conversions drop to zero after previously recording |
| Baseline deviation | Current performance vs campaign's own historical average (trend) |

---

## MATRIX 1 — CAMPAIGN BUDGET RULES

| Campaign Type | # | Rule Name | C1 | C1 Type | C2 | C2 Type | C2 Req? | Action | Mag | Guardrail | Plain English |
|---|---|---|---|---|---|---|---|---|---|---|---|
| tROAS / Max Conv Value | 1 | Increase Budget | ROAS (7d/30d) > threshold | Raw | Clicks or Convs ≥ min | Raw | Optional | Increase budget | X% | Max budget increase | If ROAS is strong, increase the budget to capture more volume |
| tROAS / Max Conv Value | 2 | Decrease Budget | ROAS (7d/30d) < threshold | Raw | Clicks or Convs ≥ min | Raw | Optional | Decrease budget | X% | Max budget decrease | If ROAS is poor with enough data, reduce budget to stop waste |
| tROAS / Max Conv Value | 3 | Emergency Budget Cut | cost_spike_confidence | System | — | — | None | Decrease budget | X% | Max budget decrease | If an abnormal cost spike is detected, cut budget immediately |
| tROAS / Max Conv Value | 4 | Pacing Reduction | pace_over_cap_detected | System | — | — | None | Decrease budget | X% | Max budget decrease | If monthly spend is on track to exceed cap, reduce budget now |
| tROAS / Max Conv Value | 5 | Pacing Increase | pace_under_cap_detected | System | ROAS > threshold | Raw | Mandatory | Increase budget | X% | Max budget increase | If spend is tracking under cap and ROAS is good, use the remaining budget |
| tCPA | 6 | Increase Budget | CPA < target | Raw | Convs ≥ min | Raw | Optional | Increase budget | X% | Max budget increase | If cost per lead is below target, increase budget to get more leads |
| tCPA | 7 | Decrease Budget | CPA > target | Raw | Convs ≥ min | Raw | Optional | Decrease budget | X% | Max budget decrease | If cost per lead is too high, reduce budget to control spend |
| tCPA | 8 | Emergency Budget Cut | cost_spike_confidence | System | — | — | None | Decrease budget | X% | Max budget decrease | If an abnormal cost spike is detected, cut budget immediately |
| tCPA | 9 | Pacing Reduction | pace_over_cap_detected | System | — | — | None | Decrease budget | X% | Max budget decrease | If monthly spend is on track to exceed cap, reduce budget now |
| tCPA | 10 | Pacing Increase | pace_under_cap_detected | System | CPA < target | Raw | Mandatory | Increase budget | X% | Max budget increase | If spend is under cap and CPA is good, use the remaining budget |
| Max Clicks | 11 | Increase Budget | Clicks (7d) > threshold | Raw | CPC < threshold | Raw | Optional | Increase budget | X% | Max budget increase | If click volume is strong and CPC is acceptable, increase budget |
| Max Clicks | 12 | Decrease Budget | CPC > threshold | Raw | Clicks (7d) < min | Raw | Optional | Decrease budget | X% | Max budget decrease | If clicks are too expensive and volume is low, reduce budget |
| Max Clicks | 13 | Emergency Budget Cut | cost_spike_confidence | System | — | — | None | Decrease budget | X% | Max budget decrease | If an abnormal cost spike is detected, cut budget immediately |
| Max Clicks | 14 | Pacing Reduction | pace_over_cap_detected | System | — | — | None | Decrease budget | X% | Max budget decrease | If monthly spend is on track to exceed cap, reduce budget now |
| Max Clicks | 15 | Pacing Increase | pace_under_cap_detected | System | CPC < threshold | Raw | Mandatory | Increase budget | X% | Max budget increase | If spend is under cap and CPC is acceptable, use the remaining budget |

---

## MATRIX 2 — CAMPAIGN BID RULES

| Campaign Type | # | Rule Name | C1 | C1 Type | C2 | C2 Type | C2 Req? | Action | Mag | Guardrail | Plain English |
|---|---|---|---|---|---|---|---|---|---|---|---|
| tROAS / Max Conv Value | 1 | Tighten tROAS Target | ROAS (30d) > threshold | Raw | Convs ≥ min | Raw | Mandatory | Increase tROAS target | X% | Min tROAS floor | If ROAS is significantly beating the goal, raise the target to push efficiency further |
| tROAS / Max Conv Value | 2 | Loosen tROAS Target | ROAS (30d) < threshold | Raw | Convs ≥ min | Raw | Mandatory | Decrease tROAS target | X% | Min tROAS floor | If ROAS is missing the goal with enough data, lower the target to recover volume |
| tCPA | 3 | Tighten tCPA Target | CPA > target | Raw | Convs ≥ min | Raw | Mandatory | Decrease tCPA target | X% | — | If cost per lead is too high, lower the CPA target to force Google to bid more carefully |
| tCPA | 4 | Loosen tCPA Target | CPA < target | Raw | Convs ≥ min | Raw | Mandatory | Increase tCPA target | X% | Absolute Max CPA | If cost per lead is well below target, raise the CPA target slightly to scale volume |
| Max Clicks | 5 | Increase Max CPC Cap | CPC hitting cap | Raw | Clicks (7d) < min | Raw | None | Increase CPC cap | X% | Max CPC ceiling | If the CPC cap is limiting click volume, raise it to get more clicks |
| Max Clicks | 6 | Decrease Max CPC Cap | CPC > threshold | Raw | Clicks (7d) ≥ min | Raw | Optional | Decrease CPC cap | X% | Min CPC floor | If clicks are too expensive, lower the CPC cap to control costs |

---

## MATRIX 3 — CAMPAIGN STATUS RULES

Notes:
- All status rules use a 14d window — sustained poor performance required
- All require 2 conditions — performance + data sufficiency
- All require human confirmation before executing — no exceptions
- Flag must be raised before pause recommendation fires

| Campaign Type | # | Rule Name | C1 | C1 Type | C2 | C2 Type | C2 Req? | Window | Action | Guardrail | Plain English |
|---|---|---|---|---|---|---|---|---|---|---|---|
| tROAS / Max Conv Value | 1 | Pause – Poor ROAS | ROAS < 50% of target | Raw | Cost ≥ min spend | Raw | Mandatory | 14d | Pause campaign | Human confirmation required | If ROAS has been well below target for 2 weeks and enough has been spent to be confident, recommend pausing the campaign |
| tCPA | 2 | Pause – High CPA | CPA > 150% of target | Raw | Convs ≥ minimum | Raw | Mandatory | 14d | Pause campaign | Human confirmation required | If cost per lead has been significantly above target for 2 weeks with enough conversions to be sure, recommend pausing the campaign |
| Max Clicks | 3 | Pause – High CPC | CPC > 2x threshold | Raw | Clicks < minimum | Raw | Mandatory | 14d | Pause campaign | Human confirmation required | If clicks are too expensive and volume is too low for 2 weeks, recommend pausing the campaign |

---

## MATRIX 4 — CAMPAIGN FLAGS

### PERFORMANCE FLAGS

| Campaign Type | # | Flag Name | Direction | Condition | C Type | Window | Plain English |
|---|---|---|---|---|---|---|---|
| tROAS / Max Conv Value | 1 | ROAS Drop | Negative | ROAS declined > X% vs baseline | Raw | Trend | If ROAS has been consistently declining vs the campaign's normal performance, raise a flag for review |
| tROAS / Max Conv Value | 2 | ROAS Spike | Positive | ROAS increased > X% vs baseline | Raw | Trend | If ROAS has spiked unusually high vs normal, flag it — could be an opportunity or an anomaly |
| tCPA | 3 | CPA Spike | Negative | CPA increased > X% vs baseline | Raw | Trend | If cost per lead is trending significantly higher than normal, raise a flag |
| tCPA | 4 | CPA Drop | Positive | CPA decreased > X% vs baseline | Raw | Trend | If cost per lead has dropped significantly, flag it as a potential scaling opportunity |
| All | 5 | CTR Drop | Negative | CTR declined > X% vs baseline | Raw | Trend | If click through rate is consistently declining, ads may be losing relevance |
| All | 6 | CTR Spike | Positive | CTR increased > X% vs baseline | Raw | Trend | If click through rate has spiked unusually, flag for review — could indicate a change in auction dynamics |
| All | 7 | CVR Drop | Negative | CVR declined > X% vs baseline | Raw | Trend | If conversion rate is consistently declining, there may be a landing page or offer issue |
| All | 8 | CVR Spike | Positive | CVR increased > X% vs baseline | Raw | Trend | If conversion rate has spiked unusually high, flag as a potential opportunity |
| All | 9 | Conversion Drop | Negative | Convs declined > X% vs baseline | Raw | Trend | If conversion volume is consistently dropping, flag for immediate review |
| All | 10 | Conversion Spike | Positive | Convs increased > X% vs baseline | Raw | Trend | If conversion volume has spiked unusually, flag as a potential scaling opportunity |
| All | 11 | Spend Drop | Negative | Spend declined > X% vs baseline | Raw | Trend | If spend is consistently dropping, the campaign may be losing delivery |
| All | 12 | Spend Spike | Positive | Spend increased > X% vs baseline | Raw | Trend | If spend has spiked unusually, flag immediately to protect budget |
| All | 13 | Impression Share Drop | Negative | IS declined > X% vs baseline | Raw | Trend | If impression share is consistently declining, the campaign is losing auction competitiveness |
| All | 14 | Impression Share Spike | Positive | IS increased > X% vs baseline | Raw | Trend | If impression share has spiked unusually, flag as a potential opportunity to scale |
| All | 15 | Zero Impressions | Negative | Impressions = 0 | Raw | 1d | If the campaign has recorded zero impressions today, something is blocking delivery |
| All | 16 | CPC Spike | Negative | CPC increased > X% vs baseline | Raw | Trend | If cost per click is trending significantly higher, the auction is getting more expensive |

### ANOMALY FLAGS

| Campaign Type | # | Flag Name | Direction | Condition | C Type | Plain English |
|---|---|---|---|---|---|---|
| All | 1 | Cost Spike | Negative | cost_spike_confidence | System | An abnormal cost surge has been detected vs the campaign's recent average — review immediately |
| All | 2 | Cost Drop | Negative | cost_drop_detected | System | An abnormal cost drop has been detected — campaign may have lost delivery |
| All | 3 | Click Volume Spike | Positive | click_z_score > threshold | System | An unusual surge in clicks detected — could indicate click fraud or a major auction change |
| All | 4 | Click Volume Drop | Negative | click_z_score < threshold | System | An unusual drop in clicks detected — something may be blocking campaign delivery |
| All | 5 | Impression Spike | Positive | impression_z_score > threshold | System | An abnormal impression surge detected — flag for review |
| All | 6 | Impression Drop | Negative | impression_z_score < threshold | System | An abnormal impression drop detected — campaign may be losing reach |
| All | 7 | Zero Conversions | Negative | conversions = 0 AND cost > threshold | System | Campaign is spending but recording zero conversions — conversion tracking may be broken |
| All | 8 | Conversion Tracking Loss | Negative | conv_tracking_loss_detected | System | Conversions have suddenly dropped to zero after previously recording — likely a tracking issue |

### TECHNICAL FLAGS

| Campaign Type | # | Flag Name | Condition | C Type | Data Source | Built? | Plain English |
|---|---|---|---|---|---|---|---|
| All | 1 | Landing Page Down | Page returning error | System | URL health check | ❌ No | The campaign landing page is returning an error — ads are sending traffic to a broken page |
| All | 2 | Landing Page Slow | Load time > threshold | System | Page speed API | ❌ No | The landing page is loading too slowly — this will hurt Quality Score and conversion rate |
| All | 3 | Ad Disapproved | One or more ads disapproved | System | Google Ads API | ⚠️ Needs Basic Access | One or more ads in this campaign have been disapproved — delivery may be impacted |
| All | 4 | Budget Exhausted Early | Budget spent before end of day | System | Campaign data | ✅ Yes | The daily budget is being fully spent too early in the day — missing afternoon and evening traffic |
| All | 5 | Billing Issue | Campaign limited by billing | System | Google Ads API | ⚠️ Needs Basic Access | A billing issue has been detected — campaign delivery may be stopped or limited |
| All | 6 | Tracking Tag Missing | Conversion tag not firing | System | Google Ads API | ⚠️ Needs Basic Access | The conversion tracking tag is not firing — conversion data may be incomplete or missing |

---

## NEXT STEPS

- [ ] Wireframe — Campaign Rules page (Table + Flow Builder + Templates)
- [ ] Spec Ad Group rules and flags
- [ ] Spec Keyword rules and flags
- [ ] Spec Ad rules and flags
- [ ] Spec Shopping rules and flags
- [ ] Build pace_under_cap_detected system signal
- [ ] Build baseline deviation system signal
- [ ] Build click_z_score and impression_z_score signals
- [ ] Build conv_tracking_loss_detected signal
- [ ] Add Guardrails section to client settings UI and YAML
- [ ] Update MASTER_KNOWLEDGE_BASE.md with architectural decisions

---

**Version:** 1.0 | **Created:** 2026-03-12 | **Master Chat:** 11.0
