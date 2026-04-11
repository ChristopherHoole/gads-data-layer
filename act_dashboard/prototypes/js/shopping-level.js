/* ============================================================================
   ACT PROTOTYPE — SHOPPING LEVEL (Page 8 — final level page)
   Chart (no fill, no vertical gridlines), table, 4 unique slide-in variants,
   performance tier breakdown, product group bid history, product feed details.
   Ecommerce persona (ROAS-focused).
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
        let va = a.children[idx]?.textContent.trim().replace(/[£%,x]/g, '') || '';
        let vb = b.children[idx]?.textContent.trim().replace(/[£%,x]/g, '') || '';
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
          if (ctx) ctx.textContent = `— 204 products, ${days} days`;
          buildChart();
          updateTable(currentRange);
          showToast(`Showing ${btn.textContent.trim()} data`, 'info');
        }
        if (btn.dataset.filter) filterProducts('status', btn.dataset.filter);
        if (btn.dataset.tier) filterProducts('tier', btn.dataset.tier);
      });
    });
  });

  let currentStatusFilter = 'all';
  let currentTierFilter = 'all';
  function filterProducts(kind, value) {
    if (kind === 'status') currentStatusFilter = value;
    if (kind === 'tier') currentTierFilter = value;
    document.querySelectorAll('#productsTable tbody tr').forEach(row => {
      if (row.classList.contains('totals-row')) return;
      const status = row.dataset.status;
      const tier = row.dataset.tier;
      const statusMatch = currentStatusFilter === 'all' || status === currentStatusFilter;
      const tierMatch = currentTierFilter === 'all' || tier === currentTierFilter;
      row.style.display = (statusMatch && tierMatch) ? '' : 'none';
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

  // ── Main page See Details — INLINE expand ───────────────────────────────
  document.querySelectorAll('#sectionApproval [data-action="details"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const item = btn.closest('.act-item');
      if (!item) return;
      const prodName = item.dataset.prod;
      const entry = PROD_DATA[prodName];
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
    convValue:   { label: 'Conv. Value',         prefix: '£', suffix: '' },
    roas:        { label: 'ROAS',                prefix: '',  suffix: 'x' },
    aov:         { label: 'AOV',                 prefix: '£', suffix: '' },
  };

  function getChartData(range) {
    if (range === '90d') {
      const n = 13;
      const labels = makeWeeklyLabels(n);
      const dailyCost = seededData(108, 22, 91, true);
      const dailyImpr = seededData(4940, 620, 91, true);
      const dailyClicks = seededData(161, 28, 91, true);
      const dailyConv = seededData(4.7, 1.2, 91, true);
      const dailyCpc = seededData(0.67, 0.08, 91, false);
      const dailyCtr = seededData(3.25, 0.3, 91, false);
      const dailyCpa = seededData(22.8, 3.5, 91, false);
      const dailyCvr = seededData(2.95, 0.35, 91, false);
      const dailyConvValue = seededData(453, 80, 91, true);
      const dailyRoas = seededData(4.2, 0.4, 91, false);
      const dailyAov = seededData(96, 8, 91, false);
      function weeklySum(arr) { const r = []; for (let w = 0; w < n; w++) { let s = 0; for (let d = 0; d < 7 && w*7+d < arr.length; d++) s += arr[w*7+d]; r.push(Math.round(s)); } return r; }
      function weeklyAvg(arr) { const r = []; for (let w = 0; w < n; w++) { let s = 0, c = 0; for (let d = 0; d < 7 && w*7+d < arr.length; d++) { s += arr[w*7+d]; c++; } r.push(Math.round(s/c*100)/100); } return r; }
      return {
        labels,
        metrics: {
          cost: weeklySum(dailyCost), impressions: weeklySum(dailyImpr),
          clicks: weeklySum(dailyClicks), conversions: weeklySum(dailyConv),
          avgCpc: weeklyAvg(dailyCpc), ctr: weeklyAvg(dailyCtr),
          cpa: weeklyAvg(dailyCpa), convRate: weeklyAvg(dailyCvr),
          convValue: weeklySum(dailyConvValue), roas: weeklyAvg(dailyRoas), aov: weeklyAvg(dailyAov),
        }
      };
    }
    const n = range === '7d' ? 7 : 30;
    const labels = makeDailyLabels(n);
    return {
      labels,
      metrics: {
        cost:        seededData(108, 22, n, true),
        impressions: seededData(4940, 620, n, true),
        clicks:      seededData(161, 28, n, true),
        avgCpc:      seededData(0.67, 0.08, n, false),
        ctr:         seededData(3.25, 0.3, n, false),
        conversions: seededData(4.7, 1.2, n, true),
        cpa:         seededData(22.8, 3.5, n, false),
        convRate:    seededData(2.95, 0.35, n, false),
        convValue:   seededData(453, 80, n, true),
        roas:        seededData(4.2, 0.4, n, false),
        aov:         seededData(96, 8, n, false),
      }
    };
  }

  // ═════════════════════════════════════════════════════════════════════════
  // TABLE DATA — 20 sample products (of 204 total)
  // ═════════════════════════════════════════════════════════════════════════

  function tierClass(tier) { return tier; }
  function tierLabel(tier) {
    return { best: 'Best Seller', mid: 'Mid-Range', under: 'Underperformer', loser: 'Loser' }[tier] || tier;
  }

  // ROAS target for Dental Supplies Direct: 4.0x
  // high: >= 4.0, mid: 3.2 – 4.0 (80% of target), low: < 3.2
  function roasClass(roas) {
    if (roas >= 4.0) return 'high';
    if (roas >= 3.2) return 'mid';
    return 'low';
  }

  function mkRows(scale) {
    const base = [
      // Best Sellers (4)
      { prod: 'Premium Implant Kit — Titanium',         sku: 'IMP-TI-001',  cat: 'Implants',                tier: 'best',  cpc: 1.85, impr30: 8420, clicks30: 264, conv30: 18, aov: 450, status: 'enabled' },
      { prod: 'Dental Curing Light UV',                 sku: 'INS-CUR-002', cat: 'Instruments',             tier: 'best',  cpc: 0.85, impr30: 11240, clicks30: 412, conv30: 32, aov: 125, status: 'enabled' },
      { prod: 'Professional Whitening Gel — 10 pack',   sku: 'WHT-GEL-003', cat: 'Whitening',               tier: 'best',  cpc: 0.60, impr30: 14820, clicks30: 548, conv30: 48, aov: 85,  status: 'enabled' },
      { prod: 'Dental Composite Shade Kit',             sku: 'RES-SHD-004', cat: 'Restoration Materials',   tier: 'best',  cpc: 1.40, impr30: 6920,  clicks30: 214, conv30: 16, aov: 220, status: 'enabled' },
      // Mid-Range (8)
      { prod: 'Dental Handpiece — Standard',            sku: 'INS-HND-005', cat: 'Instruments',             tier: 'mid',   cpc: 1.20, impr30: 5240,  clicks30: 178, conv30: 9,  aov: 180, status: 'enabled' },
      { prod: 'Impression Material 500ml',              sku: 'CON-IMP-006', cat: 'Consumables',             tier: 'mid',   cpc: 0.65, impr30: 6820,  clicks30: 238, conv30: 18, aov: 45,  status: 'enabled' },
      { prod: 'Dental Burs Set — 10 piece',             sku: 'INS-BUR-007', cat: 'Instruments',             tier: 'mid',   cpc: 0.55, impr30: 7120,  clicks30: 262, conv30: 22, aov: 65,  status: 'enabled' },
      { prod: 'Anaesthetic Cartridges 50pk',            sku: 'CON-ANS-008', cat: 'Consumables',             tier: 'mid',   cpc: 0.48, impr30: 5920,  clicks30: 214, conv30: 19, aov: 38,  status: 'enabled' },
      { prod: 'Dental Cement — Zinc Phosphate',         sku: 'RES-CEM-009', cat: 'Restoration Materials',   tier: 'mid',   cpc: 0.42, impr30: 5480,  clicks30: 198, conv30: 16, aov: 28,  status: 'enabled' },
      { prod: 'Disposable Bib 500pk',                   sku: 'CON-BIB-010', cat: 'Consumables',             tier: 'mid',   cpc: 0.35, impr30: 8420,  clicks30: 318, conv30: 28, aov: 22,  status: 'enabled' },
      { prod: 'Sterilisation Pouches 200pk',            sku: 'HYG-STE-011', cat: 'Hygiene',                 tier: 'mid',   cpc: 0.38, impr30: 6140,  clicks30: 232, conv30: 19, aov: 18,  status: 'enabled' },
      { prod: 'Dental Mirror Pack 12',                  sku: 'INS-MIR-012', cat: 'Instruments',             tier: 'mid',   cpc: 0.45, impr30: 4620,  clicks30: 168, conv30: 13, aov: 32,  status: 'enabled' },
      // Underperformers (5)
      { prod: 'Premium Dental Loupes 2.5x',             sku: 'INS-LOU-013', cat: 'Instruments',             tier: 'under', cpc: 2.15, impr30: 3820,  clicks30: 94,  conv30: 4,  aov: 380, status: 'enabled', flags: 1, flagType: 'tier-demotion' },
      { prod: 'Ultrasonic Scaler Cartridge',            sku: 'INS-USC-014', cat: 'Instruments',             tier: 'under', cpc: 0.92, impr30: 4120,  clicks30: 132, conv30: 6,  aov: 95,  status: 'enabled' },
      { prod: 'Dental Chair Covers 100pk',              sku: 'HYG-CHR-015', cat: 'Hygiene',                 tier: 'under', cpc: 0.58, impr30: 3820,  clicks30: 124, conv30: 5,  aov: 40,  status: 'enabled' },
      { prod: 'Specialty Restoration Kit',              sku: 'RES-SPC-016', cat: 'Restoration Materials',   tier: 'under', cpc: 1.20, impr30: 2840,  clicks30: 82,  conv30: 3,  aov: 285, status: 'enabled' },
      { prod: 'Digital X-Ray Sensor Cover',             sku: 'HYG-XRY-017', cat: 'Hygiene',                 tier: 'under', cpc: 0.48, impr30: 3620,  clicks30: 118, conv30: 5,  aov: 15,  status: 'enabled' },
      // Losers (3)
      { prod: 'Obscure Dental Tool Set',                sku: 'INS-OBS-018', cat: 'Instruments',             tier: 'loser', cpc: 0.82, impr30: 2140,  clicks30: 58,  conv30: 2,  aov: 120, status: 'enabled', flags: 1, flagType: 'exclusion' },
      { prod: 'Limited Edition Whitening Kit',          sku: 'WHT-LTD-019', cat: 'Whitening',               tier: 'loser', cpc: 0.74, impr30: 1840,  clicks30: 52,  conv30: 1,  aov: 75,  status: 'enabled', flags: 1, flagType: 'exclusion' },
      { prod: 'Discontinued Implant Model X',           sku: 'IMP-DIS-020', cat: 'Implants',                tier: 'loser', cpc: 0.95, impr30: 1280,  clicks30: 65,  conv30: 0,  aov: 89,  status: 'enabled', flags: 1, flagType: 'exclusion' },
    ];
    return base.map(r => {
      const impr = Math.round(r.impr30 * scale);
      const clicks = Math.round(r.clicks30 * scale);
      const conv = Math.round(r.conv30 * scale);
      const cost = clicks * r.cpc;
      const convValue = conv * r.aov;
      const roas = cost > 0 ? convValue / cost : 0;
      return {
        ...r,
        cost: '£' + cost.toFixed(2),
        impr: impr.toLocaleString(),
        clicks: clicks.toLocaleString(),
        avgCpc: '£' + r.cpc.toFixed(2),
        conv,
        convValueStr: '£' + convValue.toFixed(2),
        roasNum: roas,
        roasStr: roas.toFixed(1) + 'x',
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
    '7d':  { cost: '£756', impr: '34,580', clicks: '1,125', cpc: '£0.67', ctr: '3.25%', conv: '33', cpa: '£22.91', cvr: '2.93%', convValue: '£3,175', roas: '4.2x', aov: '£96.21',
             costChg: '↑ 6%', imprChg: '↑ 11%', clicksChg: '↑ 8%', cpcChg: '↓ 2%', ctrChg: '↑ 5%', convChg: '↑ 14%', cpaChg: '↓ 8%', cvrChg: '↑ 3%' },
    '30d': { cost: '£3,240', impr: '148,200', clicks: '4,820', cpc: '£0.67', ctr: '3.25%', conv: '142', cpa: '£22.82', cvr: '2.95%', convValue: '£13,608', roas: '4.2x', aov: '£95.83',
             costChg: '↑ 6%', imprChg: '↑ 11%', clicksChg: '↑ 8%', cpcChg: '↓ 2%', ctrChg: '↑ 5%', convChg: '↑ 14%', cpaChg: '↓ 8%', cvrChg: '↑ 3%' },
    '90d': { cost: '£9,720', impr: '444,600', clicks: '14,460', cpc: '£0.67', ctr: '3.25%', conv: '426', cpa: '£22.82', cvr: '2.95%', convValue: '£40,824', roas: '4.2x', aov: '£95.83',
             costChg: '↑ 9%', imprChg: '↑ 13%', clicksChg: '↑ 10%', cpcChg: '↓ 3%', ctrChg: '↑ 6%', convChg: '↑ 16%', cpaChg: '↓ 9%', cvrChg: '↑ 4%' },
  };

  function flagCountBadgeHtml(type, prodName) {
    if (!type) return '';
    const labels = { exclusion: 'Exclusion Candidate', 'budget-op': 'Budget Opportunity', 'tier-demotion': 'Tier Demotion' };
    return `<span class="flag-count-badge flag-count-badge--${type}" data-prod="${prodName}" title="Click to view details"><span class="material-symbols-outlined">flag</span>${labels[type] || type}</span>`;
  }

  function tierBadgeHtml(tier) {
    return `<span class="tier-badge tier-badge--${tier}">${tierLabel(tier)}</span>`;
  }

  function roasCellHtml(roas) {
    return `<span class="roas-value roas-value--${roasClass(roas)}">${roas.toFixed(1)}x</span>`;
  }

  let rowsPerPage = 20;

  function updateTable(range) {
    const rows = TABLE_DATA[range];
    const tbody = document.querySelector('#productsTable tbody');
    if (!tbody || !rows) return;
    tbody.innerHTML = '';

    const visibleRows = rows.slice(0, rowsPerPage);

    visibleRows.forEach(r => {
      const tr = document.createElement('tr');
      tr.dataset.status = r.status;
      tr.dataset.tier = r.tier;
      tr.innerHTML = `
        <td><span class="status-dot status-dot--${r.status}"></span></td>
        <td><span class="product-name-link" data-prod="${r.prod}">${r.prod}</span></td>
        <td><span class="prod-sku-text">${r.sku}</span></td>
        <td><span class="prod-meta-text">${r.cat}</span></td>
        <td>${tierBadgeHtml(r.tier)}</td>
        <td>${r.cost}</td>
        <td>${r.impr}</td>
        <td>${r.clicks}</td>
        <td>${r.avgCpc}</td>
        <td>${r.conv}</td>
        <td>${r.convValueStr}</td>
        <td>${roasCellHtml(r.roasNum)}</td>
        <td>${r.flags > 0 ? flagCountBadgeHtml(r.flagType, r.prod) : ''}</td>`;
      tbody.appendChild(tr);
    });

    // Totals row
    const totals = document.createElement('tr');
    totals.className = 'totals-row';
    const s = SUMMARY_DATA[range];
    totals.innerHTML = `<td></td><td>Total / Average</td><td></td><td></td><td></td>
      <td>${s.cost}</td><td>${s.impr}</td><td>${s.clicks}</td><td>${s.cpc}</td>
      <td>${s.conv}</td><td>${s.convValue}</td>
      <td><span class="roas-value roas-value--high">${s.roas}</span></td><td></td>`;
    tbody.appendChild(totals);

    // Update summary cards (8 cards: Cost, Impr, Clicks, Avg CPC, Conv, Conv Value, ROAS, AOV)
    const cards = document.querySelectorAll('.perf-inner .summary-card');
    const vals = [s.cost, s.impr, s.clicks, s.cpc, s.conv, s.convValue, s.roas, s.aov];
    const chgs = [s.costChg, s.imprChg, s.clicksChg, s.cpcChg, s.convChg, null, null, null];
    cards.forEach((card, i) => {
      if (vals[i] !== undefined) card.querySelector('.summary-card__value').textContent = vals[i];
      if (chgs[i]) {
        const chgEl = card.querySelector('.summary-card__change');
        if (chgEl) {
          chgEl.textContent = chgs[i];
          chgEl.className = 'summary-card__change summary-card__change--' + (chgs[i].startsWith('↑') ? 'up' : chgs[i].startsWith('↓') ? 'down' : 'flat');
        }
      }
    });

    bindProductClicks();

    // Re-apply current filters
    filterProducts('status', currentStatusFilter);
    filterProducts('tier', currentTierFilter);

    const total = 204;
    const shown = Math.min(rowsPerPage, visibleRows.length);
    const info = document.getElementById('paginationInfo');
    if (info) info.textContent = `Showing 1-${shown} of ${total} products`;

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
      line1: '#14b8a6', // teal — shopping level
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
  // PRODUCT SLIDE-IN — 4 unique variants + generic default
  // ═════════════════════════════════════════════════════════════════════════

  const PROD_DATA = {
    'Discontinued Implant Model X': {
      sku: 'IMP-DIS-020', cat: 'Implants', productGroup: 'Implants > Titanium',
      status: 'enabled', tier: 'loser',
      cost: '£62', roas: '0.0x', roasZone: 'underperforming', roasDetail: 'No conversions in 45 days',
      convValue: '£0', aov: '—',
      approvals: [{
        text: '<strong>Exclude &ldquo;Discontinued Implant Model X&rdquo; &mdash; 0 conversions in 45 days, &pound;62 spend.</strong> Discontinued model.',
        rec: 'ACT recommends: Exclude this product from Shopping campaigns to reallocate budget to converting products.',
        impact: 'Saves £62/month if excluded',
        timeWaiting: 'Identified 4 hours ago',
        flagType: 'exclusion', flagLabel: 'Exclusion Candidate', risk: 'medium',
        details: {
          Check:    'Product Exclusion Recommendations (runs overnight)',
          Signal:   '0 conversions over 45 days while spending £62. Discontinued model with limited stock. No improvement trend.',
          Rule:     'Zero converters with spend > threshold flagged for exclusion review. Requires human approval.',
          Cooldown: 'No cooldown — exclusion is a one-time action.',
          Risk:     'Medium — excluding a product is reversible but affects feed visibility.'
        }
      }],
      executed: [],
      monitoring: [],
      alerts: [],
      tierBreakdown: {
        d7:  { roas: 0.0, weight: 50 },
        d14: { roas: 0.0, weight: 30 },
        d30: { roas: 0.1, weight: 20 },
        weighted: 0.02,
      },
      bidHistory: [
        { date: '5 Apr 2026', change: '£0.95 → £0.86', delta: '-9.5%', dir: 'down', reason: 'ROAS below target — 10% reduction (cycle cap)' },
        { date: '1 Apr 2026', change: '£1.05 → £0.95', delta: '-9.5%', dir: 'down', reason: 'Zero conversions — 10% reduction' },
        { date: '28 Mar 2026', change: '£1.15 → £1.05', delta: '-8.7%', dir: 'down', reason: 'ROAS below target — 10% reduction' },
      ],
      feed: {
        title: 'Discontinued Implant Model X — Titanium 4.5mm',
        description: 'Legacy titanium implant — stock clearance. Limited availability, discontinued model.',
        imageUrl: 'https://cdn.dentalsupplies.example/disc-imp-x.jpg',
        price: '£89.00',
        availability: 'Limited stock',
        gtin: '5012345678905',
        brand: 'Inserta',
        merchantId: 'XYZ123',
        lastSync: '11 Apr 2026, 04:47 AM',
      },
    },
    'Premium Implant Kit — Titanium': {
      sku: 'IMP-TI-001', cat: 'Implants', productGroup: 'Implants > Titanium',
      status: 'enabled', tier: 'best',
      cost: '£488', roas: '6.2x', roasZone: 'outperforming', roasDetail: '55% above target',
      convValue: '£3,028', aov: '£450',
      approvals: [{
        text: '<strong>Increase bids on &ldquo;Premium Implant Kit &mdash; Titanium&rdquo; &mdash; ROAS 6.2x, losing 42% IS to budget.</strong>',
        rec: 'ACT recommends: Raise bid by 15% to capture more of the 42% lost impression share (best seller candidate).',
        impact: 'Estimated: +£380/month revenue',
        timeWaiting: 'Identified 6 hours ago',
        flagType: 'budget-op', flagLabel: 'Budget Opportunity', risk: 'low',
        details: {
          Check:    'Best Seller Budget Maximisation (runs overnight)',
          Signal:   'ROAS 6.2x (55% above 4.0x target) sustained over 14 days. Search impression share 58%. Lost to budget: 42%.',
          Rule:     'Best sellers (top 20% by ROAS) with high IS lost to budget flagged for bid increase. ACT bid raises cap at 10% per cycle auto — 15% exceeds cap and requires approval.',
          Cooldown: '72-hour cooldown begins after approval.',
          Risk:     'Low — raising bids on a proven converter carries minimal downside.'
        }
      }],
      executed: [],
      monitoring: [],
      alerts: [],
      tierBreakdown: {
        d7:  { roas: 6.4, weight: 50 },
        d14: { roas: 6.2, weight: 30 },
        d30: { roas: 5.9, weight: 20 },
        weighted: 6.24,
      },
      bidHistory: [
        { date: '8 Apr 2026', change: '£1.68 → £1.85', delta: '+10.1%', dir: 'up', reason: 'Outperforming — 10% increase (cycle cap)' },
        { date: '4 Apr 2026', change: '£1.52 → £1.68', delta: '+10.5%', dir: 'up', reason: 'ROAS above target — 10% increase' },
        { date: '1 Apr 2026', change: '£1.38 → £1.52', delta: '+10.1%', dir: 'up', reason: 'Best seller tier — 10% increase' },
      ],
      feed: {
        title: 'Premium Implant Kit — Titanium 4.0mm, Complete Surgical Set',
        description: 'Professional titanium implant kit with complete surgical set. Includes implant, abutment, healing cap, and cover screw. 10-year warranty.',
        imageUrl: 'https://cdn.dentalsupplies.example/prem-imp-ti.jpg',
        price: '£450.00',
        availability: 'In stock',
        gtin: '5012345678901',
        brand: 'Inserta',
        merchantId: 'ABC001',
        lastSync: '11 Apr 2026, 04:47 AM',
      },
    },
    'Premium Dental Loupes 2.5x': {
      sku: 'INS-LOU-013', cat: 'Instruments', productGroup: 'Instruments > Loupes',
      status: 'enabled', tier: 'under',
      cost: '£202', roas: '2.8x', roasZone: 'underperforming', roasDetail: '30% below target',
      convValue: '£1,520', aov: '£380',
      approvals: [{
        text: '<strong>&ldquo;Premium Dental Loupes 2.5x&rdquo; dropping from Mid-Range to Underperformer tier.</strong> ROAS declined from 3.8x to 2.8x over 14 days.',
        rec: 'ACT recommends: Reduce product group bid by 10% while trend reverses or investigate feed issues.',
        impact: 'Protect budget while trend reverses',
        timeWaiting: 'Identified 1 day ago',
        flagType: 'tier-demotion', flagLabel: 'Tier Demotion', risk: 'medium',
        details: {
          Check:    'Product Performance Tiers (multi-window weighted blend)',
          Signal:   '7-day ROAS: 2.6x · 14-day ROAS: 2.8x · 30-day ROAS: 3.5x. Weighted score: 2.88x — drops into Underperformer band.',
          Rule:     'Products transitioning between tiers get reduced product group bid to protect budget while trend is assessed.',
          Cooldown: '72-hour cooldown begins after approval.',
          Risk:     'Medium — reducing bid reduces impressions and may accelerate the decline if the trend reverses naturally.'
        }
      }],
      executed: [],
      monitoring: [],
      alerts: [],
      tierBreakdown: {
        d7:  { roas: 2.6, weight: 50 },
        d14: { roas: 2.8, weight: 30 },
        d30: { roas: 3.5, weight: 20 },
        weighted: 2.88,
      },
      bidHistory: [
        { date: '9 Apr 2026', change: '£2.40 → £2.15', delta: '-10.4%', dir: 'down', reason: 'ROAS 30% below target — 10% reduction' },
        { date: '3 Apr 2026', change: '£2.68 → £2.40', delta: '-10.4%', dir: 'down', reason: 'Declining ROAS — 10% reduction (cycle cap)' },
      ],
      feed: {
        title: 'Premium Dental Loupes 2.5x Magnification — Lightweight Flip-up',
        description: 'Professional-grade dental loupes with 2.5x magnification. Lightweight flip-up design, 420mm working distance. German-engineered optics.',
        imageUrl: 'https://cdn.dentalsupplies.example/prem-loupes-25x.jpg',
        price: '£380.00',
        availability: 'In stock',
        gtin: '5012345678913',
        brand: 'OptiDent',
        merchantId: 'ABC013',
        lastSync: '11 Apr 2026, 04:47 AM',
      },
    },
    'Obscure Dental Tool Set': {
      sku: 'INS-OBS-018', cat: 'Instruments', productGroup: 'Instruments > Specialty',
      status: 'enabled', tier: 'loser',
      cost: '£48', roas: '0.8x', roasZone: 'underperforming', roasDetail: '80% below target',
      convValue: '£38', aov: '£120',
      approvals: [{
        text: '<strong>Exclude &ldquo;Obscure Dental Tool Set&rdquo; &mdash; ROAS 0.8x over 30 days, well below target 4.0x.</strong>',
        rec: 'ACT recommends: Exclude this product &mdash; persistent low ROAS with no improvement trend.',
        impact: 'Saves £48/month if excluded',
        timeWaiting: 'Identified 8 hours ago',
        flagType: 'exclusion', flagLabel: 'Exclusion Candidate', risk: 'medium',
        details: {
          Check:    'Product Exclusion Recommendations (runs overnight)',
          Signal:   'ROAS 0.8x over 30 days (well below 4.0x target). 2 conversions on 58 clicks — converting but at too low a rate to be profitable.',
          Rule:     'Products with ROAS < 20% of target for 30+ days flagged for exclusion review. Requires human approval.',
          Cooldown: 'No cooldown — exclusion is a one-time action.',
          Risk:     'Medium — the product does convert occasionally. Excluding may lose the 2-3 orders/month it brings in.'
        }
      }],
      executed: [],
      monitoring: [],
      alerts: [],
      tierBreakdown: {
        d7:  { roas: 0.9, weight: 50 },
        d14: { roas: 0.8, weight: 30 },
        d30: { roas: 0.8, weight: 20 },
        weighted: 0.85,
      },
      bidHistory: [
        { date: '5 Apr 2026', change: '£0.92 → £0.82', delta: '-10.9%', dir: 'down', reason: 'ROAS below target — 10% reduction (cycle cap)' },
        { date: '1 Apr 2026', change: '£1.02 → £0.92', delta: '-9.8%', dir: 'down', reason: 'Low ROAS trend — 10% reduction' },
      ],
      feed: {
        title: 'Obscure Dental Tool Set — 8-piece Specialty Kit',
        description: 'Specialty dental tool kit for uncommon procedures. Includes 8 niche instruments.',
        imageUrl: 'https://cdn.dentalsupplies.example/obsc-tool-set.jpg',
        price: '£120.00',
        availability: 'In stock',
        gtin: '5012345678918',
        brand: 'SpecDent',
        merchantId: 'ABC018',
        lastSync: '11 Apr 2026, 04:47 AM',
      },
    },
    'Dental Composite Shade Kit': {
      sku: 'RES-SHD-004', cat: 'Restoration Materials', productGroup: 'Restoration > Composite',
      status: 'enabled', tier: 'best',
      cost: '£300', roas: '5.2x', roasZone: 'outperforming', roasDetail: '30% above target',
      convValue: '£3,520', aov: '£220',
      approvals: [],
      executed: [
        { text: '<strong>Promoted &ldquo;Dental Composite Shade Kit&rdquo;</strong> <span class="act-item__values"><span class="val-pill val-pill--old">Mid-Range</span><span class="arrow">&rarr;</span><span class="val-pill val-pill--new-positive">Best Seller</span></span>', time: '11 Apr, 05:17 AM', reason: 'ROAS improved to 5.2x over 14 days' },
      ],
      monitoring: [],
      alerts: [],
      tierBreakdown: {
        d7:  { roas: 5.4, weight: 50 },
        d14: { roas: 5.2, weight: 30 },
        d30: { roas: 4.8, weight: 20 },
        weighted: 5.22,
      },
      bidHistory: [
        { date: '11 Apr 2026', change: 'Mid-Range → Best Seller', delta: 'Tier ↑', dir: 'up', reason: 'ROAS improved to 5.2x over 14 days — auto-promoted' },
        { date: '5 Apr 2026', change: '£1.28 → £1.40', delta: '+9.4%', dir: 'up', reason: 'ROAS above target — 10% increase' },
        { date: '1 Apr 2026', change: '£1.17 → £1.28', delta: '+9.4%', dir: 'up', reason: 'Trending up — 10% increase (cycle cap)' },
      ],
      feed: {
        title: 'Dental Composite Shade Kit — 16 VITA Shades Matched',
        description: 'Complete composite shade kit with 16 VITA-matched shades. Perfect for aesthetic restorations. Includes shade guide and applicator set.',
        imageUrl: 'https://cdn.dentalsupplies.example/comp-shade-kit.jpg',
        price: '£220.00',
        availability: 'In stock',
        gtin: '5012345678904',
        brand: 'ProDent',
        merchantId: 'ABC004',
        lastSync: '11 Apr 2026, 04:47 AM',
      },
    },
  };

  const DEFAULT_PROD = PROD_DATA['Discontinued Implant Model X'];

  const prodOverlay = document.getElementById('prodSlideinOverlay');
  const prodPanel   = document.getElementById('prodSlidein');
  const prodBody    = document.getElementById('prodSlideinBody');
  const prodName    = document.getElementById('prodSlideinName');
  const prodMeta    = document.getElementById('prodSlideinMeta');

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
    if (status === 'excluded') return 'Excluded';
    if (status === 'paused') return 'Paused';
    return 'Enabled';
  }

  function openProdSlidein(prod) {
    const d = PROD_DATA[prod] || DEFAULT_PROD;
    const displayName = PROD_DATA[prod] ? prod : 'Discontinued Implant Model X';
    if (prodName) prodName.textContent = displayName;
    if (prodMeta) prodMeta.innerHTML = `
      <span class="prod-status-inline"><span class="status-dot status-dot--${d.status}"></span> ${statusLabelFor(d.status)}</span>
      <span class="prod-meta-sep">·</span>
      <span class="prod-meta-text-inline">SKU: ${d.sku}</span>
      <span class="prod-meta-sep">·</span>
      <span class="prod-meta-text-inline">${d.cat}</span>
      <span class="prod-meta-sep">·</span>
      ${tierBadgeHtml(d.tier)}`;

    let html = '';

    // Health cards (4 in a row) — Cost, ROAS, Conv Value, AOV
    html += '<div class="prod-health-grid">';
    html += `<div class="prod-health-card"><div class="prod-health-card__label">Cost (MTD)</div><div class="prod-health-card__value">${d.cost}</div></div>`;
    const roasColor = d.roasZone === 'outperforming' ? '#10b981' : d.roasZone === 'underperforming' ? '#ef4444' : '#3b82f6';
    html += `<div class="prod-health-card"><div class="prod-health-card__label">ROAS</div><div class="prod-health-card__value" style="color:${roasColor}">${d.roas}</div><div class="prod-health-card__detail"><span class="zone-badge zone-badge--${d.roasZone}">${d.roasDetail}</span></div></div>`;
    html += `<div class="prod-health-card"><div class="prod-health-card__label">Conv. Value (MTD)</div><div class="prod-health-card__value">${d.convValue}</div></div>`;
    html += `<div class="prod-health-card"><div class="prod-health-card__label">AOV</div><div class="prod-health-card__value">${d.aov}</div></div>`;
    html += '</div>';

    // ── AWAITING APPROVAL (expanded) ──────────────────────────────────────
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
            ${a.details ? `<div class="slidein-detail-expand" id="prodSlideinDetail${idx}">${detailGrid}</div>` : ''}
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

    // ── ACTIONS EXECUTED OVERNIGHT ────────────────────────────────────────
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
    html += slideinSection({
      icon: 'notifications_active', iconColor: 'var(--act-red)',
      title: 'Recent Alerts', count: alertList.length, countBg: 'var(--act-red)',
      collapsed: true, bodyHtml: '',
      emptyIcon: 'notifications_none', emptyText: 'No alerts in the last 7 days.',
      isEmpty: alertList.length === 0
    });

    // ── PERFORMANCE TIER BREAKDOWN (unique) ───────────────────────────────
    const tb = d.tierBreakdown;
    let tierBody = '<div class="slidein-section__inner">';
    tierBody += '<table class="tier-breakdown"><thead><tr><th>Window</th><th>ROAS</th><th>Weight</th><th>Weighted</th></tr></thead><tbody>';
    tierBody += `<tr><td>7-day</td><td>${tb.d7.roas.toFixed(1)}x</td><td>${tb.d7.weight}%</td><td>${(tb.d7.roas * tb.d7.weight / 100).toFixed(2)}</td></tr>`;
    tierBody += `<tr><td>14-day</td><td>${tb.d14.roas.toFixed(1)}x</td><td>${tb.d14.weight}%</td><td>${(tb.d14.roas * tb.d14.weight / 100).toFixed(2)}</td></tr>`;
    tierBody += `<tr><td>30-day</td><td>${tb.d30.roas.toFixed(1)}x</td><td>${tb.d30.weight}%</td><td>${(tb.d30.roas * tb.d30.weight / 100).toFixed(2)}</td></tr>`;
    tierBody += `<tr class="tier-breakdown__weighted"><td>Weighted score</td><td>${tb.weighted.toFixed(2)}x</td><td>&mdash;</td><td>&mdash;</td></tr>`;
    tierBody += '</tbody></table>';
    tierBody += `<div class="tier-current"><span class="tier-current__label">Current tier:</span> ${tierBadgeHtml(d.tier)}</div>`;
    tierBody += '<ul class="tier-thresholds">';
    tierBody += '<li><span class="tier-thresholds__tier">Best Seller (top 20%)</span><span>ROAS ≥ 5.0x</span></li>';
    tierBody += '<li><span class="tier-thresholds__tier">Mid-Range (60%)</span><span>ROAS 3.0x – 5.0x</span></li>';
    tierBody += '<li><span class="tier-thresholds__tier">Underperformer (15%)</span><span>ROAS 1.5x – 3.0x</span></li>';
    tierBody += '<li><span class="tier-thresholds__tier">Loser (bottom 5%)</span><span>ROAS &lt; 1.5x</span></li>';
    tierBody += '</ul>';
    tierBody += '</div>';
    html += slideinSection({
      icon: 'leaderboard', iconColor: '#14b8a6',
      title: 'Performance Tier Breakdown', collapsed: true, bodyHtml: tierBody, isEmpty: false
    });

    // ── PRODUCT GROUP BID HISTORY (unique) ────────────────────────────────
    const bidList = d.bidHistory || [];
    let bidBody = '<div class="slidein-section__inner">';
    bidBody += `<div style="font-size:12px;color:var(--act-text);opacity:0.7;margin-bottom:8px">Product group: <strong>${d.productGroup}</strong></div>`;
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
      icon: 'history', iconColor: '#14b8a6',
      title: 'Product Group Bid History', collapsed: true, bodyHtml: bidBody, isEmpty: false
    });

    // ── PRODUCT FEED DETAILS (unique) ─────────────────────────────────────
    const f = d.feed;
    const gtinStatus = f.gtin
      ? `<span class="product-feed__status--ok"><span class="material-symbols-outlined" style="font-size:14px">check_circle</span>Present</span>`
      : `<span class="product-feed__status--warn"><span class="material-symbols-outlined" style="font-size:14px">warning</span>Missing</span>`;
    const availOk = f.availability === 'In stock';
    const availStatus = availOk
      ? `<span class="product-feed__status--ok"><span class="material-symbols-outlined" style="font-size:14px">check_circle</span>${f.availability}</span>`
      : `<span class="product-feed__status--warn"><span class="material-symbols-outlined" style="font-size:14px">warning</span>${f.availability}</span>`;
    let feedBody = '<ul class="product-feed">';
    feedBody += `<li><span class="product-feed__label">Title</span><span class="product-feed__value">${f.title}</span></li>`;
    feedBody += `<li><span class="product-feed__label">Description</span><span class="product-feed__value">${f.description}</span></li>`;
    feedBody += `<li><span class="product-feed__label">Image URL</span><span class="product-feed__value product-feed__value--mono">${f.imageUrl}</span></li>`;
    feedBody += `<li><span class="product-feed__label">Price</span><span class="product-feed__value">${f.price}</span></li>`;
    feedBody += `<li><span class="product-feed__label">Availability</span><span class="product-feed__value">${availStatus}</span></li>`;
    feedBody += `<li><span class="product-feed__label">GTIN</span><span class="product-feed__value"><span class="product-feed__value--mono">${f.gtin}</span> &nbsp; ${gtinStatus}</span></li>`;
    feedBody += `<li><span class="product-feed__label">Brand</span><span class="product-feed__value">${f.brand}</span></li>`;
    feedBody += `<li><span class="product-feed__label">Merchant ID</span><span class="product-feed__value product-feed__value--mono">${f.merchantId}</span></li>`;
    feedBody += `<li><span class="product-feed__label">Last sync</span><span class="product-feed__value">${f.lastSync}</span></li>`;
    feedBody += '</ul>';
    html += slideinSection({
      icon: 'inventory_2', iconColor: '#14b8a6',
      title: 'Product Feed Details', collapsed: true, bodyHtml: feedBody, isEmpty: false
    });

    if (prodBody) prodBody.innerHTML = html;

    // Bind slide-in section toggle clicks
    prodBody.querySelectorAll('.slidein-section__header').forEach(header => {
      header.addEventListener('click', (e) => {
        if (e.target.closest('.btn-see-details') || e.target.closest('.btn-act')) return;
        header.closest('.slidein-section').classList.toggle('collapsed');
      });
    });

    // Bind See Details / Hide Details toggle
    prodBody.querySelectorAll('.btn-see-details').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const idx = btn.dataset.detailIdx;
        const panel = document.getElementById('prodSlideinDetail' + idx);
        if (panel) {
          panel.classList.toggle('show');
          btn.textContent = panel.classList.contains('show') ? 'Hide Details' : 'See Details';
        }
      });
    });

    prodOverlay?.classList.add('open');
    prodPanel?.classList.add('open');
  }

  window.closeProdSlidein = function() {
    prodOverlay?.classList.remove('open');
    prodPanel?.classList.remove('open');
  };
  prodOverlay?.addEventListener('click', closeProdSlidein);
  document.getElementById('prodSlideinClose')?.addEventListener('click', closeProdSlidein);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeProdSlidein(); });

  function bindProductClicks() {
    document.querySelectorAll('.product-name-link').forEach(link => {
      link.addEventListener('click', () => openProdSlidein(link.dataset.prod));
    });
    document.querySelectorAll('#productsTable .flag-count-badge').forEach(badge => {
      badge.addEventListener('click', () => openProdSlidein(badge.dataset.prod));
    });
  }
  bindProductClicks();

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
