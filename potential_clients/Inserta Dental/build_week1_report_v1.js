// Dental by Design — Week 1 Report (13-17 April 2026)
// Christopher Hoole | Weekly performance report

const pptxgen = require("pptxgenjs");
const path = require("path");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
pres.author = "Christopher Hoole";
pres.title = "Dental by Design - Week 1 Report - 13-17 April 2026";

// ============ Colour palette ============
const NAVY = "1E2761";
const NAVY_DEEP = "131A42";
const ICE = "CADCFC";
const GOLD = "D4A843";
const WHITE = "FFFFFF";
const DARK = "1A1A1A";
const GREY = "6B7280";
const GREY_LIGHT = "E5E7EB";
const GREEN = "10B981";

// ============ Helpers ============
const LOGO = "C:/Users/User/Desktop/gads-data-layer/potential_clients/Inserta Dental/act_logo_official.png";

function addFooter(slide, pageNum) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 7.2, w: 13.3, h: 0.3, fill: { color: NAVY }, line: { type: "none" }
  });
  slide.addText("Christopher Hoole  |  christopherhoole.com  |  Confidential", {
    x: 0.4, y: 7.2, w: 10, h: 0.3, fontSize: 9, color: WHITE, fontFace: "Calibri",
    valign: "middle", margin: 0
  });
  slide.addText(String(pageNum), {
    x: 12.5, y: 7.2, w: 0.5, h: 0.3, fontSize: 9, color: WHITE, fontFace: "Calibri",
    align: "right", valign: "middle", margin: 0
  });
  try {
    slide.addImage({ path: LOGO, x: 11.3, y: 6.7, w: 1.6, h: 0.4, sizing: { type: "contain", w: 1.6, h: 0.4 } });
  } catch (e) {}
}

function addSlideHeader(slide, eyebrow, title) {
  slide.addText(eyebrow, {
    x: 0.5, y: 0.45, w: 12.3, h: 0.35, fontSize: 11, color: GOLD, fontFace: "Calibri",
    bold: true, charSpacing: 4, margin: 0
  });
  slide.addText(title, {
    x: 0.5, y: 0.8, w: 12.3, h: 0.7, fontSize: 32, color: NAVY, fontFace: "Calibri",
    bold: true, margin: 0
  });
}

function statCard(slide, x, y, w, h, value, label, sublabel, accent) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h, fill: { color: WHITE }, line: { color: GREY_LIGHT, width: 1 }
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w: 0.08, h, fill: { color: accent || GOLD }, line: { type: "none" }
  });
  slide.addText(value, {
    x: x + 0.25, y: y + 0.2, w: w - 0.4, h: h * 0.45, fontSize: 36, color: NAVY,
    fontFace: "Calibri", bold: true, margin: 0
  });
  slide.addText(label, {
    x: x + 0.25, y: y + h * 0.55, w: w - 0.4, h: h * 0.25, fontSize: 12, color: DARK,
    fontFace: "Calibri", bold: true, margin: 0
  });
  if (sublabel) {
    slide.addText(sublabel, {
      x: x + 0.25, y: y + h * 0.78, w: w - 0.4, h: h * 0.2, fontSize: 9, color: GREY,
      fontFace: "Calibri", margin: 0
    });
  }
}

