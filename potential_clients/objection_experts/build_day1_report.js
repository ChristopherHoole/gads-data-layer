const pptxgen = require("pptxgenjs");
const path = require("path");

const CHART_DIR = path.join(__dirname, "charts");
const OUTPUT = path.join(__dirname, "reports", "05_day1_implementation_report_v3.pptx");

const NAVY = "1A237E", BLUE = "4285F4", RED = "EA4335", AMBER = "FBBC05", GREEN = "34A853";
const L_GREY = "F5F6FA", BLACK = "1A1A1A", WHITE = "FFFFFF";
const LOGO_PATH = path.join(CHART_DIR, "act_logo.png");

const F = { HERO: 44, TITLE: 28, STAT: 22, SECTION: 14, BODY: 11, FOOTER: 11 };
const makeCardShadow = () => ({ type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.10 });

let pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Christopher Hoole";
pres.title = "Day 1 Implementation Report \u2014 Objection Experts";
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
  s.addText("1 April 2026",{x:W-MARGIN-2.4,y:0.32,w:2.3,h:0.4,fontSize:F.BODY,fontFace:"Calibri",color:GREEN,align:"center",valign:"middle",bold:true,margin:0});
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

  s.addText("DAY 1\nIMPLEMENTATION\nREPORT",{x:0.6,y:1.2,w:5.5,h:2.2,fontSize:F.HERO,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addShape(pres.shapes.RECTANGLE,{x:0.6,y:3.5,w:2.5,h:0.05,fill:{color:BLUE}});
  s.addText("Objection Experts",{x:0.6,y:3.75,w:5.5,h:0.5,fontSize:F.STAT,fontFace:"Calibri",color:BLUE,margin:0});
  s.addText([
    {text:"1 April 2026",options:{breakLine:true,fontSize:F.BODY,color:BLACK,bold:true}},
    {text:"Christopher Hoole  |  Google Ads Specialist",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"christopherhoole.com",options:{fontSize:F.BODY,color:BLUE}},
  ],{x:0.6,y:4.5,w:5.5,h:1.0,fontFace:"Calibri",margin:0});

  // Right side — summary
  const rX=6.8, rW=5.9;
  s.addShape(pres.shapes.RECTANGLE,{x:rX,y:0.5,w:rW,h:1.5,fill:{color:WHITE},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:rX,y:0.5,w:0.08,h:1.5,fill:{color:GREEN}});
  s.addText("11 Changes Implemented",{x:rX+0.3,y:0.6,w:rW-0.5,h:0.35,fontSize:F.SECTION,fontFace:"Calibri",color:NAVY,margin:0});
  s.addText("Quick wins from audit reports \u2014 all live today",{x:rX+0.3,y:1.0,w:rW-0.5,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});
  s.addText("Expected impact: CPA reduction from \u00A339 toward \u00A325",{x:rX+0.3,y:1.35,w:rW-0.5,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:GREEN,bold:true,margin:0});

  const smW=(rW-0.4)/3, smY=2.3, smH=1.0;
  s.addShape(pres.shapes.RECTANGLE,{x:rX,y:smY,w:smW,h:smH,fill:{color:WHITE},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:rX,y:smY,w:0.06,h:smH,fill:{color:RED}});
  s.addText("Tracking",{x:rX+0.15,y:smY+0.1,w:smW-0.25,h:0.35,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:RED,margin:0});
  s.addText("Fixed",{x:rX+0.15,y:smY+0.5,w:smW-0.25,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});

  const sm2X=rX+smW+0.2;
  s.addShape(pres.shapes.RECTANGLE,{x:sm2X,y:smY,w:smW,h:smH,fill:{color:WHITE},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:sm2X,y:smY,w:0.06,h:smH,fill:{color:BLUE}});
  s.addText("255",{x:sm2X+0.15,y:smY+0.1,w:smW-0.25,h:0.35,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:BLUE,margin:0});
  s.addText("New Negatives",{x:sm2X+0.15,y:smY+0.5,w:smW-0.25,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});

  const sm3X=rX+2*(smW+0.2);
  s.addShape(pres.shapes.RECTANGLE,{x:sm3X,y:smY,w:smW,h:smH,fill:{color:WHITE},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:sm3X,y:smY,w:0.06,h:smH,fill:{color:GREEN}});
  s.addText("52",{x:sm3X+0.15,y:smY+0.1,w:smW-0.25,h:0.35,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:GREEN,margin:0});
  s.addText("Location Targets",{x:sm3X+0.15,y:smY+0.5,w:smW-0.25,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});

  addStripeBar(s,7.0,0.04);
}

// ═══════════════════════════════════════════
// SLIDE 2: EXECUTIVE SUMMARY (cards with coloured numbers, no dots)
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:WHITE};
  addSlideTitle(s,"What We Did Today",null);

  const changes = [
    {num:"1",text:"Fixed conversion tracking \u2014 Email Click moved from Primary to Secondary. The algorithm will no longer optimise for email link clicks.",color:RED},
    {num:"2",text:"Set Target CPA to \u00A330 \u2014 the algorithm now has a cost guardrail. Previously there was no target, allowing unlimited spend per conversion.",color:RED},
    {num:"3",text:"Disabled auto-apply recommendations \u2014 removed 2 dangerous auto-applies. Google can no longer make unsupervised changes.",color:RED},
    {num:"4",text:"Rebuilt negative keywords from scratch \u2014 255 keywords across 7 lists organised by word count (phrase + exact match only).",color:BLUE},
    {num:"5",text:"Removed 6 dangerous broad-match negatives \u2014 keywords like \"appeal\", \"test\", \"hire\" were actively blocking paying customers.",color:BLUE},
    {num:"6",text:"Re-enabled 8 high-performing keywords \u2014 573 lifetime conversions at \u00A324 average CPA. Paused by previous agency in Oct 2025.",color:GREEN},
    {num:"7",text:"Paused wasteful ad group \u2014 Neighbourhood Objections (zero conversions, \u00A379 wasted). Volume consolidated into the main ad group.",color:GREEN},
    {num:"8",text:"Adjusted device bids \u2014 Tablet reduced from -20% to -30%. Mobile and desktop kept at +10%.",color:AMBER},
    {num:"9",text:"Ad schedule bid adjustments \u2014 +15% on 8 best-performing slots, -40% on 9 worst-performing slots.",color:AMBER},
    {num:"10",text:"Rebuilt geographic targeting \u2014 replaced 20 overlapping targets with 52 county-level targets. Tiered bid adjustments.",color:AMBER},
    {num:"11",text:"Cleaned up misconfigured goal \u2014 removed Android installs conversion action (not relevant to this business).",color:BLUE},
  ];

  changes.forEach((c,i) => {
    const col = i < 6 ? MARGIN : 6.8;
    const row = i < 6 ? i : i - 6;
    const y = 1.0 + row * 0.95;
    const cardW = 5.9;

    s.addShape(pres.shapes.RECTANGLE,{x:col,y,w:cardW,h:0.85,fill:{color:WHITE},shadow:makeCardShadow(),line:{color:"E2E8F0",width:0.5}});
    s.addShape(pres.shapes.RECTANGLE,{x:col,y,w:0.05,h:0.85,fill:{color:c.color}});

    // Coloured number (no dot/circle)
    s.addText(c.num,{x:col+0.12,y:y+0.08,w:0.35,h:0.7,fontSize:F.STAT,fontFace:"Calibri",bold:true,color:c.color,margin:0,valign:"middle"});

    s.addText(c.text,{x:col+0.5,y:y+0.08,w:cardW-0.7,h:0.7,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0,valign:"middle"});
  });

  addFooter(s,2);
}

