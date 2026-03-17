"""Replace the Recommendations tab HTML and JS in ads_new.html with the new 4-tab table design."""

import re

PATH = 'act_dashboard/templates/ads_new.html'

NEW_HTML = '''    <!-- RECOMMENDATIONS TAB -->
    <div class="tab-pane fade" id="recommendations-tab" role="tabpanel">

      <!-- Header -->
      <div class="d-flex align-items-start justify-content-between gap-3 mb-4">
        <div>
          <h5 style="font-size:16px;font-weight:600;margin:0 0 4px;color:#1a1d23;">Ad Recommendations</h5>
          <p style="margin:0;color:#6b7280;font-size:13px;">Rules and flags triggered for ads in this account. <a href="/recommendations" style="color:#0d6efd;text-decoration:none;">View full recommendations page &rarr;</a></p>
        </div>
        <div class="d-flex gap-2 flex-wrap">
          <button id="ad-accept-low-risk-btn" class="btn btn-sm btn-outline-success" style="font-size:13px;">Accept all low risk</button>
          <button id="ad-run-engine-btn" class="btn btn-sm btn-outline-secondary" style="font-size:13px;display:flex;align-items:center;gap:5px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 16 16"><path d="M11.596 8.697l-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"/></svg>
            Run Recommendations Now
          </button>
        </div>
      </div>

      <!-- Inner tab nav -->
      <ul class="nav nav-tabs mb-3" id="adRecTabs" role="tablist">
        <li class="nav-item" role="presentation">
          <button class="nav-link active" id="ad-rec-pending-tab" data-bs-toggle="tab" data-bs-target="#ad-rec-pending" type="button" role="tab">
            Pending <span class="badge bg-secondary ms-1" id="ad-badge-pending">0</span>
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="ad-rec-monitoring-tab" data-bs-toggle="tab" data-bs-target="#ad-rec-monitoring" type="button" role="tab">
            Monitoring <span class="badge bg-secondary ms-1" id="ad-badge-monitoring">0</span>
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="ad-rec-successful-tab" data-bs-toggle="tab" data-bs-target="#ad-rec-successful" type="button" role="tab">
            Successful <span class="badge bg-secondary ms-1" id="ad-badge-successful">0</span>
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="ad-rec-history-tab" data-bs-toggle="tab" data-bs-target="#ad-rec-history" type="button" role="tab">
            History <span class="badge bg-secondary ms-1" id="ad-badge-history">0</span>
          </button>
        </li>
      </ul>

      <div class="tab-content" id="adRecTabContent">

        <!-- PENDING -->
        <div class="tab-pane fade show active" id="ad-rec-pending" role="tabpanel">
          <div id="ad-bulk-bar" class="rec-bulk-bar" style="display:none;">
            <span id="ad-bulk-count">0 selected</span>
            <button class="btn btn-sm btn-primary" onclick="adDoBulk('accept')">Accept selected</button>
            <button class="btn btn-sm btn-outline-danger" onclick="adDoBulk('decline')">Decline selected</button>
            <span class="rec-bulk-clear" onclick="adClearSelection()">Clear selection</span>
          </div>
          <div class="table-responsive">
            <table class="table table-sm table-hover align-middle rec-tab-slim" id="ad-pending-table">
              <thead class="table-light">
                <tr>
                  <th class="rec-col-cb"><input type="checkbox" id="ad-cb-all-pending" onchange="adToggleAll(this)"></th>
                  <th class="rec-col-name">Ad</th>
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
              <tbody id="ad-pending-tbody">
                <tr><td colspan="11" class="text-center text-muted py-4">Loading&hellip;</td></tr>
              </tbody>
            </table>
          </div>
          <div id="ad-pending-paginator" class="d-flex justify-content-between align-items-center mt-2" style="font-size:13px;"></div>
        </div>

        <!-- MONITORING -->
        <div class="tab-pane fade" id="ad-rec-monitoring" role="tabpanel">
          <div class="table-responsive">
            <table class="table table-sm table-hover align-middle rec-tab-slim" id="ad-monitoring-table">
              <thead class="table-light">
                <tr>
                  <th class="rec-col-cb"></th>
                  <th class="rec-col-date">Accepted</th>
                  <th class="rec-col-progress">Monitoring progress</th>
                  <th class="rec-col-name">Ad</th>
                  <th class="rec-col-rule">Rule name</th>
                  <th class="rec-col-plain">Plain English</th>
                  <th class="rec-col-ruleflag">Rule/Flag</th>
                  <th class="rec-col-ruletype">Rule type</th>
                  <th class="rec-col-conditions">Conditions</th>
                  <th class="rec-col-action">Action taken</th>
                  <th class="rec-col-risk">Risk</th>
                </tr>
              </thead>
              <tbody id="ad-monitoring-tbody">
                <tr><td colspan="11" class="text-center text-muted py-4">Loading&hellip;</td></tr>
              </tbody>
            </table>
          </div>
          <div id="ad-monitoring-paginator" class="d-flex justify-content-between align-items-center mt-2" style="font-size:13px;"></div>
        </div>

        <!-- SUCCESSFUL -->
        <div class="tab-pane fade" id="ad-rec-successful" role="tabpanel">
          <div class="table-responsive">
            <table class="table table-sm table-hover align-middle rec-tab-slim" id="ad-successful-table">
              <thead class="table-light">
                <tr>
                  <th class="rec-col-cb"></th>
                  <th class="rec-col-date">Accepted</th>
                  <th class="rec-col-date">Completed</th>
                  <th class="rec-col-name">Ad</th>
                  <th class="rec-col-rule">Rule name</th>
                  <th class="rec-col-plain">Plain English</th>
                  <th class="rec-col-ruleflag">Rule/Flag</th>
                  <th class="rec-col-ruletype">Rule type</th>
                  <th class="rec-col-conditions">Conditions</th>
                  <th class="rec-col-action">Action taken</th>
                  <th class="rec-col-risk">Risk</th>
                </tr>
              </thead>
              <tbody id="ad-successful-tbody">
                <tr><td colspan="11" class="text-center text-muted py-4">Loading&hellip;</td></tr>
              </tbody>
            </table>
          </div>
          <div id="ad-successful-paginator" class="d-flex justify-content-between align-items-center mt-2" style="font-size:13px;"></div>
        </div>

        <!-- HISTORY (declined + reverted) -->
        <div class="tab-pane fade" id="ad-rec-history" role="tabpanel">
          <div class="table-responsive">
            <table class="table table-sm table-hover align-middle rec-tab-slim" id="ad-history-table">
              <thead class="table-light">
                <tr>
                  <th class="rec-col-cb"></th>
                  <th class="rec-col-status">Outcome</th>
                  <th class="rec-col-date">Date actioned</th>
                  <th class="rec-col-name">Ad</th>
                  <th class="rec-col-rule">Rule name</th>
                  <th class="rec-col-plain">Plain English</th>
                  <th class="rec-col-ruleflag">Rule/Flag</th>
                  <th class="rec-col-ruletype">Rule type</th>
                  <th class="rec-col-conditions">Conditions</th>
                  <th class="rec-col-action">Action</th>
                  <th class="rec-col-risk">Risk</th>
                </tr>
              </thead>
              <tbody id="ad-history-tbody">
                <tr><td colspan="11" class="text-center text-muted py-4">Loading&hellip;</td></tr>
              </tbody>
            </table>
          </div>
          <div id="ad-history-paginator" class="d-flex justify-content-between align-items-center mt-2" style="font-size:13px;"></div>
        </div>

      </div><!-- /adRecTabContent -->

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
    if (!v) return '<span class="text-muted">—</span>';
    return '<span class="rec-cond-cell" title="' + esc(v) + '">' + esc(v.length > 60 ? v.slice(0,58)+'…' : v) + '</span>';
  }
  function actionCell(v) {
    if (!v) return '<span class="text-muted">—</span>';
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
    if (!d) return '—';
    return new Date(d).toLocaleDateString('en-GB', { day:'2-digit', month:'short', year:'numeric' });
  }
  function ageLabel(d) {
    if (!d) return '—';
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
  var AD_REC = { pending:[], monitoring:[], successful:[], history:[] };
  var AD_SEL = {};
  var AD_PAGE = { pending:1, monitoring:1, successful:1, history:1 };
  var AD_PER_PAGE = 25;

  // ── Row builders ──────────────────────────────────────────────────────────
  function pendingRow(r) {
    var id = r.rec_id;
    var chk = '<input type="checkbox" class="ad-rec-cb" data-id="' + id + '" onchange="adRecCbChange(this)" ' + (AD_SEL[id] ? 'checked' : '') + '>';
    return '<tr data-id="' + id + '">'
      + '<td>' + chk + '</td>'
      + '<td class="rec-col-name">' + esc(r.entity_name || r.campaign_name || '—') + '</td>'
      + '<td>' + esc(r.rule_name || r.rule_id || '—') + '</td>'
      + '<td>' + condCell(r.plain_english || r.action_description) + '</td>'
      + '<td>' + rfBadge(r.rule_or_flag) + '</td>'
      + '<td>' + rtBadge(r.rule_type_display || r.rule_type) + '</td>'
      + '<td>' + condCell(r.conditions) + '</td>'
      + '<td>' + actionCell(r.action_description) + '</td>'
      + '<td>' + riskBadge(r.risk_level) + '</td>'
      + '<td>' + ageLabel(r.created_at) + '</td>'
      + '<td style="white-space:nowrap;">'
        + '<button class="btn btn-xs btn-link p-0 me-1" onclick="adRecExp(' + id + ', this)" title="Expand">&#x25BC;</button>'
        + '<button class="btn btn-xs btn-success py-0 px-1 me-1" style="font-size:11px;" onclick="adRecAccept(' + id + ', this)">Accept</button>'
        + '<button class="btn btn-xs btn-outline-danger py-0 px-1" style="font-size:11px;" onclick="adRecDecline(' + id + ', this)">Decline</button>'
      + '</td>'
      + '</tr>';
  }
  function monitoringRow(r) {
    return '<tr>'
      + '<td></td>'
      + '<td>' + fmtDate(r.accepted_at) + '</td>'
      + '<td>' + progressBar(r) + '</td>'
      + '<td class="rec-col-name">' + esc(r.entity_name || r.campaign_name || '—') + '</td>'
      + '<td>' + esc(r.rule_name || r.rule_id || '—') + '</td>'
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
      + '<td class="rec-col-name">' + esc(r.entity_name || r.campaign_name || '—') + '</td>'
      + '<td>' + esc(r.rule_name || r.rule_id || '—') + '</td>'
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
      + '<td class="rec-col-name">' + esc(r.entity_name || r.campaign_name || '—') + '</td>'
      + '<td>' + esc(r.rule_name || r.rule_id || '—') + '</td>'
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
    var rows = AD_REC[tab];
    var pg   = AD_PAGE[tab];
    var start = (pg - 1) * AD_PER_PAGE;
    var slice = rows.slice(start, start + AD_PER_PAGE);
    var tbody = document.getElementById('ad-' + tab + '-tbody');
    if (!tbody) return;
    if (!rows.length) {
      tbody.innerHTML = '<tr><td colspan="' + cols + '" class="text-center text-muted py-4">No ' + tab + ' recommendations</td></tr>';
    } else {
      tbody.innerHTML = slice.map(rowFn).join('');
    }
    buildPag(tab, rows.length, pg, cols);
    // update badge
    var badge = document.getElementById('ad-badge-' + tab);
    if (badge) badge.textContent = rows.length;
  }
  function buildPag(tab, total, pg, cols) {
    var el = document.getElementById('ad-' + tab + '-paginator');
    if (!el) return;
    var pages = Math.ceil(total / AD_PER_PAGE);
    if (pages <= 1) { el.innerHTML = ''; return; }
    var btns = '';
    for (var i = 1; i <= pages; i++) {
      btns += '<button class="btn btn-xs ' + (i === pg ? 'btn-primary' : 'btn-outline-secondary') + ' py-0 px-2" style="font-size:11px;" onclick="adRecRenderAll(\'' + tab + '\',' + i + ')">' + i + '</button> ';
    }
    el.innerHTML = '<span style="color:#6b7280;">Page ' + pg + ' of ' + pages + '</span><div class="d-flex gap-1">' + btns + '</div>';
  }
  function adRecRenderAll(jumpTab, jumpPage) {
    if (jumpTab && jumpPage) AD_PAGE[jumpTab] = jumpPage;
    renderTab('pending',    pendingRow,    11);
    renderTab('monitoring', monitoringRow, 11);
    renderTab('successful', successfulRow, 11);
    renderTab('history',    historyRow,    11);
    // update total badge in outer nav
    var tot = AD_REC.pending.length + AD_REC.monitoring.length + AD_REC.successful.length + AD_REC.history.length;
    var outerBadge = document.getElementById('ad-total-count');
    if (outerBadge) outerBadge.textContent = tot;
  }

  // ── Toast ─────────────────────────────────────────────────────────────────
  function adShowToast(msg, type) {
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
  function adRecLoad() {
    fetch('/recommendations/cards')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        AD_REC.pending    = (data.pending    || []).filter(function (r) { return r.entity_type === 'ad'; });
        AD_REC.monitoring = (data.monitoring || []).filter(function (r) { return r.entity_type === 'ad'; });
        AD_REC.successful = (data.successful || []).filter(function (r) { return r.entity_type === 'ad'; });
        var hist = (data.declined || []).concat(data.reverted || []).filter(function (r) { return r.entity_type === 'ad'; });
        hist.sort(function (a, b) {
          var da = a.declined_at || a.reverted_at || ''; var db = b.declined_at || b.reverted_at || '';
          return da < db ? 1 : da > db ? -1 : 0;
        });
        AD_REC.history = hist;
        adRecRenderAll();
      })
      .catch(function (e) { console.error('adRecLoad error', e); });
  }
  window.adRecLoad = adRecLoad;

  // ── Expand row ────────────────────────────────────────────────────────────
  window.adRecExp = function (id, btn) {
    var tr = btn.closest('tr');
    var next = tr.nextElementSibling;
    if (next && next.classList.contains('rec-exp-row')) {
      next.remove(); btn.innerHTML = '&#x25BC;'; return;
    }
    btn.innerHTML = '&#x25B2;';
    var r = AD_REC.pending.find(function (x) { return x.rec_id === id; });
    if (!r) return;
    var exp = document.createElement('tbody');
    exp.innerHTML = makeExpRow(r, 11);
    tr.parentNode.insertBefore(exp.firstElementChild, tr.nextSibling);
  };

  // ── Checkbox selection ────────────────────────────────────────────────────
  window.adRecCbChange = function (cb) {
    var id = parseInt(cb.dataset.id);
    if (cb.checked) AD_SEL[id] = true; else delete AD_SEL[id];
    updateBulkBar();
  };
  window.adToggleAll = function (cb) {
    document.querySelectorAll('.ad-rec-cb').forEach(function (c) {
      c.checked = cb.checked;
      var id = parseInt(c.dataset.id);
      if (cb.checked) AD_SEL[id] = true; else delete AD_SEL[id];
    });
    updateBulkBar();
  };
  window.adClearSelection = function () {
    AD_SEL = {};
    document.querySelectorAll('.ad-rec-cb').forEach(function (c) { c.checked = false; });
    var allCb = document.getElementById('ad-cb-all-pending');
    if (allCb) allCb.checked = false;
    updateBulkBar();
  };
  function updateBulkBar() {
    var n = Object.keys(AD_SEL).length;
    var bar = document.getElementById('ad-bulk-bar');
    var cnt = document.getElementById('ad-bulk-count');
    if (bar) bar.style.display = n ? '' : 'none';
    if (cnt) cnt.textContent = n + ' selected';
  }

  // ── Accept / Decline ──────────────────────────────────────────────────────
  window.adRecAccept = function (id, btn) {
    btn.disabled = true; btn.textContent = '…';
    fetch('/recommendations/' + id + '/accept', { method: 'POST', headers: { 'Content-Type': 'application/json' } })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.success) {
          var r = AD_REC.pending.find(function (x) { return x.rec_id === id; });
          AD_REC.pending = AD_REC.pending.filter(function (x) { return x.rec_id !== id; });
          if (r) { r.status = 'monitoring'; r.accepted_at = new Date().toISOString(); AD_REC.monitoring.push(r); }
          delete AD_SEL[id]; updateBulkBar(); adRecRenderAll();
          adShowToast(d.message || 'Accepted', 'success');
        } else { adShowToast(d.message || 'Failed', 'error'); btn.disabled = false; btn.textContent = 'Accept'; }
      })
      .catch(function () { adShowToast('Request failed', 'error'); btn.disabled = false; btn.textContent = 'Accept'; });
  };
  window.adRecDecline = function (id, btn) {
    btn.disabled = true; btn.textContent = '…';
    fetch('/recommendations/' + id + '/decline', { method: 'POST', headers: { 'Content-Type': 'application/json' } })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.success) {
          var r = AD_REC.pending.find(function (x) { return x.rec_id === id; });
          AD_REC.pending = AD_REC.pending.filter(function (x) { return x.rec_id !== id; });
          if (r) { r.status = 'declined'; r.declined_at = new Date().toISOString(); AD_REC.history.unshift(r); }
          delete AD_SEL[id]; updateBulkBar(); adRecRenderAll();
          adShowToast(d.message || 'Declined', 'muted');
        } else { adShowToast(d.message || 'Failed', 'error'); btn.disabled = false; btn.textContent = 'Decline'; }
      })
      .catch(function () { adShowToast('Request failed', 'error'); btn.disabled = false; btn.textContent = 'Decline'; });
  };
  window.adDoBulk = function (action) {
    var ids = Object.keys(AD_SEL).map(Number);
    if (!ids.length) return;
    ids.forEach(function (id) {
      var btn = document.querySelector('[data-id="' + id + '"]');
      if (action === 'accept') window.adRecAccept(id, btn || document.createElement('button'));
      else window.adRecDecline(id, btn || document.createElement('button'));
    });
  };

  // ── DOMContentLoaded ──────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    // Run engine button
    var runBtn = document.getElementById('ad-run-engine-btn');
    if (runBtn) {
      runBtn.addEventListener('click', function () {
        var btn = this; var orig = btn.innerHTML;
        btn.disabled = true; btn.innerHTML = 'Running\u2026';
        fetch('/recommendations/run', { method: 'POST' })
          .then(function (r) { return r.json(); })
          .then(function (d) {
            btn.disabled = false; btn.innerHTML = orig;
            adShowToast(d.success ? (d.message || 'Engine complete.') : ('Error: ' + (d.message || 'unknown')), d.success ? 'success' : 'error');
            if (d.success) adRecLoad();
          })
          .catch(function () { btn.disabled = false; btn.innerHTML = orig; adShowToast('Request failed.', 'error'); });
      });
    }
    // Accept low risk button — only visible on Pending tab
    var lowRiskBtn = document.getElementById('ad-accept-low-risk-btn');
    if (lowRiskBtn) {
      lowRiskBtn.addEventListener('click', function () {
        AD_REC.pending.filter(function (r) { return (r.risk_level || 'low') === 'low'; }).forEach(function (r) {
          var btn = document.createElement('button');
          window.adRecAccept(r.rec_id, btn);
        });
      });
      // hide on non-pending sub-tabs
      var tabBtns = document.querySelectorAll('#adRecTabs button[data-bs-toggle="tab"]');
      tabBtns.forEach(function (btn) {
        btn.addEventListener('shown.bs.tab', function (e) {
          if (lowRiskBtn) lowRiskBtn.style.display = e.target.id === 'ad-rec-pending-tab' ? '' : 'none';
        });
      });
    }
    // Trigger load when recommendations outer tab is shown
    var recTabBtn = document.getElementById('recommendations-tab-btn');
    if (recTabBtn) recTabBtn.addEventListener('shown.bs.tab', function () { adRecLoad(); });
  });

})();
</script>'''

