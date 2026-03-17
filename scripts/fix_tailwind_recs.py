"""
Replaces the recommendations panel content and old JS in keywords.html, ads.html, shopping.html.
Run from: C:/Users/User/Desktop/gads-data-layer/
"""

IIFE_TEMPLATE = """(function () {
  var _ENTITY_TYPE = '{entity_type}';
  var _PREFIX = '{prefix}';

  function esc(s) {{ return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }}
  function rfBadge(v) {{
    if (!v) return '';
    var cls = v === 'rule' ? 'rec-rf-rule' : 'rec-rf-flag';
    return '<span class="rec-rf-badge ' + cls + '">' + esc(v.charAt(0).toUpperCase()+v.slice(1)) + '</span>';
  }}
  function rtBadge(v) {{
    if (!v) return '';
    var map = {{ budget:'rec-rt-budget', bid:'rec-rt-bid', status:'rec-rt-status', keyword:'rec-rt-keyword', shopping:'rec-rt-shopping' }};
    var cls = map[v] || 'rec-rt-budget';
    return '<span class="rec-rt-badge ' + cls + '">' + esc(v.charAt(0).toUpperCase()+v.slice(1)) + '</span>';
  }}
  function condCell(conds) {{
    if (!conds || !conds.length) return '';
    return '<div class="rec-conditions-cell">' + conds.map(function(c){{ return '<span>' + esc(c) + '</span>'; }}).join('') + '</div>';
  }}
  function actionCell(r) {{
    var dir = r.action_direction || '';
    var cls = dir === 'increase' ? 'rec-action-increase' : dir === 'decrease' ? 'rec-action-decrease' : dir === 'pause' ? 'rec-action-pause' : 'rec-action-flag';
    var arrow = dir === 'increase' ? '\\u2191 ' : dir === 'decrease' ? '\\u2193 ' : '';
    var plain = r.plain_english || (arrow + (r.action_magnitude ? r.action_magnitude + '%' : dir));
    var html = '<span class="rec-action-text ' + cls + '">' + esc(plain) + '</span>';
    if (r.current_value != null && r.proposed_value != null) {{
      html += '<div class="rec-action-sub">' + esc(String(r.current_value)) + ' \\u2192 ' + esc(String(r.proposed_value)) + '</div>';
    }}
    return html;
  }}
  function riskBadge(v) {{
    if (!v) return '';
    var cls = v === 'low' ? 'rec-risk-low' : v === 'medium' ? 'rec-risk-medium' : 'rec-risk-high';
    return '<span class="rec-risk-badge ' + cls + '">' + esc(v.charAt(0).toUpperCase()+v.slice(1)) + '</span>';
  }}
  function outcomeBadge(status) {{
    var map = {{ successful:'rec-outcome-successful', declined:'rec-outcome-declined', reverted:'rec-outcome-reverted', monitoring:'rec-outcome-monitoring' }};
    var label = {{ successful:'Successful', declined:'Declined', reverted:'Reverted', monitoring:'Monitoring' }};
    var cls = map[status] || '';
    return '<span class="rec-outcome-badge ' + cls + '">' + (label[status]||esc(status)) + '</span>';
  }}
  function fmtDate(s) {{
    if (!s) return '';
    var d = new Date(s);
    return isNaN(d) ? esc(s) : d.toLocaleDateString('en-GB', {{day:'numeric',month:'short',year:'numeric'}});
  }}
  function ageLabel(s) {{
    if (!s) return '';
    var diff = Math.floor((Date.now() - new Date(s)) / 86400000);
    return diff === 0 ? 'Today' : diff + 'd';
  }}
  function progressBar(r) {{
    if (!r.accepted_at || !r.monitoring_ends_at) return '';
    var start = new Date(r.accepted_at).getTime();
    var end   = new Date(r.monitoring_ends_at).getTime();
    var now   = Date.now();
    var pct   = Math.min(100, Math.max(0, Math.round((now - start) / (end - start) * 100)));
    var days  = Math.ceil((end - now) / 86400000);
    var endStr = new Date(r.monitoring_ends_at).toLocaleDateString('en-GB', {{day:'numeric',month:'short',year:'numeric'}});
    return '<div class="rec-progress-wrap"><div class="rec-progress-bg"><div class="rec-progress-fill" style="width:' + pct + '%"></div></div>' +
           '<div class="rec-progress-label">' + (days > 0 ? days + 'd remaining' : 'Ending') + ' \\u00b7 ends ' + endStr + '</div></div>';
  }}
  function makeExpRow(r, colspan) {{
    var why = esc(r.trigger_summary || r.plain_english || '\\u2014');
    var change = (r.current_value != null && r.proposed_value != null)
      ? esc(String(r.current_value)) + ' \\u2192 ' + esc(String(r.proposed_value))
      : (r.action_magnitude ? esc(String(r.action_magnitude)) + '%' : '\\u2014');
    var cooldown = r.cooldown_days ? esc(String(r.cooldown_days)) + ' days' : '\\u2014';
    return '<tr class="rec-expand-row" id="exp-' + esc(r.rec_id) + '">' +
      '<td colspan="' + colspan + '">' +
        '<div class="rec-expand-grid">' +
          '<div><div class="rec-expand-label">Why triggered</div><div class="rec-expand-val">' + why + '</div></div>' +
          '<div><div class="rec-expand-label">Proposed change</div><div class="rec-expand-val">' + change + '</div></div>' +
          '<div><div class="rec-expand-label">Rule details</div><div class="rec-expand-val"><ul>' +
            '<li>Cooldown: ' + cooldown + '</li>' +
            '<li>Rule: ' + esc(r.rule_id||'\\u2014') + '</li>' +
          '</ul></div></div>' +
        '</div>' +
      '</td></tr>';
  }}

  var REC = {{ pending:[], monitoring:[], successful:[], history:[] }};
  var SEL = {{}};
  var PAGE = {{ pending:1, monitoring:1, successful:1, history:1 }};
  var PER = 20;

  function pendingRow(r) {{
    var checked = SEL[r.rec_id] ? 'checked' : '';
    var high = (r.risk_level === 'high') ? '<div class="rec-human-badge"><i class="bi bi-exclamation-triangle-fill"></i> Human confirm</div>' : '';
    return '<tr class="' + (SEL[r.rec_id] ? 'rec-selected' : '') + '" onclick="{prefix}RecExp(event,\\'' + esc(r.rec_id) + '\\')" style="cursor:pointer">' +
      '<td class="rec-col-cb" onclick="event.stopPropagation()"><input type="checkbox" ' + checked + ' onchange="{prefix}RecCbChange(this,\\'' + esc(r.rec_id) + '\\')" ></td>' +
      '<td class="rec-col-name">' + esc(r.entity_name||'') + '</td>' +
      '<td class="rec-col-rule">' + esc(r.rule_name||r.rule_id||'') + '</td>' +
      '<td class="rec-col-ruleflag">' + rfBadge(r.rule_or_flag) + '</td>' +
      '<td class="rec-col-ruletype">' + rtBadge(r.rule_type_display) + '</td>' +
      '<td class="rec-col-conditions">' + condCell(r.conditions) + '</td>' +
      '<td class="rec-col-action">' + high + actionCell(r) + '</td>' +
      '<td class="rec-col-risk">' + riskBadge(r.risk_level) + '</td>' +
      '<td class="rec-col-age">' + ageLabel(r.generated_at) + '</td>' +
      '<td class="rec-col-acts"><div class="rec-row-acts">' +
        '<button class="rec-row-btn rec-row-btn-accept" onclick="event.stopPropagation();{prefix}RecAccept(\\'' + esc(r.rec_id) + '\\',this)">Accept</button>' +
        '<button class="rec-row-btn rec-row-btn-decline" onclick="event.stopPropagation();{prefix}RecDecline(\\'' + esc(r.rec_id) + '\\',this)">Decline</button>' +
      '</div></td>' +
    '</tr>' + makeExpRow(r, 10);
  }}
  function monitoringRow(r) {{
    return '<tr onclick="{prefix}RecExp(event,\\'' + esc(r.rec_id) + '\\')" style="cursor:pointer">' +
      '<td class="rec-col-name">' + esc(r.entity_name||'') + '</td>' +
      '<td class="rec-col-rule">' + esc(r.rule_name||r.rule_id||'') + '</td>' +
      '<td class="rec-col-ruleflag">' + rfBadge(r.rule_or_flag) + '</td>' +
      '<td class="rec-col-action">' + actionCell(r) + '</td>' +
      '<td class="rec-col-risk">' + riskBadge(r.risk_level) + '</td>' +
      '<td class="rec-col-date">' + fmtDate(r.accepted_at) + '</td>' +
      '<td class="rec-col-progress">' + progressBar(r) + '</td>' +
    '</tr>' + makeExpRow(r, 7);
  }}
  function successfulRow(r) {{
    return '<tr onclick="{prefix}RecExp(event,\\'' + esc(r.rec_id) + '\\')" style="cursor:pointer">' +
      '<td class="rec-col-name">' + esc(r.entity_name||'') + '</td>' +
      '<td class="rec-col-rule">' + esc(r.rule_name||r.rule_id||'') + '</td>' +
      '<td class="rec-col-ruleflag">' + rfBadge(r.rule_or_flag) + '</td>' +
      '<td class="rec-col-action">' + actionCell(r) + '</td>' +
      '<td class="rec-col-risk">' + riskBadge(r.risk_level) + '</td>' +
      '<td class="rec-col-date">' + fmtDate(r.completed_at || r.resolved_at) + '</td>' +
    '</tr>' + makeExpRow(r, 6);
  }}
  function historyRow(r) {{
    return '<tr onclick="{prefix}RecExp(event,\\'' + esc(r.rec_id) + '\\')" style="cursor:pointer">' +
      '<td class="rec-col-name">' + esc(r.entity_name||'') + '</td>' +
      '<td class="rec-col-rule">' + esc(r.rule_name||r.rule_id||'') + '</td>' +
      '<td class="rec-col-ruleflag">' + rfBadge(r.rule_or_flag) + '</td>' +
      '<td class="rec-col-action">' + actionCell(r) + '</td>' +
      '<td class="rec-col-risk">' + riskBadge(r.risk_level) + '</td>' +
      '<td class="rec-col-date">' + fmtDate(r.resolved_at || r.accepted_at) + '</td>' +
      '<td class="rec-col-status">' + outcomeBadge(r.status) + '</td>' +
    '</tr>' + makeExpRow(r, 7);
  }}

  function renderTab(tab) {{
    var items = REC[tab];
    var page  = PAGE[tab];
    var start = (page - 1) * PER;
    var slice = items.slice(start, start + PER);
    var tbody = document.getElementById('{prefix}-' + tab + '-tbody');
    var pag   = document.getElementById('{prefix}-' + tab + '-paginator');
    if (!tbody) return;
    if (!items.length) {{
      tbody.innerHTML = '<tr><td colspan="11" style="text-align:center;padding:24px;color:#6b7280;">No ' + tab + ' recommendations.</td></tr>';
      if (pag) pag.innerHTML = '';
      return;
    }}
    var html = '';
    slice.forEach(function(r) {{
      html += (tab === 'pending' ? pendingRow(r) : tab === 'monitoring' ? monitoringRow(r) : tab === 'successful' ? successfulRow(r) : historyRow(r));
    }});
    tbody.innerHTML = html;
    buildPag(pag, items.length, page, function(p) {{ PAGE[tab] = p; renderTab(tab); }});
  }}

  function buildPag(el, total, current, cb) {{
    if (!el) return;
    var pages = Math.ceil(total / PER);
    if (pages <= 1) {{ el.innerHTML = ''; return; }}
    var html = '<div style="display:flex;gap:4px;flex-wrap:wrap;margin-top:8px;">';
    for (var i = 1; i <= pages; i++) {{
      var style = i === current
        ? 'background:#1a73e8;color:#fff;border:1px solid #1a73e8;'
        : 'background:#fff;color:#374151;border:1px solid #d1d5db;';
      html += '<button style="' + style + 'padding:4px 10px;border-radius:4px;font-size:12px;cursor:pointer;" data-p="' + i + '">' + i + '</button>';
    }}
    html += '</div>';
    el.innerHTML = html;
    el.querySelectorAll('button').forEach(function(btn) {{
      btn.addEventListener('click', function() {{ cb(parseInt(this.dataset.p)); }});
    }});
  }}

  function renderAll() {{
    ['pending','monitoring','successful','history'].forEach(renderTab);
    ['pending','monitoring','successful','history'].forEach(function(k) {{
      var el = document.getElementById('{prefix}-badge-' + k);
      if (el) el.textContent = REC[k].length;
    }});
  }}

  function toast(msg, type) {{
    if (typeof showToast === 'function') showToast(msg, type, 3000);
  }}

  function recLoad() {{
    fetch('/recommendations/cards')
      .then(function(r) {{ return r.json(); }})
      .then(function(data) {{
        REC.pending    = (data.pending    || []).filter(function(r){{ return r.entity_type === _ENTITY_TYPE; }});
        REC.monitoring = (data.monitoring || []).filter(function(r){{ return r.entity_type === _ENTITY_TYPE; }});
        REC.successful = (data.successful || []).filter(function(r){{ return r.entity_type === _ENTITY_TYPE; }});
        var hist = (data.declined || []).concat(data.reverted || []).filter(function(r){{ return r.entity_type === _ENTITY_TYPE; }});
        hist.sort(function(a,b){{ return new Date(b.resolved_at||b.accepted_at||0) - new Date(a.resolved_at||a.accepted_at||0); }});
        REC.history = hist;
        SEL = {{}};
        renderAll();
      }})
      .catch(function(err) {{ console.error('{prefix} recLoad error', err); }});
  }}

  window['{prefix}RecExp'] = function(evt, id) {{
    if (evt.target.type === 'checkbox' || evt.target.tagName === 'BUTTON') return;
    var row = document.getElementById('exp-' + id);
    if (row) row.classList.toggle('open');
  }};
  window['{prefix}RecCbChange'] = function(chk, id) {{
    if (chk.checked) SEL[id] = true; else delete SEL[id];
    updateBulkBar();
  }};
  window['{prefix}ToggleAll'] = function(chk) {{
    var start = (PAGE.pending - 1) * PER;
    var slice = REC.pending.slice(start, start + PER);
    slice.forEach(function(r) {{ if (chk.checked) SEL[r.rec_id] = true; else delete SEL[r.rec_id]; }});
    renderTab('pending');
    updateBulkBar();
  }};
  window['{prefix}ClearSelection'] = function() {{
    SEL = {{}};
    var master = document.getElementById('{prefix}-chk-all');
    if (master) master.checked = false;
    renderTab('pending');
    updateBulkBar();
  }};
  function updateBulkBar() {{
    var count = Object.keys(SEL).length;
    var bar = document.getElementById('{prefix}-bulk-bar');
    var lbl = document.getElementById('{prefix}-bulk-count');
    if (bar) bar.style.display = count > 0 ? 'flex' : 'none';
    if (lbl) lbl.textContent = count + ' selected';
  }}
  window['{prefix}RecAccept'] = function(recId, btn) {{
    btn.disabled = true; btn.textContent = '...';
    fetch('/recommendations/' + recId + '/accept', {{ method:'POST', headers:{{'Content-Type':'application/json'}} }})
      .then(function(r){{ return r.json(); }})
      .then(function(d){{
        if (d.success) {{
          REC.pending = REC.pending.filter(function(r){{ return r.rec_id !== recId; }});
          delete SEL[recId];
          renderAll();
          toast('Recommendation accepted', 'success');
        }} else {{ toast(d.message || 'Failed', 'error'); btn.disabled=false; btn.textContent='Accept'; }}
      }})
      .catch(function(){{ toast('Error', 'error'); btn.disabled=false; btn.textContent='Accept'; }});
  }};
  window['{prefix}RecDecline'] = function(recId, btn) {{
    btn.disabled = true; btn.textContent = '...';
    fetch('/recommendations/' + recId + '/decline', {{ method:'POST', headers:{{'Content-Type':'application/json'}} }})
      .then(function(r){{ return r.json(); }})
      .then(function(d){{
        if (d.success) {{
          REC.pending = REC.pending.filter(function(r){{ return r.rec_id !== recId; }});
          delete SEL[recId];
          renderAll();
          toast('Recommendation declined', 'success');
        }} else {{ toast(d.message || 'Failed', 'error'); btn.disabled=false; btn.textContent='Decline'; }}
      }})
      .catch(function(){{ toast('Error', 'error'); btn.disabled=false; btn.textContent='Decline'; }});
  }};
  window['{prefix}DoBulk'] = function(action) {{
    var ids = Object.keys(SEL);
    if (!ids.length) return;
    var done = 0;
    ids.forEach(function(id) {{
      fetch('/recommendations/' + id + '/' + action, {{ method:'POST', headers:{{'Content-Type':'application/json'}} }})
        .then(function(r){{ return r.json(); }})
        .then(function(d){{
          if (d.success) REC.pending = REC.pending.filter(function(r){{ return r.rec_id !== id; }});
          done++;
          if (done === ids.length) {{ SEL = {{}}; renderAll(); toast('Done', 'success'); }}
        }});
    }});
  }};

  // Accept low risk
  window['{prefix}AcceptLowRisk'] = function() {{
    var low = REC.pending.filter(function(r){{ return r.risk_level === 'low'; }});
    if (!low.length) {{ toast('No low-risk recommendations pending', 'info'); return; }}
    low.forEach(function(r) {{ SEL[r.rec_id] = true; }});
    window['{prefix}DoBulk']('accept');
  }};

  // Patch showTab to load on first open
  var _{prefix}Loaded = false;
  var _orig{PREFIX}ShowTab = typeof showTab === 'function' ? showTab : null;
  showTab = function(tab) {{
    if (_orig{PREFIX}ShowTab) _orig{PREFIX}ShowTab(tab);
    if (tab === 'recommendations' && !_{prefix}Loaded) {{
      _{prefix}Loaded = true;
      recLoad();
    }}
  }};

  window.{prefix}RecLoad = recLoad;
}})();"""