// ═══════════════════════════════════════════
// SLIDE 3: CONVERSION TRACKING & BID STRATEGY
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:WHITE};
  addSlideTitle(s,"Conversion Tracking & Bid Strategy","The two most critical fixes \u2014 implemented immediately");

  // Before/after conversion tracking
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.3,w:5.8,h:2.5,fill:{color:"FCE8E6"},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.3,w:0.06,h:2.5,fill:{color:RED}});
  s.addText("Before",{x:MARGIN+0.25,y:1.4,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:RED,margin:0});
  s.addText([
    {text:"Email Click counted as Primary conversion",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Algorithm optimising for email link clicks (not real leads)",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"No target CPA set \u2014 unlimited cost per conversion",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Auto-apply enabled \u2014 Google making bid strategy changes",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Misconfigured Android download goal in account",options:{bullet:true,fontSize:F.BODY,color:BLACK}},
  ],{x:MARGIN+0.25,y:1.8,w:5.2,h:1.8,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:3});

  s.addShape(pres.shapes.RECTANGLE,{x:6.8,y:1.3,w:5.9,h:2.5,fill:{color:"E6F4EA"},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:6.8,y:1.3,w:0.06,h:2.5,fill:{color:GREEN}});
  s.addText("After",{x:7.1,y:1.4,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:GREEN,margin:0});
  s.addText([
    {text:"Email Click moved to Secondary \u2014 excluded from bidding",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Algorithm now optimises only for form submissions + calls",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Target CPA set to \u00A330 \u2014 clear cost guardrail in place",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Dangerous auto-applies disabled (conflicting neg removal + tracking upgrades)",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Misconfigured download goal removed",options:{bullet:true,fontSize:F.BODY,color:BLACK}},
  ],{x:7.1,y:1.8,w:5.4,h:1.8,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:3});

  // Impact statement
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:4.1,w:W-2*MARGIN,h:1.3,fill:{color:"E8F0FE"},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:4.1,w:0.06,h:1.3,fill:{color:BLUE}});
  s.addText("Expected Impact",{x:MARGIN+0.25,y:4.2,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addText([
    {text:"The target CPA gives the algorithm a cost ceiling it didn't have before. Combined with cleaner conversion data, the algorithm can now make better decisions about which clicks to pursue and which to avoid.",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Target CPA reduction plan: \u00A330 (now) \u2192 \u00A327 (week 4) \u2192 \u00A325 (week 8)",options:{bold:true,fontSize:F.BODY,color:GREEN}},
  ],{x:MARGIN+0.25,y:4.55,w:W-2*MARGIN-0.5,h:0.75,fontFace:"Calibri",margin:0,valign:"top"});

  // Auto-apply kept
  s.addText("Note: \"Use optimised ad rotation\" auto-apply was kept enabled \u2014 this is standard best practice and helps serve the best-performing ad.",{
    x:MARGIN,y:5.6,w:W-2*MARGIN,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:NAVY,italic:true,margin:0
  });

  addFooter(s,3);
}

// ═══════════════════════════════════════════
// SLIDE 4: NEGATIVE KEYWORDS
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:WHITE};
  addSlideTitle(s,"Negative Keyword Overhaul","From 191 broad-match keywords to 255 structured phrase/exact keywords");

  // Before/after
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.3,w:5.8,h:2.0,fill:{color:"FCE8E6"},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.3,w:0.06,h:2.0,fill:{color:RED}});
  s.addText("Before",{x:MARGIN+0.25,y:1.4,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:RED,margin:0});
  s.addText([
    {text:"191 keywords in a single broad-match list",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"6 were actively blocking converting search terms",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK,bold:true}},
    {text:"(\"appeal\", \"appealing\", \"appeals\", \"test\", \"hire\", \"usa\")",options:{breakLine:true,fontSize:F.BODY,color:RED}},
    {text:"No structure \u2014 impossible to audit or maintain",options:{bullet:true,fontSize:F.BODY,color:BLACK}},
  ],{x:MARGIN+0.25,y:1.8,w:5.2,h:1.3,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:3});

  s.addShape(pres.shapes.RECTANGLE,{x:6.8,y:1.3,w:5.9,h:2.0,fill:{color:"E6F4EA"},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:6.8,y:1.3,w:0.06,h:2.0,fill:{color:GREEN}});
  s.addText("After",{x:7.1,y:1.4,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:GREEN,margin:0});
  s.addText([
    {text:"255 keywords across 7 organised lists",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Phrase match + exact match only (no broad match)",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"6 dangerous blockers removed \u2014 converting terms now free to show",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK,bold:true}},
    {text:"Safety-checked against all converting search terms before applying",options:{bullet:true,fontSize:F.BODY,color:BLACK}},
  ],{x:7.1,y:1.8,w:5.4,h:1.3,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:3});

  // List structure table
  const tblH = [[
    {text:"List Name",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY}},
    {text:"Match Type",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Keywords",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
  ]];
  const tblR = [
    ["1 word","Phrase","183"],
    ["2 words","Phrase","23"],
    ["2 words","Exact","23"],
    ["3 words","Phrase","12"],
    ["3 words","Exact","12"],
    ["4 words","Exact","1"],
    ["5+ words","Exact","1"],
  ].map((row,i) => row.map((cell,j) => ({
    text:cell, options:{fill:{color:i%2===0?L_GREY:WHITE},fontSize:F.BODY,color:BLACK,align:j>0?"center":"left"}
  })));

  s.addTable([...tblH,...tblR],{
    x:MARGIN,y:3.6,w:5.8,h:3.0,
    colW:[2.5,1.8,1.5],
    border:{type:"solid",pt:0.5,color:"E2E8F0"},
    rowH:0.35,margin:[3,6,3,6],
  });

  // Key discovery callout
  s.addShape(pres.shapes.RECTANGLE,{x:6.8,y:3.6,w:5.9,h:3.0,fill:{color:"E8F0FE"},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:6.8,y:3.6,w:0.06,h:3.0,fill:{color:RED}});
  s.addText("Critical Discovery",{x:7.1,y:3.7,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:RED,margin:0});
  s.addText([
    {text:"The old broad-match negative \"appeal\" was blocking 17 search terms that actually convert \u2014 including \"appeal planning decision\" and \"planning permission appeals\".",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"The broad-match negative \"hire\" was blocking \"cheshire east planning objections\" because broad match sees \"hire\" inside \"cheshire\".",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"The broad-match negative \"test\" was blocking \"contest planning application\" because broad match sees \"test\" inside \"contest\".",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"These are now removed. Converting traffic is no longer being blocked.",options:{bold:true,fontSize:F.BODY,color:GREEN}},
  ],{x:7.1,y:4.1,w:5.4,h:2.3,fontFace:"Calibri",margin:0,valign:"top"});

  addFooter(s,4);
}

