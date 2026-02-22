# CHAT 26 BRIEF — M5 Rules Tab (Campaigns Pilot)

**Version:** 1.0  
**Created:** 2026-02-22  
**Master Chat:** Master Chat 2.0  
**Previous Chat:** Chat 25 — M4 Table Overhaul (commit ed93198)  
**Wireframe Reference:** M5_WIREFRAME_v3.html (approved by Christopher)

---

## 🎯 OBJECTIVE

Build the **Rules tab** for the Campaigns page as a fully working pilot. This is M5 of the Dashboard 3.0 modernisation.

The Rules tab replaces the existing dense table-based rules UI with a clean card-based layout that is readable, configurable, and actionable.

---

## 🚨 MANDATORY FIRST STEPS (DO NOT SKIP)

Before writing a single line of code, you MUST:

1. Request codebase ZIP upload (`C:\Users\User\Desktop\gads-data-layer`)
2. Request `PROJECT_ROADMAP.md` upload (`C:\Users\User\Desktop\gads-data-layer\docs\PROJECT_ROADMAP.md`)
3. Request `CHAT_WORKING_RULES.md` upload (`C:\Users\User\Desktop\gads-data-layer\docs\CHAT_WORKING_RULES.md`)
4. Review codebase, then ask Master Chat **5 diagnostic questions** and wait for answers
5. Write a **detailed build plan** and wait for Master Chat approval
6. Only then begin implementation

---

## 📋 5 DIAGNOSTIC QUESTIONS — WORKER ASKS, MASTER CHAT ANSWERS

After reviewing the codebase ZIP, working rules, and this brief, the worker must formulate exactly **5 diagnostic questions** and post them to **Master Chat**.

**Do NOT proceed with any code until Master Chat has answered all 5 questions.**

The questions must cover the following areas (worker phrases them based on what they find in the codebase):

1. **[DATABASE]** — Where do current rules come from? DuckDB, hardcoded Python, or config file?
2. **[ROUTE]** — What is the campaigns route file and what does the existing Rules tab currently render?
3. **[DATA MODEL]** — What fields do existing rule objects have? Does the model support scope, cooldown, magnitude, enabled/disabled?
4. **[ARCHITECTURE]** — Should rules be stored in DuckDB or a JSON config file? Worker states their recommendation and Master Chat confirms.
5. **[SCOPE]** — Which template file is live for the Campaigns page? Confirm exact filename from `render_template()` call.

**Worker posts questions → Master Chat answers → Worker writes build plan → Master Chat approves → Worker builds.**

---

## 📐 APPROVED DESIGN — M5 WIREFRAME v3

Christopher has approved the card-based layout from `M5_WIREFRAME_v3.html`. The implementation MUST match this design exactly.

### Visual Design Rules
- Each rule is a **card** (not a table row)
- Cards have a **4px coloured top bar**: blue = Budget, green = Bid, red = Status
- Campaign-specific cards have a **blue border** + "Overrides blanket" tag
- Rule naming format: **"Budget 1", "Bid 1", "Status 1"** — NOT "BUDGET-001"
- **Edit** button: pencil SVG icon
- **Delete** button: bin SVG icon (turns red on hover)
- **Toggle switch**: on/off per rule. Disabled rules fade to 45% opacity
- All icons must be **inline SVG** — NO Bootstrap Icons CDN, NO icon font CDN

### Layout Structure
```
Page tabs: Campaigns (20) | Rules (13) | Recommendations [5 pending — placeholder]

Rules tab:
  - Header: "Campaign Optimization Rules" + Add Rule button
  - Summary strip: Budget count | Bid count | Status count | Active/Total
  - Filter bar: All | Budget | Bid | Status | Blanket only | Campaign-specific only | Active only
  - Section: Budget Rules (n)
      → Card grid (auto-fill, min 340px)
  - Section: Bid Rules (n)
      → Card grid
  - Section: Status Rules (n)
      → Card grid
```

