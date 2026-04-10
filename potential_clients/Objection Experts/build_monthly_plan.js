const pptxgen = require("pptxgenjs");
const path = require("path");

const CHART_DIR = path.join(__dirname, "charts");
const OUTPUT = path.join(__dirname, "reports", "04_monthly_optimisation_plan_v2.pptx");

const NAVY = "1A237E", BLUE = "4285F4", RED = "EA4335", AMBER = "FBBC05", GREEN = "34A853";
const L_GREY = "F5F6FA", BLACK = "1A1A1A", WHITE = "FFFFFF";
const LOGO_PATH = path.join(CHART_DIR, "act_logo.png");

const F = { HERO: 44, TITLE: 28, STAT: 22, SECTION: 14, BODY: 11, FOOTER: 11 };
const makeCardShadow = () => ({ type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.10 });

let pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Christopher Hoole";
pres.title = "Monthly Optimisation Plan \u2014 Objection Experts";
const W = 13.33, MARGIN = 0.6;

function addStripeBar(s, y, h) {
  const sW = W/4;
  s.addShape(pres.shapes.RECTANGLE, {x:0,y,w:sW,h,fill:{color:BLUE}});
  s.addShape(pres.shapes.RECTANGLE, {x:sW,y,w:sW,h,fill:{color:RED}});
  s.addShape(pres.shapes.RECTANGLE, {x:sW*2,y,w:sW,h,fill:{color:AMBER}});
  s.addShape(pres.shapes.RECTANGLE, {x:sW*3,y,w:sW,h,fill:{color:GREEN}});
}

function addFooter(s, n) {
  const bY=6.92, bW=(W-2*MARGIN)/4;
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:bY,w:bW,h:0.03,fill:{color:BLUE}});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN+bW,y:bY,w:bW,h:0.03,fill:{color:RED}});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN+bW*2,y:bY,w:bW,h:0.03,fill:{color:AMBER}});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN+bW*3,y:bY,w:bW,h:0.03,fill:{color:GREEN}});
  s.addImage({path:LOGO_PATH,x:MARGIN,y:7.0,w:0.22,h:0.22});
  s.addText([{text:"Christopher Hoole",options:{bold:true,color:NAVY}},{text:"  |  christopherhoole.com  |  Confidential",options:{color:BLACK}}],
    {x:MARGIN+0.3,y:7.0,w:6,h:0.25,fontSize:F.FOOTER,fontFace:"Calibri",valign:"middle"});
  s.addText(String(n),{x:W-MARGIN-0.5,y:7.0,w:0.5,h:0.25,fontSize:F.FOOTER,color:NAVY,fontFace:"Calibri",align:"right",valign:"middle"});
}

