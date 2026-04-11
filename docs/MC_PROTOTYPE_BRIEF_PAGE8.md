# MC ACT Prototype — Page 8: Shopping Level
**Session:** MC ACT Prototype (continued)
**Date:** 2026-04-11
**Objective:** Build the final level page — Shopping Level. This is where ACT manages product performance, search term mining for Shopping campaigns, tier-based optimization, and product group bid management.

---

## IMPORTANT: FOLLOW EXISTING STANDARDS

Read `docs/ACT_PROTOTYPE_STANDARDS.md` before starting. All patterns from Pages 1-7 must be followed exactly.

Key standards:
- Level Page Structure (hybrid: data table + ACT intelligence)
- Combined Chart + Table Section pattern
- Performance Timeline Chart pattern (dual axes, straight lines, metric dropdowns, no vertical gridlines, no fill)
- Table Alignment: all left-aligned
- No all-caps
- v54 colour system (Shopping level colour = teal #14b8a6)
- Slide-in detail pattern (800px)
- Word-for-word text consistency between main page and slide-in
- Rows per page dropdown (10/20/50/100/200)
- Plain text for metadata columns
- Standard 8 metric columns: Cost, Impr., Clicks, Avg CPC, CTR, Conv., Cost/Conv, Conv Rate
- For Shopping, also add: ROAS, AOV, Conv. Value

---

## Context

Read the Shopping Level section in `docs/ACT_OPTIMIZATION_ARCHITECTURE_v54.html` — source of truth.

Key points from v54 for Shopping Level:

**Standard Shopping ONLY — no PMax** (PMax is handled elsewhere)

**4 independent checks:**
1. **Shopping Search Term Mining** — same 9-list negative keyword structure, auto-add [exact] match negatives (AUTO-EXECUTE)
2. **Product Performance Tiers** — categorise products into Best Sellers (top 20%), Mid-Range, Underperformers, Losers. Based on multi-window weighted blend (7d 50%, 14d 30%, 30d 20%)
3. **Product Exclusion Recommendations** — zero converters + low ROAS, all approval-based (APPROVAL)
4. **Best Seller Budget Maximisation** — raise bids on top performers, check IS lost to budget (AUTO-EXECUTE with guardrails)

**Plus: Product Group Bid Management**
- 10% per cycle
- 72hr cooldown
- 30% 7-day cap
- Configurable spend threshold (default £50)
- Tier percentages editable per client

**Persona:** Ecommerce (ROAS-focused, not CPA)

**8 guardrails** at shopping level.

---

## IMPORTANT: New Sample Client for Shopping

The existing sample client (Objection Experts) is a Lead Gen CPA client with no products. Shopping Level requires an Ecommerce ROAS client with products.

Use a new sample client: **"Dental Supplies Direct"** (fictional ecommerce dental supply store selling to dental practices).

- Persona: Ecommerce ROAS
- Target ROAS: 4.0x (£4 revenue per £1 spend)
- Monthly budget: £5,000
- Campaign structure: Shopping campaigns by product category
- Product feed: ~200 products across categories: Implants, Instruments, Consumables, Whitening, Hygiene, Restoration Materials

The client switcher in the top bar should still show "Objection Experts" as the active client (since that's what every other prototype page uses), but the Shopping Level page content should use "Dental Supplies Direct" sample data. This is a prototype nuance — in the real build, the Shopping Level page would be blank or show "No shopping campaigns" for clients without products.

Alternatively, you can add "Dental Supplies Direct" as an option in the client switcher dropdown and switch to it for this page. Either approach works — your call.

---

## Page Structure

Follow the same hybrid structure as previous level pages.

### Main Page:

1. **Page header** — teal (#14b8a6) level accent, title "Shopping Level", subtitle "Product Performance, Search Terms & Exclusions"
2. **Health summary cards** — 4 cards
3. **Product Performance (combined section)** — summary metric cards + timeline chart + products data table
4. **Shopping-Level Review sections** — Awaiting Approval, Actions Executed, Currently Monitoring, Recent Alerts
5. **Guardrails** — shopping level guardrails

### Slide-in Panel (800px) — opens when clicking a product:

1. **Product header** — product name, brand, SKU, category, status, current tier badge
2. **Health cards** — 4 cards (Cost, ROAS with zone badge, Conv Value, Avg Order Value)
3. **Awaiting Approval** (expanded) — this product's flags
4. **Actions Executed Overnight** (collapsed)
5. **Currently Monitoring** (collapsed)
6. **Recent Alerts** (collapsed)
7. **Performance Tier Breakdown** (collapsed) — shows the 7d/14d/30d weighted blend and which tier this product sits in
8. **Product Group Bid History** (collapsed) — last 10 bid changes at the product group level
9. **Product Feed Details** (collapsed) — title, description, image URL, price, availability, merchant ID

All sections collapsible. Only Awaiting Approval expanded by default.

---

## Section Details

### Health Summary Cards (Main Page)

| Card | Content |
|------|---------|
| Total Products | 204 (in feed) |
| Avg ROAS | 4.2x (Target: 4.0x — On Target) |
| Best Sellers | 41 products (top 20%) |
| Flagged Products | 18 (exclusion candidates, low ROAS) |

### Product Performance Combined Section (Main Page)

**Header:** "Product Performance — 204 products, 30 days" with date range pills and filters:
- All / Enabled / Paused / Excluded
- Tier filter: All / Best Seller / Mid-Range / Underperformer / Loser

**Summary metric cards:** Cost, Impr, Clicks, Avg CPC, Conv, Cost/Conv, Conv Rate, ROAS

**Timeline chart:** Dual axis, metric dropdowns, straight lines, no vertical gridlines, no fill.
Metric options for Shopping: Cost, Impressions, Clicks, Avg CPC, CTR, Conversions, Cost/Conv, Conv Rate, ROAS, AOV, Conv. Value.
Default: Cost + ROAS (since ROAS is the primary ecommerce metric)
Metric 1 colour: teal #14b8a6 (shopping level). Metric 2: green #10b981.

**Data table — Products:**

Columns:
- Status (dot)
- Product name (clickable → opens slide-in)
- SKU (plain text)
- Category (plain text)
- Tier (coloured badge: Best Seller=green, Mid-Range=blue, Underperformer=amber, Loser=red)
- Cost
- Impressions (Impr.)
- Clicks
- Avg CPC
- Conversions (Conv.)
- Conv. Value
- ROAS (coloured by performance: green if ≥target, amber if 80-100% of target, red if <80%)
- Flag badges

Sortable, left-aligned, totals/averages row at bottom, rows per page dropdown (10/20/50/100/200).

### Sample Data (20 products shown, 204 total)

Create realistic dental supply product data. Mix of:

**Best Sellers (4 in the visible 20):**
- "Premium Implant Kit — Titanium" (ROAS 6.2x, £450 AOV, healthy)
- "Dental Curing Light UV" (ROAS 5.8x, £125 AOV, healthy)
- "Professional Whitening Gel — 10 pack" (ROAS 5.5x, £85 AOV, healthy)
- "Dental Composite Shade Kit" (ROAS 5.2x, £220 AOV, healthy)

**Mid-Range (8 in the visible 20):**
- "Dental Handpiece — Standard" (ROAS 4.1x)
- "Impression Material 500ml" (ROAS 3.9x)
- "Dental Burs Set — 10 piece" (ROAS 4.3x)
- "Anaesthetic Cartridges 50pk" (ROAS 4.0x)
- "Dental Cement — Zinc Phosphate" (ROAS 3.8x)
- "Disposable Bib 500pk" (ROAS 4.2x)
- "Sterilisation Pouches 200pk" (ROAS 4.1x)
- "Dental Mirror Pack 12" (ROAS 3.9x)

**Underperformers (5 in the visible 20):**
- "Premium Dental Loupes 2.5x" (ROAS 2.8x, flagged)
- "Ultrasonic Scaler Cartridge" (ROAS 2.5x, flagged)
- "Dental Chair Covers 100pk" (ROAS 2.2x, flagged)
- "Specialty Restoration Kit" (ROAS 2.4x, flagged)
- "Digital X-Ray Sensor Cover" (ROAS 2.6x, flagged)

**Losers (3 in the visible 20):**
- "Obscure Dental Tool Set" (ROAS 0.8x, zero conversions 30+ days, exclusion candidate — flagged)
- "Limited Edition Whitening Kit" (ROAS 0.5x, low inventory, exclusion candidate — flagged)
- "Discontinued Implant Model X" (ROAS 0.0x, 0 conversions 45 days — flagged for exclusion)

Use realistic metrics — Shopping typically has lower CPCs than Search (£0.30-£2.50), higher volumes, and varying conversion rates by product.

### Shopping-Level Review Sections (Main Page)

**Awaiting Approval (5 items):**

1. **Product Exclusion — Zero Converter** (MEDIUM RISK)
   - "Exclude 'Discontinued Implant Model X' — 0 conversions in 45 days, £62 spend"
   - ACT recommends: "Exclude this product from Shopping — discontinued model with zero conversions"
   - Flag: Exclusion Candidate

2. **Product Exclusion — Low ROAS** (MEDIUM RISK)
   - "Exclude 'Obscure Dental Tool Set' — ROAS 0.8x over 30 days, well below target 4.0x"
   - ACT recommends: "Exclude this product — persistent low ROAS with no improvement trend"
   - Flag: Exclusion Candidate

3. **Best Seller Budget Opportunity** (LOW RISK)
   - "Increase bids on 'Premium Implant Kit — Titanium' — ROAS 6.2x, losing 42% IS to budget"
   - ACT recommends: "Raise bid by 15% to capture more of the 42% lost impression share (best seller candidate)"
   - Flag: Budget Opportunity

4. **Keyword Discovery — Search Term Mining** (LOW RISK)
   - "Add 'titanium dental implants bulk' as phrase match keyword — discovered from search terms with 12 conversions at 5.8x ROAS"
   - ACT recommends: "Add to main Shopping campaign as phrase match"
   - Flag: Keyword Discovery

5. **Tier Demotion — Mid to Underperformer** (MEDIUM RISK)
   - "'Premium Dental Loupes 2.5x' dropping from Mid-Range to Underperformer tier. ROAS declined from 3.8x to 2.8x over 14 days."
   - ACT recommends: "Reduce product group bid by 10% while trend reverses or investigate feed issues"
   - Flag: Tier Demotion

**Actions Executed Overnight (8 items):**

1. Added "cheap dental tools ebay" to negative keyword list "4 WORDS [exact]" — search term mining, ecommerce competitor
2. Added "free dental samples" to negative keyword list "3 WORDS [exact]" — search term mining, irrelevant intent
3. Added "dental school" to negative keyword list "2 WORDS [exact]" — wrong audience
4. Increased bid on "Dental Curing Light UV" from £0.85 to £0.94 (+10%) — ROAS 5.8x, 72hr cooldown
5. Increased bid on "Professional Whitening Gel — 10 pack" from £0.60 to £0.66 (+10%) — ROAS 5.5x, 72hr cooldown
6. Reduced bid on "Specialty Restoration Kit" from £1.20 to £1.08 (-10%) — ROAS 2.4x below target, 72hr cooldown
7. Added "dental tools wholesale" to negative keyword list "3 WORDS [exact]" — B2B intent
8. Promoted "Dental Composite Shade Kit" from Mid-Range to Best Seller tier — ROAS improved to 5.2x over 14 days

**Currently Monitoring (3 items):**

1. Bid cooldown: "Dental Curing Light UV" increased from £0.85 to £0.94. 66h remaining of 72h cooldown. Healthy.
2. Bid cooldown: "Specialty Restoration Kit" reduced from £1.20 to £1.08. 66h remaining of 72h cooldown. Trending up (ROAS improving).
3. Tier watch: "Premium Dental Loupes 2.5x" approaching Underperformer tier. ROAS 2.8x, 3 days monitoring before final demotion.

**Recent Alerts (2 items):**

1. "Feed quality alert: 12 products missing GTIN. Potential disapproval risk. Flagged 3 Apr. Under review."
2. "Merchant Centre sync issue: 3 products not updating. Flagged 5 Apr. Resolved."

### Slide-in Detail (4 unique variants)

1. **"Discontinued Implant Model X"** (Exclusion Candidate — Medium Risk) — default on load
2. **"Premium Implant Kit — Titanium"** (Budget Opportunity / Best Seller — Low Risk)
3. **"Premium Dental Loupes 2.5x"** (Tier Demotion — Medium Risk)
4. **"Dental Composite Shade Kit"** (Promoted to Best Seller — Low Risk, shown in Actions Executed context)

Other products show a generic default slide-in.

**Example: "Discontinued Implant Model X" slide-in:**

- **Header**: "Discontinued Implant Model X" · SKU: DIS-IMP-X01 · Category: Implants · Enabled · Loser tier (red)
- **Health cards**:
  - Cost (MTD): £62
  - ROAS: 0.0x (red "No conversions in 45 days · Loser" zone badge)
  - Conv Value: £0
  - AOV: —
- **Awaiting Approval** (expanded):
  - Badges: Shopping · Investigate · Medium Risk · Exclusion Candidate · Identified 4 hours ago · Impact: £62/month saved
  - Summary: "Exclude this product — 0 conversions in 45 days, £62 spend. Discontinued model."
  - ACT recommends: "Exclude this product from Shopping campaigns to reallocate budget to converting products"
  - Cooldown: "No cooldown — exclusion action"
- **Performance Tier Breakdown** (collapsed):
  - 7d ROAS: 0.0x (weight 50%)
  - 14d ROAS: 0.0x (weight 30%)
  - 30d ROAS: 0.1x (weight 20%)
  - Weighted score: 0.02x
  - Current tier: Loser
- **Product Group Bid History** (collapsed): last 10 bid changes at the product group level this product belongs to
- **Product Feed Details** (collapsed):
  - Title: "Discontinued Implant Model X — Titanium 4.5mm"
  - Description: "Legacy titanium implant — stock clearance"
  - Price: £89.00
  - Availability: Limited stock
  - GTIN: present
  - Brand: Inserta
  - Merchant ID: XYZ123

### Performance Tier Breakdown Component

Shows the multi-window weighted blend calculation:

```
Performance Tier Breakdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7-day ROAS:   X.Xx   (weight 50%) → X.X points
14-day ROAS:  X.Xx   (weight 30%) → X.X points
30-day ROAS:  X.Xx   (weight 20%) → X.X points

Weighted score: X.Xx
Current tier: Best Seller / Mid-Range / Underperformer / Loser

Tier thresholds:
  Best Seller (top 20%):    ROAS ≥ 5.0x
  Mid-Range (60%):          ROAS 3.0x – 5.0x
  Underperformer (15%):     ROAS 1.5x – 3.0x
  Loser (bottom 5%):        ROAS < 1.5x
```

Display as a clean breakdown with visual indicator of which tier the product sits in.

### Product Feed Details Component

Simple list/table showing product feed data:
- Title
- Description (truncated, expandable)
- Image URL or thumbnail
- Price
- Sale price (if applicable)
- Availability (In stock / Out of stock / Limited / Preorder)
- GTIN (present / missing)
- Brand
- Merchant ID
- Last sync: date

### Guardrails (Main Page)

From v54 Shopping Level:
- Product spend threshold: £50 (configurable)
- Product group bid adjustment per cycle: 10%
- Product group bid cooldown: 72 hours
- Product group bid 7-day cap: 30%
- Best Seller tier: top 20% by ROAS
- Mid-Range tier: 60% by ROAS
- Underperformer tier: 15% by ROAS
- Loser tier: bottom 5% by ROAS (exclusion candidates)
- Multi-window blend: 7d 50%, 14d 30%, 30d 20%

Ordered logically.

---

## Interactive Behaviours

1. **Product name click** — opens slide-in
2. **Flag badge click** — opens slide-in
3. **See Details on main page** — inline expand (NOT slide-in)
4. **See Details in slide-in** — inline expand with Hide Details toggle
5. **Chart date range** — controls both chart and table
6. **Table sort and filters** — standard + tier filter
7. **Tier badges** — coloured by tier
8. **ROAS cell** — coloured by performance vs target
9. **Performance Tier Breakdown expand** — shows weighted calculation
10. **Product Feed Details expand** — shows feed data

---

## Key Differences from Other Level Pages

- **Ecommerce persona** — ROAS-focused, not CPA (first time we're building for this persona)
- **Product-based not keyword/ad-based** — the table rows are products
- **Tier system** — unique to Shopping, 4 tiers with different actions
- **Product Feed Details section** — unique to Shopping, shows product feed data
- **Performance Tier Breakdown section** — unique to Shopping, shows weighted blend
- **Auto-execution exists** — search term mining, bid adjustments, tier promotions
- **New sample client** — Dental Supplies Direct (ecommerce) instead of Objection Experts (lead gen)
- **Conv. Value and AOV metrics** — unique to ecommerce
- **"Excluded" status filter** — unique to Shopping (products can be excluded from feeds)

---

## Browser Verification

1. Test product name click → slide-in opens
2. Test 4 unique slide-in variants
3. Test tier filter (All / Best Seller / Mid-Range / Underperformer / Loser)
4. Test Performance Tier Breakdown expand
5. Test Product Feed Details expand
6. Test chart with ROAS metric
7. Test rows per page dropdown
8. Check dark mode
9. Save screenshots

---

## Deliverables

1. `act_dashboard/prototypes/shopping-level.html`
2. Updated `docs/ACT_PROTOTYPE_STANDARDS.md` with new patterns (tier badges, Performance Tier Breakdown, Product Feed Details, ROAS colouring, ecommerce persona handling)
3. Screenshots

---

**END OF BRIEF**
