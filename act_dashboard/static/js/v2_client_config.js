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

});