// ============ SLIDE 1: COVER ============
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  // Gold accent bar top
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.3, h: 7.5, fill: { color: GOLD }, line: { type: "none" }
  });

  s.addText("WEEKLY PERFORMANCE REPORT", {
    x: 1, y: 1.2, w: 11, h: 0.4, fontSize: 12, color: GOLD, fontFace: "Calibri",
    bold: true, charSpacing: 8, margin: 0
  });

  s.addText("Week 1", {
    x: 1, y: 1.7, w: 11, h: 1.5, fontSize: 90, color: WHITE, fontFace: "Calibri",
    bold: true, margin: 0
  });

  s.addText("13 April  –  17 April 2026", {
    x: 1, y: 3.3, w: 11, h: 0.6, fontSize: 28, color: ICE, fontFace: "Calibri",
    margin: 0
  });

  // Divider line
  s.addShape(pres.shapes.LINE, {
    x: 1, y: 4.2, w: 4, h: 0, line: { color: GOLD, width: 2 }
  });

  s.addText("Dental by Design  |  Prodent Group", {
    x: 1, y: 4.4, w: 11, h: 0.5, fontSize: 20, color: WHITE, fontFace: "Calibri",
    bold: true, margin: 0
  });

  // Bottom block
  s.addText("Christopher Hoole", {
    x: 1, y: 6.3, w: 6, h: 0.35, fontSize: 14, color: WHITE, fontFace: "Calibri",
    bold: true, margin: 0
  });
  s.addText("Google Ads Specialist  |  christopherhoole.com", {
    x: 1, y: 6.6, w: 7, h: 0.3, fontSize: 11, color: ICE, fontFace: "Calibri", margin: 0
  });
  try {
    s.addImage({ path: LOGO, x: 10.6, y: 6.3, w: 2, h: 0.6, sizing: { type: "contain", w: 2, h: 0.6 } });
  } catch (e) {}
}

// ============ SLIDE 2: HEADLINES ============
{
  const s = pres.addSlide();
  s.background = { color: "FAFAFA" };
  addSlideHeader(s, "EXECUTIVE SUMMARY", "Week 1 Headlines");

  // 4 stat cards
  const cardY = 1.8;
  const cardH = 1.8;
  const cardW = 2.95;
  const gap = 0.2;
  const startX = 0.5;

  statCard(s, startX + 0 * (cardW + gap), cardY, cardW, cardH, "£8,462", "Total Spend", "across 3 active campaigns", GOLD);
  statCard(s, startX + 1 * (cardW + gap), cardY, cardW, cardH, "87", "Dengro Leads", "qualified business leads", GREEN);
  statCard(s, startX + 2 * (cardW + gap), cardY, cardW, cardH, "4", "Patient Enquiries", "Dengro bookings / purchases", GREEN);
  statCard(s, startX + 3 * (cardW + gap), cardY, cardW, cardH, "£97", "Cost Per Lead", "qualified lead economics", GOLD);

  // Narrative block
  const narrY = 4.1;
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: narrY, w: 12.3, h: 2.5, fill: { color: WHITE }, line: { color: GREY_LIGHT, width: 1 }
  });
  s.addText("A foundation week", {
    x: 0.8, y: narrY + 0.2, w: 11.7, h: 0.5, fontSize: 20, color: NAVY, fontFace: "Calibri",
    bold: true, margin: 0
  });
  s.addText([
    { text: "Week 1 focused on rebuilding the account's structural foundations. ", options: { bold: true } },
    { text: "4,700+ negative keywords restructured into 11 organised shared lists, the Brand campaign rebuilt with proper bid controls, and the Dental Implants Intent campaign re-engineered into 25 tightly-themed ad groups with 75 new keyword-aligned ads." }
  ], {
    x: 0.8, y: narrY + 0.75, w: 11.7, h: 0.8, fontSize: 14, color: DARK, fontFace: "Calibri", margin: 0
  });
  s.addText([
    { text: "The numbers that matter: ", options: { bold: true, color: NAVY } },
    { text: "87 qualified Dengro leads and 4 patient enquiries at £97 per lead / £2,115 per enquiry. That’s a healthy business-level return while the new structure enters Google's learning period." }
  ], {
    x: 0.8, y: narrY + 1.55, w: 11.7, h: 0.8, fontSize: 14, color: DARK, fontFace: "Calibri", margin: 0
  });

  addFooter(s, 2);
}