with open(PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace HTML: from "<!-- RECOMMENDATIONS TAB -->" to closing </div> of that pane
HTML_START = '    <!-- RECOMMENDATIONS TAB -->\n    <div class="tab-pane fade" id="recommendations-tab" role="tabpanel">'
HTML_END   = '\n\n    </div>\n\n  </div>\n</div>'

idx_start = content.find(HTML_START)
if idx_start == -1:
    print('ERROR: HTML start marker not found')
    exit(1)

# The recommendations-tab div closes at </div> then we have the outer </div></div>
# Find the closing pattern after the HTML_START
idx_end = content.find(HTML_END, idx_start)
if idx_end == -1:
    print('ERROR: HTML end marker not found')
    exit(1)

old_html_block = content[idx_start : idx_end]
print(f'HTML block found ({len(old_html_block)} chars), replacing...')
content = content[:idx_start] + NEW_HTML + content[idx_end:]

# 2. Replace JS: from the STATUS TAB SWITCHING block through end of script tag
JS_START = '// ===========================================================================\n// RECOMMENDATIONS TAB - STATUS TAB SWITCHING\n// ===========================================================================\n'
JS_END   = '</script>\n'

# Find the last </script> (end of the page script block)
idx_js_start = content.find(JS_START)
if idx_js_start == -1:
    print('ERROR: JS start marker not found')
    exit(1)

# Find the closing </script> after that position
idx_js_end = content.find(JS_END, idx_js_start)
if idx_js_end == -1:
    print('ERROR: JS end marker not found')
    exit(1)

old_js_block = content[idx_js_start : idx_js_end + len(JS_END)]
print(f'JS block found ({len(old_js_block)} chars), replacing...')
content = content[:idx_js_start] + NEW_JS + '\n' + content[idx_js_end + len(JS_END):]

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print('Done. ads_new.html updated.')
