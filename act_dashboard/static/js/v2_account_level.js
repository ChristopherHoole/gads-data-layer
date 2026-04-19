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
  function getClientParam() {
    return new URL(window.location.href).searchParams.get('client') || 'oe001';
  }

  document.querySelectorAll('.pill-group').forEach(group => {
    group.querySelectorAll('.pill-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        if (btn.dataset.range) {
          const daysMap = { '7d': '7', '14d': '14', '30d': '30', '90d': '90' };
          const d = daysMap[btn.dataset.range];
          if (d) window.location.href = '?client=' + getClientParam() + '&days=' + d;
        }
        if (btn.dataset.filter) {
          group.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          filterCampaigns(btn.dataset.filter);
        }
      });
    });
  });

  // -------------------------------------------------------------------------
  // DATE PICKER — calendar with presets
  // -------------------------------------------------------------------------
  const dpEl = document.getElementById('datePicker');
  const dpLeftCal = document.getElementById('dpLeftCal');
  const dpRightCal = document.getElementById('dpRightCal');
  const dpLeftLbl = document.getElementById('dpLeftLabel');
  const dpRightLbl = document.getElementById('dpRightLabel');
  const dpRangeText = document.getElementById('dpRangeText');
  const dpApply = document.getElementById('dpApply');
  const dpCancel = document.getElementById('dpCancel');
  const customBtn = document.getElementById('customRangeBtn');

  if (dpEl && customBtn) {
    const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
    const DAY_HDRS = ['Mo','Tu','We','Th','Fr','Sa','Su'];
    const today = new Date();

    let viewMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1);
    let rangeStart = null;
    let rangeEnd = null;

    function fmtDate(d) {
      return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');
    }
    function fmtShort(d) {
      return d.getDate() + ' ' + MONTHS[d.getMonth()].substring(0,3);
    }
    function sameDay(a, b) { return a && b && a.getFullYear()===b.getFullYear() && a.getMonth()===b.getMonth() && a.getDate()===b.getDate(); }
    function inRange(d) {
      if (!rangeStart || !rangeEnd) return false;
      return d > rangeStart && d < rangeEnd;
    }

    function renderCal(container, year, month) {
      const first = new Date(year, month, 1);
      const startDay = (first.getDay() + 6) % 7; // Monday = 0
      const daysInMonth = new Date(year, month + 1, 0).getDate();
      let html = '<table><thead><tr>' + DAY_HDRS.map(h => '<th>' + h + '</th>').join('') + '</tr></thead><tbody><tr>';
      for (let i = 0; i < startDay; i++) html += '<td></td>';
      for (let d = 1; d <= daysInMonth; d++) {
        const date = new Date(year, month, d);
        let cls = 'date-picker__day';
        if (sameDay(date, today)) cls += ' date-picker__day--today';
        if (sameDay(date, rangeStart)) cls += ' date-picker__day--start';
        if (sameDay(date, rangeEnd)) cls += ' date-picker__day--end';
        if (inRange(date)) cls += ' date-picker__day--in-range';
        html += '<td><span class="' + cls + '" data-date="' + fmtDate(date) + '">' + d + '</span></td>';
        if ((startDay + d) % 7 === 0 && d < daysInMonth) html += '</tr><tr>';
      }
      html += '</tr></tbody></table>';
      container.innerHTML = html;

      container.querySelectorAll('.date-picker__day').forEach(el => {
        el.addEventListener('click', () => {
          const clicked = new Date(el.dataset.date + 'T00:00:00');
          if (!rangeStart || rangeEnd) { rangeStart = clicked; rangeEnd = null; }
          else if (clicked < rangeStart) { rangeEnd = rangeStart; rangeStart = clicked; }
          else { rangeEnd = clicked; }
          dpPresets.querySelectorAll('.dp-preset').forEach(p => p.classList.remove('active'));
          renderCalendars();
          updateRangeText();
        });
      });
    }

    function renderCalendars() {
      const ly = viewMonth.getFullYear(), lm = viewMonth.getMonth();
      renderCal(dpLeftCal, ly, lm);
      const rm = lm + 1, ry = rm > 11 ? ly + 1 : ly;
      renderCal(dpRightCal, ry, rm % 12);
      dpLeftLbl.textContent = MONTHS[lm] + ' ' + ly;
      dpRightLbl.textContent = MONTHS[rm % 12] + ' ' + ry;
    }

    function updateRangeText() {
      if (rangeStart && rangeEnd) {
        dpRangeText.textContent = fmtShort(rangeStart) + ' \u2014 ' + fmtShort(rangeEnd);
        dpApply.disabled = false;
      } else if (rangeStart) {
        dpRangeText.textContent = fmtShort(rangeStart) + ' \u2014 select end date';
        dpApply.disabled = true;
      } else {
        dpRangeText.textContent = 'Select start and end dates';
        dpApply.disabled = true;
      }
    }

    // Presets (dynamic dates)
    const dpPresets = document.getElementById('dpPresets');
    const PRESETS = {
      today: () => [new Date(today), new Date(today)],
      yesterday: () => { const d = new Date(today); d.setDate(d.getDate()-1); return [d, d]; },
      thisWeek: () => { const d = new Date(today); const dow = (d.getDay()+6)%7; const mon = new Date(d); mon.setDate(d.getDate()-dow); return [mon, new Date(today)]; },
      lastWeek: () => { const d = new Date(today); const dow = (d.getDay()+6)%7; const sun = new Date(d); sun.setDate(d.getDate()-dow-1); const mon = new Date(sun); mon.setDate(sun.getDate()-6); return [mon, sun]; },
      thisMonth: () => [new Date(today.getFullYear(), today.getMonth(), 1), new Date(today)],
      lastMonth: () => [new Date(today.getFullYear(), today.getMonth()-1, 1), new Date(today.getFullYear(), today.getMonth(), 0)],
      thisQuarter: () => { const q = Math.floor(today.getMonth()/3)*3; return [new Date(today.getFullYear(), q, 1), new Date(today)]; },
      lastQuarter: () => { const q = Math.floor(today.getMonth()/3)*3; return [new Date(today.getFullYear(), q-3, 1), new Date(today.getFullYear(), q, 0)]; },
      thisYear: () => [new Date(today.getFullYear(), 0, 1), new Date(today)],
    };

    dpPresets.querySelectorAll('.dp-preset').forEach(btn => {
      btn.addEventListener('click', () => {
        const [s, e] = PRESETS[btn.dataset.preset]();
        rangeStart = s; rangeEnd = e;
        viewMonth = new Date(s.getFullYear(), s.getMonth(), 1);
        dpPresets.querySelectorAll('.dp-preset').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        renderCalendars();
        updateRangeText();
      });
    });

    // Open/close
    customBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      dpEl.classList.toggle('open');
      if (dpEl.classList.contains('open')) renderCalendars();
    });

    document.getElementById('dpPrevMonth').addEventListener('click', () => { viewMonth.setMonth(viewMonth.getMonth() - 1); renderCalendars(); });
    document.getElementById('dpNextMonth').addEventListener('click', () => { viewMonth.setMonth(viewMonth.getMonth() + 1); renderCalendars(); });

    dpCancel.addEventListener('click', () => { dpEl.classList.remove('open'); });

    dpApply.addEventListener('click', () => {
      if (!rangeStart || !rangeEnd) return;
      window.location.href = '?client=' + getClientParam() + '&start=' + fmtDate(rangeStart) + '&end=' + fmtDate(rangeEnd);
    });

    // Close on click outside
    document.addEventListener('click', (e) => {
      if (dpEl.classList.contains('open') && !dpEl.contains(e.target) && e.target !== customBtn) {
        dpEl.classList.remove('open');
      }
    });
    dpEl.addEventListener('click', (e) => e.stopPropagation());
  }

  function filterCampaigns(filter) {
    document.querySelectorAll('#campaignsTable tbody tr').forEach(row => {
      if (row.classList.contains('score-breakdown-row') || row.classList.contains('totals-row')) return;
      if (filter === 'all') { row.style.display = ''; return; }
      const status = row.dataset.status;
      row.style.display = (status === filter) ? '' : 'none';
    });
  }

  // --- Approve / Decline (guarded; disable on first click) ---
  function handleAction(btn, action, successToast, toastKind) {
    if (btn.classList.contains('btn-act--pending')) return;
    const recId = btn.dataset.recId;
    const item = btn.closest('.act-item');
    if (!recId) return;
    btn.classList.add('btn-act--pending');
    btn.disabled = true;
    // Disable sibling buttons too
    if (item) item.querySelectorAll('.btn-act--approve, .btn-act--decline').forEach(b => { b.disabled = true; });
    fetch('/v2/api/recommendations/' + recId + '/' + action, { method: 'POST' })
      .then(r => r.json())
      .then(res => {
        if (res && res.success) {
          if (item) { item.style.opacity = '0.4'; item.style.pointerEvents = 'none'; setTimeout(() => item.remove(), 400); }
          showToast(successToast, toastKind);
        } else {
          showToast(action + ' failed: ' + ((res && res.error) || 'unknown'), 'error');
          btn.classList.remove('btn-act--pending'); btn.disabled = false;
          if (item) item.querySelectorAll('.btn-act--approve, .btn-act--decline').forEach(b => { b.disabled = false; });
        }
      })
      .catch(err => {
        showToast(action + ' failed: ' + err.message, 'error');
        btn.classList.remove('btn-act--pending'); btn.disabled = false;
        if (item) item.querySelectorAll('.btn-act--approve, .btn-act--decline').forEach(b => { b.disabled = false; });
      });
  }

  document.querySelectorAll('[data-action="approve"]').forEach(btn => {
    btn.addEventListener('click', (e) => { e.stopPropagation(); handleAction(btn, 'approve', 'Approved', 'success'); });
  });
  document.querySelectorAll('[data-action="decline"]').forEach(btn => {
    btn.addEventListener('click', (e) => { e.stopPropagation(); handleAction(btn, 'decline', 'Declined', 'info'); });
  });

  // --- View Details slide-in ---
  const slideinOverlay = document.getElementById('slideinOverlay');
  const slideinPanel = document.getElementById('slideinPanel');
  const slideinBody = document.getElementById('slideinBody');
  const slideinTitle = document.getElementById('slideinTitle');

  function parseJSONAttr(s) {
    if (!s) return null;
    try { return JSON.parse(s); } catch (e) { return null; }
  }

  function renderKV(obj) {
    if (!obj || typeof obj !== 'object' || !Object.keys(obj).length) return '';
    let html = '<dl class="act-detail-grid">';
    for (const [k, v] of Object.entries(obj)) {
      const val = (typeof v === 'object') ? JSON.stringify(v, null, 2) : v;
      html += '<dt>' + k + '</dt><dd>' + val + '</dd>';
    }
    html += '</dl>';
    return html;
  }

  document.querySelectorAll('[data-action="details"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const item = btn.closest('.act-item');
      if (!item || !slideinPanel || !slideinBody) return;
      const d = item.dataset;
      const decision = parseJSONAttr(d.decisionTree);
      const current = parseJSONAttr(d.currentValue);
      const proposed = parseJSONAttr(d.proposedValue);

      if (slideinTitle) slideinTitle.textContent = d.entityName || 'Decision Details';

      let html = '';
      html += '<div style="display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap">';
      html += '<span class="badge-level badge-level--account">Account</span>';
      if (d.actionCategory) html += '<span class="badge-action badge-action--' + d.actionCategory + '">' + d.actionCategory.charAt(0).toUpperCase() + d.actionCategory.slice(1) + '</span>';
      if (d.risk) html += '<span class="badge-risk badge-risk--' + d.risk + '">' + d.risk.charAt(0).toUpperCase() + d.risk.slice(1) + ' Risk</span>';
      html += '</div>';

      if (d.summary) html += '<div style="font-size:14px;line-height:1.6;margin-bottom:12px"><strong>' + (d.entityName || '') + '</strong> &mdash; ' + d.summary + '</div>';
      if (d.recommendationText) html += '<div style="padding:10px;background:var(--act-blue-bg);border-left:3px solid var(--act-primary);margin-bottom:12px;font-size:13px">' + d.recommendationText + '</div>';
      if (d.estimatedImpact) html += '<div style="font-size:13px;color:var(--act-green);margin-bottom:16px">' + d.estimatedImpact + '</div>';

      if (decision && Object.keys(decision).length) {
        html += '<h4 style="margin:16px 0 8px;font-size:13px;font-weight:600">Decision Reasoning</h4>' + renderKV(decision);
      }
      if (current && Object.keys(current).length) {
        html += '<h4 style="margin:16px 0 8px;font-size:13px;font-weight:600">Current Values</h4>' + renderKV(current);
      }
      if (proposed && Object.keys(proposed).length) {
        html += '<h4 style="margin:16px 0 8px;font-size:13px;font-weight:600">Proposed Values</h4>' + renderKV(proposed);
      }

      slideinBody.innerHTML = html;
      slideinOverlay.classList.add('open');
      slideinPanel.classList.add('open');
    });
  });

  window.closeSlidein = function() {
    slideinOverlay && slideinOverlay.classList.remove('open');
    slideinPanel && slideinPanel.classList.remove('open');
  };
  slideinOverlay && slideinOverlay.addEventListener('click', window.closeSlidein);
  const sc = document.getElementById('slideinClose');
  sc && sc.addEventListener('click', window.closeSlidein);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') window.closeSlidein(); });

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
