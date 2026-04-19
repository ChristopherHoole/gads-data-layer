// Dental by Design — Week 1 Report (13-17 April 2026) — v2
// Matches the Account Structure Report v5 pitch deck style

const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.author = "Christopher Hoole";
pres.title = "Dental by Design - Week 1 Report - 13-17 April 2026";

// ============ Brand palette (matches pitch deck) ============
const INDIGO = "1A237E";       // primary
const INDIGO_DEEP = "131A5C";
const BLUE = "4285F4";          // Google brand
const RED = "EA4335";
const YELLOW = "FBBC05";
const GREEN = "34A853";
const CARD_BG = "E8F0FE";       // soft blue card fill
const BORDER = "E2E8F0";
const DARK = "1A1A1A";
const GREY = "6B7280";
const GREY_LIGHT = "F5F6FA";
const WHITE = "FFFFFF";

const LOGO = "C:/Users/User/Desktop/gads-data-layer/potential_clients/Inserta Dental/act_logo_official.png";

// ============ Common slide chrome ============
function addChrome(slide, pageNum, totalPages) {
  // 4-color stripe header
  slide.addShape(pres.shapes.RECTANGLE, { x: 0.00, y: 0, w: 3.33, h: 0.06, fill: { color: BLUE }, line: { type: "none" } });
  slide.addShape(pres.shapes.RECTANGLE, { x: 3.33, y: 0, w: 3.33, h: 0.06, fill: { color: RED }, line: { type: "none" } });
  slide.addShape(pres.shapes.RECTANGLE, { x: 6.67, y: 0, w: 3.33, h: 0.06, fill: { color: YELLOW }, line: { type: "none" } });
  slide.addShape(pres.shapes.RECTANGLE, { x: 10.00, y: 0, w: 3.33, h: 0.06, fill: { color: GREEN }, line: { type: "none" } });

  // Top-right page box
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 11.5, y: 0.30, w: 1.6, h: 0.35,
    fill: { color: WHITE }, line: { color: BORDER, width: 0.5 }
  });
  slide.addText(`${pageNum} / ${totalPages}`, {
    x: 11.5, y: 0.30, w: 1.6, h: 0.35, fontSize: 10, color: INDIGO,
    fontFace: "Calibri", bold: true, align: "center", valign: "middle", margin: 0
  });

  // Footer
  slide.addText("Christopher Hoole  |  christopherhoole.com  |  Confidential", {
    x: 0.6, y: 7.15, w: 8, h: 0.3,
    fontSize: 9, color: GREY, fontFace: "Calibri", valign: "middle", margin: 0
  });
  try {
    slide.addImage({ path: LOGO, x: 11.5, y: 7.05, w: 1.6, h: 0.4, sizing: { type: "contain", w: 1.6, h: 0.4 } });
  } catch (e) {}
  slide.addText(String(pageNum), {
    x: 10.9, y: 7.15, w: 0.5, h: 0.3, fontSize: 9, color: GREY,
    fontFace: "Calibri", align: "right", valign: "middle", margin: 0
  });
}

function addSlideTitle(slide, title, subtitle) {
  slide.addText(title, {
    x: 0.60, y: 0.30, w: 10.5, h: 0.50, fontSize: 28, color: INDIGO,
    fontFace: "Calibri", bold: true, margin: 0
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.60, y: 0.85, w: 10.5, h: 0.30, fontSize: 12, color: GREY,
      fontFace: "Calibri", italic: true, margin: 0
    });
  }
}

// Big stat card w/ left accent bar (matches pitch deck style)
function statCard(slide, x, y, w, h, value, label, accent) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h, fill: { color: CARD_BG }, line: { color: BORDER, width: 0.5 }
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w: 0.06, h, fill: { color: accent || INDIGO }, line: { type: "none" }
  });
  slide.addText(value, {
    x: x + 0.2, y: y + 0.1, w: w - 0.3, h: h * 0.55, fontSize: 28, color: INDIGO,
    fontFace: "Calibri", bold: true, margin: 0, valign: "bottom"
  });
  slide.addText(label, {
    x: x + 0.2, y: y + h * 0.6, w: w - 0.3, h: h * 0.35, fontSize: 11, color: DARK,
    fontFace: "Calibri", bold: true, margin: 0, valign: "top"
  });
}

const TOTAL = 11;

