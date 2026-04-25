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
  // Stage 8: total filtered row count from the server (= data.total, NOT
  // lastItems.length). Drives the AI panel context-header row count.
  let lastTotal = 0;
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
  // Fix 1.4 — stable session row numbering. After a bulk action we mark
  // rows in place rather than calling reload(), so row numbers don't
  // renumber mid-session. sessionTotal/sessionActioned drive the
  // "X of N actioned" header. hideActioned toggles a CSS class that
  // visually hides actioned rows without removing them from the DOM
  // (so remaining numbers stay 1..N gap-free in user's reference).
  let sessionTotal = 0;
  let sessionActioned = 0;
  let hideActioned = false;
  // IDs actioned IN THIS SESSION (not pre-decided rows from server). Survives
  // sort re-renders so the .actioned class + checkbox lock stick.
  let sessionActionedIds = new Set();

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
    // N3 Part B: mixed-intent downgrade — detail format
    // "adv: <phrase> | not-adv: <phrase>"
    mixed_intent_adv_and_notadv:    d => d ? `Mixed intent — ${d}` : 'Mixed intent (adv + not-adv)',
    sticky_rejected:                d => d ? `Sticky rejected — ${d}` : 'Sticky rejected',
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
        reload({preserveSession: true});  // Fix 1.4 follow-up Issue 2
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
        reload({preserveSession: true});  // Fix 1.4 follow-up Issue 2
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
        reload({preserveSession: true});  // Fix 1.4 follow-up Issue 2
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
        reload({preserveSession: true});  // Fix 1.4 follow-up Issue 2
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
        reload({preserveSession: true});  // Fix 1.4 follow-up Issue 2
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
  function renderRow(item, idx) {
    // Fix 1.4 — once a row has been actioned IN THIS SESSION, it's locked
    // and visually struck-through. Pre-decided rows from server (e.g. the
    // Approved filter view) keep their normal styling — only their status
    // pill differs. canEdit drives both checkbox + role dropdown enabled
    // state, so a sort-driven re-render preserves the locked state.
    const isActioned = sessionActionedIds.has(item.id);
    const canEdit = !isActioned
      && (item.pass1_status === 'block' || item.pass1_status === 'review');
    const checked = (!isActioned && item.pass1_status === 'block') ? 'checked' : '';
    const hideChk = item.pass1_status === 'keep' ? 'style="visibility:hidden"' : '';
    // Show the chosen role disabled on actioned rows so the user can still
    // see what they picked even after a sort re-render.
    let roleSel = '';
    if (canEdit) {
      roleSel = roleDropdown(item.pass2_target_list_role, cfg.list_roles, item.id);
    } else if (isActioned) {
      const lbl = liveTargetListLabels[item.pass2_target_list_role] || humanRole(item.pass2_target_list_role);
      roleSel = `<select class="st-target-select" disabled><option>${escapeHtml(lbl)}</option></select>`;
    }
    const pushErr = item.push_error ? `<span class="st-push-error">${escapeHtml(item.push_error)}</span>` : '';
    const pct = v => (v == null) ? EMDASH : (Number(v) * 100).toFixed(2) + '%';
    const num2 = v => (v == null) ? EMDASH : Number(v).toFixed(2);
    // N3g: continuous row # across pagination.
    const rowNum = (currentPage - 1) * PAGE_SIZE + (idx || 0) + 1;
    const actionedCls = isActioned ? ' class="actioned"' : '';
    // Stage 7 — data-ai-verdict on <tr> drives the "Only show unsure"
    // filter via a single CSS class on tbody (no reload — pure client-side).
    const aiVerdictAttr = item.ai_verdict
      ? ` data-ai-verdict="${item.ai_verdict}"`
      : '';
    return `<tr data-id="${item.id}" data-pass1="${item.pass1_status}"${aiVerdictAttr}${actionedCls}>
      <td class="col-num">${rowNum}</td>
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
      ${renderAIVerdictCell(item)}
      ${renderAIConfidenceCell(item)}
      ${renderAIExplainCell(item)}
    </tr>`;
  }

  // -------------------- Stage 7 — AI cells + buttons -----------------
  function renderAIVerdictCell(item) {
    if (item.ai_verdict == null) return '<td class="ai-verdict-empty">—</td>';
    const reasoning = item.ai_reasoning || '';
    const tip = reasoning.length > 200
      ? reasoning.slice(0, 200) + '…'
      : reasoning;
    const tipAttr = tip ? ` title="${escapeHtml(tip)}"` : '';
    const intent = item.ai_intent_tag
      ? `<span class="ai-intent-tag">${escapeHtml(item.ai_intent_tag)}</span>`
      : '';
    return `<td><span class="ai-verdict-pill ai-verdict-${item.ai_verdict}"${tipAttr}>${item.ai_verdict}</span>${intent}</td>`;
  }
  function renderAIConfidenceCell(item) {
    if (item.ai_confidence == null) return '<td class="ai-verdict-empty">—</td>';
    return `<td><span class="ai-conf-pill ai-conf-${item.ai_confidence}">${item.ai_confidence}</span></td>`;
  }
  function renderAIExplainCell(item) {
    // Stage 5 scope: explain-row endpoint accepts review_id only — Pass 3
    // (act_v2_phrase_suggestions) is out of scope this stage. We're inside
    // the Pass 1/2 renderer so all rows here are review-table rows; render
    // the link unconditionally. Pass 3 uses a separate renderP3Row().
    return `<td><a class="ai-explain-link" data-row-id="${item.id}" data-search-term="${escapeHtml(item.search_term)}">🔍 Explain</a></td>`;
  }

  // Derive the classify-terms `flow` from current filter state. Returns
  // null when ambiguous (statusView='all' or campaignSource='all') —
  // caller surfaces a toast asking the user to narrow filters.
  function getCurrentFlowOrNull() {
    if (currentTab === 'pass3') return 'pass3';
    const sv = statusView;
    const cs = campaignSource;
    if (cs === 'all' || sv === 'all') return null;
    if (sv !== 'block' && sv !== 'review') return null;
    return `${cs}_${sv}`;
  }
  // Per-row explain only needs review_id + a flow for chat_log scoping.
  // When the user has narrowed to a specific flow, use it; otherwise pick
  // a sensible fallback per row (campaign type + pass1_status).
  function getExplainFlow(item) {
    const f = getCurrentFlowOrNull();
    if (f && f !== 'pass3') return f;
    const ct = (item.campaign_types || '').toLowerCase();
    const cs = ct.includes('performance_max') ? 'pmax' : 'search';
    const sv = (item.pass1_status === 'review') ? 'review' : 'block';
    return `${cs}_${sv}`;
  }

  function getPendingClassifiableIds() {
    return lastItems
      .filter(it => it.review_status === 'pending'
        && (it.pass1_status === 'block' || it.pass1_status === 'review')
        && it.ai_verdict == null)
      .map(it => it.id);
  }
  function updateAITriageBadge() {
    const el = document.getElementById('aiTriageCount');
    if (!el) return;
    const n = getPendingClassifiableIds().length;
    el.textContent = `(${n} pending)`;
    const btn = document.getElementById('btnAITriage');
    if (btn) btn.disabled = (n === 0);
  }
  function updateApplyHCButton() {
    const btn = document.getElementById('btnApplyHighConf');
    const badge = document.getElementById('applyHighConfCount');
    if (!btn || !badge) return;
    const hcRows = lastItems.filter(it =>
      it.ai_confidence === 'high'
      && it.review_status === 'pending'
      && (it.ai_verdict === 'approve' || it.ai_verdict === 'reject'));
    if (hcRows.length === 0) {
      btn.style.display = 'none';
    } else {
      btn.style.display = '';
      // Stage 7.5: show breakdown so users know what will happen BEFORE
      // clicking. ACT-terminology mapping: approve=block, reject=keep.
      const approveCount = hcRows.filter(r => r.ai_verdict === 'approve').length;
      const rejectCount = hcRows.filter(r => r.ai_verdict === 'reject').length;
      badge.textContent =
        `(${hcRows.length}: ${approveCount} block / ${rejectCount} keep)`;
    }
  }

  // Stage 7.6: drop-in styled replacement for window.confirm — Promise
  // returns true on OK, false on Cancel / Escape / backdrop. Enter
  // confirms (the OK button is auto-focused on open).
  //
  // SECURITY: `body` is rendered as HTML so callers can include lists,
  // <strong>, etc. Callers MUST escapeHtml() any user-controlled content
  // they interpolate into the body. `title`, `okLabel`, `cancelLabel`
  // ARE escaped automatically.
  function aiConfirm({title, body, okLabel = 'OK', cancelLabel = 'Cancel',
                       okStyle = 'primary'}) {
    return new Promise((resolve) => {
      const overlay = document.createElement('div');
      overlay.className = 'ai-confirm-modal';
      overlay.innerHTML = `
        <div class="ai-confirm-content" role="dialog" aria-modal="true">
          <div class="ai-confirm-header">${escapeHtml(title)}</div>
          <div class="ai-confirm-body">${body}</div>
          <div class="ai-confirm-footer">
            <button type="button" class="btn-act ai-confirm-cancel">${escapeHtml(cancelLabel)}</button>
            <button type="button" class="btn-act ai-confirm-ok ai-confirm-ok--${escapeHtml(okStyle)}">${escapeHtml(okLabel)}</button>
          </div>
        </div>`;
      document.body.appendChild(overlay);
      const cleanup = (result) => {
        document.removeEventListener('keydown', onKey);
        overlay.remove();
        resolve(result);
      };
      const onKey = (e) => {
        if (e.key === 'Escape') cleanup(false);
        if (e.key === 'Enter')  cleanup(true);
      };
      overlay.querySelector('.ai-confirm-ok')
        .addEventListener('click', () => cleanup(true));
      overlay.querySelector('.ai-confirm-cancel')
        .addEventListener('click', () => cleanup(false));
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) cleanup(false);
      });
      document.addEventListener('keydown', onKey);
      // Auto-focus OK so Enter works immediately
      setTimeout(() => overlay.querySelector('.ai-confirm-ok').focus(), 0);
    });
  }

  // ============================================================
  // Stage 8 — AI panel: collapse/expand state + context header.
  // Stage 9 fills the body with chat. Stage 10 adds canned replies.
  // ============================================================
  const AI_PANEL_STATE_KEY = 'act_ai_panel_state';   // 'open' | 'collapsed'

  function getAIPanelState() {
    const v = localStorage.getItem(AI_PANEL_STATE_KEY);
    return (v === 'collapsed' || v === 'open') ? v : 'open';
  }
  function setAIPanelState(state) {
    localStorage.setItem(AI_PANEL_STATE_KEY, state);
    const grid = document.getElementById('aiPageGrid');
    const strip = document.getElementById('btnAIPanelExpand');
    if (grid) grid.dataset.panelState = state;
    if (strip) strip.style.display = state === 'collapsed' ? '' : 'none';
  }

  // Friendly label builder — uses what the user has selected even when
  // it's ambiguous (e.g. "All > Block" or "Search > All"). Falls back
  // to "Pass 3 Suggestions" on the pass3 tab.
  function _aiPanelFlowLabel() {
    if (currentTab === 'pass3') return 'Pass 3 Suggestions';
    const sourceMap = {all: 'All', search: 'Search', pmax: 'PMax'};
    const statusMap = {
      all: 'All', pending: 'Pending', block: 'Block', review: 'Review',
      keep: 'Keep', approved: 'Approved', pushed: 'Pushed',
      rejected: 'Rejected', expired: 'Expired',
    };
    const cs = sourceMap[campaignSource] || campaignSource || 'All';
    const sv = statusMap[statusView] || statusView || 'All';
    return `${cs} > ${sv}`;
  }

  function updateAIPanelContext() {
    const ctx = document.getElementById('aiPanelContext');
    if (!ctx) return;
    const flowLabel = _aiPanelFlowLabel();
    const clientName = (cfg && (cfg.client_name || cfg.client_id)) || '—';
    const dateStr = analysisDate || '—';
    const rowsLabel = lastTotal === 1 ? 'row' : 'rows';
    ctx.innerHTML =
      `<strong>${escapeHtml(flowLabel)}</strong> · `
      + `${lastTotal} ${rowsLabel} · `
      + `${escapeHtml(clientName)} · `
      + `${escapeHtml(dateStr)}`;
  }

  // Banners — info auto-dismisses, error stays until clicked
  function aiBanner(kind, msg) {
    const host = document.querySelector('.st-action-bar');
    if (!host) return;
    const el = document.createElement('div');
    el.className = kind === 'error' ? 'ai-error-banner' : 'ai-info-banner';
    el.innerHTML = `<span></span><button type="button" aria-label="Dismiss">×</button>`;
    el.firstElementChild.textContent = msg;
    el.lastElementChild.addEventListener('click', () => el.remove());
    host.parentNode.insertBefore(el, host.nextSibling);
    if (kind !== 'error') {
      setTimeout(() => { if (el.parentNode) el.remove(); }, 5000);
    }
  }

  // === AI Triage button ===
  async function fireAITriage() {
    const flow = getCurrentFlowOrNull();
    if (!flow) {
      aiBanner('error',
        "Pick a campaign source (Search / PMax) AND a status (Block / Review) before AI Triage — current filters are too broad.");
      return;
    }
    const ids = getPendingClassifiableIds();
    if (!ids.length) {
      aiBanner('info', 'No pending rows to classify on this page.');
      return;
    }
    if (ids.length > 100) {
      // Stage 7.6: styled confirm replacing native window.confirm.
      // Token estimate is ~5K per ~50-row batch (page-25-batches use
      // ~5K each per Stage 6 measurements).
      const tokensApprox = Math.ceil(ids.length / 50) * 5;
      const ok = await aiConfirm({
        title: `Classify ${ids.length} rows?`,
        body: `This will use approximately <strong>~${tokensApprox}K tokens</strong> of your AI quota.`,
        okLabel: 'Classify',
        okStyle: 'primary',
      });
      if (!ok) return;
    }
    const btn = document.getElementById('btnAITriage');
    btn.disabled = true;
    const origLabel = btn.innerHTML;
    btn.innerHTML = '🤖 AI Triage … <span class="ai-skeleton" style="width:40px"></span>';
    setAILoadingState(ids);
    try {
      const data = await apiPost(
        '/v2/api/ai/classify-terms',
        {
          client_id: CLIENT,
          analysis_date: analysisDate,
          flow,
          review_ids: ids,
          force_reclassify: false,
        },
      );
      await reload({preserveSession: true});
      if (data.classified === 0 && data.skipped_already_classified > 0) {
        aiBanner('info',
          `All ${data.skipped_already_classified} rows were already classified at the current prompt version. Display refreshed.`);
      } else if (data.classified > 0) {
        aiBanner('info',
          `Classified ${data.classified} rows in ${(data.wall_clock_ms / 1000).toFixed(1)}s. ${data.tokens_used} tokens used.`);
      }
    } catch (e) {
      aiBanner('error', `AI Triage failed: ${e.message}`);
    } finally {
      btn.disabled = false;
      btn.innerHTML = origLabel;
      updateAITriageBadge();
      updateApplyHCButton();
    }
  }

  // === Apply high-confidence button ===
  async function applyHighConf() {
    const hcRows = lastItems.filter(it =>
      it.ai_confidence === 'high'
      && it.review_status === 'pending'
      && (it.ai_verdict === 'approve' || it.ai_verdict === 'reject'));
    if (!hcRows.length) {
      aiBanner('info', 'No high-confidence AI verdicts pending.');
      return;
    }
    // Stage 7.5/7.6: compute id splits BEFORE the confirm so the dialog
    // shows the exact breakdown. Stage 7.6 swapped native window.confirm
    // for the styled aiConfirm modal.
    const approveIds = hcRows
      .filter(r => r.ai_verdict === 'approve').map(r => r.id);
    const rejectIds = hcRows
      .filter(r => r.ai_verdict === 'reject').map(r => r.id);
    const ok = await aiConfirm({
      title: `Apply ${hcRows.length} high-confidence AI verdicts?`,
      body: `
        <ul style="line-height:1.6; padding-left:20px; margin:0;">
          <li><strong>${approveIds.length}</strong> will be <strong>blocked</strong> (pushed as negatives in Google Ads)</li>
          <li><strong>${rejectIds.length}</strong> will be <strong>kept running</strong> (rejection of the block)</li>
        </ul>
        <p style="margin:12px 0 0; color: var(--text-muted); font-size: 12px;">You can still review them individually in the Approved / Rejected tabs before pushing to Google Ads.</p>
      `,
      okLabel: 'Apply AI calls',
      okStyle: 'primary',
    });
    if (!ok) return;
    try {
      // Reuse the negatives bulk-update endpoint. Stage 7 follows the
      // existing bulkUpdate pattern but with a pre-built id list rather
      // than reading checkboxes.
      const endpoint = '/v2/api/negatives/search-term-review/bulk-update';
      let total = 0;
      if (approveIds.length) {
        const res = await apiPost(endpoint, {
          client_id: CLIENT,
          items: approveIds.map(id => ({id, review_status: 'approved'})),
        });
        approveIds.forEach(id => markRowActioned(id, 'approved'));
        total += res.updated_count || approveIds.length;
      }
      if (rejectIds.length) {
        const res = await apiPost(endpoint, {
          client_id: CLIENT,
          items: rejectIds.map(id => ({id, review_status: 'rejected'})),
        });
        rejectIds.forEach(id => markRowActioned(id, 'rejected'));
        total += res.updated_count || rejectIds.length;
      }
      sessionActioned += approveIds.length + rejectIds.length;
      updateSessionProgress();
      // Optimistic top-card + chip updates (mirrors bulkUpdate).
      bumpCard('cntPending', -(approveIds.length + rejectIds.length));
      bumpCard('cntApproved', approveIds.length);
      bumpCard('cntRejected', rejectIds.length);
      const sourceChip = statusView === 'pending' ? 'review' : statusView;
      if (sourceChip && sourceChip !== 'all') {
        bumpChip(sourceChip, -(approveIds.length + rejectIds.length));
      }
      bumpChip('approved', approveIds.length);
      bumpChip('rejected', rejectIds.length);
      approvedReadyCount += approveIds.length;
      updateButtons();
      updateApplyHCButton();
      toast(`Applied ${total} AI verdict(s).`);
    } catch (e) {
      aiBanner('error', `Apply high-confidence failed: ${e.message}`);
    }
  }

  // === "Only show unsure" filter (pure client-side; no reload). ===
  // KNOWN LIMIT — Tier 2.2 polish: pagination is server-side, so a page
  // with zero unsure rows looks empty under filter even if other pages
  // have unsures. Acceptable for MVP — user can switch off + paginate.
  function toggleUnsureFilter() {
    const btn = document.getElementById('btnFilterUnsure');
    const active = btn.dataset.active === 'true';
    btn.dataset.active = active ? 'false' : 'true';
    if (stTable) stTable.classList.toggle('only-unsure', !active);
  }

  // ============================================================
  // Stage 9 — chat panel (free-text Opus + history hydration +
  // explain redirect into the chat stream).
  // ============================================================

  // In-flight latch — set true while ANY chat-style call is running
  // (chat send OR explain-into-panel). Prevents the user from firing
  // a second request before the first completes (the lock is also
  // enforced server-side via locks.LockContentionError, but checking
  // here is a friendlier UX — we surface a system bubble instead of
  // a 409 banner).
  let aiChatLoading = false;

  async function hydrateChatHistory() {
    const flow = getCurrentFlowOrNull();
    if (!flow || !analysisDate) {
      renderChatMessages([]);
      return;
    }
    try {
      const url = '/v2/api/ai/chat-history'
        + `?client_id=${encodeURIComponent(CLIENT)}`
        + `&flow=${encodeURIComponent(flow)}`
        + `&analysis_date=${encodeURIComponent(analysisDate)}`
        + '&limit=50';
      const r = await fetch(url, {credentials: 'same-origin'});
      if (!r.ok) {
        renderChatMessages([]);
        return;
      }
      const data = await r.json();
      renderChatMessages(data.messages || []);
    } catch (e) {
      console.warn('chat-history fetch failed:', e);
      renderChatMessages([]);
    }
  }

  function renderChatMessages(messages) {
    const list = document.getElementById('aiChatMessages');
    const empty = document.getElementById('aiChatEmpty');
    if (!list) return;
    // Strip existing message DOM (preserve the empty placeholder)
    Array.from(list.querySelectorAll('.ai-chat-msg, .ai-chat-typing'))
      .forEach(el => el.remove());
    if (!messages.length) {
      if (empty) empty.style.display = '';
      return;
    }
    if (empty) empty.style.display = 'none';
    for (const msg of messages) list.appendChild(buildMsgEl(msg));
    scrollChatToBottom();
  }

  function buildMsgEl(msg) {
    const el = document.createElement('div');
    const role = msg.role === 'user'
      ? 'user'
      : (msg.role === 'system' ? 'system' : 'assistant');
    el.className = `ai-chat-msg ai-chat-msg-${role}`;
    // Special pill for explain-marker user rows (related_review_id set)
    if (role === 'user' && msg.related_review_id) {
      el.className = 'ai-chat-msg ai-chat-msg-explain-marker';
    }
    const safe = (msg.message && msg.message.trim())
      ? msg.message
      : '[no response — try again]';
    // Bullet detection: accept both "- " and "* " (multiline regex).
    const hasBullets = /^\s*[-*]\s/m.test(safe);
    if (role === 'assistant' && hasBullets) {
      const lines = safe.split('\n').filter(l => l.trim());
      const bullets = lines.filter(l => /^\s*[-*]\s/.test(l));
      const nonBullets = lines.filter(l => !/^\s*[-*]\s/.test(l));
      const prelude = nonBullets
        .map(l => `<p>${escapeHtml(l)}</p>`).join('');
      const ul = bullets.length
        ? '<ul>' + bullets
            .map(l => `<li>${escapeHtml(l.replace(/^\s*[-*]\s*/, ''))}</li>`)
            .join('') + '</ul>'
        : '';
      el.innerHTML = prelude + ul;
    } else {
      el.innerHTML = `<div>${escapeHtml(safe).replace(/\n/g, '<br>')}</div>`;
    }
    return el;
  }

  function scrollChatToBottom() {
    const list = document.getElementById('aiChatMessages');
    if (list) list.scrollTop = list.scrollHeight;
  }

  function appendChatMsg(msg) {
    const empty = document.getElementById('aiChatEmpty');
    if (empty) empty.style.display = 'none';
    const list = document.getElementById('aiChatMessages');
    if (!list) return;
    list.appendChild(buildMsgEl(msg));
    scrollChatToBottom();
  }

  function appendTypingIndicator() {
    const list = document.getElementById('aiChatMessages');
    if (!list) return;
    const el = document.createElement('div');
    el.className = 'ai-chat-typing';
    el.id = 'aiChatTyping';
    el.innerHTML = '<span class="ai-chat-typing-dot"></span>'
      + '<span class="ai-chat-typing-dot"></span>'
      + '<span class="ai-chat-typing-dot"></span>';
    list.appendChild(el);
    scrollChatToBottom();
  }
  function removeTypingIndicator() {
    const el = document.getElementById('aiChatTyping');
    if (el) el.remove();
  }

  async function sendChatMessage() {
    if (aiChatLoading) return;
    const input = document.getElementById('aiChatInput');
    const message = input ? input.value.trim() : '';
    if (!message) return;
    const flow = getCurrentFlowOrNull();
    if (!flow) {
      appendChatMsg({
        role: 'system',
        message: 'Pick a campaign source (Search / PMax) AND a status (Block / Review) before chatting — current filters are too broad.',
      });
      return;
    }

    aiChatLoading = true;
    const sendBtn = document.getElementById('btnAIChatSend');
    if (sendBtn) sendBtn.disabled = true;

    appendChatMsg({role: 'user', message});
    input.value = '';
    if (getAIPanelState() === 'collapsed') setAIPanelState('open');
    appendTypingIndicator();

    try {
      const r = await fetch('/v2/api/ai/chat', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          client_id: CLIENT,
          flow,
          analysis_date: analysisDate,
          message,
        }),
      });
      removeTypingIndicator();
      if (!r.ok) {
        const err = await r.json().catch(() => ({error: r.statusText}));
        appendChatMsg({
          role: 'system',
          message: `Chat failed: ${err.error || r.statusText}`,
        });
        return;
      }
      const data = await r.json();
      appendChatMsg({role: 'assistant', message: data.response});
    } catch (e) {
      removeTypingIndicator();
      appendChatMsg({role: 'system', message: `Chat error: ${e.message}`});
    } finally {
      aiChatLoading = false;
      if (sendBtn) sendBtn.disabled = false;
      if (input) input.focus();
    }
  }

  async function clearChat() {
    const flow = getCurrentFlowOrNull();
    if (!flow) {
      appendChatMsg({
        role: 'system',
        message: 'No chat thread bound to the current view (filter ambiguous).',
      });
      return;
    }
    const ok = await aiConfirm({
      title: 'Clear this conversation?',
      body: 'All messages for the current view will be hidden. (Soft delete — recoverable from the database.)',
      okLabel: 'Clear',
      okStyle: 'danger',
    });
    if (!ok) return;
    try {
      const r = await fetch('/v2/api/ai/chat-clear', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          client_id: CLIENT,
          flow,
          analysis_date: analysisDate,
        }),
      });
      if (r.ok) {
        renderChatMessages([]);
      } else {
        aiBanner('error', 'Clear chat failed');
      }
    } catch (e) {
      aiBanner('error', `Clear chat error: ${e.message}`);
    }
  }

  // Replaces the Stage 7 transitional Explain modal. Per-row Explain
  // now appends to the chat stream — auto-expands the panel if it's
  // collapsed so the user actually SEES their request + reply.
  async function explainRowInPanel(reviewId, searchTerm, item) {
    if (aiChatLoading) {
      appendChatMsg({
        role: 'system',
        message: 'Another AI call is in flight — wait for it to finish.',
      });
      return;
    }
    aiChatLoading = true;
    if (getAIPanelState() === 'collapsed') setAIPanelState('open');

    appendChatMsg({
      role: 'user',
      message: `🔍 Explain row [${reviewId}]: "${searchTerm}"`,
      related_review_id: reviewId,
    });
    appendTypingIndicator();

    try {
      const r = await fetch('/v2/api/ai/explain-row', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          client_id: CLIENT,
          review_id: reviewId,
          flow: getExplainFlow(item || {}),
          analysis_date: analysisDate,
        }),
      });
      removeTypingIndicator();
      if (!r.ok) {
        const err = await r.json().catch(() => ({error: r.statusText}));
        appendChatMsg({
          role: 'system',
          message: `Explain failed: ${err.error || r.statusText}`,
        });
        return;
      }
      const data = await r.json();
      appendChatMsg({role: 'assistant', message: data.explanation});
    } catch (e) {
      removeTypingIndicator();
      appendChatMsg({role: 'system', message: `Explain error: ${e.message}`});
    } finally {
      aiChatLoading = false;
    }
  }

  // === Loading skeleton state for AI cells during a triage call ===
  function setAILoadingState(reviewIds) {
    const idSet = new Set(reviewIds);
    if (!stTable) return;
    stTable.querySelectorAll('tr[data-id]').forEach(tr => {
      const id = parseInt(tr.dataset.id, 10);
      if (!idSet.has(id)) return;
      const cells = tr.children;
      // Last 3 cells are the AI columns (positions 21/22/23 = indexes 20/21/22)
      const verdictCell = cells[20];
      const confCell = cells[21];
      if (verdictCell) verdictCell.innerHTML = '<span class="ai-skeleton"></span>';
      if (confCell) confCell.innerHTML = '<span class="ai-skeleton" style="width:40px"></span>';
    });
  }

  // -------------------- Row rendering (Pass 3) -----------------------
  function renderP3Row(item, idx) {
    // Fix 1.4 — same actioned-row lock as Pass 1/2 (in-session only).
    const isActioned = sessionActionedIds.has(item.id);
    const roleSel = isActioned
      ? `<select class="st-target-select" disabled><option>${humanRole(item.target_list_role)}</option></select>`
      : roleDropdown(item.target_list_role, cfg.phrase_roles, item.id);
    const chkAttrs = isActioned
      ? 'disabled'
      : (item.word_count >= 2 ? 'checked' : '');  // 1-word unchecked
    const pushErr = item.push_error ? `<span class="st-push-error">${escapeHtml(item.push_error)}</span>` : '';
    const sources = (item.source_search_terms || []).slice(0, 20).join(', ');
    const reviewed = item.review_status !== 'pending'
      ? `<span class="st-status st-status--${item.review_status}">${item.review_status}</span>`
      : '<span class="st-status st-status--review">pending</span>';
    const rowNum = (currentPage - 1) * PAGE_SIZE + (idx || 0) + 1;
    const actionedCls = isActioned ? ' class="actioned"' : '';
    return `<tr data-id="${item.id}"${actionedCls}>
      <td class="col-num">${rowNum}</td>
      <td><input type="checkbox" class="st-chk" ${chkAttrs}></td>
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
  // Fix 1.4 follow-up (Issue 2): chip filters (status / reason / source / p3)
  // are not a context boundary — they're just a view filter on the same
  // dataset — so the in-session actioned set must persist across them.
  // Pagination, page-size, date change, refresh, reclassify, push, and
  // initial load are real boundaries and DO reset the session set.
  async function reload(opts) {
    const preserveSession = !!(opts && opts.preserveSession);
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

    // Fix 1.4 follow-up — clear/preserve the in-session actioned set BEFORE
    // we render the new tbody, so renderRow's isActioned check sees the
    // correct state. Order matters: stale Set + new rows would otherwise
    // carry .actioned classes onto rows from a different page/date.
    sessionTotal = lastItems.length;
    if (!preserveSession) {
      sessionActioned = 0;
      sessionActionedIds = new Set();
    }
    updateSessionProgress();

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
        : '<tr><td colspan="10" class="st-loading">No matching suggestions</td></tr>';
    }

    // Stage 8: capture the server-side total so the AI panel context
    // header reads the actual filtered count (not the current page size).
    lastTotal = data.total || 0;

    document.getElementById('stPagerLabel').textContent =
      `Page ${currentPage} · ${lastItems.length} of ${data.total}`;
    document.getElementById('stPrev').disabled = currentPage <= 1;
    document.getElementById('stNext').disabled = lastItems.length < PAGE_SIZE
      || (currentPage * PAGE_SIZE) >= data.total;
    updateButtons();
    // Stage 7 — refresh AI badges/buttons whenever the table data changes
    updateAITriageBadge();
    updateApplyHCButton();
    // Stage 8 — refresh AI panel context header (flow / total / client / date)
    updateAIPanelContext();
    // Stage 9 — re-hydrate chat history when the (flow, date) scope
    // changes. hydrateChatHistory itself is a no-op when flow is null
    // (e.g. "All > All") so calling it on every reload is safe.
    hydrateChatHistory();
  }

  // -------------------- Selection & action buttons -------------------
  function getCheckedRows() {
    const rows = currentTab === 'pass12'
      ? tbody.querySelectorAll('tr[data-id]') : p3body.querySelectorAll('tr[data-id]');
    const ids = [];
    rows.forEach(tr => {
      // Fix 1.4 — actioned rows are visually struck-through and locked;
      // skip them so a stray Select-all click can't re-action them.
      if (tr.classList.contains('actioned')) return;
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

  // -------------------- Fix 1.4: stable session row numbering ---------
  // Fix 1.4 follow-up (Issue 3): single-number label "N actioned this session";
  // hide the chip entirely until the user has actioned at least one row.
  function updateSessionProgress() {
    const a = document.getElementById('stSessionActioned');
    const wrap = document.getElementById('stSessionProgress');
    if (a) a.textContent = sessionActioned;
    if (wrap) wrap.style.display = sessionActioned > 0 ? '' : 'none';
  }
  // Fix 1.4 follow-up (Issue 1): the previous textContent +/- arithmetic was
  // succeeding for Pending but not visibly applying to Approved/Rejected
  // during QA. Rewrote as a single defensive helper that strips any non-digit
  // cruft (whitespace, commas, NBSP), parses, clamps to >=0, and writes back.
  // Same code path for every card so behaviour is symmetric across paths.
  function bumpCard(id, delta) {
    const el = document.getElementById(id);
    if (!el) return;
    const raw = (el.textContent || '').replace(/[^\d-]/g, '');
    const cur = parseInt(raw, 10);
    const next = Math.max(0, (Number.isFinite(cur) ? cur : 0) + delta);
    el.textContent = String(next);
  }
  // Fix 1.4 Issue 1 (real fix): also bump the status filter pill counts
  // so the chip row stays in sync with the top stat cards. Pills are
  // re-rendered on every reload(), but bulkUpdate() deliberately doesn't
  // call reload(), so we mirror the optimistic update here.
  function bumpChip(statusKey, delta) {
    const bar = document.getElementById('stStatusBar');
    if (!bar) return;
    const btn = bar.querySelector(`.st-chip[data-status="${statusKey}"]`);
    if (!btn) return;
    const span = btn.querySelector('.st-chip__count');
    if (!span) return;
    const cur = parseInt((span.textContent || '0').replace(/[^\d-]/g, ''), 10) || 0;
    span.textContent = String(Math.max(0, cur + delta));
  }
  // Mark a single row as actioned in-place: keeps the row in the DOM (and
  // its row number stable), updates the status pill, locks the checkbox,
  // and updates the in-memory item so client-side sort + push-button
  // gating reflect the new state without triggering a reload().
  function markRowActioned(id, newStatus) {
    const root = currentTab === 'pass12' ? tbody : p3body;
    const tr = root.querySelector(`tr[data-id="${id}"]`);
    if (!tr) return false;
    if (tr.classList.contains('actioned')) return false;
    tr.classList.add('actioned');
    tr.dataset.actionedStatus = newStatus;
    sessionActionedIds.add(id);
    // Update the in-memory item too so sort / push counts stay coherent
    const item = lastItems.find(it => it.id === id);
    if (item) item.review_status = newStatus;
    // Replace the status cell pill with the new decided state
    if (currentTab === 'pass12') {
      const cells = tr.children;
      // Status column is index 3 in the Pass 1/2 wide table (col-num=0,
      // checkbox=1, search-term=2, status=3 — see thead in template).
      if (cells[3]) {
        cells[3].innerHTML =
          `<span class="st-status st-status--${newStatus}">${newStatus}</span>`;
      }
    } else {
      // Pass 3 status column is index 7 (col-num=0, chk=1, fragment=2,
      // words=3, role=4, occ=5, risk=6, status=7).
      const cells = tr.children;
      if (cells[7]) {
        cells[7].innerHTML =
          `<span class="st-status st-status--${newStatus}">${newStatus}</span>`;
      }
    }
    // Lock the checkbox so the row can't be re-actioned without reload
    const chk = tr.querySelector('input.st-chk');
    if (chk) { chk.checked = false; chk.disabled = true; }
    // Lock the role dropdown too — role choice is captured at action time
    const roleEl = tr.querySelector('select.st-target-select');
    if (roleEl) roleEl.disabled = true;
    return true;
  }
  function setHideActioned(on) {
    hideActioned = !!on;
    // Apply to both tables so a tab switch keeps the toggle's effect.
    [stTable, stP3Table].forEach(tbl => {
      if (tbl) tbl.classList.toggle('hide-actioned', hideActioned);
    });
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
    //
    // Stage 7.6: backend push endpoint is genuinely global (POSTs
    // {client_id, analysis_date} with no filter pass-through), so the
    // count + handler ARE consistent — the button DOES push exactly
    // what it says. The label gets an "(across all tabs)" caveat when
    // the global count is larger than what's visible in the current
    // filter, so the user understands the scope. Re-aligning to a
    // filtered scope would need a backend change (filter pass-through
    // on POST /v2/api/negatives/push-approved) — Tier 2.2.
    const btn = document.getElementById('stPushApproved');
    btn.disabled = approvedReadyCount === 0;
    const approvedInView = lastItems.filter(i =>
      i.review_status === 'approved' && !i.pushed_to_ads_at).length;
    if (approvedReadyCount === 0) {
      btn.textContent = 'Push approved to Google Ads';
    } else if (approvedInView < approvedReadyCount) {
      // More approved rows exist outside the current filter — be explicit
      btn.textContent =
        `Push ${approvedReadyCount} approved to Google Ads (across all tabs)`;
    } else {
      btn.textContent = `Push ${approvedReadyCount} approved to Google Ads`;
    }
    // Tooltip clarifies scope + remediation
    if (approvedReadyCount > 0 && approvedInView < approvedReadyCount) {
      btn.title =
        `${approvedReadyCount} row(s) approved across all status filters; `
        + `${approvedInView} visible here. Switch to the "Approved" status `
        + `filter to view them all before pushing.`;
    } else if (approvedReadyCount > 0) {
      btn.title =
        `${approvedReadyCount} row(s) approved; pushing will mutate Google Ads.`;
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
          : '<tr><td colspan="20" class="st-loading">No matching rows</td></tr>';
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
      // Fix 1.4 — mark each actioned row in-place so row numbers stay
      // stable for the session. We deliberately do NOT call reload();
      // that's what was renumbering the table mid-triage. Status-card +
      // chip counts go slightly stale until next filter/page change,
      // which is the accepted tradeoff documented in the brief.
      let marked = 0;
      sel.forEach(s => { if (markRowActioned(s.id, status)) marked++; });
      sessionActioned += marked;
      updateSessionProgress();
      // Fix 1.4 Issue 1 — keep the top stat cards AND the status filter
      // pills in sync with the action. Top cards use bumpCard (#cnt* IDs);
      // pills use bumpChip (data-status attribute on chip buttons inside
      // #stStatusBar). The pre-action source pill (typically Review for
      // Pass 1/2 triage) is whichever filter the user has active, except
      // 'all' (all-rows total doesn't change with an action).
      if (currentTab === 'pass12') {
        bumpCard('cntPending', -marked);
        bumpCard(status === 'approved' ? 'cntApproved' : 'cntRejected', +marked);
        const sourceChip = statusView === 'pending' ? 'review' : statusView;
        if (sourceChip && sourceChip !== 'all') bumpChip(sourceChip, -marked);
        bumpChip(status, +marked);
        if (status === 'approved') approvedReadyCount += marked;
      }
      updateButtons();
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
    reload({preserveSession: true});  // Fix 1.4 follow-up Issue 2 — tab switch is a view change, not a data boundary
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
    // Fix 1.4 — Select-all must not pick up actioned rows; their checkbox
    // is already disabled, but we also skip via the .actioned guard so a
    // future un-disabled state still couldn't reactivate them.
    const root = currentTab === 'pass12' ? tbody : p3body;
    root.querySelectorAll('tr[data-id]').forEach(tr => {
      if (tr.classList.contains('actioned')) return;
      const chk = tr.querySelector('input.st-chk');
      if (chk && !chk.disabled) chk.checked = e.target.checked;
    });
    updateButtons();
  });
  // Fix 1.4 — Hide actioned rows toggle. Pure CSS hide; numbering preserved.
  const hideToggle = document.getElementById('stHideActioned');
  if (hideToggle) {
    hideToggle.addEventListener('change', e => setHideActioned(e.target.checked));
  }
  document.addEventListener('change', e => {
    if (e.target.classList && e.target.classList.contains('st-chk')) updateButtons();
  });
  document.getElementById('stBulkApprove').addEventListener('click', () => bulkUpdate('approved'));
  document.getElementById('stBulkReject').addEventListener('click', () => bulkUpdate('rejected'));
  document.getElementById('stPushApproved').addEventListener('click', pushApproved);
  document.getElementById('stRunPass3').addEventListener('click', runPass3);

  // -------------------- Stage 7 — AI button wiring -------------------
  const _btnAITriage = document.getElementById('btnAITriage');
  if (_btnAITriage) _btnAITriage.addEventListener('click', fireAITriage);
  const _btnApplyHC = document.getElementById('btnApplyHighConf');
  if (_btnApplyHC) _btnApplyHC.addEventListener('click', applyHighConf);
  const _btnFilterUnsure = document.getElementById('btnFilterUnsure');
  if (_btnFilterUnsure) _btnFilterUnsure.addEventListener('click', toggleUnsureFilter);

  // -------------------- Stage 8 — AI panel wiring --------------------
  // Restore persisted collapse/expand state on load
  setAIPanelState(getAIPanelState());
  const _btnPanelCollapse = document.getElementById('btnAIPanelCollapse');
  if (_btnPanelCollapse) {
    _btnPanelCollapse.addEventListener('click', () => setAIPanelState('collapsed'));
  }
  const _btnPanelExpand = document.getElementById('btnAIPanelExpand');
  if (_btnPanelExpand) {
    _btnPanelExpand.addEventListener('click', () => setAIPanelState('open'));
  }
  // Initial context-header paint (reload() also calls this on every fetch)
  updateAIPanelContext();

  // Per-row Explain link — event delegation on tbody so it survives
  // re-renders (sort, reload, etc.). Stage 9 redirects the explain
  // output into the chat stream (replacing the Stage 7 transitional
  // modal); the modal HTML/CSS/JS were removed in Stage 9.
  if (tbody) {
    tbody.addEventListener('click', (e) => {
      const link = e.target.closest('.ai-explain-link');
      if (!link || link.hasAttribute('disabled')) return;
      e.preventDefault();
      const id = parseInt(link.dataset.rowId, 10);
      const item = lastItems.find(it => it.id === id);
      explainRowInPanel(id, link.dataset.searchTerm || '', item);
    });
  }

  // -------------------- Stage 9 — chat panel wiring ------------------
  const _btnChatSend = document.getElementById('btnAIChatSend');
  if (_btnChatSend) _btnChatSend.addEventListener('click', sendChatMessage);
  const _btnChatClear = document.getElementById('btnAIChatClear');
  if (_btnChatClear) _btnChatClear.addEventListener('click', clearChat);
  // Enter sends, Shift+Enter inserts newline
  const _chatInput = document.getElementById('aiChatInput');
  if (_chatInput) {
    _chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendChatMessage();
      }
    });
  }
  // Initial hydrate. reload() also re-hydrates on every fetch via the
  // hook in the reload tail (filter / date / tab change).
  hydrateChatHistory();

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
        // Fix 1.4 follow-up (Issue 2): refresh-neg-lists is a real boundary
        // — neg snapshot changed, classifications may differ next reclassify.
        // Trigger a default reload so the in-session actioned set clears.
        await reload();
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
