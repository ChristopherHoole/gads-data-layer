/* ============================================================================
   ACT PROTOTYPE — KEYWORD LEVEL (Page 6)
   Chart, table, filters, slide-in with 4 unique variants,
   bid history, search term analysis, quality score breakdown.
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
          if (ctx) ctx.textContent = `— 142 keywords, ${days} days`;
          buildChart();
          updateTable(currentRange);
          showToast(`Showing ${btn.textContent.trim()} data`, 'info');
        }
        if (btn.dataset.filter) filterKeywords(btn.dataset.filter);
      });
    });
  });

  function filterKeywords(filter) {
    document.querySelectorAll('#keywordsTable tbody tr').forEach(row => {
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

  // ── Main page See Details — INLINE expand (not slide-in) ────────────────
  document.querySelectorAll('#sectionApproval [data-action="details"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const item = btn.closest('.act-item');
      if (!item) return;
      const kwName = item.dataset.kw;
      const entry = KW_DATA[kwName];
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
  // TABLE DATA — 20 keywords (showing top 20 of 142)
  // ═════════════════════════════════════════════════════════════════════════

  function qsClass(qs) { return qs < 4 ? 'low' : qs <= 6 ? 'mid' : 'high'; }

  function mkRows(scale) {
    const base = [
      // v2 Fix 3 + 4: pending discovery row shown at top so it's visible with rowsPerPage=20
      { kw: 'dental implant clinic london', match: 'phrase', camp: 'GLO Campaign — Core',       ag: 'Long Tail',        maxCpc: 7.50, qs: 0, cost30: 144, impr30: 1620, clicks30: 84, conv30: 8, flags: 1, flagType: 'discovery', status: 'pending' },
      { kw: 'planning objection',          match: 'exact',  camp: 'Brand — Objection Experts', ag: 'Main Brand Terms', maxCpc: 2.50, qs: 8, cost30: 45, impr30: 1420, clicks30: 98, conv30: 2 },
      { kw: 'planning objections',         match: 'exact',  camp: 'Brand — Objection Experts', ag: 'Main Brand Terms', maxCpc: 2.40, qs: 7, cost30: 38, impr30: 1180, clicks30: 82, conv30: 1 },
      { kw: 'dental implants london',      match: 'phrase', camp: 'GLO Campaign — Core',       ag: 'Core Terms',       maxCpc: 8.20, qs: 6, cost30: 52, impr30: 960,  clicks30: 48, conv30: 2 },
      { kw: 'cosmetic dentist',            match: 'exact',  camp: 'GLO Campaign — Core',       ag: 'Core Terms',       maxCpc: 6.50, qs: 7, cost30: 48, impr30: 1040, clicks30: 62, conv30: 2 },
      { kw: 'veneers near me',             match: 'phrase', camp: 'GLO Campaign — Core',       ag: 'Competitor Terms', maxCpc: 7.80, qs: 5, cost30: 62, impr30: 820,  clicks30: 54, conv30: 0 },
      { kw: 'tooth replacement cost',      match: 'exact',  camp: 'GLO Campaign — Core',       ag: 'Core Terms',       maxCpc: 5.20, qs: 3, cost30: 38, impr30: 640,  clicks30: 42, conv30: 1, flags: 1, flagType: 'qs' },
      { kw: 'emergency dentist',           match: 'exact',  camp: 'GLO Campaign — Core',       ag: 'Core Terms',       maxCpc: 9.40, qs: 8, cost30: 68, impr30: 1180, clicks30: 78, conv30: 4 },
      { kw: 'teeth whitening',             match: 'broad',  camp: 'GLO Campaign — Core',       ag: 'Core Terms',       maxCpc: 4.50, qs: 6, cost30: 42, impr30: 1340, clicks30: 92, conv30: 2 },
      { kw: 'full mouth restoration',      match: 'exact',  camp: 'GLO Campaign — Core',       ag: 'Long Tail',        maxCpc: 11.20, qs: 7, cost30: 56, impr30: 480,  clicks30: 32, conv30: 2 },
      { kw: 'dental implant cost',         match: 'phrase', camp: 'GLO Campaign — Core',       ag: 'Long Tail',        maxCpc: 7.50, qs: 5, cost30: 48, impr30: 860,  clicks30: 58, conv30: 2 },
      { kw: 'best dentist london',         match: 'exact',  camp: 'GLO Campaign — Core',       ag: 'Competitor Terms', maxCpc: 8.60, qs: 4, cost30: 55, impr30: 720,  clicks30: 48, conv30: 1, flags: 1, flagType: 'qs' },
      { kw: 'planning permission objection', match: 'exact', camp: 'Brand — Objection Experts', ag: 'Brand + Service', maxCpc: 2.80, qs: 8, cost30: 22, impr30: 820,  clicks30: 48, conv30: 1 },
      { kw: 'dentist near me',             match: 'phrase', camp: 'GLO Campaign — Core',       ag: 'Retargeting Terms', maxCpc: 5.80, qs: 6, cost30: 38, impr30: 1240, clicks30: 78, conv30: 2 },
      { kw: 'invisalign braces',           match: 'exact',  camp: 'GLO Campaign — Core',       ag: 'Long Tail',        maxCpc: 10.50, qs: 7, cost30: 42, impr30: 560,  clicks30: 38, conv30: 2 },
      { kw: 'dental consultation free',    match: 'phrase', camp: 'Testing — New Keywords',    ag: 'Test Batch 3',     maxCpc: 4.20, qs: 2, cost30: 125, impr30: 2840, clicks30: 182, conv30: 0, flags: 1, flagType: 'pause' },
      { kw: 'dental implants',             match: 'exact',  camp: 'GLO Campaign — Core',       ag: 'Long Tail',        maxCpc: 7.20, qs: 6, cost30: 38, impr30: 680,  clicks30: 48, conv30: 1, flags: 1, flagType: 'conflict' },
      { kw: 'tooth pain emergency',        match: 'exact',  camp: 'GLO Campaign — Core',       ag: 'Core Terms',       maxCpc: 8.80, qs: 8, cost30: 72, impr30: 1040, clicks30: 72, conv30: 4 },
      { kw: 'white fillings',              match: 'phrase', camp: 'GLO Campaign — Core',       ag: 'Long Tail',        maxCpc: 3.80, qs: 6, cost30: 28, impr30: 920,  clicks30: 58, conv30: 1 },
      { kw: 'crown dental cost',           match: 'exact',  camp: 'GLO Campaign — Core',       ag: 'Core Terms',       maxCpc: 5.60, qs: 4, cost30: 68, impr30: 780,  clicks30: 52, conv30: 0, flags: 1, flagType: 'pause' },
      { kw: 'wisdom tooth removal',        match: 'exact',  camp: 'GLO Campaign — Core',       ag: 'Long Tail',        maxCpc: 6.20, qs: 7, cost30: 44, impr30: 720,  clicks30: 48, conv30: 2 },
    ];
    return base.map(r => {
      const cost = r.cost30 * scale;
      const clicks = Math.round(r.clicks30 * scale);
      const impr = Math.round(r.impr30 * scale);
      const conv = Math.round(r.conv30 * scale);
      return {
        ...r,
        status: r.status || 'enabled',
        cost: '£' + cost.toFixed(2),
        impr: impr.toLocaleString(),
        clicks: clicks.toLocaleString(),
        avgCpc: clicks > 0 ? '£' + (cost / clicks).toFixed(2) : '—',
        ctr: impr > 0 ? ((clicks / impr) * 100).toFixed(2) + '%' : '0.00%',
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

  function flagBadgeHtml(type, kwName) {
    if (!type) return '';
    const labels = { pause: 'Pause Candidate', discovery: 'Keyword Discovery', conflict: 'Keyword Conflict', qs: 'Low QS' };
    return `<span class="flag-count-badge flag-count-badge--${type}" data-kw="${kwName}" title="Click to view details"><span class="material-symbols-outlined">flag</span>${labels[type] || type}</span>`;
  }

  // v2 Fix 2: match type as plain text (no coloured pill)
  function matchText(m) {
    return m.charAt(0).toUpperCase() + m.slice(1);
  }

  function qsBadgeHtml(qs) {
    if (!qs) return '<span style="opacity:0.5">&mdash;</span>';
    return `<span class="qs-badge qs-badge--${qsClass(qs)}">${qs}</span>`;
  }

  // v2 Fix 1: rows-per-page state
  let rowsPerPage = 20;

  function updateTable(range) {
    const rows = TABLE_DATA[range];
    const tbody = document.querySelector('#keywordsTable tbody');
    if (!tbody || !rows) return;
    tbody.innerHTML = '';

    // v2 Fix 1: slice to first N rows based on rowsPerPage
    const visibleRows = rows.slice(0, rowsPerPage);

    visibleRows.forEach(r => {
      const tr = document.createElement('tr');
      // v2 Fix 3: pending status for discovery items
      tr.dataset.status = r.status;
      const dotClass = r.status === 'pending' ? 'pending' : r.status;
      tr.innerHTML = `
        <td><span class="status-dot status-dot--${dotClass}"></span></td>
        <td><span class="keyword-name-link" data-kw="${r.kw}">${r.kw}</span></td>
        <td><span class="kw-match-text">${matchText(r.match)}</span></td>
        <td><span class="kw-meta-text">${r.camp}</span></td>
        <td><span class="kw-meta-text">${r.ag}</span></td>
        <td>£${r.maxCpc.toFixed(2)}</td>
        <td>${qsBadgeHtml(r.qs)}</td>
        <td>${r.cost}</td>
        <td>${r.impr}</td>
        <td>${r.clicks}</td>
        <td>${r.avgCpc}</td>
        <td>${r.ctr}</td>
        <td>${r.conv}</td>
        <td>${r.costConv}</td>
        <td>${r.cvr}</td>
        <td>${r.flags > 0 ? flagBadgeHtml(r.flagType, r.kw) : ''}</td>`;
      tbody.appendChild(tr);
    });

    // Totals row — keep structural metadata columns empty for plain-text cols
    const totals = document.createElement('tr');
    totals.className = 'totals-row';
    const s = SUMMARY_DATA[range];
    totals.innerHTML = `<td></td><td>Total / Average</td><td></td><td></td><td></td><td></td><td>6.2</td>
      <td>${s.cost}</td><td>${s.impr}</td><td>${s.clicks}</td>
      <td>${s.cpc}</td><td>${s.ctr}</td><td>${s.conv}</td>
      <td>${s.cpa}</td><td>${s.cvr}</td><td></td>`;
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

    bindKeywordClicks();

    // v2 Fix 4: pagination count reflects visible rows against total 142
    const total = 142;
    const shown = Math.min(rowsPerPage, visibleRows.length);
    const info = document.getElementById('paginationInfo');
    if (info) info.textContent = `Showing 1-${shown} of ${total} keywords`;

    // Rebuild page buttons based on rowsPerPage
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
      line1: '#8b5cf6', // purple — keyword level
      line2: '#10b981', // green
      fill1: 'rgba(139,92,246,0.08)',
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
          // v3 Fix 4: fill disabled — clean line chart only, no area under lines
          { label: m1Def.label, data: m1Data, borderColor: c.line1, backgroundColor: c.fill1, fill: false, tension: 0,
            pointRadius: 3, pointHoverRadius: 5, pointBackgroundColor: c.line1, pointBorderColor: c.line1, borderWidth: 2, yAxisID: 'y1' },
          { label: m2Def.label, data: m2Data, borderColor: c.line2, backgroundColor: c.fill2, fill: false, tension: 0,
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
          // v3 Fix 3: horizontal gridlines only — no vertical gridlines
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

  // v2 Fix 1: rows-per-page dropdown
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
  // KEYWORD SLIDE-IN — 4 unique variants + generic default
  // ═════════════════════════════════════════════════════════════════════════

  const KW_DATA = {
    'dental consultation free': {
      match: 'phrase', camp: 'Testing — New Keywords', ag: 'Test Batch 3', status: 'enabled',
      cost: '£125', cpa: '—', cpaZone: 'underperforming', cpaDetail: '0 conv in 72 days',
      conv: '0', qs: 2,
      approvals: [{
        text: '<strong>Pause &ldquo;dental consultation free&rdquo;</strong> &mdash; 0 conversions in 72 days.',
        rec: 'ACT recommends: Pause and consolidate budget to performing keywords in this ad group.',
        impact: 'Saves £52/month if paused',
        timeWaiting: 'Identified 2 hours ago',
        flagType: 'pause', flagLabel: 'Pause Candidate', risk: 'medium',
        details: {
          Check:    'Keyword Pause Recommendations (runs overnight, 60+ day dead keyword window)',
          Signal:   'Zero conversions for 72 days while consuming £125 of campaign budget. Far beyond the 60-day dead keyword threshold.',
          Rule:     'Dead keyword with >60 days zero conversions. Flagged for human pause decision — pause is impactful and requires approval.',
          Cooldown: 'No cooldown — pause action is binary (pause or don\'t).',
          Risk:     'Medium — pausing affects traffic flow but this keyword has proven to convert nothing.'
        }
      }],
      executed: [],
      monitoring: [],
      alerts: [],
      bidHistory: [
        { date: '1 Apr 2026', change: '£4.60 → £4.20', delta: '-8.7%', dir: 'down', reason: 'Zero conversions — 10% reduction (cycle cap)' },
        { date: '28 Mar 2026', change: '£5.10 → £4.60', delta: '-9.8%', dir: 'down', reason: 'Zero conversions — 10% reduction (cycle cap)' },
        { date: '25 Mar 2026', change: '£5.60 → £5.10', delta: '-8.9%', dir: 'down', reason: 'Zero conversions — 10% reduction (cycle cap)' },
        { date: '22 Mar 2026', change: '£6.20 → £5.60', delta: '-9.7%', dir: 'down', reason: '7-day cap hit, continued reduction' },
        { date: '19 Mar 2026', change: '£6.80 → £6.20', delta: '-8.8%', dir: 'down', reason: 'Zero conversions — 10% reduction (cycle cap)' },
      ],
      searchTerms: [
        { term: 'free dental consultation uk',        cost: '£28', conv: '0', cpa: '—' },
        { term: 'free dental checkup',                cost: '£22', conv: '0', cpa: '—' },
        { term: 'dental consultation free nhs',       cost: '£18', conv: '0', cpa: '—' },
        { term: 'where to get free dental checkup',   cost: '£14', conv: '0', cpa: '—' },
        { term: 'free dental consultation near me',   cost: '£12', conv: '0', cpa: '—' },
        { term: 'dental advice free',                 cost: '£10', conv: '0', cpa: '—' },
        { term: 'free dentist appointment',           cost: '£8',  conv: '0', cpa: '—' },
        { term: 'cheap dental consultation',          cost: '£7',  conv: '0', cpa: '—' },
        { term: 'free dental check up london',        cost: '£4',  conv: '0', cpa: '—' },
        { term: 'free dentistry',                     cost: '£2',  conv: '0', cpa: '—' },
      ],
      qsBreakdown: {
        expectedCtr: 'below',
        adRelevance: 'below',
        landingPage: 'below',
        overall: 2,
      },
    },
    'dental implant clinic london': {
      match: 'phrase', camp: 'GLO Campaign — Core', ag: 'Long Tail', status: 'pending',
      cost: '£144', costSubtitle: 'from search term data',
      cpa: '£18.00', cpaSubtitle: 'from search term data', cpaZone: 'projected', cpaDetail: 'Projected',
      conv: '8', convSubtitle: 'from search term data', qs: null,
      approvals: [{
        text: '<strong>Add &ldquo;dental implant clinic london&rdquo; as phrase match to Dental Implants ad group.</strong> Discovered from search terms with 8 conversions at £18 CPA over 30 days.',
        rec: 'ACT recommends: Add as phrase match keyword to capture this traffic intentionally.',
        impact: 'Estimated: +8 conversions/month at £18 CPA',
        timeWaiting: 'Identified 4 hours ago',
        flagType: 'discovery', flagLabel: 'Keyword Discovery', risk: 'low',
        details: {
          Check:    'Search Term Mining — Keyword Discovery (runs overnight, 14+ day window)',
          Signal:   '8 conversions at £18.00 CPA vs £25.00 target (28% below) sustained over 30 days. Proven converter not being explicitly bid on.',
          Rule:     'Search term with 2+ conversions below target CPA for 14+ days. Flagged to add as phrase match keyword.',
          Cooldown: 'No cooldown — keyword addition is a one-time action.',
          Risk:     'Low — adding a proven converter carries minimal downside.'
        }
      }],
      executed: [],
      monitoring: [],
      alerts: [],
      bidHistory: [],
      searchTerms: [
        { term: 'dental implant clinic london',       cost: '£48', conv: '3', cpa: '£16.00' },
        { term: 'dental implant clinic central london', cost: '£32', conv: '2', cpa: '£16.00' },
        { term: 'dental implant clinic west london',  cost: '£22', conv: '1', cpa: '£22.00' },
        { term: 'london dental implant clinic',       cost: '£18', conv: '1', cpa: '£18.00' },
        { term: 'best dental implant clinic london',  cost: '£14', conv: '1', cpa: '£14.00' },
        { term: 'dental implant clinic near london',  cost: '£10', conv: '0', cpa: '—' },
      ],
      qsBreakdown: {
        expectedCtr: 'average',
        adRelevance: 'average',
        landingPage: 'above',
        overall: '—',
      },
    },
    'dental implants': {
      match: 'exact', camp: 'GLO Campaign — Core', ag: 'Long Tail', status: 'enabled',
      cost: '£38', cpa: '£38.00', cpaZone: 'ontarget', cpaDetail: 'Within target — On Target',
      conv: '1', qs: 6,
      approvals: [{
        text: '<strong>&ldquo;dental implants&rdquo; running in 2 ad groups &mdash; Dental Implants and Cosmetic Dentistry.</strong> Cannibalising impressions across ad groups.',
        rec: 'ACT recommends: Consolidate into one ad group and add as negative in the other to resolve conflict.',
        impact: 'Resolve cannibalisation across 2 ad groups',
        timeWaiting: 'Identified 1 day ago',
        flagType: 'conflict', flagLabel: 'Keyword Conflict', risk: 'medium',
        details: {
          Check:    'Keyword Conflicts & Cannibalisation (runs overnight, all keyword-based campaigns)',
          Signal:   '"dental implants" [exact] appears in 2 different ad groups in GLO Campaign — Core. Both are active and serving impressions. Cannibalisation detected.',
          Rule:     'Same keyword in different ad groups/campaigns = flag. Same ad group different match = OK.',
          Cooldown: 'No cooldown — conflict resolution is a one-time action.',
          Risk:     'Medium — consolidating affects which ads show for this query. Human decision on which ad group keeps it.'
        }
      }],
      executed: [],
      monitoring: [],
      alerts: [
        { text: '<strong>Keyword cannibalisation detected:</strong> "dental implants" running in 2 ad groups.', date: '2 Apr 2026' },
      ],
      bidHistory: [
        { date: '5 Apr 2026', change: '£6.50 → £7.20', delta: '+10.8%', dir: 'up', reason: 'Outperforming — 10% increase (cycle cap)' },
        { date: '1 Apr 2026', change: '£5.90 → £6.50', delta: '+10.2%', dir: 'up', reason: 'Below target CPA — 10% increase' },
      ],
      searchTerms: [
        { term: 'dental implants',                    cost: '£18', conv: '1', cpa: '£18.00' },
        { term: 'dental implants uk',                  cost: '£8',  conv: '0', cpa: '—' },
        { term: 'dental implants cost uk',             cost: '£6',  conv: '0', cpa: '—' },
        { term: 'dental implants procedure',           cost: '£4',  conv: '0', cpa: '—' },
        { term: 'dental implants before and after',    cost: '£2',  conv: '0', cpa: '—' },
      ],
      qsBreakdown: {
        expectedCtr: 'average',
        adRelevance: 'above',
        landingPage: 'average',
        overall: 6,
      },
      conflicts: [
        'Dental Implants (current ad group) — 48 clicks, 1 conversion, £38 cost',
        'Cosmetic Dentistry (conflicting ad group) — 32 clicks, 0 conversions, £22 cost',
      ],
    },
    'tooth replacement cost': {
      match: 'exact', camp: 'GLO Campaign — Core', ag: 'Core Terms', status: 'enabled',
      cost: '£38', cpa: '£38.00', cpaZone: 'underperforming', cpaDetail: '52% above target — Underperforming',
      conv: '1', qs: 3,
      approvals: [{
        text: '<strong>&ldquo;tooth replacement cost&rdquo; QS dropped from 6 to 3 in 7 days.</strong> Investigate ad relevance and landing page experience.',
        rec: 'ACT recommends: Review ad copy for keyword relevance and check landing page load speed and content alignment.',
        impact: 'Restore QS to reduce CPC by ~15%',
        timeWaiting: 'Identified 2 days ago',
        flagType: 'qs', flagLabel: 'Low QS', risk: 'medium',
        details: {
          Check:    'Quality Score Monitoring (weekly scan, editable per client)',
          Signal:   'Quality score dropped from 6 to 3 in a 7-day window. Expected CTR: Below Average, Ad Relevance: Below Average, Landing Page Experience: Average.',
          Rule:     'QS below 4 requires human review. ACT cannot fix this — improving QS requires human action on ad copy or landing page.',
          Cooldown: 'Weekly scan cooldown. Not re-flagged until next scheduled scan.',
          Risk:     'Medium — low QS penalises auction performance and increases CPC. Human action required.'
        }
      }],
      executed: [],
      monitoring: [],
      alerts: [],
      bidHistory: [
        { date: '3 Apr 2026', change: '£5.80 → £5.20', delta: '-10.3%', dir: 'down', reason: 'CPA above target — 10% reduction (cycle cap)' },
      ],
      searchTerms: [
        { term: 'tooth replacement cost',              cost: '£12', conv: '1', cpa: '£12.00' },
        { term: 'tooth replacement cost uk',           cost: '£8',  conv: '0', cpa: '—' },
        { term: 'tooth replacement cost london',       cost: '£6',  conv: '0', cpa: '—' },
        { term: 'tooth replacement cost average',      cost: '£5',  conv: '0', cpa: '—' },
        { term: 'how much does a tooth replacement cost', cost: '£4', conv: '0', cpa: '—' },
        { term: 'single tooth replacement cost',       cost: '£3',  conv: '0', cpa: '—' },
      ],
      qsBreakdown: {
        expectedCtr: 'below',
        adRelevance: 'below',
        landingPage: 'average',
        overall: 3,
      },
    },
  };

  const DEFAULT_KW = KW_DATA['dental consultation free'];

  const kwOverlay = document.getElementById('kwSlideinOverlay');
  const kwPanel   = document.getElementById('kwSlidein');
  const kwBody    = document.getElementById('kwSlideinBody');
  const kwName    = document.getElementById('kwSlideinName');
  const kwMeta    = document.getElementById('kwSlideinMeta');

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

  function qsValueClass(label) {
    return label === 'above' ? 'above' : label === 'average' ? 'average' : 'below';
  }
  function qsValueLabel(label) {
    return label === 'above' ? 'Above Average' : label === 'average' ? 'Average' : 'Below Average';
  }

  function openKwSlidein(kw) {
    const d = KW_DATA[kw] || DEFAULT_KW;
    const displayName = KW_DATA[kw] ? kw : 'dental consultation free';
    if (kwName) kwName.textContent = displayName;
    // v2 Fix 7: order is Status → Match → Campaign → Ad Group
    // v2 Fix 8: meta is plain text (no coloured badges)
    const statusLabel = d.status === 'pending' ? 'Pending approval' : 'Enabled';
    const statusDotClass = d.status === 'pending' ? 'pending' : d.status;
    if (kwMeta) kwMeta.innerHTML = `
      <span class="kw-status-inline"><span class="status-dot status-dot--${statusDotClass}"></span> ${statusLabel}</span>
      <span class="kw-meta-sep">·</span>
      <span class="kw-meta-text">${matchText(d.match)} match</span>
      <span class="kw-meta-sep">·</span>
      <span class="kw-meta-text">${d.camp}</span>
      <span class="kw-meta-sep">·</span>
      <span class="kw-meta-text">${d.ag}</span>`;

    let html = '';

    // Health cards (4 in a row)
    // v2 Fix 9, 10, 11, 12: tidy subtitles, projected zone badge for discovery CPA,
    // "Pending" QS card for keywords without a score yet.
    const isPending = d.status === 'pending';
    html += '<div class="kw-health-grid">';

    // Cost card (Fix 10: subtitle for discovery)
    html += `<div class="kw-health-card"><div class="kw-health-card__label">Cost (MTD)</div><div class="kw-health-card__value">${d.costValue || d.cost}</div>${d.costSubtitle ? `<div class="kw-health-card__subtitle">${d.costSubtitle}</div>` : ''}</div>`;

    // CPA card (Fix 9: shorter subtitle; Fix 11: projected badge for discovery)
    const cpaColor = d.cpaZone === 'outperforming' ? '#10b981' : d.cpaZone === 'underperforming' ? '#ef4444' : d.cpaZone === 'projected' ? '#3b82f6' : '#3b82f6';
    html += `<div class="kw-health-card"><div class="kw-health-card__label">CPA</div><div class="kw-health-card__value" style="color:${cpaColor}">${d.cpa}</div>${d.cpaSubtitle ? `<div class="kw-health-card__subtitle">${d.cpaSubtitle}</div>` : ''}${d.cpaDetail ? `<div class="kw-health-card__detail"><span class="zone-badge zone-badge--${d.cpaZone}">${d.cpaDetail}</span></div>` : ''}</div>`;

    html += `<div class="kw-health-card"><div class="kw-health-card__label">Conversions (MTD)</div><div class="kw-health-card__value">${d.conv}</div>${d.convSubtitle ? `<div class="kw-health-card__subtitle">${d.convSubtitle}</div>` : ''}</div>`;

    // QS card (Fix 12: "Pending" for discovery)
    if (typeof d.qs === 'number') {
      const qsColor = d.qs < 4 ? '#ef4444' : d.qs <= 6 ? '#f59e0b' : '#10b981';
      html += `<div class="kw-health-card"><div class="kw-health-card__label">Quality Score</div><div class="kw-health-card__value" style="color:${qsColor}">${d.qs}<span style="font-size:14px;opacity:0.5"> / 10</span></div></div>`;
    } else {
      html += `<div class="kw-health-card"><div class="kw-health-card__label">Quality Score</div><div class="kw-health-card__value kw-health-card__value--pending">Not yet assigned</div><div class="kw-health-card__subtitle">New keyword &mdash; no QS yet</div></div>`;
    }
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
            ${a.details ? `<div class="slidein-detail-expand" id="kwSlideinDetail${idx}">${detailGrid}</div>` : ''}
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
    const executedBody = (d.executed || []).map(e => {
      return `<div class="act-item"><div class="act-item__row"><div class="act-item__content"><div class="act-item__top"><span class="badge-action badge-action--act">Act</span><span class="act-item__timestamp">${e.time}</span></div><div class="act-item__summary">${e.text}${e.reason ? `<span class="act-item__reason-inline">${e.reason}</span>` : ''}</div></div></div></div>`;
    }).join('');
    html += slideinSection({
      icon: 'check_circle', iconColor: 'var(--act-green)',
      title: 'Actions Executed Overnight', count: (d.executed || []).length, countBg: 'var(--act-green)',
      collapsed: true, bodyHtml: executedBody,
      emptyIcon: 'bedtime', emptyText: 'No actions were executed overnight.',
      isEmpty: !d.executed || d.executed.length === 0
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

    // ── BID HISTORY (collapsed) — unique to Keyword Level ─────────────────
    const bidList = d.bidHistory || [];
    let bidBody = '<div class="slidein-section__inner">';
    if (bidList.length === 0) {
      bidBody += '<div class="slidein-empty-state"><span class="material-symbols-outlined">history</span><div class="slidein-empty-state__text">No bid changes recorded.</div></div>';
    } else {
      bidBody += '<table class="bid-history-table"><thead><tr><th>Date</th><th>Change</th><th>Delta</th><th>Reason</th></tr></thead><tbody>';
      bidList.forEach(h => {
        bidBody += `<tr><td>${h.date}</td><td>${h.change}</td><td><span class="bid-change bid-change--${h.dir}">${h.delta}</span></td><td>${h.reason}</td></tr>`;
      });
      bidBody += '</tbody></table>';
    }
    bidBody += '</div>';
    html += slideinSection({
      icon: 'history', iconColor: '#8b5cf6',
      title: 'Bid History', collapsed: true, bodyHtml: bidBody, isEmpty: false
    });

    // ── SEARCH TERM ANALYSIS (collapsed) — unique to Keyword Level ────────
    let stBody = '<div class="slidein-section__inner">';
    stBody += '<table class="search-term-table"><thead><tr><th>Search Term</th><th style="width:80px">Cost</th><th style="width:60px">Conv</th><th style="width:80px">CPA</th></tr></thead><tbody>';
    (d.searchTerms || []).forEach(s => {
      stBody += `<tr><td title="${s.term}">${s.term}</td><td>${s.cost}</td><td>${s.conv}</td><td>${s.cpa}</td></tr>`;
    });
    stBody += '</tbody></table>';
    stBody += '</div>';
    html += slideinSection({
      icon: 'search', iconColor: '#8b5cf6',
      title: 'Search Term Analysis', collapsed: true, bodyHtml: stBody, isEmpty: false
    });

    // ── QUALITY SCORE BREAKDOWN (collapsed) — unique to Keyword Level ─────
    const qs = d.qsBreakdown;
    let qsBody = '<ul class="qs-breakdown">';
    qsBody += `<li><span class="material-symbols-outlined">ads_click</span><span class="qs-breakdown__factor">Expected CTR</span><span class="qs-breakdown__value qs-breakdown__value--${qsValueClass(qs.expectedCtr)}">${qsValueLabel(qs.expectedCtr)}</span></li>`;
    qsBody += `<li><span class="material-symbols-outlined">article</span><span class="qs-breakdown__factor">Ad Relevance</span><span class="qs-breakdown__value qs-breakdown__value--${qsValueClass(qs.adRelevance)}">${qsValueLabel(qs.adRelevance)}</span></li>`;
    qsBody += `<li><span class="material-symbols-outlined">web</span><span class="qs-breakdown__factor">Landing Page Experience</span><span class="qs-breakdown__value qs-breakdown__value--${qsValueClass(qs.landingPage)}">${qsValueLabel(qs.landingPage)}</span></li>`;
    qsBody += `<li class="qs-breakdown__overall"><span class="material-symbols-outlined">star</span><span class="qs-breakdown__factor">Overall Quality Score</span><span class="qs-breakdown__value qs-breakdown__value--${typeof qs.overall === 'number' ? (qs.overall < 4 ? 'below' : qs.overall <= 6 ? 'average' : 'above') : 'average'}">${qs.overall}${typeof qs.overall === 'number' ? ' / 10' : ''}</span></li>`;
    qsBody += '</ul>';
    html += slideinSection({
      icon: 'star', iconColor: '#8b5cf6',
      title: 'Quality Score Breakdown', collapsed: true, bodyHtml: qsBody, isEmpty: false
    });

    if (kwBody) kwBody.innerHTML = html;

    // Bind slide-in section toggle clicks
    kwBody.querySelectorAll('.slidein-section__header').forEach(header => {
      header.addEventListener('click', (e) => {
        if (e.target.closest('.btn-see-details') || e.target.closest('.btn-act')) return;
        header.closest('.slidein-section').classList.toggle('collapsed');
      });
    });

    // Bind See Details / Hide Details toggle (inline expand inside slide-in)
    kwBody.querySelectorAll('.btn-see-details').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const idx = btn.dataset.detailIdx;
        const panel = document.getElementById('kwSlideinDetail' + idx);
        if (panel) {
          panel.classList.toggle('show');
          btn.textContent = panel.classList.contains('show') ? 'Hide Details' : 'See Details';
        }
      });
    });

    kwOverlay?.classList.add('open');
    kwPanel?.classList.add('open');
  }

  window.closeKwSlidein = function() {
    kwOverlay?.classList.remove('open');
    kwPanel?.classList.remove('open');
  };
  kwOverlay?.addEventListener('click', closeKwSlidein);
  document.getElementById('kwSlideinClose')?.addEventListener('click', closeKwSlidein);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeKwSlidein(); });

  function bindKeywordClicks() {
    document.querySelectorAll('.keyword-name-link').forEach(link => {
      link.addEventListener('click', () => openKwSlidein(link.dataset.kw));
    });
    document.querySelectorAll('#keywordsTable .flag-count-badge').forEach(badge => {
      badge.addEventListener('click', () => openKwSlidein(badge.dataset.kw));
    });
  }
  bindKeywordClicks();

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