// ============ SLIDE 3: WHAT I DELIVERED ============
{
  const s = pres.addSlide();
  s.background = { color: "FAFAFA" };
  addSlideHeader(s, "WORK DELIVERED", "Day-by-day, Tuesday to Friday");

  const headerFill = { color: NAVY };
  const headerOpt = { bold: true, color: WHITE, fontSize: 12, fill: headerFill, align: "left", valign: "middle" };

  const rows = [
    [
      { text: "DAY", options: headerOpt },
      { text: "FOCUS", options: headerOpt },
      { text: "OUTPUT", options: headerOpt }
    ],
    [
      { text: "Tue 14 Apr", options: { bold: true, color: NAVY, fontSize: 12, valign: "middle" } },
      { text: "Negative keyword overhaul", options: { fontSize: 12, color: DARK, valign: "middle" } },
      { text: "4,700+ negatives restructured into 11 organised shared lists covering competitors, abroad, wrong locations, non-DBD services, brand-specific research and cheap/NHS-seeker traffic.", options: { fontSize: 11, color: DARK, valign: "middle" } }
    ],
    [
      { text: "Wed 15 Apr", options: { bold: true, color: NAVY, fontSize: 12, valign: "middle" } },
      { text: "Brand rebuild + account-wide", options: { fontSize: 12, color: DARK, valign: "middle" } },
      { text: "Brand campaign: Target Impression Share 90% / £1.50 max CPC ceiling, 266 London postcodes, 42-cell ad schedule, 2 new RSAs. Account: auto-apply disabled, PMax → Target CPA £60, DII → Target CPA £75, 8 new RSAs, 356 more negatives.", options: { fontSize: 11, color: DARK, valign: "middle" } }
    ],
    [
      { text: "Thu 16 Apr", options: { bold: true, color: NAVY, fontSize: 12, valign: "middle" } },
      { text: "Dental Implants Intent rebuild", options: { fontSize: 12, color: DARK, valign: "middle" } },
      { text: "20 new ad groups built with 537 keywords and 60 RSAs. 4 legacy underperforming ad groups paused (£99+ CPA). Ad structure now maps to patient intent: service, cost, finance, location, quality.", options: { fontSize: 11, color: DARK, valign: "middle" } }
    ],
    [
      { text: "Fri 17 Apr", options: { bold: true, color: NAVY, fontSize: 12, valign: "middle" } },
      { text: "Final ad groups + full audit", options: { fontSize: 12, color: DARK, valign: "middle" } },
      { text: "AG21-25 built (5 ad groups, 15 RSAs). Daily search terms review of 1,786 queries. 173 DBD-blocking terms removed across all 11 negative lists. Ad Strength audit across 63 live RSAs to push toward Excellent.", options: { fontSize: 11, color: DARK, valign: "middle" } }
    ]
  ];

  s.addTable(rows, {
    x: 0.5, y: 1.7, w: 12.3,
    colW: [1.4, 3.2, 7.7],
    rowH: [0.5, 1.0, 1.2, 1.0, 1.1],
    border: { pt: 1, color: GREY_LIGHT },
    fontFace: "Calibri"
  });

  addFooter(s, 3);
}