function addSlideTitle(s, title, subtitle) {
  addStripeBar(s,0,0.06);
  s.addText(title,{x:MARGIN,y:0.3,w:7,h:0.5,fontSize:F.TITLE,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  if(subtitle) s.addText(subtitle,{x:MARGIN,y:0.85,w:10,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:BLUE,margin:0});
}

// ═══════════════════════════════════════════
// SLIDE 1: TITLE
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:L_GREY};
  addStripeBar(s,0,0.07);
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:0.07,w:0.12,h:7.43,fill:{color:BLUE}});
  s.addImage({path:LOGO_PATH,x:0.6,y:0.5,w:0.65,h:0.65});

  s.addText("MONTHLY\nOPTIMISATION PLAN",{x:0.6,y:1.4,w:5.5,h:1.8,fontSize:F.HERO,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addShape(pres.shapes.RECTANGLE,{x:0.6,y:3.3,w:2.5,h:0.05,fill:{color:BLUE}});
  s.addText("Objection Experts",{x:0.6,y:3.55,w:5.5,h:0.5,fontSize:F.STAT,fontFace:"Calibri",color:BLUE,margin:0});
  s.addText([
    {text:"Prepared by Christopher Hoole",options:{breakLine:true,fontSize:F.BODY,color:BLACK,bold:true}},
    {text:"Google Ads Specialist  |  April 2026",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"christopherhoole.com",options:{fontSize:F.BODY,color:BLUE}},
  ],{x:0.6,y:4.3,w:5.5,h:1.0,fontFace:"Calibri",margin:0});

  // Right side
  const rX=6.8, rW=5.9;
  s.addShape(pres.shapes.RECTANGLE,{x:rX,y:0.5,w:rW,h:2.0,fill:{color:WHITE},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:rX,y:0.5,w:0.08,h:2.0,fill:{color:GREEN}});
  s.addText("Target KPI",{x:rX+0.3,y:0.6,w:rW-0.5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",color:NAVY,margin:0});
  s.addText("\u00A325 CPA",{x:rX+0.3,y:0.95,w:rW-0.5,h:0.7,fontSize:F.HERO,fontFace:"Calibri",bold:true,color:GREEN,margin:0});
  s.addText("Cost per lead target",{x:rX+0.3,y:1.7,w:rW-0.5,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});

  const smW=(rW-0.2)/2, smY=2.8, smH=1.0;
  s.addShape(pres.shapes.RECTANGLE,{x:rX,y:smY,w:smW,h:smH,fill:{color:WHITE},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:rX,y:smY,w:0.06,h:smH,fill:{color:BLUE}});
  s.addText("2 hrs/week",{x:rX+0.15,y:smY+0.1,w:smW-0.25,h:0.4,fontSize:F.STAT,fontFace:"Calibri",bold:true,color:BLUE,margin:0});
  s.addText("Every Monday",{x:rX+0.15,y:smY+0.55,w:smW-0.25,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});

  const sm2X=rX+smW+0.2;
  s.addShape(pres.shapes.RECTANGLE,{x:sm2X,y:smY,w:smW,h:smH,fill:{color:WHITE},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:sm2X,y:smY,w:0.06,h:smH,fill:{color:AMBER}});
  s.addText("3 months",{x:sm2X+0.15,y:smY+0.1,w:smW-0.25,h:0.4,fontSize:F.STAT,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addText("Initial plan horizon",{x:sm2X+0.15,y:smY+0.55,w:smW-0.25,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});

  addStripeBar(s,7.0,0.04);
}

// ═══════════════════════════════════════════
// SLIDE 2: OVERVIEW
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:WHITE};
  addSlideTitle(s,"Optimisation Cadence","2 hours every Monday \u2014 consistent, data-driven improvement");

  // Weekly recurring tasks
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.3,w:W-2*MARGIN,h:1.8,fill:{color:L_GREY},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.3,w:0.06,h:1.8,fill:{color:BLUE}});
  s.addText("Every Monday (recurring tasks)",{x:MARGIN+0.25,y:1.4,w:10,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addText([
    {text:"Search term review \u2014 exclude irrelevant terms, identify new keyword opportunities",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Performance check \u2014 CPA, conversion rate, spend pacing, Quality Score changes",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Bid adjustment review \u2014 refine schedule, device, and geographic bids based on latest data",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Negative keyword maintenance \u2014 add new phrase/exact negatives from search term findings",options:{bullet:true,fontSize:F.BODY,color:BLACK}},
  ],{x:MARGIN+0.25,y:1.8,w:W-2*MARGIN-0.5,h:1.2,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:3});

  // 3-month timeline
  const phases = [
    {title:"MONTH 1",subtitle:"April 2026",desc:"Foundation",color:RED,items:[
      "Week 1: Keywords, search terms, new ads",
      "Week 2: Landing page planning + build",
      "Week 3: Landing page live + first data review",
      "Week 4: Performance analysis, CPA adjustment, Month 1 report",
    ]},
    {title:"MONTH 2",subtitle:"May 2026",desc:"Optimisation",color:AMBER,items:[
      "QS monitoring post landing page",
      "Target CPA reduction (\u00A330 \u2192 \u00A327)",
      "Ad copy testing cycle 2",
      "Geographic bid refinement",
      "Keyword expansion",
    ]},
    {title:"MONTH 3",subtitle:"June 2026",desc:"Growth",color:GREEN,items:[
      "Target CPA at \u00A325",
      "Full Q2 vs Q1 comparison",
      "Consider PMax campaign retest",
      "Landing page A/B test",
      "Quarterly review with Owen",
    ]},
  ];

  phases.forEach((p,i) => {
    const x = MARGIN + i * 4.1;
    // Card with left colour border (matching our preferred style)
    s.addShape(pres.shapes.RECTANGLE,{x,y:3.4,w:3.85,h:3.2,fill:{color:WHITE},shadow:makeCardShadow(),line:{color:"E2E8F0",width:0.5}});
    s.addShape(pres.shapes.RECTANGLE,{x,y:3.4,w:0.06,h:3.2,fill:{color:p.color}});
    s.addText(p.title,{x:x+0.2,y:3.5,w:2.2,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:p.color,margin:0});
    s.addText(p.subtitle + " \u2014 " + p.desc,{x:x+0.2,y:3.82,w:3.4,h:0.25,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});

    const items = p.items.map((item,j) => ({
      text:item, options:{bullet:true,breakLine:j<p.items.length-1,fontSize:F.BODY,color:BLACK}
    }));
    s.addText(items,{x:x+0.2,y:4.2,w:3.4,h:2.2,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:5});
  });

  addFooter(s,2);
}

// ═══════════════════════════════════════════
// SLIDE 3: MONTH 1 WEEK 1
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:WHITE};
  addSlideTitle(s,"Month 1 \u2014 Week 1 (2 April)",null);
  s.addText("Keywords, Search Terms & Ad Copy",{x:MARGIN,y:0.85,w:10,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:RED,bold:true,margin:0});

  const tasks = [
    {title:"Keyword Audit (45 mins)",items:[
      "Review all active keywords against search term performance data",
      "Add high-converting search terms as new keywords (e.g., \"planning objection solicitor\", \"object planning permission\", \"planning objection advice\")",
      "Check match types \u2014 ensure phrase match is used for core terms",
      "Verify re-enabled keywords are accruing impressions",
    ],color:BLUE},
    {title:"Search Term Exclusion (45 mins)",items:[
      "Bulk review all search terms from the past 30 days",
      "Exclude irrelevant terms \u2014 add to appropriate negative keyword list by word count",
      "Identify any new waste patterns not covered by existing negatives",
      "Document all exclusions for the monthly report",
    ],color:RED},
    {title:"Ad Copy Review (30 mins)",items:[
      "Assess performance of current 3 RSAs + 1 call-only ad",
      "Build 1-2 new RSA variants for split testing (Trust, Speed, or Value angles)",
      "Review headline and description combinations for relevance",
      "Ensure keyword insertion is working correctly",
    ],color:GREEN},
  ];

  tasks.forEach((t,i) => {
    const y = 1.3 + i * 1.7;
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y,w:W-2*MARGIN,h:1.5,fill:{color:WHITE},shadow:makeCardShadow(),line:{color:"E2E8F0",width:0.5}});
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y,w:0.06,h:1.5,fill:{color:t.color}});
    s.addText(t.title,{x:MARGIN+0.25,y:y+0.08,w:10,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
    const items = t.items.map((item,j) => ({
      text:item, options:{bullet:true,breakLine:j<t.items.length-1,fontSize:F.BODY,color:BLACK}
    }));
    s.addText(items,{x:MARGIN+0.25,y:y+0.42,w:W-2*MARGIN-0.5,h:1.0,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:3});
  });

  addFooter(s,3);
}

