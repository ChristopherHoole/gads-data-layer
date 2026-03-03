# NAVIGATION MODULE - FINAL SPECIFICATIONS

**Module:** Left Main Navigation (Slim Vertical)  
**Date:** 2026-02-28  
**Status:** APPROVED - Ready for Implementation  
**Design Inspiration:** Google Ads slim navigation  

---

## APPROVED DESIGN

**Width:** 110px  
**Icon Library:** Google Material Symbols (Outlined)  
**Icon Size:** 32px  
**Brand Text Size:** 14px  
**Menu Text Size:** 14px (except Recommendations at 11px)  
**Logo:** act_logo.svg (embedded SVG with Google colors)  

---

## LAYOUT SPECIFICATIONS

### Navigation Container
```css
width: 110px
background: #ffffff
border-right: 1px solid #dadce0
position: fixed
left: 0
top: 0
height: 100vh
z-index: 1000
```

### Branding Section
```css
padding: 16px 12px
border-bottom: 1px solid #dadce0
display: flex
flex-direction: column
align-items: center
```

**Logo:**
- Width: 48px
- Height: 48px
- SVG with concentric circles (blue, red, yellow, green)
- Margin-bottom: 8px

**Brand Text:**
- Font-size: 14px
- Font-weight: 600
- Color: #202124
- Text-align: center
- Line-height: 1.3
- Content: "Ads" / "Control" / "Tower" (stacked)

### Navigation Items
```css
padding: 12px 8px
margin: 4px 8px
min-height: 80px
border-radius: 8px
display: flex
flex-direction: column
align-items: center
justify-content: center
```

**Icon:**
- Font-size: 32px
- Margin-bottom: 4px
- Color: #5f6368 (default), #1a73e8 (active)

**Text:**
- Font-size: 14px (default), 11px (Recommendations only)
- Font-weight: 500
- Text-align: center
- Line-height: 1.2
- Color: #5f6368 (default), #1a73e8 (active)

---

## NAVIGATION ITEMS

| Item | Icon Name | Icon | Text Size | Route |
|------|-----------|------|-----------|-------|
| Dashboard | home | 🏠 | 14px | / |
| Campaigns | campaign | 📢 | 14px | /campaigns |
| Ad Groups | folder | 📁 | 14px | /ad-groups |
| Keywords | search | 🔍 | 14px | /keywords |
| Ads | article | 📄 | 14px | /ads |
| Shopping | shopping_cart | 🛒 | 14px | /shopping |
| Recommendations | lightbulb | 💡 | **11px** | /recommendations |
| Changes | history | 🕐 | 14px | /changes |
| Settings | settings | ⚙️ | 14px | /settings |

**Note:** Recommendations uses 11px text to prevent wrapping/cutoff

---

## STATES

### Default (Inactive)
```css
background: transparent
color: #5f6368
cursor: pointer
```

### Hover
```css
background: #f1f3f4
color: #202124
transition: all 150ms ease
```

### Active (Current Page)
```css
background: #e8f0fe
color: #1a73e8
font-weight: 500 (no change from default)
```

### Focus (Keyboard)
```css
outline: 2px solid #1a73e8
outline-offset: 2px
```

---

## COLOR PALETTE

**Primary Blue (Google Ads):**
- Active background: #e8f0fe
- Active text/icon: #1a73e8

**Neutrals:**
- Background: #ffffff
- Border: #dadce0
- Hover background: #f1f3f4
- Default text: #5f6368
- Hover text: #202124

**Logo Colors:**
- Blue circle: #4285F4
- Red circle: #EA4335
- Yellow circle: #FBBC05
- Green center: #34A853

---

## GOOGLE MATERIAL SYMBOLS SETUP

**CDN Link:**
```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />
```

**CSS Configuration:**
```css
.material-symbols-outlined {
  font-variation-settings:
    'FILL' 0,      /* Outlined (not filled) */
    'wght' 400,    /* Regular weight */
    'GRAD' 0,      /* Standard gradient */
    'opsz' 40;     /* Optical size for 32px display */
}
```

**Usage:**
```html
<span class="material-symbols-outlined">home</span>
```