def make_panel_html(prefix, entity_col_header):
    p = prefix
    return f"""<link rel="stylesheet" href="/static/css/recommendations.css">
<div style="margin-bottom:12px;display:flex;align-items:center;justify-content:space-between;">
  <h5 style="margin:0;font-size:16px;font-weight:600;">Recommendations</h5>
  <div style="display:flex;gap:8px;">
    <button style="padding:5px 12px;border:1px solid #d1d5db;border-radius:4px;background:#fff;font-size:13px;cursor:pointer;" onclick="{p}AcceptLowRisk()">Accept low risk</button>
    <button id="{p}-run-engine-btn" style="padding:5px 12px;background:#1a73e8;color:#fff;border:none;border-radius:4px;font-size:13px;cursor:pointer;">Run engine</button>
  </div>
</div>
<!-- Sub-tabs -->
<div style="display:flex;gap:0;border-bottom:2px solid #e5e7eb;margin-bottom:12px;">
  <button id="{p}-tab-pending" onclick="{p}SwitchTab('pending')" style="padding:8px 16px;border:none;background:none;font-size:13px;font-weight:600;color:#1a73e8;border-bottom:2px solid #1a73e8;cursor:pointer;margin-bottom:-2px;">Pending <span id="{p}-badge-pending" style="background:#e5e7eb;color:#374151;border-radius:9999px;padding:1px 7px;font-size:11px;">0</span></button>
  <button id="{p}-tab-monitoring" onclick="{p}SwitchTab('monitoring')" style="padding:8px 16px;border:none;background:none;font-size:13px;color:#6b7280;cursor:pointer;">Monitoring <span id="{p}-badge-monitoring" style="background:#e5e7eb;color:#374151;border-radius:9999px;padding:1px 7px;font-size:11px;">0</span></button>
  <button id="{p}-tab-successful" onclick="{p}SwitchTab('successful')" style="padding:8px 16px;border:none;background:none;font-size:13px;color:#6b7280;cursor:pointer;">Successful <span id="{p}-badge-successful" style="background:#e5e7eb;color:#374151;border-radius:9999px;padding:1px 7px;font-size:11px;">0</span></button>
  <button id="{p}-tab-history" onclick="{p}SwitchTab('history')" style="padding:8px 16px;border:none;background:none;font-size:13px;color:#6b7280;cursor:pointer;">History <span id="{p}-badge-history" style="background:#e5e7eb;color:#374151;border-radius:9999px;padding:1px 7px;font-size:11px;">0</span></button>
</div>
<!-- PENDING -->
<div id="{p}-pane-pending">
  <div id="{p}-bulk-bar" class="rec-bulk-bar" style="display:none;">
    <span id="{p}-bulk-count">0 selected</span>
    <button style="margin-left:8px;padding:4px 12px;background:#1a73e8;color:#fff;border:none;border-radius:4px;font-size:12px;cursor:pointer;" onclick="{p}DoBulk('accept')">Accept selected</button>
    <button style="margin-left:4px;padding:4px 12px;background:#fff;color:#dc2626;border:1px solid #fca5a5;border-radius:4px;font-size:12px;cursor:pointer;" onclick="{p}DoBulk('decline')">Decline selected</button>
    <span class="rec-bulk-clear" onclick="{p}ClearSelection()">Clear</span>
  </div>
  <table class="rec-tab-slim" style="width:100%;border-collapse:collapse;font-size:13px;">
    <thead style="background:#f9fafb;">
      <tr>
        <th class="rec-col-cb" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;"><input type="checkbox" id="{p}-chk-all" onchange="{p}ToggleAll(this)"></th>
        <th class="rec-col-name" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">{entity_col_header}</th>
        <th class="rec-col-rule" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">Rule</th>
        <th class="rec-col-ruleflag" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">R/F</th>
        <th class="rec-col-ruletype" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">Rule type</th>
        <th class="rec-col-conditions" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">Conditions</th>
        <th class="rec-col-action" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">Action</th>
        <th class="rec-col-risk" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">Risk</th>
        <th class="rec-col-age" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">Age</th>
        <th class="rec-col-acts" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">Actions</th>
      </tr>
    </thead>
    <tbody id="{p}-pending-tbody"></tbody>
  </table>
  <div id="{p}-pending-paginator"></div>
</div>
<!-- MONITORING -->
<div id="{p}-pane-monitoring" style="display:none;">
  <table class="rec-tab-slim" style="width:100%;border-collapse:collapse;font-size:13px;">
    <thead style="background:#f9fafb;">
      <tr>
        <th class="rec-col-name" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">{entity_col_header}</th>
        <th class="rec-col-rule" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">Rule</th>
        <th class="rec-col-ruleflag" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">R/F</th>
        <th class="rec-col-action" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">Action taken</th>
        <th class="rec-col-risk" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">Risk</th>
        <th class="rec-col-date" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">Accepted</th>
        <th class="rec-col-progress" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">Progress</th>
      </tr>
    </thead>
    <tbody id="{p}-monitoring-tbody"></tbody>
  </table>
  <div id="{p}-monitoring-paginator"></div>
</div>
<!-- SUCCESSFUL -->
<div id="{p}-pane-successful" style="display:none;">
  <table class="rec-tab-slim" style="width:100%;border-collapse:collapse;font-size:13px;">
    <thead style="background:#f9fafb;">
      <tr>
        <th class="rec-col-name" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">{entity_col_header}</th>
        <th class="rec-col-rule" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">Rule</th>
        <th class="rec-col-ruleflag" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">R/F</th>
        <th class="rec-col-action" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">Action taken</th>
        <th class="rec-col-risk" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">Risk</th>
        <th class="rec-col-date" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">Completed</th>
      </tr>
    </thead>
    <tbody id="{p}-successful-tbody"></tbody>
  </table>
  <div id="{p}-successful-paginator"></div>
</div>
<!-- HISTORY -->
<div id="{p}-pane-history" style="display:none;">
  <table class="rec-tab-slim" style="width:100%;border-collapse:collapse;font-size:13px;">
    <thead style="background:#f9fafb;">
      <tr>
        <th class="rec-col-name" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">{entity_col_header}</th>
        <th class="rec-col-rule" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">Rule</th>
        <th class="rec-col-ruleflag" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">R/F</th>
        <th class="rec-col-action" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">Action</th>
        <th class="rec-col-risk" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">Risk</th>
        <th class="rec-col-date" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">Date</th>
        <th class="rec-col-status" style="padding:8px;text-align:left;border-bottom:1px solid #e5e7eb;">Outcome</th>
      </tr>
    </thead>
    <tbody id="{p}-history-tbody"></tbody>
  </table>
  <div id="{p}-history-paginator"></div>
</div>
<script>
function {p}SwitchTab(tab) {{
  ['pending','monitoring','successful','history'].forEach(function(t) {{
    var pane = document.getElementById('{p}-pane-' + t);
    var btn  = document.getElementById('{p}-tab-' + t);
    if (!pane || !btn) return;
    if (t === tab) {{
      pane.style.display = '';
      btn.style.color = '#1a73e8';
      btn.style.borderBottom = '2px solid #1a73e8';
      btn.style.marginBottom = '-2px';
    }} else {{
      pane.style.display = 'none';
      btn.style.color = '#6b7280';
      btn.style.borderBottom = 'none';
      btn.style.marginBottom = '';
    }}
  }});
}}
document.addEventListener('DOMContentLoaded', function() {{
  var runBtn = document.getElementById('{p}-run-engine-btn');
  if (runBtn) {{
    runBtn.addEventListener('click', function() {{
      var self = this;
      self.disabled = true; self.textContent = 'Running...';
      fetch('/recommendations/run', {{ method:'POST' }})
        .then(function(r) {{ return r.json(); }})
        .then(function(d) {{ if (typeof showToast==='function') showToast(d.message||'Engine started','success',3000); setTimeout(window.{p}RecLoad, 2000); }})
        .catch(function() {{ if (typeof showToast==='function') showToast('Error','error',3000); }})
        .finally(function() {{ self.disabled=false; self.textContent='Run engine'; }});
    }});
  }}
}});
</script>"""


