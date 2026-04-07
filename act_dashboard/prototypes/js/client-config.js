/* ============================================================================
   ACT PROTOTYPE — CLIENT CONFIGURATION INTERACTIONS
   Updated: Save disable/enable on change, field-level validation
   ============================================================================ */

document.addEventListener('DOMContentLoaded', () => {

  const btnSave = document.getElementById('btnSave');

  // -------------------------------------------------------------------------
  // THEME TOGGLE
  // -------------------------------------------------------------------------
  const themeToggle = document.querySelector('.theme-toggle');
  if (themeToggle) {
    if (document.documentElement.getAttribute('data-theme') === 'dark') themeToggle.classList.add('night');
    themeToggle.addEventListener('click', () => {
      const html = document.documentElement;
      const goingDark = html.getAttribute('data-theme') === 'light';
      themeToggle.classList.add('transitioning');
      if (goingDark) themeToggle.classList.add('night'); else themeToggle.classList.remove('night');
      setTimeout(() => html.setAttribute('data-theme', goingDark ? 'dark' : 'light'), 400);
      setTimeout(() => themeToggle.classList.remove('transitioning'), 1000);
    });
  }

  // -------------------------------------------------------------------------
  // CLIENT SWITCHER
  // -------------------------------------------------------------------------
  const clientBtn = document.getElementById('clientSwitcher');
  const clientMenu = document.getElementById('clientMenu');
  if (clientBtn && clientMenu) {
    clientBtn.addEventListener('click', (e) => { e.stopPropagation(); clientMenu.classList.toggle('show'); });
    document.addEventListener('click', () => clientMenu.classList.remove('show'));
    clientMenu.querySelectorAll('.dropdown-item').forEach(item => {
      item.addEventListener('click', () => {
        const name = item.textContent.trim();
        clientBtn.querySelector('.client-name').textContent = name;
        document.querySelector('.config-header__sub').textContent = `Settings for ${name}`;
        clientMenu.querySelectorAll('.dropdown-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        clientMenu.classList.remove('show');
        showToast(`Switched to ${name}`, 'info');
      });
    });
  }

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
  // TOGGLE SWITCHES — also mark dirty
  // -------------------------------------------------------------------------
  document.querySelectorAll('.config-toggle').forEach(toggle => {
    toggle.addEventListener('click', () => {
      toggle.classList.toggle('on');
      markDirty();
    });
  });

  // -------------------------------------------------------------------------
  // PERSONA SWITCHER (CPA ↔ ROAS)
  // -------------------------------------------------------------------------
  const personaSelect = document.getElementById('settingPersona');
  const targetCpaRow = document.getElementById('rowTargetCpa');
  const targetRoasRow = document.getElementById('rowTargetRoas');

  if (personaSelect) {
    personaSelect.addEventListener('change', () => {
      const isLeadGen = personaSelect.value === 'leadgen';
      if (targetCpaRow) targetCpaRow.style.display = isLeadGen ? '' : 'none';
      if (targetRoasRow) targetRoasRow.style.display = isLeadGen ? 'none' : '';
      markDirty();
    });
  }

  // -------------------------------------------------------------------------
  // FIELD-LEVEL VALIDATION (Change 3)
  // -------------------------------------------------------------------------
  function setupValidation() {
    document.querySelectorAll('.config-input[type="number"]').forEach(input => {
      // Determine validation rules from context
      const suffix = input.closest('.input-group')?.querySelector('.input-group__suffix')?.textContent || '';
      const isPercent = suffix.includes('%');
      const isCurrency = suffix.includes('£');
      const isCooldown = suffix.includes('hours') || suffix.includes('days');
      const isMultiWeight = input.closest('.multi-input') && (input.id === 'weight7d' || input.id === 'weight14d' || input.id === 'weight30d');

      // Store rules on element
      input.dataset.valMin = '0';
      if (isPercent && !isMultiWeight) input.dataset.valMax = '100';

      // Get or create error element
      let errorEl = input.parentElement.querySelector('.field-error');
      if (!errorEl) {
        errorEl = document.createElement('div');
        errorEl.className = 'field-error';
        // Insert after the input-group or the input itself
        const parent = input.closest('.input-group') || input;
        parent.parentElement.insertBefore(errorEl, parent.nextSibling);
      }

      input.addEventListener('input', () => {
        validateField(input, errorEl);
        markDirty();
      });
    });

    // Also listen on selects
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
      errorEl.textContent = `Cannot be negative`;
      errorEl.classList.add('show');
      return false;
    }

    if (max !== null && val > max) {
      input.classList.add('invalid');
      errorEl.textContent = `Maximum ${max}%`;
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
      weightMsg.textContent = 'Weights sum to 100% — valid';
    } else {
      weightMsg.className = 'validation-msg validation-msg--error show';
      weightMsg.textContent = `Weights sum to ${total}% — must equal 100%`;
    }
    updateSaveButton();
  }

  [w7, w14, w30].forEach(el => { if (el) el.addEventListener('input', validateWeights); });

  // -------------------------------------------------------------------------
  // DIRTY STATE + SAVE BUTTON (Change 2)
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
  // SAVE / RESET
  // -------------------------------------------------------------------------
  btnSave?.addEventListener('click', () => {
    if (btnSave.classList.contains('btn-save--disabled')) return;
    showToast('Settings saved', 'success');
    isDirty = false;
    updateSaveButton();
    const saved = document.querySelector('.config-header__saved');
    if (saved) {
      saved.innerHTML = `<span class="material-symbols-outlined">schedule</span>Last saved: just now`;
    }
  });

  const resetOverlay = document.getElementById('resetOverlay');
  document.getElementById('btnReset')?.addEventListener('click', () => {
    if (resetOverlay) resetOverlay.classList.add('show');
  });

  document.getElementById('resetCancel')?.addEventListener('click', () => {
    if (resetOverlay) resetOverlay.classList.remove('show');
  });

  document.getElementById('resetConfirm')?.addEventListener('click', () => {
    if (resetOverlay) resetOverlay.classList.remove('show');
    isDirty = false;
    updateSaveButton();
    showToast('All settings reset to defaults', 'warning');
  });

  // -------------------------------------------------------------------------
  // ONBOARDING
  // -------------------------------------------------------------------------
  document.getElementById('btnOnboard')?.addEventListener('click', () => {
    showToast('Onboarding complete — 9 negative keyword lists created', 'success');
  });

  // -------------------------------------------------------------------------
  // TOAST
  // -------------------------------------------------------------------------
  function showToast(message, type = 'info') {
    document.querySelectorAll('.act-toast').forEach(t => t.remove());
    const toast = document.createElement('div');
    toast.className = `act-toast act-toast--${type}`;
    toast.innerHTML = `<span class="material-symbols-outlined" style="font-size:18px">${
      type === 'success' ? 'check_circle' : type === 'warning' ? 'undo' : type === 'error' ? 'error' : 'info'
    }</span>${message}`;
    document.body.appendChild(toast);
    requestAnimationFrame(() => { requestAnimationFrame(() => toast.classList.add('show')); });
    setTimeout(() => { toast.classList.remove('show'); setTimeout(() => toast.remove(), 300); }, 3000);
  }

});