// ============ SLIDE 1: COVER ============
{
  const s = pres.addSlide();
  s.background = { color: WHITE };

  // 4-color stripe (keep consistent)
  s.addShape(pres.shapes.RECTANGLE, { x: 0.00, y: 0, w: 3.33, h: 0.06, fill: { color: BLUE }, line: { type: "none" } });
  s.addShape(pres.shapes.RECTANGLE, { x: 3.33, y: 0, w: 3.33, h: 0.06, fill: { color: RED }, line: { type: "none" } });
  s.addShape(pres.shapes.RECTANGLE, { x: 6.67, y: 0, w: 3.33, h: 0.06, fill: { color: YELLOW }, line: { type: "none" } });
  s.addShape(pres.shapes.RECTANGLE, { x: 10.00, y: 0, w: 3.33, h: 0.06, fill: { color: GREEN }, line: { type: "none" } });

  // Left: title block
  s.addText("WEEKLY PERFORMANCE REPORT", {
    x: 0.60, y: 1.1, w: 8, h: 0.35, fontSize: 11, color: GREY, fontFace: "Calibri",
    bold: true, charSpacing: 4, margin: 0
  });

  s.addText("Week 1", {
    x: 0.60, y: 1.5, w: 8, h: 1.2, fontSize: 72, color: INDIGO, fontFace: "Calibri",
    bold: true, margin: 0
  });
  s.addText("Account Overhaul  |  Foundation Build", {
    x: 0.60, y: 2.8, w: 9, h: 0.5, fontSize: 22, color: DARK, fontFace: "Calibri", margin: 0
  });

  // Divider
  s.addShape(pres.shapes.LINE, { x: 0.60, y: 3.55, w: 3.5, h: 0, line: { color: INDIGO, width: 2 } });

  s.addText("Dental by Design  |  Prodent Group", {
    x: 0.60, y: 3.7, w: 10, h: 0.4, fontSize: 16, color: INDIGO, fontFace: "Calibri",
    bold: true, margin: 0
  });
  s.addText("13 April – 17 April 2026", {
    x: 0.60, y: 4.15, w: 10, h: 0.35, fontSize: 14, color: GREY, fontFace: "Calibri", margin: 0
  });

  // Key numbers strip
  const yStrip = 5.1;
  const hdr = [
    { v: "£8,462", l: "Total spend", c: BLUE },
    { v: "87", l: "Qualified leads", c: GREEN },
    { v: "4", l: "Patient enquiries", c: YELLOW },
    { v: "£97", l: "Cost per lead", c: INDIGO }
  ];
  hdr.forEach((h, i) => {
    const cx = 0.60 + i * 3.10;
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: yStrip, w: 2.85, h: 1.2, fill: { color: WHITE }, line: { color: BORDER, width: 1 }
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: yStrip, w: 0.06, h: 1.2, fill: { color: h.c }, line: { type: "none" }
    });
    s.addText(h.v, {
      x: cx + 0.2, y: yStrip + 0.1, w: 2.5, h: 0.65, fontSize: 28, color: INDIGO,
      fontFace: "Calibri", bold: true, margin: 0, valign: "bottom"
    });
    s.addText(h.l, {
      x: cx + 0.2, y: yStrip + 0.75, w: 2.5, h: 0.4, fontSize: 11, color: DARK,
      fontFace: "Calibri", margin: 0
    });
  });

  // Author row
  s.addText("Christopher Hoole", {
    x: 0.60, y: 6.65, w: 8, h: 0.3, fontSize: 13, color: INDIGO, fontFace: "Calibri",
    bold: true, margin: 0
  });
  s.addText("Google Ads Specialist  |  christopherhoole.com", {
    x: 0.60, y: 6.95, w: 8, h: 0.3, fontSize: 11, color: GREY, fontFace: "Calibri", margin: 0
  });
  try {
    s.addImage({ path: LOGO, x: 11.2, y: 6.65, w: 2, h: 0.55, sizing: { type: "contain", w: 2, h: 0.55 } });
  } catch (e) {}
}

// ============ SLIDE 2: EXECUTIVE SUMMARY ============
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  addChrome(s, 2, TOTAL);
  addSlideTitle(s, "Executive Summary", "Week 1 headlines — a foundation week");

  // Top 4 stats
  statCard(s, 0.60, 1.30, 2.80, 1.05, "£8,462", "Total Spend", BLUE);
  statCard(s, 3.70, 1.30, 2.80, 1.05, "87", "Dengro Leads", GREEN);
  statCard(s, 6.80, 1.30, 2.80, 1.05, "4", "Patient Enquiries", YELLOW);
  statCard(s, 9.90, 1.30, 2.80, 1.05, "£97", "Cost / Lead", INDIGO);

  // Summary title
  s.addText("Week 1 at a Glance", {
    x: 0.60, y: 2.60, w: 12.1, h: 0.35, fontSize: 14, color: INDIGO, fontFace: "Calibri",
    bold: true, charSpacing: 2, margin: 0
  });

  // Content: What I delivered, Early signal, What's next — 3-column layout
  const y = 3.10;
  const h = 3.50;

  // Column 1: What I delivered
  s.addShape(pres.shapes.RECTANGLE, { x: 0.60, y, w: 4.00, h, fill: { color: CARD_BG }, line: { color: BORDER, width: 0.5 } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.60, y, w: 4.00, h: 0.05, fill: { color: BLUE }, line: { type: "none" } });
  s.addText("WHAT I DELIVERED", {
    x: 0.80, y: y + 0.20, w: 3.60, h: 0.30, fontSize: 10, color: BLUE,
    fontFace: "Calibri", bold: true, charSpacing: 3, margin: 0
  });
  s.addText([
    { text: "4,700+ negatives", options: { bold: true, color: INDIGO } },
    { text: " structured into 11 shared lists", options: { color: DARK }, breakLine: true },
    { text: "Brand campaign ", options: { bold: true, color: INDIGO } },
    { text: "rebuilt on tIS 90% / £1.50 max CPC", options: { color: DARK }, breakLine: true },
    { text: "Dental Implants Intent ", options: { bold: true, color: INDIGO } },
    { text: "re-engineered — 25 ad groups, 75 RSAs", options: { color: DARK }, breakLine: true },
    { text: "PMax ", options: { bold: true, color: INDIGO } },
    { text: "switched to Target CPA £60", options: { color: DARK }, breakLine: true },
    { text: "173 DBD-blocking ", options: { bold: true, color: INDIGO } },
    { text: "terms caught + removed", options: { color: DARK }, breakLine: true },
    { text: "63 live RSAs ", options: { bold: true, color: INDIGO } },
    { text: "audited toward Excellent", options: { color: DARK } }
  ], {
    x: 0.80, y: y + 0.60, w: 3.60, h: 2.75, fontSize: 11, fontFace: "Calibri",
    color: DARK, margin: 0, paraSpaceAfter: 4
  });

  // Column 2: Early signal
  s.addShape(pres.shapes.RECTANGLE, { x: 4.75, y, w: 4.00, h, fill: { color: CARD_BG }, line: { color: BORDER, width: 0.5 } });
  s.addShape(pres.shapes.RECTANGLE, { x: 4.75, y, w: 4.00, h: 0.05, fill: { color: GREEN }, line: { type: "none" } });
  s.addText("EARLY SIGNAL", {
    x: 4.95, y: y + 0.20, w: 3.60, h: 0.30, fontSize: 10, color: GREEN,
    fontFace: "Calibri", bold: true, charSpacing: 3, margin: 0
  });
  s.addText([
    { text: "Brand CPC", options: { bold: true, color: INDIGO } },
    { text: " £3.29 → £2.16 (-35%)", options: { color: DARK }, breakLine: true },
    { text: "Brand CTR", options: { bold: true, color: INDIGO } },
    { text: " 35.14% vs 26% prior avg", options: { color: DARK }, breakLine: true },
    { text: "Brand Impression Share", options: { bold: true, color: INDIGO } },
    { text: " 100% top of page", options: { color: DARK }, breakLine: true },
    { text: "PMax best day", options: { bold: true, color: INDIGO } },
    { text: " £25 CPA (Wed 15 Apr)", options: { color: DARK }, breakLine: true },
    { text: "Search terms quality", options: { bold: true, color: INDIGO } },
    { text: " zero NHS/abroad junk this week", options: { color: DARK }, breakLine: true },
    { text: "DII", options: { bold: true, color: INDIGO } },
    { text: " in Google Learning mode — clean read in Week 2-3", options: { color: DARK } }
  ], {
    x: 4.95, y: y + 0.60, w: 3.60, h: 2.75, fontSize: 11, fontFace: "Calibri", margin: 0, paraSpaceAfter: 4
  });

  // Column 3: What's next
  s.addShape(pres.shapes.RECTANGLE, { x: 8.90, y, w: 3.80, h, fill: { color: CARD_BG }, line: { color: BORDER, width: 0.5 } });
  s.addShape(pres.shapes.RECTANGLE, { x: 8.90, y, w: 3.80, h: 0.05, fill: { color: YELLOW }, line: { type: "none" } });
  s.addText("WHAT'S NEXT", {
    x: 9.10, y: y + 0.20, w: 3.40, h: 0.30, fontSize: 10, color: "C49600",
    fontFace: "Calibri", bold: true, charSpacing: 3, margin: 0
  });
  s.addText([
    { text: "Mon 20 Apr  ", options: { bold: true, color: INDIGO } },
    { text: "Conversion tracking audit", options: { color: DARK }, breakLine: true },
    { text: "Tue 21 Apr  ", options: { bold: true, color: INDIGO } },
    { text: "AG22-25 Ad Strength", options: { color: DARK }, breakLine: true },
    { text: "Wed-Thu  ", options: { bold: true, color: INDIGO } },
    { text: "PMax asset rebuild", options: { color: DARK }, breakLine: true },
    { text: "Fri 24 Apr  ", options: { bold: true, color: INDIGO } },
    { text: "Cosmetic campaign scoping + Week 2 report", options: { color: DARK }, breakLine: true },
    { text: " ", options: { breakLine: true } },
    { text: "Awaiting your decision on two items: ", options: { bold: true, color: RED } },
    { text: "consultation pricing and the \"25+ years\" claim. See slide 10.", options: { color: DARK } }
  ], {
    x: 9.10, y: y + 0.60, w: 3.40, h: 2.75, fontSize: 11, fontFace: "Calibri", margin: 0, paraSpaceAfter: 4
  });
}

