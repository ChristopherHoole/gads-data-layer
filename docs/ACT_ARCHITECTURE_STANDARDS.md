# ACT Optimization Architecture — Standards Document

This document defines the standards for all pages in the ACT Optimization Architecture HTML document. Every page (Account Level, Campaign Level, Ad Group Level, Keyword Level, Ad Level, Shopping) must follow these standards exactly.

This is a working reference document — not client-facing. It exists to ensure consistency across all pages and to speed up the design of new levels.

---

## 1. Page Structure — Required Section Order

Every level page must follow this section order. Not every section will be relevant to every level, but if a section exists it must be in this position relative to the others.

| Position | Section | Required? | Notes |
|----------|---------|-----------|-------|
| 1 | Overview / Setup | Yes | What this level does, what gets configured, how it connects to the level above, and how it receives input from the level above |
| 2 | Actions & Monitoring | Yes | 4 colour cards (Act/Monitor/Investigate/Alert) with level-specific examples + Overnight Execution flow with cooldown callout |
| 3 | Core Logic | Yes | The main content — rules, signals, levers, tables. Multiple sections allowed here. Each section must have an explicit intro paragraph. |
| 4 | Decision Trees — Mermaid Flowcharts | Yes | Visual flowcharts using Mermaid.js. Displayed in persona-grid (2-column layout). |
| 5 | Decision Trees — Detailed Reference | Yes | Card-based step-by-step trees with explicit detail. Displayed in persona-grid (2-column layout). |
| 6 | Cooldown Summary | Yes | Reference table of all cooldowns for this level. Even if only one cooldown exists, include the section for consistency. |
| 7 | Guardrails & Safety Limits | Yes | Hard limits ACT cannot breach — always the last section on every page |

### Level Hierarchy
Each level receives input from the level above and passes output to the level below:
- **Account Level** → diagnoses account health, allocates budget between campaigns
- **Campaign Level** → receives budget allocation, pulls levers within each campaign based on bid strategy
- **Ad Group Level** → receives campaign context, manages ad group structure and performance
- **Keyword Level** → receives ad group context, manages individual keyword performance
- **Ad Level** → receives ad group context, manages ad creative performance
- **Shopping** → dedicated page for Shopping-specific concerns (feed quality, product segmentation)

---

## 2. Section Format

Every collapsible section must contain:

### Section Header
```html
<div class="section open" data-section>
    <div class="section-header" onclick="toggleSection(this)">
        <div class="section-chevron">▶</div>
        <div class="section-icon">[EMOJI]</div>
        <div class="section-title">[TITLE]</div>
        <div class="section-subtitle">[SUBTITLE — brief context]</div>
    </div>
    <div class="section-body">
```

### Section Intro Paragraph
Every section must open with an explicit intro paragraph that includes:
- What this section covers
- Which strategies/entities it applies to
- Cooldown period (if applicable)
- Per-cycle change limit (if applicable)
- Auto/Approval rules (if applicable)
- Caps and limits (if applicable)
- References to Client Configuration where settings are editable

**The intro must be fully self-contained.** Never reference other sections. Never say "same as above", "same rules as X", or "see Y section". Every parameter must be explicit within the section.

---

## 3. Design System Reference

The full Design System is documented in the "Design System" tab of the architecture document (ACT_OPTIMIZATION_ARCHITECTURE_v53.html). It is the single source of truth for all visual standards. Key references below.

### 6-Level Colour Palette

| Level | Colour Name | Hex | CSS Variable | Background | Border |
|-------|-------------|-----|-------------|------------|--------|
| Account (L1) | Blue | #3b82f6 | --blue | #eff6ff (--blue-bg) | #bfdbfe (--blue-border) |
| Campaign (L2) | Green | #10b981 | --green | #ecfdf5 (--green-bg) | #a7f3d0 (--green-border) |
| Ad Group (L3) | Amber | #f59e0b | --amber | #fffbeb (--amber-bg) | #fde68a (--amber-border) |
| Keyword (L4) | Purple | #8b5cf6 | --purple | #f5f3ff (--purple-bg) | #c4b5fd (--purple-border) |
| Ad (L5) | Pink | #ec4899 | --pink | #fdf2f8 (--pink-bg) | #fbcfe8 (--pink-border) |
| Shopping (L6) | Teal | #14b8a6 | --teal | #ecfeff | (inline) |

