const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const r2data = JSON.parse(fs.readFileSync(path.join(__dirname, "analysis_report2.json"), "utf8"));
const CHART_DIR = path.join(__dirname, "charts");
const OUTPUT = path.join(__dirname, "reports", "03_restructure_report_v2.pptx");

const NAVY = "1A237E", BLUE = "4285F4", RED = "EA4335", AMBER = "FBBC05", GREEN = "34A853";
const L_GREY = "F5F6FA", BLACK = "1A1A1A", WHITE = "FFFFFF";
const LOGO_PATH = path.join(CHART_DIR, "act_logo.png");

const F = { HERO: 44, TITLE: 28, STAT: 22, SECTION: 14, BODY: 11, FOOTER: 11 };
const TIMEFRAME_SHORT = "Jan 2025 \u2014 Mar 2026";
const makeShadow = () => ({ type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.12 });
const makeCardShadow = () => ({ type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.10 });

let pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Christopher Hoole";
pres.title = "Restructure & Growth Plan \u2014 Objection Experts";
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

function addStatCard(s,x,y,w,h,val,lab,col) {
  s.addShape(pres.shapes.RECTANGLE,{x,y,w,h,fill:{color:WHITE},shadow:makeCardShadow(),line:{color:"E2E8F0",width:0.5}});
  s.addShape(pres.shapes.RECTANGLE,{x,y,w:0.06,h,fill:{color:col}});
  s.addText(val,{x:x+0.2,y:y+0.1,w:w-0.3,h:0.5,fontSize:F.STAT,fontFace:"Calibri",bold:true,color:col,margin:0});
  s.addText(lab,{x:x+0.2,y:y+0.6,w:w-0.3,h:0.35,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});
}

