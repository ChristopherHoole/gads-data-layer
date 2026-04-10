/* ============================================================================
   ACT PROTOTYPE — CAMPAIGN LEVEL OPTION C INTERACTIONS
   Tabbed: All Campaigns + Campaign Detail. Campaign name click switches tab.
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
        item.classList.add('active'); clientMenu.classList.remove('show');
        showToast(`Switched to ${item.textContent.trim()}`, 'info');
      });
    });
  }

  // ── PAGE TABS ──
  document.querySelectorAll('.page-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.page-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById(tab.dataset.tab)?.classList.add('active');
      // Build the correct chart
      if (tab.dataset.tab === 'tabAll') { currentRange = currentRangeAll; buildChartAll(); }
      else { currentRange = currentRangeDetail; buildChartDetail(); }
    });
  });

  // Back link
  document.getElementById('backToAll')?.addEventListener('click', () => {
    document.querySelector('.page-tab[data-tab="tabAll"]').click();
  });

  // Campaign name click → switch to detail tab
  document.querySelectorAll('.campaign-name-link').forEach(link => {
    link.addEventListener('click', () => {
      const name = link.textContent.trim();
      const sel = document.getElementById('detailCampaignSelect');
      if (sel) { for (let i = 0; i < sel.options.length; i++) { if (sel.options[i].text.includes(name.split('—')[0].trim())) { sel.selectedIndex = i; break; } } }
      document.querySelector('.page-tab[data-tab="tabDetail"]').click();
      showToast(`Viewing: ${name}`, 'info');
    });
  });

  // Campaign selector in detail tab
  document.getElementById('detailCampaignSelect')?.addEventListener('change', function() {
    showToast(`Viewing: ${this.options[this.selectedIndex].text}`, 'info');
  });

  // Section collapse (both patterns)
  document.querySelectorAll('.acct-section__header, .act-section__header').forEach(header => {
    header.addEventListener('click', (e) => {
      if (e.target.closest('.pill-group') || e.target.closest('.page-tab')) return;
      const section = header.closest('.acct-section') || header.closest('.act-section');
      if (section) section.classList.toggle('collapsed');
    });
  });

  // Lever card + group collapse
  document.querySelectorAll('.lever-card__header').forEach(h => h.addEventListener('click', () => h.closest('.lever-card').classList.toggle('collapsed')));
  document.querySelectorAll('.act-group__header').forEach(h => h.addEventListener('click', (e) => { e.stopPropagation(); h.closest('.act-group').classList.toggle('collapsed'); }));

  // Approve/Decline/Undo
  document.querySelectorAll('[data-action="approve"]').forEach(b => b.addEventListener('click', (e) => { e.stopPropagation(); const i=b.closest('.act-item')||b.closest('.acct-rec'); if(i){i.style.opacity='0.4';i.style.pointerEvents='none';} showToast('Approved','success'); }));
  document.querySelectorAll('[data-action="decline"]').forEach(b => b.addEventListener('click', (e) => { e.stopPropagation(); const i=b.closest('.act-item')||b.closest('.acct-rec'); if(i){i.style.opacity='0.4';i.style.pointerEvents='none';} showToast('Declined','info'); }));
  document.querySelectorAll('[data-action="undo"]').forEach(b => b.addEventListener('click', (e) => { e.stopPropagation(); const i=b.closest('.act-item'); if(i){i.style.opacity='0.4';i.style.pointerEvents='none';} showToast('Undo queued','warning'); }));

  // Slide-in
  const slideinOverlay = document.getElementById('slideinOverlay');
  const slideinPanel = document.getElementById('slideinPanel');
  const slideinBody = document.getElementById('slideinBody');
  document.querySelectorAll('[data-action="details"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation(); const item = btn.closest('.act-item');
      if (!item || !slideinBody) return;
      const summary = item.querySelector('.act-item__summary')?.innerHTML || '';
      const badges = item.querySelector('.act-item__top')?.innerHTML || '';
      const dd = item.dataset.details ? JSON.parse(item.dataset.details) : null;
      let html = `<div style="margin-bottom:12px">${badges}</div><div style="font-size:14px;line-height:1.6;margin-bottom:16px">${summary}</div>`;
      if (dd) { html += '<dl class="act-detail-grid">'; for (const [k,v] of Object.entries(dd)) html += `<dt>${k}</dt><dd>${v}</dd>`; html += '</dl>'; }
      slideinBody.innerHTML = html; slideinOverlay?.classList.add('open'); slideinPanel?.classList.add('open');
    });
  });
  window.closeSlidein = function() { slideinOverlay?.classList.remove('open'); slideinPanel?.classList.remove('open'); };
  slideinOverlay?.addEventListener('click', closeSlidein);
  document.getElementById('slideinClose')?.addEventListener('click', closeSlidein);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeSlidein(); });

  // ── CHART UTILITIES ──
  const METRIC_DEFS = {
    cost:{label:'Cost',prefix:'£',suffix:''},impressions:{label:'Impressions',prefix:'',suffix:''},
    clicks:{label:'Clicks',prefix:'',suffix:''},avgCpc:{label:'Avg CPC',prefix:'£',suffix:''},
    ctr:{label:'CTR',prefix:'',suffix:'%'},conversions:{label:'Conversions',prefix:'',suffix:''},
    cpa:{label:'CPA (Cost/Conv)',prefix:'£',suffix:''},convRate:{label:'Conv Rate',prefix:'',suffix:'%'},
    score:{label:'Performance Score',prefix:'',suffix:''},budgetUtil:{label:'Budget Utilisation %',prefix:'',suffix:'%'},
  };
  function seededData(base,variance,count,round){const d=[];for(let i=0;i<count;i++){const v=base+(Math.sin(i*1.7+base*0.1)*variance);d.push(round?Math.round(v):Math.round(v*100)/100);}return d;}
  function makeDailyLabels(days){const l=[],d=new Date(2026,3,8);for(let i=days-1;i>=0;i--){const dt=new Date(d);dt.setDate(d.getDate()-i);l.push(dt.getDate()+' '+['Jan','Feb','Mar','Apr'][dt.getMonth()]);}return l;}
  function makeWeeklyLabels(weeks){const l=[],d=new Date(2026,3,8);for(let i=weeks-1;i>=0;i--){const dt=new Date(d);dt.setDate(d.getDate()-i*7);l.push(dt.getDate()+' '+['Jan','Feb','Mar','Apr'][dt.getMonth()]);}return l;}

  function getChartData(range, baseMultiplier) {
    const bm = baseMultiplier || 1;
    if (range === '90d') {
      const n=13, daily={cost:seededData(27*bm,8*bm,91,true),impr:seededData(620*bm,120*bm,91,true),clicks:seededData(43*bm,10*bm,91,true),conv:seededData(1.4*bm,0.8*bm,91,true),cpc:seededData(0.63,0.12,91,false),ctr:seededData(6.9,0.8,91,false),cpa:seededData(19.5,5,91,false),cvr:seededData(3.3,0.6,91,false),score:seededData(78,12,91,true),util:seededData(90,8,91,true)};
      function ws(a){const r=[];for(let w=0;w<n;w++){let s=0;for(let d=0;d<7&&w*7+d<a.length;d++)s+=a[w*7+d];r.push(Math.round(s));}return r;}
      function wa(a){const r=[];for(let w=0;w<n;w++){let s=0,c=0;for(let d=0;d<7&&w*7+d<a.length;d++){s+=a[w*7+d];c++;}r.push(Math.round(s/c*100)/100);}return r;}
      return{labels:makeWeeklyLabels(n),metrics:{cost:ws(daily.cost),impressions:ws(daily.impr),clicks:ws(daily.clicks),conversions:ws(daily.conv),avgCpc:wa(daily.cpc),ctr:wa(daily.ctr),cpa:wa(daily.cpa),convRate:wa(daily.cvr),score:wa(daily.score),budgetUtil:wa(daily.util)}};
    }
    const n=range==='7d'?7:30;
    return{labels:makeDailyLabels(n),metrics:{cost:seededData(27*bm,8*bm,n,true),impressions:seededData(620*bm,120*bm,n,true),clicks:seededData(43*bm,10*bm,n,true),avgCpc:seededData(0.63,0.12,n,false),ctr:seededData(6.9,0.8,n,false),conversions:seededData(1.4*bm,0.8*bm,n,true),cpa:seededData(19.5,5,n,false),convRate:seededData(3.3,0.6,n,false),score:seededData(78,12,n,true),budgetUtil:seededData(90,8,n,true)}};
  }

  function isDark(){return document.documentElement.getAttribute('data-theme')==='dark';}
  function cc(line1){const d=isDark();return{line1,line2:'#3b82f6',fill1:'rgba(16,185,129,0.08)',fill2:'rgba(59,130,246,0.08)',grid:d?'rgba(255,255,255,0.06)':'rgba(0,0,0,0.06)',text:d?'#fff':'#000',border:d?'rgba(255,255,255,0.1)':'rgba(0,0,0,0.1)'};}

  function makeChart(canvas, range, lineColor, bm) {
    if(!canvas) return null;
    const m1Key=canvas.closest('.tab-panel')?.querySelector('[id^="chartMetric1"]')?.value || 'cost';
    const m2Key=canvas.closest('.tab-panel')?.querySelector('[id^="chartMetric2"]')?.value || 'conversions';
    const m1=METRIC_DEFS[m1Key],m2=METRIC_DEFS[m2Key],cd=getChartData(range,bm),c=cc(lineColor);
    const existing=Chart.getChart(canvas); if(existing) existing.destroy();
    return new Chart(canvas,{type:'line',data:{labels:cd.labels,datasets:[
      {label:m1.label,data:cd.metrics[m1Key],borderColor:c.line1,backgroundColor:c.fill1,fill:true,tension:0,pointRadius:3,pointHoverRadius:5,pointBackgroundColor:c.line1,pointBorderColor:c.line1,borderWidth:2,yAxisID:'y1'},
      {label:m2.label,data:cd.metrics[m2Key],borderColor:c.line2,backgroundColor:c.fill2,fill:true,tension:0,pointRadius:3,pointHoverRadius:5,pointBackgroundColor:c.line2,pointBorderColor:c.line2,borderWidth:2,yAxisID:'y2'}
    ]},options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
      plugins:{legend:{display:false},tooltip:{backgroundColor:isDark()?'#1e293b':'#fff',titleColor:c.text,bodyColor:c.text,borderColor:c.border,borderWidth:1,padding:10,
        callbacks:{title:i=>i[0]?.label||'',label:ctx=>{const d=ctx.datasetIndex===0?m1:m2;return`${d.label}: ${d.prefix}${ctx.parsed.y}${d.suffix}`;}}}},
      scales:{x:{grid:{color:c.grid},ticks:{color:c.text,font:{size:12},maxRotation:0,autoSkipPadding:12},border:{color:c.border}},
        y1:{position:'left',title:{display:true,text:m1.label,color:c.line1,font:{size:12,weight:600}},grid:{color:c.grid},ticks:{color:c.text,font:{size:12},callback:v=>m1.prefix+v+m1.suffix},border:{color:c.border}},
        y2:{position:'right',title:{display:true,text:m2.label,color:c.line2,font:{size:12,weight:600}},grid:{drawOnChartArea:false},ticks:{color:c.text,font:{size:12},callback:v=>m2.prefix+v+m2.suffix},border:{color:c.border}}
      }}});
  }

  // ── TAB 1: ALL CAMPAIGNS ──
  let currentRangeAll = '30d';
  let currentRange = '30d';

  const TABLE_DATA = {
    '7d':[{n:'GLO Campaign — Core',st:'tCPA £25',r:'cp',s:'enabled',b:'£30/d',c:'£125.40',im:'2,680',cl:'192',cpc:'£0.65',ctr:'7.16%',cv:'7',cc:'£17.91',cvr:'3.65%',sc:'82'},
      {n:'GLO Campaign — Retargeting',st:'tCPA £15',r:'rt',s:'enabled',b:'£10/d',c:'£41.80',im:'810',cl:'62',cpc:'£0.67',ctr:'7.65%',cv:'3',cc:'£13.93',cvr:'4.84%',sc:'91'},
      {n:'Brand — Objection Experts',st:'Manual CPC',r:'bd',s:'enabled',b:'£5/d',c:'£17.50',im:'720',cl:'50',cpc:'£0.35',ctr:'6.94%',cv:'1',cc:'£17.50',cvr:'2.00%',sc:'95'},
      {n:'Testing — New Keywords',st:'Max Clicks',r:'ts',s:'enabled',b:'£5/d',c:'£26.30',im:'390',cl:'16',cpc:'£1.64',ctr:'4.10%',cv:'0',cc:'—',cvr:'0.00%',sc:'38'}],
    '30d':[{n:'GLO Campaign — Core',st:'tCPA £25',r:'cp',s:'enabled',b:'£30/d',c:'£487.20',im:'10,850',cl:'780',cpc:'£0.62',ctr:'7.19%',cv:'26',cc:'£18.74',cvr:'3.33%',sc:'82'},
      {n:'GLO Campaign — Retargeting',st:'tCPA £15',r:'rt',s:'enabled',b:'£10/d',c:'£164.40',im:'3,200',cl:'245',cpc:'£0.67',ctr:'7.66%',cv:'12',cc:'£13.70',cvr:'4.90%',sc:'91'},
      {n:'Brand — Objection Experts',st:'Manual CPC',r:'bd',s:'enabled',b:'£5/d',c:'£68.50',im:'2,800',cl:'195',cpc:'£0.35',ctr:'6.96%',cv:'3',cc:'£22.83',cvr:'1.54%',sc:'95'},
      {n:'Testing — New Keywords',st:'Max Clicks',r:'ts',s:'enabled',b:'£5/d',c:'£102.90',im:'1,570',cl:'64',cpc:'£1.61',ctr:'4.08%',cv:'1',cc:'£102.90',cvr:'1.56%',sc:'38'}],
    '90d':[{n:'GLO Campaign — Core',st:'tCPA £25',r:'cp',s:'enabled',b:'£30/d',c:'£1,461.60',im:'32,550',cl:'2,340',cpc:'£0.62',ctr:'7.19%',cv:'78',cc:'£18.74',cvr:'3.33%',sc:'82'},
      {n:'GLO Campaign — Retargeting',st:'tCPA £15',r:'rt',s:'enabled',b:'£10/d',c:'£493.20',im:'9,600',cl:'735',cpc:'£0.67',ctr:'7.66%',cv:'36',cc:'£13.70',cvr:'4.90%',sc:'91'},
      {n:'Brand — Objection Experts',st:'Manual CPC',r:'bd',s:'enabled',b:'£5/d',c:'£205.50',im:'8,400',cl:'585',cpc:'£0.35',ctr:'6.96%',cv:'9',cc:'£22.83',cvr:'1.54%',sc:'95'},
      {n:'Testing — New Keywords',st:'Max Clicks',r:'ts',s:'enabled',b:'£5/d',c:'£308.70',im:'4,710',cl:'192',cpc:'£1.61',ctr:'4.08%',cv:'3',cc:'£102.90',cvr:'1.56%',sc:'38'}]
  };
  const SUM={
    '7d':{c:'£211',im:'4,600',cl:'320',cpc:'£0.66',cv:'11',cpa:'£19.18',cvr:'3.44%'},
    '30d':{c:'£823',im:'18,420',cl:'1,284',cpc:'£0.64',cv:'42',cpa:'£19.60',cvr:'3.27%'},
    '90d':{c:'£2,469',im:'55,260',cl:'3,852',cpc:'£0.64',cv:'126',cpa:'£19.60',cvr:'3.27%'}
  };

  function updateAllTable(range) {
    const rows=TABLE_DATA[range],s=SUM[range],tbody=document.querySelector('#allCampaignsTable tbody');
    if(!tbody||!rows) return;
    tbody.querySelectorAll('tr').forEach(r=>r.remove());
    const sc={'82':'score--high','91':'score--high','95':'score--high','38':'score--low'};
    rows.forEach(r=>{
      const tr=document.createElement('tr');tr.dataset.status=r.s;
      tr.innerHTML=`<td><span class="status-dot status-dot--${r.s}"></span></td><td><span class="campaign-name-link">${r.n}</span></td><td><span class="strategy-badge">${r.st}</span></td><td><span class="role-badge role-badge--${r.r}">${r.r.toUpperCase()}</span></td><td>${r.b}</td><td>${r.c}</td><td>${r.im}</td><td>${r.cl}</td><td>${r.cpc}</td><td>${r.ctr}</td><td>${r.cv}</td><td>${r.cc}</td><td>${r.cvr}</td><td><span class="score-display ${sc[r.sc]||'score--mid'}">${r.sc}</span></td>`;
      tbody.appendChild(tr);
      // Re-bind campaign name click
      tr.querySelector('.campaign-name-link').addEventListener('click', () => {
        document.querySelector('.page-tab[data-tab="tabDetail"]').click();
        showToast(`Viewing: ${r.n}`, 'info');
      });
    });
    const tot=document.createElement('tr');tot.className='totals-row';
    tot.innerHTML=`<td></td><td>Total / Average</td><td></td><td></td><td>£50/d</td><td>${s.c}</td><td>${s.im}</td><td>${s.cl}</td><td>${s.cpc}</td><td>—</td><td>${s.cv}</td><td>${s.cpa}</td><td>${s.cvr}</td><td>—</td>`;
    tbody.appendChild(tot);
    // Update summary cards
    const cards=document.querySelectorAll('#tabAll .summary-card');
    [s.c,s.im,s.cl,s.cpc,s.cv,s.cpa,s.cvr].forEach((v,i)=>{if(cards[i])cards[i].querySelector('.summary-card__value').textContent=v;});
  }

  function filterAllTable(filter) {
    document.querySelectorAll('#allCampaignsTable tbody tr').forEach(row => {
      if(row.classList.contains('totals-row')) return;
      if(filter==='all'){row.style.display='';return;}
      row.style.display=(row.dataset.status===filter)?'':'none';
    });
  }

  function buildChartAll(){makeChart(document.getElementById('chartAll'),currentRangeAll,'#10b981',1);}

  // ── TAB 2: CAMPAIGN DETAIL ──
  let currentRangeDetail = '30d';

  function buildChartDetail(){makeChart(document.getElementById('chartDetail'),currentRangeDetail,'#10b981',0.6);}

  // ── PILL BUTTONS ──
  document.querySelectorAll('.pill-group').forEach(group => {
    group.querySelectorAll('.pill-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        group.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        if (btn.dataset.range) {
          const tab = btn.closest('.tab-panel');
          if (tab?.id === 'tabAll') {
            currentRangeAll = btn.dataset.range;
            const days = currentRangeAll==='7d'?'7':currentRangeAll==='30d'?'30':'90';
            document.getElementById('allPerfContext').textContent = `— 4 campaigns, ${days} days`;
            buildChartAll(); updateAllTable(currentRangeAll);
          } else {
            currentRangeDetail = btn.dataset.range;
            const days = currentRangeDetail==='7d'?'7':currentRangeDetail==='30d'?'30':'90';
            document.getElementById('detailPerfContext').textContent = `— ${days} days`;
            buildChartDetail();
          }
          showToast(`Showing ${btn.textContent.trim()} data`, 'info');
        }
        if (btn.dataset.filter) filterAllTable(btn.dataset.filter);
      });
    });
  });

  // ── METRIC SELECTOR CHANGE ──
  document.querySelectorAll('[id^="chartMetric1"], [id^="chartMetric2"]').forEach(sel => {
    sel.addEventListener('change', () => {
      const tab = sel.closest('.tab-panel');
      if (tab?.id === 'tabAll') buildChartAll(); else buildChartDetail();
    });
  });

  // Table sorting
  document.querySelectorAll('.data-table th[data-sort]').forEach(th => {
    th.addEventListener('click', () => {
      const table=th.closest('table'),tbody=table.querySelector('tbody');
      const rows=Array.from(tbody.querySelectorAll('tr:not(.totals-row)'));
      const idx=Array.from(th.parentElement.children).indexOf(th);
      const asc=th.dataset.dir!=='asc'; th.dataset.dir=asc?'asc':'desc';
      table.querySelectorAll('th').forEach(h=>{if(h!==th)delete h.dataset.dir;});
      rows.sort((a,b)=>{let va=a.children[idx]?.textContent.trim().replace(/[£%,]/g,'')||'',vb=b.children[idx]?.textContent.trim().replace(/[£%,]/g,'')||'';const na=parseFloat(va),nb=parseFloat(vb);if(!isNaN(na)&&!isNaN(nb))return asc?na-nb:nb-na;return asc?va.localeCompare(vb):vb.localeCompare(va);});
      rows.forEach(r=>tbody.appendChild(r));
    });
  });

  // Build initial charts
  buildChartAll();
  // Detail chart builds when tab is switched

  // Rebuild charts on theme change
  new MutationObserver(() => { setTimeout(() => { buildChartAll(); if (document.getElementById('tabDetail').classList.contains('active')) buildChartDetail(); }, 50); })
    .observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

  function showToast(msg,type='info'){
    document.querySelectorAll('.act-toast').forEach(t=>t.remove());
    const toast=document.createElement('div');toast.className=`act-toast act-toast--${type}`;
    toast.innerHTML=`<span class="material-symbols-outlined" style="font-size:18px">${type==='success'?'check_circle':type==='warning'?'undo':type==='error'?'error':'info'}</span>${msg}`;
    document.body.appendChild(toast);requestAnimationFrame(()=>{requestAnimationFrame(()=>toast.classList.add('show'));});
    setTimeout(()=>{toast.classList.remove('show');setTimeout(()=>toast.remove(),300);},3000);
  }
});
