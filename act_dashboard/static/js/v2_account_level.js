/* ============================================================================
   ACT v2 — Account Level Page Interactions
   Chart.js, date range, table sorting, sections, approve/decline
   ============================================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // Section collapse (both acct-section and act-section patterns)
  document.querySelectorAll('.acct-section__header, .act-section__header').forEach(header => {
    header.addEventListener('click', (e) => {
      if (e.target.closest('.table-toolbar') || e.target.closest('.pill-group')) return;
      const section = header.closest('.acct-section') || header.closest('.act-section');
      if (section) section.classList.toggle('collapsed');
    });
  });

  // Table sorting
  document.querySelectorAll('.data-table th[data-sort]').forEach(th => {
    th.addEventListener('click', () => {
      const table = th.closest('table');
      const tbody = table.querySelector('tbody');
      const rows = Array.from(tbody.querySelectorAll('tr:not(.score-breakdown-row):not(.totals-row)'));
      const idx = Array.from(th.parentElement.children).indexOf(th);
      const asc = th.dataset.dir !== 'asc';
      th.dataset.dir = asc ? 'asc' : 'desc';
      table.querySelectorAll('th').forEach(h => { if (h !== th) delete h.dataset.dir; });
      rows.sort((a, b) => {
        let va = a.children[idx]?.textContent.trim().replace(/[GBP%,]/g, '') || '';
        let vb = b.children[idx]?.textContent.trim().replace(/[GBP%,]/g, '') || '';
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

  // Date range pills — full page reload preserving client param
  document.querySelectorAll('.pill-group').forEach(group => {
    group.querySelectorAll('.pill-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        if (btn.dataset.range) {
          const url = new URL(window.location.href);
          const daysMap = { '7d': '7', '30d': '30', '90d': '90' };
          url.searchParams.set('days', daysMap[btn.dataset.range] || '30');
          window.location.href = url.toString();
        }
        if (btn.dataset.filter) {
          group.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          filterCampaigns(btn.dataset.filter);
        }
      });
    });
  });

  function filterCampaigns(filter) {
    document.querySelectorAll('#campaignsTable tbody tr').forEach(row => {
      if (row.classList.contains('score-breakdown-row') || row.classList.contains('totals-row')) return;
      if (filter === 'all') { row.style.display = ''; return; }
      const status = row.dataset.status;
      row.style.display = (status === filter) ? '' : 'none';
    });
  }

  // Approve/Decline (AJAX to backend)
  document.querySelectorAll('[data-action="approve"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const recId = btn.dataset.recId;
      const item = btn.closest('.act-item');
      if (recId) {
        fetch('/v2/api/recommendations/' + recId + '/approve', { method: 'POST' })
          .then(r => r.json())
          .then(res => {
            if (res.success && item) { item.style.opacity = '0.4'; item.style.pointerEvents = 'none'; }
            showToast('Approved', 'success');
          });
      } else {
        if (item) { item.style.opacity = '0.4'; item.style.pointerEvents = 'none'; }
        showToast('Approved', 'success');
      }
    });
  });

  document.querySelectorAll('[data-action="decline"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const recId = btn.dataset.recId;
      const item = btn.closest('.act-item');
      if (recId) {
        fetch('/v2/api/recommendations/' + recId + '/decline', { method: 'POST' })
          .then(r => r.json())
          .then(res => {
            if (res.success && item) { item.style.opacity = '0.4'; item.style.pointerEvents = 'none'; }
            showToast('Declined', 'info');
          });
      } else {
        if (item) { item.style.opacity = '0.4'; item.style.pointerEvents = 'none'; }
        showToast('Declined', 'info');
      }
    });
  });

  // -------------------------------------------------------------------------
  // CHART.JS — Dual-axis timeline with real data
  // -------------------------------------------------------------------------
  const METRIC_DEFS = {
    cost:        { label: 'Cost',               prefix: '\u00a3', suffix: '' },
    impressions: { label: 'Impressions',        prefix: '',  suffix: '' },
    clicks:      { label: 'Clicks',             prefix: '',  suffix: '' },
    avgCpc:      { label: 'Avg CPC',            prefix: '\u00a3', suffix: '' },
    ctr:         { label: 'CTR',                prefix: '',  suffix: '%' },
    conversions: { label: 'Conversions',        prefix: '',  suffix: '' },
    cpa:         { label: 'CPA (Cost/Conv)',    prefix: '\u00a3', suffix: '' },
    convRate:    { label: 'Conv Rate',          prefix: '',  suffix: '%' },
    score:       { label: 'Performance Score',  prefix: '',  suffix: '' },
    budgetUtil:  { label: 'Budget Utilisation %',prefix: '',  suffix: '%' },
  };

  const chartCanvas = document.getElementById('performanceChart');
  let perfChart = null;

  function isDark() { return document.documentElement.getAttribute('data-theme') === 'dark'; }

  function getChartColors() {
    const dark = isDark();
    return {
      line1: '#3b82f6', line2: '#10b981',
      fill1: 'rgba(59,130,246,0.08)', fill2: 'rgba(16,185,129,0.08)',
      grid: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)',
      text: dark ? '#ffffff' : '#000000',
      border: dark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
    };
  }

  function buildChart() {
    if (!chartCanvas || typeof Chart === 'undefined' || typeof chartData === 'undefined') return;

    const m1Key = document.getElementById('chartMetric1')?.value || 'cost';
    const m2Key = document.getElementById('chartMetric2')?.value || 'conversions';
    const m1Def = METRIC_DEFS[m1Key];
    const m2Def = METRIC_DEFS[m2Key];
    const m1Data = chartData.metrics[m1Key] || [];
    const m2Data = chartData.metrics[m2Key] || [];
    const c = getChartColors();

    if (perfChart) perfChart.destroy();

    perfChart = new Chart(chartCanvas, {
      type: 'line',
      data: {
        labels: chartData.labels,
        datasets: [
          {
            label: m1Def.label, data: m1Data,
            borderColor: c.line1, backgroundColor: c.fill1,
            fill: true, tension: 0,
            pointRadius: 3, pointHoverRadius: 5,
            pointBackgroundColor: c.line1, pointBorderColor: c.line1,
            borderWidth: 2, yAxisID: 'y1',
          },
          {
            label: m2Def.label, data: m2Data,
            borderColor: c.line2, backgroundColor: c.fill2,
            fill: true, tension: 0,
            pointRadius: 3, pointHoverRadius: 5,
            pointBackgroundColor: c.line2, pointBorderColor: c.line2,
            borderWidth: 2, yAxisID: 'y2',
          }
        ]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: isDark() ? '#1e293b' : '#ffffff',
            titleColor: c.text, bodyColor: c.text,
            borderColor: c.border, borderWidth: 1, padding: 10,
            callbacks: {
              title: function(items) { return items[0]?.label || ''; },
              label: function(ctx) {
                const def = ctx.datasetIndex === 0 ? m1Def : m2Def;
                return def.label + ': ' + def.prefix + ctx.parsed.y + def.suffix;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: c.text, font: { size: 12 }, maxRotation: 0, autoSkipPadding: 12 },
            border: { color: c.border }
          },
          y1: {
            position: 'left',
            title: { display: true, text: m1Def.label, color: c.line1, font: { size: 12, weight: 600 } },
            grid: { color: c.grid },
            ticks: { color: c.text, font: { size: 12 }, callback: function(v) { return m1Def.prefix + v + m1Def.suffix; } },
            border: { color: c.border }
          },
          y2: {
            position: 'right',
            title: { display: true, text: m2Def.label, color: c.line2, font: { size: 12, weight: 600 } },
            grid: { drawOnChartArea: false },
            ticks: { color: c.text, font: { size: 12 }, callback: function(v) { return m2Def.prefix + v + m2Def.suffix; } },
            border: { color: c.border }
          }
        }
      }
    });
  }

  buildChart();
  document.getElementById('chartMetric1')?.addEventListener('change', buildChart);
  document.getElementById('chartMetric2')?.addEventListener('change', buildChart);

  // Rebuild chart on theme change
  new MutationObserver(() => { setTimeout(buildChart, 50); })
    .observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

});