// ============ SLIDE 3: WORK DELIVERED ============
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  addChrome(s, 3, TOTAL);
  addSlideTitle(s, "Work Delivered", "Day-by-day, 14-17 April (client signed Mon 14 Apr)");

  // Intro line
  s.addText("Four active working days — ~20 hours of deep structural rebuild", {
    x: 0.60, y: 1.30, w: 12.1, h: 0.35, fontSize: 13, color: INDIGO, fontFace: "Calibri",
    bold: true, margin: 0
  });

  // Rows: Day / Focus / Output
  const headerOpt = { bold: true, color: WHITE, fontSize: 11, fill: { color: INDIGO }, valign: "middle", fontFace: "Calibri" };
  const dayOpt = { bold: true, color: INDIGO, fontSize: 12, valign: "middle", fontFace: "Calibri" };
  const focusOpt = { bold: true, color: DARK, fontSize: 11, valign: "middle", fontFace: "Calibri" };
  const outputOpt = { color: DARK, fontSize: 10, valign: "middle", fontFace: "Calibri" };

  const rows = [
    [
      { text: "DAY", options: { ...headerOpt, align: "left" } },
      { text: "FOCUS", options: { ...headerOpt, align: "left" } },
      { text: "OUTPUT", options: { ...headerOpt, align: "left" } }
    ],
    [
      { text: "Tue 14 Apr", options: dayOpt },
      { text: "Negative keyword overhaul", options: focusOpt },
      { text: "4,700+ negatives restructured into 11 organised shared lists — competitors, abroad, wrong locations, non-DBD services, brand-specific research, and cheap/NHS-seeker traffic.", options: outputOpt }
    ],
    [
      { text: "Wed 15 Apr", options: dayOpt },
      { text: "Brand rebuild + account-wide", options: focusOpt },
      { text: "Brand: Target Impression Share 90% / £1.50 max CPC, 266 London postcodes, 42-cell ad schedule, 2 new RSAs. Account: auto-apply disabled, PMax → Target CPA £60, DII → Target CPA £75, 8 new RSAs, 356 more negatives.", options: outputOpt }
    ],
    [
      { text: "Thu 16 Apr", options: dayOpt },
      { text: "Dental Implants Intent rebuild", options: focusOpt },
      { text: "20 new ad groups built, 537 keywords added, 60 RSAs written. 4 legacy under-performing ad groups paused (£99+ CPA). Ad structure mapped to patient intent: service, cost, finance, location, quality.", options: outputOpt }
    ],
    [
      { text: "Fri 17 Apr", options: dayOpt },
      { text: "Final ad groups + full audit", options: focusOpt },
      { text: "AG21-25 built (5 ad groups, 15 RSAs). 1,786 daily search queries reviewed. 173 DBD-blocking terms caught and removed across all 11 negative lists. Ad Strength audit across 63 live RSAs to push toward Excellent.", options: outputOpt }
    ]
  ];

  s.addTable(rows, {
    x: 0.60, y: 1.85, w: 12.1,
    colW: [1.4, 2.8, 7.9],
    rowH: [0.40, 1.00, 1.15, 1.00, 1.15],
    border: { pt: 0.5, color: BORDER }
  });
}