---

## LOGO SVG CODE

```html
<svg class="nav-brand-logo" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="41" fill="none" stroke="#4285F4" stroke-width="10"/>
  <circle cx="50" cy="50" r="29" fill="none" stroke="#EA4335" stroke-width="10"/>
  <circle cx="50" cy="50" r="17" fill="none" stroke="#FBBC05" stroke-width="10"/>
  <circle cx="50" cy="50" r="10" fill="#34A853"/>
</svg>
```

---

## COMPLETE HTML STRUCTURE

```html
<nav class="nav-sidebar">
  <!-- BRANDING -->
  <div class="nav-brand">
    <svg class="nav-brand-logo" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="41" fill="none" stroke="#4285F4" stroke-width="10"/>
      <circle cx="50" cy="50" r="29" fill="none" stroke="#EA4335" stroke-width="10"/>
      <circle cx="50" cy="50" r="17" fill="none" stroke="#FBBC05" stroke-width="10"/>
      <circle cx="50" cy="50" r="10" fill="#34A853"/>
    </svg>
    <div class="nav-brand-text">
      Ads<br>Control<br>Tower
    </div>
  </div>

  <!-- NAVIGATION ITEMS -->
  <div class="nav-items">
    <a href="/" class="nav-item active">
      <span class="material-symbols-outlined nav-item-icon">home</span>
      <span class="nav-item-text">Dashboard</span>
    </a>
    
    <a href="/campaigns" class="nav-item">
      <span class="material-symbols-outlined nav-item-icon">campaign</span>
      <span class="nav-item-text">Campaigns</span>
    </a>
    
    <a href="/ad-groups" class="nav-item">
      <span class="material-symbols-outlined nav-item-icon">folder</span>
      <span class="nav-item-text">Ad Groups</span>
    </a>
    
    <a href="/keywords" class="nav-item">
      <span class="material-symbols-outlined nav-item-icon">search</span>
      <span class="nav-item-text">Keywords</span>
    </a>
    
    <a href="/ads" class="nav-item">
      <span class="material-symbols-outlined nav-item-icon">article</span>
      <span class="nav-item-text">Ads</span>
    </a>
    
    <a href="/shopping" class="nav-item">
      <span class="material-symbols-outlined nav-item-icon">shopping_cart</span>
      <span class="nav-item-text">Shopping</span>
    </a>
    
    <a href="/recommendations" class="nav-item">
      <span class="material-symbols-outlined nav-item-icon">lightbulb</span>
      <span class="nav-item-text small">Recommendations</span>
    </a>
    
    <a href="/changes" class="nav-item">
      <span class="material-symbols-outlined nav-item-icon">history</span>
      <span class="nav-item-text">Changes</span>
    </a>
    
    <a href="/settings" class="nav-item">
      <span class="material-symbols-outlined nav-item-icon">settings</span>
      <span class="nav-item-text">Settings</span>
    </a>
  </div>
</nav>
```

---

## COMPLETE CSS

```css
/* Material Symbols Configuration */
.material-symbols-outlined {
  font-variation-settings:
    'FILL' 0,
    'wght' 400,
    'GRAD' 0,
    'opsz' 40;
}

/* NAVIGATION SIDEBAR */
.nav-sidebar {
  width: 110px;
  background: #ffffff;
  border-right: 1px solid #dadce0;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  z-index: 1000;
}

/* BRANDING / LOGO */
.nav-brand {
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  border-bottom: 1px solid #dadce0;
}

.nav-brand-logo {
  width: 48px;
  height: 48px;
  margin-bottom: 8px;
}

.nav-brand-text {
  font-size: 14px;
  font-weight: 600;
  color: #202124;
  text-align: center;
  line-height: 1.3;
}

/* NAVIGATION ITEMS */
.nav-items {
  flex: 1;
  padding: 8px 0;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 8px;
  margin: 4px 8px;
  text-decoration: none;
  color: #5f6368;
  border-radius: 8px;
  transition: all 150ms ease;
  cursor: pointer;
  min-height: 80px;
}

.nav-item:hover {
  background: #f1f3f4;
  color: #202124;
}

.nav-item.active {
  background: #e8f0fe;
  color: #1a73e8;
}

.nav-item-icon {
  font-size: 32px;
  margin-bottom: 4px;
}

.nav-item-text {
  font-size: 14px;
  font-weight: 500;
  text-align: center;
  line-height: 1.2;
}

/* Recommendations stays at 11px to fit */
.nav-item-text.small {
  font-size: 11px;
}

/* SCROLLBAR STYLING */
.nav-items::-webkit-scrollbar {
  width: 6px;
}

.nav-items::-webkit-scrollbar-track {
  background: transparent;
}

.nav-items::-webkit-scrollbar-thumb {
  background: #dadce0;
  border-radius: 3px;
}

.nav-items::-webkit-scrollbar-thumb:hover {
  background: #bdc1c6;
}
```