// ═══════════════════════════════════════════
// SLIDE 4: MONTH 1 WEEK 2
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:WHITE};
  addSlideTitle(s,"Month 1 \u2014 Week 2 (7 April)",null);
  s.addText("Search Terms + Landing Page Build",{x:MARGIN,y:0.85,w:10,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:RED,bold:true,margin:0});

  const tasks = [
    {title:"Search Term Review (30 mins)",items:[
      "Weekly recurring: review new search terms, exclude irrelevant, add promising ones as keywords",
    ],color:BLUE},
    {title:"Landing Page Planning & Build (90 mins)",items:[
      "Get Owen's current site files \u2014 map brand assets (colours, fonts, logos, imagery)",
      "Wireframe new dedicated landing page for planning objection keywords",
      "Shorter, more focused than homepage \u2014 headline, form, trust signals, 1 CTA",
      "Build in Claude Code (HTML/CSS/JS), matching objectionexperts.com brand perfectly",
      "Owen to set up Vercel + GitHub accounts \u2014 connect repo for continuous deployment",
      "Target: LP draft ready for review by end of session",
    ],color:GREEN},
  ];

  tasks.forEach((t,i) => {
    const h = i === 0 ? 1.0 : 3.5;
    const y = i === 0 ? 1.3 : 2.5;
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y,w:W-2*MARGIN,h,fill:{color:WHITE},shadow:makeCardShadow(),line:{color:"E2E8F0",width:0.5}});
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y,w:0.06,h,fill:{color:t.color}});
    s.addText(t.title,{x:MARGIN+0.25,y:y+0.08,w:10,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
    const items = t.items.map((item,j) => ({
      text:item, options:{bullet:true,breakLine:j<t.items.length-1,fontSize:F.BODY,color:BLACK}
    }));
    s.addText(items,{x:MARGIN+0.25,y:y+0.42,w:W-2*MARGIN-0.5,h:h-0.6,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:5});
  });

  // LP goal callout
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:6.2,w:W-2*MARGIN,h:0.5,fill:{color:"E8F0FE"}});
  s.addText("Landing page goal: Improve \"Landing Page Experience\" from Below Average to Average/Above Average \u2014 the #1 Quality Score lever.",{
    x:MARGIN+0.25,y:6.2,w:W-2*MARGIN-0.5,h:0.5,fontSize:F.BODY,fontFace:"Calibri",color:NAVY,bold:true,valign:"middle",margin:0
  });

  addFooter(s,4);
}

