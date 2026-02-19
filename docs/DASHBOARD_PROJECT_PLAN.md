# DASHBOARD UI OVERHAUL - Complete Project Plan

**Project:** Chat 21 - Google Ads-Inspired Dashboard  
**Timeline:** 20 hours / 3 days  
**Framework:** Bootstrap 5  
**Icons:** Bootstrap Icons  
**Status:** IN PROGRESS - 6/8 Complete (75%) 🔥  
**Started:** February 18, 2026 11:44 AM  
**Current:** February 19, 2026 4:15 PM  
**Mode:** LEGENDARY - 6 down, 2 to go!  
**Created:** 2026-02-18 02:45 AM  
**Updated:** 2026-02-19 04:15 PM  
**Location:** Will be moved to `/docs/DASHBOARD_PROJECT_PLAN.md`

---

## 🎯 PROJECT GOALS

### **Primary Objective:**
Create a professional, Google Ads-inspired dashboard that feels familiar to millions of Google Ads users while maintaining ACT's unique AI-powered features.

### **Success Criteria:**
- ✅ All 8 main pages redesigned (including Ad Groups)
- ✅ Responsive (desktop + mobile)
- ✅ Professional appearance
- ✅ Fast loading (<2 seconds)
- ✅ Intuitive navigation
- ✅ AI insights integrated seamlessly
- ✅ Pagination on all tables (10, 25, 50, 100 rows)
- ✅ Search terms stay within Keywords page

---

## 📋 PAGES TO BUILD/REDESIGN

### **Page Inventory:**

| # | Page Name | Current Status | Action Needed | Priority | Est. Time |
|---|-----------|----------------|---------------|----------|-----------|
| 1 | **Main Dashboard** | Exists (basic) | Major redesign | HIGH | 3 hrs |
| 2 | **Campaigns** | Doesn't exist | Build from scratch | HIGH | 2 hrs |
| 3 | **Ad Groups** | Doesn't exist | Build from scratch | HIGH | 2 hrs |
| 4 | **Keywords** | Exists (basic) | Redesign + enhance | HIGH | 3 hrs |
| 5 | **Ads** | Exists (basic) | Redesign + enhance | HIGH | 2 hrs |
| 6 | **Shopping** | Exists (4 tabs) | Redesign tabs | HIGH | 3 hrs |
| 7 | **Recommendations** | Exists (basic) | Integrate into all pages | HIGH | 2 hrs |
| 8 | **Changes** | Exists (basic) | Redesign table | MEDIUM | 1 hr |
| 9 | **Settings** | Exists (basic) | Minor polish | LOW | 0.5 hrs |

**Total:** 18.5 hours (with 1.5 hrs buffer for bugs/polish)

---

## ✅ ANSWERED QUESTIONS

1. **Build Ad Groups page?** YES - Included in 20-hour plan
2. **Search Terms separate or in Keywords?** STAY IN KEYWORDS (collapsible section)
3. **Pagination?** YES - All tables: 10, 25, 50, 100 rows per page
4. **Icons?** BOOTSTRAP ICONS (lowest risk, best integration)

---

## 🏗️ ARCHITECTURE PLAN

### **Layout Structure (All Pages):**

```
┌──────────────────────────────────────────────────────────────┐
│ TOP NAV BAR                                                   │
│ [ACT Logo] [Client: Synthetic ▼] [Date: Last 7d ▼] [User ▼] │
├──────────┬───────────────────────────────────────────────────┤
│          │ METRICS BAR                                       │
│ LEFT     │ ┌───────┬───────┬───────┬───────┬───────┬───────┐│
│ SIDEBAR  │ │Clicks │ Impr. │ Cost  │ Conv. │ ROAS  │ CPA   ││
│          │ │1,234  │45.6K  │$1,234 │  56   │ 3.2x  │  $22  ││
│ 🏠 Dash  │ │+12% ↑ │ +5% ↑ │ +8% ↑ │ -3% ↓ │+15% ↑ │ -5% ↓ ││
│ 📊 Camps │ └───────┴───────┴───────┴───────┴───────┴───────┘│
│ 📁 AdGrp │                                                   │
│ 🔑 KWs   │ DATE RANGE & FILTERS                              │
│ 📝 Ads   │ [Last 7 days ▼] [Search...] [Filters ▼]          │
│ 🛒 Shop  │                                                   │
│ ────     │                                                   │
│ 💡 Recs  │ MAIN CONTENT AREA                                 │
│ 📜 Chgs  │ (Tables, Charts, Cards)                           │
│ ────     │                                                   │
│ ⚙️ Set   │                                                   │
└──────────┴───────────────────────────────────────────────────┘
```

### **Global Navigation (Sidebar):**

```html
<div class="sidebar bg-dark text-white">
  <div class="logo">ACT Dashboard</div>
  <ul class="nav flex-column">
    <li><a href="/"><i class="bi bi-house"></i> Dashboard</a></li>
    <li><a href="/campaigns"><i class="bi bi-bar-chart"></i> Campaigns</a></li>
    <li><a href="/ad-groups"><i class="bi bi-folder"></i> Ad Groups</a></li>
    <li><a href="/keywords"><i class="bi bi-key"></i> Keywords</a></li>
    <li><a href="/ads"><i class="bi bi-file-text"></i> Ads</a></li>
    <li><a href="/shopping"><i class="bi bi-cart"></i> Shopping</a></li>
    <li class="divider"></li>
    <li><a href="/recommendations"><i class="bi bi-lightbulb"></i> Recommendations</a></li>
    <li><a href="/changes"><i class="bi bi-clock-history"></i> Changes</a></li>
    <li class="divider"></li>
    <li><a href="/settings"><i class="bi bi-gear"></i> Settings</a></li>
  </ul>
</div>
```

