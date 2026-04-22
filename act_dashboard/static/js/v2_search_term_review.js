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
  let liveTargetListLabels = {};           // Wave C4: {role: live_name} from API
  let campaignSource = 'all';              // Wave C10: all | search | pmax
  // Wave D1 — client-side column sort. Applied AFTER fetch to lastItems.
  // null = no explicit sort (server-side ordering: impr DESC tie-break).
  let sortKey = null;
  let sortDir = 'desc';                    // 'asc' | 'desc'
  // Wave D1 — whole-client approved-not-pushed count (drives Push button
  // even when current filter hides approved rows).
  let approvedReadyCount = 0;

  // ---------- Wave A humanization maps (display only; DB stores codes) ----
  // Wave C12: reason label now a function of (code, detail). When the
  // engine populates pass1_reason_detail the label shows WHICH term fired
  // the rule (e.g. 'Contains: 1kingsdental'). Fallback to short form when
  // detail is null (Rule 2, Rule 8, empty-term, client-not-configured, or
  // pre-C12 rows).
  // Wave D1: Rule 2 (existing_exact_neg_match) detail is a comma-joined list
  // of list_role codes; Rule 3 (existing_phrase_neg_match) detail is
  // "phrase|role1,role2" (pipe-delimited). Render role codes via ROLE_LABELS
  // (falls back to the raw code when unknown) so the UI shows WHERE the
  // match lives, not just that one happened.
  function _rolesFromCsv(csv) {
    return (csv || '').split(',').map(r => r.trim()).filter(Boolean)
      .map(r => ROLE_LABELS[r] || r).join(', ');
  }
  const REASON_FMT = {
    brand_protection:               d => d ? `Brand: ${d}` : 'Brand',
    existing_exact_neg_match:       (d, item) => {
      // Wave L: surface the matched keyword (= search_term by Rule 2 equality)
      // so leak diagnostics read naturally — parallel to Leak-phrase format.
      const term = item?.search_term || '';
      if (!d) return term ? `Leak — exact: ${term}` : 'Leak — exact';
      const roles = _rolesFromCsv(d);
      return term ? `Leak — exact: ${term} (${roles})` : `Leak — exact: ${roles}`;
    },
    existing_phrase_neg_match:      d => {
      if (!d) return 'Leak — phrase';
      const [phrase, rolesCsv] = d.split('|');
      if (!rolesCsv) return `Leak — phrase: ${phrase}`;
      return `Leak — phrase: ${phrase} (${_rolesFromCsv(rolesCsv)})`;
    },
    existing_multiword_neg_match:   d => d ? `Leak — phrase: ${d}` : 'Leak — phrase',
    location_outside_service_area:  d => d ? `Outside: ${d}` : 'Outside service area',
    service_not_advertised:         d => d ? `Not advertised: ${d}` : 'Not advertised',
    advertised_service_match:       d => d ? `Advertised: ${d}` : 'Advertised',
    contains_neg_vocabulary:        d => d ? `Contains: ${d}` : 'Contains excluded term',
    ambiguous: (d, item) => {
      // Wave M: phrase-level near-match signals (replaces token-level noise).
      // Each value format: "phrase|abs/total". Explicit "no_match" sentinel
      // from backend when nothing crossed the 50% meaningful-overlap threshold.
      if (!d || d === 'no_match') return 'Needs Review — no phrase match';
      const parts = {};
      d.split(';').forEach(kv => {
        const i = kv.indexOf('=');
        if (i > 0) parts[kv.slice(0, i)] = kv.slice(i + 1);
      });
      const fmt = raw => {
        const [phrase, ratio] = raw.split('|');
        return ratio ? `"${phrase}" (${ratio} tokens)` : `"${phrase}"`;
      };
      const chunks = [];
      if (parts.brand_near)   chunks.push(`brand near: ${fmt(parts.brand_near)}`);
      if (parts.adv_near)     chunks.push(`closest advertised: ${fmt(parts.adv_near)}`);
      if (parts.notadv_near)  chunks.push(`closest not-adv: ${fmt(parts.notadv_near)}`);
      return chunks.length ? `Needs Review — ${chunks.join(' · ')}` : 'Needs Review — no phrase match';
    },
    client_not_configured:          _ => 'Not configured',
    empty_term:                     _ => 'Empty term',
  };
  // Short-form labels for the Reason filter chip row (detail varies per row).
  const REASON_CHIP_LABELS = {
    brand_protection:               'Brand',
    existing_exact_neg_match:       'Leak — exact',
    existing_phrase_neg_match:      'Leak — phrase',
    existing_multiword_neg_match:   'Leak — phrase',
    location_outside_service_area:  'Outside service area',
    service_not_advertised:         'Not advertised',
    advertised_service_match:       'Advertised',
    contains_neg_vocabulary:        'Contains excluded term',
    ambiguous:                      'Needs review',
    client_not_configured:          'Not configured',
    empty_term:                     'Empty term',
  };
  // Wave C7: fallback labels track the latest DBD naming convention
  // (WRD/WRDS, Com & Bran, Loc). Used when live target_list_labels lacks
  // a role (e.g. unlinked 4_word_phrase / location_exact).
  const ROLE_LABELS = {
    '1_word_exact':     '1 WRD [ex]',
    '2_word_exact':     '2 WRDS [ex]',
    '3_word_exact':     '3 WRDS [ex]',
    '4_word_exact':     '4 WRDS [ex]',
    '5plus_word_exact': '5+ WRDS [ex]',
    '1_word_phrase':    '1 WRD "ph"',
    '2_word_phrase':    '2 WRDS "ph"',
    '3_word_phrase':    '3 WRDS "ph"',
    '4_word_phrase':    '4 WRDS "ph"',
    'location_phrase':  'Loc 1 WRD "ph"',
    'location_exact':   'Loc 1 WRD+ [ex]',
    'competitor_phrase':'Com & Bran "ph"',
    'competitor_exact': 'Com & Bran [ex]',
    // Wave C9
    'offered_not_advertised_exact':  'Off Not Adv [ex]',
    'offered_not_advertised_phrase': 'Off Not Adv "ph"',
  };
  function humanReason(code, detail, item) {
    const fn = REASON_FMT[code];
    if (!fn) return code || '';
    return fn(detail, item);
  }
  const humanReasonChip = c => REASON_CHIP_LABELS[c] || (c || '');
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

  function toast(msg, kind, durationMs) {
    toastEl.textContent = msg;
    toastEl.className = 'st-toast' + (kind === 'error' ? ' st-toast--error' : '');
    toastEl.style.display = 'block';
    clearTimeout(toast._t);
    toast._t = setTimeout(() => { toastEl.style.display = 'none'; }, durationMs || 4000);
  }

  // Wave C10: null -> "—" so PMax rows (cost/CPC/Cost-per-conv) display
  // as em-dash, clearly distinct from "£0.00". Same for percent fmt below.
  const EMDASH = '—';
  function fmtNum(n) { return n == null ? EMDASH : Number(n).toLocaleString(); }
  function fmtMoney(n) { return n == null ? EMDASH : '£' + Number(n).toFixed(2); }

  // -------------------- Chip rendering + interaction -----------------
  // Wave C10: Campaign Type chip row (single-select, default All).
  const SOURCE_CHIP_ORDER = [
    {key: 'all',    label: 'All'},
    {key: 'search', label: 'Search'},
    {key: 'pmax',   label: 'PMax'},
  ];
  function renderSourceChips(counts) {
    const bar = document.getElementById('stSourceBar');
    if (!bar) return;
    bar.querySelectorAll('.st-chip').forEach(el => el.remove());
    SOURCE_CHIP_ORDER.forEach(({key, label}) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'st-chip' + (campaignSource === key ? ' active' : '');
      btn.dataset.source = key;
      btn.innerHTML = `${label} <span class="st-chip__count">${counts[key] ?? 0}</span>`;
      btn.addEventListener('click', () => {
        if (campaignSource === key) return;
        campaignSource = key;
        currentPage = 1;                // reset pagination on source change
        reload();
      });
      bar.appendChild(btn);
    });
  }

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
      btn.innerHTML = `${humanReasonChip(code)} <span class="st-chip__count">${n}</span>`;
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

  let p3Counts = {pending: 0, approved: 0, pushed: 0, rejected: 0};
  function renderP3StatusChips() {
    const bar = document.getElementById('stFilterBarP3');
    bar.querySelectorAll('.st-chip').forEach(el => el.remove());
    ['pending', 'approved', 'pushed', 'rejected'].forEach(key => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'st-chip' + (p3View === key ? ' active' : '');
      btn.dataset.status = key;
      const label = key.charAt(0).toUpperCase() + key.slice(1);
      const n = p3Counts[key] || 0;
      btn.innerHTML = `${label} <span class="st-chip__count">${n}</span>`;
      btn.addEventListener('click', () => {
        if (p3View === key) return;
        p3View = key;
        currentPage = 1;
        // N1r: re-render chips so .active moves to the newly clicked chip.
        // Safe to self-call — the function clears existing chips on line 1.
        renderP3StatusChips();
        reload();
      });
      bar.appendChild(btn);
    });
  }

  // Wave G: "review" pill reads as "Needs / Review" stacked so the status
  // column communicates the action required in one glance. keep/block stay
  // single-line to keep the row height stable where possible.
  function renderPass1StatusPill(status) {
    if (status === 'review') {
      return '<span class="st-status st-status--review st-status--stacked">' +
             '<span>Needs</span><span>Review</span></span>';
    }
    return `<span class="st-status st-status--${status}">${status}</span>`;
  }

  // Wave I: single effective-status pill. Pending rows show Pass 1
  // classification; decided rows show user decision only. Filter context
  // already communicates the original classification; Reason column still
  // carries the why.
  function effectiveStatus(item) {
    return (item.review_status && item.review_status !== 'pending')
      ? item.review_status
      : item.pass1_status;
  }
  function renderStatusCell(item) {
    if (item.review_status && item.review_status !== 'pending') {
      return `<span class="st-status st-status--${item.review_status}">${item.review_status}</span>`;
    }
    return renderPass1StatusPill(item.pass1_status);
  }

  // -------------------- Row rendering (Pass 1/2 — 19 cols) -----------
  function renderRow(item) {
    const canEdit = item.pass1_status === 'block' || item.pass1_status === 'review';
    const checked = item.pass1_status === 'block' ? 'checked' : '';
    const hideChk = item.pass1_status === 'keep' ? 'style="visibility:hidden"' : '';
    const roleSel = canEdit ? roleDropdown(item.pass2_target_list_role, cfg.list_roles, item.id) : '';
    const pushErr = item.push_error ? `<span class="st-push-error">${escapeHtml(item.push_error)}</span>` : '';
    const pct = v => (v == null) ? EMDASH : (Number(v) * 100).toFixed(2) + '%';
    const num2 = v => (v == null) ? EMDASH : Number(v).toFixed(2);
    return `<tr data-id="${item.id}" data-pass1="${item.pass1_status}">
      <td class="st-col-check st-frozen-0" ${hideChk}><input type="checkbox" class="st-chk" ${checked} ${canEdit ? '' : 'disabled'}></td>
      <td class="st-col-term  st-frozen-1" title="${escapeHtml(item.search_term)}">${escapeHtml(item.search_term)}</td>
      <td>${renderStatusCell(item)}</td>
      <td title="${escapeHtml(humanReason(item.pass1_reason, item.pass1_reason_detail, item))}"><div class="clamp-2">${escapeHtml(humanReason(item.pass1_reason, item.pass1_reason_detail, item))}</div></td>
      <td>${roleSel}</td>
      <td>${escapeHtml(item.match_types || '')}</td>
      <td>${escapeHtml(humanStatuses(item.statuses))}</td>
      <td title="${escapeHtml(item.campaigns || '')}"><div class="clamp-2">${escapeHtml(item.campaigns || '')}</div></td>
      <td title="${escapeHtml(item.campaign_types || '')}">${escapeHtml(humanCampaignType(item.campaign_types))}</td>
      <td title="${escapeHtml(item.keywords || '')}"><div class="clamp-2">${escapeHtml(item.keywords || '')}</div></td>
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
    // Wave C4: prefer the live DB name for this client (refreshed every
    // ingestion); fall back to the static humanised map when the role
    // has no currently-linked list.
    const opts = options.map(r => {
      const label = liveTargetListLabels[r] || humanRole(r);
      return `<option value="${r}" ${r === current ? 'selected' : ''}>${escapeHtml(label)}</option>`;
    }).join('');
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
      const sourceParam = `&campaign_source=${encodeURIComponent(campaignSource)}`;
      url = `/v2/api/negatives/search-term-review/${CLIENT}`
          + `?view=${encodeURIComponent(view)}&date=${analysisDate}`
          + `&page=${currentPage}&page_size=${PAGE_SIZE}${reasonsParam}${sourceParam}`;
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
    approvedReadyCount = data.approved_ready_count || 0;
    applyClientSideSort();
    updateSortIndicators();

    // Repaint chips from server-side counts (Pass 1/2 only)
    if (currentTab === 'pass12') {
      if (data.campaign_source_counts) renderSourceChips(data.campaign_source_counts);
      if (data.counts) renderStatusChips(data.counts);
      if (data.reason_counts) renderReasonChips(data.reason_counts);
      renderPmaxOtherBanner(data.pmax_other_bucket);
      // Wave C4: cache live target-list labels for the dropdown
      liveTargetListLabels = data.target_list_labels || {};
    } else {
      // N1u: Pass 3 chip counts from server
      if (data.counts) {
        p3Counts = {
          pending: data.counts.pending || 0,
          approved: data.counts.approved || 0,
          pushed: data.counts.pushed || 0,
          rejected: data.counts.rejected || 0,
        };
        renderP3StatusChips();
      }
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
    // Wave D1 (Fix 3) — push button reflects ALL approved-not-pushed rows for
    // this client+date, not just what's in the current filtered view. Users
    // often approve from Block view (rows then move to Approved view) and
    // would otherwise see a greyed-out button that looks broken.
    const btn = document.getElementById('stPushApproved');
    btn.disabled = approvedReadyCount === 0;
    btn.textContent = approvedReadyCount > 0
      ? `Push ${approvedReadyCount} approved to Google Ads`
      : 'Push approved to Google Ads';
    // Helpful tooltip when approved rows exist but aren't visible under
    // current filters — explains why the user can't see them in the table.
    const approvedInView = lastItems.some(i =>
      i.review_status === 'approved' && !i.pushed_to_ads_at);
    if (approvedReadyCount > 0 && !approvedInView) {
      btn.title = `${approvedReadyCount} row(s) approved. Switch to the "Approved" status filter to view them before pushing.`;
    } else {
      btn.removeAttribute('title');
    }
  }

  // ---------- Wave D1: client-side column sort -----------------------
  // Compare helper: nulls last in both directions so "—" rows sink.
  function _cmp(a, b) {
    if (a == null && b == null) return 0;
    if (a == null) return 1;
    if (b == null) return -1;
    if (typeof a === 'number' && typeof b === 'number') return a - b;
    return String(a).localeCompare(String(b));
  }
  // Wave I: status sort uses the effective-status pill the user actually sees
  // (review_status when decided, else pass1_status). Alphabetical ordering
  // keeps approved/block/expired/keep/pushed/rejected/review grouped sensibly.
  function _sortValue(item, key) {
    if (key === 'pass1_status') return effectiveStatus(item);
    const v = item[key];
    if (v == null) return null;
    if (typeof v === 'number') return v;
    // numeric columns come through as numbers from the API already
    return v;
  }
  function applyClientSideSort() {
    if (!sortKey) return;
    const dirMul = sortDir === 'asc' ? 1 : -1;
    lastItems.sort((a, b) => dirMul * _cmp(_sortValue(a, sortKey), _sortValue(b, sortKey)));
  }
  function updateSortIndicators() {
    document.querySelectorAll('#stTable thead th.st-sortable').forEach(th => {
      const ind = th.querySelector('.st-sort-ind');
      if (th.dataset.sort === sortKey) {
        th.classList.add('st-sort-active');
        if (ind) ind.textContent = sortDir === 'asc' ? '▲' : '▼';
      } else {
        th.classList.remove('st-sort-active');
        if (ind) ind.textContent = '';
      }
    });
  }
  function wireSortHeaders() {
    document.querySelectorAll('#stTable thead th.st-sortable').forEach(th => {
      th.addEventListener('click', () => {
        const key = th.dataset.sort;
        if (!key) return;
        if (sortKey === key) {
          sortDir = sortDir === 'asc' ? 'desc' : 'asc';
        } else {
          sortKey = key;
          // First click on numeric cols -> DESC (highest spend first);
          // First click on text cols -> ASC (alphabetical).
          const numericKeys = new Set([
            'total_cost','total_impressions','total_clicks','avg_cpc','ctr',
            'total_conversions','cost_per_conversion','conversion_rate',
          ]);
          sortDir = numericKeys.has(key) ? 'desc' : 'asc';
        }
        applyClientSideSort();
        updateSortIndicators();
        tbody.innerHTML = lastItems.length
          ? lastItems.map(renderRow).join('')
          : '<tr><td colspan="19" class="st-loading">No matching rows</td></tr>';
        updateButtons();
      });
    });
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
      // Label is re-derived from approvedReadyCount inside updateButtons()
      // (called by reload() on success, or here on error).
      updateButtons();
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
    document.getElementById('stSourceBar').style.display = tab === 'pass12' ? '' : 'none';
    const srcNote = document.getElementById('stSourceNote');
    if (srcNote) srcNote.style.display = tab === 'pass12' ? '' : 'none';
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

  // --------- N2 Part 2/4/5: refresh snapshot + reclassify + sync pill -------
  async function loadSyncPill() {
    const txt = document.getElementById('stNegSyncText');
    const pill = document.getElementById('stNegSyncPill');
    if (!txt || !pill) return;
    try {
      const resp = await fetch(`/v2/api/negatives/lists?client_id=${encodeURIComponent(CLIENT)}`);
      const data = await resp.json();
      pill.classList.remove('neg-sync--green','neg-sync--amber','neg-sync--red','neg-sync--none');
      if (!data.last_synced_at) {
        pill.classList.add('neg-sync--none');
        txt.textContent = 'No negative snapshot yet';
        return;
      }
      const d = new Date(data.last_synced_at);
      const ageHrs = (Date.now() - d.getTime()) / 3600000;
      const zone = ageHrs < 24 ? 'neg-sync--green' : ageHrs < 48 ? 'neg-sync--amber' : 'neg-sync--red';
      pill.classList.add(zone);
      const rel = ageHrs < 1 ? `${Math.max(1, Math.floor(ageHrs*60))}m ago`
                 : ageHrs < 48 ? `${Math.floor(ageHrs)}h ago`
                 : `${Math.floor(ageHrs/24)}d ago`;
      const nice = d.toLocaleString('en-GB', { day:'2-digit', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit' });
      txt.textContent = `Negatives: ${nice} (${rel})`;
    } catch (e) {
      pill.classList.add('neg-sync--none');
      txt.textContent = 'Negatives: — (error)';
    }
  }
  loadSyncPill();

  const btnRefresh = document.getElementById('stRefreshNegs');
  if (btnRefresh) btnRefresh.addEventListener('click', async () => {
    const orig = btnRefresh.innerHTML;
    btnRefresh.disabled = true; btnRefresh.textContent = 'Refreshing…';
    try {
      const resp = await fetch('/v2/api/negatives/refresh-snapshot', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ client_id: CLIENT }),
      });
      const data = await resp.json();
      if (resp.status === 409) {
        toast('Refresh already running.', 'error');
      } else if (data.status === 'ok') {
        toast(`Synced ${data.list_count} lists, ${data.keyword_count} keywords in ${data.duration_seconds}s`);
        loadSyncPill();
      } else {
        toast('Refresh failed: ' + (data.message || 'Unknown'), 'error');
      }
    } catch (e) {
      toast('Refresh failed: ' + e.message, 'error');
    } finally {
      btnRefresh.disabled = false; btnRefresh.innerHTML = orig;
    }
  });

  // N2-polish-1: in-app confirm modal (replaces crude window.confirm).
  // Lightweight: injected on demand, removed on resolve. Returns a Promise.
  function showConfirmModal({ title, bodyHtml, confirmLabel = 'Confirm', cancelLabel = 'Cancel' }) {
    return new Promise(resolve => {
      const wrap = document.createElement('div');
      wrap.className = 'act-confirm-overlay';
      wrap.innerHTML = `
        <div class="act-confirm" role="dialog" aria-modal="true" aria-labelledby="actConfirmTitle">
          <div class="act-confirm__header">
            <h3 id="actConfirmTitle" class="act-confirm__title">${title}</h3>
          </div>
          <div class="act-confirm__body">${bodyHtml}</div>
          <div class="act-confirm__footer">
            <button type="button" class="btn-act btn-act--decline" data-role="cancel">${cancelLabel}</button>
            <button type="button" class="btn-act btn-act--approve" data-role="confirm">${confirmLabel}</button>
          </div>
        </div>`;
      document.body.appendChild(wrap);
      const cleanup = (val) => { wrap.remove(); document.removeEventListener('keydown', onKey); resolve(val); };
      const onKey = (e) => {
        if (e.key === 'Escape') cleanup(false);
        if (e.key === 'Enter')  cleanup(true);
      };
      document.addEventListener('keydown', onKey);
      wrap.addEventListener('click', (e) => { if (e.target === wrap) cleanup(false); });
      wrap.querySelector('[data-role="cancel"]').addEventListener('click', () => cleanup(false));
      wrap.querySelector('[data-role="confirm"]').addEventListener('click', () => cleanup(true));
      // Autofocus primary action for keyboard confirm
      setTimeout(() => wrap.querySelector('[data-role="confirm"]').focus(), 0);
    });
  }

  const btnReclass = document.getElementById('stReclassify');
  if (btnReclass) btnReclass.addEventListener('click', async () => {
    const confirmed = await showConfirmModal({
      title: "Reclassify today's terms",
      bodyHtml: `
        <p>Re-run Pass 1 + Pass 2 on today's search terms using the current config and latest negative list snapshot.</p>
        <ul class="act-confirm__list">
          <li><span class="act-confirm__ok">✓</span> Approved / pushed / rejected / expired rows are preserved</li>
          <li><span class="act-confirm__change">↻</span> Pending rows are re-classified in place</li>
          <li><span class="act-confirm__add">+</span> New terms are added</li>
        </ul>
      `,
      confirmLabel: 'Reclassify',
      cancelLabel: 'Cancel',
    });
    if (!confirmed) return;
    const orig = btnReclass.innerHTML;
    btnReclass.disabled = true; btnReclass.textContent = 'Reclassifying…';
    try {
      const resp = await fetch('/v2/api/negatives/reclassify-now', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ client_id: CLIENT, analysis_date: analysisDate }),
      });
      const data = await resp.json();
      if (resp.status === 409) {
        toast('Reclassify already running.', 'error');
      } else if (data.status === 'ok') {
        // N2-polish-1: no full page reload. Toast persists 5s, table
        // reloads in place via existing AJAX reload() so the user can
        // see the confirmation and the refreshed rows.
        toast(`Reclassified ${data.updated} pending rows in ${data.duration_seconds}s (ins=${data.inserted} preserved=${data.preserved})`, undefined, 5000);
        currentPage = 1;
        await reload();
      } else {
        toast('Reclassify failed: ' + (data.message || 'Unknown'), 'error');
      }
    } catch (e) {
      toast('Reclassify failed: ' + e.message, 'error');
    } finally {
      btnReclass.disabled = false; btnReclass.innerHTML = orig;
    }
  });
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

  // Wave D1: wire sortable headers once (thead is static).
  wireSortHeaders();

  // Initial load
  reload();
})();