// ═══════════════════════════════════════════
// SLIDE 5: MONTH 1 WEEK 3
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:WHITE};
  addSlideTitle(s,"Month 1 \u2014 Week 3 (14 April)",null);
  s.addText("Landing Page Live + First Performance Review",{x:MARGIN,y:0.85,w:10,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:RED,bold:true,margin:0});

  const tasks = [
    {title:"Search Term Review (30 mins)",items:[
      "Weekly recurring: review, exclude, add keywords",
    ],color:BLUE},
    {title:"Landing Page Launch (30 mins)",items:[
      "Final review and QA of landing page on Vercel preview",
      "Owen adds DNS records to connect subdomain (e.g., lp.objectionexperts.com)",
      "Push live, verify tracking is firing correctly (form submissions, phone clicks)",
      "Update Google Ads final URLs to point to new landing page",
    ],color:GREEN},
    {title:"First Performance Review (60 mins)",items:[
      "2 weeks of data since Day 1 changes \u2014 first meaningful comparison",
      "Check: CPA trend (is \u00A330 target holding?), conversion rate, click volume",
      "Check: Are re-enabled keywords getting impressions and converting?",
      "Check: Negative keywords working? Any new irrelevant terms slipping through?",
      "Check: Ad schedule and geographic bid adjustments \u2014 any obvious outliers?",
      "Document findings for month-end report",
    ],color:AMBER},
  ];

  let yPos = 1.3;
  tasks.forEach((t) => {
    const h = t.items.length <= 2 ? 0.9 : (t.items.length <= 4 ? 1.5 : 2.2);
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:yPos,w:W-2*MARGIN,h,fill:{color:WHITE},shadow:makeCardShadow(),line:{color:"E2E8F0",width:0.5}});
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:yPos,w:0.06,h,fill:{color:t.color}});
    s.addText(t.title,{x:MARGIN+0.25,y:yPos+0.08,w:10,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
    const items = t.items.map((item,j) => ({
      text:item, options:{bullet:true,breakLine:j<t.items.length-1,fontSize:F.BODY,color:BLACK}
    }));
    s.addText(items,{x:MARGIN+0.25,y:yPos+0.42,w:W-2*MARGIN-0.5,h:h-0.6,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:3});
    yPos += h + 0.15;
  });

  addFooter(s,5);
}

// ═══════════════════════════════════════════
// SLIDE 6: MONTH 1 WEEK 4
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:WHITE};
  addSlideTitle(s,"Month 1 \u2014 Week 4 (21 April)",null);
  s.addText("Full Analysis + CPA Adjustment + Month 1 Report",{x:MARGIN,y:0.85,w:10,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:RED,bold:true,margin:0});

  const tasks = [
    {title:"Search Term Review (20 mins)",items:[
      "Weekly recurring: review, exclude, add keywords",
    ],color:BLUE},
    {title:"Full Month Performance Analysis (60 mins)",items:[
      "3 weeks of data post Day 1 changes \u2014 compare to pre-change baseline",
      "CPA trend: is \u00A330 target achievable? Reduce to \u00A327 if data supports it",
      "Quality Score check: has landing page improved LP Experience score?",
      "Ad copy: which RSAs are winning? Pause worst performer if clear loser",
      "Geographic: first month of county-level data \u2014 any clear winners/losers?",
      "Device and schedule: refine any bid adjustments with 3 weeks of clean data",
    ],color:AMBER},
    {title:"Month 1 Report for Owen (40 mins)",items:[
      "Build monthly report: what changed, performance comparison, next month's focus",
      "Include: CPA before vs after, conversion rate, Quality Score changes",
      "Include: specific actions taken and their measured impact",
      "Schedule call with Owen to walk through findings",
    ],color:GREEN},
  ];

  let yPos = 1.3;
  tasks.forEach((t) => {
    const h = t.items.length <= 2 ? 0.9 : (t.items.length <= 4 ? 1.5 : 2.2);
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:yPos,w:W-2*MARGIN,h,fill:{color:WHITE},shadow:makeCardShadow(),line:{color:"E2E8F0",width:0.5}});
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:yPos,w:0.06,h,fill:{color:t.color}});
    s.addText(t.title,{x:MARGIN+0.25,y:yPos+0.08,w:10,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
    const items = t.items.map((item,j) => ({
      text:item, options:{bullet:true,breakLine:j<t.items.length-1,fontSize:F.BODY,color:BLACK}
    }));
    s.addText(items,{x:MARGIN+0.25,y:yPos+0.42,w:W-2*MARGIN-0.5,h:h-0.6,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:3});
    yPos += h + 0.15;
  });

  addFooter(s,6);
}