// ============ SLIDE 4: THE FOUNDATION ============
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  addChrome(s, 4, TOTAL);
  addSlideTitle(s, "The Foundation", "What's now in place after this week's rebuild");

  // 5 stat cards across
  const cardY = 1.40;
  const cardW = 2.40;
  const gap = 0.10;
  const startX = 0.60;

  const cards = [
    { v: "5,000+", l: "Negative Keywords", s: "11 structured lists", c: INDIGO },
    { v: "546", l: "Positive Keywords", s: "Brand + DII, structured", c: BLUE },
    { v: "75", l: "New RSAs", s: "1,050 headlines / 280 descs", c: GREEN },
    { v: "25", l: "DII Ad Groups", s: "patient-intent themed", c: YELLOW },
    { v: "810", l: "Geo Targets", s: "Gtr London, 3 campaigns", c: RED }
  ];

  cards.forEach((c, i) => {
    const x = startX + i * (cardW + gap);
    const h = 1.40;
    s.addShape(pres.shapes.RECTANGLE, { x, y: cardY, w: cardW, h, fill: { color: CARD_BG }, line: { color: BORDER, width: 0.5 } });
    s.addShape(pres.shapes.RECTANGLE, { x, y: cardY, w: 0.06, h, fill: { color: c.c }, line: { type: "none" } });
    s.addText(c.v, {
      x: x + 0.2, y: cardY + 0.1, w: cardW - 0.3, h: 0.65, fontSize: 30, color: INDIGO,
      fontFace: "Calibri", bold: true, margin: 0, valign: "bottom"
    });
    s.addText(c.l, {
      x: x + 0.2, y: cardY + 0.80, w: cardW - 0.3, h: 0.30, fontSize: 11, color: DARK,
      fontFace: "Calibri", bold: true, margin: 0
    });
    s.addText(c.s, {
      x: x + 0.2, y: cardY + 1.08, w: cardW - 0.3, h: 0.25, fontSize: 9, color: GREY,
      fontFace: "Calibri", margin: 0
    });
  });

  // Before / After comparison
  s.addText("FROM LEGACY PATCHWORK → CLEAN, STRUCTURED ACCOUNT", {
    x: 0.60, y: 3.15, w: 12.1, h: 0.35, fontSize: 11, color: INDIGO, fontFace: "Calibri",
    bold: true, charSpacing: 3, margin: 0
  });

  const headerOpt = { bold: true, color: WHITE, fontSize: 11, fill: { color: INDIGO }, valign: "middle", fontFace: "Calibri", align: "left" };
  const labelOpt = { bold: true, color: INDIGO, fontSize: 11, valign: "middle", fontFace: "Calibri" };
  const beforeOpt = { color: DARK, fontSize: 11, valign: "middle", fontFace: "Calibri" };
  const afterOpt = { color: "117534", fontSize: 11, bold: true, valign: "middle", fontFace: "Calibri" };

  const cmpRows = [
    [
      { text: "AREA", options: headerOpt },
      { text: "BEFORE (pre-engagement)", options: headerOpt },
      { text: "AFTER (Fri 17 Apr)", options: headerOpt }
    ],
    [
      { text: "Campaign count", options: labelOpt },
      { text: "47 campaigns (only 4 active, 43 legacy)", options: beforeOpt },
      { text: "3 active, structured campaigns", options: afterOpt }
    ],
    [
      { text: "Bid strategy (DII + PMax)", options: labelOpt },
      { text: "Max Conversion Value (tROAS) — arbitrary £300 values", options: beforeOpt },
      { text: "Target CPA £75 (DII) / £60 (PMax) — real cost control", options: afterOpt }
    ],
    [
      { text: "Negative keywords", options: labelOpt },
      { text: "Unstructured broad-match, 2 legacy lists, DBD-blocking", options: beforeOpt },
      { text: "11 organised lists, 5,000+ negatives, DBD-safe", options: afterOpt }
    ],
    [
      { text: "DII ad group structure", options: labelOpt },
      { text: "4 legacy ad groups averaging £99+ CPA", options: beforeOpt },
      { text: "25 ad groups mapped to patient intent", options: afterOpt }
    ],
    [
      { text: "Geo targeting", options: labelOpt },
      { text: "25-mile radius (Reading → Romford), 1 rogue Pakistan target", options: beforeOpt },
      { text: "270 Greater London postcodes, 4-tier structure", options: afterOpt }
    ]
  ];

  s.addTable(cmpRows, {
    x: 0.60, y: 3.55, w: 12.1,
    colW: [2.5, 5.3, 4.3],
    rowH: [0.35, 0.50, 0.55, 0.50, 0.50, 0.55],
    border: { pt: 0.5, color: BORDER }
  });
}

// ============ SLIDE 5: BRAND ============
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  addChrome(s, 5, TOTAL);
  addSlideTitle(s, "Brand Campaign", "Tighter targeting is already showing");

  // Left: 3 stats vertically
  statCard(s, 0.60, 1.30, 3.40, 1.55, "-35%", "Avg CPC vs March", GREEN);
  s.addText("£3.29 → £2.16", {
    x: 0.80, y: 2.55, w: 3.1, h: 0.3, fontSize: 11, color: GREY, fontFace: "Calibri", margin: 0
  });
  statCard(s, 0.60, 3.00, 3.40, 1.55, "35.14%", "Click-Through Rate", GREEN);
  s.addText("vs 26% March avg", {
    x: 0.80, y: 4.25, w: 3.1, h: 0.3, fontSize: 11, color: GREY, fontFace: "Calibri", margin: 0
  });
  statCard(s, 0.60, 4.70, 3.40, 1.55, "100%", "Impression Share", GREEN);
  s.addText("top of page, absolute top", {
    x: 0.80, y: 5.95, w: 3.1, h: 0.3, fontSize: 11, color: GREY, fontFace: "Calibri", margin: 0
  });

  // Right: chart
  s.addChart(pres.charts.LINE, [{
    name: "Avg CPC (£)",
    labels: ["23 Feb", "2 Mar", "9 Mar", "16 Mar", "23 Mar", "30 Mar", "6 Apr", "13 Apr"],
    values: [3.09, 2.41, 3.49, 4.00, 3.24, 2.31, 2.90, 2.16]
  }], {
    x: 4.25, y: 1.30, w: 8.45, h: 5.15,
    showTitle: true, title: "Brand Avg CPC — 8 week trend",
    titleFontSize: 13, titleColor: INDIGO, titleFontFace: "Calibri", titleBold: true,
    lineDataSymbol: "circle", lineDataSymbolSize: 8,
    lineSize: 3,
    chartColors: [BLUE],
    showValue: true,
    dataLabelFontSize: 10, dataLabelFormatCode: "£0.00",
    dataLabelColor: INDIGO, dataLabelFontBold: true,
    catAxisLabelFontSize: 10, catAxisLabelFontFace: "Calibri",
    valAxisLabelFontSize: 10, valAxisLabelFontFace: "Calibri",
    valAxisLabelFormatCode: "£0.00",
    valAxisMinVal: 0, valAxisMaxVal: 5,
    showLegend: false,
    plotArea: { fill: { color: GREY_LIGHT } }
  });
}

