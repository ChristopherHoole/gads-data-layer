/* N3 — Rejected Terms page front-end. Lists sticky rejections, supports
   status filter, text search, manual unreject + cycle-history inline row,
   live countdowns (1-min tick). Mirrors the search_term_review toast helper. */
(function () {
  const CLIENT = (window.RT_CONFIG || {}).client_id;
  const body = document.getElementById('rtBody');
  const toastEl = document.getElementById('rtToast');
  let state = {
    items: [],
    status: 'active',
    search: '',
    page: 1,
    pageSize: 100,
  };

  function toast(msg, kind) {
    toastEl.textContent = msg;
    toastEl.className = 'rt-toast' + (kind === 'error' ? ' rt-toast--error' : '');
    toastEl.style.display = 'block';
    clearTimeout(toast._t);
    toast._t = setTimeout(() => { toastEl.style.display = 'none'; }, 4500);
  }

  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g,
      c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  function formatCountdown(expiresAt, unrejectedAt) {
    if (unrejectedAt) return { text: 'UNREJECTED', cls: 'countdown--expired' };
    if (!expiresAt) return { text: '—', cls: '' };
    const ms = new Date(expiresAt) - Date.now();
    if (ms <= 0) return { text: 'EXPIRED', cls: 'countdown--expired' };
    const days = Math.floor(ms / 86400000);
    const hours = Math.floor(ms / 3600000);
    if (days >= 2) return { text: `${days} days`, cls: 'countdown--ok' };
    if (hours >= 2) return { text: `${hours} hrs`, cls: 'countdown--warn' };
    const mins = Math.floor(ms / 60000);
    return { text: `${Math.max(1, mins)} min`, cls: 'countdown--urgent' };
  }

  function statusOf(item) {
    if (item.unrejected_at) return item.unrejected_reason === 'manual_unreject'
      ? { label: 'Unrejected (manual)', cls: 'rt-status--grey' }
      : { label: 'Expired', cls: 'rt-status--grey' };
    if (item.expires_at && new Date(item.expires_at) <= Date.now())
      return { label: 'Expired', cls: 'rt-status--grey' };
    return { label: 'Active', cls: 'rt-status--amber' };
  }

  function fmtDate(iso) {
    if (!iso) return '—';
    try { return new Date(iso).toLocaleString('en-GB', { day:'2-digit', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit' }); }
    catch { return iso; }
  }

  async function load() {
    body.innerHTML = '<tr><td colspan="9" class="rt-loading">Loading…</td></tr>';
    try {
      const url = new URL('/v2/api/sticky-rejections', window.location.origin);
      url.searchParams.set('client_id', CLIENT);
      url.searchParams.set('status', state.status);
      const resp = await fetch(url.toString());
      const data = await resp.json();
      if (data.status !== 'ok') throw new Error(data.detail || 'failed');
      state.items = data.items || [];
      const s = data.stats || {};
      document.getElementById('rtActive').textContent = s.active_count ?? 0;
      document.getElementById('rtExpired30d').textContent = s.expired_last_30d ?? 0;
      document.getElementById('rtTotalCycles').textContent = s.total_cycles ?? 0;
      document.getElementById('rtAvgCycles').textContent = s.avg_cycles_per_term ?? 0;
      state.page = 1;
      render();
    } catch (e) {
      body.innerHTML = `<tr><td colspan="9" class="rt-loading rt-loading--error">Failed: ${escapeHtml(e.message)}</td></tr>`;
    }
  }

  function filteredItems() {
    const q = state.search.trim().toLowerCase();
    if (!q) return state.items;
    return state.items.filter(i =>
      (i.search_term_normalized || '').toLowerCase().includes(q) ||
      (i.search_term_original || '').toLowerCase().includes(q)
    );
  }

  function render() {
    const all = filteredItems();
    const totalPages = Math.max(1, Math.ceil(all.length / state.pageSize));
    if (state.page > totalPages) state.page = totalPages;
    const slice = all.slice((state.page - 1) * state.pageSize, state.page * state.pageSize);
    document.getElementById('rtCount').textContent = `${all.length} row${all.length === 1 ? '' : 's'}`;
    document.getElementById('rtPageLabel').textContent = `Page ${state.page} / ${totalPages}`;
    document.getElementById('rtPrev').disabled = state.page <= 1;
    document.getElementById('rtNext').disabled = state.page >= totalPages;

    if (slice.length === 0) {
      body.innerHTML = '<tr><td colspan="9" class="rt-loading">No rejections match the current filter.</td></tr>';
      return;
    }

    const rows = slice.map((item, idx) => {
      const rowNum = (state.page - 1) * state.pageSize + idx + 1;
      const st = statusOf(item);
      const cd = formatCountdown(item.expires_at, item.unrejected_at);
      const reason = item.reason_at_rejection || '—';
      const detail = item.reason_detail_at_rejection ? ` — ${escapeHtml(item.reason_detail_at_rejection)}` : '';
      const canUnreject = st.label === 'Active';
      return `
        <tr data-id="${item.id}" data-term="${escapeHtml(item.search_term_normalized)}">
          <td class="col-num">${rowNum}</td>
          <td class="rt-term">${escapeHtml(item.search_term_original || item.search_term_normalized)}</td>
          <td><span class="rt-status ${st.cls}">${st.label}</span></td>
          <td>
            <button type="button" class="rt-cycle-btn" data-role="history" title="Show cycle history">
              <span class="material-symbols-outlined" style="font-size:14px;vertical-align:-2px;">history</span>
              Cycle ${item.cycle_number}
            </button>
          </td>
          <td>${fmtDate(item.rejected_at)}</td>
          <td>${fmtDate(item.expires_at)}</td>
          <td><span class="rt-countdown ${cd.cls}" data-expires="${item.expires_at || ''}" data-unrej="${item.unrejected_at || ''}">${cd.text}</span></td>
          <td class="rt-reason">${escapeHtml(reason)}${detail}</td>
          <td class="rt-actions-col">
            ${canUnreject
              ? `<button type="button" class="btn-act btn-act--decline" data-role="unreject">Unreject</button>`
              : '<span class="rt-actions-placeholder">—</span>'}
          </td>
        </tr>`;
    }).join('');
    body.innerHTML = rows;
  }

  // -------- Countdown tick (every 60s) ---------------------------------
  setInterval(() => {
    document.querySelectorAll('.rt-countdown').forEach(el => {
      const cd = formatCountdown(el.dataset.expires || null, el.dataset.unrej || null);
      el.textContent = cd.text;
      el.className = 'rt-countdown ' + cd.cls;
    });
  }, 60000);

  // -------- Confirm modal (shared pattern from search_term_review) -----
  function showConfirmModal({ title, bodyHtml, confirmLabel = 'Confirm', cancelLabel = 'Cancel' }) {
    return new Promise(resolve => {
      const wrap = document.createElement('div');
      wrap.className = 'act-confirm-overlay';
      wrap.innerHTML = `
        <div class="act-confirm" role="dialog" aria-modal="true">
          <div class="act-confirm__header"><h3 class="act-confirm__title">${title}</h3></div>
          <div class="act-confirm__body">${bodyHtml}</div>
          <div class="act-confirm__footer">
            <button type="button" class="btn-act btn-act--decline" data-role="cancel">${cancelLabel}</button>
            <button type="button" class="btn-act btn-act--approve" data-role="confirm">${confirmLabel}</button>
          </div>
        </div>`;
      document.body.appendChild(wrap);
      const cleanup = (v) => { wrap.remove(); document.removeEventListener('keydown', onKey); resolve(v); };
      const onKey = (e) => { if (e.key === 'Escape') cleanup(false); if (e.key === 'Enter') cleanup(true); };
      document.addEventListener('keydown', onKey);
      wrap.addEventListener('click', (e) => { if (e.target === wrap) cleanup(false); });
      wrap.querySelector('[data-role="cancel"]').addEventListener('click', () => cleanup(false));
      wrap.querySelector('[data-role="confirm"]').addEventListener('click', () => cleanup(true));
      setTimeout(() => wrap.querySelector('[data-role="confirm"]').focus(), 0);
    });
  }

  // -------- Actions -----------------------------------------------------
  body.addEventListener('click', async (e) => {
    const row = e.target.closest('tr[data-id]');
    if (!row) return;
    const id = row.dataset.id;
    const term = row.dataset.term;

    if (e.target.closest('[data-role="unreject"]')) {
      const confirmed = await showConfirmModal({
        title: 'Unreject this term?',
        bodyHtml: `<p>Unreject <strong>${escapeHtml(term)}</strong>?</p>
          <p style="color:var(--text-muted);font-size:12px;">It will reappear in tomorrow's classification for normal processing.</p>`,
        confirmLabel: 'Unreject',
      });
      if (!confirmed) return;
      try {
        const resp = await fetch(`/v2/api/sticky-rejections/${id}/unreject`, {
          method: 'POST', headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ client_id: CLIENT }),
        });
        const data = await resp.json();
        if (data.status === 'ok') {
          toast(`Unrejected: ${term}`);
          load();
        } else {
          toast('Unreject failed: ' + (data.message || 'Unknown'), 'error');
        }
      } catch (err) { toast('Unreject failed: ' + err.message, 'error'); }
      return;
    }

    if (e.target.closest('[data-role="history"]')) {
      // Toggle inline history row
      const existing = row.nextElementSibling;
      if (existing && existing.classList.contains('rt-history-row')) {
        existing.remove();
        return;
      }
      const tr = document.createElement('tr');
      tr.className = 'rt-history-row';
      tr.innerHTML = `<td></td><td colspan="8" class="rt-history-cell">Loading history…</td>`;
      row.after(tr);
      try {
        const url = new URL('/v2/api/sticky-rejections/history', window.location.origin);
        url.searchParams.set('client_id', CLIENT);
        url.searchParams.set('term', term);
        const resp = await fetch(url.toString());
        const data = await resp.json();
        const cell = tr.querySelector('.rt-history-cell');
        if (data.status !== 'ok') {
          cell.textContent = 'Failed to load history.';
          return;
        }
        cell.innerHTML = `
          <div class="rt-history">
            <div class="rt-history__title">Cycle history for <strong>${escapeHtml(term)}</strong></div>
            <table class="rt-history__table">
              <thead><tr><th>Cycle</th><th>Rejected at</th><th>Expires at</th><th>Unrejected</th><th>Reason</th><th>By</th></tr></thead>
              <tbody>
                ${data.items.map(h => `
                  <tr>
                    <td>${h.cycle_number}</td>
                    <td>${fmtDate(h.rejected_at)}</td>
                    <td>${fmtDate(h.expires_at)}</td>
                    <td>${h.unrejected_at ? fmtDate(h.unrejected_at) + ' (' + (h.unrejected_reason || '') + ')' : '—'}</td>
                    <td>${escapeHtml(h.reason_at_rejection || '—')}</td>
                    <td>${escapeHtml(h.rejected_by || '—')}</td>
                  </tr>`).join('')}
              </tbody>
            </table>
          </div>`;
      } catch (err) {
        tr.querySelector('.rt-history-cell').textContent = 'Failed: ' + err.message;
      }
    }
  });

  // -------- Filter controls --------------------------------------------
  document.getElementById('rtStatusPills').addEventListener('click', (e) => {
    const pill = e.target.closest('.rt-pill');
    if (!pill) return;
    document.querySelectorAll('#rtStatusPills .rt-pill').forEach(p => p.classList.remove('active'));
    pill.classList.add('active');
    state.status = pill.dataset.status;
    load();
  });
  document.getElementById('rtSearch').addEventListener('input', (e) => {
    state.search = e.target.value || '';
    state.page = 1;
    render();
  });
  document.getElementById('rtPrev').addEventListener('click', () => { if (state.page > 1) { state.page--; render(); } });
  document.getElementById('rtNext').addEventListener('click', () => { state.page++; render(); });

  // -------- Boot --------------------------------------------------------
  if (!CLIENT) {
    body.innerHTML = '<tr><td colspan="9" class="rt-loading rt-loading--error">No client selected.</td></tr>';
  } else {
    load();
  }
})();
