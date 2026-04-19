/* ============================================================================
   ACT v2 — Morning Review Page Interactions
   Section/group collapse, approve/decline, bulk approve, undo, slide-in
   ============================================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // --- Section collapse (ignore clicks on bulk-bar) ---
  document.querySelectorAll('.act-section__header').forEach(header => {
    header.addEventListener('click', (e) => {
      if (e.target.closest('.act-bulk-bar')) return;
      header.closest('.act-section').classList.toggle('collapsed');
    });
  });

  // --- Group collapse ---
  document.querySelectorAll('.act-group__header').forEach(header => {
    header.addEventListener('click', (e) => {
      e.stopPropagation();
      header.closest('.act-group').classList.toggle('collapsed');
    });
  });

  // --- Approve / Decline (guarded against double-click) ---
  function handleMRAction(btn, action, label, toastMsg, toastKind) {
    if (btn.classList.contains('btn-act--pending')) return;
    const recId = btn.dataset.recId;
    const item = btn.closest('.act-item');
    if (!recId) return;
    btn.classList.add('btn-act--pending');
    btn.disabled = true;
    if (item) item.querySelectorAll('.btn-act--approve, .btn-act--decline').forEach(b => { b.disabled = true; });
    fetch('/v2/api/recommendations/' + recId + '/' + action, { method: 'POST' })
      .then(r => r.json())
      .then(res => {
        if (res && res.success) {
          markActioned(item, label, label.charAt(0).toUpperCase() + label.slice(1));
          showToast(toastMsg, toastKind);
          decrementCount('sectionApproval');
        } else {
          showToast(action + ' failed: ' + ((res && res.error) || 'unknown'), 'error');
          btn.classList.remove('btn-act--pending'); btn.disabled = false;
          if (item) item.querySelectorAll('.btn-act--approve, .btn-act--decline').forEach(b => { b.disabled = false; });
        }
      })
      .catch(err => {
        showToast(action + ' failed: ' + err.message, 'error');
        btn.classList.remove('btn-act--pending'); btn.disabled = false;
        if (item) item.querySelectorAll('.btn-act--approve, .btn-act--decline').forEach(b => { b.disabled = false; });
      });
  }

  document.querySelectorAll('[data-action="approve"]').forEach(btn => {
    btn.addEventListener('click', (e) => { e.stopPropagation(); handleMRAction(btn, 'approve', 'approved', 'Approved — change will be applied in next cycle', 'success'); });
  });
  document.querySelectorAll('[data-action="decline"]').forEach(btn => {
    btn.addEventListener('click', (e) => { e.stopPropagation(); handleMRAction(btn, 'decline', 'declined', 'Declined — no changes will be made', 'info'); });
  });

  // --- Bulk approve ---
  const bulkBtn = document.getElementById('bulkApproveBtn');
  const bulkLabel = document.getElementById('bulkLabel');
  const selectAll = document.getElementById('bulkSelectAll');

  function updateBulkLabel() {
    const checked = Array.from(document.querySelectorAll('#sectionApproval .act-item__check input:checked'));
    const count = checked.length;
    if (bulkLabel) bulkLabel.textContent = 'Approve Selected (' + count + ')';
    if (bulkBtn) bulkBtn.disabled = count === 0;
  }

  document.querySelectorAll('#sectionApproval .act-item__check input').forEach(cb => {
    cb.addEventListener('change', updateBulkLabel);
  });

  if (selectAll) {
    selectAll.addEventListener('change', () => {
      const all = document.querySelectorAll('#sectionApproval .act-item:not(.actioned) .act-item__check input');
      all.forEach(cb => { cb.checked = selectAll.checked; });
      updateBulkLabel();
    });
  }

  if (bulkBtn) {
    bulkBtn.addEventListener('click', () => {
      if (bulkBtn.classList.contains('btn-act--pending')) return;
      const checked = Array.from(document.querySelectorAll('#sectionApproval .act-item__check input:checked'));
      const ids = checked.map(cb => cb.closest('.act-item').dataset.recId).filter(Boolean);
      if (!ids.length) return;
      bulkBtn.classList.add('btn-act--pending');
      bulkBtn.disabled = true;
      fetch('/v2/api/recommendations/bulk-approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: ids.map(n => parseInt(n, 10)) })
      })
      .then(r => r.json())
      .then(res => {
        if (res.success) {
          let ok = 0;
          res.results.forEach(r => {
            if (r.success) {
              const cb = document.querySelector('#sectionApproval .act-item[data-rec-id="' + r.id + '"] .act-item__check input');
              if (cb) {
                cb.checked = false;
                markActioned(cb.closest('.act-item'), 'approved', 'Approved');
              }
              ok++;
            }
          });
          for (let i = 0; i < ok; i++) decrementCount('sectionApproval');
          if (selectAll) selectAll.checked = false;
          updateBulkLabel();
          showToast(ok + ' recommendations approved', 'success');
          bulkBtn.classList.remove('btn-act--pending');
        } else {
          showToast('Bulk approve failed: ' + (res.error || 'unknown'), 'error');
          bulkBtn.classList.remove('btn-act--pending');
          bulkBtn.disabled = false;
        }
      })
      .catch(err => {
        showToast('Bulk approve failed: ' + err.message, 'error');
        bulkBtn.classList.remove('btn-act--pending');
        bulkBtn.disabled = false;
      });
    });
  }

  // --- Undo request (on executed actions) ---
  document.querySelectorAll('[data-action="undo"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const actionId = btn.dataset.actionId;
      const item = btn.closest('.act-item');
      if (!actionId) return;
      fetch('/v2/api/actions/' + actionId + '/undo-request', { method: 'POST' })
        .then(r => r.json())
        .then(res => {
          if (res.success) {
            btn.disabled = true;
            btn.textContent = 'Undo requested';
            const badge = document.createElement('span');
            badge.className = 'undo-requested';
            badge.textContent = 'Undo requested';
            const top = item.querySelector('.act-item__top');
            if (top) top.appendChild(badge);
            showToast('Undo requested — revert will apply when execution layer is live', 'warning');
          } else {
            showToast('Undo failed: ' + (res.error || 'unknown'), 'error');
          }
        })
        .catch(err => showToast('Undo failed: ' + err.message, 'error'));
    });
  });

  // Slide-in panel handled by shared v2_decision_details.js
  // (auto-wires [data-action="details"] clicks and Escape/overlay close).

  // --- Helpers ---
  function markActioned(item, cssStatus, label) {
    if (!item) return;
    item.classList.add('actioned');
    item.style.opacity = '0.55';
    item.querySelectorAll('[data-action="approve"], [data-action="decline"]').forEach(b => {
      b.style.display = 'none';
    });
    const top = item.querySelector('.act-item__top');
    if (top) {
      const badge = document.createElement('span');
      badge.className = 'act-item__status-badge act-item__status-badge--' + cssStatus;
      badge.textContent = label;
      badge.style.cssText = 'font-size:11px;font-weight:600;padding:2px 8px;border-radius:10px;background:' +
        (cssStatus === 'approved' ? 'var(--act-green)' : 'var(--act-hover-bg)') +
        ';color:' + (cssStatus === 'approved' ? 'white' : 'var(--act-text)') + ';';
      top.appendChild(badge);
    }
    const cb = item.querySelector('.act-item__check input');
    if (cb) cb.checked = false;
  }

  function decrementCount(sectionId) {
    const section = document.getElementById(sectionId);
    if (!section) return;
    const badge = section.querySelector('.act-section__count');
    if (!badge) return;
    const current = parseInt(badge.textContent, 10) || 0;
    if (current > 0) badge.textContent = current - 1;
    // Also update the status card
    const card = document.querySelector('[data-colour="amber"] .status-card__count');
    if (card) {
      const cur = parseInt(card.textContent, 10) || 0;
      if (cur > 0) card.textContent = cur - 1;
    }
  }

});
