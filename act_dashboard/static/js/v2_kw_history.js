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
  // Column count after the round-2 reorder (16 May 2026): 14 visible
  // columns (# + 13 cells; Method merged into Rationale as a chip).
  const COL_COUNT = 14;

  async function reload() {
    const tbody = document.getElementById('khTbody');
    tbody.innerHTML = `<tr><td colspan="${COL_COUNT}" class="kh-loading">Loading&hellip;</td></tr>`;
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

  // Resolve the (chip label, chip css class) tuple for a row.
  // Six cases per the round-2 spec:
  //   in_new_ex = TRUE       -> green  "in [ex]"
  //   rule                   -> blue   "rule"
  //   ai                     -> purple "ai"
  //   manual                 -> amber  "manual"
  //   skip_brand             -> grey   "brand"
  //   skip_low_volume        -> grey   "low volume"
  //   (NULL, not mapped)     -> red    "unset"
  function methodChip(row) {
    if (row.in_new_ex) return { label: 'in [ex]', cls: 'in_ex' };
    const m = row.proposal_method;
    if (m === 'rule')             return { label: 'rule',       cls: 'rule' };
    if (m === 'ai')               return { label: 'ai',         cls: 'ai' };
    if (m === 'manual')           return { label: 'manual',     cls: 'manual' };
    if (m === 'skip_brand')       return { label: 'brand',      cls: 'skip_brand' };
    if (m === 'skip_low_volume')  return { label: 'low volume', cls: 'skip_low_volume' };
    return { label: 'unset', cls: 'unset' };
  }

  function renderRows(rows) {
    const tbody = document.getElementById('khTbody');
    if (!rows.length) {
      tbody.innerHTML = `<tr><td colspan="${COL_COUNT}" class="kh-loading">No rows match the current filters.</td></tr>`;
      return;
    }
    const offset = (state.page - 1) * state.page_size;
    const html = rows.map((r, idx) => {
      const rowNum = offset + idx + 1;
      const chip = methodChip(r);
      // Round 3 (16 May 2026): explicit red close icon for in_new_ex=false
      // so the cell reads as "definitely not in [ex]" rather than blank.
      // Material Symbols family matches the rest of the page.
      const inEx = r.in_new_ex
        ? '<span class="material-symbols-outlined kh-in-ex-true" aria-label="in ex">check</span>'
        : '<span class="material-symbols-outlined kh-in-ex-false" aria-label="not in ex">close</span>';
      return `
        <tr data-term="${escapeHtml(r.term)}" data-type="${escapeHtml(r.type)}">
          <td class="col-num kh-frozen-0">${rowNum}</td>
          <td class="kh-frozen-1 kh-term">${escapeHtml(r.term_raw || r.term)}</td>
          <td>${escapeHtml(r.type)}</td>
          <td>${inEx}</td>
          <td>${escapeHtml(r.current_new_ex_ad_group || '-')}</td>
          <td>${escapeHtml(r.proposed_ad_group || '-')}</td>
          <td class="num">${fmtMoney(r.cost_total)}</td>
          <td class="num">${fmtInt(r.impressions_total)}</td>
          <td class="num">${fmtInt(r.clicks_total)}</td>
          <td class="num">${fmtConv(r.conversions_total)}</td>
          <td>${escapeHtml(r.old_campaign || '-')}</td>
          <td>${escapeHtml(r.old_ad_group || '-')}</td>
          <td class="kh-rationale">
            <span class="kh-method kh-method--${chip.cls}">${escapeHtml(chip.label)}</span>
            <span class="kh-rationale-text">${escapeHtml(r.proposal_rationale || '-')}</span>
          </td>
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
    // Proposed ad group is now column 6 (post round-2 reorder).
    const currentCell = tr.querySelector('td:nth-child(6)');
    const current = (currentCell?.textContent || '').trim();

    const edit = document.createElement('tr');
    edit.className = 'kh-edit-row';
    edit.innerHTML = `
      <td colspan="${COL_COUNT}">
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

  // Build the current filter+sort URLSearchParams once — same for both
  // export buttons.
  function exportParams() {
    return new URLSearchParams({
      client: CLIENT,
      sort: state.sort, dir: state.dir,
      type: state.type, status: state.status, method: state.method,
      campaign: state.campaign, ex_ad_group: state.ex_ad_group,
      q: state.q,
    });
  }

  // CSV export — full row set, all columns. Round-trips active filters.
  document.getElementById('khExportCsv').addEventListener('click', () => {
    window.location.href = `/v2/api/kw-history/export.csv?${exportParams().toString()}`;
  });

  // "Export for AI" CSV — term + 6 context columns (impressions / clicks
  // / cost / conversions / already_in_ex / matched_ad_group_if_any).
  // Original casing on term, snake_case headers. Logs the expected row
  // count so the user can verify against Excel's line count
  // (lines = rows + 1 header).
  document.getElementById('khExportTermsCsv').addEventListener('click', () => {
    const expected = state.total;
    console.info(
      `[kw-history] exporting AI CSV; expected ${expected.toLocaleString('en-GB')} ` +
      `data rows (${(expected + 1).toLocaleString('en-GB')} lines incl. header). ` +
      `Status pill = ${state.status}.`
    );
    window.location.href = `/v2/api/kw-history/export-terms.csv?${exportParams().toString()}`;
  });

  // Round 3 (16 May 2026): sanity-check the stat-card + status-pill
  // counts on boot. Every bucket is a disjoint partition of the total,
  // so both sums below must equal the total. console.warn on drift so
  // any future migration / engine change that breaks the invariant is
  // caught at a glance.
  function _toInt(v) { return parseInt(String(v).replace(/[,_]/g, ''), 10) || 0; }
  function sanityCheckCounts() {
    const stats = document.getElementById('khStats');
    if (!stats) return;
    const total       = _toInt(stats.dataset.statTotal);
    const inEx        = _toInt(stats.dataset.statInEx);
    const notInEx     = _toInt(stats.dataset.statNotInEx);
    const totalMapped = _toInt(stats.dataset.statTotalMapped);
    const unmapped    = _toInt(stats.dataset.statUnmapped);
    const brand       = _toInt(stats.dataset.statBrand);
    const lowVolume   = _toInt(stats.dataset.statLowVolume);
    const proposed    = _toInt(stats.dataset.statProposed);

    const cardSplitAB = inEx + notInEx;
    if (cardSplitAB !== total) {
      console.warn(`[kw-history] card sum drift A: in_ex (${inEx}) + not_in_ex (${notInEx}) = ${cardSplitAB}, total = ${total}`);
    }
    const cardSplitCD = totalMapped + unmapped + brand + lowVolume;
    if (cardSplitCD !== total) {
      console.warn(`[kw-history] card sum drift B: total_mapped (${totalMapped}) + unmapped (${unmapped}) + brand (${brand}) + low_volume (${lowVolume}) = ${cardSplitCD}, total = ${total}`);
    }
    // Pills: in_ex + proposed + unmapped + brand + low_volume == total.
    // (total_mapped = in_ex + proposed by definition; pills break it
    // out further so the user can filter to either bucket.)
    const pillSum = inEx + proposed + unmapped + brand + lowVolume;
    if (pillSum !== total) {
      console.warn(`[kw-history] pill sum drift: in_ex (${inEx}) + proposed (${proposed}) + unmapped (${unmapped}) + brand (${brand}) + low_volume (${lowVolume}) = ${pillSum}, total = ${total}`);
    } else {
      console.info(`[kw-history] count sanity ok: cards 2+3 = cards 4+5+6+7 = pill sum = ${total}`);
    }
  }
  sanityCheckCounts();

  // Boot.
  if (!CLIENT) {
    document.getElementById('khTbody').innerHTML =
      `<tr><td colspan="${COL_COUNT}" class="kh-loading">No client selected.</td></tr>`;
  } else {
    reload();
  }
})();