function addSlideTitle(s, title, subtitle) {
  addStripeBar(s,0,0.06);
  s.addText(title,{x:MARGIN,y:0.3,w:7,h:0.5,fontSize:F.TITLE,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addShape(pres.shapes.RECTANGLE,{x:W-MARGIN-3.6,y:0.3,w:3.6,h:0.45,fill:{color:WHITE},line:{color:BLUE,width:1}});
  s.addText("Proposed Plan",{x:W-MARGIN-3.5,y:0.32,w:3.4,h:0.4,fontSize:F.BODY,fontFace:"Calibri",color:BLUE,align:"center",valign:"middle",bold:true,margin:0});
  if(subtitle) s.addText(subtitle,{x:MARGIN,y:0.85,w:9,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:BLUE,margin:0});
}

const pre = r2data.before_after.pre;

// ═══════════════════════════════════════════
// SLIDE 1: TITLE
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:L_GREY};
  addStripeBar(s,0,0.07);
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:0.07,w:0.12,h:7.43,fill:{color:BLUE}});
  s.addImage({path:LOGO_PATH,x:0.6,y:0.5,w:0.65,h:0.65});

  s.addText("RESTRUCTURE\n& GROWTH PLAN",{x:0.6,y:1.4,w:5.5,h:1.8,fontSize:F.HERO,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addShape(pres.shapes.RECTANGLE,{x:0.6,y:3.3,w:2.5,h:0.05,fill:{color:BLUE}});
  s.addText("Objection Experts",{x:0.6,y:3.55,w:5.5,h:0.5,fontSize:F.STAT,fontFace:"Calibri",color:BLUE,margin:0});
  s.addText([
    {text:"Prepared by Christopher Hoole",options:{breakLine:true,fontSize:F.BODY,color:BLACK,bold:true}},
    {text:"Google Ads Specialist  |  March 2026",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"christopherhoole.com",options:{fontSize:F.BODY,color:BLUE}},
  ],{x:0.6,y:4.3,w:5.5,h:1.0,fontFace:"Calibri",margin:0});
  s.addShape(pres.shapes.RECTANGLE,{x:0.6,y:5.5,w:4.5,h:0.5,fill:{color:WHITE},line:{color:BLUE,width:1}});
  s.addText("Based on data: Jan 2025 \u2014 Mar 2026 (15 months)",{x:0.7,y:5.52,w:4.3,h:0.45,fontSize:F.BODY,fontFace:"Calibri",color:BLUE,bold:true,valign:"middle",margin:0});

  // Right panel — opportunity stat
  const rX=6.8, rW=5.9;
  s.addShape(pres.shapes.RECTANGLE,{x:rX,y:0.5,w:rW,h:2.5,fill:{color:WHITE},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:rX,y:0.5,w:0.08,h:2.5,fill:{color:GREEN}});
  s.addText("Target CPA",{x:rX+0.3,y:0.7,w:rW-0.5,h:0.35,fontSize:F.SECTION,fontFace:"Calibri",color:NAVY,margin:0});
  s.addText("\u00A320-25",{x:rX+0.3,y:1.1,w:rW-0.5,h:0.8,fontSize:F.HERO,fontFace:"Calibri",bold:true,color:GREEN,margin:0});
  s.addText(`Down from current \u00A3${r2data.before_after.post.cpa}`,{x:rX+0.3,y:1.9,w:rW-0.5,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});

  const smW=(rW-0.4)/3, smY=3.2, smH=1.15;
  // More leads
  s.addShape(pres.shapes.RECTANGLE,{x:rX,y:smY,w:smW,h:smH,fill:{color:WHITE},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:rX,y:smY,w:0.06,h:smH,fill:{color:BLUE}});
  s.addText("+30-50%",{x:rX+0.15,y:smY+0.12,w:smW-0.25,h:0.45,fontSize:F.STAT,fontFace:"Calibri",bold:true,color:BLUE,margin:0});
  s.addText("More Leads",{x:rX+0.15,y:smY+0.6,w:smW-0.25,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});

  // Timeline
  const sm2X=rX+smW+0.2;
  s.addShape(pres.shapes.RECTANGLE,{x:sm2X,y:smY,w:smW,h:smH,fill:{color:WHITE},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:sm2X,y:smY,w:0.06,h:smH,fill:{color:AMBER}});
  s.addText("8-12 wks",{x:sm2X+0.15,y:smY+0.12,w:smW-0.25,h:0.45,fontSize:F.STAT,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addText("To Full Impact",{x:sm2X+0.15,y:smY+0.6,w:smW-0.25,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});

  // Savings
  const sm3X=rX+2*(smW+0.2);
  s.addShape(pres.shapes.RECTANGLE,{x:sm3X,y:smY,w:smW,h:smH,fill:{color:WHITE},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:sm3X,y:smY,w:0.06,h:smH,fill:{color:GREEN}});
  s.addText("\u00A34.6-7.9k",{x:sm3X+0.15,y:smY+0.12,w:smW-0.25,h:0.45,fontSize:F.STAT,fontFace:"Calibri",bold:true,color:GREEN,margin:0});
  s.addText("Annual Saving",{x:sm3X+0.15,y:smY+0.6,w:smW-0.25,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});

  addStripeBar(s,7.0,0.04);
}

// ═══════════════════════════════════════════
// SLIDE 2: EXECUTIVE SUMMARY
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background={color:WHITE};
  addSlideTitle(s,"Executive Summary","The opportunity: what's achievable with proper management");

  addStatCard(s,MARGIN,1.2,2.8,1.05,"\u00A320-25","Target CPA",GREEN);
  addStatCard(s,MARGIN+3.1,1.2,2.8,1.05,"+30-50%","More Leads (same budget)",BLUE);
  addStatCard(s,MARGIN+6.2,1.2,2.8,1.05,"8-12 wks","Time to Full Impact",AMBER);
  addStatCard(s,MARGIN+9.3,1.2,2.8,1.05,"\u00A31,500/mo","Same Monthly Budget",NAVY);

  s.addText("Restructure Plan Summary",{x:MARGIN,y:2.6,w:6,h:0.35,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addText([
    {text:"Week 1: Fix conversion tracking, add negative keywords, set target CPA, pause waste",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Weeks 2-4: New ad copy testing, schedule optimisation, Quality Score improvements",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Months 2-3: Ongoing optimisation, landing page testing, keyword expansion",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:`Based on the pre-October 2025 baseline when CPA was \u00A3${pre.cpa}, a target CPA of \u00A320-25 is achievable with the optimisations identified in Reports 1 and 2.`,options:{fontSize:F.BODY,color:BLACK}},
  ],{x:MARGIN+0.1,y:3.0,w:11.5,h:2.5,fontFace:"Calibri",paraSpaceAfter:6,margin:0,valign:"top"});

  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:5.7,w:W-2*MARGIN,h:0.7,fill:{color:"E8F0FE"},line:{color:BLUE,width:1}});
  s.addText([
    {text:"Conservative projection: ",options:{bold:true,color:NAVY}},
    {text:`Reducing CPA from \u00A3${r2data.before_after.post.cpa} to \u00A320-25 within 8-12 weeks, while maintaining or increasing lead volume on the same \u00A31,500/month budget.`,options:{color:BLACK}},
  ],{x:MARGIN+0.25,y:5.75,w:W-2*MARGIN-0.5,h:0.6,fontSize:F.BODY,fontFace:"Calibri",valign:"middle",margin:0});

  addFooter(s,2);
}

// ═══════════════════════════════════════════
// SLIDE 3: PROPOSED CAMPAIGN STRUCTURE
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background={color:WHITE};
  addSlideTitle(s,"Proposed Campaign Structure","Simplified structure designed for a \u00A31,500/month account");

  // Current vs Proposed - two columns
  // Current
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.3,w:5.8,h:5.0,fill:{color:"FCE8E6"},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.3,w:0.06,h:5.0,fill:{color:RED}});
  s.addText("Current Structure",{x:MARGIN+0.25,y:1.4,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:RED,margin:0});
  s.addText([
    {text:"GLO Campaign (Search)",options:{bold:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"  Planning Objections (95% of spend)",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"  Planning Objection Letters (2%)",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"  Planning Objection Consultants (3%)",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"  Neighbourhood Objections (0 conv.)",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:RED}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"GLO - Core - PMax (small spend)",options:{bold:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Lead Form Submissions (dormant)",options:{bold:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Planning Objection Letters campaign (dormant)",options:{bold:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Issues:",options:{bold:true,breakLine:true,fontSize:F.BODY,color:RED}},
    {text:"Volume fragmented across 4 ad groups",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"3 ad groups have insufficient data to optimise",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Dormant campaigns add clutter",options:{bullet:true,fontSize:F.BODY,color:BLACK}},
  ],{x:MARGIN+0.25,y:1.8,w:5.2,h:4.3,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:2});

  // Proposed
  s.addShape(pres.shapes.RECTANGLE,{x:6.8,y:1.3,w:5.9,h:5.0,fill:{color:"E6F4EA"},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:6.8,y:1.3,w:0.06,h:5.0,fill:{color:GREEN}});
  s.addText("Proposed Structure",{x:7.1,y:1.4,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:GREEN,margin:0});
  s.addText([
    {text:"Objection Experts \u2014 Search",options:{bold:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"  Planning Objections (core terms, broad/phrase match)",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"  Planning Permission Challenge (related intent)",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Optional: Brand Campaign",options:{bold:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"  Only if competitor bidding detected",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Rationale:",options:{bold:true,breakLine:true,fontSize:F.BODY,color:GREEN}},
    {text:"Consolidate volume into fewer, well-themed ad groups. At \u00A31,500/month, simpler is better \u2014 the algorithm needs data density to optimise effectively.",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Pause Neighbourhood Objections, Letters, and Consultants ad groups. Merge their best keywords into the main group.",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Remove dormant campaigns to keep the account clean.",options:{fontSize:F.BODY,color:BLACK}},
  ],{x:7.1,y:1.8,w:5.4,h:4.3,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:2});

  addFooter(s,3);
}

// ═══════════════════════════════════════════
// SLIDE 4: KEYWORD STRATEGY
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background={color:WHITE};
  addSlideTitle(s,"Keyword Strategy","Keep the winners, pause the losers, expand with proven search terms");

  // Top performers table
  const kwHeader = [[
    {text:"Keyword",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY}},
    {text:"Conv.",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"CPA",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"QS",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Action",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
  ]];

  const keywords = [
    ["planning objection","99","\u00A334.49","3","Keep \u2014 improve QS"],
    ["planning objections","94","\u00A337.01","3","Keep \u2014 improve QS"],
    ["challenge planning permission","68","\u00A338.90","3","Keep \u2014 improve QS"],
    ["opposing planning permission","59","\u00A333.74","-","Keep"],
    ["planning objection consultants","48","\u00A324.53","7","Keep \u2014 best CPA + QS"],
    ["object to planning application","45","\u00A317.42","-","Keep \u2014 best CPA"],
    ["objecting to planning permission","42","\u00A329.72","2","Keep \u2014 improve QS"],
    ["planning objection specialist","31","\u00A324.30","-","Keep"],
    ["planning objection letter","21","\u00A334.77","2","Keep \u2014 improve QS"],
    ["neighbour planning permission","0","\u00A377.90","-","Pause \u2014 0 conv."],
  ];

  const kwRows = keywords.map((row,i) => {
    const isWaste = row[1] === "0";
    const bg = isWaste ? "FCE8E6" : (i%2===0 ? L_GREY : WHITE);
    return [
      {text:row[0],options:{fill:{color:bg},fontSize:F.BODY,color:BLACK}},
      {text:row[1],options:{fill:{color:bg},fontSize:F.BODY,align:"center",color:isWaste?RED:BLACK,bold:true}},
      {text:row[2],options:{fill:{color:bg},fontSize:F.BODY,align:"center",color:BLACK}},
      {text:row[3],options:{fill:{color:bg},fontSize:F.BODY,align:"center",color:row[3]==="7"?GREEN:(row[3]==="2"||row[3]==="3"?RED:BLACK)}},
      {text:row[4],options:{fill:{color:bg},fontSize:F.BODY,align:"center",color:isWaste?RED:GREEN,bold:true}},
    ];
  });

  s.addTable([...kwHeader,...kwRows],{
    x:MARGIN,y:1.3,w:W-2*MARGIN,h:4.5,
    colW:[3.5,1,1.2,0.8,5.5],
    border:{type:"solid",pt:0.5,color:"E2E8F0"},
    rowH:0.38,margin:[3,6,3,6],
  });

  // Bottom recommendation
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:5.9,w:W-2*MARGIN,h:0.6,fill:{color:"E8F0FE"},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:5.9,w:0.06,h:0.6,fill:{color:BLUE}});
  s.addText([
    {text:"New keywords to add from search term data: ",options:{bold:true,color:NAVY}},
    {text:'"planning objection solicitor" (CPA \u00A318), "object planning permission" (CPA \u00A36), "planning objection advice" (CPA \u00A316)',options:{color:BLACK}},
  ],{x:MARGIN+0.25,y:5.95,w:W-2*MARGIN-0.5,h:0.5,fontSize:F.BODY,fontFace:"Calibri",valign:"middle",margin:0});

  addFooter(s,4);
}

// ═══════════════════════════════════════════
// SLIDE 5: BID STRATEGY RECOMMENDATION
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background={color:WHITE};
  addSlideTitle(s,"Bid Strategy Recommendation","From uncontrolled spending to a target CPA guardrail");

  // Before card
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.3,w:5.8,h:2.8,fill:{color:"FCE8E6"},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.3,w:0.06,h:2.8,fill:{color:RED}});
  s.addText("Current",{x:MARGIN+0.25,y:1.4,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:RED,margin:0});
  s.addText([
    {text:"Maximise Conversions",options:{bold:true,breakLine:true,fontSize:F.STAT-2,color:RED}},
    {text:"No target CPA set",options:{bold:true,breakLine:true,fontSize:F.BODY,color:RED}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"The algorithm spends whatever it takes to get a conversion. No guardrails = unpredictable costs.",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:`Result: CPA of \u00A3${r2data.before_after.post.cpa} (post-Oct 2025 avg), with monthly peaks reaching \u00A365.`,options:{fontSize:F.BODY,color:BLACK}},
  ],{x:MARGIN+0.25,y:1.8,w:5.2,h:2.2,fontFace:"Calibri",margin:0,valign:"top"});

  // After card
  s.addShape(pres.shapes.RECTANGLE,{x:6.8,y:1.3,w:5.9,h:2.8,fill:{color:"E6F4EA"},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:6.8,y:1.3,w:0.06,h:2.8,fill:{color:GREEN}});
  s.addText("Proposed",{x:7.1,y:1.4,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:GREEN,margin:0});
  s.addText([
    {text:"Maximise Conversions",options:{bold:true,breakLine:true,fontSize:F.STAT-2,color:GREEN}},
    {text:"Target CPA: \u00A325-30",options:{bold:true,breakLine:true,fontSize:F.BODY,color:GREEN}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:`Based on the pre-October 2025 baseline of \u00A3${pre.cpa}. Start conservative at \u00A330, then gradually reduce toward \u00A325 as Quality Score improvements take effect.`,options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Disable auto-apply recommendations immediately.",options:{bold:true,fontSize:F.BODY,color:NAVY}},
  ],{x:7.1,y:1.8,w:5.4,h:2.2,fontFace:"Calibri",margin:0,valign:"top"});

  // Implementation note
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:4.4,w:W-2*MARGIN,h:1.8,fill:{color:L_GREY},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:4.4,w:0.06,h:1.8,fill:{color:BLUE}});
  s.addText("Implementation Approach",{x:MARGIN+0.25,y:4.5,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addText([
    {text:"Week 1: Set target CPA at \u00A330 (conservative start)",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Week 3-4: If CPA is stable at \u00A330, reduce target to \u00A327",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Week 6-8: With QS improvements taking effect, reduce target to \u00A325",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Ongoing: Monitor weekly. Never change target CPA by more than 15-20% at a time \u2014 gradual adjustments let the algorithm adapt.",options:{bullet:true,fontSize:F.BODY,color:BLACK}},
  ],{x:MARGIN+0.25,y:4.9,w:W-2*MARGIN-0.5,h:1.2,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:3});

  addFooter(s,5);
}

// ═══════════════════════════════════════════
// SLIDE 6: CONVERSION TRACKING FIX
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background={color:WHITE};
  addSlideTitle(s,"Conversion Tracking Fix","Clean tracking = better algorithm decisions = lower CPA");

  // Before/after table
  const ctHeader = [[
    {text:"Conversion Action",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY}},
    {text:"Current",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Proposed",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Why",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY}},
  ]];
  const ctRows = [
    ["Form Submission","Primary","Primary","Real lead \u2014 keep as-is"],
    ["Google Forwarding Number","Primary","Primary","Real call lead \u2014 keep as-is"],
    ["Email Click","Primary","Secondary","NOT a lead. Remove from goals. Stops algorithm optimising for email clicks."],
    ["Phone Number Click","Secondary","Secondary","Already correct"],
  ].map((row,i) => {
    const isChange = row[1] !== row[2];
    const bg = isChange ? "FCE8E6" : (i%2===0 ? L_GREY : WHITE);
    return [
      {text:row[0],options:{fill:{color:bg},fontSize:F.BODY,color:BLACK,bold:isChange}},
      {text:row[1],options:{fill:{color:bg},fontSize:F.BODY,align:"center",color:isChange?RED:BLACK}},
      {text:row[2],options:{fill:{color:bg},fontSize:F.BODY,align:"center",color:isChange?GREEN:BLACK,bold:isChange}},
      {text:row[3],options:{fill:{color:bg},fontSize:F.BODY,color:BLACK}},
    ];
  });

  s.addTable([...ctHeader,...ctRows],{
    x:MARGIN,y:1.3,w:W-2*MARGIN,h:2.2,
    colW:[2.8,1.5,1.5,6.3],
    border:{type:"solid",pt:0.5,color:"E2E8F0"},
    rowH:0.42,margin:[4,8,4,8],
  });

  // Impact
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:3.8,w:W-2*MARGIN,h:2.3,fill:{color:L_GREY},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:3.8,w:0.06,h:2.3,fill:{color:BLUE}});
  s.addText("Impact of This Change",{x:MARGIN+0.25,y:3.9,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addText([
    {text:"The bidding algorithm currently counts 552 conversions \u2014 but 62 of these are micro-conversions (Email Clicks + Phone Number Clicks that don't represent actual leads).",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Real conversions: 490 (Form Submissions + Google Forwarding calls)",options:{bold:true,breakLine:true,fontSize:F.BODY,color:NAVY}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"By marking Email Click as Secondary, the algorithm will only optimise toward genuine form submissions and phone calls. This single change will immediately improve lead quality and CPA accuracy.",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"This is a 5-minute fix with outsized impact.",options:{bold:true,fontSize:F.BODY,color:GREEN}},
  ],{x:MARGIN+0.25,y:4.3,w:W-2*MARGIN-0.5,h:1.7,fontFace:"Calibri",margin:0,valign:"top"});

  addFooter(s,6);
}

// ═══════════════════════════════════════════
// SLIDE 7: NEGATIVE KEYWORD FRAMEWORK
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background={color:WHITE};
  addSlideTitle(s,"Negative Keyword Framework","From reactive exact-match to proactive phrase-match protection");

  // Three-tier framework
  const tiers = [
    {title:"Account-Level Negatives",desc:"Universal blockers applied across all campaigns",examples:"jobs, careers, salary, courses, university, template, example, sample, DIY, free, how to write, complaint",color:RED},
    {title:"Campaign-Level Negatives",desc:"Service-specific exclusions for the Search campaign",examples:"planning permission (applying for), planning consultant, architect, surveyor, solicitor, retrospective, neighbour dispute, fence, boundary, tree",color:AMBER},
    {title:"Ongoing Process",desc:"Weekly search term review to catch new irrelevant queries",examples:"Review search terms every Monday. Add phrase-match negatives for any irrelevant patterns. Document in a shared negative keyword list.",color:GREEN},
  ];

  tiers.forEach((t,i) => {
    const y = 1.3 + i * 1.7;
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y,w:W-2*MARGIN,h:1.5,fill:{color:WHITE},shadow:makeCardShadow(),line:{color:"E2E8F0",width:0.5}});
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y,w:0.06,h:1.5,fill:{color:t.color}});
    s.addText(t.title,{x:MARGIN+0.25,y:y+0.08,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
    s.addText(t.desc,{x:MARGIN+0.25,y:y+0.4,w:5,h:0.25,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});
    s.addText(t.examples,{x:MARGIN+0.25,y:y+0.7,w:W-2*MARGIN-0.5,h:0.65,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});
  });

  // Key shift callout
  s.addText("Key shift: Move from exact match negatives (which miss variations) to phrase match negatives (which block the root term and all variations).",{
    x:MARGIN,y:6.35,w:W-2*MARGIN,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:NAVY,bold:true,italic:true,margin:0
  });

  addFooter(s,7);
}