// ═══════════════════════════════════════════
// SLIDE 5: KEYWORD AUDIT
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:WHITE};
  addSlideTitle(s,"Keyword Audit","8 high-performing paused keywords re-enabled \u2014 573 lifetime conversions at \u00A324 avg CPA");

  const tblH = [[
    {text:"Keyword",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY}},
    {text:"Lifetime Conv.",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"CPA",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Conv Rate",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Status",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
  ]];

  const keywords = [
    ['"object to planning application"',"179","\u00A322.08","6.5%","Re-enabled"],
    ['"opposing planning permission"',"126","\u00A328.66","5.9%","Re-enabled"],
    ['"planning objection specialist"',"63","\u00A320.97","18.4%","Re-enabled"],
    ['"planning objection consultants"',"57","\u00A322.65","16.9%","Re-enabled"],
    ['"planning objection letter"',"57","\u00A324.94","6.3%","Re-enabled"],
    ['"contesting planning permission"',"44","\u00A329.52","7.2%","Re-enabled"],
    ['"planning permission objections"',"37","\u00A327.78","6.0%","Re-enabled"],
    ['"planning objection solicitor"',"10","\u00A310.77","22.6%","Re-enabled"],
  ];

  const tblR = keywords.map((row,i) => row.map((cell,j) => ({
    text:cell, options:{fill:{color:i%2===0?L_GREY:WHITE},fontSize:F.BODY,color:j===4?GREEN:(j===2?GREEN:BLACK),align:j>0?"center":"left",bold:j===4}
  })));

  s.addTable([...tblH,...tblR],{
    x:MARGIN,y:1.3,w:W-2*MARGIN,h:3.5,
    colW:[4.5,2,1.5,1.5,2.5],
    border:{type:"solid",pt:0.5,color:"E2E8F0"},
    rowH:0.38,margin:[3,6,3,6],
  });

  // Summary stats
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:5.1,w:W-2*MARGIN,h:1.3,fill:{color:"E8F0FE"},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:5.1,w:0.06,h:1.3,fill:{color:GREEN}});
  s.addText([
    {text:"Combined impact: ",options:{bold:true,color:NAVY}},
    {text:"These 8 keywords have generated 573 lifetime conversions at an average CPA of \u00A324.30. The previous agency paused them all in October 2025 as part of a restructure.",options:{breakLine:true,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Also paused: ",options:{bold:true,color:RED}},
    {text:"Neighbourhood Objections ad group (zero conversions, \u00A379 wasted). Volume now consolidated into the main Planning Objections ad group with 12 active keywords.",options:{color:BLACK}},
  ],{x:MARGIN+0.25,y:5.2,w:W-2*MARGIN-0.5,h:1.1,fontSize:F.BODY,fontFace:"Calibri",margin:0,valign:"top"});

  addFooter(s,5);
}

// ═══════════════════════════════════════════
// SLIDE 6: BID ADJUSTMENTS
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:WHITE};
  addSlideTitle(s,"Bid Adjustments","Device, schedule, and day-of-week optimisations");

  // Device
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.3,w:3.8,h:2.5,fill:{color:L_GREY},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.3,w:0.06,h:2.5,fill:{color:BLUE}});
  s.addText("Device Bids",{x:MARGIN+0.25,y:1.4,w:3,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addText([
    {text:"Mobile: +10% (no change)",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Best CPA (\u00A327), 57% of spend",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Desktop: +10% (no change)",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Best conv rate (8.6%), strong CPA (\u00A328)",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Tablet: -20% \u2192 -30%",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:RED,bold:true}},
    {text:"Lowest conv rate (4.9%), volatile CPA",options:{fontSize:F.BODY,color:BLACK}},
  ],{x:MARGIN+0.25,y:1.8,w:3.3,h:1.8,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:2});

  // Schedule increases
  s.addShape(pres.shapes.RECTANGLE,{x:4.7,y:1.3,w:3.8,h:2.5,fill:{color:"E6F4EA"},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:4.7,y:1.3,w:0.06,h:2.5,fill:{color:GREEN}});
  s.addText("Increased (+15%)",{x:4.95,y:1.4,w:3,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:GREEN,margin:0});
  s.addText("8 best-performing time slots:",{x:4.95,y:1.75,w:3.3,h:0.25,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});
  s.addText([
    {text:"Mon 2-5pm, Mon 5pm-12am",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Wed 2-5pm",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Thu 12-6am, Thu 5pm-12am",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Fri 12-2pm",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Sat 5pm-12am",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Sun 12-6am",options:{bullet:true,fontSize:F.BODY,color:BLACK}},
  ],{x:4.95,y:2.05,w:3.3,h:1.6,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:2});

  // Schedule decreases
  s.addShape(pres.shapes.RECTANGLE,{x:8.8,y:1.3,w:3.9,h:2.5,fill:{color:"FCE8E6"},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:8.8,y:1.3,w:0.06,h:2.5,fill:{color:RED}});
  s.addText("Reduced (-40%)",{x:9.05,y:1.4,w:3,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:RED,margin:0});
  s.addText("9 worst-performing time slots:",{x:9.05,y:1.75,w:3.4,h:0.25,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0});
  s.addText([
    {text:"Mon 6-9am, Wed 6-9am, Wed 9-12pm",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Fri 6-9am, Fri 5pm-12am",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Sat 6-9am",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Sun 9-12pm, Sun 12-2pm, Sun 2-5pm",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"25 slots left unchanged \u2014 will review monthly",options:{fontSize:F.BODY,color:NAVY,italic:true}},
  ],{x:9.05,y:2.05,w:3.4,h:1.6,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:2});

  // Rationale
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:4.1,w:W-2*MARGIN,h:1.0,fill:{color:"E8F0FE"}});
  s.addText("All bid adjustments are based on all-time performance data. They will be reviewed and refined monthly as new data accumulates. The approach is deliberate: increase spend where CPA is strong, reduce where it's weak.",{
    x:MARGIN+0.25,y:4.15,w:W-2*MARGIN-0.5,h:0.9,fontSize:F.BODY,fontFace:"Calibri",color:NAVY,valign:"middle",margin:0
  });

  addFooter(s,6);
}

