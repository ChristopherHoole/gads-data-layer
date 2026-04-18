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

  // --- Approve (individual) ---
  document.querySelectorAll('[data-action="approve"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const recId = btn.dataset.recId;
      const item = btn.closest('.act-item');
      if (!recId) return;
      fetch('/v2/api/recommendations/' + recId + '/approve', { method: 'POST' })
        .then(r => r.json())
        .then(res => {
          if (res.success) {
            markActioned(item, 'approved', 'Approved');
            showToast('Approved — change will be applied in next cycle', 'success');
            decrementCount('sectionApproval');
          } else {
            showToast('Approve failed: ' + (res.error || 'unknown'), 'error');
          }
        })
        .catch(err => showToast('Approve failed: ' + err.message, 'error'));
    });
  });

  // --- Decline ---
  document.querySelectorAll('[data-action="decline"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const recId = btn.dataset.recId;
      const item = btn.closest('.act-item');
      if (!recId) return;
      fetch('/v2/api/recommendations/' + recId + '/decline', { method: 'POST' })
        .then(r => r.json())
        .then(res => {
          if (res.success) {
            markActioned(item, 'declined', 'Declined');
            showToast('Declined — no changes will be made', 'info');
            decrementCount('sectionApproval');
          } else {
            showToast('Decline failed: ' + (res.error || 'unknown'), 'error');
          }
        })
        .catch(err => showToast('Decline failed: ' + err.message, 'error'));
    });
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
      const checked = Array.from(document.querySelectorAll('#sectionApproval .act-item__check input:checked'));
      const ids = checked.map(cb => cb.closest('.act-item').dataset.recId).filter(Boolean);
      if (!ids.length) return;
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
        } else {
          showToast('Bulk approve failed: ' + (res.error || 'unknown'), 'error');
        }
      })
      .catch(err => showToast('Bulk approve failed: ' + err.message, 'error'));
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

  // --- Slide-in panel ---
  const slideinOverlay = document.getElementById('slideinOverlay');
  const slideinPanel = document.getElementById('slideinPanel');
  const slideinBody = document.getElementById('slideinBody');
  const slideinFooter = document.getElementById('slideinFooter');

  document.querySelectorAll('[data-action="details"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const item = btn.closest('.act-item');
      if (!item || !slideinPanel || !slideinBody) return;
      const summary = item.querySelector('.act-item__summary')?.innerHTML || '';
      const badges = item.querySelector('.act-item__top')?.innerHTML || '';
      const decisionTree = item.dataset.details ? JSON.parse(item.dataset.details) : null;
      let html = '<div style="margin-bottom:12px">' + badges + '</div>';
      html += '<div style="font-size:14px;line-height:1.6;margin-bottom:16px">' + summary + '</div>';
      if (decisionTree) {
        html += '<dl class="act-detail-grid">';
        for (const [key, val] of Object.entries(decisionTree)) {
          html += '<dt>' + key + '</dt><dd>' + val + '</dd>';
        }
        html += '</dl>';
      }
      slideinBody.innerHTML = html;
      if (slideinFooter) slideinFooter.innerHTML = '';
      slideinOverlay?.classList.add('open');
      slideinPanel?.classList.add('open');
    });
  });

  window.closeSlidein = function() {
    slideinOverlay?.classList.remove('open');
    slideinPanel?.classList.remove('open');
  };
  slideinOverlay?.addEventListener('click', closeSlidein);
  document.getElementById('slideinClose')?.addEventListener('click', closeSlidein);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeSlidein(); });

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