// ============ SLIDE 4: CUMULATIVE BUILD ============
{
  const s = pres.addSlide();
  s.background = { color: "FAFAFA" };
  addSlideHeader(s, "THE FOUNDATION", "What's now in place");

  // 5 big stat cards
  const cardY = 1.9;
  const cardH = 2.0;
  const cardW = 2.4;
  const gap = 0.15;
  const startX = 0.55;

  statCard(s, startX + 0 * (cardW + gap), cardY, cardW, cardH, "5,000+", "Negative Keywords", "11 structured shared lists", NAVY);
  statCard(s, startX + 1 * (cardW + gap), cardY, cardW, cardH, "546", "Positive Keywords", "across Brand + DII", NAVY);
  statCard(s, startX + 2 * (cardW + gap), cardY, cardW, cardH, "75", "New RSAs", "1,050 headlines / 280 descriptions", NAVY);
  statCard(s, startX + 3 * (cardW + gap), cardY, cardW, cardH, "25", "DII Ad Groups", "patient-intent structure", NAVY);
  statCard(s, startX + 4 * (cardW + gap), cardY, cardW, cardH, "810", "Geo Targets", "Greater London, 3 campaigns", NAVY);

  // Context block
  const ctxY = 4.3;
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: ctxY, w: 12.3, h: 2.3, fill: { color: NAVY }, line: { type: "none" }
  });
  s.addText("From a legacy patchwork to a clean, structured account", {
    x: 0.8, y: ctxY + 0.25, w: 11.7, h: 0.5, fontSize: 20, color: WHITE, fontFace: "Calibri",
    bold: true, margin: 0
  });
  s.addText([
    { text: "Previously the account carried 47 campaigns (only 4 active), legacy conversion tracking, and a keyword base built across multiple agencies. ", options: { color: WHITE } },
    { text: "As of Friday it runs on 3 structured campaigns (Brand, PMax, Dental Implants Intent), one bid strategy per campaign, one negative keyword architecture, and one postcode geo framework. Every future optimisation now compounds on a consistent base.", options: { color: ICE } }
  ], {
    x: 0.8, y: ctxY + 0.85, w: 11.7, h: 1.3, fontSize: 14, fontFace: "Calibri", margin: 0
  });

  addFooter(s, 4);
}

// ============ SLIDE 5: BRAND PERFORMANCE ============
{
  const s = pres.addSlide();
  s.background = { color: "FAFAFA" };
  addSlideHeader(s, "BRAND CAMPAIGN", "Tighter targeting, stronger signals");

  // Left: big stats
  statCard(s, 0.5, 1.9, 3.8, 1.6, "-35%", "Avg CPC vs March", "£3.29 → £2.16", GREEN);
  statCard(s, 0.5, 3.65, 3.8, 1.6, "35.14%", "Click-Through Rate", "up from 26% March avg", GREEN);
  statCard(s, 0.5, 5.4, 3.8, 1.6, "100%", "Impression Share", "top of page, every search", GREEN);

  // Right: weekly trend line chart
  const cpcData = [{
    name: "Avg CPC (£)",
    labels: ["23 Feb", "2 Mar", "9 Mar", "16 Mar", "23 Mar", "30 Mar", "6 Apr", "13 Apr"],
    values: [3.09, 2.41, 3.49, 4.00, 3.24, 2.31, 2.90, 2.16]
  }];

  s.addChart(pres.charts.LINE, cpcData, {
    x: 4.6, y: 1.9, w: 8.3, h: 5.1,
    showTitle: true,
    title: "Brand Avg CPC — 8 week trend",
    titleFontSize: 14, titleColor: NAVY, titleFontFace: "Calibri",
    lineDataSymbol: "circle",
    lineDataSymbolSize: 8,
    lineSize: 3,
    chartColors: [GOLD],
    showValue: true,
    dataLabelFontSize: 10,
    dataLabelFormatCode: "£0.00",
    catAxisLabelFontSize: 10,
    catAxisLabelFontFace: "Calibri",
    valAxisLabelFontSize: 10,
    valAxisLabelFontFace: "Calibri",
    valAxisLabelFormatCode: "£0.00",
    showLegend: false
  });

  addFooter(s, 5);
}

