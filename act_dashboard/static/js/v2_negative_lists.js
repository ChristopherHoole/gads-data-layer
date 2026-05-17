/* IA refactor (13 May 2026) - Negative Lists viewer.
   Extracted from v2_client_config.js so it can be hosted by the Search
   Terms page (right-aligned tab) instead of buried in Client Config.

   Behaviour is unchanged - same DOM ids, same endpoints, same render.
   The host page provides `<div id="negLists" data-client-id="…">`; this
   script auto-detects the element on load and, when present, wires the
   refresh button + filter/search controls. The initial fetch is deferred
   until window.NegativeListsPane.boot() is called (lazy on first tab
   activation), so the heavy /v2/api/negatives/lists request doesn't fire
   on every Search Terms page load.

   Section D will polish visuals to the ACT standard. */
(function () {
  const root = document.getElementById('negLists');
  if (!root) return;  // markup absent - nothing to wire.
  const clientId = root.dataset.clientId;
  let state = { loaded: false, filter: '', roleFilter: '', data: null };

  if (!clientId) {
    window.NegativeListsPane = {
      boot: () => {
        root.innerHTML = '<div class="neg-error" style="padding:18px;color:var(--danger);">No client selected. Please select a client from the top-right dropdown.</div>';
        console.error('[NegLists] clientId missing from #negLists data-client-id');
      },
    };
    return;
  }

  function fmtWhen(iso) {
    if (!iso) return '-';
    try {
      const d = new Date(iso);
      const diffMs = Date.now() - d.getTime();
      const mins = Math.floor(diffMs / 60000);
      const hrs = Math.floor(mins / 60);
      const days = Math.floor(hrs / 24);
      const rel = days >= 1 ? `${days}d ago` : hrs >= 1 ? `${hrs}h ago` : `${Math.max(1, mins)}m ago`;
      return `${d.toLocaleString('en-GB', { day:'2-digit', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit' })} (${rel})`;
    } catch { return iso; }
  }

  function syncZoneClass(iso) {
    if (!iso) return 'neg-sync--none';
    const ageHrs = (Date.now() - new Date(iso).getTime()) / 3600000;
    if (ageHrs < 24) return 'neg-sync--green';
    if (ageHrs < 48) return 'neg-sync--amber';
    return 'neg-sync--red';
  }

  async function refresh() {
    const btn = document.getElementById('negListsRefreshBtn');
    if (btn) { btn.disabled = true; btn.textContent = 'Refreshing…'; }
    try {
      const resp = await fetch('/v2/api/negatives/refresh-snapshot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ client_id: clientId }),
      });
      const data = await resp.json();
      if (resp.status === 409) {
        showToast('Refresh already running.', 'warning');
      } else if (data.status === 'ok') {
        showToast(`Synced ${data.list_count} lists, ${data.keyword_count} keywords in ${data.duration_seconds}s`, 'success');
        await load(true);
      } else {
        showToast('Refresh failed: ' + (data.message || 'Unknown'), 'error');
      }
    } catch (e) {
      showToast('Refresh failed: ' + e.message, 'error');
    } finally {
      if (btn) { btn.disabled = false; btn.innerHTML = '<span class="material-symbols-outlined">refresh</span> Refresh neg lists from GAds'; }
    }
  }

  // Section D (13 May 2026): the host template now provides three
  // pre-built holders (#negStatsHolder, #negWarnHolder,
  // #negToolbarHolder) plus the original #negLists for the accordion.
  // We write into each holder separately so the .act-card structure
  // stays intact across renders. Old single-root render path is gone.
  function render() {
    const d = state.data;
    const statsHolder = document.getElementById('negStatsHolder');
    const warnHolder = document.getElementById('negWarnHolder');
    const toolbarHolder = document.getElementById('negToolbarHolder');

    if (!d || d.total_lists === 0) {
      if (statsHolder) statsHolder.innerHTML = '';
      if (warnHolder) warnHolder.innerHTML = '';
      if (toolbarHolder) toolbarHolder.innerHTML = '';
      root.innerHTML = `
        <div class="neg-empty">
          <p>No negative list snapshot yet.<br/>Click below to pull current lists from Google Ads.</p>
          <button type="button" class="btn-act btn-act--approve" id="negListsRefreshBtn">
            <span class="material-symbols-outlined">refresh</span> Refresh neg lists from GAds
          </button>
        </div>`;
      document.getElementById('negListsRefreshBtn')?.addEventListener('click', refresh);
      return;
    }

    // ---- Stats strip (above the card) ----
    const zone = syncZoneClass(d.last_synced_at);
    if (statsHolder) {
      // Section 8 audit [025] (17 May 2026): tooltips on every tile.
      statsHolder.innerHTML = `
        <div class="neg-stats">
          <div class="neg-stat" title="Number of negative-keyword lists in the latest GAds snapshot."><span class="neg-stat__label">Total lists</span><span class="neg-stat__val">${d.total_lists}</span></div>
          <div class="neg-stat" title="Sum of negative keywords across all lists."><span class="neg-stat__label">Total keywords</span><span class="neg-stat__val">${d.total_keywords}</span></div>
          <div class="neg-stat" title="Date the snapshot was taken in GAds."><span class="neg-stat__label">Snapshot date</span><span class="neg-stat__val">${d.snapshot_date || '-'}</span></div>
          <div class="neg-stat ${zone}" title="Last time ACT refreshed the snapshot."><span class="neg-stat__label">Last synced</span><span class="neg-stat__val">${fmtWhen(d.last_synced_at)}</span></div>
        </div>`;
    }

    // ---- Warn banner (red zone only) ----
    if (warnHolder) {
      warnHolder.innerHTML = zone === 'neg-sync--red'
        ? `<div class="neg-warn-banner">Negative list snapshot is over 48 hours old. Click Refresh to pull latest from Google Ads.</div>`
        : '';
    }

    // ---- Toolbar (refresh + search + role filter + count) ----
    const roles = Array.from(new Set(d.lists.map(l => l.list_role).filter(Boolean))).sort();
    const roleOptions = ['<option value="">All roles</option>'].concat(
      roles.map(r => `<option value="${r}"${state.roleFilter===r?' selected':''}>${r}</option>`)
    ).join('');

    if (toolbarHolder) {
      toolbarHolder.innerHTML = `
        <div class="neg-actions">
          <button type="button" class="btn-act btn-act--approve" id="negListsRefreshBtn">
            <span class="material-symbols-outlined">refresh</span> Refresh neg lists from GAds
          </button>
          <input type="search" id="negListsSearch" placeholder="Search keyword across all lists…" class="neg-search" value="${state.filter.replace(/"/g,'&quot;')}"/>
          <select id="negListsRoleFilter" class="neg-role-filter">${roleOptions}</select>
          <span class="neg-match-count" id="negMatchCount"></span>
        </div>`;
      document.getElementById('negListsRefreshBtn').addEventListener('click', refresh);
      document.getElementById('negListsSearch').addEventListener('input', e => {
        state.filter = e.target.value.trim().toLowerCase();
        renderLists();
      });
      document.getElementById('negListsRoleFilter').addEventListener('change', e => {
        state.roleFilter = e.target.value;
        renderLists();
      });
    }

    // ---- Lists accordion (inside .st-card-table) ----
    root.innerHTML = `<div id="negListsContainer" class="neg-lists"></div>`;
    renderLists();
  }

  function renderLists() {
    const container = document.getElementById('negListsContainer');
    if (!container) return;
    const d = state.data;
    const f = state.filter;
    const rf = state.roleFilter;
    let matchingLists = 0;
    let matchingTotal = 0;

    const html = d.lists.filter(l => !rf || l.list_role === rf).map((l) => {
      const matchedKws = f ? l.keywords.filter(k => (k.keyword_text || '').toLowerCase().includes(f)) : l.keywords;
      const hasMatch = f && matchedKws.length > 0;
      if (hasMatch) { matchingLists++; matchingTotal += matchedKws.length; }
      const expanded = hasMatch; // auto-expand on match
      const pageSize = 100;
      const initial = matchedKws.slice(0, pageSize);
      return `
        <div class="neg-list ${expanded?'open':''}" data-list-id="${l.list_id}" data-total="${matchedKws.length}" data-page-size="${pageSize}">
          <div class="neg-list__header">
            <span class="neg-list__toggle material-symbols-outlined">${expanded?'expand_more':'chevron_right'}</span>
            <span class="neg-list__name">${escapeHtml(l.list_name)}</span>
            <span class="neg-list__role">${l.list_role || '-'}</span>
            <span class="neg-list__match">${l.match_type || '-'}</span>
            <span class="neg-list__count">${matchedKws.length}${f ? '/' + l.keyword_count : ''} kw</span>
            <span class="neg-list__linked ${l.is_linked_to_campaign?'linked':'unlinked'}">${l.is_linked_to_campaign?'linked':'unlinked'}</span>
          </div>
          <div class="neg-list__body" style="${expanded?'':'display:none;'}">
            ${matchedKws.length === 0
              ? '<div class="neg-list__empty">No keywords.</div>'
              : `<table class="neg-kw-table">
                  <thead><tr><th>Keyword</th><th>Match</th><th>Added</th><th>By</th></tr></thead>
                  <tbody class="neg-kw-tbody">
                    ${initial.map(k => renderKwRow(k, f)).join('')}
                  </tbody>
                </table>
                ${matchedKws.length > pageSize ? `<div class="neg-kw-pager"><button type="button" class="btn btn--ghost neg-kw-more">Load more (${matchedKws.length - pageSize} remaining)</button></div>` : ''}`
            }
          </div>
        </div>`;
    }).join('');

    container.innerHTML = html || '<div style="padding:14px;color:var(--text-muted);">No lists match the current filter.</div>';

    // wire up list toggles
    container.querySelectorAll('.neg-list__header').forEach(h => {
      h.addEventListener('click', () => {
        const wrap = h.closest('.neg-list');
        const body = wrap.querySelector('.neg-list__body');
        const toggle = wrap.querySelector('.neg-list__toggle');
        const open = wrap.classList.toggle('open');
        body.style.display = open ? '' : 'none';
        toggle.textContent = open ? 'expand_more' : 'chevron_right';
      });
    });

    // Load-more pager - client-side slice into full dataset
    container.querySelectorAll('.neg-kw-more').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const wrap = btn.closest('.neg-list');
        const listId = wrap.dataset.listId;
        const list = d.lists.find(x => x.list_id === listId);
        const matched = f ? list.keywords.filter(k => (k.keyword_text || '').toLowerCase().includes(f)) : list.keywords;
        const tbody = wrap.querySelector('.neg-kw-tbody');
        const shown = tbody.querySelectorAll('tr').length;
        const next = matched.slice(shown, shown + 100);
        tbody.insertAdjacentHTML('beforeend', next.map(k => renderKwRow(k, f)).join(''));
        const remaining = matched.length - (shown + next.length);
        if (remaining <= 0) btn.parentElement.remove();
        else btn.textContent = `Load more (${remaining} remaining)`;
      });
    });

    const counter = document.getElementById('negMatchCount');
    if (counter) counter.textContent = f ? `Found in ${matchingLists} list${matchingLists===1?'':'s'}: ${matchingTotal} keyword${matchingTotal===1?'':'s'}` : '';
  }

  function renderKwRow(k, filter) {
    const txt = escapeHtml(k.keyword_text || '');
    const highlighted = filter
      ? txt.replace(new RegExp('('+filter.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')', 'ig'), '<mark>$1</mark>')
      : txt;
    const when = k.added_at ? new Date(k.added_at).toLocaleDateString('en-GB') : '-';
    return `<tr><td>${highlighted}</td><td>${k.match_type || ''}</td><td>${when}</td><td>${k.added_by || ''}</td></tr>`;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  async function load(force) {
    if (state.loaded && !force) return;
    try {
      const resp = await fetch(`/v2/api/negatives/lists?client_id=${encodeURIComponent(clientId)}`);
      const data = await resp.json();
      if (data.status !== 'ok') throw new Error(data.detail || 'failed');
      state.data = data;
      state.loaded = true;
      render();
    } catch (e) {
      root.innerHTML = `<div style="padding:18px;color:var(--danger);">Failed to load negative lists: ${e.message}</div>`;
    }
  }

  let _booted = false;
  window.NegativeListsPane = {
    boot: () => {
      if (_booted) return;
      _booted = true;
      load(false);
    },
    refresh,
    reload: () => load(true),
  };
})();
