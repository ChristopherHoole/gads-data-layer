/* ============================================================================
   ACT PROTOTYPE — CAMPAIGN LEVEL OPTION D INTERACTIONS
   Campaign list + 720px slide-in detail panel on campaign name click.
   ============================================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // Theme toggle
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

  // Client switcher
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

  // Section collapse (both acct-section and act-section patterns)
  document.querySelectorAll('.acct-section__header, .act-section__header').forEach(header => {
    header.addEventListener('click', (e) => {
      if (e.target.closest('.act-bulk-bar') || e.target.closest('.table-toolbar')) return;
      const section = header.closest('.acct-section') || header.closest('.act-section');
      if (section) section.classList.toggle('collapsed');
    });
  });

  // Group collapse
  document.querySelectorAll('.act-group__header').forEach(header => {
    header.addEventListener('click', (e) => { e.stopPropagation(); header.closest('.act-group').classList.toggle('collapsed'); });
  });

  // Table sorting
  document.querySelectorAll('.data-table th[data-sort]').forEach(th => {
    th.addEventListener('click', () => {
      const table = th.closest('table');
      const tbody = table.querySelector('tbody');
      const rows = Array.from(tbody.querySelectorAll('tr:not(.score-breakdown-row)'));
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
    });
  });

  // Score breakdown expand
  document.querySelectorAll('[data-action="expand-score"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const row = btn.closest('tr');
      const breakdown = row.nextElementSibling;
      if (breakdown && breakdown.classList.contains('score-breakdown-row')) {
        breakdown.style.display = breakdown.style.display === 'none' ? '' : 'none';
      }
    });
  });

  // Pill group buttons (date range + status filter)
  document.querySelectorAll('.pill-group').forEach(group => {
    group.querySelectorAll('.pill-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        group.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        if (btn.dataset.range) {
          currentRange = btn.dataset.range;
          const days = currentRange === '7d' ? '7' : currentRange === '30d' ? '30' : '90';
          const ctx = document.getElementById('perfContext');
          if (ctx) ctx.textContent = `— 4 campaigns, ${days} days`;
          buildChart();
          updateTable(currentRange);
          showToast(`Showing ${btn.textContent.trim()} data`, 'info');
        }
        if (btn.dataset.filter) filterCampaigns(btn.dataset.filter);
      });
    });
  });

  function filterCampaigns(filter) {
    document.querySelectorAll('#campaignsTable tbody tr').forEach(row => {
      // Skip score breakdown rows — they're controlled by score click only
      if (row.classList.contains('score-breakdown-row')) return;
      if (row.classList.contains('totals-row')) return;
      if (filter === 'all') { row.style.display = ''; return; }
      const status = row.dataset.status;
      row.style.display = (status === filter) ? '' : 'none';
      // Also hide the associated breakdown row
      const next = row.nextElementSibling;
      if (next && next.classList.contains('score-breakdown-row') && status !== filter) {
        next.style.display = 'none';
      }
    });
  }

  // Approve/Decline
  document.querySelectorAll('[data-action="approve"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const item = btn.closest('.act-item') || btn.closest('.acct-rec');
      if (item) { item.style.opacity = '0.4'; item.style.pointerEvents = 'none'; }
      showToast('Approved — change will be applied in next cycle', 'success');
    });
  });

  document.querySelectorAll('[data-action="decline"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const item = btn.closest('.act-item') || btn.closest('.acct-rec');
      if (item) { item.style.opacity = '0.4'; item.style.pointerEvents = 'none'; }
      showToast('Declined — no changes will be made', 'info');
    });
  });

  document.querySelectorAll('[data-action="undo"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const item = btn.closest('.act-item');
      if (item) { item.style.opacity = '0.4'; item.style.pointerEvents = 'none'; }
      showToast('Undo queued — will be reverted in next cycle', 'warning');
    });
  });

  // Slide-in for View Details
  const slideinOverlay = document.getElementById('slideinOverlay');
  const slideinPanel = document.getElementById('slideinPanel');
  const slideinBody = document.getElementById('slideinBody');

  document.querySelectorAll('[data-action="details"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const item = btn.closest('.act-item');
      if (!item || !slideinPanel || !slideinBody) return;
      const summary = item.querySelector('.act-item__summary')?.innerHTML || '';
      const badges = item.querySelector('.act-item__top')?.innerHTML || '';
      const detailData = item.dataset.details ? JSON.parse(item.dataset.details) : null;
      let html = `<div style="margin-bottom:12px">${badges}</div><div style="font-size:14px;line-height:1.6;margin-bottom:16px">${summary}</div>`;
      if (detailData) {
        html += '<dl class="act-detail-grid">';
        for (const [key, val] of Object.entries(detailData)) html += `<dt>${key}</dt><dd>${val}</dd>`;
        html += '</dl>';
      }
      slideinBody.innerHTML = html;
      slideinOverlay?.classList.add('open');
      slideinPanel?.classList.add('open');
    });
  });

  window.closeSlidein = function() { slideinOverlay?.classList.remove('open'); slideinPanel?.classList.remove('open'); };
  slideinOverlay?.addEventListener('click', closeSlidein);
  document.getElementById('slideinClose')?.addEventListener('click', closeSlidein);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeSlidein(); });

  // -------------------------------------------------------------------------
  // v9: PERFORMANCE TIMELINE CHART — multi-range data
  // -------------------------------------------------------------------------
  let currentRange = '30d';

  // Generate date labels
  function makeDailyLabels(days) {
    const labels = [];
    const d = new Date(2026, 3, 6); // 6 Apr 2026
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

  // Seeded random for consistent data
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
    score:       { label: 'Performance Score',   prefix: '',  suffix: '' },
    budgetUtil:  { label: 'Budget Utilisation %',prefix: '',  suffix: '%' },
  };

  function getChartData(range) {
    if (range === '90d') {
      // 90d = 13 weekly points, aggregated (sums for volume, averages for rates)
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
      const dailyScore = seededData(78, 12, 91, true);
      const dailyUtil = seededData(90, 8, 91, true);

      function weeklySum(arr) { const r = []; for (let w = 0; w < n; w++) { let s = 0; for (let d = 0; d < 7 && w*7+d < arr.length; d++) s += arr[w*7+d]; r.push(Math.round(s)); } return r; }
      function weeklyAvg(arr) { const r = []; for (let w = 0; w < n; w++) { let s = 0, c = 0; for (let d = 0; d < 7 && w*7+d < arr.length; d++) { s += arr[w*7+d]; c++; } r.push(Math.round(s/c*100)/100); } return r; }

      return {
        labels,
        metrics: {
          cost: weeklySum(dailyCost), impressions: weeklySum(dailyImpr),
          clicks: weeklySum(dailyClicks), conversions: weeklySum(dailyConv),
          avgCpc: weeklyAvg(dailyCpc), ctr: weeklyAvg(dailyCtr),
          cpa: weeklyAvg(dailyCpa), convRate: weeklyAvg(dailyCvr),
          score: weeklyAvg(dailyScore), budgetUtil: weeklyAvg(dailyUtil),
        }
      };
    }
    // 7d or 30d = daily points
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
        score:       seededData(78, 12, n, true),
        budgetUtil:  seededData(90, 8, n, true),
      }
    };
  }

  // ── TABLE DATA PER DATE RANGE ──
  const TABLE_DATA = {
    '7d': [
      { name: 'GLO Campaign — Core',     strat: 'tCPA £25', role: 'cp', status: 'enabled', budget: '£30/d', cost: '£125.40', impr: '2,680', clicks: '192', cpc: '£0.65', ctr: '7.16%', conv: '7', costconv: '£17.91', cvr: '3.65%', score: '82' },
      { name: 'GLO Campaign — Retargeting', strat: 'tCPA £15', role: 'rt', status: 'enabled', budget: '£10/d', cost: '£41.80', impr: '810', clicks: '62', cpc: '£0.67', ctr: '7.65%', conv: '3', costconv: '£13.93', cvr: '4.84%', score: '91' },
      { name: 'Brand — Objection Experts', strat: 'Manual CPC', role: 'bd', status: 'enabled', budget: '£5/d', cost: '£17.50', impr: '720', clicks: '50', cpc: '£0.35', ctr: '6.94%', conv: '1', costconv: '£17.50', cvr: '2.00%', score: '95' },
      { name: 'Testing — New Keywords',   strat: 'Max Clicks', role: 'ts', status: 'enabled', budget: '£5/d', cost: '£26.30', impr: '390', clicks: '16', cpc: '£1.64', ctr: '4.10%', conv: '0', costconv: '—', cvr: '0.00%', score: '38' },
    ],
    '30d': [
      { name: 'GLO Campaign — Core',     strat: 'tCPA £25', role: 'cp', status: 'enabled', budget: '£30/d', cost: '£487.20', impr: '10,850', clicks: '780', cpc: '£0.62', ctr: '7.19%', conv: '26', costconv: '£18.74', cvr: '3.33%', score: '82' },
      { name: 'GLO Campaign — Retargeting', strat: 'tCPA £15', role: 'rt', status: 'enabled', budget: '£10/d', cost: '£164.40', impr: '3,200', clicks: '245', cpc: '£0.67', ctr: '7.66%', conv: '12', costconv: '£13.70', cvr: '4.90%', score: '91' },
      { name: 'Brand — Objection Experts', strat: 'Manual CPC', role: 'bd', status: 'enabled', budget: '£5/d', cost: '£68.50', impr: '2,800', clicks: '195', cpc: '£0.35', ctr: '6.96%', conv: '3', costconv: '£22.83', cvr: '1.54%', score: '95' },
      { name: 'Testing — New Keywords',   strat: 'Max Clicks', role: 'ts', status: 'enabled', budget: '£5/d', cost: '£102.90', impr: '1,570', clicks: '64', cpc: '£1.61', ctr: '4.08%', conv: '1', costconv: '£102.90', cvr: '1.56%', score: '38' },
    ],
    '90d': [
      { name: 'GLO Campaign — Core',     strat: 'tCPA £25', role: 'cp', status: 'enabled', budget: '£30/d', cost: '£1,461.60', impr: '32,550', clicks: '2,340', cpc: '£0.62', ctr: '7.19%', conv: '78', costconv: '£18.74', cvr: '3.33%', score: '82' },
      { name: 'GLO Campaign — Retargeting', strat: 'tCPA £15', role: 'rt', status: 'enabled', budget: '£10/d', cost: '£493.20', impr: '9,600', clicks: '735', cpc: '£0.67', ctr: '7.66%', conv: '36', costconv: '£13.70', cvr: '4.90%', score: '91' },
      { name: 'Brand — Objection Experts', strat: 'Manual CPC', role: 'bd', status: 'enabled', budget: '£5/d', cost: '£205.50', impr: '8,400', clicks: '585', cpc: '£0.35', ctr: '6.96%', conv: '9', costconv: '£22.83', cvr: '1.54%', score: '95' },
      { name: 'Testing — New Keywords',   strat: 'Max Clicks', role: 'ts', status: 'enabled', budget: '£5/d', cost: '£308.70', impr: '4,710', clicks: '192', cpc: '£1.61', ctr: '4.08%', conv: '3', costconv: '£102.90', cvr: '1.56%', score: '38' },
    ]
  };

  const SUMMARY_DATA = {
    '7d':  { cost: '£211', impr: '4,600', clicks: '320', cpc: '£0.66', conv: '11', cpa: '£19.18', cvr: '3.44%', costChg: '↑ 8%', imprChg: '↑ 12%', clicksChg: '↑ 5%', cpcChg: '↓ 3%', convChg: '↑ 15%', cpaChg: '↓ 6%', cvrChg: '↑ 9%' },
    '30d': { cost: '£823', impr: '18,420', clicks: '1,284', cpc: '£0.64', conv: '42', cpa: '£19.60', cvr: '3.27%', costChg: '↑ 8%', imprChg: '↑ 12%', clicksChg: '↑ 5%', cpcChg: '↓ 3%', convChg: '↑ 15%', cpaChg: '↓ 6%', cvrChg: '↑ 9%' },
    '90d': { cost: '£2,469', impr: '55,260', clicks: '3,852', cpc: '£0.64', conv: '126', cpa: '£19.60', cvr: '3.27%', costChg: '↑ 11%', imprChg: '↑ 14%', clicksChg: '↑ 8%', cpcChg: '↓ 2%', convChg: '↑ 18%', cpaChg: '↓ 8%', cvrChg: '↑ 12%' },
  };

  function updateTable(range) {
    const rows = TABLE_DATA[range];
    const tbody = document.querySelector('#campaignsTable tbody');
    if (!tbody || !rows) return;

    // Remove existing data rows and breakdown rows (keep structure)
    tbody.querySelectorAll('tr').forEach(r => r.remove());

    const scoreClasses = { '82': 'score--high', '91': 'score--high', '95': 'score--high', '38': 'score--low' };

    rows.forEach(r => {
      const tr = document.createElement('tr');
      tr.dataset.status = r.status;
      tr.innerHTML = `
        <td><span class="status-dot status-dot--${r.status}"></span></td>
        <td><strong>${r.name}</strong></td>
        <td><span class="strategy-badge">${r.strat}</span></td>
        <td><span class="role-badge role-badge--${r.role}">${r.role.toUpperCase()}</span></td>
        <td>${r.budget}</td>
        <td>${r.cost}</td><td>${r.impr}</td><td>${r.clicks}</td>
        <td>${r.cpc}</td><td>${r.ctr}</td><td>${r.conv}</td>
        <td>${r.costconv}</td><td>${r.cvr}</td>
        <td><span class="score-display ${scoreClasses[r.score] || 'score--mid'}">${r.score}</span></td>`;
      tbody.appendChild(tr);
    });

    // Totals row
    const totals = document.createElement('tr');
    totals.className = 'totals-row';
    const s = SUMMARY_DATA[range];
    totals.innerHTML = `<td></td><td>Total / Average</td><td></td><td></td>
      <td>£50/d</td>
      <td>${s.cost}</td><td>${s.impr}</td><td>${s.clicks}</td>
      <td>${s.cpc}</td><td>—</td><td>${s.conv}</td>
      <td>${s.cpa}</td><td>${s.cvr}</td><td>—</td>`;
    tbody.appendChild(totals);

    // Update summary cards
    const cards = document.querySelectorAll('.perf-inner .summary-card');
    const vals = [s.cost, s.impr, s.clicks, s.cpc, s.conv, s.cpa, s.cvr];
    const chgs = [s.costChg, s.imprChg, s.clicksChg, s.cpcChg, s.convChg, s.cpaChg, s.cvrChg];
    cards.forEach((card, i) => {
      if (vals[i]) card.querySelector('.summary-card__value').textContent = vals[i];
      if (chgs[i]) {
        const chgEl = card.querySelector('.summary-card__change');
        chgEl.textContent = chgs[i];
        chgEl.className = 'summary-card__change summary-card__change--' + (chgs[i].startsWith('↑') ? 'up' : chgs[i].startsWith('↓') ? 'down' : 'flat');
      }
    });
  }

  const chartCanvas = document.getElementById('performanceChart');
  let perfChart = null;

  function isDark() { return document.documentElement.getAttribute('data-theme') === 'dark'; }

  function getChartColors() {
    const dark = isDark();
    return {
      line1: '#3b82f6',
      line2: '#10b981',
      fill1: dark ? 'rgba(59,130,246,0.08)' : 'rgba(59,130,246,0.08)',
      fill2: dark ? 'rgba(16,185,129,0.08)' : 'rgba(16,185,129,0.08)',
      grid: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)',
      text: dark ? '#ffffff' : '#000000',
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
          {
            label: m1Def.label,
            data: m1Data,
            borderColor: c.line1,
            backgroundColor: c.fill1,
            fill: true,
            tension: 0,
            pointRadius: 3,
            pointHoverRadius: 5,
            pointBackgroundColor: c.line1,
            pointBorderColor: c.line1,
            borderWidth: 2,
            yAxisID: 'y1',
          },
          {
            label: m2Def.label,
            data: m2Data,
            borderColor: c.line2,
            backgroundColor: c.fill2,
            fill: true,
            tension: 0,
            pointRadius: 3,
            pointHoverRadius: 5,
            pointBackgroundColor: c.line2,
            pointBorderColor: c.line2,
            borderWidth: 2,
            yAxisID: 'y2',
          }
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
            titleColor: c.text,
            bodyColor: c.text,
            borderColor: c.border,
            borderWidth: 1,
            padding: 10,
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
          x: {
            grid: { color: c.grid },
            ticks: { color: c.text, font: { size: 12 }, maxRotation: 0, autoSkipPadding: 12 },
            border: { color: c.border }
          },
          y1: {
            position: 'left',
            title: { display: true, text: m1Def.label, color: c.line1, font: { size: 12, weight: 600 } },
            grid: { color: c.grid },
            ticks: {
              color: c.text, font: { size: 12 },
              callback: function(v) { return m1Def.prefix + v + m1Def.suffix; }
            },
            border: { color: c.border }
          },
          y2: {
            position: 'right',
            title: { display: true, text: m2Def.label, color: c.line2, font: { size: 12, weight: 600 } },
            grid: { drawOnChartArea: false },
            ticks: {
              color: c.text, font: { size: 12 },
              callback: function(v) { return m2Def.prefix + v + m2Def.suffix; }
            },
            border: { color: c.border }
          }
        }
      }
    });
  }

  // Build on load
  buildChart();

  // Rebuild on metric change
  document.getElementById('chartMetric1')?.addEventListener('change', buildChart);
  document.getElementById('chartMetric2')?.addEventListener('change', buildChart);

  // Rebuild on theme change to update colours
  const origThemeClick = themeToggle?.onclick;
  if (themeToggle) {
    const existingListeners = themeToggle.cloneNode(true);
    // Watch for data-theme attribute change instead
    new MutationObserver(() => { setTimeout(buildChart, 50); })
      .observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  }

  // ── CAMPAIGN SLIDE-IN ──
  const CAMP_DATA = {
    'GLO Campaign — Core': { strat: 'tCPA £25', role: 'cp', status: 'enabled', budget: '£30/day', cost: '£487', cpa: '£18.50', cpaZone: 'outperforming', cpaDetail: '26% below target', conv: '26', convDetail: 'vs 22 last period (+18%)', qs: '6.2',
      levers: [
        { icon: 'devices', name: 'Device Modifiers', status: 'Mobile +10%, Desktop +0%, Tablet -35%', cooldown: 'Tablet: 5d remaining', detail: 'Mobile: +10% (1 Apr, ready) | Desktop: +0% (no changes) | Tablet: -35% (8 Apr, 5d cooldown). Caps: -60%/+30%, 7-day cooldown.' },
        { icon: 'location_on', name: 'Geographic', status: '5 locations, Scotland -50% (cap)', cooldown: 'All ready', detail: 'England +0%, Wales -10%, Scotland -50% (cap), N.Ireland -15%, London +10%. Caps: -50%/+30%, 30-day cooldown.' },
        { icon: 'schedule', name: 'Ad Schedule', status: 'Sunday -20%, Saturday -10%', cooldown: 'Sunday: 29d remaining', detail: 'Mon +0% (pending +15%), Tue-Fri +0%, Sat -10% (22 Mar), Sun -20% (8 Apr, 29d cooldown). Caps: -50%/+25%, 30-day cooldown.' },
        { icon: 'block', name: 'Negative Keywords', status: '142 across 9 lists', cooldown: 'Last added: 8 Apr', detail: '142 negative keywords across 9 standardised lists. ACT adds [exact] match only. Managed at Keyword Level.' },
        { icon: 'sort_by_alpha', name: 'Match Types', status: 'Broad 15%, Phrase 45%, Exact 40%', cooldown: 'Changes require approval', detail: 'All match type changes require approval. Managed at Keyword Level.' },
      ],
      stratTarget: '£25.00', stratAssess: 'Last: £23→£25 on 29 Mar. Next eligible: 12 Apr (14-day cooldown).',
      approvals: [
        { type: 'Bid Strategy', text: '<strong>Loosen tCPA</strong> £25 → £27.50 — CPA 26% below target', impact: '+2-3 conversions/week' },
        { type: 'Geographic', text: '<strong>Scotland geo</strong> +0% → -15% — CPA 45% above target', impact: '£4/week saving' },
        { type: 'Schedule', text: '<strong>Monday schedule</strong> +0% → +15% — Monday CPA £14.20', impact: '+1 conversion/week' },
      ],
      executed: [
        { text: '<strong>Sunday schedule</strong> +0% → -20%', time: '8 Apr, 05:14 AM' },
        { text: '<strong>Tablet device</strong> -20% → -35%', time: '8 Apr, 05:15 AM' },
        { text: '<strong>Added 4 negative keywords</strong>', time: '8 Apr, 05:15 AM' },
      ]
    },
    'GLO Campaign — Retargeting': { strat: 'tCPA £15', role: 'rt', status: 'enabled', budget: '£10/day', cost: '£164', cpa: '£13.70', cpaZone: 'outperforming', cpaDetail: '9% below target', conv: '12', convDetail: 'vs 10 last period (+20%)', qs: '5.8',
      levers: [{ icon:'devices',name:'Device',status:'All at +0%',cooldown:'All ready',detail:'No changes made.' },{ icon:'location_on',name:'Geographic',status:'No adjustments',cooldown:'Ready',detail:'No geo modifiers.' },{ icon:'schedule',name:'Schedule',status:'No adjustments',cooldown:'Ready',detail:'No schedule modifiers.' },{ icon:'block',name:'Negatives',status:'89 across 9 lists',cooldown:'Last: 6 Apr',detail:'89 keywords.' },{ icon:'sort_by_alpha',name:'Match Types',status:'Phrase 60%, Exact 40%',cooldown:'—',detail:'No broad match.' }],
      stratTarget:'£15.00', stratAssess:'On target. Last: £13→£15 on 20 Mar. Next eligible: 3 Apr.',
      approvals:[], executed:[{ text:'<strong>Added 2 negative keywords</strong>', time:'8 Apr, 05:14 AM' }]
    }
  };
  // Fallback for campaigns without full data
  const DEFAULT_CAMP = CAMP_DATA['GLO Campaign — Core'];

  const campOverlay = document.getElementById('campSlideinOverlay');
  const campPanel = document.getElementById('campSlidein');
  const campBody = document.getElementById('campSlideinBody');
  const campName = document.getElementById('campSlideinName');
  const campMeta = document.getElementById('campSlideinMeta');

  function openCampSlidein(name) {
    const d = CAMP_DATA[name] || DEFAULT_CAMP;
    if (campName) campName.textContent = name;
    if (campMeta) campMeta.innerHTML = `<span class="strategy-badge">${d.strat}</span><span class="role-badge role-badge--${d.role}">${d.role.toUpperCase()}</span><span style="font-size:14px;color:var(--act-text)"><span class="status-dot status-dot--${d.status}"></span> ${d.status}</span><span style="font-size:14px;font-weight:600;color:var(--act-text)">${d.budget}</span>`;

    let html = '';

    // Health cards 2x2
    html += '<div class="camp-health-grid">';
    html += `<div class="camp-health-card"><div class="camp-health-card__label">Cost (MTD)</div><div class="camp-health-card__value">${d.cost}</div></div>`;
    html += `<div class="camp-health-card"><div class="camp-health-card__label">CPA</div><div class="camp-health-card__value" style="color:#10b981">${d.cpa}</div><div class="camp-health-card__detail"><span class="zone-badge zone-badge--${d.cpaZone}">${d.cpaDetail}</span></div></div>`;
    html += `<div class="camp-health-card"><div class="camp-health-card__label">Conversions (MTD)</div><div class="camp-health-card__value">${d.conv}</div><div class="camp-health-card__detail">${d.convDetail}</div></div>`;
    html += `<div class="camp-health-card"><div class="camp-health-card__label">QS Average</div><div class="camp-health-card__value">${d.qs}</div></div>`;
    html += '</div>';

    // Review items
    if (d.approvals.length > 0) {
      html += '<div class="camp-section-label">Awaiting Approval</div>';
      d.approvals.forEach(a => {
        html += `<div class="act-item" data-priority="investigate" style="padding:10px 0;border-bottom:1px solid var(--act-border-light)"><div class="act-item__row"><div class="act-item__content"><div class="act-item__top"><span class="badge-action badge-action--investigate">Investigate</span><span style="font-size:12px;color:var(--act-text);opacity:0.7">${a.type}</span></div><div class="act-item__summary">${a.text}</div><div class="act-item__impact"><span class="material-symbols-outlined">trending_up</span>${a.impact}</div></div><div class="act-item__actions"><button class="btn-act btn-act--approve" onclick="this.closest('.act-item').style.opacity='0.4';this.closest('.act-item').style.pointerEvents='none';">Approve</button><button class="btn-act btn-act--decline" onclick="this.closest('.act-item').style.opacity='0.4';this.closest('.act-item').style.pointerEvents='none';">Decline</button></div></div></div>`;
      });
    }

    if (d.executed.length > 0) {
      html += '<div class="camp-section-label">Executed Overnight</div>';
      d.executed.forEach(e => {
        html += `<div style="padding:8px 0;border-bottom:1px solid var(--act-border-light);font-size:14px;color:var(--act-text);display:flex;justify-content:space-between"><span>${e.text}</span><span style="font-size:12px;opacity:0.7">${e.time}</span></div>`;
      });
    }

    // Lever status
    html += '<div class="camp-section-label">Lever Status</div><div class="lever-summary">';
    d.levers.forEach((l, i) => {
      html += `<div class="lever-summary-row" data-lever="${i}"><span class="material-symbols-outlined">${l.icon}</span><div style="flex:1"><div class="lever-summary__name">${l.name}</div><div class="lever-summary__status">${l.status}</div><div class="lever-summary__cooldown">${l.cooldown}</div><div class="lever-summary__detail">${l.detail}</div></div><span class="material-symbols-outlined lever-summary__chevron">chevron_right</span></div>`;
    });
    html += '</div>';

    // Strategy summary
    html += '<div class="camp-section-label">Bid Strategy</div>';
    html += `<div class="strategy-compact"><div style="display:flex;align-items:center;gap:12px;margin-bottom:4px"><div class="strategy-compact__target">${d.stratTarget}</div><span class="zone-badge zone-badge--${d.cpaZone}">${d.cpaDetail}</span></div><div class="strategy-compact__detail">${d.stratAssess}</div></div>`;

    // Full detail button
    html += '<button class="btn-full-detail" onclick="alert(\'Would navigate to full Campaign Detail page\')"><span class="material-symbols-outlined">open_in_new</span>View Full Detail</button>';

    if (campBody) campBody.innerHTML = html;

    // Bind lever row expand
    campBody.querySelectorAll('.lever-summary-row').forEach(row => {
      row.addEventListener('click', () => row.classList.toggle('expanded'));
    });

    campOverlay?.classList.add('open');
    campPanel?.classList.add('open');
  }

  function closeCampSlidein() {
    campOverlay?.classList.remove('open');
    campPanel?.classList.remove('open');
  }

  campOverlay?.addEventListener('click', closeCampSlidein);
  document.getElementById('campSlideinClose')?.addEventListener('click', closeCampSlidein);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeCampSlidein(); });

  // Bind campaign name clicks in table
  document.querySelectorAll('.campaign-name-link').forEach(link => {
    link.addEventListener('click', () => openCampSlidein(link.textContent.trim()));
  });

  // Toast
  function showToast(message, type = 'info') {
    document.querySelectorAll('.act-toast').forEach(t => t.remove());
    const toast = document.createElement('div');
    toast.className = `act-toast act-toast--${type}`;
    toast.innerHTML = `<span class="material-symbols-outlined" style="font-size:18px">${
      type === 'success' ? 'check_circle' : type === 'warning' ? 'undo' : type === 'error' ? 'error' : 'info'
    }</span>${message}`;
    document.body.appendChild(toast);
    requestAnimationFrame(() => { requestAnimationFrame(() => toast.classList.add('show')); });
    setTimeout(() => { toast.classList.remove('show'); setTimeout(() => toast.remove(), 300); }, 3000);
  }
});