// ============ SLIDE 6: PMAX PERFORMANCE ============
{
  const s = pres.addSlide();
  s.background = { color: "FAFAFA" };
  addSlideHeader(s, "PMAX CAMPAIGN", "Delivering at scale");

  // Top row: stats
  statCard(s, 0.5, 1.9, 3.0, 1.7, "78.5", "Dengro Leads", "this week", GREEN);
  statCard(s, 3.65, 1.9, 3.0, 1.7, "3", "Patient Enquiries", "Dengro bookings", GREEN);
  statCard(s, 6.8, 1.9, 3.0, 1.7, "£73", "CPA (primary)", "down from £86 prior week", GOLD);
  statCard(s, 9.95, 1.9, 3.0, 1.7, "£25", "Best-day CPA", "Wed 15 Apr, after tCPA switch", GOLD);

  // Narrative box
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 3.8, w: 12.3, h: 3.1, fill: { color: WHITE }, line: { color: GREY_LIGHT, width: 1 }
  });
  s.addText("What changed this week", {
    x: 0.8, y: 4.0, w: 11.7, h: 0.5, fontSize: 18, color: NAVY, fontFace: "Calibri",
    bold: true, margin: 0
  });
  s.addText([
    { text: "•  Bid strategy switched from Max Conversion Value (tROAS 80%) to Target CPA £60.", options: { bullet: false, breakLine: true, color: DARK } },
    { text: "•  Removed 3 dangerous single-word negatives that were blocking DBD's own postcodes.", options: { breakLine: true, color: DARK } },
    { text: "•  Geo + schedule aligned with Brand (270 postcodes, 42-cell schedule).", options: { breakLine: true, color: DARK } },
    { text: "•  Shared negative lists cleaned — zero NHS/cheap-seeker junk in search terms this week.", options: { breakLine: true, color: DARK } },
    { text: " ", options: { breakLine: true } },
    { text: "Flagged for Week 2: ", options: { bold: true, color: GOLD } },
    { text: "Google still reports \"most asset groups limited by policy\" on PMax. Queued for rebuild next week with premium-positioned assets.", options: { color: DARK } }
  ], {
    x: 0.8, y: 4.5, w: 11.7, h: 2.3, fontSize: 13, fontFace: "Calibri", margin: 0
  });

  addFooter(s, 6);
}

// ============ SLIDE 7: DII PERFORMANCE ============
{
  const s = pres.addSlide();
  s.background = { color: "FAFAFA" };
  addSlideHeader(s, "DENTAL IMPLANTS INTENT", "Learning mode — by design");

  // Top row stats
  statCard(s, 0.5, 1.9, 3.0, 1.7, "25", "Ad Groups", "mapped to patient intent", NAVY);
  statCard(s, 3.65, 1.9, 3.0, 1.7, "75", "RSAs Live", "each keyword-aligned", NAVY);
  statCard(s, 6.8, 1.9, 3.0, 1.7, "~650", "Keywords", "phrase + exact, all in DBD's service range", NAVY);
  statCard(s, 9.95, 1.9, 3.0, 1.7, "63%", "Impression Share", "strong visibility on intent traffic", GREEN);

  // Narrative box
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 3.8, w: 12.3, h: 3.1, fill: { color: WHITE }, line: { color: GREY_LIGHT, width: 1 }
  });
  s.addText("Why the CPA temporarily spiked — and why that's fine", {
    x: 0.8, y: 4.0, w: 11.7, h: 0.5, fontSize: 18, color: NAVY, fontFace: "Calibri",
    bold: true, margin: 0
  });
  s.addText([
    { text: "The campaign was restructured mid-week (Tue-Thu): 20 new ad groups built, 4 legacy groups paused, bid strategy switched to Target CPA £75, and the keyword base rebuilt from the ground up. ", options: { color: DARK } },
    { text: "Google needs ~14-21 days to rebalance bids against the new structure.", options: { bold: true, color: NAVY } },
    { text: " Week 1 CPA is an average of 1 day of the old structure + 4 days of learning. Week 2 will give the first clean read.", options: { color: DARK }, breakLine: true },
    { text: " ", options: { breakLine: true } },
    { text: "Early positives: ", options: { bold: true, color: GREEN } },
    { text: "Wednesday delivered 3 primary conversions at £122 CPA — first sign the new structure is converting. All Ad Strength scores being pushed toward Excellent this week as part of the audit.", options: { color: DARK } }
  ], {
    x: 0.8, y: 4.5, w: 11.7, h: 2.3, fontSize: 13, fontFace: "Calibri", margin: 0
  });

  addFooter(s, 7);
}

