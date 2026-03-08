# SLIDEIN CSS SPECIFICATION — Ads Control Tower
# Version: 1.0 | Date: 2026-03-08
# Applies to: Leads, Replies, Sent page slideins
# Reference wireframe: ACT_SLIDEIN_WIREFRAME_v2.html

---

## UNIVERSAL RULES

- All 3 slideins (Leads, Replies, Sent) use IDENTICAL structure and CSS
- The only differences between pages are: footer buttons, composer placeholder text, AI draft button (Replies only)
- Width: 500px fixed, full viewport height, right-anchored
- Font: DM Sans (import from Google Fonts) — NOT Arial, NOT Inter
- Monospace elements (timestamps): DM Mono

---

## COLOUR PALETTE

```css
:root {
  /* ACT brand */
  --act-blue:   #4285F4;
  --act-green:  #34A853;
  --act-yellow: #FBBC05;
  --act-red:    #EA4335;

  /* Thread items */
  --sent-bg:           #f8f9fa;
  --sent-border:       #4285F4;
  --sent-badge-bg:     #e5e7eb;
  --sent-badge-text:   #374151;
  --reply-bg:          #f0fdf4;
  --reply-border:      #34A853;
  --reply-badge-bg:    #dcfce7;
  --reply-badge-text:  #15803d;

  /* Notes */
  --notes-bg:          #fffbeb;
  --notes-text:        #78350f;
  --notes-title:       #92400e;

  /* UI chrome */
  --divider:           #e5e7eb;
  --muted:             #6b7280;
  --body-text:         #4b5563;
  --heading-text:      #1a1d23;

  /* Badges */
  --badge-agency-bg:   #dbeafe;
  --badge-agency-text: #1d4ed8;
  --badge-direct-bg:   #f3e8ff;
  --badge-direct-text: #7e22ce;
  --badge-recruiter-bg: #fef3c7;
  --badge-recruiter-text: #92400e;
  --badge-website-bg:  #f3f4f6;
  --badge-website-text:#374151;
  --badge-rr-bg:       #dcfce7;
  --badge-rr-text:     #15803d;
  --badge-cold-bg:     #f3f4f6;
  --badge-cold-text:   #6b7280;
  --badge-queued-bg:   #fef9c3;
  --badge-queued-text: #854d0e;
  --badge-contacted-bg:#dbeafe;
  --badge-contacted-text:#1d4ed8;
  --badge-low-bg:      #fef2f2;
  --badge-low-text:    #991b1b;
  --badge-medium-bg:   #fff7ed;
  --badge-medium-text: #9a3412;
  --badge-hot-bg:      #dcfce7;
  --badge-hot-text:    #166534;
  --badge-tz-bg:       #f0f9ff;
  --badge-tz-text:     #0369a1;
}
```

---

## SLIDEIN CONTAINER

```css
.si-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 500px;
  height: 100vh;
  background: #fff;
  border-left: 1px solid var(--divider);
  display: flex;
  flex-direction: column;
  z-index: 1050;
  animation: siSlideIn 0.2s ease;
}

@keyframes siSlideIn {
  from { transform: translateX(30px); opacity: 0; }
  to   { transform: translateX(0);    opacity: 1; }
}

.si-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 1049;
}
```

---

## SECTION 1: HEADER (fixed, does not scroll)

```css
.si-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--divider);
  flex-shrink: 0;
  background: #fff;
}

.si-header-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 8px;
}

.si-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--heading-text);
  line-height: 1.3;
}

.si-email {
  font-size: 12px;
  color: var(--muted);
  margin-top: 2px;
}

.si-close {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: none;
  background: #f3f4f6;
  color: #6b7280;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.1s, color 0.1s;
}
.si-close:hover { background: #e5e7eb; color: #111; }
```

### Badges row

```css
.si-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.si-badge {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

/* Apply colour variables per badge type — see COLOUR PALETTE above */
.si-badge-agency    { background: var(--badge-agency-bg);    color: var(--badge-agency-text); }
.si-badge-direct    { background: var(--badge-direct-bg);    color: var(--badge-direct-text); }
.si-badge-recruiter { background: var(--badge-recruiter-bg); color: var(--badge-recruiter-text); }
.si-badge-website   { background: var(--badge-website-bg);   color: var(--badge-website-text); }
.si-badge-rr        { background: var(--badge-rr-bg);        color: var(--badge-rr-text); }
.si-badge-cold      { background: var(--badge-cold-bg);      color: var(--badge-cold-text); }
.si-badge-queued    { background: var(--badge-queued-bg);    color: var(--badge-queued-text); }
.si-badge-contacted { background: var(--badge-contacted-bg); color: var(--badge-contacted-text); }
.si-badge-low       { background: var(--badge-low-bg);       color: var(--badge-low-text); }
.si-badge-medium    { background: var(--badge-medium-bg);    color: var(--badge-medium-text); }
.si-badge-hot       { background: var(--badge-hot-bg);       color: var(--badge-hot-text); }
.si-badge-tz        { background: var(--badge-tz-bg);        color: var(--badge-tz-text); }
```