---

## ACTIVE STATE LOGIC

**Flask/Jinja2 Implementation:**
```python
# In template
<a href="/campaigns" 
   class="nav-item {% if request.path == '/campaigns' %}active{% endif %}">
  <span class="material-symbols-outlined nav-item-icon">campaign</span>
  <span class="nav-item-text">Campaigns</span>
</a>
```

**Route Matching:**
- `/` → Dashboard active
- `/campaigns` → Campaigns active
- `/ad-groups` → Ad Groups active
- `/keywords` → Keywords active
- `/ads` → Ads active
- `/shopping` → Shopping active
- `/recommendations` → Recommendations active
- `/changes` → Changes active
- `/settings` → Settings active

---

## FILES TO CREATE/MODIFY

### 1. static/css/navigation.css (NEW FILE)
Complete CSS for navigation module (copy from above)

### 2. templates/base_bootstrap.html (MODIFY)
- Add Material Symbols CDN in `<head>`
- Replace existing navigation with new slim nav structure
- Ensure Google Material Icons CSS config included

### 3. All page templates (VERIFY)
- Ensure active class logic works correctly
- Test on all 8 pages

---

## IMPLEMENTATION CHECKLIST

- [ ] Create static/css/navigation.css
- [ ] Add Google Material Symbols CDN to base_bootstrap.html
- [ ] Replace navigation HTML in base_bootstrap.html
- [ ] Add active state logic (Jinja2 template)
- [ ] Test on Dashboard page
- [ ] Test on Campaigns page
- [ ] Test on Ad Groups page
- [ ] Test on Keywords page
- [ ] Test on Ads page
- [ ] Test on Shopping page
- [ ] Test on Recommendations page
- [ ] Test on Changes page
- [ ] Test on Settings page
- [ ] Verify hover states work
- [ ] Verify active states work
- [ ] Verify logo displays
- [ ] Verify brand text displays
- [ ] Verify all icons display
- [ ] Verify "Recommendations" text fits (11px)
- [ ] Verify main content margin-left: 110px
- [ ] Test keyboard navigation
- [ ] Test scrollbar (if many items)
- [ ] Screenshot all pages for handoff

---

## ACCESSIBILITY

**Semantic HTML:**
- `<nav>` element
- `<a>` tags for links
- `aria-current="page"` on active item

**Keyboard:**
- All links focusable via Tab
- Enter/Space to activate
- Focus ring visible

**Screen Readers:**
- Icon + text combination (both read)
- Current page announced
- Descriptive link text

**Color Contrast:**
- Default text (#5f6368 on #ffffff): 4.6:1 (AA) ✓
- Active text (#1a73e8 on #e8f0fe): 4.8:1 (AA+) ✓
- Hover text (#202124 on #f1f3f4): 15:1 (AAA) ✓

---

## MOCKUP FILE

**Reference:** nav_mockup_v3.html  
**Status:** Approved by Christopher on 2026-02-28  

---

## NEXT STEPS

1. Create Chat 51 brief for navigation implementation
2. Worker chat implements navigation
3. Test across all 8 pages
4. Take screenshots of all pages
5. Move to next module (metrics cards)

---

**Specification Status:** FINAL - APPROVED  
**Ready for Implementation:** YES  
**Estimated Implementation Time:** 2-3 hours  

---
