/* ============================================================================
   ACT PROTOTYPE — ACCOUNT LEVEL v9 INTERACTIONS
   v9: Combined section, straight lines, shared date range, multi-interval data
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
          // Update context note
          const days = currentRange === '7d' ? '7' : currentRange === '30d' ? '30' : '90';
          const ctx = document.getElementById('perfContext');
          if (ctx) ctx.textContent = `\u2014 4 campaigns, ${days} days`;
          // Rebuild chart with new range
          buildChart();
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
    const n = range === '7d' ? 7 : range === '30d' ? 30 : 13;
    const labels = range === '90d' ? makeWeeklyLabels(n) : makeDailyLabels(n);
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
