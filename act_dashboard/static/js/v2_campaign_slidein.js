/* ============================================================================
   ACT v2 — Campaign Detail Slide-in
   800px right-aligned panel. Opens via window.openCampaignSlidein(clientId, campaignId).
   Reusable on /v2/account today, /v2/campaigns later.
   ============================================================================ */
(function() {
  'use strict';

  const LEVER_NAMES = {
    device_mod: { label: 'Device modifiers', icon: 'devices' },
    geo_mod:    { label: 'Geographic modifiers', icon: 'location_on' },
    schedule_mod: { label: 'Ad schedule modifiers', icon: 'schedule' },
  };

  let trendChart = null;

  function el(id) { return document.getElementById(id); }
  function fmtGBP(v) { return '£' + Number(v).toLocaleString(undefined, { maximumFractionDigits: 2 }); }
  function fmtInt(v) { return Number(v).toLocaleString(); }

  function renderHeader(c) {
    const name = el('campSlideinName');
    const meta = el('campSlideinMeta');
    if (name) name.textContent = c.name;
    if (!meta) return;
    const roleBadge = c.role
      ? `<span class="role-badge role-badge--${c.role.toLowerCase()}">${c.role}</span>`
      : '';
    meta.innerHTML =
      `<span style="font-size:14px;color:var(--act-text)"><span class="status-dot status-dot--${c.status}"></span> ${c.status.charAt(0).toUpperCase() + c.status.slice(1)}</span>` +
      `<span class="strategy-badge">${c.bid_strategy}</span>` +
      roleBadge +
      `<span style="font-size:14px;font-weight:600;color:var(--act-text)">£${fmtInt(c.daily_budget)}/day</span>`;
  }

  function renderHealth(h) {
    let cpaBlock = '<div class="camp-health-card__value">&mdash;</div><div class="camp-health-card__detail">No conversions yet</div>';
    if (h.cpa != null) {
      const colour = h.cpa_zone === 'outperforming' ? '#10b981' : h.cpa_zone === 'underperforming' ? '#ef4444' : 'var(--act-text)';
      const zoneHtml = h.cpa_zone ? `<span class="zone-badge zone-badge--${h.cpa_zone}">${h.cpa_detail}</span>` : '';
      cpaBlock = `<div class="camp-health-card__value" style="color:${colour}">${fmtGBP(h.cpa)}</div><div class="camp-health-card__detail">${zoneHtml}${h.target_cpa ? ' vs target £' + h.target_cpa : ''}</div>`;
    }
    const convDetail = h.projected_conv != null ? `Projected: ${h.projected_conv}` : '';
    const qsVal = h.qs_avg != null ? h.qs_avg.toFixed(1) + '/10' : '&mdash;';
    return `<div class="camp-health-grid">
      <div class="camp-health-card"><div class="camp-health-card__label">Cost (MTD)</div><div class="camp-health-card__value">${fmtGBP(h.cost_mtd)}</div></div>
      <div class="camp-health-card"><div class="camp-health-card__label">CPA</div>${cpaBlock}</div>
      <div class="camp-health-card"><div class="camp-health-card__label">Conversions (MTD)</div><div class="camp-health-card__value">${fmtInt(h.conversions_mtd)}</div><div class="camp-health-card__detail">${convDetail}</div></div>
      <div class="camp-health-card"><div class="camp-health-card__label">QS Average</div><div class="camp-health-card__value">${qsVal}</div></div>
    </div>`;
  }

  function renderScore(s) {
    const colour = s.current > 0 ? '#10b981' : s.current < 0 ? '#ef4444' : 'var(--act-text)';
    const sign = s.current > 0 ? '+' : '';
    const WINDOW_LABEL = { '7d': '7-day', '14d': '14-day', '30d': '30-day' };
    let rowsHtml = '';
    s.breakdown.forEach(row => {
      const pts = row.points;
      const pSign = pts > 0 ? '+' : '';
      const barColour = pts >= 0 ? '#10b981' : '#ef4444';
      const barWidth = Math.min(Math.abs(pts), 100);
      const windowKey = row.window || (row.label.match(/(\d+)-day/) || [])[1];
      const winLabel = (row.label.match(/(\d+-day)/) || ['', ''])[1] || row.label;
      const metric = row.metric != null ? (row.metric_unit === '£' ? '£' + row.metric : row.metric + row.metric_unit) : '—';
      rowsHtml += `<div class="score-breakdown__row" style="padding:6px 0">
        <span class="score-breakdown__label">${winLabel}</span>
        <span style="font-size:12px;color:var(--act-text);min-width:60px">${metric}</span>
        <div class="score-breakdown__bar"><div class="score-breakdown__fill" style="width:${barWidth}%;background:${barColour}"></div></div>
        <span class="score-breakdown__pts" style="color:${pts > 0 ? '#10b981' : pts < 0 ? '#ef4444' : 'var(--act-text)'}">${pSign}${pts} pts</span>
      </div>`;
    });
    return `<div class="slidein-section">
      <div class="slidein-section__header"><span class="material-symbols-outlined" style="font-size:20px;color:#3b82f6">scoreboard</span><span style="font-size:16px;font-weight:600">Score Breakdown</span><span class="material-symbols-outlined slidein-section__toggle">expand_more</span></div>
      <div class="slidein-section__body"><div style="padding:14px 20px">
        <div style="display:flex;align-items:baseline;gap:12px;margin-bottom:12px">
          <div style="font-size:32px;font-weight:700;color:${colour}">${sign}${s.current}</div>
          <div style="font-size:13px;color:var(--act-text);opacity:0.8">${s.interpretation}</div>
        </div>
        ${rowsHtml}
      </div></div>
    </div>`;
  }

  function renderBudgetPosition(b, pendingShift, proposed) {
    if (!b) {
      return `<div class="slidein-section collapsed">
        <div class="slidein-section__header"><span class="material-symbols-outlined" style="font-size:20px;color:#3b82f6">account_balance</span><span style="font-size:16px;font-weight:600">Budget Position</span><span class="material-symbols-outlined slidein-section__toggle">expand_more</span></div>
        <div class="slidein-section__body"><div style="padding:14px 20px;font-size:13px;color:var(--act-text);opacity:0.7">No role assigned — budget bands not applied.</div></div>
      </div>`;
    }
    const statusLabel = s => s === 'in_band' ? 'Within band' : s === 'over_band' ? 'Over band' : 'Under band';
    const statusColour = s => s === 'in_band' ? '#10b981' : s === 'over_band' ? '#ef4444' : '#f59e0b';
    const dotPos = Math.max(0, Math.min(100, b.current_pct));
    const propPos = proposed ? Math.max(0, Math.min(100, proposed.pct)) : null;
    const proposedRow = proposed ? `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
        <div style="font-size:14px"><strong>If approved: ${fmtGBP(proposed.mtd)}</strong> MTD (${proposed.pct}% of total)</div>
        <span style="font-size:12px;font-weight:600;padding:2px 8px;border-radius:10px;color:white;background:${statusColour(proposed.status)}">${statusLabel(proposed.status)}</span>
      </div>` : '';
    const ghostMarker = propPos != null ? `<div style="position:absolute;left:${propPos}%;top:-3px;width:16px;height:16px;border-radius:50%;background:transparent;border:2px dashed ${statusColour(proposed.status)};transform:translateX(-50%)" title="If approved"></div>` : '';
    return `<div class="slidein-section">
      <div class="slidein-section__header"><span class="material-symbols-outlined" style="font-size:20px;color:#3b82f6">account_balance</span><span style="font-size:16px;font-weight:600">Budget Position</span><span class="material-symbols-outlined slidein-section__toggle">expand_more</span></div>
      <div class="slidein-section__body"><div style="padding:14px 20px">
        <div style="font-size:13px;margin-bottom:8px"><strong>${b.role} (${b.role_label}):</strong> ${b.band_min_pct}–${b.band_max_pct}% of ${fmtGBP(b.monthly_budget_total)}/mo = ${fmtGBP(b.band_min_abs)}–${fmtGBP(b.band_max_abs)}/mo</div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
          <div style="font-size:14px"><strong>Current: ${fmtGBP(b.current_mtd)}</strong> MTD (${b.current_pct}% of total)</div>
          <span style="font-size:12px;font-weight:600;padding:2px 8px;border-radius:10px;color:white;background:${statusColour(b.status)}">${statusLabel(b.status)}</span>
        </div>
        ${proposedRow}
        <div style="position:relative;height:10px;background:var(--act-border-light);border-radius:5px;margin-bottom:8px">
          <div style="position:absolute;left:${b.band_min_pct}%;width:${b.band_max_pct - b.band_min_pct}%;top:0;bottom:0;background:var(--act-blue-bg);border-radius:5px"></div>
          <div style="position:absolute;left:${dotPos}%;top:-3px;width:16px;height:16px;border-radius:50%;background:${statusColour(b.status)};transform:translateX(-50%);border:2px solid white;box-shadow:0 1px 3px rgba(0,0,0,0.2)"></div>
          ${ghostMarker}
        </div>
        ${pendingShift ? `<div style="padding:10px;background:var(--act-blue-bg);border-left:3px solid var(--act-primary);font-size:13px;margin-top:8px"><span class="material-symbols-outlined" style="font-size:16px;vertical-align:middle">lightbulb</span> Pending: ${pendingShift}</div>` : ''}
      </div></div>
    </div>`;
  }

  function renderTrendSection() {
    return `<div class="slidein-section">
      <div class="slidein-section__header"><span class="material-symbols-outlined" style="font-size:20px;color:#3b82f6">trending_up</span><span style="font-size:16px;font-weight:600">8-Week Trend</span><span class="material-symbols-outlined slidein-section__toggle">expand_more</span></div>
      <div class="slidein-section__body"><div style="padding:14px 20px">
        <div style="height:200px"><canvas id="campTrendChart"></canvas></div>
      </div></div>
    </div>`;
  }

  function buildTrendChart(trend) {
    const canvas = document.getElementById('campTrendChart');
    if (!canvas || typeof Chart === 'undefined') return;
    if (trendChart) trendChart.destroy();
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#ffffff' : '#000000';
    const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';
    trendChart = new Chart(canvas, {
      type: 'line',
      data: {
        labels: trend.labels,
        datasets: [
          { label: 'Cost', data: trend.cost, borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.08)', fill: true, tension: 0, pointRadius: 3, borderWidth: 2, yAxisID: 'y1' },
          { label: 'Conversions', data: trend.conversions, borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.08)', fill: true, tension: 0, pointRadius: 3, borderWidth: 2, yAxisID: 'y2' },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { color: textColor, font: { size: 11 } } },
          y1: { position: 'left', title: { display: true, text: 'Cost (£)', color: '#3b82f6' }, grid: { color: gridColor }, ticks: { color: textColor, callback: v => '£' + v } },
          y2: { position: 'right', title: { display: true, text: 'Conversions', color: '#10b981' }, grid: { drawOnChartArea: false }, ticks: { color: textColor } },
        },
      },
    });
  }

  function renderList(title, icon, iconColour, badgeColour, items, emptyMsg, fmtItem, collapsed) {
    if (!items || !items.length) {
      if (!emptyMsg) return '';
      return `<div class="slidein-section ${collapsed ? 'collapsed' : ''}">
        <div class="slidein-section__header"><span class="material-symbols-outlined" style="font-size:20px;color:${iconColour}">${icon}</span><span style="font-size:16px;font-weight:600">${title}</span><span class="material-symbols-outlined slidein-section__toggle">expand_more</span></div>
        <div class="slidein-section__body"><div style="padding:12px;font-size:13px;color:var(--act-text);opacity:0.7">${emptyMsg}</div></div>
      </div>`;
    }
    const rows = items.map(fmtItem).join('');
    const count = `<span style="font-size:12px;font-weight:600;padding:2px 8px;border-radius:10px;color:white;background:${badgeColour}">${items.length}</span>`;
    return `<div class="slidein-section ${collapsed ? 'collapsed' : ''}">
      <div class="slidein-section__header"><span class="material-symbols-outlined" style="font-size:20px;color:${iconColour}">${icon}</span><span style="font-size:16px;font-weight:600">${title}</span>${count}<span class="material-symbols-outlined slidein-section__toggle">expand_more</span></div>
      <div class="slidein-section__body">${rows}</div>
    </div>`;
  }

  function fmtApproval(a) {
    const summary = a.perspective || a.summary;
    return `<div class="act-item" data-rec-id="${a.id}"><div class="act-item__row"><div class="act-item__content">
      <div class="act-item__top"><span class="badge-action badge-action--${a.action_category}">${a.action_category.charAt(0).toUpperCase() + a.action_category.slice(1)}</span><span class="badge-risk badge-risk--${a.risk_level}">${a.risk_level.charAt(0).toUpperCase() + a.risk_level.slice(1)} Risk</span></div>
      <div class="act-item__summary">${summary}</div>
      ${a.recommendation_text ? `<div class="act-item__recommendation"><span class="material-symbols-outlined">lightbulb</span>${a.recommendation_text}</div>` : ''}
      ${a.estimated_impact ? `<div class="act-item__impact"><span class="material-symbols-outlined">trending_up</span>${a.estimated_impact}</div>` : ''}
    </div>
    <div class="act-item__actions">
      <button class="btn-act btn-act--approve" data-action="approve" data-rec-id="${a.id}">Approve</button>
      <button class="btn-act btn-act--decline" data-action="decline" data-rec-id="${a.id}">Decline</button>
    </div></div></div>`;
  }

  function fmtExecuted(e) {
    const ts = e.executed_at ? e.executed_at.slice(0, 16) : '';
    return `<div class="act-item"><div class="act-item__row"><div class="act-item__content">
      <div class="act-item__top"><span class="badge-action badge-action--act">Act</span><span class="act-item__timestamp">${ts}</span></div>
      <div class="act-item__summary">${e.action_type}${e.reason ? ' &mdash; ' + e.reason : ''}</div>
    </div></div></div>`;
  }

  function fmtMonitoring(m) {
    const healthLabel = m.health === 'healthy' ? 'Healthy' : m.health === 'trending_down' ? 'Trending Down' : 'Too early to assess';
    const healthClass = m.health === 'healthy' ? 'healthy' : m.health === 'trending_down' ? 'warning' : 'neutral';
    return `<div class="act-item"><div class="act-item__row"><div class="act-item__content">
      <div class="act-item__top"><span class="badge-action badge-action--monitor">Monitor</span></div>
      <div class="act-item__summary">${m.type.replace(/_/g, ' ')}</div>
      <div class="act-item__started"><span class="material-symbols-outlined">calendar_today</span>Started: ${m.started_at.slice(0, 10)}</div>
      <div><span class="health-label health-label--${healthClass}">${healthLabel}</span></div>
    </div></div></div>`;
  }

  function fmtAlert(a) {
    return `<div class="act-item"><div class="act-item__row"><div class="act-item__content">
      <div class="act-item__top"><span class="badge-action badge-action--alert">Alert</span><span class="act-item__timestamp">${a.raised_at.slice(0, 10)}</span></div>
      <div class="act-item__summary"><strong>${a.title}</strong>${a.description ? ' &mdash; ' + a.description : ''}</div>
    </div></div></div>`;
  }

  function leverRow(icon, name, status, detailHtml, guardrail) {
    const guardHtml = guardrail ? `<div class="lever-guardrail-note"><span class="material-symbols-outlined">shield</span><span class="lever-guardrail-note__text">${guardrail}</span></div>` : '';
    return `<div class="lever-summary-row">
      <div class="lever-summary-row__header">
        <span class="material-symbols-outlined">${icon}</span>
        <div style="flex:1"><div class="lever-summary__name">${name}</div><div class="lever-summary__status">${status}</div></div>
        <span class="material-symbols-outlined lever-summary__chevron">chevron_right</span>
      </div>
      <div class="lever-summary__detail">${detailHtml}${guardHtml}</div>
    </div>`;
  }

  function miniTable(cols, rows) {
    if (!rows || !rows.length) return '<div style="font-size:13px;color:var(--act-text);opacity:0.6;padding:8px 0">No data yet.</div>';
    const head = '<thead><tr>' + cols.map(c => `<th>${c}</th>`).join('') + '</tr></thead>';
    const body = '<tbody>' + rows.map(r => '<tr>' + r.map(c => `<td>${c}</td>`).join('') + '</tr>').join('') + '</tbody>';
    return `<table class="lever-mini-table">${head}${body}</table>`;
  }

  function matchBar(dist) {
    if (!dist || (!dist.BROAD && !dist.PHRASE && !dist.EXACT)) {
      return '<div style="font-size:13px;color:var(--act-text);opacity:0.6;padding:8px 0">No match-type data.</div>';
    }
    const total = (dist.BROAD || 0) + (dist.PHRASE || 0) + (dist.EXACT || 0);
    const pct = v => total > 0 ? Math.round(v / total * 100) : 0;
    const b = pct(dist.BROAD || 0), p = pct(dist.PHRASE || 0), e = pct(dist.EXACT || 0);
    return `<div class="slidein-match-bar">
      ${b > 0 ? `<div class="slidein-match-bar__segment" style="width:${b}%;background:#ef4444">${b}%</div>` : ''}
      ${p > 0 ? `<div class="slidein-match-bar__segment" style="width:${p}%;background:#f59e0b">${p}%</div>` : ''}
      ${e > 0 ? `<div class="slidein-match-bar__segment" style="width:${e}%;background:#10b981">${e}%</div>` : ''}
    </div>
    <div class="slidein-match-legend">
      <span><span class="slidein-match-legend__dot" style="background:#ef4444"></span>Broad (${b}%)</span>
      <span><span class="slidein-match-legend__dot" style="background:#f59e0b"></span>Phrase (${p}%)</span>
      <span><span class="slidein-match-legend__dot" style="background:#10b981"></span>Exact (${e}%)</span>
    </div>`;
  }

  function renderLevers(levers) {
    const dev = levers.device || {};
    const geo = levers.geo || {};
    const sched = levers.schedule || {};
    const devGuard = `Caps: ${levers.device_caps?.min ?? '—'}% / +${levers.device_caps?.max ?? '—'}% · Cooldown: ${levers.device_caps?.cooldown ?? '—'} days`;
    const geoGuard = `Caps: ${levers.geo_caps?.min ?? '—'}% / +${levers.geo_caps?.max ?? '—'}% · Cooldown: ${levers.geo_caps?.cooldown ?? '—'} days`;
    const schedGuard = `Caps: ${levers.schedule_caps?.min ?? '—'}% / +${levers.schedule_caps?.max ?? '—'}% · Cooldown: ${levers.schedule_caps?.cooldown ?? '—'} days`;

    const devRows = (dev.rows || []).map(r => [r.device, fmtGBP(r.cost), r.cpa != null ? fmtGBP(r.cpa) : '—', r.conv, r.ctr + '%']);
    const geoRows = (geo.rows || []).map(r => [r.location, fmtGBP(r.cost), r.cpa != null ? fmtGBP(r.cpa) : '—', r.conv]);
    const schedRows = (sched.rows || []).map(r => [r.slot, fmtGBP(r.cost), r.cpa != null ? fmtGBP(r.cpa) : '—', r.conv]);

    const devStatus = (dev.rows?.length || 0) + ' devices';
    const geoStatus = (geo.rows?.length || 0) + ' locations';
    const schedStatus = (sched.rows?.length || 0) + ' time slots';

    const negTotal = (levers.negatives?.total || 0);
    const negLists = (levers.negatives?.lists || 0);
    const negStatus = negTotal + ' across ' + negLists + ' lists';
    const negDetail = `<div style="font-size:14px;color:var(--act-text);padding:8px 0">${negTotal} negative keywords across ${negLists} standardised lists. ACT adds <strong>[exact]</strong> match only. Phrase match is human-managed. Managed at Keyword Level.</div>`;

    const md = levers.match_dist || {};
    const mdTotal = (md.BROAD || 0) + (md.PHRASE || 0) + (md.EXACT || 0);
    const mdStatus = mdTotal > 0
      ? `Broad ${Math.round((md.BROAD||0)/mdTotal*100)}% · Phrase ${Math.round((md.PHRASE||0)/mdTotal*100)}% · Exact ${Math.round((md.EXACT||0)/mdTotal*100)}%`
      : 'No data';

    let rows = '';
    rows += leverRow('devices', 'Device Modifiers', devStatus, miniTable(['Device', 'Cost', 'CPA', 'Conv', 'CTR'], devRows), devGuard);
    rows += leverRow('location_on', 'Geographic Modifiers', geoStatus, miniTable(['Location', 'Cost', 'CPA', 'Conv'], geoRows), geoGuard);
    rows += leverRow('schedule', 'Ad Schedule', schedStatus, miniTable(['Day/Hour', 'Cost', 'CPA', 'Conv'], schedRows), schedGuard);
    rows += leverRow('block', 'Negative Keywords', negStatus, negDetail, 'ACT adds [exact] match only · Phrase match is human-managed');
    rows += leverRow('sort_by_alpha', 'Match Types', mdStatus, matchBar(md), 'Changes require approval · Managed at Keyword Level');

    return `<div class="slidein-section collapsed">
      <div class="slidein-section__header"><span class="material-symbols-outlined" style="font-size:20px;color:#10b981">tune</span><span style="font-size:16px;font-weight:600">Universal Levers</span><span class="material-symbols-outlined slidein-section__toggle">expand_more</span></div>
      <div class="slidein-section__body"><div class="lever-summary">${rows}</div></div>
    </div>`;
  }

  function renderBidStrategy(c, h) {
    return `<div class="slidein-section collapsed">
      <div class="slidein-section__header"><span class="material-symbols-outlined" style="font-size:20px;color:#10b981">target</span><span style="font-size:16px;font-weight:600">Bid Strategy</span><span class="material-symbols-outlined slidein-section__toggle">expand_more</span></div>
      <div class="slidein-section__body" style="padding:16px">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
          <div class="slidein-strategy__value">${c.bid_strategy}</div>
          ${h.cpa_zone ? `<span class="zone-badge zone-badge--${h.cpa_zone}">${h.cpa_detail}</span>` : ''}
        </div>
        <div class="lever-guardrail-note" style="margin-top:12px"><span class="material-symbols-outlined">shield</span><span class="lever-guardrail-note__text">Max 10% per cycle · 14-day cooldown · Loosening requires approval</span></div>
      </div>
    </div>`;
  }

  function render(data) {
    renderHeader(data.campaign);
    const body = el('campSlideinBody');
    if (!body) return;

    let html = '';
    // Section order: state → performance → reviews → budget → knobs
    html += renderHealth(data.health);
    html += renderTrendSection();
    html += renderList('Awaiting Approval', 'pending_actions', 'var(--act-amber)', 'var(--act-amber)',
                      data.awaiting, 'No pending recommendations for this campaign.', fmtApproval, false);
    html += renderList('Actions Executed Overnight', 'check_circle', 'var(--act-green)', 'var(--act-green)',
                      data.executed, 'No actions executed in the last 24h.', fmtExecuted, true);
    html += renderList('Currently Monitoring', 'visibility', 'var(--act-blue)', 'var(--act-blue)',
                      data.monitoring, 'No active monitoring.', fmtMonitoring, true);
    html += renderList('Recent Alerts', 'notifications_active', 'var(--act-red)', 'var(--act-red)',
                      data.alerts, 'No alerts in last 7 days.', fmtAlert, true);
    html += renderScore(data.score);
    html += renderBudgetPosition(data.budget_position, data.pending_shift, data.budget_proposed);
    html += renderLevers(data.levers);
    html += renderBidStrategy(data.campaign, data.health);

    body.innerHTML = html;

    buildTrendChart(data.trend);

    // Collapse toggles
    body.querySelectorAll('.slidein-section__header').forEach(h => {
      h.addEventListener('click', () => h.closest('.slidein-section').classList.toggle('collapsed'));
    });

    // Lever row expand (click header toggles detail)
    body.querySelectorAll('.lever-summary-row__header').forEach(h => {
      h.addEventListener('click', () => h.closest('.lever-summary-row').classList.toggle('expanded'));
    });
  }

  function open(overlay, panel) {
    overlay && overlay.classList.add('open');
    panel && panel.classList.add('open');
  }
  function close() {
    const overlay = el('campSlideinOverlay');
    const panel = el('campSlidein');
    overlay && overlay.classList.remove('open');
    panel && panel.classList.remove('open');
  }

  window.openCampaignSlidein = function(clientId, campaignId) {
    const overlay = el('campSlideinOverlay');
    const panel = el('campSlidein');
    const body = el('campSlideinBody');
    if (!panel) return;
    body.innerHTML = '<div style="padding:40px;text-align:center;color:var(--act-text);opacity:0.6">Loading…</div>';
    open(overlay, panel);
    fetch(`/v2/api/account/campaign-slidein/${encodeURIComponent(clientId)}/${encodeURIComponent(campaignId)}`)
      .then(r => r.json())
      .then(data => {
        if (!data.success) {
          body.innerHTML = `<div style="padding:40px;text-align:center;color:var(--act-red)">Error: ${data.error || 'unknown'}</div>`;
          return;
        }
        render(data);
      })
      .catch(err => {
        body.innerHTML = `<div style="padding:40px;text-align:center;color:var(--act-red)">Load failed: ${err.message}</div>`;
      });
  };
  window.closeCampSlidein = close;

  document.addEventListener('DOMContentLoaded', () => {
    el('campSlideinOverlay')?.addEventListener('click', close);
    el('campSlideinClose')?.addEventListener('click', close);
    document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
  });
})();