// ============ SLIDE 6: PMAX ============
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  addChrome(s, 6, TOTAL);
  addSlideTitle(s, "Performance Max", "Delivering the bulk of qualified leads");

  // Top row 4 stats
  statCard(s, 0.60, 1.30, 2.95, 1.30, "78.5", "Dengro Leads", GREEN);
  statCard(s, 3.70, 1.30, 2.95, 1.30, "3", "Patient Enquiries", YELLOW);
  statCard(s, 6.80, 1.30, 2.95, 1.30, "£73", "CPA (primary)", BLUE);
  statCard(s, 9.90, 1.30, 2.85, 1.30, "£25", "Best-day CPA", INDIGO);

  s.addText("£86 prior week → £73 this week. Wednesday 15 April hit £25 CPA (best single-day in the account) after the Target CPA switch.", {
    x: 0.60, y: 2.75, w: 12.1, h: 0.4, fontSize: 11, color: GREY, fontFace: "Calibri", italic: true, margin: 0
  });

  // Two columns: What changed (left) / Flagged for Week 2 (right)
  const y = 3.30;
  const h = 3.25;

  s.addShape(pres.shapes.RECTANGLE, { x: 0.60, y, w: 5.95, h, fill: { color: CARD_BG }, line: { color: BORDER, width: 0.5 } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.60, y, w: 5.95, h: 0.05, fill: { color: GREEN }, line: { type: "none" } });
  s.addText("WHAT CHANGED THIS WEEK", {
    x: 0.80, y: y + 0.18, w: 5.55, h: 0.3, fontSize: 10, color: GREEN,
    fontFace: "Calibri", bold: true, charSpacing: 3, margin: 0
  });
  s.addText([
    { text: "Bid strategy switched ", options: { bold: true, color: INDIGO } },
    { text: "Max Conv Value (tROAS 80%) → Target CPA £60", options: { color: DARK }, breakLine: true },
    { text: "3 dangerous negatives removed ", options: { bold: true, color: INDIGO } },
    { text: "single-word exacts blocking DBD postcodes (stratford, southall, twickenham)", options: { color: DARK }, breakLine: true },
    { text: "Geo + ad schedule aligned ", options: { bold: true, color: INDIGO } },
    { text: "270 postcodes, 42-cell schedule", options: { color: DARK }, breakLine: true },
    { text: "Shared negative lists cleaned ", options: { bold: true, color: INDIGO } },
    { text: "zero NHS/cheap/abroad junk in search terms this week", options: { color: DARK } }
  ], {
    x: 0.80, y: y + 0.55, w: 5.55, h: 2.5, fontSize: 11, fontFace: "Calibri", margin: 0, paraSpaceAfter: 6
  });

  s.addShape(pres.shapes.RECTANGLE, { x: 6.75, y, w: 6.00, h, fill: { color: CARD_BG }, line: { color: BORDER, width: 0.5 } });
  s.addShape(pres.shapes.RECTANGLE, { x: 6.75, y, w: 6.00, h: 0.05, fill: { color: YELLOW }, line: { type: "none" } });
  s.addText("FLAGGED FOR WEEK 2", {
    x: 6.95, y: y + 0.18, w: 5.60, h: 0.3, fontSize: 10, color: "B88900",
    fontFace: "Calibri", bold: true, charSpacing: 3, margin: 0
  });
  s.addText([
    { text: "Asset groups limited by policy ", options: { bold: true, color: INDIGO } },
    { text: "Google still flags \"most asset groups limited by policy\" — PMax is not running at full potential until this is resolved.", options: { color: DARK }, breakLine: true },
    { text: " ", options: { breakLine: true } },
    { text: "Planned fix: ", options: { bold: true, color: INDIGO } },
    { text: "Full asset rebuild Wed-Thu Week 2. Strip unverified claims (\"99.12% success\", \"Voted #1 UK\", \"Save 60%\") and replace with premium-positioned, verifiable assets aligned to the £1,695-£15,990 service range.", options: { color: DARK }, breakLine: true },
    { text: " ", options: { breakLine: true } },
    { text: "Expected upside: ", options: { bold: true, color: GREEN } },
    { text: "lifting policy limits typically unlocks 2-3× reach at the same CPA.", options: { color: DARK } }
  ], {
    x: 6.95, y: y + 0.55, w: 5.60, h: 2.5, fontSize: 11, fontFace: "Calibri", margin: 0, paraSpaceAfter: 6
  });
}