// ============ SLIDE 8: REAL BUSINESS METRICS ============
{
  const s = pres.addSlide();
  s.background = { color: "FAFAFA" };
  addSlideHeader(s, "THE NUMBERS THAT MATTER", "Real business outcomes this week");

  // Left: the two big callouts
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.9, w: 6.1, h: 2.5, fill: { color: NAVY }, line: { type: "none" }
  });
  s.addText("87", { x: 0.8, y: 2.0, w: 5.5, h: 1.4, fontSize: 96, color: WHITE, fontFace: "Calibri", bold: true, margin: 0 });
  s.addText("Qualified Dengro leads", { x: 0.8, y: 3.3, w: 5.5, h: 0.5, fontSize: 20, color: GOLD, fontFace: "Calibri", bold: true, margin: 0 });
  s.addText("At £97 per qualified lead", { x: 0.8, y: 3.75, w: 5.5, h: 0.4, fontSize: 14, color: ICE, fontFace: "Calibri", margin: 0 });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.7, y: 1.9, w: 6.1, h: 2.5, fill: { color: GOLD }, line: { type: "none" }
  });
  s.addText("4", { x: 7.0, y: 2.0, w: 5.5, h: 1.4, fontSize: 96, color: WHITE, fontFace: "Calibri", bold: true, margin: 0 });
  s.addText("Patient enquiries", { x: 7.0, y: 3.3, w: 5.5, h: 0.5, fontSize: 20, color: NAVY, fontFace: "Calibri", bold: true, margin: 0 });
  s.addText("At £2,115 per enquiry — healthy vs implant LTV", { x: 7.0, y: 3.75, w: 5.5, h: 0.4, fontSize: 14, color: WHITE, fontFace: "Calibri", margin: 0 });

  // Bottom: breakdown by campaign
  const headerOpt = { bold: true, color: WHITE, fontSize: 12, fill: { color: NAVY }, valign: "middle" };
  const cell = { fontSize: 12, color: DARK, valign: "middle", fontFace: "Calibri" };
  const cellBold = { fontSize: 12, color: NAVY, bold: true, valign: "middle", fontFace: "Calibri" };

  const rows = [
    [
      { text: "CAMPAIGN", options: headerOpt },
      { text: "DENGRO LEADS", options: { ...headerOpt, align: "center" } },
      { text: "PATIENT ENQUIRIES", options: { ...headerOpt, align: "center" } },
      { text: "SPEND", options: { ...headerOpt, align: "center" } },
      { text: "COST / LEAD", options: { ...headerOpt, align: "center" } }
    ],
    [
      { text: "Brand", options: cellBold },
      { text: "2", options: { ...cell, align: "center" } },
      { text: "0", options: { ...cell, align: "center" } },
      { text: "£280", options: { ...cell, align: "center" } },
      { text: "£140", options: { ...cell, align: "center" } }
    ],
    [
      { text: "Dental Implants Intent", options: cellBold },
      { text: "6.5", options: { ...cell, align: "center" } },
      { text: "1", options: { ...cell, align: "center" } },
      { text: "£2,222", options: { ...cell, align: "center" } },
      { text: "£342", options: { ...cell, align: "center" } }
    ],
    [
      { text: "Performance Max", options: cellBold },
      { text: "78.5", options: { ...cell, align: "center" } },
      { text: "3", options: { ...cell, align: "center" } },
      { text: "£5,960", options: { ...cell, align: "center" } },
      { text: "£76", options: { ...cell, align: "center" } }
    ],
    [
      { text: "WEEK 1 TOTAL", options: { ...cellBold, fill: { color: ICE }, fontSize: 13 } },
      { text: "87", options: { ...cellBold, align: "center", fill: { color: ICE } } },
      { text: "4", options: { ...cellBold, align: "center", fill: { color: ICE } } },
      { text: "£8,462", options: { ...cellBold, align: "center", fill: { color: ICE } } },
      { text: "£97", options: { ...cellBold, align: "center", fill: { color: ICE } } }
    ]
  ];

  s.addTable(rows, {
    x: 0.5, y: 4.7, w: 12.3,
    colW: [4.3, 2.0, 2.5, 1.75, 1.75],
    rowH: [0.4, 0.42, 0.42, 0.42, 0.5],
    border: { pt: 1, color: GREY_LIGHT }
  });

  addFooter(s, 8);
}