// ═══════════════════════════════════════════
// SLIDE 7: GEOGRAPHIC REBUILD
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:WHITE};
  addSlideTitle(s,"Geographic Targeting Rebuild","From 20 overlapping targets to 52 clean county-level targets");

  // Before
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.3,w:5.8,h:2.0,fill:{color:"FCE8E6"},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.3,w:0.06,h:2.0,fill:{color:RED}});
  s.addText("Before",{x:MARGIN+0.25,y:1.4,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:RED,margin:0});
  s.addText([
    {text:"20 overlapping location targets",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"\"United Kingdom\" catch-all (45% of spend, worst CPA)",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"London targeted 3 times (city + radius + catch-all)",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Random radius targets including \"Hair Salons within Plymouth\"",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"No bid adjustments \u2014 every area treated equally",options:{bullet:true,fontSize:F.BODY,color:BLACK}},
  ],{x:MARGIN+0.25,y:1.8,w:5.2,h:1.3,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:3});

  // After
  s.addShape(pres.shapes.RECTANGLE,{x:6.8,y:1.3,w:5.9,h:2.0,fill:{color:"E6F4EA"},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:6.8,y:1.3,w:0.06,h:2.0,fill:{color:GREEN}});
  s.addText("After",{x:7.1,y:1.4,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:GREEN,margin:0});
  s.addText([
    {text:"52 county-level targets \u2014 full UK coverage, zero overlap",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"49 English counties + Scotland + Wales + Northern Ireland",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Tiered bid adjustments: +15% (13 top counties), 0% (20), -20% (7 weak)",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Every click now attributable to a specific county",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Clean data for monthly optimisation from day one",options:{bullet:true,fontSize:F.BODY,color:BLACK}},
  ],{x:7.1,y:1.8,w:5.4,h:1.3,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:3});

  // Top performing counties
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:3.6,w:W-2*MARGIN,h:2.8,fill:{color:L_GREY},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:3.6,w:0.06,h:2.8,fill:{color:BLUE}});
  s.addText("Top Performing Counties (+15% bid increase)",{x:MARGIN+0.25,y:3.7,w:10,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});

  const topCounties = [
    ["Greater London","58 conv","\u00A322 CPA","10.6% CR"],
    ["Kent","30 conv","\u00A320 CPA","10.6% CR"],
    ["Essex","27 conv","\u00A320 CPA","11.6% CR"],
    ["Surrey","30 conv","\u00A322 CPA","10.7% CR"],
    ["Hertfordshire","19 conv","\u00A322 CPA","9.2% CR"],
    ["Norfolk","14 conv","\u00A315 CPA","13.3% CR"],
    ["Staffordshire","13 conv","\u00A313 CPA","11.9% CR"],
  ];

  const ctH = [[
    {text:"County",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY}},
    {text:"Conversions",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"CPA",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Conv Rate",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
  ]];
  const ctR = topCounties.map((row,i) => row.map((cell,j) => ({
    text:cell, options:{fill:{color:i%2===0?"E8F0FE":WHITE},fontSize:F.BODY,color:j>=1?GREEN:BLACK,align:j>0?"center":"left",bold:j===2}
  })));

  s.addTable([...ctH,...ctR],{
    x:MARGIN+0.2,y:4.1,w:W-2*MARGIN-0.4,h:2.1,
    colW:[3.5,2.5,2.5,3],
    border:{type:"solid",pt:0.5,color:"E2E8F0"},
    rowH:0.26,margin:[2,6,2,6],
  });

  addFooter(s,7);
}

