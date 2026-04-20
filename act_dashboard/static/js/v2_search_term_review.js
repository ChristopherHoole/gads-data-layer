/* N1b Gate 5 — Search Term Review front-end
   Handles: tab switch, filter-chip view load, selection, bulk approve/reject,
   push-approved, run-pass3, pagination, toast, error display. */

(function () {
  const cfg = JSON.parse(document.getElementById('stConfig').textContent);
  const CLIENT = cfg.client_id;
  let analysisDate = cfg.analysis_date;
  let currentTab = 'pass12';              // pass12 | pass3
  let currentPage = 1;
  // Wave C: page size configurable + persisted in localStorage
  const PAGE_SIZE_KEY = 'st_rows_per_page';
  const ALLOWED_PAGE_SIZES = [10, 25, 50, 100, 250];
  function loadPageSize() {
    const raw = parseInt(localStorage.getItem(PAGE_SIZE_KEY) || '', 10);
    return ALLOWED_PAGE_SIZES.includes(raw) ? raw : 50;
  }
  let PAGE_SIZE = loadPageSize();
  let lastItems = [];                      // items currently rendered
  let statusView = 'all';                  // single-select status chip
  let selectedReasons = new Set();         // multi-select reason chips
  let p3View = 'pending';                  // Pass 3 tab single-select

  // ---------- Wave A humanization maps (display only; DB stores codes) ----
  const REASON_LABELS = {
    brand_protection:               'Brand protected',
    existing_exact_neg_match:       'Already blocked (exact)',
    existing_phrase_neg_match:      'Already blocked (phrase)',
    existing_multiword_neg_match:   'Already blocked (multi-word)',
    location_outside_service_area:  'Outside service area',
    service_not_advertised:         'Not advertised',
    advertised_service_match:       'Advertised service',
    contains_neg_vocabulary:        'Contains negged word',
    ambiguous:                      'Needs review',
    client_not_configured:          'Not configured',
    empty_term:                     'Empty term',
  };
  const ROLE_LABELS = {
    '1_word_exact':     '1 WORD [exact]',
    '2_word_exact':     '2 WORDS [exact]',
    '3_word_exact':     '3 WORDS [exact]',
    '4_word_exact':     '4 WORDS [exact]',
    '5plus_word_exact': '5+ WORDS [exact]',
    '1_word_phrase':    '1 WORD "phrase"',
    '2_word_phrase':    '2 WORDS "phrase"',
    '3_word_phrase':    '3 WORDS "phrase"',
    '4_word_phrase':    '4 WORDS "phrase"',
    'location_phrase':  'Location 1 WORD "phrase"',
    'location_exact':   'Location 1 WORD+ [exact]',
    'competitor_phrase':'Competitors & Brands "phrase"',
    'competitor_exact': 'Competitors & Brands [exact]',
  };
  const humanReason = r => REASON_LABELS[r] || (r || '');
  const humanRole   = r => ROLE_LABELS[r] || (r || '—');

  // Wave B Gate C: search_term_view.status humanised for display
  const STATUS_LABELS = {
    NONE:            'None',
    ADDED:           'Added',
    EXCLUDED:        'Excluded',
    ADDED_EXCLUDED:  'Added & Excluded',
    UNKNOWN:         'Unknown',
  };
  // For comma-joined statuses coming back from SQL STRING_AGG, humanise each
  // token individually so "NONE, ADDED" -> "None, Added".
  function humanStatuses(s) {
    if (!s) return '';
    return s.split(',').map(x => STATUS_LABELS[x.trim()] || x.trim()).join(', ');
  }

  // Wave C2: campaign_type enum -> display label
  const CAMPAIGN_TYPE_LABELS = {
    SEARCH:          'Search',
    PERFORMANCE_MAX: 'PMax',
    SHOPPING:        'Shopping',
    DISPLAY:         'Display',
    VIDEO:           'Video',
  };
  function humanCampaignType(s) {
    if (!s) return '';
    return s.split(',').map(x => {
      const t = x.trim();
      if (CAMPAIGN_TYPE_LABELS[t]) return CAMPAIGN_TYPE_LABELS[t];
      // Unknown value — title-case fallback
      return t ? t.charAt(0) + t.slice(1).toLowerCase().replace(/_/g, ' ') : '';
    }).join(', ');
  }

  const STATUS_CHIP_ORDER = [
    {key: 'all',      label: 'All'},
    {key: 'block',    label: 'Block'},
    {key: 'review',   label: 'Review'},
    {key: 'keep',     label: 'Keep'},
    {key: 'approved', label: 'Approved'},
    {key: 'pushed',   label: 'Pushed'},
    {key: 'rejected', label: 'Rejected'},
    {key: 'expired',  label: 'Expired'},
  ];
  // Display order for reason chips — matches brief
  const REASON_CHIP_ORDER = [
    'brand_protection',
    'existing_exact_neg_match',
    'existing_phrase_neg_match',
    'existing_multiword_neg_match',
    'location_outside_service_area',
    'service_not_advertised',
    'advertised_service_match',
    'contains_neg_vocabulary',
    'ambiguous',
    'client_not_configured',
  ];

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

  // -------------------- Chip rendering + interaction -----------------
  function renderStatusChips(counts) {
    const bar = document.getElementById('stStatusBar');
    // Preserve the label span; remove any previous chips
    bar.querySelectorAll('.st-chip').forEach(el => el.remove());
    STATUS_CHIP_ORDER.forEach(({key, label}) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'st-chip' + (statusView === key ? ' active' : '');
      btn.dataset.status = key;
      btn.innerHTML = `${label} <span class="st-chip__count">${counts[key] ?? 0}</span>`;
      btn.addEventListener('click', () => {
        if (statusView === key) return;
        statusView = key;
        currentPage = 1;
        reload();
      });
      bar.appendChild(btn);
    });
  }

  function renderReasonChips(reasonCounts) {
    const bar = document.getElementById('stReasonBar');
    bar.querySelectorAll('.st-chip').forEach(el => el.remove());
    REASON_CHIP_ORDER.forEach(code => {
      const n = reasonCounts[code] || 0;
      if (n === 0) return;  // hide zero-count reasons per brief
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'st-chip' + (selectedReasons.has(code) ? ' active' : '');
      btn.dataset.reason = code;
      btn.innerHTML = `${humanReason(code)} <span class="st-chip__count">${n}</span>`;
      btn.addEventListener('click', () => {
        if (selectedReasons.has(code)) selectedReasons.delete(code);
        else selectedReasons.add(code);
        currentPage = 1;
        reload();
      });
      bar.appendChild(btn);
    });
    // If any other reason codes appear in data that aren't in the known
    // order, append them so they're never invisible.
    Object.keys(reasonCounts).forEach(code => {
      if (REASON_CHIP_ORDER.includes(code)) return;
      if (!reasonCounts[code]) return;
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'st-chip' + (selectedReasons.has(code) ? ' active' : '');
      btn.dataset.reason = code;
      btn.innerHTML = `${humanReason(code)} <span class="st-chip__count">${reasonCounts[code]}</span>`;
      btn.addEventListener('click', () => {
        if (selectedReasons.has(code)) selectedReasons.delete(code);
        else selectedReasons.add(code);
        currentPage = 1;
        reload();
      });
      bar.appendChild(btn);
    });
  }

  // -------------------- PMax Other-bucket transparency banner --------
  function renderPmaxOtherBanner(bucket) {
    const el = document.getElementById('stPmaxOtherBanner');
    const txt = document.getElementById('stPmaxOtherText');
    if (!el || !bucket) {
      if (el) el.style.display = 'none';
      return;
    }
    const date = bucket.snapshot_date || analysisDate;
    const impr = bucket.impressions != null ? bucket.impressions.toLocaleString() : null;
    const cost = bucket.cost != null ? fmtMoney(bucket.cost) : null;
    const n    = bucket.distinct_term_count;
    // Phrasing adapts to which fields Google surfaced:
    //  - If distinct_term_count present: "N additional PMax queries ..."
    //  - Else: lead with impressions
    //  - Cost clause dropped when null
    let lead;
    if (n != null) {
      lead = `${n.toLocaleString()} additional PMax ${n === 1 ? 'query' : 'queries'}`;
    } else if (impr != null) {
      lead = `Additional PMax queries (${impr} impressions)`;
    } else {
      lead = 'Additional PMax queries';
    }
    const parts = [lead, `aggregated into Google's "Other search terms" bucket for ${date}`];
    const metrics = [];
    if (n != null && impr != null) metrics.push(`${impr} impr`);
    if (cost) metrics.push(`${cost} cost`);
    let detail = '';
    if (metrics.length) detail = ` (${metrics.join(', ')})`;
    txt.textContent = `Note: ${parts.join(' ')}${detail}. Individual terms not available via the API — review in Google Ads UI for full PMax coverage.`;
    el.style.display = '';
  }

  function renderP3StatusChips() {
    const bar = document.getElementById('stFilterBarP3');
    bar.querySelectorAll('.st-chip').forEach(el => el.remove());
    ['pending', 'approved', 'pushed', 'rejected'].forEach(key => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'st-chip' + (p3View === key ? ' active' : '');
      btn.dataset.status = key;
      btn.textContent = key.charAt(0).toUpperCase() + key.slice(1);
      btn.addEventListener('click', () => {
        if (p3View === key) return;
        p3View = key;
        currentPage = 1;
        reload();
      });
      bar.appendChild(btn);
    });
  }

  // -------------------- Row rendering (Pass 1/2 — 19 cols) -----------
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
    const pct = v => (v == null) ? '' : (Number(v) * 100).toFixed(2) + '%';
    const num2 = v => (v == null) ? '' : Number(v).toFixed(2);
    return `<tr data-id="${item.id}" data-pass1="${item.pass1_status}">
      <td class="st-col-check st-frozen-0" ${hideChk}><input type="checkbox" class="st-chk" ${checked} ${canEdit ? '' : 'disabled'}></td>
      <td class="st-col-term  st-frozen-1" title="${escapeHtml(item.search_term)}">${escapeHtml(item.search_term)}</td>
      <td><span class="${statusClass}">${item.pass1_status}</span>${reviewed}</td>
      <td>${escapeHtml(humanReason(item.pass1_reason))}</td>
      <td>${roleSel}</td>
      <td>${escapeHtml(item.match_types || '')}</td>
      <td>${escapeHtml(humanStatuses(item.statuses))}</td>
      <td title="${escapeHtml(item.campaigns || '')}">${escapeHtml(item.campaigns || '')}</td>
      <td title="${escapeHtml(item.campaign_types || '')}">${escapeHtml(humanCampaignType(item.campaign_types))}</td>
      <td title="${escapeHtml(item.keywords || '')}">${escapeHtml(item.keywords || '')}</td>
      <td class="num">${fmtMoney(item.total_cost)}</td>
      <td class="num">${fmtNum(item.total_impressions)}</td>
      <td class="num">${fmtNum(item.total_clicks)}</td>
      <td class="num">${fmtMoney(item.avg_cpc)}</td>
      <td class="num">${pct(item.ctr)}</td>
      <td class="num">${fmtNum(item.total_conversions)}</td>
      <td class="num">${fmtMoney(item.cost_per_conversion)}</td>
      <td class="num">${pct(item.conversion_rate)}</td>
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
    // Humanize labels (values stay as role codes — DB sees raw codes)
    const opts = options.map(r =>
      `<option value="${r}" ${r === current ? 'selected' : ''}>${escapeHtml(humanRole(r))}</option>`
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
    let url, view;
    if (currentTab === 'pass12') {
      view = statusView;
      const reasonsParam = selectedReasons.size
        ? `&reasons=${encodeURIComponent([...selectedReasons].join(','))}`
        : '';
      url = `/v2/api/negatives/search-term-review/${CLIENT}`
          + `?view=${encodeURIComponent(view)}&date=${analysisDate}`
          + `&page=${currentPage}&page_size=${PAGE_SIZE}${reasonsParam}`;
    } else {
      view = p3View;
      url = `/v2/api/negatives/phrase-suggestions/${CLIENT}`
          + `?view=${encodeURIComponent(view)}&date=${analysisDate}`
          + `&page=${currentPage}&page_size=${PAGE_SIZE}`;
    }

    let data;
    try {
      data = await apiGet(url);
    } catch (e) {
      toast(`Load failed: ${e.message}`, 'error');
      return;
    }
    lastItems = data.items || [];

    // Repaint chips from server-side counts (Pass 1/2 only)
    if (currentTab === 'pass12') {
      if (data.counts) renderStatusChips(data.counts);
      if (data.reason_counts) renderReasonChips(data.reason_counts);
      renderPmaxOtherBanner(data.pmax_other_bucket);
    }

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
      `Page ${currentPage} · ${lastItems.length} of ${data.total}`;
    document.getElementById('stPrev').disabled = currentPage <= 1;
    document.getElementById('stNext').disabled = lastItems.length < PAGE_SIZE
      || (currentPage * PAGE_SIZE) >= data.total;
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
    document.getElementById('stStatusBar').style.display = tab === 'pass12' ? '' : 'none';
    document.getElementById('stReasonBar').style.display = tab === 'pass12' ? '' : 'none';
    document.getElementById('stFilterBarP3').style.display = tab === 'pass3' ? '' : 'none';
    // Banner is Pass 1/2 scoped — hide when switching to Pass 3
    const banner = document.getElementById('stPmaxOtherBanner');
    if (banner && tab === 'pass3') banner.style.display = 'none';
    stTable.style.display = tab === 'pass12' ? '' : 'none';
    stP3Table.style.display = tab === 'pass3' ? '' : 'none';
    if (tab === 'pass3') renderP3StatusChips();
    reload();
  }

  // -------------------- Wire events ----------------------------------
  document.querySelectorAll('.st-tab').forEach(el => {
    el.addEventListener('click', () => {
      if (!el.disabled) switchTab(el.dataset.tab);
    });
  });
  // Chip interaction is now attached inside renderStatusChips /
  // renderReasonChips / renderP3StatusChips (per-button listener).
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
  // Wave C: rows-per-page — sync dropdown with localStorage, wire change handler
  const pageSizeSel = document.getElementById('stPageSize');
  if (pageSizeSel) {
    pageSizeSel.value = String(PAGE_SIZE);
    pageSizeSel.addEventListener('change', () => {
      const n = parseInt(pageSizeSel.value, 10);
      if (!ALLOWED_PAGE_SIZES.includes(n)) return;
      PAGE_SIZE = n;
      localStorage.setItem(PAGE_SIZE_KEY, String(n));
      currentPage = 1;
      reload();
    });
  }

  // Initial load
  reload();
})();
