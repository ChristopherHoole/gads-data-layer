"""Replace the Recommendations tab HTML and JS in shopping_new.html with the new 4-tab table design."""

PATH = 'act_dashboard/templates/shopping_new.html'

NEW_HTML = '''    <!-- RECOMMENDATIONS TAB -->
    <div class="tab-pane fade {% if active_tab == 'recommendations' %}show active{% endif %}"
         id="recommendations-tab" role="tabpanel">

      <!-- Header -->
      <div class="d-flex align-items-start justify-content-between gap-3 mb-4">
        <div>
          <h5 style="font-size:16px;font-weight:600;margin:0 0 4px;color:#1a1d23;">Shopping Recommendations</h5>
          <p style="margin:0;color:#6b7280;font-size:13px;">Rules and flags triggered for shopping products in this account. <a href="/recommendations" style="color:#0d6efd;text-decoration:none;">View full recommendations page &rarr;</a></p>
        </div>
        <div class="d-flex gap-2 flex-wrap">
          <button id="shop-accept-low-risk-btn" class="btn btn-sm btn-outline-success" style="font-size:13px;">Accept all low risk</button>
          <button id="shop-run-engine-btn" class="btn btn-sm btn-outline-secondary" style="font-size:13px;display:flex;align-items:center;gap:5px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 16 16"><path d="M11.596 8.697l-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"/></svg>
            Run Recommendations Now
          </button>
        </div>
      </div>

      <!-- Inner tab nav -->
      <ul class="nav nav-tabs mb-3" id="shopRecTabs" role="tablist">
        <li class="nav-item" role="presentation">
          <button class="nav-link active" id="shop-rec-pending-tab" data-bs-toggle="tab" data-bs-target="#shop-rec-pending" type="button" role="tab">
            Pending <span class="badge bg-secondary ms-1" id="shop-badge-pending">0</span>
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="shop-rec-monitoring-tab" data-bs-toggle="tab" data-bs-target="#shop-rec-monitoring" type="button" role="tab">
            Monitoring <span class="badge bg-secondary ms-1" id="shop-badge-monitoring">0</span>
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="shop-rec-successful-tab" data-bs-toggle="tab" data-bs-target="#shop-rec-successful" type="button" role="tab">
            Successful <span class="badge bg-secondary ms-1" id="shop-badge-successful">0</span>
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="shop-rec-history-tab" data-bs-toggle="tab" data-bs-target="#shop-rec-history" type="button" role="tab">
            History <span class="badge bg-secondary ms-1" id="shop-badge-history">0</span>
          </button>
        </li>
      </ul>

      <div class="tab-content" id="shopRecTabContent">

        <!-- PENDING -->
        <div class="tab-pane fade show active" id="shop-rec-pending" role="tabpanel">
          <div id="shop-bulk-bar" class="rec-bulk-bar" style="display:none;">
            <span id="shop-bulk-count">0 selected</span>
            <button class="btn btn-sm btn-primary" onclick="shopDoBulk('accept')">Accept selected</button>
            <button class="btn btn-sm btn-outline-danger" onclick="shopDoBulk('decline')">Decline selected</button>
            <span class="rec-bulk-clear" onclick="shopClearSelection()">Clear selection</span>
          </div>
          <div class="table-responsive">
            <table class="table table-sm table-hover align-middle rec-tab-slim" id="shop-pending-table">
              <thead class="table-light">
                <tr>
                  <th class="rec-col-cb"><input type="checkbox" id="shop-cb-all-pending" onchange="shopToggleAll(this)"></th>
                  <th class="rec-col-name">Product</th>
                  <th class="rec-col-rule">Rule name</th>
                  <th class="rec-col-plain">Plain English</th>
                  <th class="rec-col-ruleflag">Rule/Flag</th>
                  <th class="rec-col-ruletype">Rule type</th>
                  <th class="rec-col-conditions">Conditions</th>
                  <th class="rec-col-action">Action</th>
                  <th class="rec-col-risk">Risk</th>
                  <th class="rec-col-age">Age</th>
                  <th class="rec-col-acts">Actions</th>
                </tr>
              </thead>
              <tbody id="shop-pending-tbody">
                <tr><td colspan="11" class="text-center text-muted py-4">Loading&hellip;</td></tr>
              </tbody>
            </table>
          </div>
          <div id="shop-pending-paginator" class="d-flex justify-content-between align-items-center mt-2" style="font-size:13px;"></div>
        </div>

        <!-- MONITORING -->
        <div class="tab-pane fade" id="shop-rec-monitoring" role="tabpanel">
          <div class="table-responsive">
            <table class="table table-sm table-hover align-middle rec-tab-slim" id="shop-monitoring-table">
              <thead class="table-light">
                <tr>
                  <th class="rec-col-cb"></th>
                  <th class="rec-col-date">Accepted</th>
                  <th class="rec-col-progress">Monitoring progress</th>
                  <th class="rec-col-name">Product</th>
                  <th class="rec-col-rule">Rule name</th>
                  <th class="rec-col-plain">Plain English</th>
                  <th class="rec-col-ruleflag">Rule/Flag</th>
                  <th class="rec-col-ruletype">Rule type</th>
                  <th class="rec-col-conditions">Conditions</th>
                  <th class="rec-col-action">Action taken</th>
                  <th class="rec-col-risk">Risk</th>
                </tr>
              </thead>
              <tbody id="shop-monitoring-tbody">
                <tr><td colspan="11" class="text-center text-muted py-4">Loading&hellip;</td></tr>
              </tbody>
            </table>
          </div>
          <div id="shop-monitoring-paginator" class="d-flex justify-content-between align-items-center mt-2" style="font-size:13px;"></div>
        </div>

        <!-- SUCCESSFUL -->
        <div class="tab-pane fade" id="shop-rec-successful" role="tabpanel">
          <div class="table-responsive">
            <table class="table table-sm table-hover align-middle rec-tab-slim" id="shop-successful-table">
              <thead class="table-light">
                <tr>
                  <th class="rec-col-cb"></th>
                  <th class="rec-col-date">Accepted</th>
                  <th class="rec-col-date">Completed</th>
                  <th class="rec-col-name">Product</th>
                  <th class="rec-col-rule">Rule name</th>
                  <th class="rec-col-plain">Plain English</th>
                  <th class="rec-col-ruleflag">Rule/Flag</th>
                  <th class="rec-col-ruletype">Rule type</th>
                  <th class="rec-col-conditions">Conditions</th>
                  <th class="rec-col-action">Action taken</th>
                  <th class="rec-col-risk">Risk</th>
                </tr>
              </thead>
              <tbody id="shop-successful-tbody">
                <tr><td colspan="11" class="text-center text-muted py-4">Loading&hellip;</td></tr>
              </tbody>
            </table>
          </div>
          <div id="shop-successful-paginator" class="d-flex justify-content-between align-items-center mt-2" style="font-size:13px;"></div>
        </div>

        <!-- HISTORY (declined + reverted) -->
        <div class="tab-pane fade" id="shop-rec-history" role="tabpanel">
          <div class="table-responsive">
            <table class="table table-sm table-hover align-middle rec-tab-slim" id="shop-history-table">
              <thead class="table-light">
                <tr>
                  <th class="rec-col-cb"></th>
                  <th class="rec-col-status">Outcome</th>
                  <th class="rec-col-date">Date actioned</th>
                  <th class="rec-col-name">Product</th>
                  <th class="rec-col-rule">Rule name</th>
                  <th class="rec-col-plain">Plain English</th>
                  <th class="rec-col-ruleflag">Rule/Flag</th>
                  <th class="rec-col-ruletype">Rule type</th>
                  <th class="rec-col-conditions">Conditions</th>
                  <th class="rec-col-action">Action</th>
                  <th class="rec-col-risk">Risk</th>
                </tr>
              </thead>
              <tbody id="shop-history-tbody">
                <tr><td colspan="11" class="text-center text-muted py-4">Loading&hellip;</td></tr>
              </tbody>
            </table>
          </div>
          <div id="shop-history-paginator" class="d-flex justify-content-between align-items-center mt-2" style="font-size:13px;"></div>
        </div>

      </div><!-- /shopRecTabContent -->

    </div>'''

