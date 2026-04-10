/* ============================================================================
   ACT PROTOTYPE — CAMPAIGN LEVEL OPTION B INTERACTIONS
   Single campaign detail. Chart only (no table), lever status, strategy panel.
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

  // Campaign selector
  document.getElementById('campaignSelect')?.addEventListener('change', function() {
    showToast(`Viewing: ${this.options[this.selectedIndex].text}`, 'info');
  });

  // Section collapse
  document.querySelectorAll('.acct-section__header, .act-section__header').forEach(header => {
    header.addEventListener('click', (e) => {
      if (e.target.closest('.pill-group')) return;
      const section = header.closest('.acct-section') || header.closest('.act-section');
      if (section) section.classList.toggle('collapsed');
    });
  });

  // Lever card expand/collapse
  document.querySelectorAll('.lever-card__header').forEach(h => {
    h.addEventListener('click', () => h.closest('.lever-card').classList.toggle('collapsed'));
  });

  // Group collapse
  document.querySelectorAll('.act-group__header').forEach(h => {
    h.addEventListener('click', (e) => { e.stopPropagation(); h.closest('.act-group').classList.toggle('collapsed'); });
  });

  // Approve/Decline/Undo
  document.querySelectorAll('[data-action="approve"]').forEach(btn => {
    btn.addEventListener('click', (e) => { e.stopPropagation(); const i = btn.closest('.act-item'); if(i){i.style.opacity='0.4';i.style.pointerEvents='none';} showToast('Approved — change will be applied in next cycle','success'); });
  });
  document.querySelectorAll('[data-action="decline"]').forEach(btn => {
    btn.addEventListener('click', (e) => { e.stopPropagation(); const i = btn.closest('.act-item'); if(i){i.style.opacity='0.4';i.style.pointerEvents='none';} showToast('Declined — no changes will be made','info'); });
  });
  document.querySelectorAll('[data-action="undo"]').forEach(btn => {
    btn.addEventListener('click', (e) => { e.stopPropagation(); const i = btn.closest('.act-item'); if(i){i.style.opacity='0.4';i.style.pointerEvents='none';} showToast('Undo queued','warning'); });
  });

  // Slide-in
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
      if (detailData) { html += '<dl class="act-detail-grid">'; for (const [k,v] of Object.entries(detailData)) html += `<dt>${k}</dt><dd>${v}</dd>`; html += '</dl>'; }
      slideinBody.innerHTML = html;
      slideinOverlay?.classList.add('open'); slideinPanel?.classList.add('open');
    });
  });
  window.closeSlidein = function() { slideinOverlay?.classList.remove('open'); slideinPanel?.classList.remove('open'); };
  slideinOverlay?.addEventListener('click', closeSlidein);
  document.getElementById('slideinClose')?.addEventListener('click', closeSlidein);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeSlidein(); });

  // ── CHART ──
  const METRIC_DEFS = {
    cost:{label:'Cost',prefix:'£',suffix:''}, impressions:{label:'Impressions',prefix:'',suffix:''},
    clicks:{label:'Clicks',prefix:'',suffix:''}, avgCpc:{label:'Avg CPC',prefix:'£',suffix:''},
    ctr:{label:'CTR',prefix:'',suffix:'%'}, conversions:{label:'Conversions',prefix:'',suffix:''},
    cpa:{label:'CPA (Cost/Conv)',prefix:'£',suffix:''}, convRate:{label:'Conv Rate',prefix:'',suffix:'%'},
    score:{label:'Performance Score',prefix:'',suffix:''}, budgetUtil:{label:'Budget Utilisation %',prefix:'',suffix:'%'},
  };

  function seededData(base,variance,count,round) {
    const data=[]; for(let i=0;i<count;i++){const v=base+(Math.sin(i*1.7+base*0.1)*variance);data.push(round?Math.round(v):Math.round(v*100)/100);}return data;
  }
  function makeDailyLabels(days) { const l=[],d=new Date(2026,3,8); for(let i=days-1;i>=0;i--){const dt=new Date(d);dt.setDate(d.getDate()-i);l.push(dt.getDate()+' '+['Jan','Feb','Mar','Apr'][dt.getMonth()]);}return l; }
  function makeWeeklyLabels(weeks) { const l=[],d=new Date(2026,3,8); for(let i=weeks-1;i>=0;i--){const dt=new Date(d);dt.setDate(d.getDate()-i*7);l.push(dt.getDate()+' '+['Jan','Feb','Mar','Apr'][dt.getMonth()]);}return l; }

  let currentRange = '30d';

  function getChartData(range) {
    if (range === '90d') {
      const n=13, daily={cost:seededData(16,5,91,true),impr:seededData(360,80,91,true),clicks:seededData(26,7,91,true),conv:seededData(0.9,0.5,91,true),cpc:seededData(0.62,0.15,91,false),ctr:seededData(7.2,1,91,false),cpa:seededData(18.5,4,91,false),cvr:seededData(3.4,0.7,91,false),score:seededData(80,10,91,true),util:seededData(92,6,91,true)};
      function ws(a){const r=[];for(let w=0;w<n;w++){let s=0;for(let d=0;d<7&&w*7+d<a.length;d++)s+=a[w*7+d];r.push(Math.round(s));}return r;}
      function wa(a){const r=[];for(let w=0;w<n;w++){let s=0,c=0;for(let d=0;d<7&&w*7+d<a.length;d++){s+=a[w*7+d];c++;}r.push(Math.round(s/c*100)/100);}return r;}
      return{labels:makeWeeklyLabels(n),metrics:{cost:ws(daily.cost),impressions:ws(daily.impr),clicks:ws(daily.clicks),conversions:ws(daily.conv),avgCpc:wa(daily.cpc),ctr:wa(daily.ctr),cpa:wa(daily.cpa),convRate:wa(daily.cvr),score:wa(daily.score),budgetUtil:wa(daily.util)}};
    }
    const n=range==='7d'?7:30;
    return{labels:makeDailyLabels(n),metrics:{cost:seededData(16,5,n,true),impressions:seededData(360,80,n,true),clicks:seededData(26,7,n,true),avgCpc:seededData(0.62,0.15,n,false),ctr:seededData(7.2,1,n,false),conversions:seededData(0.9,0.5,n,true),cpa:seededData(18.5,4,n,false),convRate:seededData(3.4,0.7,n,false),score:seededData(80,10,n,true),budgetUtil:seededData(92,6,n,true)}};
  }

  // Date range pills
  document.querySelectorAll('.pill-group').forEach(group => {
    group.querySelectorAll('.pill-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        group.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        if (btn.dataset.range) {
          currentRange = btn.dataset.range;
          const days = currentRange==='7d'?'7':currentRange==='30d'?'30':'90';
          const ctx = document.getElementById('perfContext');
          if (ctx) ctx.textContent = `— ${days} days`;
          buildChart();
          showToast(`Showing ${btn.textContent.trim()} data`, 'info');
        }
      });
    });
  });

  const chartCanvas = document.getElementById('performanceChart');
  let perfChart = null;
  function isDark() { return document.documentElement.getAttribute('data-theme') === 'dark'; }
  function getChartColors() {
    const dark=isDark();
    return{line1:'#10b981',line2:'#3b82f6',fill1:'rgba(16,185,129,0.08)',fill2:'rgba(59,130,246,0.08)',
      grid:dark?'rgba(255,255,255,0.06)':'rgba(0,0,0,0.06)',text:dark?'#ffffff':'#000000',border:dark?'rgba(255,255,255,0.1)':'rgba(0,0,0,0.1)'};
  }

  function buildChart() {
    if(!chartCanvas) return;
    const m1Key=document.getElementById('chartMetric1').value, m2Key=document.getElementById('chartMetric2').value;
    const m1=METRIC_DEFS[m1Key],m2=METRIC_DEFS[m2Key],cd=getChartData(currentRange),c=getChartColors();
    if(perfChart) perfChart.destroy();
    perfChart = new Chart(chartCanvas, {
      type:'line',
      data:{labels:cd.labels,datasets:[
        {label:m1.label,data:cd.metrics[m1Key],borderColor:c.line1,backgroundColor:c.fill1,fill:true,tension:0,pointRadius:3,pointHoverRadius:5,pointBackgroundColor:c.line1,pointBorderColor:c.line1,borderWidth:2,yAxisID:'y1'},
        {label:m2.label,data:cd.metrics[m2Key],borderColor:c.line2,backgroundColor:c.fill2,fill:true,tension:0,pointRadius:3,pointHoverRadius:5,pointBackgroundColor:c.line2,pointBorderColor:c.line2,borderWidth:2,yAxisID:'y2'}
      ]},
      options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
        plugins:{legend:{display:false},tooltip:{backgroundColor:isDark()?'#1e293b':'#ffffff',titleColor:c.text,bodyColor:c.text,borderColor:c.border,borderWidth:1,padding:10,
          callbacks:{title:i=>i[0]?.label||'',label:ctx=>{const d=ctx.datasetIndex===0?m1:m2;return`${d.label}: ${d.prefix}${ctx.parsed.y}${d.suffix}`;}}}},
        scales:{x:{grid:{color:c.grid},ticks:{color:c.text,font:{size:12},maxRotation:0,autoSkipPadding:12},border:{color:c.border}},
          y1:{position:'left',title:{display:true,text:m1.label,color:c.line1,font:{size:12,weight:600}},grid:{color:c.grid},ticks:{color:c.text,font:{size:12},callback:v=>m1.prefix+v+m1.suffix},border:{color:c.border}},
          y2:{position:'right',title:{display:true,text:m2.label,color:c.line2,font:{size:12,weight:600}},grid:{drawOnChartArea:false},ticks:{color:c.text,font:{size:12},callback:v=>m2.prefix+v+m2.suffix},border:{color:c.border}}
        }
      }
    });
  }

  buildChart();
  document.getElementById('chartMetric1')?.addEventListener('change', buildChart);
  document.getElementById('chartMetric2')?.addEventListener('change', buildChart);
  new MutationObserver(() => { setTimeout(buildChart, 50); }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

  function showToast(message, type='info') {
    document.querySelectorAll('.act-toast').forEach(t=>t.remove());
    const toast=document.createElement('div'); toast.className=`act-toast act-toast--${type}`;
    toast.innerHTML=`<span class="material-symbols-outlined" style="font-size:18px">${type==='success'?'check_circle':type==='warning'?'undo':type==='error'?'error':'info'}</span>${message}`;
    document.body.appendChild(toast);
    requestAnimationFrame(()=>{requestAnimationFrame(()=>toast.classList.add('show'));});
    setTimeout(()=>{toast.classList.remove('show');setTimeout(()=>toast.remove(),300);},3000);
  }
});