### Risk Level Badges

| Level | Colour | Hex | Note |
|-------|--------|-----|------|
| Low Risk | Grey | #94a3b8 | NOT green — green is reserved for Act |
| Medium Risk | Amber | #f59e0b | Same as --amber |
| High Risk | Red | #ef4444 | Same as --red |

### Status Badges

| Status | Colour | Hex |
|--------|--------|-----|
| Healthy | Green | #10b981 |
| Trending Down | Amber | #f59e0b |
| Too Early to Assess | Grey | #94a3b8 |

### Typography Colours (Finalised v54)

Only 2 text colour tiers are permitted. Grey text colours (--text-muted, --text-faint) are deprecated and mapped to --text-secondary.

| Variable | Light Mode | Dark Mode | Usage |
|----------|-----------|-----------|-------|
| --text-primary | #1e293b | #f1f5f9 | Headings, bold text, table signal columns, important content |
| --text-secondary | #2d3748 | #d1d5db | Body text, descriptions, subtitles, table detail columns, callout text |
| ~~--text-muted~~ | DEPRECATED | DEPRECATED | Mapped to --text-secondary. Do not use. |
| ~~--text-faint~~ | DEPRECATED | DEPRECATED | Mapped to --text-secondary. Do not use. |

**Brand colours** (level colours, action category colours) may be used for badges, pills, interactive elements, and accent text only — never for body copy.

