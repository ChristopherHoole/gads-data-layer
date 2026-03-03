# METRICS CARDS FINAL SPECIFICATIONS

**Module:** Dashboard Design Upgrade - Module 2 (Metrics Cards)  
**Created:** 2026-02-28  
**Status:** APPROVED - Ready for implementation  
**Wireframe:** dashboard_wireframe_v8.html

---

## OVERVIEW

Replace current metrics cards (colored backgrounds) with redesigned cards featuring:
- White backgrounds (#ffffff)
- Color-coded left borders (4px: green/blue/gray)
- Sentence case labels (no ALL CAPS)
- Interactive sparkline hover (dot follows mouse, tooltip shows value)
- Same grid layout as current implementation
- Max-width container (1600px, left-aligned)

---

## GRID LAYOUT

### Container
```css
.m2-wrapper {
    max-width: 1600px;
    margin-bottom: 24px;
}
```

### Row 1: Financial + Leads (9 columns)
```css
grid-template-columns: repeat(4, 1fr) 14px repeat(4, 1fr);
gap: 6px;
```

**Positions:**
1. Cost (Financial)
2. Revenue (Financial)
3. ROAS (Financial)
4. [Blank space]
5. **[Vertical divider - 14px column]**
6. Conversions (Leads)
7. Cost / conv (Leads)
8. Conv rate (Leads)
9. [Blank space]

### Row 2: Actions Metrics (9 columns)
Same grid structure: `repeat(4, 1fr) 14px repeat(4, 1fr)`

**Positions:**
1. Impressions
2. Clicks
3. Avg CPC
4. Avg CTR
5. **[Hidden divider]**
6. Search impr share
7. Search top IS
8. Search abs top IS
9. Click share

### Section Labels
Grid above cards: `grid-template-columns: repeat(4, 1fr) 14px repeat(4, 1fr)`

**Labels:**
- "Financial" above positions 1-4
- "Leads" above positions 6-9 (aligned with Conversions card)

---

## METRIC CARD SPECIFICATIONS

### Card Dimensions
```css
min-height: 90px;
padding: 8px 10px;
border-radius: 8px;
background: #ffffff;
border-left: 4px solid [color];
```

### Border Colors by Category

**Financial (Green):**
- Border: `#34a853`
- Cards: Cost, Revenue, ROAS

**Leads (Blue):**
- Border: `#1a73e8`
- Cards: Conversions, Cost/conv, Conv rate

**Actions (Gray):**
- Border: `#5f6368`
- Cards: All 8 Actions metrics

### Card Structure
```html
<div class="m2-card m2-card-[category]">
  <div class="m2-card-inner">
    <div class="m2-card-label">[Label]</div>
    <div class="m2-card-value">[Value]</div>
    <div class="m2-card-change">
      <span class="m2-change-[color]">[Arrow] [%]</span>
    </div>
  </div>
  <div class="m2-sparkline-wrap">
    <svg class="m2-sparkline" viewBox="0 0 100 30">
      <polyline points="[...]" fill="none" stroke="[color]" stroke-width="2"/>
      <circle class="sparkline-dot" cx="50" cy="15"/>
    </svg>
    <div class="sparkline-tooltip">[Date]: [Value]</div>
  </div>
</div>
```

---

## TEXT SPECIFICATIONS

### Labels
```css
font-size: 12px;
color: #5f6368;
font-weight: 500;
line-height: 1.2;
```
**Case:** Sentence case (e.g., "Cost", "Conv rate", "Search impr share")

### Values
```css
font-size: 28px;
font-weight: 600;
color: #202124;
line-height: 1;
margin-top: 4px;
```

### Change Indicators
```css
font-size: 13px;
font-weight: 500;
margin-top: 4px;
```

**Colors:**
- `.m2-change-green`: `#34a853` (positive changes for non-inverted metrics)
- `.m2-change-red`: `#ea4335` (negative changes for non-inverted metrics)
- `.m2-change-neutral`: `#5f6368` (zero change)

**Format:**
- Positive: `↑ +9.1%`
- Negative: `↓ 9.1%`
- Neutral: `→ 0%`

---

## SECTION LABELS

### Group Labels Row
```css
.m2-group-labels-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr) 14px repeat(4, 1fr);
    gap: 6px;
    margin-bottom: 8px;
}

.m2-group-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    color: #5f6368;
    padding-left: 2px;
}
```

### HTML Structure
```html
<div class="m2-group-labels-row">
    <div class="m2-group-label">Financial</div>
    <div></div><div></div><div></div>
    <div></div><!-- separator column -->
    <div></div><!-- push Leads to align with first card -->
    <div class="m2-group-label">Leads</div>
    <div></div><div></div>
</div>
```

---

## VERTICAL DIVIDER

### Separator Column
```css
.m2-separator {
    display: flex;
    align-items: center;
    justify-content: center;
}

.m2-separator::after {
    content: '';
    display: block;
    width: 1px;
    height: 100%;
    background: #dadce0;
    border-radius: 2px;
    min-height: 90px;
}
```

### Hidden Separator (Actions Row)
```css
.m2-separator-hidden::after {
    background: transparent;
}
```

**Usage:** Position 5 in both rows (14px grid column)

---

## BLANK SPACES

### Specifications
```css
.m2-card-blank {
    background: transparent;
    border: none;
    min-height: 90px;
}
```

**Positions:** 4 and 9 in Row 1

---

## SPARKLINE SPECIFICATIONS

### Wrapper
```css
.m2-sparkline-wrap {
    margin-top: 8px;
    position: relative;
    height: 32px;
}

.m2-sparkline {
    width: 100%;
    height: 100%;
    cursor: crosshair;
}
```

### SVG Structure
```html
<svg class="m2-sparkline" viewBox="0 0 100 30" preserveAspectRatio="none">
    <polyline points="[data points]" 
              fill="none" 
              stroke="[color]" 
              stroke-width="2"/>
    <circle class="sparkline-dot" cx="50" cy="15"/>
</svg>
```

### Interactive Dot
```css
.sparkline-dot {
    r: 6;
    fill: #1a73e8;
    opacity: 0;
    transition: opacity 150ms ease;
}

.m2-sparkline-wrap:hover .sparkline-dot {
    opacity: 1;
}
```

**Behavior:**
- Dot hidden by default
- Appears on hover
- Follows mouse position along sparkline
- Positioned at closest data point to cursor

### Tooltip
```css
.sparkline-tooltip {
    position: absolute;
    background: #202124;
    color: #ffffff;
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 11px;
    white-space: nowrap;
    pointer-events: none;
    opacity: 0;
    transition: opacity 150ms ease;
    z-index: 10;
    transform: translate(-50%, -100%);
}

.sparkline-tooltip.show {
    opacity: 1;
}
```

**Content Format:** `"Feb 24: [value]"`

**Examples:**
- `"Feb 24: $184.5k"`
- `"Feb 24: 18.7k"`
- `"Feb 24: 3.0%"`

---

## INTERACTIVE BEHAVIOR

### JavaScript Implementation
```javascript
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.m2-sparkline-wrap').forEach(sparkline => {
        const svg = sparkline.querySelector('.m2-sparkline');
        const dot = sparkline.querySelector('.sparkline-dot');
        const tooltip = sparkline.querySelector('.sparkline-tooltip');
        const polyline = sparkline.querySelector('polyline');
        
        if (!svg || !dot || !tooltip || !polyline) return;
        
        // Parse points from polyline
        const pointsStr = polyline.getAttribute('points');
        const points = pointsStr.split(' ').map(p => {
            const [x, y] = p.split(',').map(Number);
            return { x, y };
        });
        
        svg.addEventListener('mousemove', (e) => {
            const rect = svg.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const svgX = (mouseX / rect.width) * 100;
            
            // Find closest point
            let closestPoint = points[0];
            let minDist = Math.abs(points[0].x - svgX);
            
            points.forEach(point => {
                const dist = Math.abs(point.x - svgX);
                if (dist < minDist) {
                    minDist = dist;
                    closestPoint = point;
                }
            });
            
            // Move dot to closest point
            dot.setAttribute('cx', closestPoint.x);
            dot.setAttribute('cy', closestPoint.y);
            
            // Show and position tooltip
            tooltip.classList.add('show');
            const tooltipX = (closestPoint.x / 100) * rect.width;
            const tooltipY = (closestPoint.y / 30) * rect.height;
            tooltip.style.left = tooltipX + 'px';
            tooltip.style.top = tooltipY + 'px';
        });
        
        svg.addEventListener('mouseleave', () => {
            tooltip.classList.remove('show');
            const centerPoint = points[Math.floor(points.length / 2)];
            dot.setAttribute('cx', centerPoint.x);
            dot.setAttribute('cy', centerPoint.y);
        });
    });
});
```

---

## COLLAPSIBLE ACTIONS SECTION

### Toggle Pill
```css
.m2-toggle-divider {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: flex-start; /* LEFT-ALIGNED */
    margin: 16px 0 12px 0;
    cursor: pointer;
    user-select: none;
}

.m2-toggle-divider::before {
    content: '';
    position: absolute;
    left: 0;
    right: 0;
    top: 50%;
    height: 1px;
    background: #dadce0;
}

.m2-toggle-pill {
    position: relative;
    background: #fff;
    border: 1px solid #dadce0;
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 11px;
    color: #5f6368;
    font-weight: 600;
    white-space: nowrap;
    transition: border-color 0.15s, color 0.15s;
}

.m2-toggle-divider:hover .m2-toggle-pill {
    border-color: #5f6368;
    color: #202124;
}
```

### HTML Structure
```html
<div class="m2-toggle-divider" onclick="toggleActions()">
    <div class="m2-toggle-pill" id="toggle-pill">▼ Actions metrics</div>
</div>

<div class="m2-cards-row" id="actions-row">
    <!-- 8 Actions metric cards -->
</div>
```

### Toggle Function
```javascript
function toggleActions() {
    const actionsRow = document.getElementById('actions-row');
    const pill = document.getElementById('toggle-pill');
    
    if (actionsRow.style.display === 'none') {
        actionsRow.style.display = '';
        pill.textContent = '▼ Actions metrics';
    } else {
        actionsRow.style.display = 'none';
        pill.textContent = '▶ Actions metrics';
    }
}
```

---

## METRIC DEFINITIONS

### Dashboard Page (14 total cards)

**Financial (3):**
1. Cost - `$184.5k` - Inverted colors (↓ is good)
2. Revenue - `$580.8k` - Normal colors (↑ is good)
3. ROAS - `3.15x` - Normal colors (↑ is good)

**Leads (3):**
6. Conversions - `18.7k` - Normal colors
7. Cost / conv - `$9.86` - Inverted colors
8. Conv rate - `3.0%` - Normal colors

**Actions (8):**
1. Impressions - `7.69M`
2. Clicks - `229.8k`
3. Avg CPC - `$0.80`
4. Avg CTR - `3.0%`
5. Search impr share - `67.6%`
6. Search top IS - `38.5%`
7. Search abs top IS - `16.8%`
8. Click share - `43.6%`

---

## COLOR PALETTE

### Category Borders
- **Financial:** `#34a853` (Google Green)
- **Leads:** `#1a73e8` (Google Blue)
- **Actions:** `#5f6368` (Google Gray)

### Text Colors
- **Primary:** `#202124` (values)
- **Secondary:** `#5f6368` (labels)
- **Positive:** `#34a853` (green)
- **Negative:** `#ea4335` (red)
- **Neutral:** `#5f6368` (gray)

### Backgrounds
- **Cards:** `#ffffff` (white)
- **Page:** `#f8f9fa` (light gray)
- **Tooltip:** `#202124` (dark)

### Borders/Dividers
- **Divider:** `#dadce0`
- **Pill border:** `#dadce0`

---

## PAGES TO UPDATE

Apply metrics cards to all 8 pages:

1. **Dashboard** (`/`) - 14 cards (3 Financial + 3 Leads + 8 Actions)
2. **Campaigns** (`/campaigns`) - TBD (wireframe separately)
3. **Keywords** (`/keywords`) - TBD (wireframe separately)
4. **Ad Groups** (`/ad-groups`) - TBD (wireframe separately)
5. **Ads** (`/ads`) - TBD (wireframe separately)
6. **Shopping** (`/shopping`) - TBD (wireframe separately)
7. **Recommendations** (`/recommendations`) - TBD (wireframe separately)
8. **Changes** (`/changes`) - TBD (wireframe separately)

**Note:** Dashboard wireframe is complete and approved. Other pages will be wireframed separately to determine exact metrics for each page.

---

## FILES TO CREATE/MODIFY

### New Files
1. **C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\metrics_cards.css**
   - Complete CSS for metrics cards module
   - Grid layouts, card styles, sparkline styles
   - Interactive states (hover, active)
   - Responsive behavior

### Modified Files
2. **C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\macros\metrics_cards.html**
   - Update macro to use new design
   - White backgrounds, color-coded borders
   - Sentence case labels
   - Interactive sparklines with dots and tooltips
   - Left-aligned Actions pill

3. **C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\base_bootstrap.html**
   - Add `<link>` to metrics_cards.css in `<head>` section
   - Position: After navigation.css

---

## IMPLEMENTATION CHECKLIST

### CSS Module
- [ ] Create metrics_cards.css
- [ ] Grid layouts (9-column for both rows)
- [ ] Card styles (white bg, left border, padding, height)
- [ ] Category border colors (green/blue/gray)
- [ ] Text styles (labels, values, changes)
- [ ] Section label styles
- [ ] Vertical divider styles
- [ ] Blank space styles
- [ ] Sparkline wrapper and SVG styles
- [ ] Interactive dot styles
- [ ] Tooltip styles
- [ ] Toggle pill styles
- [ ] Hover states
- [ ] Responsive behavior (if needed)

### Macro Updates
- [ ] Update metrics_cards.html macro
- [ ] White backgrounds
- [ ] Left borders only (4px, color-coded)
- [ ] Sentence case labels
- [ ] Add sparkline dots to SVG
- [ ] Add tooltips with correct values
- [ ] Interactive JavaScript
- [ ] Left-align Actions pill
- [ ] Update section labels grid
- [ ] Test all card types

### Base Template
- [ ] Add CSS link to base_bootstrap.html
- [ ] Verify load order (after navigation.css)

### Testing
- [ ] Dashboard page loads correctly
- [ ] All 14 cards render
- [ ] Colors correct (green/blue/gray borders)
- [ ] Section labels align correctly
- [ ] Vertical divider displays
- [ ] Blank spaces invisible
- [ ] Sparklines render
- [ ] Hover shows dot on ALL cards
- [ ] Tooltips show correct values
- [ ] Actions toggle works
- [ ] No console errors
- [ ] Responsive behavior
- [ ] All 8 pages (after other wireframes)

---

## REFERENCE FILES

1. **dashboard_wireframe_v8.html** - Final approved wireframe
2. **Current metrics_cards.html** - Existing macro (for comparison)
3. **navigation.css** - Reference for CSS patterns (Chat 51)

---

## SUCCESS CRITERIA

- [ ] White card backgrounds (#ffffff)
- [ ] Color-coded left borders (4px: green/blue/gray)
- [ ] Sentence case labels
- [ ] 90px min-height cards
- [ ] 9-column grid (4 + divider + 4)
- [ ] Section labels ("Financial", "Leads") aligned correctly
- [ ] Vertical 1px divider between sections
- [ ] Blank spaces invisible
- [ ] Interactive sparklines (dot follows mouse)
- [ ] Tooltips show correct values
- [ ] Actions section left-aligned and collapsible
- [ ] Max-width 1600px container
- [ ] Works on Dashboard page
- [ ] No regressions on other pages
- [ ] Clean, maintainable code

---

**Document:** METRICS_CARDS_FINAL_SPECS.md  
**Created:** 2026-02-28  
**Status:** APPROVED  
**Ready for:** Chat 52 Implementation
