/* KW + Search Term History Viewer (Phase 3).
   Server-side filtering + pagination via /v2/api/kw-history/rows.
   Sortable headers, filter pills, search, manual override, CSV export. */
(function () {
  const cfg = window.KH_CONFIG || {};
  const CLIENT = cfg.client_id;

  const state = {
    page: 1,
    page_size: 100,
    sort: 'clicks_total',
    dir: 'desc',
    type: 'all',
    status: 'all',
    method: 'all',
    campaign: 'all',
    ex_ad_group: 'all',
    q: '',
    total: 0,
  };

  // ---------- helpers ----------
  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g,
      c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }
  function fmtInt(n) { return (Number(n || 0)).toLocaleString('en-GB'); }
  function fmtMoney(n) {
    return '£' + (Number(n || 0)).toLocaleString('en-GB',
      { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  function fmtConv(n) {
    const v = Number(n || 0);
    return v.toLocaleString('en-GB', { maximumFractionDigits: 2 });
  }
  function toast(msg, kind) {
    const el = document.getElementById('khToast');
    if (!el) return;
    el.textContent = msg;
    el.className = 'kh-toast' + (kind === 'error' ? ' kh-toast--error' : '');
    el.style.display = '';
    clearTimeout(toast._t);
    toast._t = setTimeout(() => { el.style.display = 'none'; }, 4500);
  }

  // ---------- fetch + render ----------
  async function reload() {
    const tbody = document.getElementById('khTbody');
    tbody.innerHTML = '<tr><td colspan="15" class="kh-loading">Loading&hellip;</td></tr>';
    const params = new URLSearchParams({
      client: CLIENT,
      page: state.page, page_size: state.page_size,
      sort: state.sort, dir: state.dir,
      type: state.type, status: state.status, method: state.method,
      campaign: state.campaign, ex_ad_group: state.ex_ad_group,
      q: state.q,
    });
    try {
      const resp = await fetch(`/v2/api/kw-history/rows?${params.toString()}`);
      const data = await resp.json();
      if (data.status !== 'ok') throw new Error(data.reason || 'failed');
      state.total = data.total;
      renderRows(data.rows);
      renderPager();
      updateSortIndicators();
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="15" class="kh-loading">Failed: ${escapeHtml(e.message)}</td></tr>`;
    }
  }

  function renderRows(rows) {
    const tbody = document.getElementById('khTbody');
    if (!rows.length) {
      tbody.innerHTML = '<tr><td colspan="15" class="kh-loading">No rows match the current filters.</td></tr>';
      return;
    }
    const offset = (state.page - 1) * state.page_size;
    const html = rows.map((r, idx) => {
      const rowNum = offset + idx + 1;
      const method = r.proposal_method || 'unset';
      const inEx = r.in_new_ex
        ? '<span class="kh-in-ex-true">&check;</span>'
        : '<span class="kh-in-ex-false">&mdash;</span>'.replace('&mdash;', '-');
      return `
        <tr data-term="${escapeHtml(r.term)}" data-type="${escapeHtml(r.type)}">
          <td class="col-num kh-frozen-0">${rowNum}</td>
          <td class="kh-frozen-1 kh-term">${escapeHtml(r.term_raw || r.term)}</td>
          <td>${escapeHtml(r.type)}</td>
          <td class="num">${fmtInt(r.impressions_total)}</td>
          <td class="num">${fmtInt(r.clicks_total)}</td>
          <td class="num">${fmtMoney(r.cost_total)}</td>
          <td class="num">${fmtConv(r.conversions_total)}</td>
          <td>${escapeHtml(r.old_campaign || '-')}</td>
          <td>${escapeHtml(r.old_ad_group || '-')}</td>
          <td>${inEx}</td>
          <td>${escapeHtml(r.current_new_ex_ad_group || '-')}</td>
          <td>${escapeHtml(r.proposed_ad_group || '-')}</td>
          <td><span class="kh-method kh-method--${escapeHtml(method)}">${escapeHtml(method)}</span></td>
          <td class="kh-rationale">${escapeHtml(r.proposal_rationale || '-')}</td>
          <td>
            <button type="button" class="kh-edit-btn" data-role="edit"
                    title="Manual override: edit proposed ad group">
              <span class="material-symbols-outlined">edit</span>
            </button>
          </td>
        </tr>`;
    }).join('');
    tbody.innerHTML = html;
  }

  function renderPager() {
    const totalPages = Math.max(1, Math.ceil(state.total / state.page_size));
    if (state.page > totalPages) state.page = totalPages;
    const start = state.total === 0 ? 0 : (state.page - 1) * state.page_size + 1;
    const end   = Math.min(state.total, state.page * state.page_size);
    document.getElementById('khPagerSummary').textContent =
      `Showing ${fmtInt(start)} to ${fmtInt(end)} of ${fmtInt(state.total)}`;
    document.getElementById('khPagerLabel').textContent =
      `${state.page} / ${totalPages}`;
    document.getElementById('khPrev').disabled = state.page <= 1;
    document.getElementById('khNext').disabled = state.page >= totalPages;
  }

  function updateSortIndicators() {
    document.querySelectorAll('.kh-table th.kh-sortable').forEach(th => {
      th.classList.remove('kh-sort-active');
      const g = th.querySelector('.kh-sort-glyph');
      if (g) g.textContent = 'unfold_more';
    });
    const active = document.querySelector(
      `.kh-table th.kh-sortable[data-sort="${state.sort}"]`);
    if (active) {
      active.classList.add('kh-sort-active');
      const g = active.querySelector('.kh-sort-glyph');
      if (g) g.textContent = state.dir === 'asc' ? 'expand_less' : 'expand_more';
    }
  }

  // ---------- inline manual override ----------
  function openEditRow(tr) {
    // Close any open edit row first.
    document.querySelectorAll('.kh-edit-row').forEach(r => r.remove());
    const term = tr.dataset.term;
    const type = tr.dataset.type;
    const currentCell = tr.querySelector('td:nth-child(12)');
    const current = (currentCell?.textContent || '').trim();

    const edit = document.createElement('tr');
    edit.className = 'kh-edit-row';
    edit.innerHTML = `
      <td colspan="15">
        <label>Proposed ad group (sets method = manual)</label>
        <input type="text" data-role="ag-input"
               value="${current === '-' ? '' : escapeHtml(current)}"
               placeholder="e.g. [*] Dental Implants - COST"/>
        <div class="kh-edit-actions">
          <button type="button" class="btn-act btn-act--approve" data-role="save">Save override</button>
          <button type="button" class="btn-act btn-act--decline" data-role="cancel">Cancel</button>
        </div>
      </td>`;
    tr.after(edit);
    const input = edit.querySelector('[data-role="ag-input"]');
    input.focus();
    input.select();

    edit.querySelector('[data-role="cancel"]').addEventListener('click',
      () => edit.remove());
    edit.querySelector('[data-role="save"]').addEventListener('click',
      () => saveOverride(term, type, input.value, edit));
    input.addEventListener('keydown', e => {
      if (e.key === 'Enter') saveOverride(term, type, input.value, edit);
      if (e.key === 'Escape') edit.remove();
    });
  }

  async function saveOverride(term, type, value, editRow) {
    const ag = (value || '').trim();
    if (!ag) { toast('Proposed ad group required', 'error'); return; }
    try {
      const resp = await fetch('/v2/api/kw-history/override', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          client_id: CLIENT, term, type, proposed_ad_group: ag,
        }),
      });
      const data = await resp.json();
      if (data.status === 'ok') {
        toast(`Override saved: ${ag}`);
        editRow.remove();
        reload();
      } else {
        toast('Save failed: ' + (data.message || 'unknown'), 'error');
      }
    } catch (e) {
      toast('Save failed: ' + e.message, 'error');
    }
  }

  // ---------- wire events ----------
  // Filter pills.
  document.querySelectorAll('.pill-group').forEach(group => {
    group.addEventListener('click', e => {
      const btn = e.target.closest('.pill-btn');
      if (!btn) return;
      group.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const target = group.dataset.pillTarget;
      const value = btn.dataset.value;
      state[target] = value;
      state.page = 1;
      reload();
    });
  });

  // Campaign + [ex] dropdowns.
  document.getElementById('khCampaign').addEventListener('change', e => {
    state.campaign = e.target.value;
    state.page = 1;
    reload();
  });
  document.getElementById('khExAdGroup').addEventListener('change', e => {
    state.ex_ad_group = e.target.value;
    state.page = 1;
    reload();
  });

  // Search box (debounced).
  let searchTimer;
  document.getElementById('khSearch').addEventListener('input', e => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      state.q = e.target.value.trim();
      state.page = 1;
      reload();
    }, 250);
  });

  // Sort headers.
  document.querySelectorAll('.kh-table th.kh-sortable').forEach(th => {
    th.addEventListener('click', () => {
      const key = th.dataset.sort;
      if (state.sort === key) {
        state.dir = state.dir === 'asc' ? 'desc' : 'asc';
      } else {
        state.sort = key;
        state.dir = (key === 'term') ? 'asc' : 'desc';
      }
      state.page = 1;
      reload();
    });
  });

  // Page-size + nav.
  document.getElementById('khPageSize').addEventListener('change', e => {
    state.page_size = parseInt(e.target.value, 10) || 100;
    state.page = 1;
    reload();
  });
  document.getElementById('khPrev').addEventListener('click', () => {
    if (state.page > 1) { state.page--; reload(); }
  });
  document.getElementById('khNext').addEventListener('click', () => {
    state.page++; reload();
  });

  // Manual override pencil.
  document.getElementById('khTbody').addEventListener('click', e => {
    if (e.target.closest('[data-role="edit"]')) {
      const tr = e.target.closest('tr[data-term]');
      if (tr) openEditRow(tr);
    }
  });

  // CSV export — round-trip the filters via the export endpoint URL.
  document.getElementById('khExportCsv').addEventListener('click', () => {
    const params = new URLSearchParams({
      client: CLIENT,
      sort: state.sort, dir: state.dir,
      type: state.type, status: state.status, method: state.method,
      campaign: state.campaign, ex_ad_group: state.ex_ad_group,
      q: state.q,
    });
    window.location.href = `/v2/api/kw-history/export.csv?${params.toString()}`;
  });

  // Boot.
  if (!CLIENT) {
    document.getElementById('khTbody').innerHTML =
      '<tr><td colspan="15" class="kh-loading">No client selected.</td></tr>';
  } else {
    reload();
  }
})();
