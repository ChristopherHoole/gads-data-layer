/* ============================================================================
   ACT PROTOTYPE — AD LEVEL (Page 7)
   Chart (no fill, no vertical gridlines), table, 4 unique slide-in variants,
   ad preview, asset performance, extensions status.
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

  // ── Section collapse ─────────────────────────────────────────────────────
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

  // ── Pill buttons ─────────────────────────────────────────────────────────
  document.querySelectorAll('.pill-group').forEach(group => {
    group.querySelectorAll('.pill-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        group.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        if (btn.dataset.range) {
          currentRange = btn.dataset.range;
          const days = currentRange === '7d' ? '7' : currentRange === '30d' ? '30' : '90';
          const ctx = document.getElementById('perfContext');
          if (ctx) ctx.textContent = `— 42 ads, ${days} days`;
          buildChart();
          updateTable(currentRange);
          showToast(`Showing ${btn.textContent.trim()} data`, 'info');
        }
        if (btn.dataset.filter) filterAds(btn.dataset.filter);
      });
    });
  });

  function filterAds(filter) {
    document.querySelectorAll('#adsTable tbody tr').forEach(row => {
      if (row.classList.contains('totals-row')) return;
      if (filter === 'all') { row.style.display = ''; return; }
      const status = row.dataset.status;
      row.style.display = (status === filter) ? '' : 'none';
    });
  }

  // ── Approve / Decline ────────────────────────────────────────────────────
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-action="approve"], [data-action="decline"]');
    if (!btn) return;
    e.stopPropagation();
    const item = btn.closest('.act-item');
    if (item) { item.style.opacity = '0.4'; item.style.pointerEvents = 'none'; }
    if (btn.dataset.action === 'approve') showToast('Approved — change will be applied in next cycle', 'success');
    else showToast('Declined — no changes will be made', 'info');
  });

  // ── Main page See Details — INLINE expand ───────────────────────────────
  document.querySelectorAll('#sectionApproval [data-action="details"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const item = btn.closest('.act-item');
      if (!item) return;
      const adName = item.dataset.ad;
      const entry = AD_DATA[adName];
      const details = entry?.approvals?.[0]?.details;
      if (!details) return;

      let expand = item.querySelector('.slidein-detail-expand');
      if (!expand) {
        expand = document.createElement('div');
        expand.className = 'slidein-detail-expand';
        let grid = '<dl class="act-detail-grid">';
        for (const [k, v] of Object.entries(details)) grid += `<dt>${k}</dt><dd>${v}</dd>`;
        grid += '</dl>';
        expand.innerHTML = grid;
        const rec = item.querySelector('.act-item__recommendation');
        rec?.parentNode.insertBefore(expand, rec.nextSibling);
      }

      expand.classList.toggle('show');
      btn.textContent = expand.classList.contains('show') ? 'Hide Details' : 'See Details';
    });
  });

  // ═════════════════════════════════════════════════════════════════════════
  // PERFORMANCE TIMELINE CHART
  // ═════════════════════════════════════════════════════════════════════════

  let currentRange = '30d';

  function makeDailyLabels(days) {
    const labels = [];
    const d = new Date(2026, 3, 9);
    for (let i = days - 1; i >= 0; i--) {
      const dt = new Date(d); dt.setDate(d.getDate() - i);
      labels.push(dt.getDate() + ' ' + ['Jan','Feb','Mar','Apr','May'][dt.getMonth()]);
    }
    return labels;
  }
  function makeWeeklyLabels(weeks) {
    const labels = [];
    const d = new Date(2026, 3, 9);
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
  // TABLE DATA — 20 sample ads (of 42 total)
  // ═════════════════════════════════════════════════════════════════════════

  function mkRows(scale) {
    // days fields only scale for cost-like metrics; daysLive is absolute
    const base = [
      { ad: 'Fast Planning Results',          type: 'RSA',       strength: 'good',      camp: 'GLO Campaign — Core',       ag: 'Planning Objections',     status: 'disapproved', impr30: 0,    clicks30: 0,  conv30: 0, cpc: 0.64, days: 42, flags: 1, flagType: 'disapproval' },
      { ad: 'Expert Planning Help',           type: 'RSA',       strength: 'poor',      camp: 'GLO Campaign — Core',       ag: 'Planning Objections',     status: 'enabled',     impr30: 2420, clicks30: 142, conv30: 3, cpc: 0.68, days: 35, flags: 1, flagType: 'ad-strength' },
      { ad: 'Planning Objection Experts',     type: 'RSA',       strength: 'good',      camp: 'GLO Campaign — Core',       ag: 'Planning Objections',     status: 'enabled',     impr30: 3120, clicks30: 214, conv30: 6, cpc: 0.62, days: 72 },
      { ad: 'Planning Objection Letters',     type: 'RSA',       strength: 'average',   camp: 'GLO Campaign — Core',       ag: 'Planning Objection Letters', status: 'enabled',  impr30: 1840, clicks30: 96,  conv30: 2, cpc: 0.64, days: 32, flags: 1, flagType: 'asset-perf' },
      { ad: 'Objection Letter Writing',       type: 'RSA',       strength: 'good',      camp: 'GLO Campaign — Core',       ag: 'Planning Objection Letters', status: 'enabled',  impr30: 1620, clicks30: 82,  conv30: 3, cpc: 0.58, days: 58 },
      { ad: 'Neighbour Planning Objections',  type: 'RSA',       strength: 'good',      camp: 'GLO Campaign — Core',       ag: 'Neighbourhood Objections', status: 'enabled',    impr30: 1340, clicks30: 78,  conv30: 2, cpc: 0.61, days: 45 },
      { ad: 'Stop Neighbour Planning',        type: 'RSA',       strength: 'average',   camp: 'GLO Campaign — Core',       ag: 'Neighbourhood Objections', status: 'enabled',    impr30: 980,  clicks30: 54,  conv30: 1, cpc: 0.65, days: 38 },
      { ad: 'Objection Experts Official',     type: 'RSA',       strength: 'excellent', camp: 'Brand — Objection Experts', ag: 'Main Brand Terms',         status: 'enabled',    impr30: 1820, clicks30: 132, conv30: 2, cpc: 0.35, days: 120 },
      { ad: '600+ Objections Prepared',       type: 'RSA',       strength: 'good',      camp: 'Brand — Objection Experts', ag: 'Main Brand Terms',         status: 'enabled',    impr30: 1240, clicks30: 88,  conv30: 1, cpc: 0.36, days: 90 },
      { ad: 'Call Objection Experts',         type: 'Call Only', strength: 'good',      camp: 'Brand — Objection Experts', ag: 'Main Brand Terms',         status: 'enabled',    impr30: 480,  clicks30: 42,  conv30: 2, cpc: 0.33, days: 60 },
      { ad: 'Consultation Available',         type: 'RSA',       strength: 'good',      camp: 'GLO Campaign — Core',       ag: 'Planning Objections',     status: 'enabled',     impr30: 450,  clicks30: 14,  conv30: 0, cpc: 0.72, days: 25, flags: 1, flagType: 'performance' },
      { ad: 'Free Consultation Offered',      type: 'RSA',       strength: 'good',      camp: 'GLO Campaign — Core',       ag: 'Planning Objections',     status: 'enabled',     impr30: 1120, clicks30: 76,  conv30: 3, cpc: 0.63, days: 42 },
      { ad: 'Book Your Consultation',         type: 'RSA',       strength: 'excellent', camp: 'GLO Campaign — Core',       ag: 'Planning Objections',     status: 'enabled',     impr30: 1540, clicks30: 108, conv30: 4, cpc: 0.59, days: 55 },
      { ad: '5-Day Turnaround Objections',    type: 'RSA',       strength: 'good',      camp: 'GLO Campaign — Core',       ag: 'Long Tail',               status: 'enabled',     impr30: 1280, clicks30: 86,  conv30: 3, cpc: 0.66, days: 48 },
      { ad: 'RTPI Qualified Planner',         type: 'RSA',       strength: 'good',      camp: 'GLO Campaign — Core',       ag: 'Long Tail',               status: 'enabled',     impr30: 1120, clicks30: 74,  conv30: 2, cpc: 0.67, days: 52 },
      { ad: 'From £350+VAT',                  type: 'RSA',       strength: 'average',   camp: 'GLO Campaign — Core',       ag: 'Long Tail',               status: 'enabled',     impr30: 820,  clicks30: 44,  conv30: 1, cpc: 0.70, days: 30 },
      { ad: 'Come Back — Special Offer',      type: 'RSA',       strength: 'good',      camp: 'GLO Campaign — Retargeting', ag: 'Recent Visitors',        status: 'enabled',     impr30: 1620, clicks30: 124, conv30: 5, cpc: 0.67, days: 65 },
      { ad: 'Your Planning Objection',        type: 'RSA',       strength: 'good',      camp: 'GLO Campaign — Retargeting', ag: 'Cart Abandoners',        status: 'enabled',     impr30: 960,  clicks30: 73,  conv30: 5, cpc: 0.67, days: 48 },
      { ad: 'New Brand RSA',                  type: 'RSA',       strength: 'learning',  camp: 'Testing — New Keywords',    ag: 'Test Batch 2',             status: 'enabled',    impr30: 280,  clicks30: 11,  conv30: 1, cpc: 1.60, days: 3 },
      { ad: 'Test Ad Variant A',              type: 'RSA',       strength: 'average',   camp: 'Testing — New Keywords',    ag: 'Test Batch 4',             status: 'enabled',    impr30: 280,  clicks30: 11,  conv30: 0, cpc: 1.55, days: 18 },
    ];
    return base.map(r => {
      const impr = Math.round(r.impr30 * scale);
      const clicks = Math.round(r.clicks30 * scale);
      const conv = Math.round(r.conv30 * scale);
      // v2 Fix 1: use the base cpc value to derive per-row cost + avg CPC.
      // Each row has its own base CPC so the table shows realistic variance.
      const baseCpc = r.cpc || 0.64;
      const cost = clicks * baseCpc;
      return {
        ...r,
        cost: clicks > 0 ? '£' + cost.toFixed(2) : '£0.00',
        impr: impr.toLocaleString(),
        clicks: clicks.toLocaleString(),
        avgCpc: clicks > 0 ? '£' + baseCpc.toFixed(2) : '—',
        ctr: impr > 0 ? ((clicks / impr) * 100).toFixed(2) + '%' : '—',
        conv,
        costConv: conv > 0 ? '£' + (cost / conv).toFixed(2) : '—',
        cvr: clicks > 0 ? ((conv / clicks) * 100).toFixed(2) + '%' : '0.00%',
        flags: r.flags || 0,
      };
    });
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

  function flagCountBadgeHtml(type, adName) {
    if (!type) return '';
    const labels = {
      disapproval: 'Disapproval', 'ad-strength': 'Ad Strength', 'asset-perf': 'Asset Performance',
      'ad-count': 'Ad Count', performance: 'Performance', extensions: 'Extensions'
    };
    return `<span class="flag-count-badge flag-count-badge--${type}" data-ad="${adName}" title="Click to view details"><span class="material-symbols-outlined">flag</span>${labels[type] || type}</span>`;
  }

  function adStrengthBadgeHtml(strength) {
    const labels = { excellent: 'Excellent', good: 'Good', average: 'Average', poor: 'Poor', learning: 'Learning' };
    return `<span class="ad-strength-badge ad-strength-badge--${strength}">${labels[strength]}</span>`;
  }

  let rowsPerPage = 20;

  function updateTable(range) {
    const rows = TABLE_DATA[range];
    const tbody = document.querySelector('#adsTable tbody');
    if (!tbody || !rows) return;
    tbody.innerHTML = '';

    const visibleRows = rows.slice(0, rowsPerPage);

    visibleRows.forEach(r => {
      const tr = document.createElement('tr');
      tr.dataset.status = r.status;
      const dotClass = r.status === 'disapproved' ? 'disapproved' : r.status;
      tr.innerHTML = `
        <td><span class="status-dot status-dot--${dotClass}"></span></td>
        <td><span class="ad-name-link" data-ad="${r.ad}">${r.ad}</span></td>
        <td><span class="ad-type-text">${r.type}</span></td>
        <td>${adStrengthBadgeHtml(r.strength)}</td>
        <td><span class="ad-meta-text">${r.camp}</span></td>
        <td><span class="ad-meta-text">${r.ag}</span></td>
        <td>${r.cost}</td>
        <td>${r.impr}</td>
        <td>${r.clicks}</td>
        <td>${r.avgCpc}</td>
        <td>${r.ctr}</td>
        <td>${r.conv}</td>
        <td>${r.costConv}</td>
        <td>${r.cvr}</td>
        <td>${r.days}</td>
        <td>${r.flags > 0 ? flagCountBadgeHtml(r.flagType, r.ad) : ''}</td>`;
      tbody.appendChild(tr);
    });

    // Totals row — v2 Fix 1: adds Cost and Avg CPC columns
    const totals = document.createElement('tr');
    totals.className = 'totals-row';
    const s = SUMMARY_DATA[range];
    totals.innerHTML = `<td></td><td>Total / Average</td><td></td><td></td><td></td><td></td>
      <td>${s.cost}</td><td>${s.impr}</td><td>${s.clicks}</td><td>${s.cpc}</td><td>${s.ctr}</td>
      <td>${s.conv}</td><td>${s.cpa}</td><td>${s.cvr}</td><td>—</td><td></td>`;
    tbody.appendChild(totals);

    // Update summary cards
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

    bindAdClicks();

    const total = 42;
    const shown = Math.min(rowsPerPage, visibleRows.length);
    const info = document.getElementById('paginationInfo');
    if (info) info.textContent = `Showing 1-${shown} of ${total} ads`;

    // Rebuild page buttons
    const pageButtons = document.getElementById('pageButtons');
    if (pageButtons) {
      const totalPages = Math.ceil(total / rowsPerPage);
      let btnHtml = '<button class="page-btn" disabled>&laquo;</button>';
      const maxBtns = Math.min(totalPages, 5);
      for (let i = 1; i <= maxBtns; i++) {
        btnHtml += `<button class="page-btn${i === 1 ? ' active' : ''}">${i}</button>`;
      }
      btnHtml += `<button class="page-btn"${totalPages <= 1 ? ' disabled' : ''}>&raquo;</button>`;
      pageButtons.innerHTML = btnHtml;
    }
  }

  // ── Chart ────────────────────────────────────────────────────────────────
  const chartCanvas = document.getElementById('performanceChart');
  let perfChart = null;

  function isDark() { return document.documentElement.getAttribute('data-theme') === 'dark'; }

  function getChartColors() {
    const dark = isDark();
    return {
      line1: '#ec4899', // pink — ad level
      line2: '#10b981',
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
          // No fill, no vertical gridlines (matches Keyword Level v3 pattern)
          { label: m1Def.label, data: m1Data, borderColor: c.line1, fill: false, tension: 0,
            pointRadius: 3, pointHoverRadius: 5, pointBackgroundColor: c.line1, pointBorderColor: c.line1, borderWidth: 2, yAxisID: 'y1' },
          { label: m2Def.label, data: m2Data, borderColor: c.line2, fill: false, tension: 0,
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
          x: { grid: { display: false }, ticks: { color: c.text, font: { size: 12 }, maxRotation: 0, autoSkipPadding: 12 }, border: { color: c.border } },
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

  updateTable('30d');
  buildChart();

  document.getElementById('rowsPerPage')?.addEventListener('change', (e) => {
    rowsPerPage = parseInt(e.target.value, 10);
    updateTable(currentRange);
    showToast(`Showing ${rowsPerPage} rows per page`, 'info');
  });

  document.getElementById('chartMetric1')?.addEventListener('change', buildChart);
  document.getElementById('chartMetric2')?.addEventListener('change', buildChart);

  new MutationObserver(() => { setTimeout(buildChart, 50); })
    .observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

  // ═════════════════════════════════════════════════════════════════════════
  // AD SLIDE-IN — 4 unique variants + generic default
  // ═════════════════════════════════════════════════════════════════════════

  // Shared ad preview data (RSA content). The 4 unique variants share the same
  // core dental ad copy but differ in approvals, assets, extensions, etc.
  const BASE_RSA_HEADLINES = [
    { pos: 'Any',        text: 'Expert Planning Objections', rating: 'best' },
    { pos: 'Pos 2',      text: 'RTPI Qualified Planner',     rating: 'good', pinned: true },
    { pos: 'Any',        text: '5-Day Turnaround',           rating: 'good' },
    { pos: 'Any',        text: '600+ Objections Prepared',   rating: 'good' },
    { pos: 'Any',        text: 'From £350 + VAT',            rating: 'good' },
    { pos: 'Any',        text: 'Free Consultation',          rating: 'good' },
    { pos: 'Any',        text: 'Written by Experts',         rating: 'good' },
    { pos: 'Any',        text: 'Object Planning Application',rating: 'good' },
    { pos: 'Any',        text: 'Fast Response Service',      rating: 'good' },
    { pos: 'Any',        text: 'Proven Track Record',        rating: 'good' },
  ];

  const BASE_DESCRIPTIONS = [
    { text: 'Professional planning objection letters written by RTPI-qualified planners. 5-day turnaround.', rating: 'good' },
    { text: 'Over 600 successful objections. Fixed fee from £350+VAT. Free initial consultation available.', rating: 'good' },
    { text: 'Stop that planning application affecting your home. Expert help, fast response, proven results.', rating: 'good' },
    { text: 'Book your free consultation today. Written objection delivered in 5 working days.', rating: 'good' },
  ];

  const AD_DATA = {
    'Fast Planning Results': {
      type: 'RSA', camp: 'GLO Campaign — Core', ag: 'Planning Objections', status: 'disapproved',
      strength: 'good',
      impr: '0', ctr: '—', conv: '0', costConv: '—',
      imprDetail: 'Paused due to disapproval',
      approvals: [{
        text: '<strong>&ldquo;Fast Planning Results&rdquo; disapproved for misleading content.</strong> Requires headline edit and resubmission.',
        rec: 'ACT recommends: Remove or replace headline 4 &ldquo;Guaranteed Results&rdquo; which violates misleading content policy.',
        impact: 'Restore ad serving',
        timeWaiting: 'Identified 3 hours ago',
        flagType: 'disapproval', flagLabel: 'Disapproval', risk: 'high',
        details: {
          Check:    'Ad Disapprovals (daily scan)',
          Signal:   'Headline 4 "Guaranteed Results" flagged by Google Ads for "Misleading content" policy. Ad stopped serving at 02:14 AM.',
          Rule:     'Disapproved ads are flagged immediately — daily scan. Requires human edit and resubmission.',
          Cooldown: 'No cooldown — resubmission required.',
          Risk:     'High — ad is not serving. Every hour of delay loses impression share.'
        }
      }],
      executed: [],
      monitoring: [],
      alerts: [
        { text: '<strong>Previous disapproval resolved</strong> on 7 Apr 2026 after headline edit. Re-flagged today for new issue.', date: '7 Apr 2026' },
      ],
      preview: {
        title: 'Expert Planning Objections | RTPI Qualified | 5-Day Turnaround',
        url: 'www.objectionexperts.com',
        desc: 'Professional planning objection letters written by RTPI-qualified planners. 5-day turnaround.',
        headlines: [
          { pos: 'Any',   text: 'Expert Planning Objections', status: 'active' },
          { pos: 'Pos 2', text: 'RTPI Qualified',             status: 'pinned' },
          { pos: 'Any',   text: '5-Day Turnaround',           status: 'active' },
          { pos: 'Any',   text: 'Guaranteed Results',         status: 'flagged' },
          { pos: 'Any',   text: 'From £350 + VAT',            status: 'active' },
          { pos: 'Any',   text: '600+ Objections Won',        status: 'active' },
          { pos: 'Any',   text: 'Free Consultation',          status: 'active' },
        ],
        descriptions: [
          { text: 'Professional planning objection letters written by RTPI-qualified planners. 5-day turnaround.', status: 'active' },
          { text: 'Over 600 successful objections. Fixed fee from £350+VAT. Free initial consultation available.', status: 'active' },
        ],
      },
      assets: [
        { asset: 'Expert Planning Objections', type: 'Headline',    pos: 'Any',   status: 'Active',      rating: 'best' },
        { asset: 'RTPI Qualified',             type: 'Headline',    pos: 'Pos 2', status: 'Active',      rating: 'good' },
        { asset: '5-Day Turnaround',           type: 'Headline',    pos: 'Any',   status: 'Active',      rating: 'good' },
        { asset: 'Guaranteed Results',         type: 'Headline',    pos: 'Any',   status: 'Disapproved', rating: 'flagged' },
        { asset: 'From £350 + VAT',            type: 'Headline',    pos: 'Any',   status: 'Active',      rating: 'good' },
        { asset: '600+ Objections Won',        type: 'Headline',    pos: 'Any',   status: 'Active',      rating: 'good' },
        { asset: 'Professional planning objection letters…', type: 'Description', pos: '—', status: 'Active', rating: 'good' },
        { asset: 'Over 600 successful objections…',         type: 'Description', pos: '—', status: 'Active', rating: 'good' },
      ],
      extensions: {
        sitelinks:  { count: 4, required: 4, ok: true },
        callouts:   { count: 6, required: 4, ok: true },
        snippets:   { count: 2, required: 1, ok: true },
        callExt:    { active: true, tracked: true, ok: true },
      },
    },
    'Expert Planning Help': {
      type: 'RSA', camp: 'GLO Campaign — Core', ag: 'Planning Objections', status: 'enabled',
      strength: 'poor',
      impr: '2,420', ctr: '5.87%', conv: '3', costConv: '£30.29',
      approvals: [{
        text: '<strong>&ldquo;Expert Planning Help&rdquo; ad strength is Poor after 35 days live.</strong> 2 headlines rated Low.',
        rec: 'ACT recommends: Replace headlines 4 and 7 with new variations to improve ad strength.',
        impact: 'Improve ad performance and Quality Score',
        timeWaiting: 'Identified 1 day ago',
        flagType: 'ad-strength', flagLabel: 'Ad Strength', risk: 'medium',
        details: {
          Check:    'Ad Strength Monitoring (weekly scan)',
          Signal:   'Ad strength rating: Poor. 2 of 10 headlines rated Low by Google Ads after 30+ days live. Specifically headlines 4 and 7.',
          Rule:     'Ad strength below "Good" flagged for human review. ACT cannot write new headlines — human copy edit required.',
          Cooldown: 'No cooldown — re-scanned weekly.',
          Risk:     'Medium — poor ad strength reduces Quality Score and increases CPC.'
        }
      }],
      executed: [],
      monitoring: [],
      alerts: [
        { text: '<strong>Ad strength alert:</strong> Flagged for Poor rating on 5 Apr 2026. Under review.', date: '5 Apr 2026' },
      ],
      preview: {
        title: 'Expert Planning Help | Professional Objections | Fast',
        url: 'www.objectionexperts.com/help',
        desc: 'Expert help with planning objections. RTPI qualified, fast turnaround, proven results.',
        headlines: [
          { pos: 'Any',   text: 'Expert Planning Help',       status: 'active' },
          { pos: 'Pos 1', text: 'Professional Planners',      status: 'pinned' },
          { pos: 'Any',   text: 'RTPI Qualified Expert',      status: 'active' },
          { pos: 'Any',   text: 'Help Fast',                  status: 'low' },
          { pos: 'Any',   text: 'Objection Service',          status: 'active' },
          { pos: 'Any',   text: 'Planning Law Experts',       status: 'active' },
          { pos: 'Any',   text: 'We Help',                    status: 'low' },
          { pos: 'Any',   text: 'Expert Advice Available',    status: 'active' },
        ],
        descriptions: [
          { text: 'Expert help with planning objections. RTPI qualified, fast turnaround, proven results.', status: 'active' },
          { text: 'Stop that planning application. Get expert help from qualified planners. Free consultation.', status: 'active' },
        ],
      },
      assets: [
        { asset: 'Expert Planning Help',       type: 'Headline',    pos: 'Any',   status: 'Active', rating: 'good' },
        { asset: 'Professional Planners',      type: 'Headline',    pos: 'Pos 1', status: 'Active', rating: 'good' },
        { asset: 'RTPI Qualified Expert',      type: 'Headline',    pos: 'Any',   status: 'Active', rating: 'good' },
        { asset: 'Help Fast',                  type: 'Headline',    pos: 'Any',   status: 'Active', rating: 'low' },
        { asset: 'Objection Service',          type: 'Headline',    pos: 'Any',   status: 'Active', rating: 'good' },
        { asset: 'Planning Law Experts',       type: 'Headline',    pos: 'Any',   status: 'Active', rating: 'good' },
        { asset: 'We Help',                    type: 'Headline',    pos: 'Any',   status: 'Active', rating: 'low' },
        { asset: 'Expert Advice Available',    type: 'Headline',    pos: 'Any',   status: 'Active', rating: 'good' },
      ],
      extensions: {
        sitelinks:  { count: 4, required: 4, ok: true },
        callouts:   { count: 4, required: 4, ok: true },
        snippets:   { count: 1, required: 1, ok: true },
        callExt:    { active: true, tracked: true, ok: true },
      },
    },
    'Planning Objection Letters': {
      type: 'RSA', camp: 'GLO Campaign — Core', ag: 'Planning Objection Letters', status: 'enabled',
      strength: 'average',
      impr: '1,840', ctr: '5.22%', conv: '2', costConv: '£30.72',
      approvals: [{
        text: '<strong>3 assets in &ldquo;Planning Objection Letters&rdquo; RSA rated Low for 32 days.</strong> Consider replacing.',
        rec: 'ACT recommends: Replace low-rated headlines to improve asset diversity and performance.',
        impact: 'Improve asset diversity and CTR',
        timeWaiting: 'Identified 2 days ago',
        flagType: 'asset-perf', flagLabel: 'Asset Performance', risk: 'low',
        details: {
          Check:    'RSA Asset Performance (weekly scan, 30+ day window)',
          Signal:   '3 headlines rated "Low" by Google Ads for 32 consecutive days. Headlines 5, 8 and 9 are the weakest performers.',
          Rule:     'RSA assets rated Low for 30+ days flagged for human replacement review.',
          Cooldown: 'No cooldown — re-scanned weekly.',
          Risk:     'Low — the RSA still has enough strong assets to serve effectively, but diversity would improve performance.'
        }
      }],
      executed: [],
      monitoring: [],
      alerts: [],
      preview: {
        title: 'Planning Objection Letters | Professional Service',
        url: 'www.objectionexperts.com/letters',
        desc: 'Professional planning objection letters. RTPI qualified, 5-day delivery, from £350+VAT.',
        headlines: [
          { pos: 'Any',   text: 'Planning Objection Letters', status: 'active' },
          { pos: 'Any',   text: 'RTPI Qualified',             status: 'active' },
          { pos: 'Any',   text: '5-Day Delivery',             status: 'active' },
          { pos: 'Any',   text: 'Professional Service',       status: 'active' },
          { pos: 'Any',   text: 'Letter Writing Service',     status: 'low' },
          { pos: 'Any',   text: 'From £350+VAT',              status: 'active' },
          { pos: 'Any',   text: 'Free Consultation',          status: 'active' },
          { pos: 'Any',   text: 'Object to Planning',         status: 'low' },
          { pos: 'Any',   text: 'Written Objections',         status: 'low' },
          { pos: 'Any',   text: 'Expert Advice',              status: 'active' },
        ],
        descriptions: [
          { text: 'Professional planning objection letters. RTPI qualified, 5-day delivery, from £350+VAT.', status: 'active' },
          { text: 'Expert help objecting to planning applications. Free consultation, fast turnaround.', status: 'active' },
        ],
      },
      assets: [
        { asset: 'Planning Objection Letters', type: 'Headline', pos: 'Any', status: 'Active', rating: 'good' },
        { asset: 'RTPI Qualified',             type: 'Headline', pos: 'Any', status: 'Active', rating: 'best' },
        { asset: '5-Day Delivery',             type: 'Headline', pos: 'Any', status: 'Active', rating: 'good' },
        { asset: 'Professional Service',       type: 'Headline', pos: 'Any', status: 'Active', rating: 'good' },
        { asset: 'Letter Writing Service',     type: 'Headline', pos: 'Any', status: 'Active', rating: 'low' },
        { asset: 'From £350+VAT',              type: 'Headline', pos: 'Any', status: 'Active', rating: 'good' },
        { asset: 'Free Consultation',          type: 'Headline', pos: 'Any', status: 'Active', rating: 'good' },
        { asset: 'Object to Planning',         type: 'Headline', pos: 'Any', status: 'Active', rating: 'low' },
        { asset: 'Written Objections',         type: 'Headline', pos: 'Any', status: 'Active', rating: 'low' },
        { asset: 'Expert Advice',              type: 'Headline', pos: 'Any', status: 'Active', rating: 'good' },
      ],
      extensions: {
        sitelinks:  { count: 4, required: 4, ok: true },
        callouts:   { count: 5, required: 4, ok: true },
        snippets:   { count: 1, required: 1, ok: true },
        callExt:    { active: true, tracked: true, ok: true },
      },
    },
    'Consultation Available': {
      type: 'RSA', camp: 'GLO Campaign — Core', ag: 'Planning Objections', status: 'enabled',
      strength: 'good',
      impr: '450', ctr: '3.11%', conv: '0', costConv: '—',
      approvals: [{
        text: '<strong>&ldquo;Consultation Available&rdquo; ad is 35% worse CTR than ad group average.</strong> 25 days live, 450 impressions.',
        rec: 'ACT recommends: Review ad copy or pause to let better performers take more impression share.',
        impact: 'Shift impression share to better performers',
        timeWaiting: 'Identified 2 days ago',
        flagType: 'performance', flagLabel: 'Performance', risk: 'low',
        details: {
          Check:    'Ad Performance Comparison (weekly scan, 21+ days live, 100+ impressions)',
          Signal:   'CTR of 3.11% vs ad group average 4.78% (35% worse). 450 impressions in 25 days — above the 100 minimum for comparison.',
          Rule:     'Ads 30%+ worse than ad group average (after 21+ days live and 100+ impressions) flagged for human review.',
          Cooldown: 'No cooldown — re-scanned weekly.',
          Risk:     'Low — pausing one underperforming ad in a 3+ ad rotation has minimal downside.'
        }
      }],
      executed: [],
      monitoring: [],
      alerts: [],
      preview: {
        title: 'Consultation Available | Planning Objections | Book Now',
        url: 'www.objectionexperts.com/consultation',
        desc: 'Book a free consultation with our planning experts. RTPI qualified, fast response.',
        headlines: [
          { pos: 'Any',   text: 'Consultation Available',     status: 'active' },
          { pos: 'Any',   text: 'Book Free Consultation',     status: 'active' },
          { pos: 'Any',   text: 'Planning Experts',           status: 'active' },
          { pos: 'Any',   text: 'RTPI Qualified',             status: 'active' },
          { pos: 'Any',   text: 'Fast Response',              status: 'active' },
          { pos: 'Any',   text: 'Expert Planning Advice',     status: 'active' },
          { pos: 'Any',   text: 'Speak to Planner',           status: 'active' },
          { pos: 'Any',   text: 'Objection Service',          status: 'active' },
        ],
        descriptions: [
          { text: 'Book a free consultation with our planning experts. RTPI qualified, fast response.', status: 'active' },
          { text: 'Get expert advice on your planning objection. Free initial consultation available.', status: 'active' },
        ],
      },
      assets: [
        { asset: 'Consultation Available',   type: 'Headline', pos: 'Any', status: 'Active', rating: 'good' },
        { asset: 'Book Free Consultation',   type: 'Headline', pos: 'Any', status: 'Active', rating: 'good' },
        { asset: 'Planning Experts',         type: 'Headline', pos: 'Any', status: 'Active', rating: 'best' },
        { asset: 'RTPI Qualified',           type: 'Headline', pos: 'Any', status: 'Active', rating: 'good' },
        { asset: 'Fast Response',            type: 'Headline', pos: 'Any', status: 'Active', rating: 'good' },
        { asset: 'Expert Planning Advice',   type: 'Headline', pos: 'Any', status: 'Active', rating: 'good' },
        { asset: 'Speak to Planner',         type: 'Headline', pos: 'Any', status: 'Active', rating: 'good' },
        { asset: 'Objection Service',        type: 'Headline', pos: 'Any', status: 'Active', rating: 'good' },
      ],
      extensions: {
        sitelinks:  { count: 4, required: 4, ok: true },
        callouts:   { count: 4, required: 4, ok: true },
        snippets:   { count: 1, required: 1, ok: true },
        callExt:    { active: true, tracked: true, ok: true },
      },
    },
  };

  const DEFAULT_AD = AD_DATA['Fast Planning Results'];

  const adOverlay = document.getElementById('adSlideinOverlay');
  const adPanel   = document.getElementById('adSlidein');
  const adBody    = document.getElementById('adSlideinBody');
  const adName    = document.getElementById('adSlideinName');
  const adMeta    = document.getElementById('adSlideinMeta');

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

  function statusLabelFor(status) {
    if (status === 'disapproved') return 'Disapproved';
    if (status === 'paused') return 'Paused';
    return 'Enabled';
  }
  function statusDotClass(status) {
    if (status === 'disapproved') return 'disapproved';
    if (status === 'paused') return 'paused';
    return 'enabled';
  }

  function openAdSlidein(ad) {
    const d = AD_DATA[ad] || DEFAULT_AD;
    const displayName = AD_DATA[ad] ? ad : 'Fast Planning Results';
    if (adName) adName.textContent = displayName;
    if (adMeta) adMeta.innerHTML = `
      <span class="ad-status-inline"><span class="status-dot status-dot--${statusDotClass(d.status)}"></span> ${statusLabelFor(d.status)}</span>
      <span class="ad-meta-sep">·</span>
      <span class="ad-meta-text-inline">${d.type}</span>
      <span class="ad-meta-sep">·</span>
      <span class="ad-meta-text-inline">${d.camp}</span>
      <span class="ad-meta-sep">·</span>
      <span class="ad-meta-text-inline">${d.ag}</span>
      <span class="ad-meta-sep">·</span>
      ${adStrengthBadgeHtml(d.strength)}`;

    let html = '';

    // Health cards (4 in a row) — Impressions, CTR, Conversions, Cost/Conv
    html += '<div class="ad-health-grid">';
    html += `<div class="ad-health-card"><div class="ad-health-card__label">Impressions (MTD)</div><div class="ad-health-card__value">${d.impr}</div>${d.imprDetail ? `<div class="ad-health-card__detail">${d.imprDetail}</div>` : ''}</div>`;
    html += `<div class="ad-health-card"><div class="ad-health-card__label">CTR</div><div class="ad-health-card__value">${d.ctr}</div></div>`;
    html += `<div class="ad-health-card"><div class="ad-health-card__label">Conversions (MTD)</div><div class="ad-health-card__value">${d.conv}</div></div>`;
    html += `<div class="ad-health-card"><div class="ad-health-card__label">Cost / Conv</div><div class="ad-health-card__value">${d.costConv}</div></div>`;
    html += '</div>';

    // ── AWAITING APPROVAL (expanded, always shown) ────────────────────────
    const approvalsBody = d.approvals.map((a, idx) => {
      let detailGrid = '';
      if (a.details) {
        detailGrid = '<dl class="act-detail-grid">';
        for (const [k, v] of Object.entries(a.details)) detailGrid += `<dt>${k}</dt><dd>${v}</dd>`;
        detailGrid += '</dl>';
      }
      const actionLabel = a.risk === 'high' ? 'Alert' : 'Investigate';
      const actionClass = a.risk === 'high' ? 'alert' : 'investigate';
      const priorityAttr = a.risk === 'high' ? 'alert' : 'investigate';
      return `<div class="act-item" data-priority="${priorityAttr}">
        <div class="act-item__row">
          <div class="act-item__content">
            <div class="act-item__top">
              <span class="badge-action badge-action--${actionClass}">${actionLabel}</span>
              <span class="badge-risk badge-risk--${a.risk}">${a.risk.charAt(0).toUpperCase() + a.risk.slice(1)} Risk</span>
              <span class="flag-badge flag-badge--${a.flagType}">${a.flagLabel}</span>
              ${a.timeWaiting ? `<span class="act-item__waiting"><span class="material-symbols-outlined">schedule</span>${a.timeWaiting}</span>` : ''}
              <span class="act-item__impact"><span class="material-symbols-outlined">trending_up</span>${a.impact}</span>
            </div>
            <div class="act-item__summary">${a.text}</div>
            <div class="act-item__recommendation"><span class="material-symbols-outlined">lightbulb</span>${a.rec}</div>
            ${a.details ? `<div class="slidein-detail-expand" id="adSlideinDetail${idx}">${detailGrid}</div>` : ''}
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

    // ── ACTIONS EXECUTED OVERNIGHT (always empty at Ad Level) ─────────────
    html += slideinSection({
      icon: 'check_circle', iconColor: 'var(--act-green)',
      title: 'Actions Executed Overnight', count: 0, countBg: 'var(--act-green)',
      collapsed: true, bodyHtml: '',
      emptyIcon: 'bedtime', emptyText: 'No actions were executed overnight.',
      isEmpty: true
    });

    // ── CURRENTLY MONITORING ──────────────────────────────────────────────
    const monList = d.monitoring || [];
    html += slideinSection({
      icon: 'visibility', iconColor: 'var(--act-blue)',
      title: 'Currently Monitoring', count: monList.length, countBg: 'var(--act-blue)',
      collapsed: true, bodyHtml: '',
      emptyIcon: 'visibility_off', emptyText: 'Nothing is currently being monitored.',
      isEmpty: monList.length === 0
    });

    // ── RECENT ALERTS ─────────────────────────────────────────────────────
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

    // ── AD PREVIEW (unique) ───────────────────────────────────────────────
    const p = d.preview;
    let previewBody = '<div class="slidein-section__inner">';
    previewBody += '<div class="ad-preview">';
    previewBody += '<div class="ad-preview__sponsored">Sponsored · Objection Experts</div>';
    previewBody += `<div class="ad-preview__title">${p.title}</div>`;
    previewBody += `<div class="ad-preview__url">${p.url}</div>`;
    previewBody += `<div class="ad-preview__desc">${p.desc}</div>`;
    previewBody += '</div>';

    previewBody += '<hr class="ad-preview-divider">';
    previewBody += '<div class="ad-preview__heading">Headlines (' + p.headlines.length + ')</div>';
    previewBody += '<ul class="ad-preview-list">';
    p.headlines.forEach((h, i) => {
      let statusBadge = '';
      let warnIcon = '';
      if (h.status === 'flagged') {
        statusBadge = '<span class="ad-preview-list__status ad-preview-list__status--flagged">Disapproved</span>';
        warnIcon = '<span class="material-symbols-outlined ad-preview-list__warning">warning</span>';
      } else if (h.status === 'pinned' || h.pos.startsWith('Pos')) {
        statusBadge = `<span class="ad-preview-list__status ad-preview-list__status--pinned">Pinned</span>`;
      } else if (h.status === 'low') {
        statusBadge = '<span class="ad-preview-list__status ad-preview-list__status--flagged">Low</span>';
      }
      previewBody += `<li><span class="ad-preview-list__pos">${h.pos}</span><span class="ad-preview-list__text">H${i+1}: ${h.text}</span>${statusBadge}${warnIcon}</li>`;
    });
    previewBody += '</ul>';

    previewBody += '<div class="ad-preview__heading">Descriptions (' + p.descriptions.length + ')</div>';
    previewBody += '<ul class="ad-preview-list">';
    p.descriptions.forEach((ds, i) => {
      previewBody += `<li><span class="ad-preview-list__pos">D${i+1}</span><span class="ad-preview-list__text">${ds.text}</span></li>`;
    });
    previewBody += '</ul>';
    previewBody += '</div>';

    html += slideinSection({
      icon: 'ad_units', iconColor: '#ec4899',
      title: 'Ad Preview', collapsed: true, bodyHtml: previewBody, isEmpty: false
    });

    // ── ASSET PERFORMANCE (unique) ────────────────────────────────────────
    let assetBody = '<div class="slidein-section__inner">';
    assetBody += '<table class="asset-perf-table"><thead><tr><th style="width:40%">Asset</th><th style="width:18%">Type</th><th style="width:14%">Status</th><th style="width:14%">Rating</th></tr></thead><tbody>';
    (d.assets || []).forEach(a => {
      assetBody += `<tr><td title="${a.asset}">${a.asset}</td><td>${a.type}</td><td>${a.status}</td><td><span class="asset-perf-rating asset-perf-rating--${a.rating}">${a.rating === 'flagged' ? 'Policy Violation' : a.rating.charAt(0).toUpperCase() + a.rating.slice(1)}</span></td></tr>`;
    });
    assetBody += '</tbody></table></div>';
    html += slideinSection({
      icon: 'analytics', iconColor: '#ec4899',
      title: 'Asset Performance', collapsed: true, bodyHtml: assetBody, isEmpty: false
    });

    // ── EXTENSIONS STATUS (unique) ────────────────────────────────────────
    const ext = d.extensions;
    let extBody = '<ul class="extensions-status">';
    function extLi(icon, label, val, ok) {
      const iconName = ok ? 'check_circle' : 'cancel';
      const iconClass = ok ? 'extensions-status__icon--ok' : 'extensions-status__icon--miss';
      return `<li><span class="material-symbols-outlined ${iconClass}">${iconName}</span><span class="extensions-status__label">${label}</span><span class="extensions-status__value">${val}</span></li>`;
    }
    extBody += extLi('link',         'Sitelinks',      `${ext.sitelinks.count} of ${ext.sitelinks.required}+ required`,  ext.sitelinks.ok);
    extBody += extLi('chat',         'Callouts',       `${ext.callouts.count} of ${ext.callouts.required}+ required`,   ext.callouts.ok);
    extBody += extLi('list',         'Snippets',       `${ext.snippets.count} of ${ext.snippets.required}+ required`,   ext.snippets.ok);
    extBody += extLi('call',         'Call extension', ext.callExt.active ? (ext.callExt.tracked ? 'Active (tracking enabled)' : 'Active (no tracking)') : 'Not set', ext.callExt.ok);
    extBody += '</ul>';
    html += slideinSection({
      icon: 'extension', iconColor: '#ec4899',
      title: 'Extensions Status', collapsed: true, bodyHtml: extBody, isEmpty: false
    });

    if (adBody) adBody.innerHTML = html;

    // Bind slide-in section toggle clicks
    adBody.querySelectorAll('.slidein-section__header').forEach(header => {
      header.addEventListener('click', (e) => {
        if (e.target.closest('.btn-see-details') || e.target.closest('.btn-act')) return;
        header.closest('.slidein-section').classList.toggle('collapsed');
      });
    });

    // Bind See Details / Hide Details toggle (inline expand inside slide-in)
    adBody.querySelectorAll('.btn-see-details').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const idx = btn.dataset.detailIdx;
        const panel = document.getElementById('adSlideinDetail' + idx);
        if (panel) {
          panel.classList.toggle('show');
          btn.textContent = panel.classList.contains('show') ? 'Hide Details' : 'See Details';
        }
      });
    });

    adOverlay?.classList.add('open');
    adPanel?.classList.add('open');
  }

  window.closeAdSlidein = function() {
    adOverlay?.classList.remove('open');
    adPanel?.classList.remove('open');
  };
  adOverlay?.addEventListener('click', closeAdSlidein);
  document.getElementById('adSlideinClose')?.addEventListener('click', closeAdSlidein);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeAdSlidein(); });

  function bindAdClicks() {
    document.querySelectorAll('.ad-name-link').forEach(link => {
      link.addEventListener('click', () => openAdSlidein(link.dataset.ad));
    });
    document.querySelectorAll('#adsTable .flag-count-badge').forEach(badge => {
      badge.addEventListener('click', () => openAdSlidein(badge.dataset.ad));
    });
  }
  bindAdClicks();

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
