/* ============================================================================
   ACT v2 — Shared Decision Details slide-in renderer
   Used by /v2/morning-review and /v2/account. Single source of truth so the
   two pages cannot drift. Populates #slideinPanel from data-* attrs on an
   .act-item click, with formatted current/proposed values (never raw JSON).
   ============================================================================ */
(function() {
  'use strict';

  // ---- Field formatter: key → {label, formatValue} -------------------------
  const FIELD_DEFS = {
    daily_budget:    { label: 'Daily budget',      fmt: v => '£' + Number(v).toLocaleString() + '/day' },
    monthly_budget:  { label: 'Monthly budget',    fmt: v => '£' + Number(v).toLocaleString() + '/month' },
    share_pct:       { label: 'Share of total',    fmt: v => v + '%' },
    target_cpa:      { label: 'Target CPA',        fmt: v => '£' + v },
    target_roas:     { label: 'Target ROAS',       fmt: v => v + 'x' },
    cost:            { label: 'Cost',              fmt: v => '£' + Number(v).toLocaleString() },
    cpa:             { label: 'CPA',               fmt: v => '£' + v },
    roas:            { label: 'ROAS',              fmt: v => v + 'x' },
    conversions:     { label: 'Conversions',       fmt: v => Number(v).toLocaleString() },
    impressions:     { label: 'Impressions',       fmt: v => Number(v).toLocaleString() },
    clicks:          { label: 'Clicks',            fmt: v => Number(v).toLocaleString() },
    avg_cpc:         { label: 'Avg CPC',           fmt: v => '£' + v },
    ctr:             { label: 'CTR',               fmt: v => v + '%' },
    bid:             { label: 'Max CPC bid',       fmt: v => '£' + v },
    status:          { label: 'Status',            fmt: v => String(v) },
  };

  function humanize(key) {
    return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  }

  function formatField(key, val) {
    const def = FIELD_DEFS[key];
    if (def) return { label: def.label, value: def.fmt(val) };
    // Unknown key → humanize; stringify scalar without JSON braces
    return { label: humanize(key), value: String(val) };
  }

  function parseJSONAttr(s) {
    if (!s) return null;
    try { return JSON.parse(s); } catch (e) { return null; }
  }

  function isPlainObj(v) {
    return v && typeof v === 'object' && !Array.isArray(v);
  }

  // ---- Render current + proposed as "before → after" per entity ------------
  // current and proposed are either flat {key:value} or nested {entity:{key:value}}.
  function renderValuesSection(current, proposed) {
    // If nested (keys of current are objects themselves), render per-entity blocks.
    const currKeys = current ? Object.keys(current) : [];
    const propKeys = proposed ? Object.keys(proposed) : [];
    const allEntityKeys = Array.from(new Set([...currKeys, ...propKeys]));
    if (!allEntityKeys.length) return '';

    const nested = allEntityKeys.some(k =>
      (current && isPlainObj(current[k])) || (proposed && isPlainObj(proposed[k])));

    let html = '';
    if (nested) {
      allEntityKeys.forEach(entity => {
        const c = (current && current[entity]) || {};
        const p = (proposed && proposed[entity]) || {};
        const fieldKeys = Array.from(new Set([...Object.keys(c), ...Object.keys(p)]));
        if (!fieldKeys.length) return;
        html += '<div style="margin-bottom:12px">';
        html += '<div style="font-size:13px;font-weight:600;margin-bottom:4px">' + entity + '</div>';
        html += '<dl class="act-detail-grid" style="margin:0">';
        fieldKeys.forEach(k => {
          const hasC = c[k] !== undefined && c[k] !== null;
          const hasP = p[k] !== undefined && p[k] !== null;
          if (!hasC && !hasP) return;
          const ref = formatField(k, hasC ? c[k] : p[k]);
          let valHtml;
          if (hasC && hasP && String(c[k]) !== String(p[k])) {
            const cf = formatField(k, c[k]).value;
            const pf = formatField(k, p[k]).value;
            valHtml = cf + ' <span style="opacity:0.5">→</span> <strong>' + pf + '</strong>';
          } else if (hasP) {
            valHtml = formatField(k, p[k]).value;
          } else {
            valHtml = formatField(k, c[k]).value;
          }
          html += '<dt>' + ref.label + '</dt><dd>' + valHtml + '</dd>';
        });
        html += '</dl></div>';
      });
    } else {
      // Flat: one combined dl
      html += '<dl class="act-detail-grid">';
      allEntityKeys.forEach(k => {
        const hasC = current && current[k] !== undefined && current[k] !== null;
        const hasP = proposed && proposed[k] !== undefined && proposed[k] !== null;
        if (!hasC && !hasP) return;
        const ref = formatField(k, hasC ? current[k] : proposed[k]);
        let valHtml;
        if (hasC && hasP && String(current[k]) !== String(proposed[k])) {
          const cf = formatField(k, current[k]).value;
          const pf = formatField(k, proposed[k]).value;
          valHtml = cf + ' <span style="opacity:0.5">→</span> <strong>' + pf + '</strong>';
        } else if (hasP) {
          valHtml = formatField(k, proposed[k]).value;
        } else {
          valHtml = formatField(k, current[k]).value;
        }
        html += '<dt>' + ref.label + '</dt><dd>' + valHtml + '</dd>';
      });
      html += '</dl>';
    }
    return html;
  }

  // ---- Decision tree is free-form key/value (Check/Signal/Rule/Cooldown/Risk) ----
  function renderDecisionTree(obj) {
    if (!obj || !Object.keys(obj).length) return '';
    let html = '<dl class="act-detail-grid">';
    for (const [k, v] of Object.entries(obj)) {
      const val = (typeof v === 'object') ? JSON.stringify(v) : v;
      html += '<dt>' + k.charAt(0).toUpperCase() + k.slice(1) + '</dt><dd>' + val + '</dd>';
    }
    html += '</dl>';
    return html;
  }

  const LEVEL_CLASS = { account: 'account', campaign: 'campaign', ad_group: 'adgroup', keyword: 'keyword', ad: 'ad', shopping: 'shopping' };
  const LEVEL_LABEL = { account: 'Account', campaign: 'Campaign', ad_group: 'Ad Group', keyword: 'Keyword', ad: 'Ad', shopping: 'Shopping' };

  // ---- Main: open + populate -----------------------------------------------
  function openDecisionDetails(item) {
    const panel = document.getElementById('slideinPanel');
    const overlay = document.getElementById('slideinOverlay');
    const body = document.getElementById('slideinBody');
    const title = document.getElementById('slideinTitle');
    if (!item || !panel || !body) return;

    const d = item.dataset;
    const decision = parseJSONAttr(d.decisionTree);
    const current = parseJSONAttr(d.currentValue);
    const proposed = parseJSONAttr(d.proposedValue);

    if (title) title.textContent = d.entityName || 'Decision Details';

    const level = d.level || 'account';
    const lvlClass = LEVEL_CLASS[level] || 'account';
    const lvlLabel = LEVEL_LABEL[level] || 'Account';
    const cap = s => s ? s.charAt(0).toUpperCase() + s.slice(1) : '';

    let html = '';
    // 1. Tag row
    html += '<div style="display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap">';
    html += '<span class="badge-level badge-level--' + lvlClass + '">' + lvlLabel + '</span>';
    if (d.actionCategory) html += '<span class="badge-action badge-action--' + d.actionCategory + '">' + cap(d.actionCategory) + '</span>';
    if (d.risk) html += '<span class="badge-risk badge-risk--' + d.risk + '">' + cap(d.risk) + ' Risk</span>';
    html += '</div>';

    // 2. One-line recommendation
    if (d.summary) {
      html += '<div style="font-size:14px;line-height:1.6;margin-bottom:12px">';
      if (d.entityName) html += '<strong>' + d.entityName + '</strong> &mdash; ';
      html += d.summary + '</div>';
    }

    // 3. Blue rationale callout
    if (d.recommendationText) {
      html += '<div style="padding:10px;background:var(--act-blue-bg);border-left:3px solid var(--act-primary);margin-bottom:12px;font-size:13px">' + d.recommendationText + '</div>';
    }

    // 4. Estimated improvement (green)
    if (d.estimatedImpact) {
      html += '<div style="font-size:13px;color:var(--act-green);margin-bottom:16px">' + d.estimatedImpact + '</div>';
    }

    // 5+6. Decision Reasoning
    if (decision && Object.keys(decision).length) {
      html += '<h4 style="margin:16px 0 8px;font-size:13px;font-weight:600">Decision Reasoning</h4>';
      html += renderDecisionTree(decision);
    }

    // 7+8. Values — combined current + proposed view
    const hasCurrent = current && Object.keys(current).length;
    const hasProposed = proposed && Object.keys(proposed).length;
    if (hasCurrent && hasProposed) {
      html += '<h4 style="margin:16px 0 8px;font-size:13px;font-weight:600">Current → Proposed</h4>';
      html += renderValuesSection(current, proposed);
    } else if (hasCurrent) {
      html += '<h4 style="margin:16px 0 8px;font-size:13px;font-weight:600">Current Values</h4>';
      html += renderValuesSection(current, null);
    } else if (hasProposed) {
      html += '<h4 style="margin:16px 0 8px;font-size:13px;font-weight:600">Proposed Values</h4>';
      html += renderValuesSection(null, proposed);
    }

    body.innerHTML = html;
    overlay && overlay.classList.add('open');
    panel.classList.add('open');
  }

  function closeSlidein() {
    const panel = document.getElementById('slideinPanel');
    const overlay = document.getElementById('slideinOverlay');
    overlay && overlay.classList.remove('open');
    panel && panel.classList.remove('open');
  }

  // Wire default handlers — click overlay, close btn, Escape
  document.addEventListener('DOMContentLoaded', () => {
    const overlay = document.getElementById('slideinOverlay');
    const closeBtn = document.getElementById('slideinClose');
    overlay && overlay.addEventListener('click', closeSlidein);
    closeBtn && closeBtn.addEventListener('click', closeSlidein);
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closeSlidein(); });

    // Auto-wire any [data-action="details"] button if the page hasn't bound its own
    document.querySelectorAll('[data-action="details"]').forEach(btn => {
      if (btn.dataset.detailsBound) return;
      btn.dataset.detailsBound = '1';
      btn.addEventListener('click', e => {
        e.stopPropagation();
        openDecisionDetails(btn.closest('.act-item'));
      });
    });
  });

  // Expose globals
  window.openDecisionDetails = openDecisionDetails;
  window.closeSlidein = closeSlidein;
})();