---

## 📐 DESIGN SYSTEM

### **Color Palette:**

**Bootstrap Default (Google Ads-Inspired):**
- Primary Blue: `#0d6efd`
- Success Green: `#198754`
- Danger Red: `#dc3545`
- Warning Yellow: `#ffc107`
- Info Cyan: `#0dcaf0`
- Secondary Gray: `#6c757d`

**Backgrounds:**
- Page: `#f8f9fa` (light gray)
- Cards: `#ffffff`
- Sidebar: `#212529` (dark)
- Table Hover: `#e9ecef`

### **Typography:**
- Body: 14px
- Tables: 13px
- Headings: Bootstrap defaults (h1-h6)
- Metrics: 24px bold

### **Icons:**
Bootstrap Icons 1.11 via CDN:
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
```

---

## 📄 DETAILED PAGE SPECIFICATIONS

---

## **PAGE 1: MAIN DASHBOARD**

### **Metrics Bar:**
| Metric | Value | Change |
|--------|-------|--------|
| Clicks | 1,234 | +12% ↑ (green) |
| Impressions | 45.6K | +5% ↑ (green) |
| Cost | $1,234 | +8% ↑ (red) |
| Conversions | 56 | -3% ↓ (red) |
| ROAS | 3.2x | +15% ↑ (green) |
| CPA | $22 | -5% ↓ (green) |

**Note:** Change % compares last 7 days vs previous 7 days

### **Cards:**

**Card 1: Performance Trend Chart** (col-12)
- Chart.js line chart
- Tabs: 7 days | 30 days | 90 days
- Lines: Cost (red), Conversions (green), ROAS (blue)
- X-axis: Dates
- Y-axis: Dual (cost/conversions left, ROAS right)

**Card 2: Top 5 Campaigns** (col-6)
Table columns:
1. Campaign Name
2. Status (badge)
3. Cost (7d)
4. Conversions (7d)
5. ROAS
6. Actions (dropdown icon)

**Card 3: Pending Recommendations** (col-6)
- Header: "12 Recommendations" (badge)
- List of top 3 by predicted impact:
  - Icon (lightbulb)
  - Rule name
  - Entity (Campaign/Keyword/Ad)
  - Impact: "+$234 revenue"
- Button: "Review All" → /recommendations

**Card 4: Recent Changes** (col-6)
List of last 5 changes:
- Date/time (small, muted)
- Campaign name
- Change badge: "Bid ↑ +15%"
- Status: "Monitoring" (warning) | "Success" (success)

**Card 5: Account Health** (col-6)
Metrics:
- Active Campaigns: 42
- Paused Campaigns: 8
- Campaigns with Issues: 3 (danger badge)
- Last Data Sync: "2 hours ago"

### **AI Insights:**
Alert badges at top:
- `bg-warning` "Budget pacing 15% ahead of target"
- `bg-danger` "3 campaigns underperforming vs ROAS target"
- `bg-success` "2 optimization opportunities available"

### **Quick Actions:**
- Button: "Apply Top Recommendations" (btn-primary)
- Button: "View All Recommendations" (btn-secondary)
- Button: "Export Report" (btn-outline-primary)

---

## **PAGE 2: CAMPAIGNS**

### **Metrics Bar** (Dynamic - updates with selected rows)
| Metric | Formula |
|--------|---------|
| Clicks | SUM(selected rows) or SUM(all) if none selected |
| Cost | SUM(selected) |
| Conv. | SUM(selected) |
| ROAS | SUM(conv_value) / SUM(cost) |
| CPA | SUM(cost) / SUM(conv) |
| CTR | SUM(clicks) / SUM(impr) |

Header text: "Selected Campaigns (15 of 42)" or "All Campaigns (42 total)"

### **Table Columns:**
1. ☐ Checkbox
2. **Campaign Name** (linked to Google Ads, sortable)
3. **Status** (badge: Active/Paused/Removed)
4. **Type** (badge: Search/Display/Shopping)
5. **Budget** ($XX.XX daily)
6. **Spend** (7-day total, sortable)
7. **Clicks** (sortable)
8. **Impressions** (sortable)
9. **CTR** (%, sortable)
10. **Conversions** (sortable)
11. **ROAS** (sortable)
12. **AI Insight** (badge icon if rec exists)
13. **Actions** (dropdown)

### **Badges:**
**Status:**
- Active: `badge bg-success`
- Paused: `badge bg-secondary`
- Removed: `badge bg-danger`

**Type:**
- Search: `badge bg-info`
- Shopping: `badge bg-primary`
- Display: `badge bg-warning`

**AI Insight:**
- `badge bg-warning` with `<i class="bi bi-lightbulb"></i>` icon
- Tooltip: "AI suggests increasing budget by 15%"

### **Cards (above table):**
**Card 1:** Campaign Type Pie Chart (col-4)
**Card 2:** Budget Utilization Bar Chart (col-8)

### **Pagination:**
"Showing 1-25 of 42" | [10] [25] [50] [100] | < 1 2 >

### **Pending Recommendations (Right Sidebar):**
- Header: "8 Campaign Recommendations"
- List:
  - Campaign name (truncated)
  - Rec type badge ("Budget ↑")
  - Impact ("+$450/wk")
  - "Apply" button (btn-sm btn-primary)

### **Quick Actions:**
**Toolbar (top-right):**
- "Create Campaign" (btn-primary)
- "Export" (btn-outline-secondary)

**Bulk Actions (appears when ☐ checked):**
- "Bulk Edit" (btn-secondary)
- "Pause Selected" (btn-danger)

**Row Actions (dropdown):**
- Edit Budget
- Pause Campaign  
- View Performance Details
- View in Google Ads (external link)

---

## **PAGE 3: AD GROUPS**

### **Metrics Bar:**
| Metric | Value |
|--------|-------|
| Clicks | 12,345 |
| Cost | $5,678 |
| Conv. | 234 |
| ROAS | 3.4x |
| CTR | 2.3% |
| Avg QS | 7.2 |

### **Table Columns:**
1. ☐ Checkbox
2. **Ad Group Name** (linked, sortable)
3. **Campaign** (parent, muted text, small)
4. **Status** (badge)
5. **Max CPC** (editable inline)
6. **Clicks** (sortable)
7. **CTR** (%, sortable)
8. **Conversions** (sortable)
9. **Cost/Conv** (CPA, sortable)
10. **Quality Score** (color coded, sortable)
11. **AI Insight** (badge)
12. **Actions** (dropdown)

### **Quality Score Color Coding:**
- 8-10: `text-success` (green)
- 5-7: `text-warning` (yellow)
- 1-4: `text-danger` (red)
- N/A: `text-muted` (gray)

### **Badges:**
Same as campaigns for status.

**AI Insight badges:**
- `bg-danger` "Low quality score detected"
- `bg-warning` "Bid too high vs ROAS target"
- `bg-success` "Optimization opportunity"

### **Cards:**
**Card 1:** QS Distribution (bar chart showing count of ad groups by QS range)
**Card 2:** Top/Bottom 5 Ad Groups (2 mini tables side by side)

### **Pagination:** Same as campaigns (10/25/50/100)

### **Pending Recommendations:**
"12 Ad Group Recommendations"
Grouped tabs: Bid Adjustments (8) | Pause (4)

### **Quick Actions:**
**Bulk (when selected):**
- "Adjust Bids" → modal with % or $ input
- "Pause Selected"

**Row actions:**
- Edit Max CPC
- View Keywords (navigate to Keywords filtered to this ad group)
- Pause Ad Group

---

## **PAGE 4: KEYWORDS**

### **Metrics Bar:**
| Metric | Value |
|--------|-------|
| All Keywords | 2,847 total |
| Active | 2,456 |
| Paused | 391 |
| Clicks | 23,456 |
| Cost | $8,901 |
| Conv. | 456 |
| CPA | $19.50 |
| Avg QS | 6.8 |
| Wasted Spend | $234 (red if >$100) |

### **Table Columns:**
1. ☐ Checkbox
2. **Keyword** (text with match type pill beside it)
3. **Match Type** (badge-pill)
4. **Status** (badge)
5. **Campaign** (muted, small)
6. **Ad Group** (muted, small)
7. **Max CPC** (editable)
8. **QS** (1-10, color coded) + expandable sub-columns:
   - Landing Page (1-10)
   - Ad Relevance (1-10)
   - Expected CTR (1-10)
9. **Clicks (7d)** (sortable)
10. **Cost (30d)** (sortable)
11. **Conv. (30d)** (sortable)
12. **CPA** (sortable)
13. **ROAS** (sortable, if ecom)
14. **AI Insight** (badge with tooltip)
15. **Actions** (dropdown)

### **Match Type Pills:**
- Exact: `badge badge-pill bg-success` "Exact"
- Phrase: `badge badge-pill bg-primary` "Phrase"
- Broad: `badge badge-pill bg-warning` "Broad"

### **AI Insight Badges (Detailed):**

**Badge Colors & Icons:**
- `bg-danger` + `<i class="bi bi-pause-circle"></i>` → "Pause recommended"
- `bg-warning` + `<i class="bi bi-arrow-down"></i>` → "Decrease bid"
- `bg-success` + `<i class="bi bi-arrow-up"></i>` → "Increase bid"
- `bg-info` + `<i class="bi bi-plus-circle"></i>` → "Add as keyword"
- `bg-secondary` + `<i class="bi bi-x-circle"></i>` → "Add as negative"

**Tooltip Content:**
- Rule ID: KW-PAUSE-001
- Rationale: "High cost ($234), zero conversions in 30 days"
- Predicted Impact: "Save $150/month"
- Click badge → Opens full recommendation modal

### **Cards (above table):**
**Card 1:** QS Distribution Histogram (col-4)
**Card 2:** Low Data Keywords Count (col-4) - warning if >50
**Card 3:** Wasted Spend Total (col-4) - danger if >$100

### **Search Terms Section (Collapsible Panel, below keywords table):**

**Toggle:** "Show Search Terms (1,234)" / "Hide Search Terms"

**When expanded, table shows:**

**Columns:**
1. **Search Term** (actual user query)
2. **Status** (badge: "Added" if exists as keyword, "None" if not)
3. **Triggered Keyword** (which keyword matched this)
4. **Match Type** (how it matched: Exact/Phrase/Broad)
5. **Clicks (30d)**
6. **Cost (30d)**
7. **Conv. (30d)**
8. **CVR** (Conversion Rate %)
9. **AI Insight** (add as keyword vs negative)
10. **Quick Actions:**
    - "Add as Keyword" button
    - "Add as Negative" button

### **Pagination:** 10/25/50/100 (default 25)

### **Pending Recommendations (Right Sidebar):**
"45 Keyword Recommendations"

**Grouped Tabs:**
- Pause (12)
- Bid Decrease (18)
- Bid Increase (8)
- Add Keywords (5)
- Add Negatives (2)

Each shows:
- Keyword text
- Rule ID badge
- Predicted impact
- "Apply" button

### **Quick Actions:**

**Toolbar:**
- "Adjust Selected Bids" → modal
- "Pause Selected"
- "Add Selected to Negatives"
- "Export"

**Row Actions:**
- Pause Keyword
- Edit Bid (inline or modal)
- View Performance Graph (modal with Chart.js)
- Add to Negative List

---

## **PAGE 5: ADS**

### **Metrics Bar:**
| Metric | Value |
|--------|-------|
| All Ads | 983 total |
| RSAs | 856 |
| ETAs | 127 |
| Clicks | 18,234 |
| Cost | $6,789 |
| Conv. | 289 |
| CTR | 1.9% |
| Avg Strength | Good (7.2/10) |

### **Table Columns:**
1. ☐ Checkbox
2. **Ad Preview** (text snippet, clickable → opens modal)
3. **Ad Type** (badge: RSA/ETA)
4. **Status** (badge)
5. **Campaign** (muted, small)
6. **Ad Group** (muted, small)
7. **Ad Strength** (for RSAs - progress bar)
8. **Clicks** (sortable)
9. **Impressions** (sortable)
10. **CTR** (%, sortable)
11. **Conv.** (sortable)
12. **Cost/Conv** (CPA)
13. **AI Insight** (badge)
14. **Actions** (dropdown)

### **Ad Strength Progress Bar:**
HTML examples:
```html
<!-- Poor (1-33%) -->
<div class="progress">
  <div class="progress-bar bg-danger" style="width: 25%">Poor</div>