// ============ SLIDE 9: 8-WEEK CONTEXT ============
{
  const s = pres.addSlide();
  s.background = { color: "FAFAFA" };
  addSlideHeader(s, "EIGHT-WEEK CONTEXT", "Here’s where we started");

  // Chart: weekly spend and leads combined
  const spendData = [
    {
      name: "Weekly Spend (£)",
      labels: ["23 Feb", "2 Mar", "9 Mar", "16 Mar", "23 Mar", "30 Mar", "6 Apr", "13 Apr"],
      values: [17101, 14475, 8115, 13173, 11558, 9997, 10291, 8462]
    }
  ];

  s.addChart(pres.charts.BAR, spendData, {
    x: 0.5, y: 1.8, w: 12.3, h: 2.5,
    barDir: "col",
    showTitle: true,
    title: "Weekly Spend — 8 weeks",
    titleFontSize: 14, titleColor: NAVY,
    chartColors: [NAVY],
    showValue: true,
    dataLabelFontSize: 9,
    dataLabelFormatCode: "£#,##0",
    dataLabelColor: WHITE,
    catAxisLabelFontSize: 10,
    valAxisLabelFontSize: 10,
    valAxisLabelFormatCode: "£#,##0",
    showLegend: false
  });

  const convData = [
    {
      name: "Primary Conversions",
      labels: ["23 Feb", "2 Mar", "9 Mar", "16 Mar", "23 Mar", "30 Mar", "6 Apr", "13 Apr"],
      values: [229.5, 184.6, 115.7, 133.7, 239.2, 148.4, 134.1, 101.0]
    }
  ];

  s.addChart(pres.charts.BAR, convData, {
    x: 0.5, y: 4.45, w: 12.3, h: 2.5,
    barDir: "col",
    showTitle: true,
    title: "Weekly Primary Conversions — 8 weeks",
    titleFontSize: 14, titleColor: NAVY,
    chartColors: [GOLD],
    showValue: true,
    dataLabelFontSize: 9,
    dataLabelFormatCode: "0",
    dataLabelColor: NAVY,
    catAxisLabelFontSize: 10,
    valAxisLabelFontSize: 10,
    showLegend: false
  });

  addFooter(s, 9);
}