### Rule Card Structure (per card)
```
[4px coloured top bar]
[Body]
  Rule type + number ("Budget 1") — coloured label
  Rule name (bold, full — no truncation)
  Toggle switch (top right)

  Condition block (grey background):
    "When all of these are true:"
    IF [metric] [operator] [value] [unit]
    AND [metric] [operator] [value]

  Action block (coloured gradient):
    Icon + "Increase/Decrease daily budget by X%"
    Sub-text: cooldown note or Constitution cap note

[Footer]
  Scope pill (🌐 All campaigns OR 🎯 Campaign name)
  Risk badge (Low / Medium / High / Unknown)
  Override tag (only on campaign-specific cards)
  Edit button (pencil icon) | Delete button (bin icon)
```

### Add/Edit Rule — Slide-in Drawer
Opens from right side. 5 steps with numbered circle headers:

1. **Rule Type** — dropdown: Budget / Bid / Status
2. **Scope** — two cards: All Campaigns (🌐) vs Campaign-Specific (🎯). If specific, show campaign dropdown.
3. **Condition** — two condition rows (metric / operator / value / unit). Extensible.
4. **Action** — Direction dropdown (Increase / Decrease / Hold / Flag for review) + Magnitude % input (1–20, capped)
5. **Settings** — Rule name text input + Cooldown dropdown (7 / 14 / 30 days)

Live rule preview at bottom of drawer showing IF/THEN/SCOPE/COOLDOWN in plain English.

**Priority callout** in Scope section: "Campaign-specific rules always override blanket rules on the same campaign."

---

## 🔒 WHAT IS CHANGEABLE AT CAMPAIGN LEVEL

Rules may only trigger actions for fields that the system can actually change. At campaign level:

| Action type | What changes |
|---|---|
| Budget | Daily budget (increase or decrease by %) |
| Bid | Target ROAS or Target CPA (increase or decrease by %) |
| Status | Pause / Enable / Flag for human review |

**No other fields.** Do not create rules for anything else at this level.

---

## ⚙️ RULE DATA MODEL

Each rule must store these fields:

| Field | Type | Notes |
|---|---|---|
| rule_id | string | Auto-generated, e.g. "budget_1" |
| rule_type | string | "budget" / "bid" / "status" |
| rule_number | int | Sequential per type: 1, 2, 3... |
| display_name | string | "Budget 1", "Bid 1", etc. |
| name | string | User-defined name |
| scope | string | "blanket" / "specific" |
| campaign_id | string / null | Only if scope = "specific" |
| condition_metric | string | e.g. "roas_30d" |
| condition_operator | string | "gt" / "lt" / "gte" / "lte" |
| condition_value | float | Threshold value |
| condition_unit | string | "x_target" / "absolute" |
| condition_2_* | same as above | Second condition (optional) |
| action_direction | string | "increase" / "decrease" / "hold" / "flag" |
| action_magnitude | float | Percentage (1–20) |
| risk_level | string | "low" / "medium" / "high" / "unknown" |
| cooldown_days | int | 7 / 14 / 30 |
| enabled | bool | True / False |
| created_at | datetime | Auto |
| updated_at | datetime | Auto |

---

## 🗃️ DATA STORAGE RECOMMENDATION

Rules should be stored in a **JSON file** (`rules_config.json`) rather than DuckDB. Reason: rules are configuration, not analytics data. JSON is simpler to read/write/version-control.

Suggested location: `C:\Users\User\Desktop\gads-data-layer\act_autopilot\rules_config.json`

Worker must verify whether existing rules are already stored somewhere and migrate if needed. Do NOT duplicate.

---

## 📁 FILES EXPECTED TO BE MODIFIED

Worker must request current versions of ALL files before editing:

| File | Path |
|---|---|
| Campaigns route | `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\campaigns.py` |
| Campaigns template | Confirm from render_template() call — request current file |
| Rules config | `C:\Users\User\Desktop\gads-data-layer\act_autopilot\rules_config.json` (may need creating) |
| Base template | `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\base_bootstrap.html` |

Worker may also need to create:
- A new API endpoint for: add rule / edit rule / toggle rule / delete rule
- A rules helper module if logic is complex

---

## 🏗️ BUILD PLAN STRUCTURE (Worker must produce this)

Worker must present a build plan with these stages before any code:

**Stage A — Diagnostic (pre-code)**
- Answer all 5 questions
- Map existing rules data
- Confirm template filenames
- Present to Master Chat for approval

**Stage B — Data Layer**
- Create or migrate `rules_config.json` with existing rules in new data model
- Write Python helper to load/save/validate rules
- Test read/write works

**Stage C — Backend Routes**
- Add routes to `campaigns.py` for:
  - `GET /campaigns/rules` — load and return rules
  - `POST /api/rules/add` — add rule
  - `PUT /api/rules/<id>/update` — edit rule
  - `PUT /api/rules/<id>/toggle` — enable/disable
  - `DELETE /api/rules/<id>` — delete rule

**Stage D — Frontend (Template)**
- Add Rules tab to campaigns template (matching wireframe v3 exactly)
- Card grid layout per section
- Slide-in drawer with 5-step form
- Filter bar (client-side JS filtering)
- Toggle handlers
- Edit/Delete handlers

**Stage E — Testing**
- Load Rules tab: verify cards render with correct data
- Add a new rule via drawer: verify it saves and appears
- Toggle a rule off: verify card fades and state persists
- Edit a rule: verify changes save
- Delete a rule: verify it disappears
- Filter bar: verify Budget/Bid/Status filters work
- Blanket/Specific filter: verify it works

**Stage F — Handoff**
- Create `CHAT_26_HANDOFF.md`
- Create `CHAT_26_DETAILED_SUMMARY.md`
- Git commit with correct message format

---

## 🚫 RECOMMENDATIONS TAB — PLACEHOLDER ONLY

The Recommendations tab must appear as a third tab alongside Campaigns and Rules, but must show a placeholder message only:

```
💡 Recommendations — Chat 27 scope
Auto-generated daily from rules engine. Accept / Decline / Modify actions.
```

Do NOT build any recommendations functionality in this chat.

---

## ✅ CONSTITUTION GUARDRAILS (display only — not enforced in this chat)

The UI must display Constitution constraints as informational notes:
- Max change magnitude: ±20% (shown as hint in drawer)
- Cooldown period: selectable 7/14/30 days (shown in drawer and on card)
- Risk level: shown on each card as badge

Actual enforcement happens in the execution engine (already built). This chat is UI only.

---

## 📏 TECHNICAL CONSTRAINTS

- Template must extend `base_bootstrap.html` (NOT `base.html`)
- Bootstrap 5 components only
- NO jQuery — vanilla JavaScript only
- NO Bootstrap Icons CDN — use inline SVG for all icons
- Database queries use `ro.analytics.*` prefix (read-only)
- Full Windows paths in all file references
- Complete files only — no code snippets

---

## ✅ SUCCESS CRITERIA

Chat 26 is complete when:

| Test | Expected result |
|---|---|
| Rules tab loads | Cards visible, correct data, correct colours |
| Budget / Bid / Status sections | All render with correct card count |
| Add Rule drawer | Opens, all 5 steps visible, icons working |
| Add Rule — save | New rule appears as card |
| Toggle off | Card fades, state persists on reload |
| Edit rule | Drawer pre-fills with existing values, saves correctly |
| Delete rule | Card removed, no errors |
| Filter bar | Filters cards correctly client-side |
| Recommendations tab | Shows placeholder only |
| No console errors | Clean browser console |

---

## 📝 HANDOFF REQUIREMENTS

At end of chat, worker must produce:

1. `CHAT_26_HANDOFF.md` — git commit command, current state, what Chat 27 needs to know
2. `CHAT_26_DETAILED_SUMMARY.md` — what was built, decisions made, lessons learned

Both must be uploaded to Master Chat before git commit.

---

## 🔗 KEY REFERENCES

- Approved wireframe: `M5_WIREFRAME_v3.html` (available in Master Chat outputs)
- Previous chat handoff: `docs/CHAT_25_HANDOFF.md`
- Master knowledge base: `docs/MASTER_KNOWLEDGE_BASE.md`
- Working rules: `docs/CHAT_WORKING_RULES.md`
- Last commit: `ed93198` — docs update post Chat 25

---

**END OF CHAT 26 BRIEF**