// ═══════════════════════════════════════════
// SLIDE 8: WHAT'S NEXT
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:L_GREY};
  addStripeBar(s,0,0.06);
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:0.06,w:0.12,h:7.44,fill:{color:BLUE}});

  s.addText("What Happens Next",{x:MARGIN,y:0.3,w:7,h:0.5,fontSize:F.TITLE,fontFace:"Calibri",bold:true,color:NAVY,margin:0});

  // Timeline
  const steps = [
    {when:"Tomorrow\n(2 April)",what:"Deep keyword audit, search term exclusions, new ad copy variants for testing",color:RED},
    {when:"Week 2\n(7 April)",what:"Landing page build begins \u2014 dedicated page to improve Quality Score",color:AMBER},
    {when:"Week 3\n(14 April)",what:"Landing page live. First performance review of Day 1 changes.",color:GREEN},
    {when:"Week 4\n(21 April)",what:"Full analysis. Reduce target CPA to \u00A327 if data supports it. Month 1 report.",color:BLUE},
  ];

  steps.forEach((st,i) => {
    const y = 1.1 + i * 1.15;
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y,w:W-2*MARGIN,h:1.0,fill:{color:WHITE},shadow:makeCardShadow()});
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y,w:0.06,h:1.0,fill:{color:st.color}});
    s.addText(st.when,{x:MARGIN+0.25,y:y+0.1,w:1.6,h:0.7,fontSize:F.BODY,fontFace:"Calibri",color:st.color,bold:true,margin:0,valign:"middle"});
    s.addText(st.what,{x:MARGIN+2.0,y:y+0.1,w:W-2*MARGIN-2.3,h:0.7,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0,valign:"middle"});
  });

  // Reporting commitment
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:5.8,w:W-2*MARGIN,h:0.8,fill:{color:NAVY}});
  s.addText([
    {text:"Monthly reports showing exactly what changed and what improved. ",options:{color:WHITE}},
    {text:"No vanity metrics, no jargon. Just data.",options:{color:GREEN,bold:true}},
  ],{x:MARGIN+0.3,y:5.8,w:W-2*MARGIN-0.6,h:0.8,fontSize:F.BODY,fontFace:"Calibri",align:"center",valign:"middle",margin:0});

  addFooter(s,8);
}

// ── Save ──
pres.writeFile({fileName:OUTPUT}).then(() => {
  console.log(`Day 1 report saved to: ${OUTPUT}`);
}).catch(err => console.error("Error:",err));
