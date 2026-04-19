const pptxgen = require("pptxgenjs");
const path = require("path");

const CHART_DIR = path.join(__dirname, "charts");
const OUTPUT = path.join(__dirname, "reports", "07_week2_session_report_v1.pptx");

const NAVY = "1A237E", BLUE = "4285F4", RED = "EA4335", AMBER = "FBBC05", GREEN = "34A853";
const L_GREY = "F5F6FA", BLACK = "1A1A1A", WHITE = "FFFFFF";
const LOGO_PATH = path.join(CHART_DIR, "act_logo.png");
const F = { HERO: 44, TITLE: 28, STAT: 22, SECTION: 14, BODY: 11, FOOTER: 11 };
const makeCardShadow = () => ({ type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.10 });

let pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Christopher Hoole";
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
  s.addShape(pres.shapes.RECTANGLE,{x:W-MARGIN-2.5,y:0.3,w:2.5,h:0.45,fill:{color:WHITE},line:{color:GREEN,width:1}});
  s.addText("14 April 2026",{x:W-MARGIN-2.4,y:0.32,w:2.3,h:0.4,fontSize:F.BODY,fontFace:"Calibri",color:GREEN,align:"center",valign:"middle",bold:true,margin:0});
  if(subtitle) s.addText(subtitle,{x:MARGIN,y:0.85,w:10,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:BLUE,margin:0});
}