</div>

<!-- Average (34-66%) -->
<div class="progress">
  <div class="progress-bar bg-warning" style="width: 50%">Average</div>
</div>

<!-- Good (67-89%) -->
<div class="progress">
  <div class="progress-bar bg-success" style="width: 75%">Good</div>
</div>

<!-- Excellent (90-100%) -->
<div class="progress">
  <div class="progress-bar bg-info" style="width: 100%">Excellent</div>
</div>
```

### **Preview Modal (Bootstrap Modal):**

**Trigger:** Click ad preview text in table

**Modal Size:** Large (modal-lg)

**Modal Header:**
- Title: "Ad Preview - ID: 123456789"
- Status badge
- Close button (×)

**Modal Body - Two Columns:**

**Left Column (60% width):**

**Section 1: Google Ads Preview (styled box)**
```
┌──────────────────────────────────┐
│ Ad · https://example.com         │
│ ────────────────────────────────│
│ Headline 1 - Headline 2 -       │
│ Headline 3                       │
│                                  │
│ Description line 1 continues     │
│ with more details and CTA.       │
└──────────────────────────────────┘
```

**Section 2: All Headlines (numbered list)**
1. Headline 1 📌 (if pinned to position 1)
2. Headline 2
3. Headline 3
... up to 15

**Section 3: All Descriptions (numbered list)**
1. Description 1
2. Description 2
... up to 4

**Section 4: URLs**
- Final URL: https://example.com/product
- Display Path: example.com/product

**Right Column (40% width):**

**Performance Metrics Card:**
| Metric | Value |
|--------|-------|
| Impressions | 12,345 |
| Clicks | 234 |
| CTR | 1.9% |
| Conversions | 12 |
| Cost | $234 |
| CPA | $19.50 |

**Ad Strength Details Card (RSA only):**
- Overall Score: Good (progress bar)
- Improvement Suggestions:
  - ✅ Enough headlines (15)
  - ⚠️ Add more unique descriptions
  - ✅ Keywords in headlines
  - ❌ Avoid repetition in headlines 3, 7, 11

**Modal Footer:**
- "Edit in Google Ads" (btn-primary, external link)
- "Close" (btn-secondary)

### **Asset Performance Breakdown (Expandable Row Detail):**

**When you click expand icon on RSA row, shows beneath:**

**Three Cards in Row:**

**Card 1: Headline Performance**
Table:
| Headline | Impressions | Performance | Pin |
|----------|-------------|-------------|-----|
| Headline 1 | 5,234 | Best (bg-success) | Position 1 |
| Headline 2 | 4,123 | Good (bg-primary) | - |
| Headline 3 | 3,456 | Low (bg-danger) | - |
... all 15

**Card 2: Description Performance**
Table:
| Description | Impressions | Performance |
|-------------|-------------|-------------|
| Description 1 | 8,234 | Best |
| Description 2 | 7,123 | Good |
... all 4

**Card 3: Ad Strength Breakdown**
List with icons:
- ✅ `text-success` "Enough headlines (15)"
- ⚠️ `text-warning` "Add more unique descriptions (currently 3, need 4)"
- ✅ `text-success` "Keywords in headlines"
- ❌ `text-danger` "Avoid repetition (headlines 3, 7, 11 similar)"

### **AI Insight Badges:**
- `bg-danger` "AD-PAUSE-003: Poor performance, pause recommended"
- `bg-warning` "AD-REVIEW-002: Ad strength Poor, needs improvement"
- `bg-info` "AD-ASSET-001: Add more headline variations"
- `bg-secondary` "AD-GROUP-001: Too many ads in ad group (>5)"

### **Cards (above table):**
**Card 1:** Ad Strength Distribution Pie Chart (col-6)
**Card 2:** Ad Type Breakdown (RSA vs ETA) Pie Chart (col-6)

### **Pagination:** 10/25/50/100

### **Pending Recommendations:**
"289 Ad Recommendations"
Grouped:
- Pause (102)
- Review/Improve (187)

### **Quick Actions:**
**Toolbar:**
- "Create New Ad" (btn-primary)
- "Export"

**Bulk (when selected):**
- "Pause Selected"

**Row Actions:**
- Pause Ad
- View in Google Ads (external)
- View Performance (chart modal)
- Expand Asset Details (for RSAs)

---

## **PAGE 6: SHOPPING**

**Tabs:** Campaigns | Products | Feed Quality | Recommendations

---

### **TAB 1: Campaigns**

**Metrics Bar:**
| Metric | Value |
|--------|-------|
| All Shopping | 8 campaigns |
| Cost | $12,345 |
| Conv. | 456 |
| ROAS | 3.2x |
| Impr. | 234K |
| Avg Priority | Medium |

**Table Columns:**
1. ☐ Checkbox
2. **Campaign Name**
3. **Status** (badge)
4. **Priority** (badge: Low/Medium/High)
5. **Feed Label** (badge or "None")
6. **Impressions (30d)**
7. **Clicks (30d)**
8. **Cost (30d)**
9. **Conv. (30d)**
10. **Conv. Value** (revenue)
11. **ROAS** (color coded)
12. **AI Insight** (badge)
13. **Actions**

**ROAS Color Coding:**
- >3.0: `text-success` (green)
- 2.0-2.9: `text-warning` (yellow)
- <2.0: `text-danger` (red)

**Priority Badges:**
- High: `bg-danger`
- Medium: `bg-warning`
- Low: `bg-secondary`

---

### **TAB 2: Products**

**Metrics Bar:**
| Metric | Value |
|--------|-------|
| Top 200 Products | (by cost) |
| Cost | $8,901 |
| Conv. | 234 |
| ROAS | 2.8x |
| Out of Stock | 12 items (red if >0) |
| Feed Issues | 45 items (red if >10) |

**Table Columns:**
1. **Image** (50x50px thumbnail)
2. **Product Title** (truncated to 50 chars, full on hover)
3. **Product ID** (muted, small font)
4. **Brand** (badge-secondary)
5. **Category** (badge-info)
6. **Availability** (badge)
7. **Clicks (30d)**
8. **Cost (30d)**
9. **Conv. (30d)**
10. **Conv. Value**
11. **ROAS** (color coded)
12. **Feed Quality** (progress bar %)
13. **Issues** (badge count)
14. **AI Insight** (badge)
15. **Actions**

**Availability Badges:**
- In Stock: `bg-success`
- Out of Stock: `bg-danger`
- PreOrder: `bg-warning`

**Feed Quality Progress Bar:**
- 90-100%: `bg-success`
- 70-89%: `bg-warning`
- <70%: `bg-danger`

**Issues Badge:**
If product has issues, show count:
- `badge bg-danger` "3 issues" (if disapproved)
- `badge bg-warning` "1 issue" (if price mismatch)

---

### **TAB 3: Feed Quality**

**Layout: 4 Cards in Top Row + Issues Table Below**

**Card 1: Approval Status (col-3)**
- Pie chart:
  - Approved (green)
  - Disapproved (red)
  - Pending (yellow)
- Total: 1,234 products

**Card 2: Price Mismatches (col-3)**
- Large number: 45
- Percentage: 3.6% of total
- Badge: `bg-danger` if >5%, `bg-warning` if 2-5%, `bg-success` if <2%

**Card 3: Disapproval Reasons (col-3)**
- Bar chart of top 5:
  1. Missing price (23)
  2. Image quality (12)
  3. Policy violation (8)
  4. Missing description (5)
  5. Other (7)

**Card 4: Feed Freshness (col-3)**
- Last sync: "2 hours ago"
- Status badge:
  - `bg-success` if <24 hrs
  - `bg-warning` if 24-48 hrs
  - `bg-danger` if >48 hrs

**Feed Issues Table:**

**Columns:**
1. **Product ID**
2. **Product Title** (truncated)
3. **Brand**
4. **Approval Status** (badge)
5. **Issues** (multiple badges possible)
6. **Disapproval Reasons** (expandable list)
7. **Actions** (link to Merchant Center)

**Issue Badges:**
- Disapproved: `bg-danger`
- Price Mismatch: `bg-warning`
- Missing Info: `bg-secondary`

**Pagination:** 10/25/50/100

---

### **TAB 4: Recommendations**

**Same structure as main Recommendations page but filtered to Shopping:**

**Table:**
1. Product ID
2. Product Title (truncated)
3. Recommendation Type (badge)
4. Current Bid
5. Recommended Bid
6. Predicted Impact
7. Actions (Apply/Reject buttons)

---

### **AI Insights (Shopping):**
- `bg-warning` "SHOP-BID-001: Increase product bid by 15%"
- `bg-danger` "SHOP-PAUSE-001: Product underperforming, consider pausing"
- `bg-info` "SHOP-FEED-001: Fix feed quality issues (3 products)"

### **Pending Recommendations (Sidebar):**
"23 Shopping Recommendations"
Grouped:
- Bid Adjustments (18)
- Feed Quality (5)

### **Quick Actions:**
**Tab-specific:**
- Campaigns Tab: "Create Campaign", "Export"
- Products Tab: "Fix Feed Issues" → jumps to Feed Quality tab
- Feed Quality Tab: "Open Merchant Center" (external)
- Recommendations Tab: "Apply All Low Risk"

---

## 🔨 IMPLEMENTATION PLAN

### **Day 1 (10-12 hours today):**

**Chat 21a: Bootstrap Setup (2 hrs)**
- [ ] Add Bootstrap 5.3 CDN to new base template
- [ ] Add Bootstrap Icons 1.11 CDN
- [ ] Create `templates/base_bootstrap.html`
- [ ] Build dark sidebar with navigation
- [ ] Build top navbar (client selector, date picker, user menu)
- [ ] Create `static/css/custom.css` for overrides
- [ ] Test responsive collapse behavior
- [ ] Create reusable components:
  - `templates/components/sidebar.html`
  - `templates/components/navbar.html`

**Chat 21b: Main Dashboard (3 hrs)**
- [ ] Create `templates/dashboard_new.html`
- [ ] Build metrics bar component (`components/metrics_bar.html`)
- [ ] Performance trend chart (Chart.js)
- [ ] Top 5 campaigns card + table
- [ ] Pending recommendations widget
- [ ] Recent changes feed
- [ ] Account health card
- [ ] Quick action buttons
- [ ] Update `routes/dashboard.py` to use new template

**Chat 21c: Campaigns View (2 hrs)**
- [ ] Create `routes/campaigns.py` (NEW blueprint)
- [ ] Create `templates/campaigns.html`
- [ ] Load campaign data from DuckDB
- [ ] Build campaigns table with all 13 columns
- [ ] Add status & type badges
- [ ] Add sortable headers (JS)
- [ ] Add pagination (10/25/50/100)
- [ ] Add checkbox bulk select
- [ ] Campaign type pie chart
- [ ] Budget utilization bar chart
- [ ] Register blueprint in `app.py`

**Chat 21d: Keywords View (3 hrs)**
- [ ] Create `templates/keywords_new.html`
- [ ] Redesign table with 15 columns
- [ ] Match type pills (Exact/Phrase/Broad)
- [ ] Quality score color coding
- [ ] Expandable QS sub-columns (LP, Ad Rel, CTR)
- [ ] AI insight badges with tooltips
- [ ] Add search terms collapsible section
- [ ] Search terms table (10 columns)
- [ ] QS distribution histogram
- [ ] Low data keywords card
- [ ] Wasted spend card
- [ ] Update `routes/keywords.py` to use new template

**END OF DAY 1 (if 10 hours): 4 pages complete**
- Main Dashboard ✅
- Campaigns ✅
- Keywords ✅
- Bootstrap foundation ✅

**Remaining for Day 2:**
- Ad Groups (2 hrs)
- Ads (2 hrs)
- Shopping (3 hrs)
- AI Insights Integration (2 hrs)
- Polish (1 hr)

---

### **Day 2 (8 hours):**

**Chat 21e: Ad Groups View (2 hrs)**
- [ ] Create `routes/ad_groups.py` (NEW blueprint)
- [ ] Create `templates/ad_groups.html`
- [ ] Load ad group data from DuckDB
- [ ] Build table with 12 columns
- [ ] Quality score color coding
- [ ] AI insight badges
- [ ] QS distribution chart
- [ ] Top/Bottom 5 ad groups cards
- [ ] Inline CPC editing (optional)
- [ ] Pagination
- [ ] Register blueprint in `app.py`

**Chat 21f: Ads View (2 hrs)**
- [ ] Create `templates/ads_new.html`
- [ ] Redesign table with 13 columns
- [ ] Ad type badges (RSA/ETA)
- [ ] Ad strength progress bars
- [ ] Build preview modal (large modal)
  - Google Ads preview styling
  - Headline/description lists
  - Performance metrics sidebar
  - Ad strength breakdown
- [ ] Asset performance expandable row detail
  - 3 cards: Headlines, Descriptions, Strength
- [ ] Ad strength distribution pie chart
- [ ] Ad type breakdown pie chart
- [ ] Update `routes/ads.py` to use new template

**Chat 21g: Shopping View (3 hrs)**
- [ ] Create `templates/shopping_new.html`
- [ ] Bootstrap tabs component (4 tabs)
- [ ] Tab 1: Campaigns table (13 columns, ROAS color coding)
- [ ] Tab 2: Products table (15 columns, images, feed quality bars)
- [ ] Tab 3: Feed Quality
  - 4 metric cards
  - Issues table with expandable reasons
- [ ] Tab 4: Recommendations table
- [ ] Update `routes/shopping.py` to use new template

**Chat 21h: Charts & Polish (1 hr)**
- [ ] Standardize Chart.js colors (Bootstrap palette)
- [ ] Add loading spinners for tables
- [ ] Fix any responsive issues
- [ ] Test all pagination
- [ ] Test all modals
- [ ] Cross-browser check (Chrome, Firefox, Edge)
- [ ] Fix any bugs found

**END OF DAY 2: All 8 pages complete**

---

### **Day 3 (Optional - if needed):**

**Final Polish & Testing (2-4 hrs)**
- [ ] Performance optimization
- [ ] Accessibility check (ARIA labels)
- [ ] Final responsive testing
- [ ] User acceptance testing
- [ ] Bug fixes
- [ ] Documentation updates

---

## 📁 COMPLETE FILE STRUCTURE

### **New Files:**
```
act_dashboard/
├── static/
│   ├── css/
│   │   └── custom.css                    # Custom Bootstrap overrides
│   └── js/
│       ├── tables.js                     # Sorting, filtering, pagination
│       ├── charts.js                     # Chart.js configurations
│       └── dashboard.js                  # General utilities
├── templates/
│   ├── base_bootstrap.html               # NEW Bootstrap base template
│   ├── components/
│   │   ├── sidebar.html                  # Reusable sidebar navigation
│   │   ├── navbar.html                   # Reusable top navbar
│   │   ├── metrics_bar.html              # Reusable metrics bar
│   │   ├── pagination.html               # Reusable pagination component
│   │   └── rec_sidebar.html              # AI recommendations sidebar
│   ├── dashboard_new.html                # Redesigned main dashboard
│   ├── campaigns.html                    # NEW - Campaigns page
│   ├── ad_groups.html                    # NEW - Ad Groups page
│   ├── keywords_new.html                 # Redesigned keywords
│   ├── ads_new.html                      # Redesigned ads
│   └── shopping_new.html                 # Redesigned shopping
└── routes/
    ├── campaigns.py                      # NEW - Campaigns blueprint
    └── ad_groups.py                      # NEW - Ad Groups blueprint