// ═══════════════════════════════════════════
// SLIDE 8: AD COPY TESTING PLAN
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background={color:WHITE};
  addSlideTitle(s,"Ad Copy Testing Plan","Three messaging angles to test against the current winner");

  const angles = [
    {title:"RSA 1: Trust & Credibility",headlines:["Expert Planning Objection Help","600+ Objections Prepared Since 2023","RTPI Qualified Town Planner","Proven 60% Success Rate"],desc:"Emphasises track record and qualifications. Targets risk-averse prospects who want proof.",color:BLUE},
    {title:"RSA 2: Speed & Urgency",headlines:["Planning Objection in 5 Working Days","Same-Day Consultations Available","Don't Miss Your Objection Deadline","Fast, Professional Objection Letters"],desc:"Appeals to time-sensitive prospects. Planning objections often have tight deadlines.",color:AMBER},
    {title:"RSA 3: Value & Accessibility",headlines:["From \u00A3350+VAT Per Objection","Free Initial Consultation","Fixed Fee \u2014 No Hidden Costs","Affordable Planning Objection Help"],desc:"Leads with price transparency. Reduces friction for cost-conscious prospects.",color:GREEN},
  ];

  angles.forEach((a,i) => {
    const x = MARGIN + i * 4.1;
    s.addShape(pres.shapes.RECTANGLE,{x,y:1.3,w:3.85,h:4.8,fill:{color:WHITE},shadow:makeCardShadow(),line:{color:"E2E8F0",width:0.5}});
    s.addShape(pres.shapes.RECTANGLE,{x,y:1.3,w:0.06,h:4.8,fill:{color:a.color}});

    s.addText(a.title,{x:x+0.2,y:1.4,w:3.4,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
    s.addText("Sample headlines:",{x:x+0.2,y:1.8,w:3.4,h:0.25,fontSize:F.BODY,fontFace:"Calibri",bold:true,color:BLACK,margin:0});

    const hlText = a.headlines.map((h,j) => ({
      text:h, options:{bullet:true,breakLine:j<a.headlines.length-1,fontSize:F.BODY,color:BLACK}
    }));
    s.addText(hlText,{x:x+0.2,y:2.1,w:3.4,h:2.0,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:3});

    s.addText("Angle:",{x:x+0.2,y:4.3,w:3.4,h:0.25,fontSize:F.BODY,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
    s.addText(a.desc,{x:x+0.2,y:4.6,w:3.4,h:1.3,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});
  });

  s.addText("Testing plan: Run all 3 RSAs for 4-6 weeks. Keep the winner, replace the worst performer with a new challenger. Continuous improvement.",{
    x:MARGIN,y:6.35,w:W-2*MARGIN,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:NAVY,bold:true,italic:true,margin:0
  });

  addFooter(s,8);
}

// ═══════════════════════════════════════════
// SLIDE 9: SCHEDULE & DEVICE OPTIMISATION
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background={color:WHITE};
  addSlideTitle(s,"Schedule & Device Optimisation","Data-driven bid adjustments based on 15 months of performance");

  // Schedule recommendations
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.3,w:6,h:3.5,fill:{color:L_GREY},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.3,w:0.06,h:3.5,fill:{color:BLUE}});
  s.addText("Ad Schedule Adjustments",{x:MARGIN+0.25,y:1.4,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});

  const schedItems = [
    {text:"Increase bids +15-20%:",options:{bold:true,breakLine:true,fontSize:F.BODY,color:GREEN}},
    {text:"Mon 2-5pm (CPA \u00A324), Wed 2-5pm (CPA \u00A324), Thu 5pm-12am (CPA \u00A324), Sat 5-12pm (CPA \u00A320)",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Reduce bids -30-50%:",options:{bold:true,breakLine:true,fontSize:F.BODY,color:RED}},
    {text:"All days 12-6am (low volume, zero/low conversions), Sun 12-2pm (CPA \u00A3136), Fri 5-12pm (CPA \u00A383)",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Keep as-is:",options:{bold:true,breakLine:true,fontSize:F.BODY,color:NAVY}},
    {text:"All other time slots \u2014 monitor for 4 weeks, then adjust based on results",options:{fontSize:F.BODY,color:BLACK}},
  ];
  s.addText(schedItems,{x:MARGIN+0.25,y:1.8,w:5.4,h:2.8,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:2});

  // Device recommendations
  s.addShape(pres.shapes.RECTANGLE,{x:6.7,y:1.3,w:6,h:3.5,fill:{color:L_GREY},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:6.7,y:1.3,w:0.06,h:3.5,fill:{color:AMBER}});
  s.addText("Device Bid Adjustments",{x:6.95,y:1.4,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addText([
    {text:"Mobile (57% of spend):",options:{bold:true,breakLine:true,fontSize:F.BODY,color:NAVY}},
    {text:"Current: +10%. Proposed: Keep at +10%. Best CPA (\u00A332.24) and highest volume.",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Desktop (41% of spend):",options:{bold:true,breakLine:true,fontSize:F.BODY,color:NAVY}},
    {text:"Current: +10%. Proposed: Reduce to +0%. CPA slightly higher than mobile (\u00A334.55).",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Tablet (3% of spend):",options:{bold:true,breakLine:true,fontSize:F.BODY,color:NAVY}},
    {text:"Current: -20%. Proposed: Reduce to -35%. Highest CPA (\u00A334.99) and lowest conv rate (5.0%).",options:{fontSize:F.BODY,color:BLACK}},
  ],{x:6.95,y:1.8,w:5.4,h:2.8,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:2});

  // Day of week
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:5.1,w:W-2*MARGIN,h:1.3,fill:{color:"E8F0FE"},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:5.1,w:0.06,h:1.3,fill:{color:BLUE}});
  s.addText("Day-of-Week Adjustments",{x:MARGIN+0.25,y:5.2,w:5,h:0.25,fontSize:F.BODY,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addText([
    {text:"Monday (best CPA \u00A327): +10%  |  Sunday (worst CPA \u00A347): -25%  |  Saturday: -10%",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"All adjustments are starting points based on historical data. Review after 4 weeks and refine.",options:{fontSize:F.BODY,color:NAVY,italic:true}},
  ],{x:MARGIN+0.25,y:5.5,w:W-2*MARGIN-0.5,h:0.7,fontFace:"Calibri",margin:0,valign:"top"});

  addFooter(s,9);
}

// ═══════════════════════════════════════════
// SLIDE 10: QUALITY SCORE IMPROVEMENT
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background={color:WHITE};
  addSlideTitle(s,"Quality Score Improvement Plan","Roadmap from QS 2-3 to QS 6-7+");

  const steps = [
    {num:"1",title:"Tighter Ad Group Themes",desc:"Consolidate keywords into well-themed groups. When keywords closely match ad copy, Google rates your ad relevance higher.",impact:"Expected CTR + Ad Relevance",color:BLUE},
    {num:"2",title:"Better Ad Copy Alignment",desc:"Write headlines that closely mirror the keywords in each ad group. Include the core search term in Headline 1 and Description 1.",impact:"Expected CTR + Ad Relevance",color:GREEN},
    {num:"3",title:"Landing Page Optimisation",desc:"Consider a dedicated landing page for planning objections. Faster load time, clearer match to ad messaging, focused CTA.",impact:"Landing Page Experience",color:AMBER},
  ];

  steps.forEach((st,i) => {
    const y = 1.3 + i * 1.55;
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y,w:W-2*MARGIN,h:1.35,fill:{color:WHITE},shadow:makeCardShadow(),line:{color:"E2E8F0",width:0.5}});
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y,w:0.06,h:1.35,fill:{color:st.color}});

    s.addShape(pres.shapes.OVAL,{x:MARGIN+0.2,y:y+0.35,w:0.5,h:0.5,fill:{color:st.color}});
    s.addText(st.num,{x:MARGIN+0.2,y:y+0.35,w:0.5,h:0.5,fontSize:F.SECTION+2,fontFace:"Calibri",bold:true,color:WHITE,align:"center",valign:"middle",margin:0});

    s.addText(st.title,{x:MARGIN+0.9,y:y+0.1,w:6,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
    s.addText(st.desc,{x:MARGIN+0.9,y:y+0.45,w:7.5,h:0.7,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});

    // Impact badge
    s.addShape(pres.shapes.RECTANGLE,{x:W-MARGIN-3,y:y+0.15,w:2.8,h:0.3,fill:{color:"E6F4EA"}});
    s.addText(`Improves: ${st.impact}`,{x:W-MARGIN-3,y:y+0.15,w:2.8,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:GREEN,align:"center",valign:"middle",margin:0});
  });

  // Bottom impact statement
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:5.95,w:W-2*MARGIN,h:0.6,fill:{color:NAVY}});
  s.addText("Every 1-point QS improvement reduces CPC. Moving from QS 3 to QS 7 could cut click costs by 30-50%.",{
    x:MARGIN+0.3,y:5.95,w:W-2*MARGIN-0.6,h:0.6,fontSize:F.BODY,fontFace:"Calibri",color:GREEN,bold:true,align:"center",valign:"middle",margin:0
  });

  addFooter(s,10);
}

// ═══════════════════════════════════════════
// SLIDE 11: PROJECTED RESULTS
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background={color:WHITE};
  addSlideTitle(s,"Projected Results","Conservative projections based on identified optimisation opportunities");

  // Before/after comparison
  const metrics = [
    ["Monthly Spend","\u00A31,500","\u00A31,500","Same budget"],
    ["Cost Per Conversion",`\u00A3${r2data.before_after.post.cpa}`,"\u00A320-25","35-48% reduction"],
    ["Monthly Conversions","~13","18-25","+38-92% more leads"],
    ["Conversion Rate",`${r2data.before_after.post.conv_rate}%`,"9-12%","+40-87% improvement"],
    ["Quality Score","2-3","6-7+","Within 8-12 weeks"],
    ["Avg CPC",`\u00A3${r2data.before_after.post.avg_cpc}`,"\u00A31.50-2.00","QS improvement effect"],
  ];

  const tblH = [[
    {text:"Metric",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY}},
    {text:"Current",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Projected",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Change",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
  ]];
  const tblR = metrics.map((row,i) => {
    const bg = i%2===0 ? L_GREY : WHITE;
    return [
      {text:row[0],options:{fill:{color:bg},fontSize:F.BODY,color:BLACK,bold:true}},
      {text:row[1],options:{fill:{color:bg},fontSize:F.BODY,align:"center",color:RED}},
      {text:row[2],options:{fill:{color:bg},fontSize:F.BODY,align:"center",color:GREEN,bold:true}},
      {text:row[3],options:{fill:{color:bg},fontSize:F.BODY,align:"center",color:GREEN}},
    ];
  });

  s.addTable([...tblH,...tblR],{
    x:MARGIN,y:1.3,w:W-2*MARGIN,h:3.2,
    colW:[3,2.5,2.5,4],
    border:{type:"solid",pt:0.5,color:"E2E8F0"},
    rowH:0.42,margin:[4,8,4,8],
  });

  // Caveat + methodology
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:4.8,w:W-2*MARGIN,h:1.6,fill:{color:L_GREY},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:4.8,w:0.06,h:1.6,fill:{color:BLUE}});
  s.addText("Methodology & Caveats",{x:MARGIN+0.25,y:4.9,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addText([
    {text:"These are conservative projections based on the pre-October 2025 performance baseline, when CPA was consistently \u00A322-30 without the optimisations proposed here.",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Actual results will depend on market conditions, seasonality, and the speed of Quality Score improvements. I've deliberately underpromised so we can overdeliver.",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Monthly conversions calculated as: \u00A31,500 budget \u00F7 target CPA.",options:{fontSize:F.BODY,color:NAVY,italic:true}},
  ],{x:MARGIN+0.25,y:5.25,w:W-2*MARGIN-0.5,h:1.0,fontFace:"Calibri",margin:0,valign:"top"});

  addFooter(s,11);
}

// ═══════════════════════════════════════════
// SLIDE 12: IMPLEMENTATION TIMELINE
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background={color:WHITE};
  addSlideTitle(s,"Implementation Timeline","Quick wins start immediately \u2014 full impact within 8-12 weeks");

  const phases = [
    {title:"WEEK 1",subtitle:"Quick Wins",items:["Fix conversion tracking (Email Click \u2192 Secondary)","Set target CPA at \u00A330","Add phrase-match negative keywords","Pause Neighbourhood Objections ad group","Disable auto-apply recommendations"],color:RED},
    {title:"WEEKS 2-4",subtitle:"Optimisation",items:["Launch 3 RSA ad copy variants for A/B testing","Implement ad schedule bid adjustments","Adjust device bids (tablet to -35%)","Add day-of-week bid adjustments (Sun -25%)","Begin weekly search term review process"],color:AMBER},
    {title:"MONTHS 2-3",subtitle:"Growth",items:["Analyse ad copy test results, keep winner","Reduce target CPA toward \u00A325 as QS improves","Expand keyword coverage with proven search terms","Consider dedicated landing page test","Review and refine all bid adjustments"],color:GREEN},
  ];

  phases.forEach((p,i) => {
    const x = MARGIN + i * 4.1;
    s.addShape(pres.shapes.RECTANGLE,{x,y:1.3,w:3.85,h:5.0,fill:{color:WHITE},shadow:makeCardShadow(),line:{color:"E2E8F0",width:0.5}});
    s.addShape(pres.shapes.RECTANGLE,{x,y:1.3,w:3.85,h:0.7,fill:{color:p.color}});

    s.addText(p.title,{x,y:1.3,w:3.85,h:0.35,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:WHITE,align:"center",valign:"middle",margin:0});
    s.addText(p.subtitle,{x,y:1.65,w:3.85,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:WHITE,align:"center",valign:"middle",margin:0});

    const items = p.items.map((item,j) => ({
      text:item, options:{bullet:true,breakLine:j<p.items.length-1,fontSize:F.BODY,color:BLACK}
    }));
    s.addText(items,{x:x+0.15,y:2.15,w:3.55,h:3.8,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:6});
  });

  s.addText("Improvements start in Week 1, not in 3 months. The quick wins alone can reduce waste by \u00A3380-655/month.",{
    x:MARGIN,y:6.4,w:W-2*MARGIN,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:NAVY,bold:true,italic:true,margin:0
  });

  addFooter(s,12);
}

// ═══════════════════════════════════════════
// SLIDE 13: WHY CHRISTOPHER HOOLE
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background={color:WHITE};
  addSlideTitle(s,"Why Christopher Hoole",null);

  // Three value cards
  const values = [
    {title:"Hands-On Specialist",desc:"Not a junior in a big agency. I personally manage every account \u2014 no handoffs, no account managers who don't understand the data. You get direct access to the person making the decisions.",color:BLUE},
    {title:"Data-Driven Approach",desc:"Every recommendation in these reports is backed by your actual data. No guesswork, no generic playbooks. The analysis you've seen here is how I work on an ongoing basis \u2014 finding waste, fixing issues, improving performance.",color:GREEN},
    {title:"Transparent Reporting",desc:"Monthly reports showing exactly what changed, what improved, and what we're working on next. No vanity metrics, no hiding behind jargon. You'll always know where your \u00A31,500 is going and what it's producing.",color:AMBER},
  ];

  values.forEach((v,i) => {
    const y = 1.1 + i * 1.7;
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y,w:W-2*MARGIN,h:1.5,fill:{color:WHITE},shadow:makeCardShadow(),line:{color:"E2E8F0",width:0.5}});
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y,w:0.06,h:1.5,fill:{color:v.color}});
    s.addText(v.title,{x:MARGIN+0.3,y:y+0.12,w:W-2*MARGIN-0.6,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
    s.addText(v.desc,{x:MARGIN+0.3,y:y+0.5,w:W-2*MARGIN-0.6,h:0.85,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});
  });

  // Credentials footer
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:6.15,w:W-2*MARGIN,h:0.5,fill:{color:NAVY}});
  s.addText("christopherhoole.com  |  Google Ads Specialist  |  These reports are the proof.",{
    x:MARGIN+0.3,y:6.15,w:W-2*MARGIN-0.6,h:0.5,fontSize:F.BODY,fontFace:"Calibri",color:WHITE,align:"center",valign:"middle",margin:0
  });

  addFooter(s,13);
}

