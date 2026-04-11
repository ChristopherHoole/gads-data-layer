/* ============================================================================
   ACT PROTOTYPE — AD GROUP LEVEL (Page 5)
   Chart, table, filters, slide-in, outlier analysis, structural health.
   ============================================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ── Theme toggle ─────────────────────────────────────────────────────────
  const themeToggle = document.querySelector('.theme-toggle');
  if (themeToggle) {
    if (document.documentElement.getAttribute('data-theme') === 'dark') themeToggle.classList.add('night');
    themeToggle.addEventListener('click', () => {
      const html = document.documentElement;
      const goingDark = html.getAttribute('data-theme') === 'light';
      themeToggle.classList.add('transitioning');
      if (goingDark) themeToggle.classList.add('night'); else themeToggle.classList.remove('night');
      setTimeout(() => html.setAttribute('data-theme', goingDark ? 'dark' : 'light'), 400);
      setTimeout(() => themeToggle.classList.remove('transitioning'), 1000);
    });
  }

  // ── Client switcher ──────────────────────────────────────────────────────
  const clientBtn = document.getElementById('clientSwitcher');
  const clientMenu = document.getElementById('clientMenu');
  if (clientBtn && clientMenu) {
    clientBtn.addEventListener('click', (e) => { e.stopPropagation(); clientMenu.classList.toggle('show'); });
    document.addEventListener('click', () => clientMenu.classList.remove('show'));
    clientMenu.querySelectorAll('.dropdown-item').forEach(item => {
      item.addEventListener('click', () => {
        clientBtn.querySelector('.client-name').textContent = item.textContent.trim();
        clientMenu.querySelectorAll('.dropdown-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        clientMenu.classList.remove('show');
        showToast(`Switched to ${item.textContent.trim()}`, 'info');
      });
    });
  }

  // ── Section collapse (both acct-section and act-section) ────────────────
  document.querySelectorAll('.acct-section__header, .act-section__header').forEach(header => {
    header.addEventListener('click', (e) => {
      if (e.target.closest('.table-toolbar')) return;
      const section = header.closest('.acct-section') || header.closest('.act-section');
      if (section) section.classList.toggle('collapsed');
    });
  });

  // ── Group collapse ───────────────────────────────────────────────────────
  document.querySelectorAll('.act-group__header').forEach(header => {
    header.addEventListener('click', (e) => { e.stopPropagation(); header.closest('.act-group').classList.toggle('collapsed'); });
  });

  // ── Table sorting ────────────────────────────────────────────────────────
  document.querySelectorAll('.data-table th[data-sort]').forEach(th => {
    th.addEventListener('click', () => {
      const table = th.closest('table');
      const tbody = table.querySelector('tbody');
      const rows = Array.from(tbody.querySelectorAll('tr:not(.totals-row)'));
      const totals = tbody.querySelector('tr.totals-row');
      const idx = Array.from(th.parentElement.children).indexOf(th);
      const asc = th.dataset.dir !== 'asc';
      th.dataset.dir = asc ? 'asc' : 'desc';
      table.querySelectorAll('th').forEach(h => { if (h !== th) delete h.dataset.dir; });
      rows.sort((a, b) => {
        let va = a.children[idx]?.textContent.trim().replace(/[£%,]/g, '') || '';
        let vb = b.children[idx]?.textContent.trim().replace(/[£%,]/g, '') || '';
        const na = parseFloat(va), nb = parseFloat(vb);
        if (!isNaN(na) && !isNaN(nb)) return asc ? na - nb : nb - na;
        return asc ? va.localeCompare(vb) : vb.localeCompare(va);
      });
      rows.forEach(r => tbody.appendChild(r));
      if (totals) tbody.appendChild(totals);
    });
  });

  // ── Pill buttons (date range + status filter) ───────────────────────────
  document.querySelectorAll('.pill-group').forEach(group => {
    group.querySelectorAll('.pill-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        group.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        if (btn.dataset.range) {
          currentRange = btn.dataset.range;
          const days = currentRange === '7d' ? '7' : currentRange === '30d' ? '30' : '90';
          const ctx = document.getElementById('perfContext');
          if (ctx) ctx.textContent = `— 18 ad groups, ${days} days`;
          buildChart();
          updateTable(currentRange);
          showToast(`Showing ${btn.textContent.trim()} data`, 'info');
        }
        if (btn.dataset.filter) filterAdGroups(btn.dataset.filter);
      });
    });
  });

  function filterAdGroups(filter) {
    document.querySelectorAll('#adGroupsTable tbody tr').forEach(row => {
      if (row.classList.contains('totals-row')) return;
      if (filter === 'all') { row.style.display = ''; return; }
      const status = row.dataset.status;
      row.style.display = (status === filter) ? '' : 'none';
    });
  }

  // ── Approve / Decline / Undo ─────────────────────────────────────────────
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-action="approve"], [data-action="decline"], [data-action="undo"]');
    if (!btn) return;
    e.stopPropagation();
    const item = btn.closest('.act-item');
    if (item) { item.style.opacity = '0.4'; item.style.pointerEvents = 'none'; }
    if (btn.dataset.action === 'approve') showToast('Approved — change will be applied in next cycle', 'success');
    else if (btn.dataset.action === 'decline') showToast('Declined — no changes will be made', 'info');
    else showToast('Undo queued — will be reverted in next cycle', 'warning');
  });

  // ── Slide-in for "See Details" (decision tree) ──────────────────────────
  const slideinOverlay = document.getElementById('slideinOverlay');
  const slideinPanel = document.getElementById('slideinPanel');
  const slideinBody = document.getElementById('slideinBody');

  document.querySelectorAll('[data-action="details"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const item = btn.closest('.act-item');
      if (!item || !slideinPanel || !slideinBody) return;
      const agName = item.dataset.ag || 'Ad Group';
      // Instead of the small decision slide-in, open the full ad-group slide-in
      openAgSlidein(agName);
    });
  });

  window.closeSlidein = function() { slideinOverlay?.classList.remove('open'); slideinPanel?.classList.remove('open'); };
  slideinOverlay?.addEventListener('click', closeSlidein);
  document.getElementById('slideinClose')?.addEventListener('click', closeSlidein);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') { closeSlidein(); closeAgSlidein(); } });

  // ═════════════════════════════════════════════════════════════════════════
  // PERFORMANCE TIMELINE CHART
  // ═════════════════════════════════════════════════════════════════════════

  let currentRange = '30d';

  function makeDailyLabels(days) {
    const labels = [];
    const d = new Date(2026, 3, 6);
    for (let i = days - 1; i >= 0; i--) {
      const dt = new Date(d); dt.setDate(d.getDate() - i);
      labels.push(dt.getDate() + ' ' + ['Jan','Feb','Mar','Apr','May'][dt.getMonth()]);
    }
    return labels;
  }
  function makeWeeklyLabels(weeks) {
    const labels = [];
    const d = new Date(2026, 3, 6);
    for (let i = weeks - 1; i >= 0; i--) {
      const dt = new Date(d); dt.setDate(d.getDate() - i * 7);
      labels.push(dt.getDate() + ' ' + ['Jan','Feb','Mar','Apr','May'][dt.getMonth()]);
    }
    return labels;
  }

  function seededData(base, variance, count, round) {
    const data = [];
    let v = base;
    for (let i = 0; i < count; i++) {
      v = base + (Math.sin(i * 1.7 + base * 0.1) * variance);
      data.push(round ? Math.round(v) : Math.round(v * 100) / 100);
    }
    return data;
  }

  const METRIC_DEFS = {
    cost:        { label: 'Cost',               prefix: '£', suffix: '' },
    impressions: { label: 'Impressions',         prefix: '',  suffix: '' },
    clicks:      { label: 'Clicks',              prefix: '',  suffix: '' },
    avgCpc:      { label: 'Avg CPC',             prefix: '£', suffix: '' },
    ctr:         { label: 'CTR',                 prefix: '',  suffix: '%' },
    conversions: { label: 'Conversions',         prefix: '',  suffix: '' },
    cpa:         { label: 'CPA (Cost/Conv)',     prefix: '£', suffix: '' },
    convRate:    { label: 'Conv Rate',           prefix: '',  suffix: '%' },
  };

  function getChartData(range) {
    if (range === '90d') {
      const n = 13;
      const labels = makeWeeklyLabels(n);
      const dailyCost = seededData(27, 8, 91, true);
      const dailyImpr = seededData(620, 120, 91, true);
      const dailyClicks = seededData(43, 10, 91, true);
      const dailyConv = seededData(1.4, 0.8, 91, true);
      const dailyCpc = seededData(0.63, 0.12, 91, false);
      const dailyCtr = seededData(6.9, 0.8, 91, false);
      const dailyCpa = seededData(19.5, 5, 91, false);
      const dailyCvr = seededData(3.3, 0.6, 91, false);
      function weeklySum(arr) { const r = []; for (let w = 0; w < n; w++) { let s = 0; for (let d = 0; d < 7 && w*7+d < arr.length; d++) s += arr[w*7+d]; r.push(Math.round(s)); } return r; }
      function weeklyAvg(arr) { const r = []; for (let w = 0; w < n; w++) { let s = 0, c = 0; for (let d = 0; d < 7 && w*7+d < arr.length; d++) { s += arr[w*7+d]; c++; } r.push(Math.round(s/c*100)/100); } return r; }
      return {
        labels,
        metrics: {
          cost: weeklySum(dailyCost), impressions: weeklySum(dailyImpr),
          clicks: weeklySum(dailyClicks), conversions: weeklySum(dailyConv),
          avgCpc: weeklyAvg(dailyCpc), ctr: weeklyAvg(dailyCtr),
          cpa: weeklyAvg(dailyCpa), convRate: weeklyAvg(dailyCvr),
        }
      };
    }
    const n = range === '7d' ? 7 : 30;
    const labels = makeDailyLabels(n);
    return {
      labels,
      metrics: {
        cost:        seededData(27, 8, n, true),
        impressions: seededData(620, 120, n, true),
        clicks:      seededData(43, 10, n, true),
        avgCpc:      seededData(0.63, 0.12, n, false),
        ctr:         seededData(6.9, 0.8, n, false),
        conversions: seededData(1.4, 0.8, n, true),
        cpa:         seededData(19.5, 5, n, false),
        convRate:    seededData(3.3, 0.6, n, false),
      }
    };
  }

  // ═════════════════════════════════════════════════════════════════════════
  // TABLE DATA PER DATE RANGE (18 ad groups across 4 campaigns)
  // ═════════════════════════════════════════════════════════════════════════

  function mkRows(scale) {
    // scale: 7d ≈ 0.25x of 30d, 90d ≈ 3x of 30d
    const base = [
      // GLO Campaign — Core (5 ad groups) — campaign total £487
      { name: 'Core Terms',         camp: 'GLO Campaign — Core', kw: 32, ads: 4, cost30: 194.80, impr30: 4340, clicks30: 312, cpc: 0.62, ctr: 7.19, conv30: 11, convRate: 3.53, flags: 0 },
      { name: 'Brand Defence',      camp: 'GLO Campaign — Core', kw: 12, ads: 3, cost30: 38.96,  impr30: 870,  clicks30: 62,  cpc: 0.63, ctr: 7.13, conv30: 3,  convRate: 4.84, flags: 0 },
      { name: 'Competitor Terms',   camp: 'GLO Campaign — Core', kw: 24, ads: 3, cost30: 73.05,  impr30: 1630, clicks30: 117, cpc: 0.62, ctr: 7.18, conv30: 2,  convRate: 1.71, flags: 1, flagType: 'negative' },
      { name: 'Long Tail',          camp: 'GLO Campaign — Core', kw: 48, ads: 4, cost30: 121.75, impr30: 2710, clicks30: 195, cpc: 0.62, ctr: 7.19, conv30: 9,  convRate: 4.62, flags: 1, flagType: 'positive' },
      { name: 'Retargeting Terms',  camp: 'GLO Campaign — Core', kw: 18, ads: 3, cost30: 58.44,  impr30: 1300, clicks30: 94,  cpc: 0.62, ctr: 7.23, conv30: 1,  convRate: 1.06, flags: 0 },
      // GLO Campaign — Retargeting (3 ad groups) — campaign total £164
      { name: 'Recent Visitors',    camp: 'GLO Campaign — Retargeting', kw: 15, ads: 3, cost30: 82.00,  impr30: 1600, clicks30: 122, cpc: 0.67, ctr: 7.62, conv30: 5, convRate: 4.10, flags: 0 },
      { name: 'Cart Abandoners',    camp: 'GLO Campaign — Retargeting', kw: 10, ads: 2, cost30: 49.20,  impr30: 960,  clicks30: 73,  cpc: 0.67, ctr: 7.60, conv30: 5, convRate: 6.85, flags: 1, flagType: 'positive' },
      { name: 'Past Customers',     camp: 'GLO Campaign — Retargeting', kw: 8,  ads: 2, cost30: 32.80,  impr30: 640,  clicks30: 50,  cpc: 0.66, ctr: 7.81, conv30: 2, convRate: 4.00, flags: 0 },
      // Brand — Objection Experts (4 ad groups) — campaign total £68
      { name: 'Main Brand Terms',   camp: 'Brand — Objection Experts', kw: 14, ads: 3, cost30: 47.60, impr30: 1960, clicks30: 136, cpc: 0.35, ctr: 6.94, conv30: 2, convRate: 1.47, flags: 0 },
      { name: 'Brand + Service',    camp: 'Brand — Objection Experts', kw: 9,  ads: 2, cost30: 10.20, impr30: 420,  clicks30: 29,  cpc: 0.35, ctr: 6.90, conv30: 1, convRate: 3.45, flags: 0 },
      { name: 'Brand + Location',   camp: 'Brand — Objection Experts', kw: 6,  ads: 2, cost30: 6.80,  impr30: 280,  clicks30: 20,  cpc: 0.34, ctr: 7.14, conv30: 0, convRate: 0,    flags: 0 },
      { name: 'Brand Misspellings', camp: 'Brand — Objection Experts', kw: 11, ads: 2, cost30: 3.40,  impr30: 140,  clicks30: 10,  cpc: 0.34, ctr: 7.14, conv30: 0, convRate: 0,    flags: 1, flagType: 'pause' },
      // Testing — New Keywords (6 ad groups) — campaign total £102
      { name: 'Test Batch 1',       camp: 'Testing — New Keywords', kw: 16, ads: 2, cost30: 20.40, impr30: 310, clicks30: 13, cpc: 1.57, ctr: 4.19, conv30: 0, convRate: 0,    flags: 0 },
      { name: 'Test Batch 2',       camp: 'Testing — New Keywords', kw: 14, ads: 2, cost30: 18.36, impr30: 280, clicks30: 11, cpc: 1.67, ctr: 3.93, conv30: 1, convRate: 9.09, flags: 0 },
      { name: 'Test Batch 3',       camp: 'Testing — New Keywords', kw: 15, ads: 2, cost30: 15.30, impr30: 240, clicks30: 10, cpc: 1.53, ctr: 4.17, conv30: 0, convRate: 0,    flags: 1, flagType: 'pause' },
      { name: 'Test Batch 4',       camp: 'Testing — New Keywords', kw: 13, ads: 2, cost30: 18.36, impr30: 280, clicks30: 11, cpc: 1.67, ctr: 3.93, conv30: 0, convRate: 0,    flags: 0 },
      { name: 'Test Batch 5',       camp: 'Testing — New Keywords', kw: 12, ads: 2, cost30: 15.30, impr30: 230, clicks30: 10, cpc: 1.53, ctr: 4.35, conv30: 0, convRate: 0,    flags: 0 },
      { name: 'Test Batch 6',       camp: 'Testing — New Keywords', kw: 11, ads: 2, cost30: 14.28, impr30: 220, clicks30: 9,  cpc: 1.59, ctr: 4.09, conv30: 0, convRate: 0,    flags: 0 },
    ];
    return base.map(r => ({
      ...r,
      cost: '£' + (r.cost30 * scale).toFixed(2),
      impr: Math.round(r.impr30 * scale).toLocaleString(),
      clicks: Math.round(r.clicks30 * scale).toLocaleString(),
      cpcStr: '£' + r.cpc.toFixed(2),
      ctrStr: r.ctr.toFixed(2) + '%',
      conv: Math.round(r.conv30 * scale),
      costconv: r.conv30 * scale < 1 ? '—' : '£' + (r.cost30 * scale / (r.conv30 * scale)).toFixed(2),
      cvrStr: r.convRate > 0 ? r.convRate.toFixed(2) + '%' : '0.00%',
    }));
  }

  const TABLE_DATA = {
    '7d':  mkRows(7/30),
    '30d': mkRows(1),
    '90d': mkRows(3),
  };

  const SUMMARY_DATA = {
    '7d':  { cost: '£211', impr: '4,600', clicks: '320', cpc: '£0.66', ctr: '6.97%', conv: '11', cpa: '£19.18', cvr: '3.44%',
             costChg: '↑ 8%', imprChg: '↑ 12%', clicksChg: '↑ 5%', cpcChg: '↓ 3%', ctrChg: '↑ 4%', convChg: '↑ 15%', cpaChg: '↓ 6%', cvrChg: '↑ 9%' },
    '30d': { cost: '£823', impr: '18,420', clicks: '1,284', cpc: '£0.64', ctr: '6.97%', conv: '42', cpa: '£19.60', cvr: '3.27%',
             costChg: '↑ 8%', imprChg: '↑ 12%', clicksChg: '↑ 5%', cpcChg: '↓ 3%', ctrChg: '↑ 4%', convChg: '↑ 15%', cpaChg: '↓ 6%', cvrChg: '↑ 9%' },
    '90d': { cost: '£2,469', impr: '55,260', clicks: '3,852', cpc: '£0.64', ctr: '6.97%', conv: '126', cpa: '£19.60', cvr: '3.27%',
             costChg: '↑ 11%', imprChg: '↑ 14%', clicksChg: '↑ 8%', cpcChg: '↓ 2%', ctrChg: '↑ 5%', convChg: '↑ 18%', cpaChg: '↓ 8%', cvrChg: '↑ 12%' },
  };

  function flagBadgeHtml(type, agName) {
    if (!type) return '—';
    const labels = { negative: 'Negative Outlier', positive: 'Positive Outlier', pause: 'Pause Candidate', concentration: 'Concentration' };
    return `<span class="flag-count-badge" data-ag="${agName}" title="Click to view details"><span class="material-symbols-outlined">flag</span>${labels[type] || type}</span>`;
  }

  function updateTable(range) {
    const rows = TABLE_DATA[range];
    const tbody = document.querySelector('#adGroupsTable tbody');
    if (!tbody || !rows) return;
    tbody.innerHTML = '';

    rows.forEach(r => {
      const tr = document.createElement('tr');
      tr.dataset.status = 'enabled';
      tr.innerHTML = `
        <td><span class="status-dot status-dot--enabled"></span></td>
        <td><span class="adgroup-name-link" data-ag="${r.name}">${r.name}</span></td>
        <td><span class="parent-campaign-badge">${r.camp}</span></td>
        <td>${r.kw}</td>
        <td>${r.ads}</td>
        <td>${r.cost}</td>
        <td>${r.impr}</td>
        <td>${r.clicks}</td>
        <td>${r.cpcStr}</td>
        <td>${r.ctrStr}</td>
        <td>${r.conv}</td>
        <td>${r.costconv}</td>
        <td>${r.cvrStr}</td>
        <td>${r.flags > 0 ? flagBadgeHtml(r.flagType, r.name) : '—'}</td>`;
      tbody.appendChild(tr);
    });

    // Totals row
    const totals = document.createElement('tr');
    totals.className = 'totals-row';
    const s = SUMMARY_DATA[range];
    totals.innerHTML = `<td></td><td>Total / Average</td><td></td><td>274</td><td>45</td>
      <td>${s.cost}</td><td>${s.impr}</td><td>${s.clicks}</td>
      <td>${s.cpc}</td><td>${s.ctr}</td><td>${s.conv}</td>
      <td>${s.cpa}</td><td>${s.cvr}</td><td>—</td>`;
    tbody.appendChild(totals);

    // Update summary cards (8 cards: cost, impr, clicks, cpc, ctr, conv, cpa, cvr)
    const cards = document.querySelectorAll('.perf-inner .summary-card');
    const vals = [s.cost, s.impr, s.clicks, s.cpc, s.ctr, s.conv, s.cpa, s.cvr];
    const chgs = [s.costChg, s.imprChg, s.clicksChg, s.cpcChg, s.ctrChg, s.convChg, s.cpaChg, s.cvrChg];
    cards.forEach((card, i) => {
      if (vals[i] !== undefined) card.querySelector('.summary-card__value').textContent = vals[i];
      if (chgs[i]) {
        const chgEl = card.querySelector('.summary-card__change');
        chgEl.textContent = chgs[i];
        chgEl.className = 'summary-card__change summary-card__change--' + (chgs[i].startsWith('↑') ? 'up' : chgs[i].startsWith('↓') ? 'down' : 'flat');
      }
    });

    // Re-bind name click handlers after rebuilding rows
    bindAdGroupClicks();

    // Update pagination
    const info = document.getElementById('paginationInfo');
    if (info) info.textContent = `Showing 1-${rows.length} of ${rows.length} ad groups`;
  }

  // ── Chart ────────────────────────────────────────────────────────────────
  const chartCanvas = document.getElementById('performanceChart');
  let perfChart = null;

  function isDark() { return document.documentElement.getAttribute('data-theme') === 'dark'; }

  function getChartColors() {
    const dark = isDark();
    return {
      line1: '#f59e0b', // amber — ad group level
      line2: '#10b981', // green
      fill1: 'rgba(245,158,11,0.08)',
      fill2: 'rgba(16,185,129,0.08)',
      grid:  dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)',
      text:  dark ? '#ffffff' : '#000000',
      border: dark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
    };
  }

  function buildChart() {
    if (!chartCanvas) return;
    const m1Key = document.getElementById('chartMetric1').value;
    const m2Key = document.getElementById('chartMetric2').value;
    const m1Def = METRIC_DEFS[m1Key];
    const m2Def = METRIC_DEFS[m2Key];
    const chartData = getChartData(currentRange);
    const m1Data = chartData.metrics[m1Key];
    const m2Data = chartData.metrics[m2Key];
    const c = getChartColors();

    if (perfChart) perfChart.destroy();

    perfChart = new Chart(chartCanvas, {
      type: 'line',
      data: {
        labels: chartData.labels,
        datasets: [
          { label: m1Def.label, data: m1Data, borderColor: c.line1, backgroundColor: c.fill1, fill: true, tension: 0,
            pointRadius: 3, pointHoverRadius: 5, pointBackgroundColor: c.line1, pointBorderColor: c.line1, borderWidth: 2, yAxisID: 'y1' },
          { label: m2Def.label, data: m2Data, borderColor: c.line2, backgroundColor: c.fill2, fill: true, tension: 0,
            pointRadius: 3, pointHoverRadius: 5, pointBackgroundColor: c.line2, pointBorderColor: c.line2, borderWidth: 2, yAxisID: 'y2' }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: isDark() ? '#1e293b' : '#ffffff',
            titleColor: c.text, bodyColor: c.text, borderColor: c.border, borderWidth: 1, padding: 10,
            callbacks: {
              title: function(items) { return items[0]?.label || ''; },
              label: function(ctx) {
                const def = ctx.datasetIndex === 0 ? m1Def : m2Def;
                return `${def.label}: ${def.prefix}${ctx.parsed.y}${def.suffix}`;
              }
            }
          }
        },
        scales: {
          x: { grid: { color: c.grid }, ticks: { color: c.text, font: { size: 12 }, maxRotation: 0, autoSkipPadding: 12 }, border: { color: c.border } },
          y1: { position: 'left',
                title: { display: true, text: m1Def.label, color: c.line1, font: { size: 12, weight: 600 } },
                grid: { color: c.grid },
                ticks: { color: c.text, font: { size: 12 }, callback: function(v) { return m1Def.prefix + v + m1Def.suffix; } },
                border: { color: c.border } },
          y2: { position: 'right',
                title: { display: true, text: m2Def.label, color: c.line2, font: { size: 12, weight: 600 } },
                grid: { drawOnChartArea: false },
                ticks: { color: c.text, font: { size: 12 }, callback: function(v) { return m2Def.prefix + v + m2Def.suffix; } },
                border: { color: c.border } }
        }
      }
    });
  }

  // Init table + chart
  updateTable('30d');
  buildChart();

  // Rebuild chart on metric change
  document.getElementById('chartMetric1')?.addEventListener('change', buildChart);
  document.getElementById('chartMetric2')?.addEventListener('change', buildChart);

  // Rebuild chart on theme change
  new MutationObserver(() => { setTimeout(buildChart, 50); })
    .observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

  // ═════════════════════════════════════════════════════════════════════════
  // AD GROUP SLIDE-IN
  // ═════════════════════════════════════════════════════════════════════════

  const AG_DATA = {
    'Competitor Terms': {
      camp: 'GLO Campaign — Core', status: 'enabled', kw: 24, ads: 3, qs: '4.2',
      cost: '£248', cpa: '£35.00', cpaZone: 'underperforming', cpaDetail: '60% above campaign avg — Underperforming',
      conv: '7', qsVal: '4.2',
      approvals: [{
        text: '<strong>Negative performance outlier.</strong> This ad group consumes 15% of campaign spend at £35 CPA vs £22 campaign avg (60% worse).',
        rec: 'ACT recommends: Investigate keyword selection and ad copy. Consider pausing underperforming keywords or reducing bids.',
        impact: 'Potential saving: £80/month',
        timeWaiting: 'Identified 6 hours ago',
        flagType: 'negative', flagLabel: 'Negative Outlier', risk: 'medium',
        details: {
          Check:    'Negative Performance Outliers (runs overnight, 14+ day window)',
          Signal:   'CPA of £35.00 vs campaign average of £22.00 (59% worse) while consuming 15% of campaign spend for 14+ days.',
          Rule:     'Ad group has >30% of campaign spend OR CPA/ROAS 50%+ worse than campaign average for 14+ days. Flagged as negative outlier for human review.',
          Cooldown: 'No cooldown — monitoring flag only. Re-runs overnight.',
          Risk:     'Medium — significant budget waste but ad group is generating some conversions.'
        }
      }],
      executed: [
        { text: '<strong>Added 3 negative keywords to Competitor Terms ad group</strong>', time: '8 Apr, 05:14 AM', reason: 'Search terms with spend above target CPA and 0 conversions' },
      ],
      monitoring: [
        { text: '<strong>Competitor Terms negative outlier flag:</strong> Monitoring performance after negative keyword additions. 3 days into 7-day observation.',
          started: '5 Apr 2026, 05:12 AM', progress: 43, remaining: '3 of 7 days', health: 'healthy', healthLabel: 'Healthy' },
      ],
      alerts: [],
      outlier: {
        rows: [
          { metric: 'Cost Share',    self: '15%',   avg: '—',       delta: '—', class: 'flat' },
          { metric: 'CPA',           self: '£35.00', avg: '£22.00',  delta: '+59% (worse)', class: 'worse' },
          { metric: 'Conv Rate',     self: '2.8%',  avg: '4.5%',    delta: '-38% (worse)', class: 'worse' },
          { metric: 'Avg CPC',       self: '£3.20', avg: '£2.80',   delta: '+14% (higher)', class: 'worse' },
          { metric: 'Quality Score', self: '4.2',   avg: '6.1',     delta: '-31% (lower)', class: 'worse' },
        ],
        note: 'This ad group is flagged as a negative outlier because it exceeds the 30% spend + 50% worse CPA thresholds.'
      },
      structural: [
        { icon: 'search',          label: 'Keywords',                   value: '24 active (3 paused)' },
        { icon: 'article',         label: 'Ads',                        value: '3 active (2 RSAs, 1 call-only)' },
        { icon: 'star',            label: 'Average Quality Score',      value: '4.2 / 10' },
        { icon: 'edit_calendar',   label: 'Days since last change',     value: '12 days' },
        { icon: 'event',           label: 'Days since last conversion', value: '4 days' },
        { icon: 'bolt',            label: 'Ad strength',                value: 'Average' },
      ],
    },
    'Long Tail': {
      camp: 'GLO Campaign — Core', status: 'enabled', kw: 48, ads: 4, qs: '7.8',
      cost: '£122', cpa: '£13.53', cpaZone: 'outperforming', cpaDetail: '38% below campaign avg — Outperforming',
      conv: '9', qsVal: '7.8',
      approvals: [{
        text: '<strong>Positive performance outlier.</strong> 45% better CPA than campaign average. Consider promoting to standalone campaign.',
        rec: 'ACT recommends: Promote to standalone campaign so it can receive independent budget allocation.',
        impact: 'Estimated: +3-5 conversions/week if promoted',
        timeWaiting: 'Identified 2 days ago',
        flagType: 'positive', flagLabel: 'Positive Outlier', risk: 'low',
        details: {
          Check:    'Positive Performance Outliers (runs overnight, 21+ day window, 100+ clicks)',
          Signal:   'CPA of £13.53 vs campaign average of £22.00 (38% better, threshold met) sustained over 21+ days with 195 clicks.',
          Rule:     'Ad group CPA/ROAS 40%+ better than campaign average for 21+ days with 100+ clicks. Flagged as promotion candidate.',
          Cooldown: 'No cooldown — monitoring flag only. Re-runs overnight.',
          Risk:     'Low — consistent outperformance with no downside to promoting.'
        }
      }],
      executed: [],
      monitoring: [],
      alerts: [],
      outlier: {
        rows: [
          { metric: 'Cost Share',    self: '25%',    avg: '—',      delta: '—', class: 'flat' },
          { metric: 'CPA',           self: '£13.53', avg: '£22.00', delta: '-38% (better)', class: 'better' },
          { metric: 'Conv Rate',     self: '4.62%',  avg: '3.33%',  delta: '+39% (better)', class: 'better' },
          { metric: 'Avg CPC',       self: '£0.62',  avg: '£0.62',  delta: '0% (flat)', class: 'flat' },
          { metric: 'Quality Score', self: '7.8',    avg: '6.1',    delta: '+28% (higher)', class: 'better' },
        ],
        note: 'This ad group is flagged as a positive outlier because it exceeds the 40% better CPA threshold over 21+ days with 100+ clicks.'
      },
      structural: [
        { icon: 'search',        label: 'Keywords',                   value: '48 active (0 paused)' },
        { icon: 'article',       label: 'Ads',                        value: '4 active (4 RSAs)' },
        { icon: 'star',          label: 'Average Quality Score',      value: '7.8 / 10' },
        { icon: 'edit_calendar', label: 'Days since last change',     value: '8 days' },
        { icon: 'event',         label: 'Days since last conversion', value: '1 day' },
        { icon: 'bolt',          label: 'Ad strength',                value: 'Excellent' },
      ],
    },
    'Test Batch 3': {
      camp: 'Testing — New Keywords', status: 'enabled', kw: 15, ads: 2, qs: '3.1',
      cost: '£45', cpa: '—', cpaZone: 'underperforming', cpaDetail: '0 conversions in 21 days — Underperforming',
      conv: '0', qsVal: '3.1',
      approvals: [{
        text: '<strong>Pause recommendation.</strong> 21 days with zero conversions despite £45 spend.',
        rec: 'ACT recommends: Pause this ad group and reallocate budget to performing test batches.',
        impact: 'Estimated saving: £15/week if paused',
        timeWaiting: 'Identified 8 hours ago',
        flagType: 'pause', flagLabel: 'Pause Candidate', risk: 'medium',
        details: {
          Check:    'Pause Recommendations (runs overnight, 21+ day window)',
          Signal:   'Zero conversions for 21 days while consuming £45 of campaign budget. Sustained waste.',
          Rule:     'Ad group has >30% of campaign spend AND 0 conversions for 21+ days. Flagged for human pause decision.',
          Cooldown: 'No cooldown — monitoring flag only. Re-runs overnight.',
          Risk:     'Medium — pausing affects all keywords and ads in this ad group. Human decision required.'
        }
      }],
      executed: [
        { text: '<strong>Paused 2 keywords in Test Batch 3 ad group</strong>', time: '8 Apr, 05:15 AM', reason: '0 conversions in 21 days' },
      ],
      monitoring: [],
      alerts: [],
      outlier: {
        rows: [
          { metric: 'Cost Share',    self: '15%',    avg: '—',      delta: '—', class: 'flat' },
          { metric: 'CPA',           self: '—',      avg: '£102.90', delta: '— (0 conv)', class: 'worse' },
          { metric: 'Conv Rate',     self: '0%',     avg: '1.56%',  delta: '-100% (worse)', class: 'worse' },
          { metric: 'Avg CPC',       self: '£1.53',  avg: '£1.61',  delta: '-5% (lower)', class: 'better' },
          { metric: 'Quality Score', self: '3.1',    avg: '3.6',    delta: '-14% (lower)', class: 'worse' },
        ],
        note: 'This ad group is flagged for pause because it has zero conversions for 21+ days despite spending £45.'
      },
      structural: [
        { icon: 'search',        label: 'Keywords',                   value: '15 active (2 paused overnight)' },
        { icon: 'article',       label: 'Ads',                        value: '2 active (2 RSAs)' },
        { icon: 'star',          label: 'Average Quality Score',      value: '3.1 / 10' },
        { icon: 'edit_calendar', label: 'Days since last change',     value: '0 days (today)' },
        { icon: 'event',         label: 'Days since last conversion', value: '21 days (never)' },
        { icon: 'bolt',          label: 'Ad strength',                value: 'Poor' },
      ],
    },
    'Main Brand Terms': {
      camp: 'Brand — Objection Experts', status: 'enabled', kw: 14, ads: 3, qs: '9.4',
      cost: '£47', cpa: '£23.80', cpaZone: 'ontarget', cpaDetail: 'On target — Healthy',
      conv: '2', qsVal: '9.4',
      approvals: [{
        text: '<strong>Concentration alert.</strong> This ad group consumes 70% of campaign spend with only 3 other ad groups active.',
        rec: 'ACT recommends: Review ad group balance. Consider redistributing budget or consolidating underperforming ad groups.',
        impact: 'Better budget distribution across 4 active ad groups',
        timeWaiting: 'Identified 1 day ago',
        flagType: 'concentration', flagLabel: 'Concentration Alert', risk: 'medium',
        details: {
          Check:    'Budget Concentration Alerts (runs overnight, 14+ day window)',
          Signal:   'Main Brand Terms consuming 70% of campaign spend (£47 of £68) while the other 3 active ad groups share the remaining 30%.',
          Rule:     '3+ active ad groups, one consuming >50% of campaign spend for 14+ days. Flagged for budget rebalancing review.',
          Cooldown: 'No cooldown — monitoring flag only. Re-runs overnight.',
          Risk:     'Medium — redistributing budget may affect brand campaign performance. Human review required.'
        }
      }],
      executed: [],
      monitoring: [],
      alerts: [
        { text: '<strong>Concentration alert</strong> previously acknowledged on 5 Apr 2026 — flag re-raised today as concentration remains above threshold.', date: '5 Apr 2026' },
      ],
      outlier: {
        rows: [
          { metric: 'Cost Share',    self: '70%',    avg: '25% (expected)', delta: '+180% (dominant)', class: 'worse' },
          { metric: 'CPA',           self: '£23.80', avg: '£22.83',        delta: '+4% (higher)', class: 'flat' },
          { metric: 'Conv Rate',     self: '1.47%',  avg: '1.54%',         delta: '-5% (lower)', class: 'flat' },
          { metric: 'Avg CPC',       self: '£0.35',  avg: '£0.35',         delta: '0% (flat)', class: 'flat' },
          { metric: 'Quality Score', self: '9.4',    avg: '8.8',           delta: '+7% (higher)', class: 'better' },
        ],
        note: 'This ad group is flagged for concentration because it consumes >50% of campaign spend while 3+ other ad groups are active.'
      },
      structural: [
        { icon: 'search',        label: 'Keywords',                   value: '14 active (0 paused)' },
        { icon: 'article',       label: 'Ads',                        value: '3 active (2 RSAs, 1 call-only)' },
        { icon: 'star',          label: 'Average Quality Score',      value: '9.4 / 10' },
        { icon: 'edit_calendar', label: 'Days since last change',     value: '45 days' },
        { icon: 'event',         label: 'Days since last conversion', value: '2 days' },
        { icon: 'bolt',          label: 'Ad strength',                value: 'Excellent' },
      ],
    },
  };

  const DEFAULT_AG = AG_DATA['Competitor Terms'];

  const agOverlay = document.getElementById('agSlideinOverlay');
  const agPanel   = document.getElementById('agSlidein');
  const agBody    = document.getElementById('agSlideinBody');
  const agName    = document.getElementById('agSlideinName');
  const agMeta    = document.getElementById('agSlideinMeta');

  // Helper: slide-in section wrapper with empty state support
  function slideinSection({ icon, iconColor, title, count, countBg, collapsed, bodyHtml, emptyIcon, emptyText, isEmpty }) {
    const collapsedClass = collapsed ? ' collapsed' : '';
    const countBadge = count !== undefined
      ? `<span style="font-size:12px;font-weight:600;padding:2px 8px;border-radius:10px;color:white;background:${countBg}">${count}</span>`
      : '';
    const inner = isEmpty
      ? `<div class="slidein-empty-state"><span class="material-symbols-outlined">${emptyIcon}</span><div class="slidein-empty-state__text">${emptyText}</div></div>`
      : bodyHtml;
    return `<div class="slidein-section${collapsedClass}">
      <div class="slidein-section__header">
        <span class="material-symbols-outlined" style="font-size:20px;color:${iconColor}">${icon}</span>
        <span style="font-size:16px;font-weight:600;color:var(--act-text)">${title}</span>
        ${countBadge}
        <span class="material-symbols-outlined slidein-section__toggle">expand_more</span>
      </div>
      <div class="slidein-section__body">${inner}</div>
    </div>`;
  }

  function openAgSlidein(name) {
    const d = AG_DATA[name] || DEFAULT_AG;
    const displayName = AG_DATA[name] ? name : 'Competitor Terms';
    if (agName) agName.textContent = displayName;
    if (agMeta) agMeta.innerHTML = `
      <span style="font-size:14px;color:var(--act-text)"><span class="status-dot status-dot--${d.status}"></span> Enabled</span>
      <span class="parent-campaign-badge">${d.camp}</span>
      <span style="font-size:14px;color:var(--act-text)">${d.kw} keywords</span>
      <span style="font-size:14px;color:var(--act-text)">${d.ads} ads</span>
      <span style="font-size:14px;color:var(--act-text)">QS ${d.qs}</span>`;

    let html = '';

    // Health cards (4 in a row)
    html += '<div class="ag-health-grid">';
    html += `<div class="ag-health-card"><div class="ag-health-card__label">Cost (MTD)</div><div class="ag-health-card__value">${d.cost}</div></div>`;
    html += `<div class="ag-health-card"><div class="ag-health-card__label">CPA</div><div class="ag-health-card__value" style="color:${d.cpaZone === 'outperforming' ? '#10b981' : d.cpaZone === 'underperforming' ? '#ef4444' : '#3b82f6'}">${d.cpa}</div><div class="ag-health-card__detail"><span class="zone-badge zone-badge--${d.cpaZone}">${d.cpaDetail}</span></div></div>`;
    html += `<div class="ag-health-card"><div class="ag-health-card__label">Conversions (MTD)</div><div class="ag-health-card__value">${d.conv}</div></div>`;
    html += `<div class="ag-health-card"><div class="ag-health-card__label">QS Average</div><div class="ag-health-card__value">${d.qsVal}</div></div>`;
    html += '</div>';

    // ── AWAITING APPROVAL (expanded, always shown) ────────────────────────
    const approvalsBody = d.approvals.map((a, idx) => {
      let detailGrid = '';
      if (a.details) {
        detailGrid = '<dl class="act-detail-grid">';
        for (const [k, v] of Object.entries(a.details)) detailGrid += `<dt>${k}</dt><dd>${v}</dd>`;
        detailGrid += '</dl>';
      }
      return `<div class="act-item" data-priority="investigate">
        <div class="act-item__row">
          <div class="act-item__content">
            <div class="act-item__top">
              <span class="badge-action badge-action--investigate">Investigate</span>
              <span class="badge-risk badge-risk--${a.risk}">${a.risk.charAt(0).toUpperCase() + a.risk.slice(1)} Risk</span>
              <span class="flag-badge flag-badge--${a.flagType}">${a.flagLabel}</span>
              ${a.timeWaiting ? `<span class="act-item__waiting"><span class="material-symbols-outlined">schedule</span>${a.timeWaiting}</span>` : ''}
              <span class="act-item__impact"><span class="material-symbols-outlined">trending_up</span>${a.impact}</span>
            </div>
            <div class="act-item__summary">${a.text}</div>
            <div class="act-item__recommendation"><span class="material-symbols-outlined">lightbulb</span>${a.rec}</div>
            ${a.details ? `<div class="slidein-detail-expand" id="slideinDetail${idx}">${detailGrid}</div>` : ''}
          </div>
          <div class="act-item__actions">
            <button class="btn-act btn-act--approve" onclick="this.closest('.act-item').style.opacity='0.4';this.closest('.act-item').style.pointerEvents='none';">Approve</button>
            <button class="btn-act btn-act--decline" onclick="this.closest('.act-item').style.opacity='0.4';this.closest('.act-item').style.pointerEvents='none';">Decline</button>
            ${a.details ? `<button class="btn-see-details" data-detail-idx="${idx}">See Details</button>` : ''}
          </div>
        </div>
      </div>`;
    }).join('');
    html += slideinSection({
      icon: 'pending_actions', iconColor: 'var(--act-amber)',
      title: 'Awaiting Approval', count: d.approvals.length, countBg: 'var(--act-amber)',
      collapsed: false, bodyHtml: approvalsBody,
      emptyIcon: 'check_circle', emptyText: 'All clear — no actions need your review today',
      isEmpty: d.approvals.length === 0
    });

    // ── ACTIONS EXECUTED OVERNIGHT (collapsed, always shown) ──────────────
    const executedBody = d.executed.map(e => {
      return `<div class="act-item"><div class="act-item__row"><div class="act-item__content"><div class="act-item__top"><span class="badge-action badge-action--act">Act</span><span class="act-item__timestamp">${e.time}</span></div><div class="act-item__summary">${e.text}${e.reason ? `<span class="act-item__reason-inline">${e.reason}</span>` : ''}</div></div></div></div>`;
    }).join('');
    html += slideinSection({
      icon: 'check_circle', iconColor: 'var(--act-green)',
      title: 'Actions Executed Overnight', count: d.executed.length, countBg: 'var(--act-green)',
      collapsed: true, bodyHtml: executedBody,
      emptyIcon: 'bedtime', emptyText: 'No actions were executed overnight.',
      isEmpty: d.executed.length === 0
    });

    // ── CURRENTLY MONITORING (collapsed, always shown) ────────────────────
    const monList = d.monitoring || [];
    const monitoringBody = monList.map(m => {
      const barColor = m.health === 'healthy' ? 'var(--act-green)' : m.health === 'warning' ? 'var(--act-amber)' : '#9aa0a6';
      const labelClass = m.health === 'healthy' ? 'health-label--healthy' : m.health === 'warning' ? 'health-label--warning' : 'health-label--neutral';
      return `<div class="act-item"><div class="act-item__row"><div class="act-item__content"><div class="act-item__top"><span class="badge-action badge-action--monitor">Monitor</span><span class="act-item__started"><span class="material-symbols-outlined">calendar_today</span>Started: ${m.started}</span></div><div class="act-item__summary">${m.text}</div><div class="act-item__progress"><div class="act-item__progress-bar"><div class="act-item__progress-fill" style="width:${m.progress}%;background:${barColor}"></div></div><span class="act-item__progress-text">${m.remaining}</span><span class="health-label ${labelClass}">${m.healthLabel}</span></div></div></div></div>`;
    }).join('');
    html += slideinSection({
      icon: 'visibility', iconColor: 'var(--act-blue)',
      title: 'Currently Monitoring', count: monList.length, countBg: 'var(--act-blue)',
      collapsed: true, bodyHtml: monitoringBody,
      emptyIcon: 'visibility_off', emptyText: 'Nothing is currently being monitored.',
      isEmpty: monList.length === 0
    });

    // ── RECENT ALERTS (collapsed, always shown) ───────────────────────────
    const alertList = d.alerts || [];
    const alertsBody = alertList.map(a => {
      return `<div class="act-item" data-priority="alert"><div class="act-item__row"><div class="act-item__content"><div class="act-item__top"><span class="badge-action badge-action--alert">Alert</span><span class="act-item__timestamp">${a.date}</span></div><div class="act-item__summary">${a.text}</div></div></div></div>`;
    }).join('');
    html += slideinSection({
      icon: 'notifications_active', iconColor: 'var(--act-red)',
      title: 'Recent Alerts', count: alertList.length, countBg: 'var(--act-red)',
      collapsed: true, bodyHtml: alertsBody,
      emptyIcon: 'notifications_none', emptyText: 'No alerts in the last 7 days.',
      isEmpty: alertList.length === 0
    });

    // ── OUTLIER ANALYSIS (collapsed) — unique to Ad Group Level ───────────
    let outlierBody = '<div class="slidein-section__inner">';
    outlierBody += '<table class="outlier-table"><thead><tr><th>Metric</th><th>This Ad Group</th><th>Campaign Average</th><th>Delta</th></tr></thead><tbody>';
    d.outlier.rows.forEach(r => {
      outlierBody += `<tr><td>${r.metric}</td><td>${r.self}</td><td>${r.avg}</td><td class="outlier-delta--${r.class}">${r.delta}</td></tr>`;
    });
    outlierBody += '</tbody></table>';
    outlierBody += `<div class="outlier-note"><span class="material-symbols-outlined">info</span>${d.outlier.note}</div>`;
    outlierBody += '</div>';
    html += slideinSection({
      icon: 'analytics', iconColor: '#f59e0b',
      title: 'Outlier Analysis', collapsed: true, bodyHtml: outlierBody, isEmpty: false
    });

    // ── STRUCTURAL HEALTH (collapsed) — unique to Ad Group Level ──────────
    let structBody = '<ul class="structural-health">';
    d.structural.forEach(s => {
      structBody += `<li><span class="material-symbols-outlined">${s.icon}</span>${s.label}<span class="structural-health__value">${s.value}</span></li>`;
    });
    structBody += '</ul>';
    html += slideinSection({
      icon: 'health_and_safety', iconColor: '#f59e0b',
      title: 'Structural Health', collapsed: true, bodyHtml: structBody, isEmpty: false
    });

    if (agBody) agBody.innerHTML = html;

    // Bind slide-in section toggle clicks
    agBody.querySelectorAll('.slidein-section__header').forEach(header => {
      header.addEventListener('click', (e) => {
        if (e.target.closest('.btn-see-details') || e.target.closest('.btn-act')) return;
        header.closest('.slidein-section').classList.toggle('collapsed');
      });
    });

    // Bind See Details / Hide Details toggle
    agBody.querySelectorAll('.btn-see-details').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const idx = btn.dataset.detailIdx;
        const panel = document.getElementById('slideinDetail' + idx);
        if (panel) {
          panel.classList.toggle('show');
          btn.textContent = panel.classList.contains('show') ? 'Hide Details' : 'See Details';
        }
      });
    });

    agOverlay?.classList.add('open');
    agPanel?.classList.add('open');
  }

  window.closeAgSlidein = function() {
    agOverlay?.classList.remove('open');
    agPanel?.classList.remove('open');
  };
  agOverlay?.addEventListener('click', closeAgSlidein);
  document.getElementById('agSlideinClose')?.addEventListener('click', closeAgSlidein);

  function bindAdGroupClicks() {
    document.querySelectorAll('.adgroup-name-link').forEach(link => {
      link.addEventListener('click', () => openAgSlidein(link.dataset.ag));
    });
    // Flag column badges also open the slide-in for that ad group
    document.querySelectorAll('#adGroupsTable .flag-count-badge').forEach(badge => {
      badge.addEventListener('click', () => openAgSlidein(badge.dataset.ag));
    });
  }
  bindAdGroupClicks();

  // ═════════════════════════════════════════════════════════════════════════
  // TOAST
  // ═════════════════════════════════════════════════════════════════════════
  function showToast(msg, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `act-toast act-toast--${type}`;
    toast.innerHTML = `<span class="material-symbols-outlined">${type === 'success' ? 'check_circle' : type === 'warning' ? 'undo' : type === 'error' ? 'error' : 'info'}</span>${msg}`;
    document.body.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => { toast.classList.remove('show'); setTimeout(() => toast.remove(), 300); }, 3000);
  }

});
