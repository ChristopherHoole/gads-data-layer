/* ============================================================================
   ACT PROTOTYPE v3 — MORNING REVIEW INTERACTIONS
   v3: View Details stays clickable after approve/decline (Change 6)
   ============================================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // -------------------------------------------------------------------------
  // THEME TOGGLE
  // -------------------------------------------------------------------------
  const themeToggle = document.querySelector('.theme-toggle');
  if (themeToggle) {
    if (document.documentElement.getAttribute('data-theme') === 'dark') {
      themeToggle.classList.add('night');
    }
    themeToggle.addEventListener('click', () => {
      const html = document.documentElement;
      const goingDark = html.getAttribute('data-theme') === 'light';
      themeToggle.classList.add('transitioning');
      if (goingDark) { themeToggle.classList.add('night'); }
      else { themeToggle.classList.remove('night'); }
      setTimeout(() => { html.setAttribute('data-theme', goingDark ? 'dark' : 'light'); }, 400);
      setTimeout(() => { themeToggle.classList.remove('transitioning'); }, 1000);
    });
  }

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
  // SECTION + GROUP COLLAPSE
  // -------------------------------------------------------------------------
  document.querySelectorAll('.act-section__header').forEach(header => {
    header.addEventListener('click', (e) => {
      if (e.target.closest('.act-bulk-bar')) return;
      header.closest('.act-section').classList.toggle('collapsed');
    });
  });

  document.querySelectorAll('.act-group__header').forEach(header => {
    header.addEventListener('click', (e) => {
      e.stopPropagation();
      header.closest('.act-group').classList.toggle('collapsed');
    });
  });

  // -------------------------------------------------------------------------
  // v3 Change 6: APPROVE / DECLINE — fade but keep View Details clickable
  // -------------------------------------------------------------------------
  function markActioned(item, status) {
    item.classList.add('actioned');
    // Add status badge after the action badges
    const top = item.querySelector('.act-item__top');
    if (top) {
      const badge = document.createElement('span');
      badge.className = `act-item__status-badge act-item__status-badge--${status}`;
      badge.textContent = status === 'approved' ? 'Approved' : 'Declined';
      top.appendChild(badge);
    }
    // Uncheck if checked
    const cb = item.querySelector('.act-item__check input');
    if (cb) cb.checked = false;
  }

  document.querySelectorAll('[data-action="approve"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const item = btn.closest('.act-item');
      if (item.classList.contains('actioned')) return;
      markActioned(item, 'approved');
      showToast('Approved — change will be applied in next cycle', 'success');
      updateApprovalCount(-1);
      closeSlidein();
    });
  });

  document.querySelectorAll('[data-action="decline"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const item = btn.closest('.act-item');
      if (item.classList.contains('actioned')) return;
      markActioned(item, 'declined');
      showToast('Declined — no changes will be made', 'info');
      updateApprovalCount(-1);
      closeSlidein();
    });
  });

  // -------------------------------------------------------------------------
  // UNDO BUTTONS
  // -------------------------------------------------------------------------
  document.querySelectorAll('[data-action="undo"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const item = btn.closest('.act-item');
      item.classList.add('actioned');
      btn.style.display = 'none';
      showToast('Undo queued — will be reverted in next cycle', 'warning');
    });
  });

  // -------------------------------------------------------------------------
  // SLIDE-IN PANEL
  // -------------------------------------------------------------------------
  const slideinOverlay = document.getElementById('slideinOverlay');
  const slideinPanel = document.getElementById('slideinPanel');
  const slideinBody = document.getElementById('slideinBody');
  const slideinTitle = document.getElementById('slideinTitle');
  const slideinFooter = document.getElementById('slideinFooter');

  function openSlidein(item) {
    if (!slideinPanel || !slideinBody) return;

    const summary = item.querySelector('.act-item__summary')?.innerHTML || '';
    const levelBadge = item.querySelector('.badge-level')?.outerHTML || '';
    const actionBadge = item.querySelector('.badge-action')?.outerHTML || '';
    const riskBadge = item.querySelector('.badge-risk')?.outerHTML || '';
    const recommendation = item.querySelector('.act-item__recommendation')?.textContent || '';
    const detailData = item.dataset.details ? JSON.parse(item.dataset.details) : null;
    const isActioned = item.classList.contains('actioned');

    if (slideinTitle) slideinTitle.innerHTML = 'Decision Details';

    let html = `
      <div class="act-slidein__section">
        <div class="act-slidein__section-title">Item</div>
        <div style="display:flex;gap:6px;margin-bottom:8px;flex-wrap:wrap">${levelBadge} ${actionBadge} ${riskBadge}</div>
        <div class="act-slidein__summary">${summary}</div>
      </div>
    `;

    if (recommendation) {
      html += `
        <div class="act-slidein__section">
          <div class="act-slidein__section-title">Recommendation</div>
          <div style="font-size:14px;color:var(--act-text);line-height:1.5">${recommendation.replace('lightbulb', '').trim()}</div>
        </div>
      `;
    }

    if (detailData) {
      html += `<div class="act-slidein__section"><div class="act-slidein__section-title">Decision Tree Reasoning</div><dl class="act-detail-grid">`;
      for (const [key, val] of Object.entries(detailData)) {
        html += `<dt>${key}</dt><dd>${val}</dd>`;
      }
      html += `</dl></div>`;
    }

    slideinBody.innerHTML = html;

    // Footer: show Approve/Decline only if NOT already actioned
    const approveBtn = item.querySelector('[data-action="approve"]');
    if (slideinFooter && approveBtn && !isActioned) {
      slideinFooter.innerHTML = `
        <button class="btn-act btn-act--decline" onclick="document.querySelector('.act-item[data-slidein-active] [data-action=\\'decline\\']')?.click();">Decline</button>
        <button class="btn-act btn-act--approve" onclick="document.querySelector('.act-item[data-slidein-active] [data-action=\\'approve\\']')?.click();">Approve</button>
      `;
      slideinFooter.style.display = '';
    } else if (slideinFooter) {
      if (isActioned) {
        const statusBadge = item.querySelector('.act-item__status-badge');
        slideinFooter.innerHTML = `<span style="font-size:14px;color:var(--act-text)">${statusBadge ? statusBadge.textContent : 'Actioned'}</span>`;
        slideinFooter.style.display = '';
      } else {
        slideinFooter.style.display = 'none';
      }
    }

    document.querySelectorAll('[data-slidein-active]').forEach(el => el.removeAttribute('data-slidein-active'));
    item.setAttribute('data-slidein-active', '');
    slideinOverlay?.classList.add('open');
    slideinPanel?.classList.add('open');
  }

  window.closeSlidein = function() {
    slideinOverlay?.classList.remove('open');
    slideinPanel?.classList.remove('open');
    document.querySelectorAll('[data-slidein-active]').forEach(el => el.removeAttribute('data-slidein-active'));
  };

  slideinOverlay?.addEventListener('click', closeSlidein);
  document.getElementById('slideinClose')?.addEventListener('click', closeSlidein);

  document.querySelectorAll('[data-action="details"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      openSlidein(btn.closest('.act-item'));
    });
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeSlidein();
  });

  // -------------------------------------------------------------------------
  // BULK SELECT
  // -------------------------------------------------------------------------
  const bulkSelectAll = document.getElementById('bulkSelectAll');
  const bulkApproveBtn = document.getElementById('bulkApproveBtn');
  const bulkLabel = document.getElementById('bulkLabel');

  if (bulkSelectAll) {
    bulkSelectAll.addEventListener('change', () => {
      const checks = document.querySelectorAll('#sectionApproval .act-item:not(.actioned) .act-item__check input');
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
      const checked = document.querySelectorAll('#sectionApproval .act-item:not(.actioned) .act-item__check input:checked');
      if (checked.length === 0) return;
      checked.forEach(cb => {
        const item = cb.closest('.act-item');
        markActioned(item, 'approved');
      });
      showToast(`${checked.length} item${checked.length > 1 ? 's' : ''} approved`, 'success');
      updateApprovalCount(-checked.length);
      updateBulkCount();
    });
  }

  function updateBulkCount() {
    const checkedItems = document.querySelectorAll('#sectionApproval .act-item:not(.actioned) .act-item__check input:checked');
    const count = checkedItems.length;
    let low = 0, med = 0, high = 0;
    checkedItems.forEach(cb => {
      const risk = cb.closest('.act-item')?.dataset.risk || 'low';
      if (risk === 'low') low++;
      else if (risk === 'medium') med++;
      else if (risk === 'high') high++;
    });

    if (bulkLabel) {
      if (count === 0) {
        bulkLabel.textContent = 'Approve Selected (0)';
      } else {
        let parts = [];
        if (low > 0) parts.push(`${low} low-risk`);
        if (med > 0) parts.push(`${med} medium-risk`);
        if (high > 0) parts.push(`${high} high-risk`);
        bulkLabel.textContent = `Approve Selected (${parts.join(', ')})`;
      }
    }
    if (bulkApproveBtn) bulkApproveBtn.disabled = count === 0;
  }

  function updateApprovalCount(delta) {
    const card = document.querySelector('.status-card--amber .status-card__count');
    const badge = document.querySelector('#sectionApproval .act-section__count');
    if (card) card.textContent = Math.max(0, parseInt(card.textContent) + delta);
    if (badge) badge.textContent = Math.max(0, parseInt(badge.textContent) + delta);
  }

  // -------------------------------------------------------------------------
  // TOAST
  // -------------------------------------------------------------------------
  function showToast(message, type = 'info') {
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