// ============ SLIDE 7: DII (Search Intent) ============
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  addChrome(s, 7, TOTAL);
  addSlideTitle(s, "Dental Implants Intent", "In Google Learning mode — by design");

  // Top stats
  statCard(s, 0.60, 1.30, 2.95, 1.30, "25", "New Ad Groups", BLUE);
  statCard(s, 3.70, 1.30, 2.95, 1.30, "75", "RSAs Live", BLUE);
  statCard(s, 6.80, 1.30, 2.95, 1.30, "~650", "Keywords", BLUE);
  statCard(s, 9.90, 1.30, 2.85, 1.30, "63%", "Impression Share", GREEN);

  // Narrative
  const y = 2.90;
  s.addShape(pres.shapes.RECTANGLE, { x: 0.60, y, w: 12.1, h: 3.85, fill: { color: CARD_BG }, line: { color: BORDER, width: 0.5 } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.60, y, w: 12.1, h: 0.05, fill: { color: BLUE }, line: { type: "none" } });
  s.addText("WHY WEEK 1 CPA IS NOT THE CLEAN READ", {
    x: 0.80, y: y + 0.2, w: 11.7, h: 0.35, fontSize: 11, color: BLUE, fontFace: "Calibri",
    bold: true, charSpacing: 3, margin: 0
  });

  s.addText([
    { text: "The campaign was fully restructured mid-week (Tue-Thu):", options: { color: DARK, bold: true }, breakLine: true },
    { text: "•   ", options: { color: BLUE, bold: true } },
    { text: "20 new ad groups built + 4 legacy groups paused", options: { color: DARK }, breakLine: true },
    { text: "•   ", options: { color: BLUE, bold: true } },
    { text: "Bid strategy switched to Target CPA £75", options: { color: DARK }, breakLine: true },
    { text: "•   ", options: { color: BLUE, bold: true } },
    { text: "Keyword base rebuilt from the ground up (537 new keywords)", options: { color: DARK }, breakLine: true },
    { text: "•   ", options: { color: BLUE, bold: true } },
    { text: "On Fri 17 Apr, AG21-25 added — bringing the structure to 25 ad groups", options: { color: DARK }, breakLine: true },
    { text: " ", options: { breakLine: true } },
    { text: "Google requires 14-21 days to rebalance bids against a restructured campaign. ", options: { bold: true, color: INDIGO } },
    { text: "Week 1 CPA blends 1 day of the old structure with 4 days of Google's learning phase. ", options: { color: DARK } },
    { text: "Week 2-3 is when we get the first clean performance read.", options: { bold: true, color: INDIGO }, breakLine: true },
    { text: " ", options: { breakLine: true } },
    { text: "Early positive: ", options: { bold: true, color: GREEN } },
    { text: "Wednesday 15 April delivered 3 primary conversions at £122 CPA — the first sign the new structure is converting. ", options: { color: DARK } },
    { text: "The DII impression share climbed to 76% on Thursday and 58% on Friday, confirming the new ad groups are winning their intended auctions.", options: { color: DARK } }
  ], {
    x: 0.80, y: y + 0.60, w: 11.7, h: 3.10, fontSize: 11, fontFace: "Calibri", color: DARK, margin: 0, paraSpaceAfter: 2
  });
}

// ============ SLIDE 8: REAL BUSINESS OUTCOMES ============
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  addChrome(s, 8, TOTAL);
  addSlideTitle(s, "The Numbers That Matter", "Real business outcomes — Dengro CRM data");

  // Left hero box
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.60, y: 1.30, w: 6.00, h: 2.50, fill: { color: INDIGO }, line: { type: "none" }
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.60, y: 1.30, w: 6.00, h: 0.08, fill: { color: GREEN }, line: { type: "none" } });
  s.addText("87", {
    x: 0.80, y: 1.50, w: 5.60, h: 1.3, fontSize: 88, color: WHITE, fontFace: "Calibri", bold: true, margin: 0
  });
  s.addText("Qualified Dengro Leads", {
    x: 0.80, y: 2.85, w: 5.60, h: 0.4, fontSize: 18, color: GREEN, fontFace: "Calibri", bold: true, margin: 0
  });
  s.addText("at £97 per qualified lead across all campaigns", {
    x: 0.80, y: 3.30, w: 5.60, h: 0.4, fontSize: 12, color: CARD_BG, fontFace: "Calibri", margin: 0
  });

  // Right hero box
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.75, y: 1.30, w: 6.00, h: 2.50, fill: { color: YELLOW }, line: { type: "none" }
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.75, y: 1.30, w: 6.00, h: 0.08, fill: { color: INDIGO }, line: { type: "none" } });
  s.addText("4", {
    x: 6.95, y: 1.50, w: 5.60, h: 1.3, fontSize: 88, color: INDIGO, fontFace: "Calibri", bold: true, margin: 0
  });
  s.addText("Patient Enquiries (Bookings + Purchases)", {
    x: 6.95, y: 2.85, w: 5.60, h: 0.4, fontSize: 18, color: INDIGO, fontFace: "Calibri", bold: true, margin: 0
  });
  s.addText("£2,115 per enquiry — strong vs implant £1,695-£15,990 LTV", {
    x: 6.95, y: 3.30, w: 5.60, h: 0.4, fontSize: 12, color: "1A1A1A", fontFace: "Calibri", margin: 0
  });

  // Bottom table: breakdown
  const headerOpt = { bold: true, color: WHITE, fontSize: 11, fill: { color: INDIGO }, valign: "middle", fontFace: "Calibri" };
  const cellOpt = { color: DARK, fontSize: 11, valign: "middle", fontFace: "Calibri" };
  const boldOpt = { color: INDIGO, bold: true, fontSize: 11, valign: "middle", fontFace: "Calibri" };

  const rows = [
    [
      { text: "CAMPAIGN", options: headerOpt },
      { text: "DENGRO LEADS", options: { ...headerOpt, align: "center" } },
      { text: "PATIENT ENQUIRIES", options: { ...headerOpt, align: "center" } },
      { text: "SPEND", options: { ...headerOpt, align: "center" } },
      { text: "£ / LEAD", options: { ...headerOpt, align: "center" } },
      { text: "£ / ENQUIRY", options: { ...headerOpt, align: "center" } }
    ],
    [
      { text: "Brand", options: boldOpt },
      { text: "2", options: { ...cellOpt, align: "center" } },
      { text: "0", options: { ...cellOpt, align: "center" } },
      { text: "£280", options: { ...cellOpt, align: "center" } },
      { text: "£140", options: { ...cellOpt, align: "center" } },
      { text: "—", options: { ...cellOpt, align: "center" } }
    ],
    [
      { text: "Dental Implants Intent", options: boldOpt },
      { text: "6.5", options: { ...cellOpt, align: "center" } },
      { text: "1", options: { ...cellOpt, align: "center" } },
      { text: "£2,222", options: { ...cellOpt, align: "center" } },
      { text: "£342", options: { ...cellOpt, align: "center" } },
      { text: "£2,222", options: { ...cellOpt, align: "center" } }
    ],
    [
      { text: "Performance Max", options: boldOpt },
      { text: "78.5", options: { ...cellOpt, align: "center" } },
      { text: "3", options: { ...cellOpt, align: "center" } },
      { text: "£5,960", options: { ...cellOpt, align: "center" } },
      { text: "£76", options: { ...cellOpt, align: "center" } },
      { text: "£1,987", options: { ...cellOpt, align: "center" } }
    ],
    [
      { text: "WEEK 1 TOTAL", options: { ...boldOpt, fill: { color: CARD_BG }, fontSize: 12 } },
      { text: "87", options: { ...boldOpt, align: "center", fill: { color: CARD_BG }, fontSize: 12 } },
      { text: "4", options: { ...boldOpt, align: "center", fill: { color: CARD_BG }, fontSize: 12 } },
      { text: "£8,462", options: { ...boldOpt, align: "center", fill: { color: CARD_BG }, fontSize: 12 } },
      { text: "£97", options: { ...boldOpt, align: "center", fill: { color: CARD_BG }, fontSize: 12 } },
      { text: "£2,115", options: { ...boldOpt, align: "center", fill: { color: CARD_BG }, fontSize: 12 } }
    ]
  ];

  s.addTable(rows, {
    x: 0.60, y: 4.10, w: 12.15,
    colW: [3.5, 1.7, 2.15, 1.6, 1.6, 1.6],
    rowH: [0.38, 0.42, 0.42, 0.42, 0.48],
    border: { pt: 0.5, color: BORDER }
  });
}