**Rules:**
- No #94a3b8, #64748b, #cbd5e1, or #334155 hex codes for text anywhere
- No `color: grey` or `color: gray` anywhere
- All text must be either --text-primary, --text-secondary, or a brand colour
- Badge text on coloured backgrounds uses pure white (#ffffff)

## 4. Colour Coding — 4 Response Categories

Every page must use these 4 categories consistently across tables, decision trees, and flowcharts.

| Category | Colour | CSS Class (badge) | CSS Class (flow step) | Mermaid Style | When Used |
|----------|--------|-------------------|----------------------|---------------|-----------|
| Act | Green | `status-act` | `flow-result-act` | `fill:#ecfdf5,stroke:#10b981` | ACT auto-executes this change overnight. Issue is inside the ads platform. |
| Monitor | Blue | `status-monitor` | `flow-result-monitor` | `fill:#eff6ff,stroke:#3b82f6` | No action needed. Performance is within target or insufficient data. |
| Investigate | Amber | `status-investigate` | `flow-result-investigate` | `fill:#fffbeb,stroke:#f59e0b` | Requires human approval. Fix may be external or action is a loosening change. |
| Alert | Red | `status-alert` | `flow-result-alert` | `fill:#fef2f2,stroke:#ef4444` | Urgent issue or hard limit. No automated action — human must investigate. |

### Decision Tree Branch Colours
| Branch Type | CSS Class | When Used |
|-------------|-----------|-----------|
| Positive/Yes (action taken) | `branch-yes` | Green label — ACT takes action on this path |
| Negative/No (problem path) | `branch-no` | Red label — problem detected, further diagnosis needed |
| Monitor/No action | `branch-monitor` | Blue label — no action needed, performance is on target |

### Mermaid Node Colours
| Node Type | Fill | Stroke | Used For |
|-----------|------|--------|----------|
| Start node | `#f1f5f9` | `#94a3b8` | Entry point of the flowchart |
| Decision diamond (blue theme) | `#eff6ff` | `#3b82f6` | Questions/checks (Lead Gen, CPA-focused) |
| Decision diamond (purple theme) | `#f5f3ff` | `#8b5cf6` | Questions/checks (Ecommerce, ROAS-focused) |
| Act (auto-execute) | `#ecfdf5` | `#10b981` | ACT takes action |
| Monitor (no action) | `#eff6ff` | `#3b82f6` | No action needed |
| Investigate (approval) | `#fffbeb` | `#f59e0b` | Requires approval |
| Alert (urgent) | `#fef2f2` | `#ef4444` | Urgent — human review |
| Hard stop | `#fef2f2` | `#ef4444` (3px) | Floor/ceiling reached |

---

## 4. Table Standards

### Required Columns
All action/lever tables must have these columns in this order:

| Column | Content |
|--------|---------|
| Signal | What triggers this row (threshold, time period, click minimum) |
| Detail | Real-world example with specific numbers |
| ACT Response | Explicit action description (not just "Act" — state what ACT does) |
| Cooldown | Time before ACT can adjust this item again. Use "—" if not applicable. Use "None" for binary actions. |
| Auto/Approval | "Auto" for auto-executed, "Approval" for human approval needed, "—" for monitor/no action rows |

### Required Rows
Every table must include a "within target range / no action" row with:
- `status-monitor` badge
- "No action" or "Monitor" text
- Cooldown: "—"
- Auto/Approval: "—"

### ACT Response — Must Be Explicit
Never use vague responses like "Act" or "Investigate". Always state the specific action:
- **Good:** "Act: Reduce budget for this campaign, reallocate to better performers"
- **Bad:** "Act"
- **Good:** "Act: Lower bid by 10% (auto, 72hr cooldown)"
- **Bad:** "Act — scale?"
- **Good:** "Investigate: Check search terms first, then flag as website/landing page issue if terms are fine"
- **Bad:** "Investigate"
- **Good:** "Alert: Do not adjust budget — product/inventory issue outside ads platform. Check Merchant Center and stock."
- **Bad:** "Alert"
- **Good:** "Monitor: No action — campaign CPA is within target range"
- **Bad:** "No action"

### Signal Column — Must Include All Parameters
Every signal must specify all relevant parameters. Never leave a threshold vague.
- **Good:** "CPA/ROAS 20-50% worse, 14+ days, 50+ clicks"
- **Bad:** "CPA/ROAS worse"
- **Good:** "Spend > 2x CPA target, 0 conversions, 14+ days"
- **Bad:** "High spend, no conversions"
- **Good:** "Exact match converting well, < 50 impressions/day, 21+ days"
- **Bad:** "Low volume keyword"

---

## 5. Decision Tree Standards

### Mermaid Flowcharts
- Use `data-mermaid` attribute approach (deferred rendering) to avoid display:none rendering issues
- Use `startOnLoad: false` in Mermaid config
- Render charts via `renderMermaidInPage()` when tab becomes visible
- Every node ID must be prefixed with a unique 2-3 letter prefix per chart (e.g., MC_ for Manual CPC, TC_ for tCPA)
- Act nodes must include cooldown reference (e.g., "72hr cooldown")
- Use `<br/>` for line breaks in labels (not `\n`)
- Display in `persona-grid` (2-column layout)
- Blue theme for Lead Gen / CPA-focused charts
- Purple theme for Ecommerce / ROAS-focused charts

### Detailed Reference Cards
- Display in `persona-grid` (2-column layout) where possible
- Each card must include:
  - Title with number and strategy name
  - Step-by-step nodes using `decision-tree` class
  - `node-question` for the decision point
  - `node-detail` with explicit parameters: signal windows, cooldowns, caps, Client Configuration references
  - `tree-branches` for yes/no paths with appropriate colour classes
  - `scenario-flow` for action outcomes with explicit responses including cooldown and auto/approval
  - Nested flows use `padding-left:24px` (first level) and `padding-left:48px` (second level)

---

## 6. Writing Rules

1. **Every section must be fully self-contained.** Never reference other sections. Never say "same as above", "same rules as X", or "see Y section". Every table, explanation, and parameter must be explicit and complete within its own section. This is critical because the document will be used as a build specification.

2. **Every ACT response must state the specific action.** Not just the category (Act/Investigate/Alert) but what ACT actually does. Include the cooldown and auto/approval status inline where practical.

3. **Every threshold must include:** the percentage, the time period, and the minimum data requirement (click count). Example: "CPA/ROAS 20-50% worse, 14+ days, 50+ clicks". Never use vague thresholds like "worse" or "high spend".

4. **Every cooldown must be stated** in three places: the section intro paragraph, the table Cooldown column, and the decision tree node detail text.

5. **Every cap/limit must be stated** in the section intro paragraph and also listed in the Guardrails section at the bottom of the page.

6. **Client Configuration references:** Any editable setting must note "editable per client in the Client Configuration tab". When a new editable setting is created, it must be immediately added to the Client Configuration tab.

7. **Counter-intuitive logic must be explained.** If the logic is not obvious (e.g., raising tCPA target when CPA is too high, or lowering tROAS target when ROAS is too low), include a `callout callout-info` explanation box within the section. The explanation must be self-contained and not reference other sections.

8. **Universal principle: loosening = approval, tightening = auto.** Any action that accepts higher costs or lower returns (loosening) always requires human approval. Any action that improves efficiency (tightening) can be auto-executed within caps. This principle must be stated explicitly wherever tCPA, tROAS, or CPC cap adjustments are discussed.

9. **Monitor rows must use blue styling.** Any "no action" or "within target" row must use `status-monitor` (blue), never `status-act` (green). Green is reserved exclusively for rows where ACT takes an action.

10. **No orphaned content.** Every section must have proper opening and closing HTML tags. Every `persona-grid` must have a closing comment `<!-- end persona-grid -->`. Every page must have a closing comment `<!-- end page-[name] -->`.

---

## 7. Technical Standards

### Font Sizes
| Element | Size |
|---------|------|
| Minimum font size | 12px |
| Body text / table cells | 13px |
| Section titles | 16px |
| Card titles | 14-15px |
| Level titles | 28px |
| Top nav logo | 18px |

### Emoji Mapping — Consistent Across All Pages
| Section Type | Emoji |
|-------------|-------|
| Overview / Personas / Setup | 👤 or 🏗️ |
| Target Ranges | 🎯 |
| Actions & Monitoring | ⚡ |
| Campaign Roles | 🏷️ |
| Budget / Money | 💰 |
| Competition / Balance | ⚖️ |
| Signal Decomposition / Data | 📊 |
| Signal Detection / Time | ⏱️ |
| Performance Scoring | 📈 |
| Decision Trees — Mermaid | 🔀 |
| Decision Trees — Detailed | 🌳 |
| Cooldown Summary | ⏳ |
| Guardrails | 🛡️ |
| Negative Keywords | 🚫 |
| Device | 📱 |
| Geo | 🌍 |
| Ad Schedule | 🕐 |
| Match Types | 🔤 |
| Manual CPC | 🎛️ |
| Target CPA | 🎯 |
| Target ROAS | 💰 |
| Maximize Conversions | 🔄 |
| Max Clicks | 🖱️ |
| PMax | 🤖 |
| Shopping | 🛒 |
| Negative Performance Outliers | 📉 |
| Positive Performance Outliers | 📈 |
| Pause Recommendations | ⏸️ |

### CSS Classes Available
| Purpose | Class |
|---------|-------|
| 2-column grid | `persona-grid` |
| Collapsible section | `section` with `data-section` |
| Data table | `data-table` |
| Callout (info) | `callout callout-info` |
| Callout (warning) | `callout callout-warning` |
| Callout (key) | `callout callout-key` |
| Status badge (act) | `status status-act` |
| Status badge (monitor) | `status status-monitor` |
| Status badge (investigate) | `status status-investigate` |
| Status badge (alert) | `status status-alert` |
| Flow step | `flow-step flow-trigger` / `flow-check` / `flow-result-act` / `flow-result-monitor` / `flow-result-investigate` / `flow-result-alert` |
| Flow arrow | `flow-arrow` (content: →) |
| Decision tree | `decision-tree` > `tree-node` > `node-dot` + `node-content` |
| Branch cards | `tree-branch branch-yes` / `branch-no` / `branch-monitor` |
| Priority list | `priority-list` with `priority-num` spans |
| Guardrail list | `guardrail-list` |
| Review flow | `review-flow` > `review-step` |
| Budget bars | `budget-bar-container` / `budget-bar-track` / `budget-bar-fill` |
| Zone visual | `zone-visual` > `zone-block` |
| Scoring bar | `scoring-bar` > `scoring-segment` |

### Theme Support
- Light theme is default (`data-theme="light"`)
- Dark theme toggle available (`data-theme="dark"`)
- All colours use CSS variables (e.g., `var(--blue)`, `var(--green-bg)`)
- Theme toggle function: `toggleTheme()`

### Versioning
- Every version is saved as a separate file: `ACT_OPTIMIZATION_ARCHITECTURE_v[N].html`
- Never overwrite a previous version
- Always create a new version before making changes
- Update `MEMORY.md` with the latest version number after each new version
- Latest version number is tracked in: `docs/ACT_OPTIMIZATION_ARCHITECTURE_v[N].html` and `memory/MEMORY.md`

### Nav Tab Management
- Each level gets a nav tab in the top bar
- Tabs for incomplete levels use `class="nav-tab disabled"` and no `onclick`
- When a level page is built, enable its tab: `class="nav-tab"` with `onclick="showLevel('[name]')"`
- The Client Configuration tab is always enabled and separated with a left border
- Active tab uses `class="nav-tab active"`

### Mermaid Rendering — Critical Implementation Detail
Mermaid charts inside hidden pages (`display:none`) will fail to render on page load. To solve this:
1. Set `mermaid.initialize({ startOnLoad: false })`
2. Store chart code in `data-mermaid` HTML attributes (HTML-escaped)
3. On page load, call `renderMermaidInPage('page-account')` for the visible page
4. In `showLevel()`, call `renderMermaidInPage('page-' + name)` with a 50ms setTimeout after making the page visible
5. The `renderMermaidInPage()` function finds `.mermaid-pending` elements, creates `.mermaid` divs with the code, calls `mermaid.run()`, then reclasses to `.mermaid-done`

---

## 8. Client Configuration

Every new editable setting discovered during design must be immediately added to the Client Configuration tab. The tab has these sections:

| Section | What It Contains |
|---------|-----------------|
| Account-Level Settings | Persona, budget, target range, deviation threshold, budget bands, role mapping, max overnight move |
| Campaign-Level Settings | CPC floor/ceiling, tCPA floor/ceiling, tROAS floor/ceiling, per-cycle change, 7-day max change |
| Cooldown Periods | All cooldowns — budget shift, keyword bid, product group, device, geo, schedule, tCPA/tROAS, CPC cap |
| Modifier Caps | Auto max negative/positive and approval max for device, geo, ad schedule |

When designing a new level (Ad Group, Keyword, Ad, Shopping), check:
1. Are there new cooldowns? → Add to Cooldown Periods section in Client Configuration AND to the level's own Cooldown Summary section AND to the Campaign Level Cooldown Summary (if it's a campaign-level lever)
2. Are there new caps/limits? → Add to Modifier Caps section or create new section in Client Configuration
3. Are there new editable thresholds? → Add to appropriate section in Client Configuration
4. Are there new auto/approval rules? → Document in the level's Actions & Monitoring section AND in the level's Guardrails section

---

## 9. Quality Checklist — Run Before Finalising Any Page

Before marking a page as complete, verify all of the following:

- [ ] All section intros are fully self-contained (no cross-references)
- [ ] All tables have the 5 required columns (Signal, Detail, ACT Response, Cooldown, Auto/Approval)
- [ ] All tables have a "within target range / no action" monitor row
- [ ] All ACT responses are explicit (state the specific action, not just the category)
- [ ] All signals include percentage, time period, and click minimum where applicable
- [ ] All cooldowns are stated in section intro, table rows, and decision tree nodes
- [ ] All caps/limits are stated in section intro and Guardrails section
- [ ] All "no action" elements use blue styling (not green) across tables, decision trees, and Mermaid charts
- [ ] All Mermaid node IDs have unique prefixes per chart
- [ ] All Mermaid Act nodes include cooldown references
- [ ] Emojis are consistent with the emoji mapping table
- [ ] Section order matches the required order (Overview → Actions → Core Logic → Decision Trees → Cooldowns → Guardrails)
- [ ] New editable settings have been added to Client Configuration tab
- [ ] No orphaned HTML tags or unclosed divs
- [ ] Page renders correctly in both light and dark themes
- [ ] Mermaid charts render when switching to the page tab (deferred rendering working)