```

### **Modified Files:**
```
act_dashboard/routes/
├── dashboard.py        # Update to use dashboard_new.html
├── keywords.py         # Update to use keywords_new.html
├── ads.py             # Update to use ads_new.html
└── shopping.py        # Update to use shopping_new.html

act_dashboard/
└── app.py             # Register new blueprints (campaigns, ad_groups)
```

---

## 🎨 REUSABLE COMPONENTS LIBRARY

### **1. Metrics Card**
```html
<div class="col-md-2">
  <div class="card metric-card">
    <div class="card-body text-center">
      <h3 class="metric-value">1,234</h3>
      <p class="metric-label text-muted">Clicks</p>
      <span class="metric-change text-success">
        <i class="bi bi-arrow-up"></i> +12%
      </span>
    </div>
  </div>
</div>
```

### **2. Data Table with Pagination**
```html
<div class="table-responsive">
  <table class="table table-hover table-striped">
    <thead class="table-light">
      <tr>
        <th><input type="checkbox" class="select-all"></th>
        <th class="sortable" data-sort="name">Campaign <i class="bi bi-arrow-down-up"></i></th>
        <th class="sortable" data-sort="clicks">Clicks <i class="bi bi-arrow-down-up"></i></th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      <!-- Rows populated by backend -->
    </tbody>
  </table>
