/* ============================================================================
   ACT PROTOTYPE — MORNING REVIEW INTERACTIONS
   ============================================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // -------------------------------------------------------------------------
  // CLIENT SWITCHER
  // -------------------------------------------------------------------------
  const clientBtn = document.getElementById('clientSwitcher');
  const clientMenu = document.getElementById('clientMenu');
  if (clientBtn && clientMenu) {
    clientBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      clientMenu.classList.toggle('show');
    });
    document.addEventListener('click', () => clientMenu.classList.remove('show'));
    clientMenu.querySelectorAll('.dropdown-item').forEach(item => {
      item.addEventListener('click', () => {
        const name = item.textContent.trim();
        clientBtn.querySelector('.client-name').textContent = name;
        clientMenu.querySelectorAll('.dropdown-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        clientMenu.classList.remove('show');
        showToast(`Switched to ${name}`, 'info');
      });
    });
  }

  // -------------------------------------------------------------------------
  // STATUS CARD FILTERING
  // -------------------------------------------------------------------------
  const statusCards = document.querySelectorAll('.status-card');
  const sections = {
    green: document.getElementById('sectionExecuted'),
    amber: document.getElementById('sectionApproval'),
    blue: document.getElementById('sectionMonitoring'),
    red: document.getElementById('sectionAlerts'),
  };

  let activeFilter = null;

  statusCards.forEach(card => {
    card.addEventListener('click', () => {
      const colour = card.dataset.colour;
      if (activeFilter === colour) {
        // Deselect — show all
        activeFilter = null;
        statusCards.forEach(c => c.classList.remove('active'));
        Object.values(sections).forEach(s => { if (s) s.style.display = ''; });
      } else {
        activeFilter = colour;
        statusCards.forEach(c => c.classList.toggle('active', c.dataset.colour === colour));
        Object.entries(sections).forEach(([key, s]) => {
          if (s) s.style.display = (key === colour) ? '' : 'none';
        });
      }
    });
  });

  // -------------------------------------------------------------------------
  // SECTION COLLAPSE / EXPAND
  // -------------------------------------------------------------------------
  document.querySelectorAll('.act-section__header').forEach(header => {
    header.addEventListener('click', (e) => {
      // Don't collapse if clicking bulk actions inside header
      if (e.target.closest('.act-bulk-bar')) return;
      const section = header.closest('.act-section');
      section.classList.toggle('collapsed');
    });
  });

  // -------------------------------------------------------------------------
  // APPROVE / DECLINE BUTTONS
  // -------------------------------------------------------------------------
  document.querySelectorAll('[data-action="approve"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const item = btn.closest('.act-item');
      item.style.opacity = '0.4';
      item.style.pointerEvents = 'none';
      showToast('Approved — change will be applied in next cycle', 'success');
      updateApprovalCount(-1);
    });
  });

  document.querySelectorAll('[data-action="decline"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const item = btn.closest('.act-item');
      item.style.opacity = '0.4';
      item.style.pointerEvents = 'none';
      showToast('Declined — no changes will be made', 'info');
      updateApprovalCount(-1);
    });
  });

  // -------------------------------------------------------------------------
  // UNDO BUTTONS
  // -------------------------------------------------------------------------
  document.querySelectorAll('[data-action="undo"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const item = btn.closest('.act-item');
      item.style.opacity = '0.4';
      item.style.pointerEvents = 'none';
      showToast('Undo queued — will be reverted in next cycle', 'warning');
    });
  });

  // -------------------------------------------------------------------------
  // VIEW DETAILS EXPAND
  // -------------------------------------------------------------------------
  document.querySelectorAll('[data-action="details"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const item = btn.closest('.act-item');
      const details = item.querySelector('.act-item__details');
      if (details) {
        details.classList.toggle('show');
        btn.textContent = details.classList.contains('show') ? 'Hide Details' : 'View Details';
      }
    });
  });

  // -------------------------------------------------------------------------
  // BULK SELECT
  // -------------------------------------------------------------------------
  const bulkSelectAll = document.getElementById('bulkSelectAll');
  const bulkApproveBtn = document.getElementById('bulkApproveBtn');
  const bulkCount = document.getElementById('bulkCount');

  if (bulkSelectAll) {
    bulkSelectAll.addEventListener('change', () => {
      const checks = document.querySelectorAll('#sectionApproval .act-item__check input');
      checks.forEach(c => { c.checked = bulkSelectAll.checked; });
      updateBulkCount();
    });
  }

  document.querySelectorAll('#sectionApproval .act-item__check input').forEach(cb => {
    cb.addEventListener('change', updateBulkCount);
  });

  if (bulkApproveBtn) {
    bulkApproveBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const checked = document.querySelectorAll('#sectionApproval .act-item__check input:checked');
      if (checked.length === 0) return;
      checked.forEach(cb => {
        const item = cb.closest('.act-item');
        item.style.opacity = '0.4';
        item.style.pointerEvents = 'none';
      });
      showToast(`${checked.length} item${checked.length > 1 ? 's' : ''} approved`, 'success');
      updateApprovalCount(-checked.length);
    });
  }

  function updateBulkCount() {
    const count = document.querySelectorAll('#sectionApproval .act-item__check input:checked').length;
    if (bulkCount) bulkCount.textContent = count;
    if (bulkApproveBtn) bulkApproveBtn.disabled = count === 0;
  }

  function updateApprovalCount(delta) {
    const card = document.querySelector('.status-card--amber .status-card__count');
    const badge = document.querySelector('#sectionApproval .act-section__count');
    if (card) {
      const val = Math.max(0, parseInt(card.textContent) + delta);
      card.textContent = val;
    }
    if (badge) {
      const val = Math.max(0, parseInt(badge.textContent) + delta);
      badge.textContent = val;
    }
  }

  // -------------------------------------------------------------------------
  // TOAST NOTIFICATION
  // -------------------------------------------------------------------------
  function showToast(message, type = 'info') {
    // Remove any existing toast
    document.querySelectorAll('.act-toast').forEach(t => t.remove());

    const toast = document.createElement('div');
    toast.className = `act-toast act-toast--${type}`;
    toast.innerHTML = `<span class="material-symbols-outlined" style="font-size:18px">${
      type === 'success' ? 'check_circle' :
      type === 'warning' ? 'undo' :
      type === 'error' ? 'error' : 'info'
    }</span>${message}`;
    document.body.appendChild(toast);

    requestAnimationFrame(() => {
      requestAnimationFrame(() => toast.classList.add('show'));
    });

    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

});