// ═══════════════════════════════════════════
// SLIDE 7: MONTH 2 (individual cards)
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:WHITE};
  addSlideTitle(s,"Month 2 \u2014 May 2026","Optimisation phase \u2014 refine what's working, fix what isn't");

  const items = [
    {label:"Quality Score Monitoring",desc:"Track QS changes after landing page launch. Target: move core keywords from QS 2-3 to QS 5-6. This directly reduces CPC.",color:GREEN},
    {label:"Target CPA Reduction",desc:"If CPA is stable at \u00A330, reduce to \u00A327. Gradual steps \u2014 never more than 15-20% at a time.",color:BLUE},
    {label:"Ad Copy Testing Cycle 2",desc:"Review Month 1 ad test results. Replace worst performing RSA with a new challenger. Test different angles.",color:RED},
    {label:"Geographic Bid Refinement",desc:"Full month of county-level data available. Increase bids on top performers, reduce on underperformers.",color:AMBER},
    {label:"Keyword Expansion",desc:"Promote best converting search terms to keywords. Review close variants. Consider new ad groups if a theme emerges.",color:BLUE},
    {label:"Weekly Search Term Reviews",desc:"Continue every Monday \u2014 this never stops. The negative keyword lists will grow and protection will improve.",color:GREEN},
  ];

  items.forEach((item,i) => {
    const col = i < 3 ? MARGIN : 6.8;
    const row = i < 3 ? i : i - 3;
    const y = 1.3 + row * 1.6;
    const cardW = 5.9;

    s.addShape(pres.shapes.RECTANGLE,{x:col,y,w:cardW,h:1.4,fill:{color:WHITE},shadow:makeCardShadow(),line:{color:"E2E8F0",width:0.5}});
    s.addShape(pres.shapes.RECTANGLE,{x:col,y,w:0.06,h:1.4,fill:{color:item.color}});
    s.addText(item.label,{x:col+0.25,y:y+0.1,w:cardW-0.5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
    s.addText(item.desc,{x:col+0.25,y:y+0.45,w:cardW-0.5,h:0.8,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0,valign:"top"});
  });

  addFooter(s,7);
}

// ═══════════════════════════════════════════
// SLIDE 8: MONTH 3 (individual cards)
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:WHITE};
  addSlideTitle(s,"Month 3 \u2014 June 2026","Growth phase \u2014 scaling what works");

  const items = [
    {label:"Target CPA at \u00A325",desc:"If QS improvements have taken effect, push target CPA to \u00A325. This should yield 60+ leads per month at the \u00A31,500 budget.",color:GREEN},
    {label:"Full Quarter Comparison",desc:"Q2 2026 vs Q1 2026 vs Q4 2025 \u2014 demonstrate the trajectory. CPA, conversion rate, lead volume, Quality Score, impression share.",color:BLUE},
    {label:"PMax Campaign Retest",desc:"The old PMax campaign had a \u00A39.73 CPA with 20 conversions. With the account now clean, a PMax retest could unlock additional volume at low CPA.",color:AMBER},
    {label:"Landing Page A/B Test",desc:"If baseline LP is performing, test a variant (different headline, form placement, or social proof). Small improvements compound.",color:RED},
    {label:"Quarterly Strategy Review",desc:"Call with Owen to review 3 months of progress. Discuss budget, goals, and strategy for Q3. Present the data, agree the next quarter's plan.",color:NAVY},
  ];

  // 3 cards top row, 2 bottom row
  items.forEach((item,i) => {
    const col = i < 3 ? MARGIN + i * 4.1 : MARGIN + (i - 3) * 4.1;
    const y = i < 3 ? 1.3 : 3.6;
    const cardW = 3.85;
    const cardH = i < 3 ? 2.0 : 2.0;

    s.addShape(pres.shapes.RECTANGLE,{x:col,y,w:cardW,h:cardH,fill:{color:WHITE},shadow:makeCardShadow(),line:{color:"E2E8F0",width:0.5}});
    s.addShape(pres.shapes.RECTANGLE,{x:col,y,w:0.06,h:cardH,fill:{color:item.color}});
    s.addText(item.label,{x:col+0.2,y:y+0.1,w:cardW-0.4,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
    s.addText(item.desc,{x:col+0.2,y:y+0.5,w:cardW-0.4,h:cardH-0.7,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0,valign:"top"});
  });

  addFooter(s,8);
}

// ═══════════════════════════════════════════
// SLIDE 9: CPA REDUCTION TIMELINE
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:WHITE};
  addSlideTitle(s,"CPA Reduction Roadmap","Target: \u00A338.63 \u2192 \u00A325 within 3 months");

  // Timeline visual - 4 milestones
  const milestones = [
    {label:"Day 1\n(Today)",value:"\u00A330",desc:"Target CPA set.\nQuick wins implemented.",color:RED,x:1.2},
    {label:"Week 4\n(21 Apr)",value:"\u00A327",desc:"First reduction.\nIf CPA stable at \u00A330.",color:AMBER,x:4.4},
    {label:"Week 8\n(19 May)",value:"\u00A325",desc:"Target achieved.\nQS improvements active.",color:GREEN,x:7.6},
    {label:"Month 3\n(June)",value:"\u00A320-25",desc:"Sustained performance.\nLanding page + QS gains.",color:GREEN,x:10.8},
  ];

  // Connecting line
  s.addShape(pres.shapes.RECTANGLE,{x:1.7,y:2.5,w:9.9,h:0.06,fill:{color:BLUE}});

  milestones.forEach(m => {
    // Circle marker
    s.addShape(pres.shapes.OVAL,{x:m.x,y:2.2,w:0.7,h:0.7,fill:{color:m.color}});
    s.addText(m.value,{x:m.x,y:2.2,w:0.7,h:0.7,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:WHITE,align:"center",valign:"middle",margin:0});
    // Label above
    s.addText(m.label,{x:m.x-0.5,y:1.3,w:1.7,h:0.7,fontSize:F.BODY,fontFace:"Calibri",color:NAVY,bold:true,align:"center",margin:0});
    // Description below
    s.addText(m.desc,{x:m.x-0.5,y:3.15,w:1.7,h:1.0,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,align:"center",margin:0});
  });

  // What drives each reduction
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:4.5,w:W-2*MARGIN,h:2.0,fill:{color:L_GREY},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:4.5,w:0.06,h:2.0,fill:{color:BLUE}});
  s.addText("What Drives Each Reduction",{x:MARGIN+0.25,y:4.6,w:10,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addText([
    {text:"\u00A338 \u2192 \u00A330: ",options:{bold:true,color:RED}},
    {text:"Conversion tracking fix + target CPA guardrail + negative keywords (already done)",options:{breakLine:true,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"\u00A330 \u2192 \u00A327: ",options:{bold:true,color:AMBER}},
    {text:"Re-enabled high-performing keywords + schedule/geo bid optimisations reducing wasted spend",options:{breakLine:true,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"\u00A327 \u2192 \u00A325: ",options:{bold:true,color:GREEN}},
    {text:"Quality Score improvements from dedicated landing page \u2014 lower CPCs across all keywords",options:{breakLine:true,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"\u00A325 sustained: ",options:{bold:true,color:GREEN}},
    {text:"Ongoing weekly optimisation, ad copy testing, keyword expansion, geographic refinement",options:{color:BLACK}},
  ],{x:MARGIN+0.25,y:5.0,w:W-2*MARGIN-0.5,h:1.4,fontSize:F.BODY,fontFace:"Calibri",margin:0,valign:"top"});

  addFooter(s,9);
}

// ── Save ──
pres.writeFile({fileName:OUTPUT}).then(() => {
  console.log(`Monthly plan saved to: ${OUTPUT}`);
}).catch(err => console.error("Error:",err));