def make_iife(prefix, entity_type):
    upper = prefix[0].upper() + prefix[1:]
    return IIFE_TEMPLATE.replace('{entity_type}', entity_type).replace('{prefix}', prefix).replace('{PREFIX}', upper)


# ─── Process keywords.html ─────────────────────────────────────────────────────
path = 'C:/Users/User/Desktop/gads-data-layer/act_dashboard/templates/keywords.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace recommendations panel content
old_panel_start = '<div id="panel-recommendations" class="hidden">'
old_panel_end = '</div>\n\n<!-- JavaScript -->'
s = content.find(old_panel_start)
e = content.find(old_panel_end)
assert s != -1, 'kw panel start not found'
assert e != -1, 'kw panel end not found'
new_panel = old_panel_start + '\n' + make_panel_html('kw', 'Keyword') + '\n</div>\n\n<!-- JavaScript -->'
content = content[:s] + new_panel + content[e + len(old_panel_end):]

# 2. Replace old keyword rec JS section
old_js_marker = '// ==================== KEYWORD RECOMMENDATIONS EXECUTION ===================='
js_start = content.find(old_js_marker)
assert js_start != -1, 'kw JS start not found'
# Find closing </script> after js_start
script_end = content.find('</script>', js_start)
assert script_end != -1, 'kw script end not found'
new_js = '\n' + make_iife('kw', 'keyword') + '\n'
content = content[:js_start] + new_js + content[script_end:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f'keywords.html done. Lines: {content.count(chr(10))}')