// ═══════════════════════════════════════════
// SLIDE 14: NEXT STEPS
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background={color:L_GREY};
  addStripeBar(s,0,0.06);
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:0.06,w:0.12,h:7.44,fill:{color:BLUE}});

  s.addText("Next Steps",{x:MARGIN,y:0.3,w:7,h:0.5,fontSize:F.TITLE,fontFace:"Calibri",bold:true,color:NAVY,margin:0});

  // ── Left side: CTA + action plan ──
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.1,w:7.3,h:5.2,fill:{color:WHITE},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.1,w:0.06,h:5.2,fill:{color:GREEN}});

  s.addText("Grant me editor access and I'll implement\nthe quick wins in Week 1.",{
    x:MARGIN+0.3,y:1.25,w:6.7,h:0.8,fontSize:F.STAT-2,fontFace:"Calibri",bold:true,color:NAVY,margin:0
  });

  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN+0.3,y:2.15,w:3,h:0.04,fill:{color:GREEN}});

  s.addText([
    {text:"Day 1",options:{bold:true,color:GREEN}},
    {text:": Fix conversion tracking, set target CPA, disable auto-apply",options:{breakLine:true,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Day 2-3",options:{bold:true,color:GREEN}},
    {text:": Add phrase-match negative keywords, pause waste ad groups",options:{breakLine:true,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Day 4-5",options:{bold:true,color:GREEN}},
    {text:": Implement schedule and device bid adjustments",options:{breakLine:true,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Week 2+",options:{bold:true,color:GREEN}},
    {text:": Launch ad copy tests, begin weekly optimisation cycle",options:{breakLine:true,color:BLACK}},
  ],{x:MARGIN+0.3,y:2.4,w:6.7,h:2.5,fontSize:F.BODY,fontFace:"Calibri",margin:0,valign:"top"});

  // What you'll see
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN+0.3,y:5.0,w:6.7,h:0.04,fill:{color:BLUE}});
  s.addText([
    {text:"What you'll see: ",options:{bold:true,color:NAVY}},
    {text:"Lower CPAs within 2 weeks. Fewer wasted clicks immediately. Monthly reports showing exactly what changed and what improved.",options:{color:BLACK}},
  ],{x:MARGIN+0.3,y:5.15,w:6.7,h:0.7,fontSize:F.BODY,fontFace:"Calibri",margin:0,valign:"top"});

  // ── Right side: Contact + stats ──
  // Contact card
  s.addShape(pres.shapes.RECTANGLE,{x:8.3,y:1.1,w:4.4,h:2.4,fill:{color:NAVY}});
  s.addImage({path:LOGO_PATH,x:8.7,y:1.35,w:0.55,h:0.55});
  s.addText("Christopher Hoole",{x:9.4,y:1.35,w:3,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:WHITE,margin:0});
  s.addText("Google Ads Specialist",{x:9.4,y:1.65,w:3,h:0.25,fontSize:F.BODY,fontFace:"Calibri",color:WHITE,margin:0});

  s.addShape(pres.shapes.RECTANGLE,{x:8.7,y:2.1,w:3.6,h:0.03,fill:{color:BLUE}});

  s.addText([
    {text:"christopherhoole.com",options:{breakLine:true,fontSize:F.BODY,color:GREEN,bold:true}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Ready to start whenever you are.",options:{fontSize:F.BODY,color:WHITE}},
  ],{x:8.7,y:2.3,w:3.6,h:0.9,fontFace:"Calibri",margin:0});

  // Three stat cards stacked vertically
  const cX = 8.3, cW = 4.4, cH = 0.85, cGap = 0.15;

  s.addShape(pres.shapes.RECTANGLE,{x:cX,y:3.7,w:cW,h:cH,fill:{color:WHITE},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:cX,y:3.7,w:0.06,h:cH,fill:{color:GREEN}});
  s.addText("\u00A320-25 CPA",{x:cX+0.2,y:3.75,w:2.5,h:0.35,fontSize:F.SECTION+2,fontFace:"Calibri",bold:true,color:GREEN,margin:0});
  s.addText("Target cost per conversion",{x:cX+0.2,y:4.12,w:cW-0.4,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});

  s.addShape(pres.shapes.RECTANGLE,{x:cX,y:3.7+cH+cGap,w:cW,h:cH,fill:{color:WHITE},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:cX,y:3.7+cH+cGap,w:0.06,h:cH,fill:{color:BLUE}});
  s.addText("\u00A34,560-7,860/yr",{x:cX+0.2,y:3.75+cH+cGap,w:3,h:0.35,fontSize:F.SECTION+2,fontFace:"Calibri",bold:true,color:BLUE,margin:0});
  s.addText("Projected annual saving",{x:cX+0.2,y:4.12+cH+cGap,w:cW-0.4,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});

  s.addShape(pres.shapes.RECTANGLE,{x:cX,y:3.7+2*(cH+cGap),w:cW,h:cH,fill:{color:WHITE},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:cX,y:3.7+2*(cH+cGap),w:0.06,h:cH,fill:{color:AMBER}});
  s.addText("Week 1 Start",{x:cX+0.2,y:3.75+2*(cH+cGap),w:3,h:0.35,fontSize:F.SECTION+2,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addText("Improvements begin immediately",{x:cX+0.2,y:4.12+2*(cH+cGap),w:cW-0.4,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});

  addFooter(s,14);
}

// ── Save ──
pres.writeFile({fileName:OUTPUT}).then(() => {
  console.log(`Report 3 saved to: ${OUTPUT}`);
}).catch(err => console.error("Error:",err));