// ============ SLIDE 9: 8-WEEK CONTEXT ============
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  addChrome(s, 9, TOTAL);
  addSlideTitle(s, "Eight-Week Context", "Where the account sits vs prior 7 weeks");

  // Chart: spend
  s.addChart(pres.charts.BAR, [{
    name: "Weekly Spend (£)",
    labels: ["23 Feb", "2 Mar", "9 Mar", "16 Mar", "23 Mar", "30 Mar", "6 Apr", "13 Apr"],
    values: [17101, 14475, 8115, 13173, 11558, 9997, 10291, 8462]
  }], {
    x: 0.60, y: 1.30, w: 6.00, h: 2.55,
    barDir: "col",
    showTitle: true, title: "Weekly Spend (£)",
    titleFontSize: 12, titleColor: INDIGO, titleFontFace: "Calibri", titleBold: true,
    chartColors: [BLUE],
    showValue: true, dataLabelFontSize: 8, dataLabelFormatCode: "£#,##0",
    dataLabelColor: INDIGO, dataLabelFontBold: true,
    catAxisLabelFontSize: 9, catAxisLabelFontFace: "Calibri",
    valAxisLabelFontSize: 9, valAxisLabelFontFace: "Calibri",
    valAxisLabelFormatCode: "£#,##0",
    showLegend: false
  });

  // Chart: conversions
  s.addChart(pres.charts.BAR, [{
    name: "Primary Conversions",
    labels: ["23 Feb", "2 Mar", "9 Mar", "16 Mar", "23 Mar", "30 Mar", "6 Apr", "13 Apr"],
    values: [229.5, 184.6, 115.7, 133.7, 239.2, 148.4, 134.1, 101.0]
  }], {
    x: 6.75, y: 1.30, w: 6.00, h: 2.55,
    barDir: "col",
    showTitle: true, title: "Primary Conversions",
    titleFontSize: 12, titleColor: INDIGO, titleFontFace: "Calibri", titleBold: true,
    chartColors: [GREEN],
    showValue: true, dataLabelFontSize: 9, dataLabelFormatCode: "0",
    dataLabelColor: INDIGO, dataLabelFontBold: true,
    catAxisLabelFontSize: 9, catAxisLabelFontFace: "Calibri",
    valAxisLabelFontSize: 9, valAxisLabelFontFace: "Calibri",
    showLegend: false
  });

  // Narrative block
  const y = 4.00;
  s.addShape(pres.shapes.RECTANGLE, { x: 0.60, y, w: 12.1, h: 2.75, fill: { color: CARD_BG }, line: { color: BORDER, width: 0.5 } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.60, y, w: 12.1, h: 0.05, fill: { color: INDIGO }, line: { type: "none" } });
  s.addText("READING THE CONTEXT", {
    x: 0.80, y: y + 0.2, w: 11.7, h: 0.35, fontSize: 11, color: INDIGO, fontFace: "Calibri",
    bold: true, charSpacing: 3, margin: 0
  });
  s.addText([
    { text: "Weekly spend was trimmed from ~£17K to £8.5K — ", options: { color: DARK } },
    { text: "intentional. ", options: { bold: true, color: INDIGO } },
    { text: "The previous setup was optimising toward arbitrary £300 booking values via Max Conv Value bidding. Switching to Target CPA + paused legacy campaigns tightened spend to converting traffic only.", options: { color: DARK }, breakLine: true },
    { text: " ", options: { breakLine: true } },
    { text: "Primary conversion volume dipped to 101 in Week 1 — ", options: { color: DARK } },
    { text: "expected. ", options: { bold: true, color: INDIGO } },
    { text: "The account is in Google Learning mode while the new bid strategy and ad group structure rebalance. All-conversions (including Dengro leads) reached 231 — our real business-signal metric.", options: { color: DARK }, breakLine: true },
    { text: " ", options: { breakLine: true } },
    { text: "Week 2-3 will show the true impact once Learning completes.", options: { bold: true, color: GREEN } }
  ], {
    x: 0.80, y: y + 0.55, w: 11.7, h: 2.1, fontSize: 11, fontFace: "Calibri", margin: 0, paraSpaceAfter: 2
  });
}