</div>

<!-- Pagination Component -->
<nav>
  <div class="d-flex justify-content-between align-items-center">
    <div class="text-muted">Showing 1-25 of 156</div>
    <div class="btn-group">
      <button class="btn btn-sm btn-outline-secondary active">25</button>
      <button class="btn btn-sm btn-outline-secondary">50</button>
      <button class="btn btn-sm btn-outline-secondary">100</button>
    </div>
    <ul class="pagination mb-0">
      <li class="page-item disabled"><a class="page-link" href="#">Previous</a></li>
      <li class="page-item active"><a class="page-link" href="#">1</a></li>
      <li class="page-item"><a class="page-link" href="#">2</a></li>
      <li class="page-item"><a class="page-link" href="#">3</a></li>
      <li class="page-item"><a class="page-link" href="#">Next</a></li>
    </ul>
  </div>
</nav>
```

### **3. Status Badge**
```html
<span class="badge bg-success">Active</span>
<span class="badge bg-secondary">Paused</span>
<span class="badge bg-danger">Removed</span>
```

### **4. AI Insight Badge with Tooltip**
```html
<span class="badge bg-warning ai-insight" 
      data-bs-toggle="tooltip" 
      data-bs-placement="top"
      title="KW-PAUSE-001: High cost, zero conversions">
  <i class="bi bi-lightbulb"></i>
