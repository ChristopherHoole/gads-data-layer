NEW_JS = """(function () {
  function esc(s) { return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
  function rfBadge(v) {
    if (!v) return '';
    var cls = v === 'rule' ? 'rec-rf-rule' : 'rec-rf-flag';
    return '<span class="rec-rf-badge ' + cls + '">' + esc(v.charAt(0).toUpperCase()+v.slice(1)) + '</span>';
  }
  function rtBadge(v) {
    if (!v) return '';
    var map = { budget:'rec-rt-budget', bid:'rec-rt-bid', status:'rec-rt-status', keyword:'rec-rt-keyword', shopping:'rec-rt-shopping' };
    var cls = map[v] || 'rec-rt-budget';
    return '<span class="rec-rt-badge ' + cls + '">' + esc(v.charAt(0).toUpperCase()+v.slice(1)) + '</span>';
  }
  function condCell(conds) {
    if (!conds || !conds.length) return '';
    return '<div class="rec-conditions-cell">' + conds.map(function(c){ return '<span>' + esc(c) + '</span>'; }).join('') + '</div>';
  }
  function actionCell(r) {
    var dir = r.action_direction || '';
    var cls = dir === 'increase' ? 'rec-action-increase' : dir === 'decrease' ? 'rec-action-decrease' : dir === 'pause' ? 'rec-action-pause' : 'rec-action-flag';
    var arrow = dir === 'increase' ? '\\u2191 ' : dir === 'decrease' ? '\\u2193 ' : '';
    var plain = r.plain_english || (arrow + (r.action_magnitude ? r.action_magnitude + '%' : dir));
    var html = '<span class="rec-action-text ' + cls + '">' + esc(plain) + '</span>';
    if (r.current_value != null && r.proposed_value != null) {
      html += '<div class="rec-action-sub">' + esc(String(r.current_value)) + ' \\u2192 ' + esc(String(r.proposed_value)) + '</div>';
    }
    return html;
  }
  function riskBadge(v) {
    if (!v) return '';
    var cls = v === 'low' ? 'rec-risk-low' : v === 'medium' ? 'rec-risk-medium' : 'rec-risk-high';
    return '<span class="rec-risk-badge ' + cls + '">' + esc(v.charAt(0).toUpperCase()+v.slice(1)) + '</span>';
  }
  function outcomeBadge(status) {
    var map = { successful:'rec-outcome-successful', declined:'rec-outcome-declined', reverted:'rec-outcome-reverted', monitoring:'rec-outcome-monitoring' };
    var label = { successful:'Successful', declined:'Declined', reverted:'Reverted', monitoring:'Monitoring' };
    var cls = map[status] || '';
    return '<span class="rec-outcome-badge ' + cls + '">' + (label[status]||esc(status)) + '</span>';
  }
  function fmtDate(s) {
    if (!s) return '';
    var d = new Date(s);
    return isNaN(d) ? esc(s) : d.toLocaleDateString('en-GB', {day:'numeric',month:'short',year:'numeric'});
  }
  function ageLabel(s) {
    if (!s) return '';
    var diff = Math.floor((Date.now() - new Date(s)) / 86400000);
    return diff === 0 ? 'Today' : diff + 'd';
  }
  function progressBar(r) {
    if (!r.accepted_at || !r.monitoring_ends_at) return '';
    var start = new Date(r.accepted_at).getTime();
    var end   = new Date(r.monitoring_ends_at).getTime();
    var now   = Date.now();
    var pct   = Math.min(100, Math.max(0, Math.round((now - start) / (end - start) * 100)));
    var days  = Math.ceil((end - now) / 86400000);
    var endStr = new Date(r.monitoring_ends_at).toLocaleDateString('en-GB', {day:'numeric',month:'short',year:'numeric'});
    return '<div class="rec-progress-wrap"><div class="rec-progress-bg"><div class="rec-progress-fill" style="width:' + pct + '%"></div></div>' +
           '<div class="rec-progress-label">' + (days > 0 ? days + 'd remaining' : 'Ending') + ' \\u00b7 ends ' + endStr + '</div></div>';
  }
  function makeExpRow(r, colspan) {
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
  }
  var AG_REC = { pending:[], monitoring:[], successful:[], history:[] };
  var AG_SEL = {};
  var AG_PAGE = { pending:1, monitoring:1, successful:1, history:1 };
  var AG_PER_PAGE = 20;
  function pendingRow(r) {
    var checked = AG_SEL[r.rec_id] ? 'checked' : '';
    var high = (r.risk_level === 'high') ? '<div class="rec-human-badge"><i class="bi bi-exclamation-triangle-fill"></i> Human confirm</div>' : '';
    return '<tr class="' + (AG_SEL[r.rec_id] ? 'rec-selected' : '') + '" onclick="agRecExp(event,\\'' + esc(r.rec_id) + '\\')" style="cursor:pointer">' +
      '<td class="rec-col-cb" onclick="event.stopPropagation()"><input type="checkbox" ' + checked + ' onchange="agRecCbChange(this,\\'' + esc(r.rec_id) + '\\')" ></td>' +
      '<td class="rec-col-name">' + esc(r.entity_name||'') + '</td>' +
      '<td class="rec-col-rule">' + esc(r.rule_name||r.rule_id||'') + '</td>' +
      '<td class="rec-col-ruleflag">' + rfBadge(r.rule_or_flag) + '</td>' +
      '<td class="rec-col-ruletype">' + rtBadge(r.rule_type_display) + '</td>' +
      '<td class="rec-col-conditions">' + condCell(r.conditions) + '</td>' +
      '<td class="rec-col-action">' + high + actionCell(r) + '</td>' +
      '<td class="rec-col-risk">' + riskBadge(r.risk_level) + '</td>' +
      '<td class="rec-col-age">' + ageLabel(r.generated_at) + '</td>' +
      '<td class="rec-col-acts"><div class="rec-row-acts">' +
        '<button class="rec-row-btn rec-row-btn-accept" onclick="event.stopPropagation();agRecAccept(\\'' + esc(r.rec_id) + '\\',this)">Accept</button>' +
        '<button class="rec-row-btn rec-row-btn-decline" onclick="event.stopPropagation();agRecDecline(\\'' + esc(r.rec_id) + '\\',this)">Decline</button>' +
      '</div></td>' +
    '</tr>' + makeExpRow(r, 10);
  }
  function monitoringRow(r) {
    return '<tr onclick="agRecExp(event,\\'' + esc(r.rec_id) + '\\')" style="cursor:pointer">' +
      '<td class="rec-col-name">' + esc(r.entity_name||'') + '</td>' +
      '<td class="rec-col-rule">' + esc(r.rule_name||r.rule_id||'') + '</td>' +
      '<td class="rec-col-ruleflag">' + rfBadge(r.rule_or_flag) + '</td>' +
      '<td class="rec-col-action">' + actionCell(r) + '</td>' +
      '<td class="rec-col-risk">' + riskBadge(r.risk_level) + '</td>' +
      '<td class="rec-col-date">' + fmtDate(r.accepted_at) + '</td>' +
      '<td class="rec-col-progress">' + progressBar(r) + '</td>' +
    '</tr>' + makeExpRow(r, 7);
  }
  function successfulRow(r) {
    return '<tr onclick="agRecExp(event,\\'' + esc(r.rec_id) + '\\')" style="cursor:pointer">' +
      '<td class="rec-col-name">' + esc(r.entity_name||'') + '</td>' +
      '<td class="rec-col-rule">' + esc(r.rule_name||r.rule_id||'') + '</td>' +
      '<td class="rec-col-ruleflag">' + rfBadge(r.rule_or_flag) + '</td>' +
      '<td class="rec-col-action">' + actionCell(r) + '</td>' +
      '<td class="rec-col-risk">' + riskBadge(r.risk_level) + '</td>' +
      '<td class="rec-col-date">' + fmtDate(r.completed_at || r.resolved_at) + '</td>' +
    '</tr>' + makeExpRow(r, 6);
  }
  function historyRow(r) {
    return '<tr onclick="agRecExp(event,\\'' + esc(r.rec_id) + '\\')" style="cursor:pointer">' +
      '<td class="rec-col-name">' + esc(r.entity_name||'') + '</td>' +
      '<td class="rec-col-rule">' + esc(r.rule_name||r.rule_id||'') + '</td>' +
      '<td class="rec-col-ruleflag">' + rfBadge(r.rule_or_flag) + '</td>' +
      '<td class="rec-col-action">' + actionCell(r) + '</td>' +
      '<td class="rec-col-risk">' + riskBadge(r.risk_level) + '</td>' +
      '<td class="rec-col-date">' + fmtDate(r.resolved_at || r.accepted_at) + '</td>' +
      '<td class="rec-col-status">' + outcomeBadge(r.status) + '</td>' +
    '</tr>' + makeExpRow(r, 7);
  }
  function renderTab(tab) {
    var items = AG_REC[tab];
    var page  = AG_PAGE[tab];
    var start = (page - 1) * AG_PER_PAGE;
    var slice = items.slice(start, start + AG_PER_PAGE);
    var tbody = document.getElementById('ag-' + tab + '-tbody');
    var pag   = document.getElementById('ag-' + tab + '-paginator');
    if (!tbody) return;
    if (!items.length) {
      tbody.innerHTML = '<tr><td colspan="11" class="text-center text-muted py-4">No ' + tab + ' recommendations for ad groups.</td></tr>';
      if (pag) pag.innerHTML = '';
      return;
    }
    var html = '';
    slice.forEach(function(r) {
      html += (tab === 'pending' ? pendingRow(r) : tab === 'monitoring' ? monitoringRow(r) : tab === 'successful' ? successfulRow(r) : historyRow(r));
    });
    tbody.innerHTML = html;
    buildPag(pag, items.length, page, function(p) { AG_PAGE[tab] = p; renderTab(tab); });
  }
  function buildPag(el, total, current, cb) {
    if (!el) return;
    var pages = Math.ceil(total / AG_PER_PAGE);
    if (pages <= 1) { el.innerHTML = ''; return; }
    var html = '';
    for (var i = 1; i <= pages; i++) {
      html += '<button class="btn btn-sm ' + (i === current ? 'btn-primary' : 'btn-outline-secondary') + '" data-p="' + i + '">' + i + '</button>';
    }
    el.innerHTML = html;
    el.querySelectorAll('button').forEach(function(btn) {
      btn.addEventListener('click', function() { cb(parseInt(this.dataset.p)); });
    });
  }
  function agRecRenderAll() {
    ['pending','monitoring','successful','history'].forEach(renderTab);
    ['pending','monitoring','successful','history'].forEach(function(k) {
      var el = document.getElementById('ag-badge-' + k);
      if (el) el.textContent = AG_REC[k].length;
    });
  }
  function agShowToast(msg, type) {
    var wrap = document.getElementById('act-toast-wrap');
    if (!wrap) return;
    var cls = type === 'success' ? 't-success' : type === 'error' ? 't-error' : 't-muted';
    wrap.innerHTML = '<div class="act-toast ' + cls + '">' + esc(msg) + '</div>';
    var t = wrap.querySelector('.act-toast');
    if (t) t.style.display = 'block';
    setTimeout(function() { wrap.innerHTML = ''; }, 3500);
  }
  function agRecLoad() {
    fetch('/recommendations/cards')
      .then(function(r) { return r.json(); })
      .then(function(data) {
        AG_REC.pending    = (data.pending    || []).filter(function(r){ return r.entity_type === 'ad_group'; });
        AG_REC.monitoring = (data.monitoring || []).filter(function(r){ return r.entity_type === 'ad_group'; });
        AG_REC.successful = (data.successful || []).filter(function(r){ return r.entity_type === 'ad_group'; });
        var hist = (data.declined || []).concat(data.reverted || []).filter(function(r){ return r.entity_type === 'ad_group'; });
        hist.sort(function(a,b){ return new Date(b.resolved_at||b.accepted_at||0) - new Date(a.resolved_at||a.accepted_at||0); });
        AG_REC.history = hist;
        AG_SEL = {};
        agRecRenderAll();
      })
      .catch(function(err) { console.error('agRecLoad error', err); });
  }
  window.agRecExp = function(evt, id) {
    if (evt.target.type === 'checkbox' || evt.target.tagName === 'BUTTON') return;
    var row = document.getElementById('exp-' + id);
    if (row) row.classList.toggle('open');
  };
  window.agRecCbChange = function(chk, id) {
    if (chk.checked) AG_SEL[id] = true; else delete AG_SEL[id];
    updateBulkBar();
  };
  window.agToggleAll = function(chk) {
    var page = AG_PAGE.pending;
    var start = (page - 1) * AG_PER_PAGE;
    var slice = AG_REC.pending.slice(start, start + AG_PER_PAGE);
    slice.forEach(function(r) { if (chk.checked) AG_SEL[r.rec_id] = true; else delete AG_SEL[r.rec_id]; });
    renderTab('pending');
    updateBulkBar();
  };
  window.agClearSelection = function() {
    AG_SEL = {};
    var master = document.getElementById('ag-chk-all');
    if (master) master.checked = false;
    renderTab('pending');
    updateBulkBar();
  };
  function updateBulkBar() {
    var count = Object.keys(AG_SEL).length;
    var bar = document.getElementById('ag-bulk-bar');
    var lbl = document.getElementById('ag-bulk-count');
    if (bar) bar.style.display = count > 0 ? 'flex' : 'none';
    if (lbl) lbl.textContent = count + ' selected';
  }
  window.agRecAccept = function(recId, btn) {
    btn.disabled = true; btn.textContent = '...';
    fetch('/recommendations/' + recId + '/accept', { method:'POST', headers:{'Content-Type':'application/json','X-CSRFToken': getCSRFToken()} })
      .then(function(r){ return r.json(); })
      .then(function(d){
        if (d.success) {
          AG_REC.pending = AG_REC.pending.filter(function(r){ return r.rec_id !== recId; });
          delete AG_SEL[recId];
          agRecRenderAll();
          agShowToast('Recommendation accepted', 'success');
        } else { agShowToast(d.message || 'Failed', 'error'); btn.disabled=false; btn.textContent='Accept'; }
      })
      .catch(function(){ agShowToast('Error', 'error'); btn.disabled=false; btn.textContent='Accept'; });
  };
  window.agRecDecline = function(recId, btn) {
    btn.disabled = true; btn.textContent = '...';
    fetch('/recommendations/' + recId + '/decline', { method:'POST', headers:{'Content-Type':'application/json','X-CSRFToken': getCSRFToken()} })
      .then(function(r){ return r.json(); })
      .then(function(d){
        if (d.success) {
          AG_REC.pending = AG_REC.pending.filter(function(r){ return r.rec_id !== recId; });
          delete AG_SEL[recId];
          agRecRenderAll();
          agShowToast('Recommendation declined', 'success');
        } else { agShowToast(d.message || 'Failed', 'error'); btn.disabled=false; btn.textContent='Decline'; }
      })
      .catch(function(){ agShowToast('Error', 'error'); btn.disabled=false; btn.textContent='Decline'; });
  };
  window.agDoBulk = function(action) {
    var ids = Object.keys(AG_SEL);
    if (!ids.length) return;
    var done = 0;
    ids.forEach(function(id) {
      fetch('/recommendations/' + id + '/' + action, { method:'POST', headers:{'Content-Type':'application/json','X-CSRFToken': getCSRFToken()} })
        .then(function(r){ return r.json(); })
        .then(function(d){
          if (d.success) AG_REC.pending = AG_REC.pending.filter(function(r){ return r.rec_id !== id; });
          done++;
          if (done === ids.length) { AG_SEL = {}; agRecRenderAll(); agShowToast('Done', 'success'); }
        });
    });
  };
  document.addEventListener('DOMContentLoaded', function() {
    var runBtn = document.getElementById('ag-run-engine-btn');
    if (runBtn) {
      runBtn.addEventListener('click', function() {
        var self = this;
        self.disabled = true;
        self.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Running...';
        fetch('/recommendations/run', { method:'POST', headers:{'X-CSRFToken': getCSRFToken()} })
          .then(function(r){ return r.json(); })
          .then(function(d){ agShowToast(d.message || 'Engine started', 'success'); setTimeout(agRecLoad, 2000); })
          .catch(function(){ agShowToast('Error', 'error'); })
          .finally(function(){ self.disabled=false; self.innerHTML='<i class="bi bi-play-circle"></i> Run engine'; });
      });
    }
    var lrBtn = document.getElementById('ag-accept-low-risk-btn');
    if (lrBtn) {
      lrBtn.addEventListener('click', function() {
        var lowRisk = AG_REC.pending.filter(function(r){ return r.risk_level === 'low'; });
        if (!lowRisk.length) { agShowToast('No low-risk recommendations pending', 'info'); return; }
        lowRisk.forEach(function(r) { AG_SEL[r.rec_id] = true; });
        window.agDoBulk('accept');
      });
    }
    var recTabBtn = document.getElementById('recommendations-tab-btn');
    if (recTabBtn) {
      recTabBtn.addEventListener('shown.bs.tab', agRecLoad);
    }
  });
  window.agRecLoad = agRecLoad;
})();"""

with open('C:/Users/User/Desktop/gads-data-layer/act_dashboard/templates/ad_groups.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_block_start = '// Fetch recommendations from server\nasync function agFetchRecommendations()'
old_block_end_marker = "        this.innerHTML = '<i class=\"bi bi-play-circle\"></i> Run Recommendations Now';\n        });\n    });\n  }\n});"

s = content.find(old_block_start)
e = content.find(old_block_end_marker)
if s == -1 or e == -1:
    print('MARKERS NOT FOUND', s, e)
else:
    end_pos = e + len(old_block_end_marker)
    new_content = content[:s] + NEW_JS + content[end_pos:]
    with open('C:/Users/User/Desktop/gads-data-layer/act_dashboard/templates/ad_groups.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('Done. Lines:', new_content.count('\n'))