// ============ SLIDE 10: DECISIONS + WEEK 2 PLAN ============
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  addChrome(s, 10, TOTAL);
  addSlideTitle(s, "What's Next", "Two decisions needed + Week 2 plan");

  // Left: decisions
  s.addShape(pres.shapes.RECTANGLE, { x: 0.60, y: 1.30, w: 6.00, h: 5.45, fill: { color: WHITE }, line: { color: RED, width: 2 } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.60, y: 1.30, w: 6.00, h: 0.55, fill: { color: RED }, line: { type: "none" } });
  s.addText("2 DECISIONS NEED YOUR CALL", {
    x: 0.80, y: 1.30, w: 5.60, h: 0.55, fontSize: 12, color: WHITE, fontFace: "Calibri",
    bold: true, valign: "middle", charSpacing: 4, margin: 0
  });

  // Decision 1
  s.addText("1", {
    x: 0.80, y: 2.05, w: 0.6, h: 0.65, fontSize: 36, color: RED, fontFace: "Calibri", bold: true, margin: 0
  });
  s.addText("Consultation pricing", {
    x: 1.45, y: 2.10, w: 5.0, h: 0.45, fontSize: 16, color: INDIGO, fontFace: "Calibri", bold: true, margin: 0
  });
  s.addText([
    { text: "Ads currently say ", options: { color: DARK } },
    { text: "\"Free Consultation\"", options: { bold: true, color: INDIGO } },
    { text: ". Website says ", options: { color: DARK } },
    { text: "£95", options: { bold: true, color: RED } },
    { text: ". Need to align — free, £95, or tiered by service — so ads match reality and clear Google's misleading-pricing policy.", options: { color: DARK } }
  ], {
    x: 1.45, y: 2.55, w: 5.0, h: 1.20, fontSize: 11, fontFace: "Calibri", margin: 0
  });

  // Decision 2
  s.addText("2", {
    x: 0.80, y: 4.05, w: 0.6, h: 0.65, fontSize: 36, color: RED, fontFace: "Calibri", bold: true, margin: 0
  });
  s.addText("\"25+ Years\" experience claim", {
    x: 1.45, y: 4.10, w: 5.0, h: 0.45, fontSize: 16, color: INDIGO, fontFace: "Calibri", bold: true, margin: 0
  });
  s.addText([
    { text: "Ads reference ", options: { color: DARK } },
    { text: "\"25+ years\"", options: { bold: true, color: INDIGO } },
    { text: " — clinic founded 2010 (16 years). Clarify whether this refers to the principal's personal experience, combined team years, or something else. Ads will be updated to a verifiable claim.", options: { color: DARK } }
  ], {
    x: 1.45, y: 4.55, w: 5.0, h: 1.35, fontSize: 11, fontFace: "Calibri", margin: 0
  });

  s.addText("Awaiting your reply to refine ads in Week 2", {
    x: 0.80, y: 6.20, w: 5.60, h: 0.35, fontSize: 10, color: GREY, fontFace: "Calibri", italic: true, margin: 0
  });

  // Right: Week 2 plan
  s.addShape(pres.shapes.RECTANGLE, { x: 6.75, y: 1.30, w: 6.00, h: 5.45, fill: { color: INDIGO }, line: { type: "none" } });
  s.addShape(pres.shapes.RECTANGLE, { x: 6.75, y: 1.30, w: 6.00, h: 0.55, fill: { color: INDIGO_DEEP }, line: { type: "none" } });
  s.addText("WEEK 2 PLAN   (20 – 24 APRIL)", {
    x: 6.95, y: 1.30, w: 5.60, h: 0.55, fontSize: 12, color: YELLOW, fontFace: "Calibri",
    bold: true, valign: "middle", charSpacing: 4, margin: 0
  });

  const plan = [
    { day: "Mon 20 Apr", task: "End-to-end conversion tracking audit (priority — before any CPA decisions)" },
    { day: "Tue 21 Apr", task: "Resume Ad Strength audit on AG22-25 once Google approves them" },
    { day: "Wed 22 Apr", task: "Performance Max asset rebuild — lift the policy limit" },
    { day: "Thu 23 Apr", task: "Sitelink + callout + structured snippet extensions across all campaigns" },
    { day: "Fri 24 Apr", task: "Cosmetic Dentistry campaign scoping + Week 2 report" }
  ];
  let py = 2.05;
  plan.forEach(p => {
    s.addText(p.day, {
      x: 6.95, y: py, w: 5.60, h: 0.30, fontSize: 11, color: YELLOW, fontFace: "Calibri",
      bold: true, charSpacing: 2, margin: 0
    });
    s.addText(p.task, {
      x: 6.95, y: py + 0.28, w: 5.60, h: 0.55, fontSize: 11, color: WHITE, fontFace: "Calibri", margin: 0
    });
    py += 0.92;
  });
}

// ============ SLIDE 11: CLOSING ============
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  addChrome(s, 11, TOTAL);

  // Big framed block
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.60, y: 1.50, w: 12.1, h: 5.00, fill: { color: INDIGO }, line: { type: "none" }
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.60, y: 1.50, w: 12.1, h: 0.10, fill: { color: YELLOW }, line: { type: "none" }
  });

  s.addText("Questions?", {
    x: 0.90, y: 2.0, w: 11.5, h: 1.2, fontSize: 64, color: WHITE, fontFace: "Calibri",
    bold: true, margin: 0
  });
  s.addText("Happy to walk through any part of this report — or jump on a 20-minute call to align on Week 2 priorities.", {
    x: 0.90, y: 3.3, w: 11.5, h: 0.8, fontSize: 16, color: CARD_BG, fontFace: "Calibri", margin: 0
  });

  s.addShape(pres.shapes.LINE, { x: 0.90, y: 4.35, w: 3.5, h: 0, line: { color: YELLOW, width: 2 } });

  s.addText("Christopher Hoole  |  Google Ads Specialist", {
    x: 0.90, y: 4.55, w: 11.5, h: 0.35, fontSize: 14, color: WHITE, fontFace: "Calibri", bold: true, margin: 0
  });
  s.addText("christopherhoole.com  |  chrishoole101@gmail.com", {
    x: 0.90, y: 4.92, w: 11.5, h: 0.35, fontSize: 12, color: CARD_BG, fontFace: "Calibri", margin: 0
  });
}

// ============ WRITE FILE ============
const OUT = "C:/Users/User/Desktop/gads-data-layer/potential_clients/Inserta Dental/reports/DentalByDesign.co.uk - Week 1 Report 13-17 April 2026-v2.pptx";
pres.writeFile({ fileName: OUT }).then(f => console.log("Wrote: " + f));
