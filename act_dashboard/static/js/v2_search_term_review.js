/* N1b Gate 5 — Search Term Review front-end
   Handles: tab switch, filter-chip view load, selection, bulk approve/reject,
   push-approved, run-pass3, pagination, toast, error display. */

(function () {
  const cfg = JSON.parse(document.getElementById('stConfig').textContent);
  const CLIENT = cfg.client_id;
  let analysisDate = cfg.analysis_date;
  let currentTab = 'pass12';              // pass12 | pass3
  let currentPage = 1;
  const PAGE_SIZE = 100;
  let lastItems = [];                      // items currently rendered

  const tbody = document.getElementById('stTbody');
  const p3body = document.getElementById('stP3Tbody');
  const stTable = document.getElementById('stTable');
  const stP3Table = document.getElementById('stP3Table');
  const toastEl = document.getElementById('stToast');

  // -------------------- HTTP helpers ---------------------------------
  async function apiGet(url) {
    const r = await fetch(url, {credentials: 'same-origin'});
    if (!r.ok) throw new Error(`GET ${url} -> ${r.status}`);
    return r.json();
  }
  async function apiPost(url, body) {
    const r = await fetch(url, {
      method: 'POST',
      credentials: 'same-origin',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(body),
    });
    if (!r.ok) throw new Error(`POST ${url} -> ${r.status}`);
    return r.json();
  }

  function toast(msg, kind) {
    toastEl.textContent = msg;
    toastEl.className = 'st-toast' + (kind === 'error' ? ' st-toast--error' : '');
    toastEl.style.display = 'block';
    clearTimeout(toast._t);
    toast._t = setTimeout(() => { toastEl.style.display = 'none'; }, 4000);
  }

  function fmtNum(n) { return n == null ? '' : Number(n).toLocaleString(); }
  function fmtMoney(n) { return n == null ? '' : '£' + Number(n).toFixed(2); }

  // -------------------- View selection -------------------------------
  function getActiveViews(tab) {
    const bar = tab === 'pass12' ? document.getElementById('stFilterBar')
                                 : document.getElementById('stFilterBarP3');
    return Array.from(bar.querySelectorAll('input[data-view]:checked'))
      .map(el => el.dataset.view);
  }

  // -------------------- Row rendering (Pass 1/2) ---------------------
  function renderRow(item) {
    const canEdit = item.pass1_status === 'block' || item.pass1_status === 'review';
    const checked = item.pass1_status === 'block' ? 'checked' : '';
    const hideChk = item.pass1_status === 'keep' ? 'style="visibility:hidden"' : '';
    const roleSel = canEdit ? roleDropdown(item.pass2_target_list_role, cfg.list_roles, item.id) : '';
    const pushErr = item.push_error ? `<span class="st-push-error">${escapeHtml(item.push_error)}</span>` : '';
    const statusClass = `st-status st-status--${item.pass1_status}`;
    const reviewed = item.review_status !== 'pending'
      ? ` · <span class="st-status st-status--${item.review_status}">${item.review_status}</span>`
      : '';
    return `<tr data-id="${item.id}" data-pass1="${item.pass1_status}">
      <td ${hideChk}><input type="checkbox" class="st-chk" ${checked} ${canEdit ? '' : 'disabled'}></td>
      <td class="st-table__term">${escapeHtml(item.search_term)}</td>
      <td class="num">${fmtNum(item.total_impressions)}</td>
      <td class="num">${fmtNum(item.total_clicks)}</td>
      <td class="num">${fmtMoney(item.total_cost)}</td>
      <td class="num">${fmtNum(item.total_conversions)}</td>
      <td><span class="${statusClass}">${item.pass1_status}</span>${reviewed}</td>
      <td>${escapeHtml(item.pass1_reason || '')}</td>
      <td>${roleSel}</td>
      <td>${pushErr}</td>
    </tr>`;
  }

  // -------------------- Row rendering (Pass 3) -----------------------
  function renderP3Row(item) {
    const roleSel = roleDropdown(item.target_list_role, cfg.phrase_roles, item.id);
    const checked = item.word_count >= 2 ? 'checked' : '';  // 1-word unchecked
    const pushErr = item.push_error ? `<span class="st-push-error">${escapeHtml(item.push_error)}</span>` : '';
    const sources = (item.source_search_terms || []).slice(0, 20).join(', ');
    const reviewed = item.review_status !== 'pending'
      ? `<span class="st-status st-status--${item.review_status}">${item.review_status}</span>`
      : '<span class="st-status st-status--review">pending</span>';
    return `<tr data-id="${item.id}">
      <td><input type="checkbox" class="st-chk" ${checked}></td>
      <td class="st-table__term">${escapeHtml(item.fragment)}</td>
      <td class="num">${item.word_count}</td>
      <td>${roleSel}</td>
      <td class="num">${item.occurrence_count}</td>
      <td><span class="st-risk st-risk--${item.risk_level}">${item.risk_level}</span></td>
      <td>${reviewed}</td>
      <td class="st-table__sources" title="${escapeHtml(sources)}">${escapeHtml(sources)}</td>
      <td>${pushErr}</td>
    </tr>`;
  }

  function roleDropdown(current, options, rowId) {
    const opts = options.map(r =>
      `<option value="${r}" ${r === current ? 'selected' : ''}>${r}</option>`
    ).join('');
    return `<select class="st-target-select" data-row-id="${rowId}">${opts}</select>`;
  }

  function escapeHtml(s) {
    if (s == null) return '';
    return String(s).replace(/[&<>"']/g, c =>
      ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  // -------------------- Load + render --------------------------------
  async function reload() {
    const views = getActiveViews(currentTab);
    if (views.length === 0) {
      if (currentTab === 'pass12') tbody.innerHTML = '<tr><td colspan="10" class="st-loading">Select at least one filter</td></tr>';
      else p3body.innerHTML = '<tr><td colspan="9" class="st-loading">Select at least one filter</td></tr>';
      lastItems = [];
      updateButtons();
      return;
    }
    // Single view = single request; multiple = merge results.
    const urlBase = currentTab === 'pass12'
      ? `/v2/api/negatives/search-term-review/${CLIENT}`
      : `/v2/api/negatives/phrase-suggestions/${CLIENT}`;
    let merged = [];
    let total = 0;
    try {
      for (const v of views) {
        const data = await apiGet(
          `${urlBase}?view=${v}&date=${analysisDate}&page=${currentPage}&page_size=${PAGE_SIZE}`
        );
        merged = merged.concat(data.items);
        total += data.total;
      }
    } catch (e) {
      toast(`Load failed: ${e.message}`, 'error');
      return;
    }
    // Dedup by id if multiple views overlap (shouldn't, but safe)
    const seen = new Set();
    lastItems = merged.filter(x => { if (seen.has(x.id)) return false; seen.add(x.id); return true; });

    if (currentTab === 'pass12') {
      tbody.innerHTML = lastItems.length
        ? lastItems.map(renderRow).join('')
        : '<tr><td colspan="10" class="st-loading">No matching rows</td></tr>';
    } else {
      p3body.innerHTML = lastItems.length
        ? lastItems.map(renderP3Row).join('')
        : '<tr><td colspan="9" class="st-loading">No matching suggestions</td></tr>';
    }

    document.getElementById('stPagerLabel').textContent =
      `Page ${currentPage} · ${lastItems.length} of ${total}`;
    document.getElementById('stPrev').disabled = currentPage <= 1;
    document.getElementById('stNext').disabled = lastItems.length < PAGE_SIZE;
    updateButtons();
  }

  // -------------------- Selection & action buttons -------------------
  function getCheckedRows() {
    const rows = currentTab === 'pass12'
      ? tbody.querySelectorAll('tr[data-id]') : p3body.querySelectorAll('tr[data-id]');
    const ids = [];
    rows.forEach(tr => {
      const chk = tr.querySelector('input.st-chk');
      if (chk && chk.checked && !chk.disabled) {
        const roleEl = tr.querySelector('select.st-target-select');
        ids.push({
          id: parseInt(tr.dataset.id, 10),
          role_override: roleEl ? roleEl.value : null,
        });
      }
    });
    return ids;
  }

  function updateButtons() {
    const sel = getCheckedRows();
    document.getElementById('lblApprove').textContent = sel.length;
    document.getElementById('lblReject').textContent = sel.length;
    document.getElementById('stBulkApprove').disabled = sel.length === 0;
    document.getElementById('stBulkReject').disabled = sel.length === 0;
    const approvedInView = lastItems.some(i =>
      i.review_status === 'approved' && !i.pushed_to_ads_at);
    document.getElementById('stPushApproved').disabled = !approvedInView;
  }

  async function bulkUpdate(status) {
    const sel = getCheckedRows();
    if (!sel.length) return;
    const endpoint = currentTab === 'pass12'
      ? '/v2/api/negatives/search-term-review/bulk-update'
      : '/v2/api/negatives/phrase-suggestions/bulk-update';
    const items = sel.map(s => {
      const o = {id: s.id, review_status: status};
      if (s.role_override) {
        if (currentTab === 'pass12') o.pass2_target_list_role_override = s.role_override;
        else o.target_list_role_override = s.role_override;
      }
      return o;
    });
    try {
      const res = await apiPost(endpoint, {client_id: CLIENT, items});
      toast(`${status}: ${res.updated_count} row(s)`);
      await reload();
    } catch (e) { toast(`Bulk update failed: ${e.message}`, 'error'); }
  }

  async function pushApproved() {
    const endpoint = currentTab === 'pass12'
      ? '/v2/api/negatives/push-approved'
      : '/v2/api/negatives/push-phrase-suggestions';
    const btn = document.getElementById('stPushApproved');
    btn.disabled = true; btn.textContent = 'Pushing…';
    try {
      const res = await apiPost(endpoint, {client_id: CLIENT, analysis_date: analysisDate});
      const msg = `Pushed: ${res.succeeded_count} succeeded, ${res.failed_count} failed`;
      toast(msg, res.failed_count > 0 ? 'error' : undefined);
      await reload();
    } catch (e) {
      toast(`Push failed: ${e.message}`, 'error');
    } finally {
      btn.textContent = 'Push approved to Google Ads';
    }
  }

  async function runPass3() {
    try {
      const res = await apiPost('/v2/api/negatives/run-pass3',
        {client_id: CLIENT, analysis_date: analysisDate});
      toast(`Pass 3: ${res.suggestions_created} suggestion(s) created`);
      document.getElementById('cntSugg').textContent = res.suggestions_created;
      // Auto-enable the Pass 3 tab
      document.querySelector('.st-tab[data-tab="pass3"]').disabled = false;
    } catch (e) { toast(`Pass 3 failed: ${e.message}`, 'error'); }
  }

  // -------------------- Tab switching --------------------------------
  function switchTab(tab) {
    currentTab = tab;
    currentPage = 1;
    document.querySelectorAll('.st-tab').forEach(el => {
      el.classList.toggle('active', el.dataset.tab === tab);
    });
    document.getElementById('stFilterBar').style.display = tab === 'pass12' ? '' : 'none';
    document.getElementById('stFilterBarP3').style.display = tab === 'pass3' ? '' : 'none';
    stTable.style.display = tab === 'pass12' ? '' : 'none';
    stP3Table.style.display = tab === 'pass3' ? '' : 'none';
    reload();
  }

  // -------------------- Wire events ----------------------------------
  document.querySelectorAll('.st-tab').forEach(el => {
    el.addEventListener('click', () => {
      if (!el.disabled) switchTab(el.dataset.tab);
    });
  });
  document.querySelectorAll('.st-filter-bar input[data-view]').forEach(el => {
    el.addEventListener('change', () => { currentPage = 1; reload(); });
  });
  document.getElementById('stSelectAll').addEventListener('change', e => {
    const chks = (currentTab === 'pass12' ? tbody : p3body)
      .querySelectorAll('input.st-chk:not(:disabled)');
    chks.forEach(c => { c.checked = e.target.checked; });
    updateButtons();
  });
  document.addEventListener('change', e => {
    if (e.target.classList && e.target.classList.contains('st-chk')) updateButtons();
  });
  document.getElementById('stBulkApprove').addEventListener('click', () => bulkUpdate('approved'));
  document.getElementById('stBulkReject').addEventListener('click', () => bulkUpdate('rejected'));
  document.getElementById('stPushApproved').addEventListener('click', pushApproved);
  document.getElementById('stRunPass3').addEventListener('click', runPass3);
  document.getElementById('stDate').addEventListener('change', e => {
    analysisDate = e.target.value;
    currentPage = 1;
    reload();
  });
  document.getElementById('stPrev').addEventListener('click', () => {
    if (currentPage > 1) { currentPage--; reload(); }
  });
  document.getElementById('stNext').addEventListener('click', () => {
    currentPage++; reload();
  });

  // Initial load
  reload();
})();