# ─── Process ads.html ──────────────────────────────────────────────────────────
path = 'C:/Users/User/Desktop/gads-data-layer/act_dashboard/templates/ads.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_panel_start = '        <!-- Tab 3: Recommendations -->\n        <div id="content-recommendations" class="tab-content hidden">'
old_panel_end = '        </div>\n\n<script>'
s = content.find(old_panel_start)
if s == -1:
    old_panel_start = '        <!-- Tab 3: Recommendations -->\n        <div id="content-recommendations" class="tab-content hidden">'
    # Try without leading spaces
    old_panel_start2 = '<!-- Tab 3: Recommendations -->'
    s2 = content.find(old_panel_start2)
    # Find the actual div
    div_s = content.find('<div id="content-recommendations"', s2 if s2 != -1 else 0)
    s = div_s
    assert s != -1, 'ads panel start not found'
    # Find what comes right before it
    pre = content.rfind('\n', 0, s)
    s = pre + 1  # include from line start

# Find end: closing div then </div>\n\n<script> or </div>\n<script>
old_panel_end = '</div>\n\n<script>'
e = content.find(old_panel_end, s)
if e == -1:
    old_panel_end = '</div>\n<script>'
    e = content.find(old_panel_end, s)
assert e != -1, 'ads panel end not found'