NEW_JS = '''// ===========================================================================
// RECOMMENDATIONS TAB - TABLE UI (Chat 96)
// ===========================================================================
(function () {
  'use strict';

  // ── Helpers ───────────────────────────────────────────────────────────────
  function esc(s) {
    if (s == null) return '';
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }
  function rfBadge(v) {
    if (!v) return '<span class="rec-badge-flag">Flag</span>';
    var lv = v.toLowerCase();
    if (lv === 'rule') return '<span class="rec-badge-rule">Rule</span>';
    return '<span class="rec-badge-flag">Flag</span>';
  }
  function rtBadge(v) {
    var m = { budget:'Budget', bid:'Bid', status:'Status', keyword:'Keyword', shopping:'Shopping' };
    return '<span class="rec-badge-type">' + esc(m[v] || v || 'Other') + '</span>';
  }
  function condCell(v) {
    if (!v) return '<span class="text-muted">\u2014</span>';
    return '<span class="rec-cond-cell" title="' + esc(v) + '">' + esc(v.length > 60 ? v.slice(0,58)+'\u2026' : v) + '</span>';
  }
  function actionCell(v) {
    if (!v) return '<span class="text-muted">\u2014</span>';
    return '<span class="rec-action-pill">' + esc(v) + '</span>';
  }
  function riskBadge(r) {
    var cls = { low:'rec-risk-low', medium:'rec-risk-med', high:'rec-risk-high' };
    return '<span class="' + (cls[r] || 'rec-risk-low') + '">' + esc(r||'low') + '</span>';
  }
  function outcomeBadge(s) {
    var cls = { declined:'rec-outcome-declined', reverted:'rec-outcome-reverted' };
    return '<span class="' + (cls[s] || 'rec-outcome-declined') + '">' + esc(s) + '</span>';
  }
  function fmtDate(d) {
    if (!d) return '\u2014';
    return new Date(d).toLocaleDateString('en-GB', { day:'2-digit', month:'short', year:'numeric' });
  }
  function ageLabel(d) {
    if (!d) return '\u2014';
    var days = Math.round((Date.now() - new Date(d)) / 86400000);
    return days < 1 ? 'Today' : days + 'd';
  }
  function progressBar(r) {
    var pct = Math.min(100, Math.max(0, r.monitoring_progress_pct || 0));
    return '<div class="rec-progress-wrap"><div class="rec-progress-bar" style="width:' + pct + '%"></div></div><span style="font-size:11px;color:#6b7280;">' + pct + '%</span>';
  }
  function makeExpRow(r, cols) {
    var plain = r.plain_english || r.action_description || '';
    var cond  = r.conditions || '';
    return '<tr class="rec-exp-row"><td colspan="' + cols + '" class="rec-exp-cell">'
      + (plain ? '<div><strong>Plain English:</strong> ' + esc(plain) + '</div>' : '')
      + (cond  ? '<div><strong>Conditions:</strong> ' + esc(cond) + '</div>' : '')
      + '<div><strong>Rec ID:</strong> ' + esc(r.rec_id) + '</div>'
      + '</td></tr>';
  }

  // ── State ─────────────────────────────────────────────────────────────────
  var SHOP_REC = { pending:[], monitoring:[], successful:[], history:[] };
  var SHOP_SEL = {};
  var SHOP_PAGE = { pending:1, monitoring:1, successful:1, history:1 };
  var SHOP_PER_PAGE = 25;

  // ── Row builders ──────────────────────────────────────────────────────────
  function pendingRow(r) {
    var id = r.rec_id;
    var chk = '<input type="checkbox" class="shop-rec-cb" data-id="' + id + '" onchange="shopRecCbChange(this)" ' + (SHOP_SEL[id] ? 'checked' : '') + '>';
    return '<tr data-id="' + id + '">'
      + '<td>' + chk + '</td>'
      + '<td class="rec-col-name">' + esc(r.entity_name || r.campaign_name || '\u2014') + '</td>'
      + '<td>' + esc(r.rule_name || r.rule_id || '\u2014') + '</td>'
      + '<td>' + condCell(r.plain_english || r.action_description) + '</td>'
      + '<td>' + rfBadge(r.rule_or_flag) + '</td>'
      + '<td>' + rtBadge(r.rule_type_display || r.rule_type) + '</td>'
      + '<td>' + condCell(r.conditions) + '</td>'
      + '<td>' + actionCell(r.action_description) + '</td>'
      + '<td>' + riskBadge(r.risk_level) + '</td>'
      + '<td>' + ageLabel(r.created_at) + '</td>'
      + '<td style="white-space:nowrap;">'
        + '<button class="btn btn-xs btn-link p-0 me-1" onclick="shopRecExp(' + id + ', this)" title="Expand">&#x25BC;</button>'
        + '<button class="btn btn-xs btn-success py-0 px-1 me-1" style="font-size:11px;" onclick="shopRecAccept(' + id + ', this)">Accept</button>'
        + '<button class="btn btn-xs btn-outline-danger py-0 px-1" style="font-size:11px;" onclick="shopRecDecline(' + id + ', this)">Decline</button>'
      + '</td>'
      + '</tr>';
  }
  function monitoringRow(r) {
    return '<tr>'
      + '<td></td>'
      + '<td>' + fmtDate(r.accepted_at) + '</td>'
      + '<td>' + progressBar(r) + '</td>'
      + '<td class="rec-col-name">' + esc(r.entity_name || r.campaign_name || '\u2014') + '</td>'
      + '<td>' + esc(r.rule_name || r.rule_id || '\u2014') + '</td>'
      + '<td>' + condCell(r.plain_english || r.action_description) + '</td>'
      + '<td>' + rfBadge(r.rule_or_flag) + '</td>'
      + '<td>' + rtBadge(r.rule_type_display || r.rule_type) + '</td>'
      + '<td>' + condCell(r.conditions) + '</td>'
      + '<td>' + actionCell(r.action_description) + '</td>'
      + '<td>' + riskBadge(r.risk_level) + '</td>'
      + '</tr>';
  }
  function successfulRow(r) {
    return '<tr>'
      + '<td></td>'
      + '<td>' + fmtDate(r.accepted_at) + '</td>'
      + '<td>' + fmtDate(r.completed_at) + '</td>'
      + '<td class="rec-col-name">' + esc(r.entity_name || r.campaign_name || '\u2014') + '</td>'
      + '<td>' + esc(r.rule_name || r.rule_id || '\u2014') + '</td>'
      + '<td>' + condCell(r.plain_english || r.action_description) + '</td>'
      + '<td>' + rfBadge(r.rule_or_flag) + '</td>'
      + '<td>' + rtBadge(r.rule_type_display || r.rule_type) + '</td>'
      + '<td>' + condCell(r.conditions) + '</td>'
      + '<td>' + actionCell(r.action_description) + '</td>'
      + '<td>' + riskBadge(r.risk_level) + '</td>'
      + '</tr>';
  }
  function historyRow(r) {
    var dt = r.declined_at || r.reverted_at || r.completed_at;
    return '<tr>'
      + '<td></td>'
      + '<td>' + outcomeBadge(r.status) + '</td>'
      + '<td>' + fmtDate(dt) + '</td>'
      + '<td class="rec-col-name">' + esc(r.entity_name || r.campaign_name || '\u2014') + '</td>'
      + '<td>' + esc(r.rule_name || r.rule_id || '\u2014') + '</td>'
      + '<td>' + condCell(r.plain_english || r.action_description) + '</td>'
      + '<td>' + rfBadge(r.rule_or_flag) + '</td>'
      + '<td>' + rtBadge(r.rule_type_display || r.rule_type) + '</td>'
      + '<td>' + condCell(r.conditions) + '</td>'
      + '<td>' + actionCell(r.action_description) + '</td>'
      + '<td>' + riskBadge(r.risk_level) + '</td>'
      + '</tr>';
  }

  // ── Render ────────────────────────────────────────────────────────────────
  function renderTab(tab, rowFn, cols) {
    var rows = SHOP_REC[tab];
    var pg   = SHOP_PAGE[tab];
    var start = (pg - 1) * SHOP_PER_PAGE;
    var slice = rows.slice(start, start + SHOP_PER_PAGE);
    var tbody = document.getElementById('shop-' + tab + '-tbody');
    if (!tbody) return;
    if (!rows.length) {
      tbody.innerHTML = '<tr><td colspan="' + cols + '" class="text-center text-muted py-4">No ' + tab + ' recommendations</td></tr>';
    } else {
      tbody.innerHTML = slice.map(rowFn).join('');
    }
    buildPag(tab, rows.length, pg, cols);
    var badge = document.getElementById('shop-badge-' + tab);
    if (badge) badge.textContent = rows.length;
  }
  function buildPag(tab, total, pg, cols) {
    var el = document.getElementById('shop-' + tab + '-paginator');
    if (!el) return;
    var pages = Math.ceil(total / SHOP_PER_PAGE);
    if (pages <= 1) { el.innerHTML = ''; return; }
    var btns = '';
    for (var i = 1; i <= pages; i++) {
      btns += '<button class="btn btn-xs ' + (i === pg ? 'btn-primary' : 'btn-outline-secondary') + ' py-0 px-2" style="font-size:11px;" onclick="shopRecRenderAll(\'' + tab + '\',' + i + ')">' + i + '</button> ';
    }
    el.innerHTML = '<span style="color:#6b7280;">Page ' + pg + ' of ' + pages + '</span><div class="d-flex gap-1">' + btns + '</div>';
  }
  function shopRecRenderAll(jumpTab, jumpPage) {
    if (jumpTab && jumpPage) SHOP_PAGE[jumpTab] = jumpPage;
    renderTab('pending',    pendingRow,    11);
    renderTab('monitoring', monitoringRow, 11);
    renderTab('successful', successfulRow, 11);
    renderTab('history',    historyRow,    11);
    var tot = SHOP_REC.pending.length + SHOP_REC.monitoring.length + SHOP_REC.successful.length + SHOP_REC.history.length;
    var outerBadge = document.getElementById('shop-total-count');
    if (outerBadge) outerBadge.textContent = tot;
  }

  // ── Toast ─────────────────────────────────────────────────────────────────
  function shopShowToast(msg, type) {
    var wrap = document.getElementById('act-toast-wrap');
    if (!wrap) {
      wrap = document.createElement('div');
      wrap.id = 'act-toast-wrap';
      document.body.appendChild(wrap);
    }
    var t = document.createElement('div');
    t.className = 'act-toast t-' + (type || 'success');
    t.textContent = msg;
    wrap.appendChild(t);
    setTimeout(function () { t.style.opacity = '0'; setTimeout(function () { t.remove(); }, 300); }, 3000);
  }

  // ── Load data ─────────────────────────────────────────────────────────────
  function shopRecLoad() {
    fetch('/recommendations/cards')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        SHOP_REC.pending    = (data.pending    || []).filter(function (r) { return r.entity_type === 'shopping_product'; });
        SHOP_REC.monitoring = (data.monitoring || []).filter(function (r) { return r.entity_type === 'shopping_product'; });
        SHOP_REC.successful = (data.successful || []).filter(function (r) { return r.entity_type === 'shopping_product'; });
        var hist = (data.declined || []).concat(data.reverted || []).filter(function (r) { return r.entity_type === 'shopping_product'; });
        hist.sort(function (a, b) {
          var da = a.declined_at || a.reverted_at || ''; var db = b.declined_at || b.reverted_at || '';
          return da < db ? 1 : da > db ? -1 : 0;
        });
        SHOP_REC.history = hist;
        shopRecRenderAll();
      })
      .catch(function (e) { console.error('shopRecLoad error', e); });
  }
  window.shopRecLoad = shopRecLoad;

  // ── Expand row ────────────────────────────────────────────────────────────
  window.shopRecExp = function (id, btn) {
    var tr = btn.closest('tr');
    var next = tr.nextElementSibling;
    if (next && next.classList.contains('rec-exp-row')) {
      next.remove(); btn.innerHTML = '&#x25BC;'; return;
    }
    btn.innerHTML = '&#x25B2;';
    var r = SHOP_REC.pending.find(function (x) { return x.rec_id === id; });
    if (!r) return;
    var exp = document.createElement('tbody');
    exp.innerHTML = makeExpRow(r, 11);
    tr.parentNode.insertBefore(exp.firstElementChild, tr.nextSibling);
  };

  // ── Checkbox selection ────────────────────────────────────────────────────
  window.shopRecCbChange = function (cb) {
    var id = parseInt(cb.dataset.id);
    if (cb.checked) SHOP_SEL[id] = true; else delete SHOP_SEL[id];
    updateBulkBar();
  };
  window.shopToggleAll = function (cb) {
    document.querySelectorAll('.shop-rec-cb').forEach(function (c) {
      c.checked = cb.checked;
      var id = parseInt(c.dataset.id);
      if (cb.checked) SHOP_SEL[id] = true; else delete SHOP_SEL[id];
    });
    updateBulkBar();
  };
  window.shopClearSelection = function () {
    SHOP_SEL = {};
    document.querySelectorAll('.shop-rec-cb').forEach(function (c) { c.checked = false; });
    var allCb = document.getElementById('shop-cb-all-pending');
    if (allCb) allCb.checked = false;
    updateBulkBar();
  };
  function updateBulkBar() {
    var n = Object.keys(SHOP_SEL).length;
    var bar = document.getElementById('shop-bulk-bar');
    var cnt = document.getElementById('shop-bulk-count');
    if (bar) bar.style.display = n ? '' : 'none';
    if (cnt) cnt.textContent = n + ' selected';
  }

  // ── Accept / Decline ──────────────────────────────────────────────────────
  window.shopRecAccept = function (id, btn) {
    btn.disabled = true; btn.textContent = '\u2026';
    fetch('/recommendations/' + id + '/accept', { method: 'POST', headers: { 'Content-Type': 'application/json' } })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.success) {
          var r = SHOP_REC.pending.find(function (x) { return x.rec_id === id; });
          SHOP_REC.pending = SHOP_REC.pending.filter(function (x) { return x.rec_id !== id; });
          if (r) { r.status = 'monitoring'; r.accepted_at = new Date().toISOString(); SHOP_REC.monitoring.push(r); }
          delete SHOP_SEL[id]; updateBulkBar(); shopRecRenderAll();
          shopShowToast(d.message || 'Accepted', 'success');
        } else { shopShowToast(d.message || 'Failed', 'error'); btn.disabled = false; btn.textContent = 'Accept'; }
      })
      .catch(function () { shopShowToast('Request failed', 'error'); btn.disabled = false; btn.textContent = 'Accept'; });
  };
  window.shopRecDecline = function (id, btn) {
    btn.disabled = true; btn.textContent = '\u2026';
    fetch('/recommendations/' + id + '/decline', { method: 'POST', headers: { 'Content-Type': 'application/json' } })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.success) {
          var r = SHOP_REC.pending.find(function (x) { return x.rec_id === id; });
          SHOP_REC.pending = SHOP_REC.pending.filter(function (x) { return x.rec_id !== id; });
          if (r) { r.status = 'declined'; r.declined_at = new Date().toISOString(); SHOP_REC.history.unshift(r); }
          delete SHOP_SEL[id]; updateBulkBar(); shopRecRenderAll();
          shopShowToast(d.message || 'Declined', 'muted');
        } else { shopShowToast(d.message || 'Failed', 'error'); btn.disabled = false; btn.textContent = 'Decline'; }
      })
      .catch(function () { shopShowToast('Request failed', 'error'); btn.disabled = false; btn.textContent = 'Decline'; });
  };
  window.shopDoBulk = function (action) {
    var ids = Object.keys(SHOP_SEL).map(Number);
    if (!ids.length) return;
    ids.forEach(function (id) {
      var btn = document.querySelector('[data-id="' + id + '"]');
      if (action === 'accept') window.shopRecAccept(id, btn || document.createElement('button'));
      else window.shopRecDecline(id, btn || document.createElement('button'));
    });
  };

  // ── DOMContentLoaded ──────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    var runBtn = document.getElementById('shop-run-engine-btn');
    if (runBtn) {
      runBtn.addEventListener('click', function () {
        var btn = this; var orig = btn.innerHTML;
        btn.disabled = true; btn.innerHTML = 'Running\u2026';
        fetch('/recommendations/run', { method: 'POST' })
          .then(function (r) { return r.json(); })
          .then(function (d) {
            btn.disabled = false; btn.innerHTML = orig;
            shopShowToast(d.success ? (d.message || 'Engine complete.') : ('Error: ' + (d.message || 'unknown')), d.success ? 'success' : 'error');
            if (d.success) shopRecLoad();
          })
          .catch(function () { btn.disabled = false; btn.innerHTML = orig; shopShowToast('Request failed.', 'error'); });
      });
    }
    var lowRiskBtn = document.getElementById('shop-accept-low-risk-btn');
    if (lowRiskBtn) {
      lowRiskBtn.addEventListener('click', function () {
        SHOP_REC.pending.filter(function (r) { return (r.risk_level || 'low') === 'low'; }).forEach(function (r) {
          var btn = document.createElement('button');
          window.shopRecAccept(r.rec_id, btn);
        });
      });
      var tabBtns = document.querySelectorAll('#shopRecTabs button[data-bs-toggle="tab"]');
      tabBtns.forEach(function (btn) {
        btn.addEventListener('shown.bs.tab', function (e) {
          if (lowRiskBtn) lowRiskBtn.style.display = e.target.id === 'shop-rec-pending-tab' ? '' : 'none';
        });
      });
    }
    // Trigger load when outer recommendations tab is shown
    var recTabBtn = document.getElementById('tab-btn-recommendations');
    if (recTabBtn) recTabBtn.addEventListener('shown.bs.tab', function () { shopRecLoad(); });
    // Also load if page opened directly on recommendations tab
    var recPane = document.getElementById('recommendations-tab');
    if (recPane && recPane.classList.contains('active')) { shopRecLoad(); }
  });

})();
</script>

{% endblock %}'''