function addStatCard(s,x,y,w,h,val,lab,col) {
  s.addShape(pres.shapes.RECTANGLE,{x,y,w,h,fill:{color:WHITE},shadow:makeCardShadow(),line:{color:"E2E8F0",width:0.5}});
  s.addShape(pres.shapes.RECTANGLE,{x,y,w:0.06,h,fill:{color:col}});
  s.addText(val,{x:x+0.2,y:y+0.1,w:w-0.3,h:0.5,fontSize:F.STAT,fontFace:"Calibri",bold:true,color:col,margin:0});
  s.addText(lab,{x:x+0.2,y:y+0.6,w:w-0.3,h:0.35,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});
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

  s.addText("WEEK 2\nSESSION REPORT",{x:0.6,y:1.4,w:5.5,h:1.5,fontSize:F.HERO,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addShape(pres.shapes.RECTANGLE,{x:0.6,y:3.0,w:2.5,h:0.05,fill:{color:BLUE}});
  s.addText("Objection Experts",{x:0.6,y:3.25,w:5.5,h:0.5,fontSize:F.STAT,fontFace:"Calibri",color:BLUE,margin:0});
  s.addText([
    {text:"14 April 2026",options:{breakLine:true,fontSize:F.BODY,color:BLACK,bold:true}},
    {text:"Christopher Hoole  |  Google Ads Specialist",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"christopherhoole.com",options:{fontSize:F.BODY,color:BLUE}},
  ],{x:0.6,y:4.0,w:5.5,h:1.0,fontFace:"Calibri",margin:0});

  // Right side stats
  const rX=6.8, rW=5.9, smW=(rW-0.4)/3, smH=1.0;

  addStatCard(s,rX,0.5,smW,smH,"53","Terms Excluded",RED);
  addStatCard(s,rX+smW+0.2,0.5,smW,smH,"\u00A319.83","Our RSA CPA",GREEN);
  addStatCard(s,rX+2*(smW+0.2),0.5,smW,smH,"18.75%","Our RSA Conv Rate",BLUE);

  addStatCard(s,rX,1.7,smW,smH,"3","Ads Paused",AMBER);
  addStatCard(s,rX+smW+0.2,1.7,smW,smH,"12","LP Changes",GREEN);
  addStatCard(s,rX+2*(smW+0.2),1.7,smW,smH,"34","Total Conversions",NAVY);

  s.addShape(pres.shapes.RECTANGLE,{x:rX,y:3.0,w:rW,h:1.8,fill:{color:WHITE},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:rX,y:3.0,w:0.06,h:1.8,fill:{color:NAVY}});
  s.addText("Today's Focus",{x:rX+0.25,y:3.1,w:rW-0.5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addText([
    {text:"1. Full data analysis (ads, keywords, search terms)",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"2. Search term exclusions (53 more added)",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"3. Landing page v3 - all Owen's feedback implemented",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"4. Paused RSA 2, call-only ads (poor performance)",options:{bullet:true,fontSize:F.BODY,color:BLACK}},
  ],{x:rX+0.25,y:3.5,w:rW-0.5,h:1.2,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:4});

  addStripeBar(s,7.0,0.04);
}

// ═══════════════════════════════════════════
// SLIDE 2: WEEK-ON-WEEK PERFORMANCE
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:WHITE};
  addSlideTitle(s,"Week-on-Week Performance","GLO Campaign - 6 week trend (2 Mar - 12 Apr 2026)");

  // Weekly performance table
  const tblH = [[
    {text:"Week",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY}},
    {text:"Cost",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Impr",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Clicks",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"CPC",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"CTR",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Conv",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"CPA",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Conv Rate",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Trend",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
  ]];

  const weeks = [
    {w:"2 Mar",cost:"\u00A3324",impr:"1,722",cl:"133",cpc:"\u00A32.44",ctr:"7.72%",conv:"6",cpa:"\u00A354",cr:"4.51%",note:"Pre-changes"},
    {w:"9 Mar",cost:"\u00A3336",impr:"1,759",cl:"130",cpc:"\u00A32.58",ctr:"7.39%",conv:"7",cpa:"\u00A348",cr:"5.38%",note:"Pre-changes"},
    {w:"16 Mar",cost:"\u00A3383",impr:"1,802",cl:"134",cpc:"\u00A32.85",ctr:"7.44%",conv:"4",cpa:"\u00A396",cr:"2.99%",note:"Easter/Low"},
    {w:"23 Mar",cost:"\u00A3389",impr:"1,425",cl:"114",cpc:"\u00A33.41",ctr:"8.00%",conv:"6",cpa:"\u00A365",cr:"5.26%",note:"Easter"},
    {w:"30 Mar",cost:"\u00A3198",impr:"1,092",cl:"74",cpc:"\u00A32.67",ctr:"6.78%",conv:"3",cpa:"\u00A366",cr:"4.05%",note:"Bank holiday"},
    {w:"6 Apr",cost:"\u00A3408",impr:"2,464",cl:"155",cpc:"\u00A32.63",ctr:"6.29%",conv:"8",cpa:"\u00A351",cr:"5.16%",note:"Post-changes"},
  ];

  const tblR = weeks.map((w,i) => {
    const bg = i%2===0 ? L_GREY : WHITE;
    const isLatest = i === 5;
    const cpaColor = w.cpa === "\u00A351" ? GREEN : (w.cpa === "\u00A348" ? GREEN : BLACK);
    return [
      {text:w.w,options:{fill:{color:bg},fontSize:F.BODY,color:BLACK,bold:isLatest}},
      {text:w.cost,options:{fill:{color:bg},fontSize:F.BODY,align:"center",color:BLACK}},
      {text:w.impr,options:{fill:{color:bg},fontSize:F.BODY,align:"center",color:BLACK}},
      {text:w.cl,options:{fill:{color:bg},fontSize:F.BODY,align:"center",color:BLACK}},
      {text:w.cpc,options:{fill:{color:bg},fontSize:F.BODY,align:"center",color:BLACK}},
      {text:w.ctr,options:{fill:{color:bg},fontSize:F.BODY,align:"center",color:BLACK}},
      {text:w.conv,options:{fill:{color:bg},fontSize:F.BODY,align:"center",color:isLatest?GREEN:BLACK,bold:isLatest}},
      {text:w.cpa,options:{fill:{color:bg},fontSize:F.BODY,align:"center",color:cpaColor,bold:true}},
      {text:w.cr,options:{fill:{color:bg},fontSize:F.BODY,align:"center",color:BLACK}},
      {text:w.note,options:{fill:{color:bg},fontSize:F.BODY,align:"center",color:isLatest?GREEN:NAVY}},
    ];
  });

  s.addTable([...tblH,...tblR],{
    x:MARGIN,y:1.3,w:W-2*MARGIN,h:3.0,
    colW:[1.0,0.9,1.0,0.9,0.9,0.9,0.8,0.9,1.0,2.0],
    border:{type:"solid",pt:0.5,color:"E2E8F0"},
    rowH:0.40,margin:[3,5,3,5],
  });

  // Trend analysis
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:4.6,w:W-2*MARGIN,h:2.0,fill:{color:L_GREY},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:4.6,w:0.06,h:2.0,fill:{color:BLUE}});
  s.addText("Trend Analysis",{x:MARGIN+0.25,y:4.7,w:10,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addText([
    {text:"Latest week (6 Apr): Best performance in 6 weeks",options:{bold:true,breakLine:true,fontSize:F.BODY,color:GREEN}},
    {text:"8 conversions (\u00A351 CPA) - highest conversion volume and second-lowest CPA in the period",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"CPA trend: ",options:{bold:true,color:NAVY}},
    {text:"\u00A354 > \u00A348 > \u00A396 > \u00A365 > \u00A366 > \u00A351. The spike in weeks 3-5 coincided with Easter bank holidays. Post-Easter, CPA dropped to \u00A351 with the highest conversion volume (8).",options:{breakLine:true,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Impression share increased 126%: ",options:{bold:true,color:NAVY}},
    {text:"From 1,092 (week 5) to 2,464 (week 6) - the algorithm is finding more relevant searches post-optimisation.",options:{breakLine:true,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Note: ",options:{bold:true,color:NAVY}},
    {text:"CPA is still above the \u00A330 target. The landing page (currently being built) is the main lever for reducing this further through Quality Score improvement.",options:{color:BLACK}},
  ],{x:MARGIN+0.25,y:5.05,w:W-2*MARGIN-0.5,h:1.4,fontFace:"Calibri",margin:0,valign:"top"});

  addFooter(s,2);
}

// ═══════════════════════════════════════════
// SLIDE 3: AD PERFORMANCE
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:WHITE};
  addSlideTitle(s,"Ad Performance","2 ads now running - RSA 2 and call-only paused this week");

  const adH = [[
    {text:"Ad",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY}},
    {text:"Status",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Strength",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Cost",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Impr",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Clicks",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"CPC",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Conv",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"CPA",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Conv Rate",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Calls",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
  ]];

  const adRows = [
    ["RSA 1 (Keyword Insertion)","Enabled","Excellent","\u00A31,315","5,768","497","\u00A32.65","24","\u00A354.41","4.86%","7"],
    ["Our RSA (Objection Experts)","Enabled","Good","\u00A360","425","16","\u00A33.72","3","\u00A319.83","18.75%","1"],
    ["RSA 2 (Objection Letter)","Paused","Good","\u00A3281","1,821","117","\u00A32.41","2","\u00A3140.70","1.71%","1"],
    ["RSA 3 (Objection Help)","Paused","Good","\u00A3159","845","61","\u00A32.61","2","\u00A3106.10","2.46%","0"],
    ["Call-only (Expert Help)","Paused","--","\u00A388","1,248","19","\u00A34.65","2","\u00A337.89","12.28%","2"],
  ];

  const adR = adRows.map((row,i) => {
    const bg = i%2===0 ? L_GREY : WHITE;
    const isOurs = i === 1;
    const isPaused = row[1] === "Paused";
    return row.map((cell,j) => ({
      text:cell,
      options:{
        fill:{color:isOurs?"E6F4EA":(isPaused?"FCE8E6":bg)},
        fontSize:F.BODY,color:j===1?(isPaused?RED:GREEN):(j===8?(isOurs?GREEN:BLACK):BLACK),
        align:j>0?"center":"left",bold:j===8||j===0||j===1
      }
    }));
  });

  s.addTable([...adH,...adR],{
    x:MARGIN,y:1.3,w:W-2*MARGIN,h:2.8,
    colW:[2.8,0.9,1.0,0.9,0.8,0.8,0.8,0.7,1.0,1.0,0.7],
    border:{type:"solid",pt:0.5,color:"E2E8F0"},
    rowH:0.42,margin:[3,5,3,5],
  });

  // Key findings
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:4.4,w:5.8,h:2.1,fill:{color:"E6F4EA"},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:4.4,w:0.06,h:2.1,fill:{color:GREEN}});
  s.addText("Our RSA - Best Performer",{x:MARGIN+0.25,y:4.5,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:GREEN,margin:0});
  s.addText([
    {text:"\u00A319.83 CPA - lowest of any ad in the account",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"18.75% conversion rate - nearly 4x better than RSA 1",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"3 of Owen's 4 conversions led to sales",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Getting less volume (425 impr vs 5,768) - needs time to build",options:{bullet:true,fontSize:F.BODY,color:BLACK}},
  ],{x:MARGIN+0.25,y:4.85,w:5.2,h:1.5,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:3});

  s.addShape(pres.shapes.RECTANGLE,{x:6.8,y:4.4,w:5.9,h:2.1,fill:{color:"FCE8E6"},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:6.8,y:4.4,w:0.06,h:2.1,fill:{color:RED}});
  s.addText("Paused This Week",{x:7.1,y:4.5,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:RED,margin:0});
  s.addText([
    {text:"RSA 2 (Objection Letter): \u00A3140.70 CPA, 1.71% CR",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"117 clicks, 2 conversions - worst efficiency of any ad",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Call-only ad: Owen confirmed leads are poor quality",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"High CPC (\u00A34.65), low CTR (1.52%), poor lead quality",options:{bullet:true,fontSize:F.BODY,color:BLACK}},
  ],{x:7.1,y:4.85,w:5.4,h:1.5,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:3});

  addFooter(s,3);
}

// ═══════════════════════════════════════════
// SLIDE 4: WHAT WE DID + LANDING PAGE
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:WHITE};
  addSlideTitle(s,"Work Completed","Optimisation, exclusions, and landing page updates");

  const changes = [
    {num:"1",text:"Resolved Owen's solicitor/legal keyword concerns - added \"solicitor\", \"solicitors\", \"legal\", \"law\" as phrase-match negatives. Verified auto-created assets are off.",color:RED},
    {num:"2",text:"Cleaned up 472 account-level + 240 campaign-level negatives from previous agency. Migrated 408 useful ones to structured lists.",color:RED},
    {num:"3",text:"53 more search terms excluded as exact match - appeals, informational queries, DIY intent, wrong-service searches.",color:BLUE},
    {num:"4",text:"Paused RSA 2 (Planning Objection Letter) - \u00A3140.70 CPA. Paused all call-only ads - Owen confirmed leads are poor.",color:AMBER},
    {num:"5",text:"Landing page v3 built with all 12 of Owen's feedback items: 21-day urgency, simplified 4-field form, WhatsApp button, floating CTA, 3 new FAQs, and more.",color:GREEN},
  ];

  changes.forEach((c,i) => {
    const y = 1.15 + i * 1.05;
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y,w:W-2*MARGIN,h:0.9,fill:{color:WHITE},shadow:makeCardShadow(),line:{color:"E2E8F0",width:0.5}});
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y,w:0.05,h:0.9,fill:{color:c.color}});
    s.addText(c.num,{x:MARGIN+0.15,y:y+0.05,w:0.35,h:0.8,fontSize:F.STAT,fontFace:"Calibri",bold:true,color:c.color,margin:0,valign:"top"});
    s.addText(c.text,{x:MARGIN+0.5,y:y+0.05,w:W-2*MARGIN-0.7,h:0.8,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0,valign:"middle"});
  });

  addFooter(s,4);
}