new_panel_div = '        <!-- Tab 3: Recommendations -->\n        <div id="content-recommendations" class="tab-content hidden">\n' + make_panel_html('ad', 'Ad') + '\n        </div>'
content = content[:s] + new_panel_div + '\n\n<script>' + content[e + len(old_panel_end):]

# Replace old ad rec JS
old_js_marker = '// ==================== AD RECOMMENDATIONS EXECUTION ===================='
js_start = content.find(old_js_marker)
assert js_start != -1, 'ads JS start not found'
script_end = content.find('</script>', js_start)
assert script_end != -1, 'ads script end not found'
new_js = '\n' + make_iife('ad', 'ad') + '\n'
content = content[:js_start] + new_js + content[script_end:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f'ads.html done. Lines: {content.count(chr(10))}')


# ─── Process shopping.html ─────────────────────────────────────────────────────
path = 'C:/Users/User/Desktop/gads-data-layer/act_dashboard/templates/shopping.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_panel_start = '<div id="content-recommendations" class="tab-content hidden">'
old_panel_end = '\n\n<script>'
s = content.find(old_panel_start)
assert s != -1, 'shopping panel start not found'
e = content.find(old_panel_end, s)
if e == -1:
    old_panel_end = '\n<script>'
    e = content.find(old_panel_end, s)
assert e != -1, 'shopping panel end not found'
# Find the end of the div (look for </div> before <script>)
# The panel ends with </div> on a line before \n\n<script>
div_end = content.rfind('\n</div>', s, e)
assert div_end != -1, 'shopping div end not found'
end_pos = div_end + len('\n</div>')

new_panel = old_panel_start + '\n' + make_panel_html('shop', 'Product') + '\n</div>'
content = content[:s] + new_panel + content[end_pos:]

# Replace old shopping rec JS
old_js_marker = '// ==================== SHOPPING RECOMMENDATIONS EXECUTION ===================='
js_start = content.find(old_js_marker)
assert js_start != -1, 'shopping JS start not found'
script_end = content.find('</script>', js_start)
assert script_end != -1, 'shopping script end not found'
new_js = '\n' + make_iife('shop', 'shopping_product') + '\n'
content = content[:js_start] + new_js + content[script_end:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f'shopping.html done. Lines: {content.count(chr(10))}')