### Progress bar

```css
.si-progress {
  display: flex;
  gap: 3px;
  margin-top: 10px;
}

.si-prog-stage {
  flex: 1;
  height: 4px;
  border-radius: 2px;
  background: #e5e7eb;
  transition: background 0.2s;
}
.si-prog-stage.done   { background: var(--act-green); }
.si-prog-stage.active { background: var(--act-blue); }

.si-prog-labels {
  display: flex;
  margin-top: 4px;
}

.si-prog-label {
  flex: 1;
  font-size: 9px;
  color: #9ca3af;
  text-align: center;
}
```

---

## SECTION 2: SCROLLABLE BODY

```css
.si-body {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* Scrollbar */
.si-body::-webkit-scrollbar { width: 4px; }
.si-body::-webkit-scrollbar-track { background: transparent; }
.si-body::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 2px; }
```

---

## SECTION 3: REPLY COMPOSER (top of body, always visible)

```css
.si-composer {
  padding: 14px 20px;
  border-bottom: 1px solid var(--divider);
  background: #fafafa;
  flex-shrink: 0;
}

.si-composer-label {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 8px;
}

.si-composer-textarea {
  width: 100%;
  min-height: 80px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 10px 12px;
  font-family: 'DM Sans', sans-serif;
  font-size: 13px;
  color: #374151;
  resize: none;
  background: #fff;
  transition: border-color 0.15s;
  outline: none;
}
.si-composer-textarea:focus  { border-color: var(--act-blue); }
.si-composer-textarea::placeholder { color: #d1d5db; }

.si-composer-toolbar {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  flex-wrap: wrap;
}

/* Toolbar buttons: B, I, attach, etc. */
.si-toolbar-btn {
  padding: 4px 10px;
  border-radius: 4px;
  border: 1px solid #e5e7eb;
  background: #fff;
  font-size: 12px;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  font-family: 'DM Sans', sans-serif;
  transition: background 0.1s;
}
.si-toolbar-btn:hover { background: #f3f4f6; }
.si-toolbar-btn.bold  { font-weight: 700; }
.si-toolbar-btn.italic { font-style: italic; }

/* AI draft button — Replies page only */
.si-toolbar-btn.ai-draft {
  background: #f0fdf4;
  border-color: #86efac;
  color: #166534;
}

/* Signature toggle */
.si-sig-toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--muted);
  cursor: pointer;
  margin-left: 4px;
  user-select: none;
}

.si-toggle-pip {
  width: 28px;
  height: 16px;
  border-radius: 8px;
  background: var(--act-green);
  position: relative;
  flex-shrink: 0;
  transition: background 0.2s;
}
.si-toggle-pip::after {
  content: '';
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #fff;
  position: absolute;
  top: 2px;
  right: 2px;
  transition: right 0.2s;
}
.si-toggle-pip.off { background: #d1d5db; }
.si-toggle-pip.off::after { right: auto; left: 2px; }

/* Send button */
.si-send-btn {
  margin-left: auto;
  padding: 6px 16px;
  background: var(--act-blue);
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  font-family: 'DM Sans', sans-serif;
  transition: background 0.15s;
}
.si-send-btn:hover { background: #2b6de4; }
```

---

## SECTION 4: NOTES (below composer, above thread)

```css
.si-notes {
  padding: 12px 20px;
  border-bottom: 1px solid var(--divider);
  background: var(--notes-bg);
  flex-shrink: 0;
}

.si-notes-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 5px;
}

.si-notes-title {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: var(--notes-title);
}

.si-notes-edit {
  font-size: 11px;
  color: var(--act-blue);
  cursor: pointer;
  background: none;
  border: none;
  font-family: 'DM Sans', sans-serif;
}
.si-notes-edit:hover { text-decoration: underline; }

.si-notes-body {
  font-size: 12px;
  color: var(--notes-text);
  line-height: 1.5;
}

.si-notes-empty {
  font-size: 12px;
  color: #d97706;
  font-style: italic;
}
```

---

## SECTION 5: CONVERSATION THREAD (scrollable, newest first)