</span>
```

### **5. Progress Bar (Ad Strength)**
```html
<!-- Poor -->
<div class="progress" style="height: 20px;">
  <div class="progress-bar bg-danger" style="width: 25%">Poor</div>
</div>

<!-- Good -->
<div class="progress" style="height: 20px;">
  <div class="progress-bar bg-success" style="width: 75%">Good</div>
</div>
```

### **6. Modal Template**
```html
<div class="modal fade" id="adPreviewModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Ad Preview - ID: 123456</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <!-- Content -->
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
        <a href="#" class="btn btn-primary" target="_blank">Edit in Google Ads</a>
      </div>
    </div>
  </div>
</div>
```

---

## 🧪 TESTING CHECKLIST

### **Functional Testing:**
- [ ] All pages load without errors
- [ ] All links navigate correctly
- [ ] Tables sort correctly (asc/desc)
- [ ] Pagination works (10/25/50/100)
- [ ] Filters apply correctly
- [ ] Date picker updates metrics
- [ ] Charts render with correct data
- [ ] Modals open/close properly
- [ ] Tooltips appear on hover
- [ ] Forms submit correctly
- [ ] Bulk actions work when rows selected
- [ ] Search functionality works

### **Visual Testing:**
- [ ] Consistent spacing throughout
- [ ] Text alignment correct
- [ ] Colors match design system
- [ ] Icons display correctly
- [ ] Progress bars render properly
- [ ] Badges use correct colors
- [ ] No layout shifts on load
- [ ] Text is readable (good contrast)

### **Responsive Testing:**
- [ ] Desktop 1920x1080 (primary target)
- [ ] Laptop 1366x768
- [ ] Tablet 768x1024 (iPad)
- [ ] Mobile 375x667 (iPhone)
- [ ] Sidebar collapses on mobile (<768px)
- [ ] Tables scroll horizontally on mobile
- [ ] Metrics bar stacks vertically on mobile
- [ ] Cards stack properly on smaller screens

### **Performance Testing:**
- [ ] Initial page load <2 seconds
- [ ] Table render <500ms (for 100 rows)
- [ ] Chart render <1 second
- [ ] No console errors
- [ ] No JavaScript errors
- [ ] Smooth scrolling
- [ ] Tooltips don't lag

### **Cross-Browser Testing:**
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Edge (latest)
- [ ] Safari (if on Mac)

---

## 🚀 LAUNCH CHECKLIST

**Before Merging to Main:**
- [ ] All functional tests passing
- [ ] All visual tests passing
- [ ] All responsive tests passing
- [ ] All performance tests passing
- [ ] No console errors or warnings
- [ ] All tooltips working
- [ ] All modals working
- [ ] All charts rendering
- [ ] All images loading
- [ ] All links working (no 404s)
- [ ] Git commits are clean and descriptive
- [ ] PROJECT_ROADMAP.md updated

**Git Commits Strategy:**
- After Chat 21a: "Bootstrap setup complete"
- After Chat 21b: "Main dashboard redesign complete"
- After Chat 21c: "Campaigns page complete"
- After Chat 21d: "Keywords page redesign complete"
- After Chat 21e: "Ad Groups page complete"
- After Chat 21f: "Ads page redesign complete"
- After Chat 21g: "Shopping page redesign complete"
- After Chat 21h: "Dashboard UI overhaul complete - all pages"

**Post-Launch:**
- [ ] Monitor error logs for issues
- [ ] Watch for user feedback
- [ ] Track page load performance
- [ ] Fix any bugs immediately
- [ ] Plan Phase 2 improvements

---

## 📊 PROGRESS TRACKING

**Daily Checklist:**

**Day 1:**
- [x] Chat 21a: Bootstrap Setup (50 min actual vs 2 hrs estimated) ✅
- [x] Chat 21b: Main Dashboard (53 min actual vs 3 hrs estimated) ✅
- [x] Chat 21c: Campaigns View (100 min actual vs 2 hrs estimated) ✅
- [x] Chat 21d: Keywords View (125 min actual vs 70 min estimated) ✅
**Progress: 4/4 Day 1 tasks complete | Finished 9:35 PM**

**Day 2 (Early Morning / Afternoon):**
- [x] Chat 21e: Ad Groups View (120 min actual vs 70 min estimated) ✅
- [x] Chat 21f: Ads View (~180 min actual vs 70 min estimated) ✅
- [ ] Chat 21g: Shopping View (est. 90 min)
- [ ] Chat 21h: Polish & Charts (est. 60 min)
**Progress: 2/4 Day 2 tasks complete | Next: Chat 21g**

**Day 3 (if needed):**
- [ ] Bug fixes
- [ ] Performance optimization
- [ ] Final testing
**Total: 2-4 hours | Polish & QA**

---

## 📝 CRITICAL NOTES

### **DuckDB Queries Needed:**

**For Campaigns page:**
```sql
SELECT campaign_id, campaign_name, status, campaign_type, budget,
       SUM(cost_micros)/1000000 as spend_7d,
       SUM(clicks) as clicks, SUM(impressions) as impressions,
       SUM(conversions) as conversions