// ═══════════════════════════════════════════
// SLIDE 5: NEXT STEPS
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:L_GREY};
  addStripeBar(s,0,0.06);
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:0.06,w:0.12,h:7.44,fill:{color:BLUE}});

  s.addText("Next Steps",{x:MARGIN,y:0.3,w:7,h:0.5,fontSize:F.TITLE,fontFace:"Calibri",bold:true,color:NAVY,margin:0});

  const tasks = [
    {title:"Owen: Set Up Vercel + GitHub Accounts",desc:"Required to push the landing page live. Once set up, share the login details so I can connect the repository and deploy.",time:"Owen",color:RED},
    {title:"Landing Page Live",desc:"Connect Owen's WordPress form for auto-response. Add DNS record for subdomain (e.g. lp.objectionexperts.com). Push live and update ad URLs.",time:"Next week",color:GREEN},
    {title:"Weekly Search Term Review",desc:"Continue refining exclusions. Monitor for any new patterns slipping through.",time:"Every Monday",color:BLUE},
    {title:"Monitor Ad Performance",desc:"Track our RSA vs RSA 1. If our RSA maintains its \u00A320 CPA as volume increases, consider pausing RSA 1 to test.",time:"Ongoing",color:AMBER},
  ];

  tasks.forEach((t,i) => {
    const y = 1.1 + i * 1.25;
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y,w:W-2*MARGIN,h:1.05,fill:{color:WHITE},shadow:makeCardShadow()});
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y,w:0.06,h:1.05,fill:{color:t.color}});
    s.addText(t.title,{x:MARGIN+0.25,y:y+0.1,w:8,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
    s.addText(t.desc,{x:MARGIN+0.25,y:y+0.45,w:W-2*MARGIN-2.5,h:0.45,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0,valign:"top"});
    s.addText(t.time,{x:W-MARGIN-1.8,y:y+0.1,w:1.6,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:t.color,bold:true,align:"right",margin:0});
  });

  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:6.3,w:W-2*MARGIN,h:0.45,fill:{color:NAVY}});
  s.addText("Key priority: Get the landing page live to improve Quality Scores and reduce CPA toward \u00A325 target.",{
    x:MARGIN+0.3,y:6.3,w:W-2*MARGIN-0.6,h:0.45,fontSize:F.BODY,fontFace:"Calibri",color:GREEN,bold:true,align:"center",valign:"middle",margin:0
  });

  addFooter(s,5);
}

pres.writeFile({fileName:OUTPUT}).then(() => {
  console.log(`Report saved to: ${OUTPUT}`);
}).catch(err => console.error("Error:",err));