```css
.si-thread {
  flex: 1;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
}

.si-thread-label {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 2px;
  flex-shrink: 0;
}

/* Thread items */
.si-thread-item {
  border-radius: 6px;
  padding: 12px 14px;
  border-left: 3px solid;
  flex-shrink: 0;
}

.si-thread-item.outbound {
  background: var(--sent-bg);
  border-left-color: var(--sent-border);
}

.si-thread-item.inbound {
  background: var(--reply-bg);
  border-left-color: var(--reply-border);
}

.si-thread-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

/* Thread badges */
.si-thread-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 3px;
  letter-spacing: 0.3px;
  text-transform: uppercase;
}
.si-thread-badge.sent {
  background: var(--sent-badge-bg);
  color: var(--sent-badge-text);
}
.si-thread-badge.reply-received {
  background: var(--reply-badge-bg);
  color: var(--reply-badge-text);
}

.si-thread-ts {
  font-size: 11px;
  color: var(--muted);
  font-family: 'DM Mono', monospace;
}

.si-thread-subject {
  font-size: 12px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 4px;
}

.si-thread-body {
  font-size: 12px;
  color: var(--body-text);
  line-height: 1.5;
}

/* Clamped body — "Show more" expands */
.si-thread-body.clamped {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.si-show-more-btn {
  font-size: 11px;
  color: var(--act-blue);
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px 0;
  font-family: 'DM Sans', sans-serif;
  margin-top: 4px;
  display: block;
}
.si-show-more-btn:hover { text-decoration: underline; }

/* Quoted text toggle (Gmail-style "...") */
.si-quoted-toggle {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 6px;
  padding: 2px 8px;
  background: #e5e7eb;
  border-radius: 3px;
  font-size: 11px;
  color: #6b7280;
  cursor: pointer;
  border: none;
  font-family: 'DM Sans', sans-serif;
  transition: background 0.1s;
}
.si-quoted-toggle:hover { background: #d1d5db; }

.si-quoted-content {
  display: none;
  margin-top: 8px;
  padding: 8px 10px;
  background: #f9fafb;
  border-left: 2px solid #d1d5db;
  font-size: 11px;
  color: #9ca3af;
  line-height: 1.5;
  border-radius: 0 4px 4px 0;
}
.si-quoted-content.open { display: block; }

/* Empty state */
.si-thread-empty {
  text-align: center;
  padding: 32px 16px;
  color: var(--muted);
  font-size: 13px;
}
```

---

## SECTION 6: FOOTER (fixed, does not scroll)

```css
.si-footer {
  padding: 12px 20px;
  border-top: 1px solid var(--divider);
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  flex-shrink: 0;
  background: #fff;
}

.si-footer-btn {
  padding: 7px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid #e5e7eb;
  background: #fff;
  color: #374151;
  font-family: 'DM Sans', sans-serif;
  transition: background 0.1s, border-color 0.1s;
  white-space: nowrap;
}
.si-footer-btn:hover { background: #f3f4f6; }

.si-footer-btn.primary {
  background: var(--act-blue);
  color: #fff;
  border-color: var(--act-blue);
}
.si-footer-btn.primary:hover { background: #2b6de4; }

.si-footer-btn.success {
  background: var(--act-green);
  color: #fff;
  border-color: var(--act-green);
}
.si-footer-btn.success:hover { background: #2d9248; }

.si-footer-btn.danger {
  color: #dc2626;
  border-color: #fecaca;
  background: #fff;
}
.si-footer-btn.danger:hover { background: #fef2f2; }
```

---

## FOOTER BUTTONS PER PAGE

| Page    | Buttons (left to right) |
|---------|------------------------|
| Leads   | `+ Queue email` (primary) · `Edit lead` · `✓ Mark won` (success) · `✕ Mark lost` (danger) · `Update status` |
| Replies | `✓ Mark as won` (success) · `📅 Book meeting` · `Update status` · `✕ Mark as lost` (danger) |
| Sent    | `+ Queue follow-up` (primary) · `Update status` · `✓ Mark won` (success) · `✕ Mark lost` (danger) |

---

## TERMINOLOGY — EXACT STRINGS (use these everywhere)

| Old | New |
|-----|-----|
| Replied | Reply Received |
| Reply | Reply Received (badge/status) |
| reply | reply (verb, lowercase — "Write a reply...") |
| replied | reply_received (DB status value) |

**Progress bar stage labels (exact):**
Cold → Queued → Contacted → Reply Received → Meeting → Won

---

## THREAD ORDER RULE

Thread items are rendered **newest first** (top) → oldest last (bottom).
Backend query: `ORDER BY created_at DESC` (or equivalent timestamp column).

---

## FONT IMPORT

Add to base_bootstrap.html `<head>`:
```html
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
```

Apply globally:
```css
body { font-family: 'DM Sans', sans-serif; }
```

---

## FILES TO ADD CSS TO

All slidein CSS goes in a new file:
`C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\outreach-slidein.css`

Include in base_bootstrap.html (or outreach templates):
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/outreach-slidein.css') }}">
```

---

**Version:** 1.0 | **Date:** 2026-03-08
**Reference wireframe:** ACT_SLIDEIN_WIREFRAME_v2.html