// ============ SLIDE 10: DECISIONS + WEEK 2 ============
{
  const s = pres.addSlide();
  s.background = { color: "FAFAFA" };
  addSlideHeader(s, "WHAT'S NEXT", "Two decisions + Week 2 plan");

  // Left: decisions needed
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.85, w: 6.0, h: 5.1, fill: { color: WHITE }, line: { color: GOLD, width: 2 }
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.85, w: 6.0, h: 0.6, fill: { color: GOLD }, line: { type: "none" }
  });
  s.addText("2 ITEMS NEED YOUR DECISION", {
    x: 0.7, y: 1.85, w: 5.6, h: 0.6, fontSize: 13, color: NAVY, fontFace: "Calibri",
    bold: true, valign: "middle", charSpacing: 3, margin: 0
  });

  s.addText("1. Consultation pricing", {
    x: 0.7, y: 2.65, w: 5.6, h: 0.4, fontSize: 15, color: NAVY, fontFace: "Calibri", bold: true, margin: 0
  });
  s.addText("Ads currently say \"Free Consultation\". Website says £95. Need to align — free, £95, or tiered — so ads match reality and clear Google's misleading pricing policy.", {
    x: 0.7, y: 3.05, w: 5.6, h: 1.1, fontSize: 12, color: DARK, fontFace: "Calibri", margin: 0
  });

  s.addText("2. \"25+ Years\" experience claim", {
    x: 0.7, y: 4.4, w: 5.6, h: 0.4, fontSize: 15, color: NAVY, fontFace: "Calibri", bold: true, margin: 0
  });
  s.addText("Ads reference \"25+ years\" — clinic founded 2010 (16 years). Clarify whether this refers to team principal experience, combined team years, or something else. Ads will be updated to a verifiable claim.", {
    x: 0.7, y: 4.8, w: 5.6, h: 1.4, fontSize: 12, color: DARK, fontFace: "Calibri", margin: 0
  });

  s.addText("Awaiting your reply", {
    x: 0.7, y: 6.3, w: 5.6, h: 0.4, fontSize: 11, color: GREY, fontFace: "Calibri", italic: true, margin: 0
  });

  // Right: Week 2 plan
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.7, y: 1.85, w: 6.1, h: 5.1, fill: { color: NAVY }, line: { type: "none" }
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.7, y: 1.85, w: 6.1, h: 0.6, fill: { color: NAVY_DEEP }, line: { type: "none" }
  });
  s.addText("WEEK 2 PLAN  (20 - 24 APRIL)", {
    x: 6.9, y: 1.85, w: 5.7, h: 0.6, fontSize: 13, color: GOLD, fontFace: "Calibri",
    bold: true, valign: "middle", charSpacing: 3, margin: 0
  });

  const planItems = [
    ["Mon 20 Apr", "End-to-end conversion tracking audit — priority before any CPA analysis"],
    ["Tue 21 Apr", "Ad Strength audit resumed on AG22-25 (once Google review clears)"],
    ["Wed-Thu", "Performance Max rebuild — new assets, policy compliance, lift \"limited\" status"],
    ["Fri 24 Apr", "Cosmetic Dentistry campaign scoping + Week 2 report"]
  ];

  let py = 2.75;
  planItems.forEach(([day, task], i) => {
    s.addText(day, {
      x: 6.9, y: py, w: 5.7, h: 0.3, fontSize: 12, color: GOLD, fontFace: "Calibri",
      bold: true, margin: 0
    });
    s.addText(task, {
      x: 6.9, y: py + 0.3, w: 5.7, h: 0.7, fontSize: 12, color: WHITE, fontFace: "Calibri", margin: 0
    });
    py += 1.05;
  });

  addFooter(s, 10);
}

// ============ SLIDE 11: CLOSING ============
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.3, h: 7.5, fill: { color: GOLD }, line: { type: "none" }
  });

  s.addText("Questions?", {
    x: 1, y: 2.5, w: 11, h: 1.3, fontSize: 72, color: WHITE, fontFace: "Calibri",
    bold: true, margin: 0
  });
  s.addText("Happy to walk through any part of this report — or jump on a call to discuss Week 2 priorities.", {
    x: 1, y: 4.0, w: 11, h: 0.9, fontSize: 18, color: ICE, fontFace: "Calibri", margin: 0
  });

  s.addShape(pres.shapes.LINE, {
    x: 1, y: 5.2, w: 4, h: 0, line: { color: GOLD, width: 2 }
  });

  s.addText("Christopher Hoole  |  Google Ads Specialist", {
    x: 1, y: 5.4, w: 11, h: 0.4, fontSize: 16, color: WHITE, fontFace: "Calibri", bold: true, margin: 0
  });
  s.addText("christopherhoole.com  |  chrishoole101@gmail.com", {
    x: 1, y: 5.85, w: 11, h: 0.4, fontSize: 13, color: ICE, fontFace: "Calibri", margin: 0
  });

  try {
    s.addImage({ path: LOGO, x: 10.6, y: 6.3, w: 2, h: 0.6, sizing: { type: "contain", w: 2, h: 0.6 } });
  } catch (e) {}
}

// ============ WRITE FILE ============
const OUT = "C:/Users/User/Desktop/gads-data-layer/potential_clients/Inserta Dental/reports/DentalByDesign.co.uk - Week 1 Report 13-17 April 2026-v1.pptx";
pres.writeFile({ fileName: OUT }).then(f => console.log("Wrote: " + f));
