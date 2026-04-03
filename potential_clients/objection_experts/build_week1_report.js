const pptxgen = require("pptxgenjs");
const path = require("path");

const CHART_DIR = path.join(__dirname, "charts");
const OUTPUT = path.join(__dirname, "reports", "06_week1_session_report_v1.pptx");

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
  s.addText("3 April 2026",{x:W-MARGIN-2.4,y:0.32,w:2.3,h:0.4,fontSize:F.BODY,fontFace:"Calibri",color:GREEN,align:"center",valign:"middle",bold:true,margin:0});
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

  s.addText("WEEK 1\nSESSION REPORT",{x:0.6,y:1.4,w:5.5,h:1.5,fontSize:F.HERO,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addShape(pres.shapes.RECTANGLE,{x:0.6,y:3.0,w:2.5,h:0.05,fill:{color:BLUE}});
  s.addText("Objection Experts",{x:0.6,y:3.25,w:5.5,h:0.5,fontSize:F.STAT,fontFace:"Calibri",color:BLUE,margin:0});
  s.addText([
    {text:"3 April 2026",options:{breakLine:true,fontSize:F.BODY,color:BLACK,bold:true}},
    {text:"Christopher Hoole  |  Google Ads Specialist",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"christopherhoole.com",options:{fontSize:F.BODY,color:BLUE}},
  ],{x:0.6,y:4.0,w:5.5,h:1.0,fontFace:"Calibri",margin:0});

  // Right side stats
  const rX=6.8, rW=5.9, smW=(rW-0.4)/3, smY=0.5, smH=1.0;

  addStatCard(s,rX,smY,smW,smH,"548+","Terms Excluded",RED);
  addStatCard(s,rX+smW+0.2,smY,smW,smH,"17","Keywords Added",GREEN);
  addStatCard(s,rX+2*(smW+0.2),smY,smW,smH,"1","New RSA Built",BLUE);

  // Second row
  const sm2Y = 1.7;
  addStatCard(s,rX,sm2Y,smW,smH,"Excellent","New Ad Strength",GREEN);
  addStatCard(s,rX+smW+0.2,sm2Y,smW,smH,"10","Appeal Negatives",AMBER);
  addStatCard(s,rX+2*(smW+0.2),sm2Y,smW,smH,"4","Owen Fixes",BLUE);

  // Focus areas
  s.addShape(pres.shapes.RECTANGLE,{x:rX,y:3.0,w:rW,h:2.0,fill:{color:WHITE},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:rX,y:3.0,w:0.06,h:2.0,fill:{color:NAVY}});
  s.addText("Today\u2019s Focus",{x:rX+0.25,y:3.1,w:rW-0.5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addText([
    {text:"1. Owen\u2019s feedback on negative keywords",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"2. Keyword audit \u2014 17 new high-performers added",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"3. Search term review \u2014 548+ exclusions",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"4. Ad copy \u2014 new Excellent-strength RSA live",options:{bullet:true,fontSize:F.BODY,color:BLACK}},
  ],{x:rX+0.25,y:3.5,w:rW-0.5,h:1.3,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:4});

  addStripeBar(s,7.0,0.04);
}

// ═══════════════════════════════════════════
// SLIDE 2: WHAT WE DID
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:WHITE};
  addSlideTitle(s,"What We Did Today","Week 1 optimisation session \u2014 2 hours");

  const changes = [
    {num:"1",text:"Actioned Owen\u2019s feedback \u2014 removed \"permitted development\", \"change of use\", \"planning permission extension\" from negatives. Owen objects to these applications.",color:RED},
    {num:"2",text:"Added 10 appeal phrase-match negatives \u2014 Owen confirmed appeals are a different service. Blocks \u00A3390/year of wasted spend on appeal searches.",color:RED},
    {num:"3",text:"Replaced \"planning consultant\" phrase match with exact-match variants \u2014 stops blocking \"objection by planning consultant\" while still blocking wrong-service searches.",color:RED},
    {num:"4",text:"Added 17 new high-converting keywords \u2014 found from search term data. Best finds: \"planning objection advice\" (CPA \u00A310), \"object planning permission\" (CPA \u00A36).",color:GREEN},
    {num:"5",text:"Excluded 548+ irrelevant search terms as exact match \u2014 appeals, refusals, solicitor searches, templates, DIY intent, informational queries. All organised by word count.",color:BLUE},
    {num:"6",text:"Paused worst-performing RSA (CPA \u00A359, CR 4.3%) \u2014 \"Planning Objection Help\" was dragging down account performance.",color:AMBER},
    {num:"7",text:"Built new RSA with Excellent ad strength \u2014 Trust & Credibility angle. 15 headlines, 4 descriptions, keywords in descriptions. Now in review.",color:GREEN},
  ];

  changes.forEach((c,i) => {
    const col = i < 4 ? MARGIN : 6.8;
    const row = i < 4 ? i : i - 4;
    const y = 1.15 + row * 1.3;
    const cardW = 5.9;

    s.addShape(pres.shapes.RECTANGLE,{x:col,y,w:cardW,h:1.15,fill:{color:WHITE},shadow:makeCardShadow(),line:{color:"E2E8F0",width:0.5}});
    s.addShape(pres.shapes.RECTANGLE,{x:col,y,w:0.05,h:1.15,fill:{color:c.color}});
    s.addText(c.num,{x:col+0.12,y:y+0.08,w:0.35,h:1.0,fontSize:F.STAT,fontFace:"Calibri",bold:true,color:c.color,margin:0,valign:"top"});
    s.addText(c.text,{x:col+0.5,y:y+0.08,w:cardW-0.7,h:1.0,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0,valign:"middle"});
  });

  addFooter(s,2);
}

// ═══════════════════════════════════════════
// SLIDE 3: KEYWORD CHANGES
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:WHITE};
  addSlideTitle(s,"Keyword & Negative Changes","Client feedback actioned + new keywords from search term data");

  // Owen's fixes
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.3,w:5.8,h:2.5,fill:{color:WHITE},shadow:makeCardShadow(),line:{color:"E2E8F0",width:0.5}});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.3,w:0.06,h:2.5,fill:{color:RED}});
  s.addText("Owen\u2019s Feedback Actioned",{x:MARGIN+0.25,y:1.4,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addText([
    {text:"Removed from negatives (Owen\u2019s core services):",options:{bold:true,breakLine:true,fontSize:F.BODY,color:NAVY}},
    {text:"\"permitted development\" \u2014 Owen objects to these",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"\"change of use\" \u2014 Owen\u2019s most common work currently",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"\"planning permission extension\" \u2014 Owen objects to these",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"\"planning consultant\" phrase match \u2192 exact match variants",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Added 10 appeal phrase-match negatives:",options:{bold:true,breakLine:true,fontSize:F.BODY,color:RED}},
    {text:"Owen confirmed: appeals are a completely different planning service",options:{fontSize:F.BODY,color:BLACK}},
  ],{x:MARGIN+0.25,y:1.8,w:5.2,h:1.8,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:2});

  // New keywords
  s.addShape(pres.shapes.RECTANGLE,{x:6.8,y:1.3,w:5.9,h:2.5,fill:{color:WHITE},shadow:makeCardShadow(),line:{color:"E2E8F0",width:0.5}});
  s.addShape(pres.shapes.RECTANGLE,{x:6.8,y:1.3,w:0.06,h:2.5,fill:{color:GREEN}});
  s.addText("17 New Keywords Added",{x:7.1,y:1.4,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addText([
    {text:"Top performers from search term data:",options:{bold:true,breakLine:true,fontSize:F.BODY,color:GREEN}},
    {text:"\"planning objection advice\" \u2014 CPA \u00A310, 39% CR",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"\"object planning permission\" \u2014 CPA \u00A36, 37% CR",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"\"objection planning application\" \u2014 CPA \u00A35, 44% CR",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"\"how to stop a planning application\" \u2014 CPA \u00A312",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"\"oppose planning permission\" \u2014 CPA \u00A311",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"All added as phrase match to Planning Objections ad group",options:{bold:true,fontSize:F.BODY,color:NAVY}},
  ],{x:7.1,y:1.8,w:5.4,h:1.8,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:2});

  // Search term exclusions summary
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:4.1,w:W-2*MARGIN,h:2.3,fill:{color:L_GREY},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:4.1,w:0.06,h:2.3,fill:{color:BLUE}});
  s.addText("548+ Search Terms Excluded",{x:MARGIN+0.25,y:4.2,w:10,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
  s.addText([
    {text:"Every non-converting, irrelevant search term reviewed and excluded as exact match. Categories blocked:",options:{breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Appeals & refusals \u2014 different planning service entirely (Owen confirmed)",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Solicitor/lawyer/consultant searches \u2014 people looking for different professionals",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Templates, samples, examples \u2014 DIY intent, not seeking a paid service",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"\"How many needed\", timescales, costs \u2014 purely informational queries",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"Council-specific searches, complaints, enforcement, building regs",options:{bullet:true,breakLine:true,fontSize:F.BODY,color:BLACK}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"All organised by word count across structured negative keyword lists (phrase + exact match).",options:{bold:true,fontSize:F.BODY,color:NAVY}},
  ],{x:MARGIN+0.25,y:4.55,w:W-2*MARGIN-0.5,h:1.7,fontFace:"Calibri",margin:0,valign:"top",paraSpaceAfter:2});

  addFooter(s,3);
}

// ═══════════════════════════════════════════
// SLIDE 4: AD COPY
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:WHITE};
  addSlideTitle(s,"Ad Copy Changes","Worst performer paused, new Excellent-strength RSA live");

  // Paused ad
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.3,w:5.8,h:1.8,fill:{color:"FCE8E6"},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:1.3,w:0.06,h:1.8,fill:{color:RED}});
  s.addText("Paused: \"Planning Objection Help\"",{x:MARGIN+0.25,y:1.4,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:RED,margin:0});
  s.addText([
    {text:"CPA: \u00A359.36  |  Conv Rate: 4.3%  |  CTR: 4.7%",options:{breakLine:true,fontSize:F.BODY,color:RED,bold:true}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"Worst performer across all metrics. Dragging down the ad group\u2019s overall performance. Pausing it concentrates budget into better-performing ads.",options:{fontSize:F.BODY,color:BLACK}},
  ],{x:MARGIN+0.25,y:1.8,w:5.2,h:1.1,fontFace:"Calibri",margin:0,valign:"top"});

  // New ad
  s.addShape(pres.shapes.RECTANGLE,{x:6.8,y:1.3,w:5.9,h:1.8,fill:{color:"E6F4EA"},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:6.8,y:1.3,w:0.06,h:1.8,fill:{color:GREEN}});
  s.addText("New: Trust & Credibility RSA",{x:7.1,y:1.4,w:5,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:GREEN,margin:0});
  s.addText([
    {text:"Ad Strength: Excellent",options:{breakLine:true,fontSize:F.BODY,color:GREEN,bold:true}},
    {text:"",options:{breakLine:true,fontSize:5}},
    {text:"15 headlines + 4 descriptions. Leads with RTPI credentials, 600+ objections, fixed pricing, free consultation. Keywords in descriptions for better relevance.",options:{fontSize:F.BODY,color:BLACK}},
  ],{x:7.1,y:1.8,w:5.4,h:1.1,fontFace:"Calibri",margin:0,valign:"top"});

  // Current ad lineup
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:3.4,w:W-2*MARGIN,h:2.5,fill:{color:L_GREY},shadow:makeCardShadow()});
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:3.4,w:0.06,h:2.5,fill:{color:NAVY}});
  s.addText("Current Ad Lineup (3 ads running)",{x:MARGIN+0.25,y:3.5,w:10,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});

  const adHeader = [[
    {text:"Ad",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY}},
    {text:"Type",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Strength",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"CPA",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Conv Rate",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
    {text:"Status",options:{fill:{color:NAVY},color:WHITE,bold:true,fontSize:F.BODY,align:"center"}},
  ]];

  const adRows = [
    ["RSA 1: Keyword Insertion","RSA","Good","\u00A326.42","7.1%","Running"],
    ["RSA 2: Objection Letter","RSA","Good","\u00A342.89","5.4%","Running"],
    ["NEW: Trust & Credibility","RSA","Excellent","TBD","TBD","In Review"],
  ].map((row,i) => row.map((cell,j) => ({
    text:cell,
    options:{
      fill:{color:i%2===0?L_GREY:WHITE},fontSize:F.BODY,color:j===5?(i===2?AMBER:GREEN):BLACK,
      align:j>0?"center":"left",bold:j===5||j===2
    }
  })));

  s.addTable([...adHeader,...adRows],{
    x:MARGIN+0.2,y:3.95,w:W-2*MARGIN-0.4,h:1.5,
    colW:[4,1.2,1.5,1.5,1.5,1.8],
    border:{type:"solid",pt:0.5,color:"E2E8F0"},
    rowH:0.35,margin:[3,6,3,6],
  });

  // Plan
  s.addText("Plan: If new RSA outperforms RSA 2 (\u00A342 CPA) within 1-2 weeks, pause RSA 2 and run our ad alongside the top performer.",{
    x:MARGIN,y:6.15,w:W-2*MARGIN,h:0.4,fontSize:F.BODY,fontFace:"Calibri",color:NAVY,bold:true,italic:true,margin:0
  });

  addFooter(s,4);
}