with open(PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace HTML block
HTML_START = "    <!-- RECOMMENDATIONS TAB -->\n    <div class=\"tab-pane fade {% if active_tab == 'recommendations' %}show active{% endif %}\"\n         id=\"recommendations-tab\" role=\"tabpanel\">"
HTML_END   = "\n\n    </div>\n\n  </div>\n  <!-- End Tab Content -->"

idx_start = content.find(HTML_START)
if idx_start == -1:
    print('ERROR: HTML start marker not found')
    exit(1)

idx_end = content.find(HTML_END, idx_start)
if idx_end == -1:
    print('ERROR: HTML end marker not found')
    exit(1)

old_html = content[idx_start : idx_end]
print(f'HTML block: {len(old_html)} chars')
content = content[:idx_start] + NEW_HTML + content[idx_end:]

# 2. Replace JS block
JS_START = '// ===========================================================================\n// RECOMMENDATIONS TAB - STATUS TAB SWITCHING\n// ===========================================================================\n'
# End: everything through </script>\n\n{% endblock %}
JS_END = '</script>\n\n{% endblock %}'

idx_js_start = content.find(JS_START)
if idx_js_start == -1:
    print('ERROR: JS start marker not found')
    exit(1)

idx_js_end = content.find(JS_END, idx_js_start)
if idx_js_end == -1:
    print('ERROR: JS end marker not found')
    exit(1)

old_js = content[idx_js_start : idx_js_end + len(JS_END)]
print(f'JS block: {len(old_js)} chars')
content = content[:idx_js_start] + NEW_JS + '\n'

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print('Done. shopping_new.html updated.')