FROM analytics.campaign_daily
WHERE customer_id = ? AND snapshot_date >= CURRENT_DATE - 7
GROUP BY campaign_id, campaign_name, status, campaign_type, budget
ORDER BY spend_7d DESC
```

**For Ad Groups page:**
```sql
SELECT ad_group_id, ad_group_name, campaign_name, status, max_cpc,
       AVG(quality_score) as avg_qs,
       SUM(clicks) as clicks, SUM(conversions) as conversions,
       SUM(cost_micros)/1000000 as cost
FROM analytics.ad_group_features_daily
WHERE customer_id = ? AND snapshot_date = ?
GROUP BY ad_group_id, ad_group_name, campaign_name, status, max_cpc
ORDER BY cost DESC
```

(Keywords, Ads, Shopping queries already exist in current routes - will reuse)

### **JavaScript Libraries Required:**
- Bootstrap 5.3 (CSS + JS bundle)
- Bootstrap Icons 1.11
- Chart.js 4.4 (for charts)
- NO jQuery needed (Bootstrap 5 doesn't require it)

### **Custom CSS Priorities:**
1. Sidebar styling (dark theme)
2. Metrics cards spacing
3. Table row hover effects
4. Badge custom sizes
5. Progress bar custom heights
6. Modal content layouts

---

## 📊 CURRENT PROGRESS (as of Feb 18, 6:15 PM)

**Completed:** 3/8 chats (37.5%)
- ✅ Chat 21a: Bootstrap foundation (50 min)
- ✅ Chat 21b: Main dashboard with real data (53 min)
- ✅ Chat 21c: Campaigns page + rule system (100 min)

**Stats:**
- Files created: 14 new, 4 modified
- Lines of code: 3,166 (production-ready)
- Time invested: ~3.5 hours actual work (~5.5 hours elapsed)
- Commits: 3 (5789628, 4976a29, pending for 21c)

**Next:** Chat 21d (Keywords) starting ~6:30 PM

---

**Plan Created:** 2026-02-18 02:45 AM  
**Last Updated:** 2026-02-18 06:15 PM  
**Status:** IN PROGRESS 🔥  
**Status:** READY TO START  
**Estimated Completion:** 2 days (20 hours)  
**Next Step:** Chat 21a - Bootstrap Setup