// ═══════════════════════════════════════════
// SLIDE 5: NEXT WEEK
// ═══════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = {color:L_GREY};
  addStripeBar(s,0,0.06);
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:0.06,w:0.12,h:7.44,fill:{color:BLUE}});

  s.addText("Next Monday (7 April)",{x:MARGIN,y:0.3,w:7,h:0.5,fontSize:F.TITLE,fontFace:"Calibri",bold:true,color:NAVY,margin:0});

  const tasks = [
    {title:"Check New RSA Performance",desc:"Is it approved? Getting impressions? Early CPA vs RSA 2 (\u00A342.89). If winning, consider pausing RSA 2.",time:"15 mins",color:GREEN},
    {title:"Search Term Review",desc:"1,776 remaining unactioned terms. Continue exclusion pass. Also review any new terms from this week\u2019s traffic.",time:"30 mins",color:BLUE},
    {title:"Add Sitelinks, Callouts & Snippets",desc:"Replace duplicate sitelinks with clean set. Add new callouts and structured snippets. Improves ad real estate and Quality Score.",time:"30 mins",color:AMBER},
    {title:"Landing Page Planning",desc:"Get Owen\u2019s site files. Map brand assets. Wireframe dedicated landing page for planning objection keywords. Start build.",time:"45 mins",color:RED},
  ];

  tasks.forEach((t,i) => {
    const y = 1.1 + i * 1.3;
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y,w:W-2*MARGIN,h:1.1,fill:{color:WHITE},shadow:makeCardShadow()});
    s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y,w:0.06,h:1.1,fill:{color:t.color}});
    s.addText(t.title,{x:MARGIN+0.25,y:y+0.1,w:8,h:0.3,fontSize:F.SECTION,fontFace:"Calibri",bold:true,color:NAVY,margin:0});
    s.addText(t.desc,{x:MARGIN+0.25,y:y+0.45,w:W-2*MARGIN-2.5,h:0.5,fontSize:F.BODY,fontFace:"Calibri",color:BLACK,margin:0,valign:"top"});
    s.addText(t.time,{x:W-MARGIN-1.5,y:y+0.1,w:1.3,h:0.3,fontSize:F.BODY,fontFace:"Calibri",color:t.color,bold:true,align:"right",margin:0});
  });

  // Bottom bar
  s.addShape(pres.shapes.RECTANGLE,{x:MARGIN,y:6.4,w:W-2*MARGIN,h:0.4,fill:{color:NAVY}});
  s.addText("2 hours every Monday \u2014 consistent, data-driven improvement.",{
    x:MARGIN+0.3,y:6.4,w:W-2*MARGIN-0.6,h:0.4,fontSize:F.BODY,fontFace:"Calibri",color:WHITE,align:"center",valign:"middle",margin:0
  });

  addFooter(s,5);
}

pres.writeFile({fileName:OUTPUT}).then(() => {
  console.log(`Week 1 report saved to: ${OUTPUT}`);
}).catch(err => console.error("Error:",err));
