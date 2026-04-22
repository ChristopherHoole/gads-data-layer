/* ============================================================================
   ACT v2 — Client Configuration Page Interactions
   Tabs, toggles, validation, save/reset, persona switch, level toggles
   ============================================================================ */

document.addEventListener('DOMContentLoaded', () => {

  const btnSave = document.getElementById('btnSave');
  const CLIENT_ID = document.getElementById('configRoot')?.dataset.clientId;

  // -------------------------------------------------------------------------
  // VERTICAL TAB SWITCHING
  // -------------------------------------------------------------------------
  document.querySelectorAll('.config-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.config-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.config-panel').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      const panel = document.getElementById('panel-' + tab.dataset.tab);
      if (panel) panel.classList.add('active');
      // N2 Part 3: lazy-load neg-list viewer on first activation
      if (tab.dataset.tab === 'negative-lists' && !NegLists._loaded) {
        NegLists.load();
      }
    });
  });

  // -------------------------------------------------------------------------
  // N1v — COLLAPSIBLE SECTIONS (matches Account Level / Morning Review pattern)
  // -------------------------------------------------------------------------
  document.querySelectorAll('.act-section__header').forEach(header => {
    header.style.cursor = 'pointer';
    header.addEventListener('click', () => {
      const section = header.closest('.act-section');
      if (section) section.classList.toggle('collapsed');
    });
  });

  // -------------------------------------------------------------------------
  // TOGGLE SWITCHES
  // -------------------------------------------------------------------------
  document.querySelectorAll('.config-toggle').forEach(toggle => {
    toggle.addEventListener('click', () => {
      toggle.classList.toggle('on');
      markDirty();
    });
  });

  // -------------------------------------------------------------------------
  // PERSONA SWITCHER (CPA / ROAS)
  // -------------------------------------------------------------------------
  const personaSelect = document.getElementById('settingPersona');
  const targetCpaRow = document.getElementById('rowTargetCpa');
  const targetRoasRow = document.getElementById('rowTargetRoas');

  if (personaSelect) {
    personaSelect.addEventListener('change', () => {
      const isLeadGen = personaSelect.value === 'lead_gen_cpa';
      if (targetCpaRow) targetCpaRow.style.display = isLeadGen ? '' : 'none';
      if (targetRoasRow) targetRoasRow.style.display = isLeadGen ? 'none' : '';
      markDirty();
    });
  }

  // -------------------------------------------------------------------------
  // FIELD-LEVEL VALIDATION
  // -------------------------------------------------------------------------
  function setupValidation() {
    document.querySelectorAll('.config-input[type="number"]').forEach(input => {
      const suffix = input.closest('.input-group')?.querySelector('.input-group__suffix')?.textContent || '';
      const isPercent = suffix.includes('%');
      const isMultiWeight = input.closest('.multi-input') && (input.id === 'weight7d' || input.id === 'weight14d' || input.id === 'weight30d');

      input.dataset.valMin = '0';
      if (isPercent && !isMultiWeight) input.dataset.valMax = '100';

      let errorEl = input.parentElement.querySelector('.field-error');
      if (!errorEl) {
        errorEl = document.createElement('div');
        errorEl.className = 'field-error';
        const parent = input.closest('.input-group') || input;
        parent.parentElement.insertBefore(errorEl, parent.nextSibling);
      }

      input.addEventListener('input', () => {
        validateField(input, errorEl);
        markDirty();
      });
    });

    document.querySelectorAll('.config-select').forEach(sel => {
      sel.addEventListener('change', markDirty);
    });

    // N1j — profile textareas (services_advertised, services_not_advertised,
    // service_locations, client_brand_terms, rule_7_exclude_tokens) weren't
    // wired to dirty-state. 'input' (not 'change') so Save activates the
    // instant the user types, matching numeric-input behaviour above.
    document.querySelectorAll('textarea[data-key]').forEach(textarea => {
      textarea.addEventListener('input', markDirty);
    });
  }

  function validateField(input, errorEl) {
    const val = parseFloat(input.value);
    const min = parseFloat(input.dataset.valMin);
    const max = input.dataset.valMax ? parseFloat(input.dataset.valMax) : null;

    if (input.value === '') {
      input.classList.remove('invalid');
      errorEl.classList.remove('show');
      return true;
    }
    if (isNaN(val)) {
      input.classList.add('invalid');
      errorEl.textContent = 'Must be a number';
      errorEl.classList.add('show');
      return false;
    }
    if (val < min) {
      input.classList.add('invalid');
      errorEl.textContent = 'Cannot be negative';
      errorEl.classList.add('show');
      return false;
    }
    if (max !== null && val > max) {
      input.classList.add('invalid');
      errorEl.textContent = 'Maximum ' + max + '%';
      errorEl.classList.add('show');
      return false;
    }
    input.classList.remove('invalid');
    errorEl.classList.remove('show');
    return true;
  }

  function hasValidationErrors() {
    return document.querySelectorAll('.config-input.invalid').length > 0 ||
      (weightMsg && weightMsg.classList.contains('validation-msg--error') && weightMsg.classList.contains('show'));
  }

  setupValidation();

  // -------------------------------------------------------------------------
  // N1n — Profile-list summary cards + slide-in editor
  // -------------------------------------------------------------------------
  const listEditor = (function () {
    const el = {
      slidein:  document.getElementById('listEditor'),
      overlay:  document.getElementById('listEditorOverlay'),
      title:    document.getElementById('listEditorTitle'),
      desc:     document.getElementById('listEditorDesc'),
      search:   document.getElementById('listEditorSearch'),
      sort:     document.getElementById('listEditorSort'),
      count:    document.getElementById('listEditorCount'),
      addInput: document.getElementById('listEditorAddInput'),
      addBtn:   document.getElementById('listEditorAddBtn'),
      rows:     document.getElementById('listEditorRows'),
      warn:     document.getElementById('listEditorWarn'),
      closeBtn: document.getElementById('listEditorClose'),
      cancelBtn:document.getElementById('listEditorCancel'),
      saveBtn:  document.getElementById('listEditorSave'),
    };
    if (!el.slidein) return null;

    // State for the currently-open editor session.
    let activeField = null;            // string key, e.g. "services_advertised"
    let activeTextarea = null;         // hidden <textarea> element
    let originalSerialized = '';       // value at open-time, for dirty check
    let items = [];                    // string[] in insertion order (for "recent")

    // ---------- Parsing / serialisation (mirrors backend normalisation)
    function parseCsv(s) {
      if (!s) return [];
      // Accept both comma and newline separators.
      return s.split(/[,\n]/).map(x => x.trim().toLowerCase()).filter(Boolean);
    }
    function dedupe(arr) {
      const seen = new Set();
      const out = [];
      for (const v of arr) {
        if (!seen.has(v)) { seen.add(v); out.push(v); }
      }
      return out;
    }
    function serialize(arr) {
      return arr.join(', ');
    }
    function escapeHtml(s) {
      return String(s).replace(/[&<>"']/g, c =>
        ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    }

    // ---------- Row rendering
    function renderRows() {
      const q = (el.search.value || '').trim().toLowerCase();
      const sort = el.sort.value;
      // Build a sorted copy without mutating `items` (insertion order is
      // preserved there to keep "recently added" sort meaningful).
      let display = items.map((v, i) => ({v, i}));
      if (sort === 'az')       display.sort((a, b) => a.v.localeCompare(b.v));
      else if (sort === 'za')  display.sort((a, b) => b.v.localeCompare(a.v));
      else                     display.sort((a, b) => b.i - a.i);  // recent
      let visible = 0;
      if (!items.length) {
        el.rows.innerHTML = '<div class="list-editor__empty">No phrases yet. Add one above.</div>';
      } else {
        el.rows.innerHTML = display.map(({v}) => {
          const hide = q && !v.includes(q) ? ' hidden' : '';
          if (!hide) visible++;
          return `<div class="list-editor__row${hide}" data-val="${escapeHtml(v)}" role="listitem">
            <span class="list-editor__row-text">${escapeHtml(v)}</span>
            <button type="button" class="list-editor__row-remove" aria-label="Remove">&times;</button>
          </div>`;
        }).join('');
      }
      el.count.textContent = q
        ? `${visible} of ${items.length}`
        : `${items.length} phrase${items.length === 1 ? '' : 's'}`;
    }

    // ---------- Warning helper
    let warnTimer = null;
    function warn(msg) {
      el.warn.textContent = msg;
      el.warn.style.display = '';
      clearTimeout(warnTimer);
      warnTimer = setTimeout(() => { el.warn.style.display = 'none'; }, 4000);
    }
    function clearWarn() { el.warn.style.display = 'none'; }

    // ---------- Add handler — accepts single phrase OR comma/newline paste
    function addFromInput() {
      const raw = el.addInput.value;
      if (!raw.trim()) return;
      const parsed = parseCsv(raw);
      if (!parsed.length) {
        warn('Nothing to add.');
        return;
      }
      const existing = new Set(items);
      const added = [];
      const dupes = [];
      for (const p of parsed) {
        if (existing.has(p)) { dupes.push(p); continue; }
        items.push(p);
        existing.add(p);
        added.push(p);
      }
      el.addInput.value = '';
      renderRows();
      if (added.length && dupes.length) {
        warn(`Added ${added.length}. Skipped ${dupes.length} duplicate(s).`);
      } else if (dupes.length) {
        warn(`Already in list: ${dupes.slice(0, 3).join(', ')}${dupes.length > 3 ? '…' : ''}`);
      } else {
        clearWarn();
      }
    }

    // ---------- Row remove (event delegation)
    el.rows.addEventListener('click', (e) => {
      const btn = e.target.closest('.list-editor__row-remove');
      if (!btn) return;
      const row = btn.closest('.list-editor__row');
      const val = row?.dataset.val;
      if (val == null) return;
      items = items.filter(v => v !== val);
      renderRows();
    });

    // ---------- Open / close
    function updateSummary(container, arr) {
      const countEl = container.querySelector('.config-list-summary__count');
      const prevEl  = container.querySelector('.config-list-summary__preview');
      if (countEl) countEl.textContent = `${arr.length} phrase${arr.length === 1 ? '' : 's'}`;
      if (prevEl)  prevEl.textContent  = arr.slice(0, 5).join(', ');
    }
    function open(container) {
      activeField = container.dataset.field;
      activeTextarea = document.querySelector(`textarea[data-key="${activeField}"]`);
      if (!activeTextarea) return;
      originalSerialized = activeTextarea.value || '';
      items = dedupe(parseCsv(originalSerialized));
      el.title.textContent = container.dataset.label || activeField;
      el.desc.textContent  = container.dataset.desc || '';
      el.search.value = '';
      el.sort.value = 'az';
      el.addInput.value = '';
      clearWarn();
      renderRows();
      el.slidein.classList.add('open');
      el.slidein.setAttribute('aria-hidden', 'false');
      el.overlay.classList.add('open');
      setTimeout(() => el.search.focus(), 50);
    }
    function close() {
      el.slidein.classList.remove('open');
      el.slidein.setAttribute('aria-hidden', 'true');
      el.overlay.classList.remove('open');
      activeField = null;
      activeTextarea = null;
    }
    function tryCancel() {
      const current = serialize(items);
      const originalNormalized = serialize(dedupe(parseCsv(originalSerialized)));
      if (current !== originalNormalized) {
        if (!confirm('Discard changes?')) return;
      }
      close();
    }
    function save() {
      if (!activeTextarea) return close();
      const newVal = serialize(items);
      const originalNormalized = serialize(dedupe(parseCsv(originalSerialized)));
      activeTextarea.value = newVal;
      // Fire input so Wave J's dirty listener marks the page dirty.
      if (newVal !== originalNormalized) {
        activeTextarea.dispatchEvent(new Event('input', { bubbles: true }));
      }
      // Update the matching summary card in-place.
      const card = document.querySelector(`.config-list-summary[data-field="${activeField}"]`);
      if (card) updateSummary(card, items);
      close();
    }

    // ---------- Wire global handlers
    document.querySelectorAll('.config-list-summary').forEach(card => {
      // Seed count + preview from the hidden textarea on page load.
      const ta = document.querySelector(`textarea[data-key="${card.dataset.field}"]`);
      if (ta) updateSummary(card, dedupe(parseCsv(ta.value || '')));
      card.querySelector('.config-list-summary__edit')
          .addEventListener('click', () => open(card));
    });
    el.closeBtn.addEventListener('click', tryCancel);
    el.cancelBtn.addEventListener('click', tryCancel);
    el.overlay.addEventListener('click', tryCancel);
    el.saveBtn.addEventListener('click', save);
    el.addBtn.addEventListener('click', addFromInput);
    el.addInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') { e.preventDefault(); addFromInput(); }
    });
    el.search.addEventListener('input', renderRows);
    el.sort.addEventListener('change', renderRows);
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && el.slidein.classList.contains('open')) tryCancel();
    });

    return { open, close };
  })();

  // -------------------------------------------------------------------------
  // SCORING WEIGHTS VALIDATION
  // -------------------------------------------------------------------------
  const w7 = document.getElementById('weight7d');
  const w14 = document.getElementById('weight14d');
  const w30 = document.getElementById('weight30d');
  const weightMsg = document.getElementById('weightValidation');

  function validateWeights() {
    if (!w7 || !w14 || !w30 || !weightMsg) return;
    const total = (parseInt(w7.value) || 0) + (parseInt(w14.value) || 0) + (parseInt(w30.value) || 0);
    if (total === 100) {
      weightMsg.className = 'validation-msg validation-msg--success show';
      weightMsg.textContent = 'Weights sum to 100% \u2014 valid';
    } else {
      weightMsg.className = 'validation-msg validation-msg--error show';
      weightMsg.textContent = 'Weights sum to ' + total + '% \u2014 must equal 100%';
    }
    updateSaveButton();
  }

  [w7, w14, w30].forEach(el => { if (el) el.addEventListener('input', validateWeights); });

  // -------------------------------------------------------------------------
  // DIRTY STATE + SAVE BUTTON
  // -------------------------------------------------------------------------
  let isDirty = false;

  function markDirty() {
    isDirty = true;
    updateSaveButton();
  }

  function updateSaveButton() {
    if (!btnSave) return;
    if (isDirty && !hasValidationErrors()) {
      btnSave.classList.remove('btn-save--disabled');
    } else {
      btnSave.classList.add('btn-save--disabled');
    }
  }

  // -------------------------------------------------------------------------
  // COLLECT ALL SETTINGS FROM PAGE
  // -------------------------------------------------------------------------
  function collectData() {
    const data = {
      client_id: CLIENT_ID,
      client: {
        persona: personaSelect ? personaSelect.value : 'lead_gen_cpa',
        monthly_budget: parseFloat(document.querySelector('[data-key="monthly_budget"]')?.value) || 0,
        target_cpa: null,
        target_roas: null
      },
      level_states: {},
      settings: {}
    };

    // Target CPA/ROAS based on persona
    if (data.client.persona === 'lead_gen_cpa') {
      data.client.target_cpa = parseFloat(document.querySelector('[data-key="target_cpa"]')?.value) || null;
    } else {
      data.client.target_roas = parseFloat(document.querySelector('[data-key="target_roas"]')?.value) || null;
    }

    // N1a — client profile textareas (lowercase + trim on client; server re-normalises)
    const PROFILE_FIELDS = ['services_not_advertised', 'services_advertised', 'service_locations', 'client_brand_terms', 'rule_7_exclude_tokens'];
    PROFILE_FIELDS.forEach(k => {
      const el = document.querySelector(`textarea[data-key="${k}"]`);
      data.client[k] = el ? el.value.trim().toLowerCase() : '';
    });

    // Level states
    document.querySelectorAll('.level-row').forEach(row => {
      const level = row.dataset.level;
      const activeBtn = row.querySelector('.level-toggle__opt.active');
      if (level && activeBtn) {
        // Map HTML data-level to DB level names
        const levelMap = { 'adgroup': 'ad_group' };
        data.level_states[levelMap[level] || level] = activeBtn.dataset.state === 'monitor' ? 'monitor_only' : activeBtn.dataset.state;
      }
    });

    // Settings from data-key inputs
    document.querySelectorAll('[data-key]').forEach(el => {
      const key = el.dataset.key;
      // Skip client-level fields (handled in data.client above)
      if (['monthly_budget', 'target_cpa', 'target_roas',
           'services_not_advertised', 'services_advertised',
           'service_locations', 'client_brand_terms',
           'rule_7_exclude_tokens'].includes(key)) return;

      let value;
      if (el.classList.contains('config-toggle')) {
        value = el.classList.contains('on') ? 'true' : 'false';
      } else if (el.tagName === 'SELECT') {
        value = el.value;
      } else {
        value = el.value;
      }
      data.settings[key] = value === '' ? null : value;
    });

    return data;
  }

  // -------------------------------------------------------------------------
  // SAVE
  // -------------------------------------------------------------------------
  btnSave?.addEventListener('click', () => {
    if (btnSave.classList.contains('btn-save--disabled')) return;

    const data = collectData();

    fetch('/v2/config/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    .then(r => r.json())
    .then(result => {
      if (result.success) {
        showToast('Settings saved', 'success');
        isDirty = false;
        updateSaveButton();
        const saved = document.querySelector('.config-header__saved');
        if (saved) {
          saved.innerHTML = '<span class="material-symbols-outlined">schedule</span>Last saved: just now';
        }
      } else {
        showToast('Save failed: ' + (result.error || 'Unknown error'), 'error');
      }
    })
    .catch(err => showToast('Save failed: ' + err.message, 'error'));
  });

  // -------------------------------------------------------------------------
  // RESET
  // -------------------------------------------------------------------------
  const resetOverlay = document.getElementById('resetOverlay');

  document.getElementById('btnReset')?.addEventListener('click', () => {
    if (resetOverlay) resetOverlay.classList.add('show');
  });

  document.getElementById('resetCancel')?.addEventListener('click', () => {
    if (resetOverlay) resetOverlay.classList.remove('show');
  });

  document.getElementById('resetConfirm')?.addEventListener('click', () => {
    if (resetOverlay) resetOverlay.classList.remove('show');

    fetch('/v2/config/reset', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ client_id: CLIENT_ID })
    })
    .then(r => r.json())
    .then(result => {
      if (result.success) {
        showToast('All settings reset to defaults', 'warning');
        setTimeout(() => window.location.reload(), 500);
      } else {
        showToast('Reset failed: ' + (result.error || 'Unknown error'), 'error');
      }
    })
    .catch(err => showToast('Reset failed: ' + err.message, 'error'));
  });

  // -------------------------------------------------------------------------
  // OPTIMIZATION LEVELS — 3-STATE TOGGLE
  // -------------------------------------------------------------------------
  const STATE_LABELS = { off: 'Off', monitor: 'Monitor Only', active: 'Active' };

  function applyLevelState(row, newState) {
    row.classList.remove('state-off', 'state-monitor', 'state-active');
    row.classList.add('state-' + newState);
    row.querySelectorAll('.level-toggle__opt').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.state === newState);
    });
    const label = row.querySelector('[data-state-label]');
    if (label) label.textContent = STATE_LABELS[newState];
  }

  // Initialise level states from data attributes
  document.querySelectorAll('.level-row').forEach(row => {
    const initialState = row.dataset.initialState || 'off';
    applyLevelState(row, initialState);
  });

  // Wire toggle clicks
  document.querySelectorAll('.level-toggle').forEach(toggle => {
    toggle.querySelectorAll('.level-toggle__opt').forEach(btn => {
      btn.addEventListener('click', () => {
        const row = btn.closest('.level-row');
        const newState = btn.dataset.state;
        applyLevelState(row, newState);
        markDirty();
        const levelName = row.querySelector('.level-row__name')?.textContent || 'Level';
        showToast(levelName + ': ' + STATE_LABELS[newState], newState === 'active' ? 'success' : 'info');
      });
    });
  });

  // Campaign role assignment dropdowns (auto-save on change)
  function refreshRoleStatus() {
    const rows = document.querySelectorAll('.role-assign-table tbody tr');
    const total = rows.length;
    let assigned = 0;
    rows.forEach(r => { if (r.querySelector('.role-assign-select').value) assigned++; });
    const status = document.getElementById('roleStatusText');
    if (status) {
      status.textContent = assigned + ' of ' + total + ' campaigns mapped' +
        (assigned < total ? ' — awaiting assignment' : '');
    }
    const icon = status?.closest('.checklist-item')?.querySelector('.checklist-icon');
    if (icon) {
      const done = (assigned === total && total > 0);
      icon.classList.toggle('checklist-icon--done', done);
      icon.classList.toggle('checklist-icon--pending', !done);
      const iconSpan = icon.querySelector('.material-symbols-outlined');
      if (iconSpan) iconSpan.textContent = done ? 'check' : 'pending';
    }
  }

  document.querySelectorAll('.role-assign-select').forEach(select => {
    select.addEventListener('change', async (e) => {
      const row = e.target.closest('tr');
      const payload = {
        client_id: CLIENT_ID,
        campaign_id: row.dataset.campaignId,
        campaign_name: row.dataset.campaignName,
        role: e.target.value,
      };
      try {
        const res = await fetch('/v2/config/roles/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        const result = await res.json();
        if (result.success) {
          showToast(
            payload.campaign_name + ' → ' + (payload.role || 'Unassigned'),
            payload.role ? 'success' : 'info'
          );
          refreshRoleStatus();
        } else {
          showToast('Role save failed: ' + (result.error || 'Unknown'), 'error');
        }
      } catch (err) {
        showToast('Role save failed: ' + err.message, 'error');
      }
    });
  });

  // ==========================================================================
  // N2 Part 3 + 5 — Negative Lists viewer (read-only) + last-synced pill
  // ==========================================================================
  const NegLists = (() => {
    const root = document.getElementById('negLists');
    if (!root) return { load: () => {}, _loaded: false };
    const clientId = root.dataset.clientId;
    let state = { loaded: false, filter: '', roleFilter: '', data: null };

    // Defence-in-depth: if the template ever renders an empty data-client-id
    // (e.g. wrong Jinja var), surface a human-readable error instead of the
    // raw "client_id required" API response.
    if (!clientId) {
      return {
        load: () => {
          root.innerHTML = '<div class="neg-error" style="padding:18px;color:var(--danger);">No client selected. Please select a client from the top-right dropdown.</div>';
          console.error('[NegLists] clientId missing from #negLists data-client-id');
        },
        _loaded: false,
      };
    }

    function fmtWhen(iso) {
      if (!iso) return '—';
      try {
        const d = new Date(iso);
        const diffMs = Date.now() - d.getTime();
        const mins = Math.floor(diffMs / 60000);
        const hrs = Math.floor(mins / 60);
        const days = Math.floor(hrs / 24);
        const rel = days >= 1 ? `${days}d ago` : hrs >= 1 ? `${hrs}h ago` : `${Math.max(1, mins)}m ago`;
        return `${d.toLocaleString('en-GB', { day:'2-digit', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit' })} (${rel})`;
      } catch { return iso; }
    }

    function syncZoneClass(iso) {
      if (!iso) return 'neg-sync--none';
      const ageHrs = (Date.now() - new Date(iso).getTime()) / 3600000;
      if (ageHrs < 24) return 'neg-sync--green';
      if (ageHrs < 48) return 'neg-sync--amber';
      return 'neg-sync--red';
    }

    async function refresh() {
      const btn = document.getElementById('negListsRefreshBtn');
      if (btn) { btn.disabled = true; btn.textContent = 'Refreshing…'; }
      try {
        const resp = await fetch('/v2/api/negatives/refresh-snapshot', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ client_id: clientId }),
        });
        const data = await resp.json();
        if (resp.status === 409) {
          showToast('Refresh already running.', 'warning');
        } else if (data.status === 'ok') {
          showToast(`Synced ${data.list_count} lists, ${data.keyword_count} keywords in ${data.duration_seconds}s`, 'success');
          await load(true);
        } else {
          showToast('Refresh failed: ' + (data.message || 'Unknown'), 'error');
        }
      } catch (e) {
        showToast('Refresh failed: ' + e.message, 'error');
      } finally {
        if (btn) { btn.disabled = false; btn.innerHTML = '<span class="material-symbols-outlined">refresh</span> Refresh Neg Lists from GAds'; }
      }
    }

    function render() {
      const d = state.data;
      if (!d || d.total_lists === 0) {
        root.innerHTML = `
          <div class="neg-empty" style="padding:24px;border:1px dashed var(--border);border-radius:8px;text-align:center;">
            <p style="margin-bottom:12px;color:var(--text-muted);">No negative list snapshot yet.<br/>Click below to pull current lists from Google Ads.</p>
            <button type="button" class="btn btn--primary" id="negListsRefreshBtn">
              <span class="material-symbols-outlined">refresh</span> Refresh Neg Lists from GAds
            </button>
          </div>`;
        document.getElementById('negListsRefreshBtn')?.addEventListener('click', refresh);
        return;
      }

      // Role filter options
      const roles = Array.from(new Set(d.lists.map(l => l.list_role).filter(Boolean))).sort();
      const roleOptions = ['<option value="">All roles</option>'].concat(
        roles.map(r => `<option value="${r}"${state.roleFilter===r?' selected':''}>${r}</option>`)
      ).join('');

      const zone = syncZoneClass(d.last_synced_at);
      const warnBanner = zone === 'neg-sync--red'
        ? `<div class="neg-warn-banner">Negative list snapshot is over 48 hours old. Click Refresh to pull latest from Google Ads.</div>`
        : '';

      root.innerHTML = `
        ${warnBanner}
        <div class="neg-stats">
          <div class="neg-stat"><span class="neg-stat__label">Total lists</span><span class="neg-stat__val">${d.total_lists}</span></div>
          <div class="neg-stat"><span class="neg-stat__label">Total keywords</span><span class="neg-stat__val">${d.total_keywords}</span></div>
          <div class="neg-stat"><span class="neg-stat__label">Snapshot date</span><span class="neg-stat__val">${d.snapshot_date || '—'}</span></div>
          <div class="neg-stat ${zone}"><span class="neg-stat__label">Last synced</span><span class="neg-stat__val">${fmtWhen(d.last_synced_at)}</span></div>
        </div>
        <div class="neg-actions">
          <button type="button" class="btn btn--primary" id="negListsRefreshBtn">
            <span class="material-symbols-outlined">refresh</span> Refresh Neg Lists from GAds
          </button>
          <input type="search" id="negListsSearch" placeholder="Search keyword across all lists…" class="neg-search" value="${state.filter.replace(/"/g,'&quot;')}"/>
          <select id="negListsRoleFilter" class="neg-role-filter">${roleOptions}</select>
          <span class="neg-match-count" id="negMatchCount"></span>
        </div>
        <div id="negListsContainer" class="neg-lists"></div>
      `;

      document.getElementById('negListsRefreshBtn').addEventListener('click', refresh);
      document.getElementById('negListsSearch').addEventListener('input', e => {
        state.filter = e.target.value.trim().toLowerCase();
        renderLists();
      });
      document.getElementById('negListsRoleFilter').addEventListener('change', e => {
        state.roleFilter = e.target.value;
        renderLists();
      });
      renderLists();
    }

    function renderLists() {
      const container = document.getElementById('negListsContainer');
      if (!container) return;
      const d = state.data;
      const f = state.filter;
      const rf = state.roleFilter;
      let matchingLists = 0;
      let matchingTotal = 0;

      const html = d.lists.filter(l => !rf || l.list_role === rf).map((l) => {
        const matchedKws = f ? l.keywords.filter(k => (k.keyword_text || '').toLowerCase().includes(f)) : l.keywords;
        const hasMatch = f && matchedKws.length > 0;
        if (hasMatch) { matchingLists++; matchingTotal += matchedKws.length; }
        const expanded = hasMatch; // auto-expand on match
        const pageSize = 100;
        const initial = matchedKws.slice(0, pageSize);
        return `
          <div class="neg-list ${expanded?'open':''}" data-list-id="${l.list_id}" data-total="${matchedKws.length}" data-page-size="${pageSize}">
            <div class="neg-list__header">
              <span class="neg-list__toggle material-symbols-outlined">${expanded?'expand_more':'chevron_right'}</span>
              <span class="neg-list__name">${escapeHtml(l.list_name)}</span>
              <span class="neg-list__role">${l.list_role || '—'}</span>
              <span class="neg-list__match">${l.match_type || '—'}</span>
              <span class="neg-list__count">${matchedKws.length}${f ? '/' + l.keyword_count : ''} kw</span>
              <span class="neg-list__linked ${l.is_linked_to_campaign?'linked':'unlinked'}">${l.is_linked_to_campaign?'linked':'unlinked'}</span>
            </div>
            <div class="neg-list__body" style="${expanded?'':'display:none;'}">
              ${matchedKws.length === 0
                ? '<div class="neg-list__empty">No keywords.</div>'
                : `<table class="neg-kw-table">
                    <thead><tr><th>Keyword</th><th>Match</th><th>Added</th><th>By</th></tr></thead>
                    <tbody class="neg-kw-tbody">
                      ${initial.map(k => renderKwRow(k, f)).join('')}
                    </tbody>
                  </table>
                  ${matchedKws.length > pageSize ? `<div class="neg-kw-pager"><button type="button" class="btn btn--ghost neg-kw-more">Load more (${matchedKws.length - pageSize} remaining)</button></div>` : ''}`
              }
            </div>
          </div>`;
      }).join('');

      container.innerHTML = html || '<div style="padding:14px;color:var(--text-muted);">No lists match the current filter.</div>';

      // wire up list toggles
      container.querySelectorAll('.neg-list__header').forEach(h => {
        h.addEventListener('click', () => {
          const wrap = h.closest('.neg-list');
          const body = wrap.querySelector('.neg-list__body');
          const toggle = wrap.querySelector('.neg-list__toggle');
          const open = wrap.classList.toggle('open');
          body.style.display = open ? '' : 'none';
          toggle.textContent = open ? 'expand_more' : 'chevron_right';
        });
      });

      // Load-more pager — client-side slice into full dataset
      container.querySelectorAll('.neg-kw-more').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          const wrap = btn.closest('.neg-list');
          const listId = wrap.dataset.listId;
          const list = d.lists.find(x => x.list_id === listId);
          const matched = f ? list.keywords.filter(k => (k.keyword_text || '').toLowerCase().includes(f)) : list.keywords;
          const tbody = wrap.querySelector('.neg-kw-tbody');
          const shown = tbody.querySelectorAll('tr').length;
          const next = matched.slice(shown, shown + 100);
          tbody.insertAdjacentHTML('beforeend', next.map(k => renderKwRow(k, f)).join(''));
          const remaining = matched.length - (shown + next.length);
          if (remaining <= 0) btn.parentElement.remove();
          else btn.textContent = `Load more (${remaining} remaining)`;
        });
      });

      const counter = document.getElementById('negMatchCount');
      if (counter) counter.textContent = f ? `Found in ${matchingLists} list${matchingLists===1?'':'s'}: ${matchingTotal} keyword${matchingTotal===1?'':'s'}` : '';
    }

    function renderKwRow(k, filter) {
      const txt = escapeHtml(k.keyword_text || '');
      const highlighted = filter
        ? txt.replace(new RegExp('('+filter.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')', 'ig'), '<mark>$1</mark>')
        : txt;
      const when = k.added_at ? new Date(k.added_at).toLocaleDateString('en-GB') : '—';
      return `<tr><td>${highlighted}</td><td>${k.match_type || ''}</td><td>${when}</td><td>${k.added_by || ''}</td></tr>`;
    }

    function escapeHtml(s) {
      return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    }

    async function load(force) {
      if (state.loaded && !force) return;
      try {
        const resp = await fetch(`/v2/api/negatives/lists?client_id=${encodeURIComponent(clientId)}`);
        const data = await resp.json();
        if (data.status !== 'ok') throw new Error(data.detail || 'failed');
        state.data = data;
        state.loaded = true;
        NegLists._loaded = true;
        render();
      } catch (e) {
        root.innerHTML = `<div style="padding:18px;color:var(--danger);">Failed to load negative lists: ${e.message}</div>`;
      }
    }

    return { load, refresh, _loaded: false };
  })();

});
