const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const data = JSON.parse(fs.readFileSync(path.join(__dirname, "analysis_output.json"), "utf8"));
const CHART_DIR = path.join(__dirname, "charts");
const OUTPUT = path.join(__dirname, "reports", "01_waste_spend_report_v6.pptx");

// ── Colours (ACT logo / Google brand — NO greys for text) ──
const NAVY    = "1A237E";
const BLUE    = "4285F4";
const RED     = "EA4335";
const AMBER   = "FBBC05";
const GREEN   = "34A853";
const L_GREY  = "F5F6FA";  // Background only, never for text
const BLACK   = "1A1A1A";  // Primary text colour (near-black)
const WHITE   = "FFFFFF";
const LOGO_PATH = path.join(CHART_DIR, "act_logo.png");

// ── STANDARDISED FONT SIZES (minimum 11pt — footer is only exception) ──
const F = {
  HERO: 44,       // Big hero numbers
  TITLE: 28,      // Slide titles
  STAT: 22,       // Stat card big numbers
  SECTION: 14,    // Section headers
  BODY: 11,       // All body text, tables, bullets, commentary — minimum size
  FOOTER: 11,     // Footer text (was 8, now 11 minimum)
};

// ── TIMEFRAME ──
const TIMEFRAME = "Jan 2025 — Mar 2026 (15 months)";
const TIMEFRAME_SHORT = "Jan 2025 — Mar 2026";

// ── Factory helpers ──
const makeShadow = () => ({ type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.12 });
const makeCardShadow = () => ({ type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.10 });

// ── Presentation setup ──
let pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Christopher Hoole";
pres.title = "Waste Spend Analysis — Objection Experts";
const W = 13.33, H = 7.5, MARGIN = 0.6;

// ── Google-stripe accent bar ──
function addStripeBar(slide, y, h) {
  const sW = W / 4;
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y, w: sW, h, fill: { color: BLUE } });
  slide.addShape(pres.shapes.RECTANGLE, { x: sW, y, w: sW, h, fill: { color: RED } });
  slide.addShape(pres.shapes.RECTANGLE, { x: sW*2, y, w: sW, h, fill: { color: AMBER } });
  slide.addShape(pres.shapes.RECTANGLE, { x: sW*3, y, w: sW, h, fill: { color: GREEN } });
}

// ── Footer ──
function addFooter(slide, pageNum) {
  const barY = 6.92;
  const barW = (W - 2*MARGIN) / 4;
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN, y: barY, w: barW, h: 0.03, fill: { color: BLUE } });
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN + barW, y: barY, w: barW, h: 0.03, fill: { color: RED } });
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN + barW*2, y: barY, w: barW, h: 0.03, fill: { color: AMBER } });
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN + barW*3, y: barY, w: barW, h: 0.03, fill: { color: GREEN } });
  slide.addImage({ path: LOGO_PATH, x: MARGIN, y: 7.0, w: 0.22, h: 0.22 });
  slide.addText([
    { text: "Christopher Hoole", options: { bold: true, color: NAVY } },
    { text: "  |  christopherhoole.com  |  Confidential", options: { color: BLACK } },
  ], {
    x: MARGIN + 0.3, y: 7.0, w: 6, h: 0.25,
    fontSize: F.FOOTER, fontFace: "Calibri", valign: "middle"
  });
  slide.addText(String(pageNum), {
    x: W - MARGIN - 0.5, y: 7.0, w: 0.5, h: 0.25,
    fontSize: F.FOOTER, color: NAVY, fontFace: "Calibri", align: "right", valign: "middle"
  });
}

// ── Stat card ──
function addStatCard(slide, x, y, w, h, value, label, accentColor) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h, fill: { color: WHITE },
    shadow: makeCardShadow(), line: { color: "E2E8F0", width: 0.5 }
  });
  slide.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.06, h, fill: { color: accentColor } });
  slide.addText(value, {
    x: x + 0.2, y: y + 0.1, w: w - 0.3, h: 0.5,
    fontSize: F.STAT, fontFace: "Calibri", bold: true, color: accentColor, margin: 0
  });
  slide.addText(label, {
    x: x + 0.2, y: y + 0.6, w: w - 0.3, h: 0.35,
    fontSize: F.BODY, fontFace: "Calibri", color: BLACK, margin: 0
  });
}

// ── Slide title helper ──
function addSlideTitle(slide, title, subtitle) {
  addStripeBar(slide, 0, 0.06);
  slide.addText(title, {
    x: MARGIN, y: 0.3, w: 7, h: 0.5,
    fontSize: F.TITLE, fontFace: "Calibri", bold: true, color: NAVY, margin: 0
  });
  // Timeframe badge — always visible, prominent
  slide.addShape(pres.shapes.RECTANGLE, {
    x: W - MARGIN - 3.6, y: 0.3, w: 3.6, h: 0.45,
    fill: { color: WHITE }, line: { color: BLUE, width: 1 }
  });
  slide.addText(`Data: ${TIMEFRAME_SHORT}`, {
    x: W - MARGIN - 3.5, y: 0.32, w: 3.4, h: 0.4,
    fontSize: F.BODY, fontFace: "Calibri", color: BLUE, align: "center", valign: "middle", bold: true, margin: 0
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: MARGIN, y: 0.85, w: 9, h: 0.3,
      fontSize: F.BODY, fontFace: "Calibri", color: RED, margin: 0
    });
  }
}

// ═══════════════════════════════════════════
// SLIDE 1: TITLE (Option 4 — Light grey + bold accents)
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: L_GREY };
  addStripeBar(slide, 0, 0.07);

  // Blue left accent strip
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0.07, w: 0.12, h: 7.43, fill: { color: BLUE } });

  slide.addImage({ path: LOGO_PATH, x: 0.6, y: 0.5, w: 0.65, h: 0.65 });

  slide.addText("WASTE SPEND\nANALYSIS", {
    x: 0.6, y: 1.4, w: 5.5, h: 1.8,
    fontSize: F.HERO, fontFace: "Calibri", bold: true, color: NAVY, margin: 0
  });

  slide.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 3.3, w: 2.5, h: 0.05, fill: { color: BLUE } });

  slide.addText("Objection Experts", {
    x: 0.6, y: 3.55, w: 5.5, h: 0.5,
    fontSize: F.STAT, fontFace: "Calibri", color: BLUE, margin: 0
  });

  slide.addText([
    { text: "Prepared by Christopher Hoole", options: { breakLine: true, fontSize: F.BODY, color: BLACK, bold: true } },
    { text: "Google Ads Specialist  |  March 2026", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "christopherhoole.com", options: { fontSize: F.BODY, color: BLUE } },
  ], { x: 0.6, y: 4.3, w: 5.5, h: 1.0, fontFace: "Calibri", margin: 0 });

  // Prominent date range callout
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 5.5, w: 4.5, h: 0.5,
    fill: { color: WHITE }, line: { color: BLUE, width: 1 }
  });
  slide.addText(`Data period: ${TIMEFRAME}`, {
    x: 0.7, y: 5.52, w: 4.3, h: 0.45,
    fontSize: F.BODY, fontFace: "Calibri", color: BLUE, bold: true, valign: "middle", margin: 0
  });

  // Right side — stat cards (Option 4 style)
  const rX = 6.8, rW = 5.9;

  // Main waste card
  slide.addShape(pres.shapes.RECTANGLE, {
    x: rX, y: 0.5, w: rW, h: 2.5,
    fill: { color: WHITE }, shadow: makeCardShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: rX, y: 0.5, w: 0.08, h: 2.5, fill: { color: RED } });
  slide.addText(`£${data.total_waste.toLocaleString()}`, {
    x: rX + 0.3, y: 0.7, w: rW - 0.5, h: 0.9,
    fontSize: F.HERO, fontFace: "Calibri", bold: true, color: RED, margin: 0
  });
  slide.addText("Identified Waste", {
    x: rX + 0.3, y: 1.5, w: rW - 0.5, h: 0.35,
    fontSize: F.SECTION, fontFace: "Calibri", color: NAVY, margin: 0
  });
  slide.addText(`${data.waste_pct}% of your £${data.total_spend.toLocaleString()} total spend`, {
    x: rX + 0.3, y: 1.9, w: rW - 0.5, h: 0.3,
    fontSize: F.BODY, fontFace: "Calibri", color: BLACK, margin: 0
  });

  // Three stat cards below
  const smW = (rW - 0.4) / 3;
  const smH = 1.15;
  const smY = 3.2;

  // Card: Conversions
  slide.addShape(pres.shapes.RECTANGLE, {
    x: rX, y: smY, w: smW, h: smH,
    fill: { color: WHITE }, shadow: makeCardShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: rX, y: smY, w: 0.06, h: smH, fill: { color: GREEN } });
  slide.addText(`${Math.round(data.total_conversions)}`, {
    x: rX + 0.15, y: smY + 0.12, w: smW - 0.25, h: 0.45,
    fontSize: F.STAT, fontFace: "Calibri", bold: true, color: GREEN, margin: 0
  });
  slide.addText("Conversions", {
    x: rX + 0.15, y: smY + 0.6, w: smW - 0.25, h: 0.3,
    fontSize: F.BODY, fontFace: "Calibri", color: BLACK, margin: 0
  });

  // Card: Monthly savings
  const sm2X = rX + smW + 0.2;
  slide.addShape(pres.shapes.RECTANGLE, {
    x: sm2X, y: smY, w: smW, h: smH,
    fill: { color: WHITE }, shadow: makeCardShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: sm2X, y: smY, w: 0.06, h: smH, fill: { color: BLUE } });
  slide.addText("£380-655", {
    x: sm2X + 0.15, y: smY + 0.12, w: smW - 0.25, h: 0.45,
    fontSize: F.STAT, fontFace: "Calibri", bold: true, color: BLUE, margin: 0
  });
  slide.addText("Saving/Month", {
    x: sm2X + 0.15, y: smY + 0.6, w: smW - 0.25, h: 0.3,
    fontSize: F.BODY, fontFace: "Calibri", color: BLACK, margin: 0
  });

  // Card: Annualised savings
  const sm3X = rX + 2*(smW + 0.2);
  slide.addShape(pres.shapes.RECTANGLE, {
    x: sm3X, y: smY, w: smW, h: smH,
    fill: { color: WHITE }, shadow: makeCardShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: sm3X, y: smY, w: 0.06, h: smH, fill: { color: AMBER } });
  slide.addText("£4.6-7.9k", {
    x: sm3X + 0.15, y: smY + 0.12, w: smW - 0.25, h: 0.45,
    fontSize: F.STAT, fontFace: "Calibri", bold: true, color: NAVY, margin: 0
  });
  slide.addText("Saving/Year", {
    x: sm3X + 0.15, y: smY + 0.6, w: smW - 0.25, h: 0.3,
    fontSize: F.BODY, fontFace: "Calibri", color: BLACK, margin: 0
  });

  // Bottom stripe
  addStripeBar(slide, 7.0, 0.04);
}

// ═══════════════════════════════════════════
// SLIDE 2: EXECUTIVE SUMMARY
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "Executive Summary", null);

  addStatCard(slide, MARGIN, 1.2, 2.8, 1.05, `£${data.total_spend.toLocaleString()}`, "Total Spend Analysed", NAVY);
  addStatCard(slide, MARGIN + 3.1, 1.2, 2.8, 1.05, `£${data.total_waste.toLocaleString()}`, "Waste Identified", RED);
  addStatCard(slide, MARGIN + 6.2, 1.2, 2.8, 1.05, `${data.waste_pct}%`, "Of Budget Wasted", AMBER);
  addStatCard(slide, MARGIN + 9.3, 1.2, 2.8, 1.05, `${Math.round(data.total_conversions)}`, "Total Conversions", GREEN);

  slide.addText("Key Findings", {
    x: MARGIN, y: 2.6, w: 6, h: 0.35,
    fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: NAVY, margin: 0
  });

  const cats = data.waste_categories;
  slide.addText([
    { text: `895+ locations generated clicks but zero conversions, accounting for £${cats["Geographic Waste"].toLocaleString()} in wasted spend`, options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: `258 search terms consumed £${cats["Non-Converting Search Terms"].toLocaleString()} with zero conversions — many are irrelevant to planning objections`, options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: `Sunday CPA of £${data.day_of_week.sunday_cpa} vs weekday average of £${data.day_of_week.avg_weekday_cpa} — a ${((data.day_of_week.sunday_cpa / data.day_of_week.avg_weekday_cpa - 1) * 100).toFixed(0)}% premium with no bid adjustment`, options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: `The "Neighbourhood Objections" ad group spent £79 with zero conversions`, options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: `Most negative keywords use exact match only — slight variations of blocked terms still trigger ads`, options: { bullet: true, fontSize: F.BODY, color: BLACK } },
  ], {
    x: MARGIN + 0.1, y: 3.0, w: 11.5, h: 2.6,
    fontFace: "Calibri", paraSpaceAfter: 8, margin: 0, valign: "top"
  });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: MARGIN, y: 5.85, w: W - 2*MARGIN, h: 0.7,
    fill: { color: "E8F0FE" }, line: { color: BLUE, width: 1 }
  });
  slide.addText([
    { text: "Recommendation: ", options: { bold: true, color: NAVY } },
    { text: `Implementing the quick wins identified in this report could save an estimated £${data.monthly_waste_estimate.toLocaleString()}/month and significantly reduce cost per conversion.`, options: { color: BLACK } },
  ], {
    x: MARGIN + 0.25, y: 5.9, w: W - 2*MARGIN - 0.5, h: 0.6,
    fontSize: F.BODY, fontFace: "Calibri", valign: "middle", margin: 0
  });

  addFooter(slide, 2);
}

// ═══════════════════════════════════════════
// SLIDE 3: SEARCH TERM WASTE
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "Search Term Waste",
    `258 search terms spent £${data.search_term_waste.total.toLocaleString()} with zero conversions`);

  let top15 = data.search_term_waste.top20.slice(0, 15);
  let tableHeader = [[
    { text: "Search Term", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY } },
    { text: "Clicks", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY, align: "center" } },
    { text: "Cost", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY, align: "center" } },
    { text: "Conv.", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY, align: "center" } },
  ]];
  let tableRows = top15.map((row, i) => [
    { text: row["Search term"], options: { fill: { color: i%2===0 ? L_GREY : WHITE }, fontSize: F.BODY, color: BLACK } },
    { text: String(Math.round(row.Clicks)), options: { fill: { color: i%2===0 ? L_GREY : WHITE }, fontSize: F.BODY, align: "center", color: BLACK } },
    { text: `£${row.Cost.toFixed(2)}`, options: { fill: { color: i%2===0 ? L_GREY : WHITE }, fontSize: F.BODY, align: "center", color: RED, bold: true } },
    { text: "0", options: { fill: { color: i%2===0 ? L_GREY : WHITE }, fontSize: F.BODY, align: "center", color: RED } },
  ]);

  slide.addTable([...tableHeader, ...tableRows], {
    x: MARGIN, y: 1.3, w: 7.5, h: 5.2,
    colW: [3.8, 0.9, 1.2, 0.9],
    border: { type: "solid", pt: 0.5, color: "E2E8F0" },
    rowH: 0.32, margin: [3, 6, 3, 6],
  });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 8.5, y: 1.3, w: 4.2, h: 2.5,
    fill: { color: L_GREY }, shadow: makeCardShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: 8.5, y: 1.3, w: 0.06, h: 2.5, fill: { color: RED } });

  slide.addText("Key Insight", {
    x: 8.8, y: 1.45, w: 3.7, h: 0.3,
    fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: NAVY, margin: 0
  });
  slide.addText([
    { text: `These 258 non-converting search terms represent ${((data.search_term_waste.total / data.total_spend) * 100).toFixed(1)}% of total spend.`, options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Many are users searching for general planning advice, templates, or services unrelated to planning objections.", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "These should be blocked with negative keywords to prevent further waste.", options: { fontSize: F.BODY, color: NAVY, bold: true } },
  ], {
    x: 8.8, y: 1.85, w: 3.7, h: 1.8,
    fontFace: "Calibri", margin: 0, valign: "top"
  });

  addStatCard(slide, 8.5, 4.2, 4.2, 1.0, `£${data.search_term_waste.total.toLocaleString()}`, "Total Non-Converting Search Term Spend", RED);

  addFooter(slide, 3);
}

// ═══════════════════════════════════════════
// SLIDE 4: WASTE BY CATEGORY
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "Waste by Category",
    "Non-converting search terms grouped by intent category");

  slide.addImage({ path: path.join(CHART_DIR, "waste_by_category.png"), x: MARGIN, y: 1.35, w: 7.5, h: 4.0 });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 8.5, y: 1.35, w: 4.2, h: 5.0,
    fill: { color: L_GREY }, shadow: makeCardShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: 8.5, y: 1.35, w: 0.06, h: 5.0, fill: { color: AMBER } });

  slide.addText("Category Breakdown", {
    x: 8.8, y: 1.5, w: 3.7, h: 0.3,
    fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: NAVY, margin: 0
  });

  const catBullets = data.search_term_waste.by_category.map(cat => ([
    { text: `${cat.Category}: `, options: { bold: true, breakLine: false, fontSize: F.BODY, color: NAVY } },
    { text: `£${cat.Cost.toFixed(0)} (${cat.Clicks} clicks)`, options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
  ])).flat();
  catBullets.push(
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Action Required:", options: { bold: true, breakLine: true, fontSize: F.BODY, color: RED } },
    { text: "Add phrase-match negative keywords for each category", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Review 'Other' category for additional patterns", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Set up weekly search term reviews", options: { bullet: true, fontSize: F.BODY, color: BLACK } },
  );

  slide.addText(catBullets, {
    x: 8.8, y: 1.9, w: 3.7, h: 4.2,
    fontFace: "Calibri", margin: 0, valign: "top", paraSpaceAfter: 4
  });

  addFooter(slide, 4);
}

// ═══════════════════════════════════════════
// SLIDE 5: NEGATIVE KEYWORD GAPS
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "Negative Keyword Gaps",
    "Protection gaps that allow irrelevant traffic through");

  const nk = data.negative_keywords;

  // LEFT
  slide.addShape(pres.shapes.RECTANGLE, {
    x: MARGIN, y: 1.35, w: 5.6, h: 4.8,
    fill: { color: L_GREY }, shadow: makeCardShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN, y: 1.35, w: 0.06, h: 4.8, fill: { color: GREEN } });

  slide.addText("Currently Blocked", {
    x: MARGIN + 0.25, y: 1.45, w: 5, h: 0.35,
    fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: GREEN, margin: 0
  });
  slide.addText(`${nk.total_main + nk.total_details} total negative keywords`, {
    x: MARGIN + 0.25, y: 1.85, w: 5, h: 0.25,
    fontSize: F.BODY, fontFace: "Calibri", color: BLACK, margin: 0
  });

  const matchItems = [
    { text: `Exact match: ${nk.exact_count} keywords`, options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: `Broad match: ${nk.broad_count} keywords`, options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: `Phrase match: ${nk.phrase_count} keywords`, options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Examples (exact match):", options: { bold: true, breakLine: true, fontSize: F.BODY, color: NAVY } },
  ];
  nk.examples_exact.slice(0, 6).forEach(kw => {
    matchItems.push({ text: kw, options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } });
  });
  slide.addText(matchItems, {
    x: MARGIN + 0.25, y: 2.2, w: 5, h: 3.5,
    fontFace: "Calibri", margin: 0, valign: "top", paraSpaceAfter: 3
  });

  // RIGHT
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 6.8, y: 1.35, w: 5.9, h: 4.8,
    fill: { color: WHITE }, shadow: makeCardShadow(),
    line: { color: RED, width: 1.5 }
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: 6.8, y: 1.35, w: 0.06, h: 4.8, fill: { color: RED } });

  slide.addText("Should Be Blocked", {
    x: 7.1, y: 1.45, w: 5.3, h: 0.35,
    fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: RED, margin: 0
  });
  slide.addText("Recommended additions based on search term analysis", {
    x: 7.1, y: 1.85, w: 5.3, h: 0.25,
    fontSize: F.BODY, fontFace: "Calibri", color: BLACK, margin: 0
  });

  slide.addText([
    { text: 'Phrase match negatives for:', options: { bold: true, breakLine: true, fontSize: F.BODY, color: NAVY } },
    { text: '"planning permission" (wrong service)', options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: '"planning consultant" / "planning advisor"', options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: '"template" / "example" / "sample"', options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: '"how to write" / "DIY"', options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: '"neighbour dispute" / "fence" / "boundary"', options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: '"job" / "career" / "salary"', options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Critical Issue:", options: { bold: true, breakLine: true, fontSize: F.BODY, color: RED } },
    { text: `${nk.exact_count} of ${nk.total_main} negatives use exact match only. This means a negative for [planning consultant] won't block "planning consultants" (plural) or "best planning consultant near me".`, options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Switch to phrase match for broader protection.", options: { bold: true, fontSize: F.BODY, color: NAVY } },
  ], {
    x: 7.1, y: 2.2, w: 5.3, h: 3.5,
    fontFace: "Calibri", margin: 0, valign: "top", paraSpaceAfter: 3
  });

  addFooter(slide, 5);
}

// ═══════════════════════════════════════════
// SLIDE 6: AD GROUP PERFORMANCE
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "Ad Group Performance",
    `£${data.ad_groups.zero_conv_spend.toFixed(0)} spent on ad groups with zero conversions`);

  let agHeader = [[
    { text: "Ad Group", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY } },
    { text: "Spend", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY, align: "center" } },
    { text: "Clicks", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY, align: "center" } },
    { text: "Conversions", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY, align: "center" } },
    { text: "CPA", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY, align: "center" } },
    { text: "Status", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY, align: "center" } },
  ]];

  let agRows = data.ad_groups.data.map((ag, i) => {
    const isWaste = ag.Conversions === 0;
    const bgColor = isWaste ? "FCE8E6" : (i%2===0 ? L_GREY : WHITE);
    return [
      { text: ag["Ad group"], options: { fill: { color: bgColor }, fontSize: F.BODY, color: BLACK, bold: isWaste } },
      { text: `£${ag.Cost.toFixed(0)}`, options: { fill: { color: bgColor }, fontSize: F.BODY, align: "center", color: isWaste ? RED : BLACK } },
      { text: String(Math.round(ag.Clicks)), options: { fill: { color: bgColor }, fontSize: F.BODY, align: "center", color: BLACK } },
      { text: String(Math.round(ag.Conversions)), options: { fill: { color: bgColor }, fontSize: F.BODY, align: "center", color: isWaste ? RED : GREEN, bold: true } },
      { text: ag.CPA ? `£${parseFloat(ag.CPA).toFixed(2)}` : "N/A", options: { fill: { color: bgColor }, fontSize: F.BODY, align: "center", color: BLACK } },
      { text: isWaste ? "WASTE" : "Active", options: { fill: { color: bgColor }, fontSize: F.BODY, align: "center", color: isWaste ? RED : GREEN, bold: true } },
    ];
  });

  slide.addTable([...agHeader, ...agRows], {
    x: MARGIN, y: 1.45, w: W - 2*MARGIN, h: 2.2,
    colW: [4.5, 1.5, 1.3, 1.7, 1.5, 1.5],
    border: { type: "solid", pt: 0.5, color: "E2E8F0" },
    rowH: 0.42, margin: [4, 8, 4, 8],
  });

  // Left card
  slide.addShape(pres.shapes.RECTANGLE, {
    x: MARGIN, y: 4.1, w: 5.8, h: 2.3,
    fill: { color: "FCE8E6" }, shadow: makeCardShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN, y: 4.1, w: 0.06, h: 2.3, fill: { color: RED } });
  slide.addText("Neighbourhood Objections", {
    x: MARGIN + 0.25, y: 4.2, w: 5.2, h: 0.3,
    fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: RED, margin: 0
  });
  slide.addText([
    { text: "Created in October 2025 as part of a restructure, but has never generated a single conversion.", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "With only £79 spent, the waste is small — but the ad group fragments the campaign's data, making it harder for the algorithm to optimise.", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Recommendation: Pause this ad group and consolidate volume.", options: { bold: true, fontSize: F.BODY, color: NAVY } },
  ], {
    x: MARGIN + 0.25, y: 4.55, w: 5.2, h: 1.7,
    fontFace: "Calibri", margin: 0, valign: "top"
  });

  // Right card
  const mainAgPct = ((data.ad_groups.data[0].Cost / data.total_spend) * 100).toFixed(0);
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 6.8, y: 4.1, w: 5.9, h: 2.3,
    fill: { color: L_GREY }, shadow: makeCardShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: 6.8, y: 4.1, w: 0.06, h: 2.3, fill: { color: BLUE } });
  slide.addText("Volume Concentration", {
    x: 7.1, y: 4.2, w: 5.3, h: 0.3,
    fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: NAVY, margin: 0
  });
  slide.addText([
    { text: `${mainAgPct}% of all spend`, options: { bold: true, breakLine: true, fontSize: F.STAT, color: BLUE } },
    { text: 'goes through the "Planning Objections" ad group.', options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "The three smaller ad groups account for just 5% of spend combined. This fragmentation means the algorithm never gets enough data to optimise.", options: { fontSize: F.BODY, color: BLACK } },
  ], {
    x: 7.1, y: 4.55, w: 5.3, h: 1.7,
    fontFace: "Calibri", margin: 0, valign: "top"
  });

  addFooter(slide, 6);
}

// ═══════════════════════════════════════════
// SLIDE 7: TIME OF DAY
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "Time-of-Day Performance",
    `£${data.hour_of_day.zero_conv_spend.toFixed(0)} spent during hours with zero conversions`);

  slide.addImage({ path: path.join(CHART_DIR, "hour_of_day.png"), x: MARGIN, y: 1.3, w: 8.5, h: 4.0 });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 9.3, y: 1.3, w: 3.4, h: 4.0,
    fill: { color: L_GREY }, shadow: makeCardShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: 9.3, y: 1.3, w: 0.06, h: 4.0, fill: { color: NAVY } });

  slide.addText("Key Findings", {
    x: 9.55, y: 1.45, w: 3, h: 0.3,
    fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: NAVY, margin: 0
  });

  const hourData = data.hour_of_day.data.filter(h => h.Conversions >= 15).sort((a, b) =>
    (a.Cost / a.Conversions) - (b.Cost / b.Conversions));
  const bestHour = hourData[0];
  const bestHourCPA = bestHour ? (bestHour.Cost / bestHour.Conversions).toFixed(2) : "N/A";
  const bestHourConvs = bestHour ? Math.round(bestHour.Conversions) : 0;

  slide.addText([
    { text: "Dead zone: 1am", options: { bold: true, breakLine: true, fontSize: F.BODY, color: RED } },
    { text: `£${data.hour_of_day.zero_conv_spend.toFixed(0)} spent with 0 conversions`, options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: `Best hour: ${bestHour ? bestHour["Hour of the day"] + ":00" : "N/A"}`, options: { bold: true, breakLine: true, fontSize: F.BODY, color: GREEN } },
    { text: `CPA £${bestHourCPA} (${bestHourConvs} conversions)`, options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Peak performance:", options: { bold: true, breakLine: true, fontSize: F.BODY, color: NAVY } },
    { text: "9am-6pm business hours show the strongest conversion volume.", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Recommendation:", options: { bold: true, breakLine: true, fontSize: F.BODY, color: BLUE } },
    { text: "Reduce bids during off-peak hours (midnight-6am). Increase bids during peak business hours.", options: { fontSize: F.BODY, color: BLACK } },
  ], {
    x: 9.55, y: 1.85, w: 3, h: 3.3,
    fontFace: "Calibri", margin: 0, valign: "top", paraSpaceAfter: 2
  });

  slide.addText("Red = zero conversions  |  Amber = low (<10)  |  Blue = active  |  Line = conversions", {
    x: MARGIN, y: 5.5, w: 8, h: 0.25,
    fontSize: F.BODY, fontFace: "Calibri", color: NAVY, margin: 0
  });

  addFooter(slide, 7);
}

// ═══════════════════════════════════════════
// SLIDE 8: DAY OF WEEK
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "Day-of-Week Performance",
    `Sunday CPA £${data.day_of_week.sunday_cpa} vs £${data.day_of_week.avg_weekday_cpa} weekday avg — ${((data.day_of_week.sunday_cpa / data.day_of_week.avg_weekday_cpa - 1) * 100).toFixed(0)}% premium`);

  slide.addImage({ path: path.join(CHART_DIR, "day_of_week.png"), x: MARGIN, y: 1.3, w: 8.5, h: 4.0 });

  const dowData = data.day_of_week.data;
  const monday = dowData.find(d => d["Day of the week"] === "Monday");
  const sunday = dowData.find(d => d["Day of the week"] === "Sunday");

  // Monday card
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 9.3, y: 1.3, w: 3.4, h: 1.5,
    fill: { color: "E6F4EA" }, shadow: makeCardShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: 9.3, y: 1.3, w: 0.06, h: 1.5, fill: { color: GREEN } });
  slide.addText("Monday (Best)", {
    x: 9.55, y: 1.4, w: 3, h: 0.25,
    fontSize: F.BODY, fontFace: "Calibri", bold: true, color: GREEN, margin: 0
  });
  slide.addText([
    { text: `${Math.round(monday.Conversions)} conversions`, options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: `CPA: £${(monday.Cost / monday.Conversions).toFixed(2)}`, options: { breakLine: true, fontSize: F.BODY, color: GREEN, bold: true } },
    { text: `Conv rate: ${(monday.Conversions / monday.Clicks * 100).toFixed(1)}%`, options: { fontSize: F.BODY, color: BLACK } },
  ], { x: 9.55, y: 1.7, w: 3, h: 0.9, fontFace: "Calibri", margin: 0, valign: "top" });

  // Sunday card
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 9.3, y: 3.0, w: 3.4, h: 1.5,
    fill: { color: "FCE8E6" }, shadow: makeCardShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: 9.3, y: 3.0, w: 0.06, h: 1.5, fill: { color: RED } });
  slide.addText("Sunday (Worst)", {
    x: 9.55, y: 3.1, w: 3, h: 0.25,
    fontSize: F.BODY, fontFace: "Calibri", bold: true, color: RED, margin: 0
  });
  slide.addText([
    { text: `${Math.round(sunday.Conversions)} conversions`, options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: `CPA: £${data.day_of_week.sunday_cpa}`, options: { breakLine: true, fontSize: F.BODY, color: RED, bold: true } },
    { text: `Premium: £${data.day_of_week.sunday_excess.toFixed(0)} excess spend`, options: { fontSize: F.BODY, color: RED } },
  ], { x: 9.55, y: 3.4, w: 3, h: 0.9, fontFace: "Calibri", margin: 0, valign: "top" });

  // Recommendation
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 9.3, y: 4.7, w: 3.4, h: 1.1,
    fill: { color: L_GREY }, shadow: makeCardShadow()
  });
  slide.addText([
    { text: "Recommendation", options: { bold: true, breakLine: true, fontSize: F.BODY, color: NAVY } },
    { text: "Reduce Sunday bids by 20-30%. Increase Monday/Wednesday bids where CPA is lowest.", options: { fontSize: F.BODY, color: BLACK } },
  ], { x: 9.55, y: 4.8, w: 3, h: 0.9, fontFace: "Calibri", margin: 0, valign: "top" });

  addFooter(slide, 8);
}

// ═══════════════════════════════════════════
// SLIDE 9: DEVICE PERFORMANCE
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "Device Performance", null);
  slide.addText("GLO Campaign — performance and current bid adjustments by device", {
    x: MARGIN, y: 0.8, w: 7, h: 0.25,
    fontSize: F.BODY, fontFace: "Calibri", color: BLACK, margin: 0
  });

  let devHeader = [[
    { text: "Device", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY } },
    { text: "Spend", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY, align: "center" } },
    { text: "Clicks", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY, align: "center" } },
    { text: "Conv.", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY, align: "center" } },
    { text: "CPA", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY, align: "center" } },
    { text: "Conv Rate", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY, align: "center" } },
    { text: "Bid Adj.", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY, align: "center" } },
  ]];

  const devData = data.device.data;
  const bidAdj = data.device.bid_adjustments;
  let devRows = devData.map((dev, i) => {
    const bg = i%2===0 ? L_GREY : WHITE;
    const cpa = dev.CPA ? parseFloat(dev.CPA) : null;
    const bestCPA = Math.min(...devData.filter(d => d.CPA).map(d => parseFloat(d.CPA)));
    const cpaColor = cpa === bestCPA ? GREEN : BLACK;
    return [
      { text: dev.Device, options: { fill: { color: bg }, fontSize: F.BODY, color: BLACK, bold: true } },
      { text: `£${dev.Cost.toLocaleString()}`, options: { fill: { color: bg }, fontSize: F.BODY, align: "center", color: BLACK } },
      { text: String(Math.round(dev.Clicks)), options: { fill: { color: bg }, fontSize: F.BODY, align: "center", color: BLACK } },
      { text: String(Math.round(dev.Conversions)), options: { fill: { color: bg }, fontSize: F.BODY, align: "center", color: BLACK } },
      { text: cpa ? `£${cpa.toFixed(2)}` : "N/A", options: { fill: { color: bg }, fontSize: F.BODY, align: "center", color: cpaColor, bold: true } },
      { text: `${dev["Conv Rate"].toFixed(1)}%`, options: { fill: { color: bg }, fontSize: F.BODY, align: "center", color: BLACK } },
      { text: bidAdj[dev.Device] || "--", options: { fill: { color: bg }, fontSize: F.BODY, align: "center", color: NAVY, bold: true } },
    ];
  });

  slide.addTable([...devHeader, ...devRows], {
    x: MARGIN, y: 1.3, w: W - 2*MARGIN, h: 1.8,
    colW: [2.5, 1.7, 1.3, 1.3, 1.5, 1.5, 1.9],
    border: { type: "solid", pt: 0.5, color: "E2E8F0" },
    rowH: 0.42, margin: [4, 8, 4, 8],
  });

  slide.addImage({ path: path.join(CHART_DIR, "device_performance.png"), x: MARGIN, y: 3.4, w: 6.5, h: 3.0 });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 7.5, y: 3.4, w: 5.2, h: 3.0,
    fill: { color: L_GREY }, shadow: makeCardShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: 7.5, y: 3.4, w: 0.06, h: 3.0, fill: { color: BLUE } });

  slide.addText("Analysis", {
    x: 7.8, y: 3.5, w: 4.7, h: 0.3,
    fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: NAVY, margin: 0
  });
  slide.addText([
    { text: "Mobile has the best CPA (£32.24) but the highest spend — this is positive.", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Current bid adjustments (+10% mobile, +10% desktop, -20% tablet) are reasonable but could be refined.", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Tablets have the weakest conversion rate (5.0%) and highest CPA.", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Recommendation: Reduce tablet bids to -30% or -40%.", options: { bold: true, fontSize: F.BODY, color: NAVY } },
  ], {
    x: 7.8, y: 3.85, w: 4.7, h: 2.3,
    fontFace: "Calibri", margin: 0, valign: "top", paraSpaceAfter: 2
  });

  addFooter(slide, 9);
}

// ═══════════════════════════════════════════
// SLIDE 10: GEOGRAPHIC WASTE
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "Geographic Waste",
    `895+ locations spent £${data.geographic.total_waste.toLocaleString()} with zero conversions`);

  slide.addImage({ path: path.join(CHART_DIR, "geographic_waste.png"), x: MARGIN, y: 1.3, w: 7.5, h: 4.5 });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 8.5, y: 1.3, w: 4.2, h: 3.0,
    fill: { color: L_GREY }, shadow: makeCardShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: 8.5, y: 1.3, w: 0.06, h: 3.0, fill: { color: RED } });

  slide.addText("Key Finding", {
    x: 8.8, y: 1.45, w: 3.7, h: 0.3,
    fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: NAVY, margin: 0
  });
  slide.addText([
    { text: `£${data.geographic.total_waste.toLocaleString()} — ${((data.geographic.total_waste / data.total_spend) * 100).toFixed(0)}% of total spend — went to locations that never converted.`, options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "While individual amounts are small, the cumulative waste across 895+ locations is the largest single waste category.", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "This is typical of UK-wide targeting without geographic bid adjustments.", options: { fontSize: F.BODY, color: BLACK } },
  ], {
    x: 8.8, y: 1.85, w: 3.7, h: 2.3,
    fontFace: "Calibri", margin: 0, valign: "top"
  });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 8.5, y: 4.55, w: 4.2, h: 1.7,
    fill: { color: "E8F0FE" }, shadow: makeCardShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: 8.5, y: 4.55, w: 0.06, h: 1.7, fill: { color: BLUE } });

  slide.addText("Recommendations", {
    x: 8.8, y: 4.65, w: 3.7, h: 0.25,
    fontSize: F.BODY, fontFace: "Calibri", bold: true, color: NAVY, margin: 0
  });
  slide.addText([
    { text: "Identify top-converting regions and increase bids there", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Exclude consistently non-converting areas", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Add location bid adjustments to focus budget on proven areas", options: { bullet: true, fontSize: F.BODY, color: BLACK } },
  ], {
    x: 8.8, y: 4.95, w: 3.7, h: 1.1,
    fontFace: "Calibri", margin: 0, valign: "top", paraSpaceAfter: 4
  });

  addFooter(slide, 10);
}

// ═══════════════════════════════════════════
// SLIDE 11: TOTAL WASTE SUMMARY (Option 4 style — light grey)
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: L_GREY };
  addStripeBar(slide, 0, 0.06);

  // Blue left accent
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0.06, w: 0.12, h: 7.44, fill: { color: BLUE } });

  slide.addText("Total Waste Summary", {
    x: 0.6, y: 0.3, w: 7, h: 0.5,
    fontSize: F.TITLE, fontFace: "Calibri", bold: true, color: NAVY, margin: 0
  });

  // Timeframe badge
  slide.addShape(pres.shapes.RECTANGLE, {
    x: W - MARGIN - 3.6, y: 0.3, w: 3.6, h: 0.45,
    fill: { color: WHITE }, line: { color: BLUE, width: 1 }
  });
  slide.addText(`Data: ${TIMEFRAME_SHORT}`, {
    x: W - MARGIN - 3.5, y: 0.32, w: 3.4, h: 0.4,
    fontSize: F.BODY, fontFace: "Calibri", color: BLUE, align: "center", valign: "middle", bold: true, margin: 0
  });

  // Big stat card
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 1.0, w: 7, h: 1.5,
    fill: { color: WHITE }, shadow: makeCardShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 1.0, w: 0.08, h: 1.5, fill: { color: RED } });
  slide.addText(`£${data.total_waste.toLocaleString()}`, {
    x: 0.9, y: 1.05, w: 4, h: 0.8,
    fontSize: F.HERO, fontFace: "Calibri", bold: true, color: RED, margin: 0
  });
  slide.addText(`of your £${data.total_spend.toLocaleString()} (${data.waste_pct}%) was spent on non-converting traffic`, {
    x: 0.9, y: 1.85, w: 6.5, h: 0.4,
    fontSize: F.SECTION, fontFace: "Calibri", color: BLACK, margin: 0
  });

  // Waterfall chart
  slide.addImage({ path: path.join(CHART_DIR, "waste_waterfall.png"), x: 0.6, y: 2.8, w: 7, h: 3.5 });

  // Right side - breakdown cards
  const catEntries = Object.entries(data.waste_categories);
  let yPos = 1.0;
  catEntries.forEach(([cat, val]) => {
    const pct = ((val / data.total_waste) * 100).toFixed(0);
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 8.2, y: yPos, w: 4.5, h: 0.75,
      fill: { color: WHITE }, shadow: makeCardShadow()
    });
    slide.addShape(pres.shapes.RECTANGLE, { x: 8.2, y: yPos, w: 0.06, h: 0.75, fill: { color: RED } });
    slide.addText(cat, {
      x: 8.5, y: yPos + 0.05, w: 2.8, h: 0.25,
      fontSize: F.BODY, fontFace: "Calibri", color: BLACK, margin: 0
    });
    slide.addText(`£${val.toLocaleString()}`, {
      x: 8.5, y: yPos + 0.35, w: 2, h: 0.3,
      fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: RED, margin: 0
    });
    slide.addText(`${pct}%`, {
      x: 11.5, y: yPos + 0.12, w: 1, h: 0.45,
      fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: NAVY, align: "center", margin: 0
    });
    yPos += 0.88;
  });

  slide.addText("Note: Some overlap exists between categories. The total represents the upper bound of identifiable waste.", {
    x: 8.2, y: yPos + 0.15, w: 4.5, h: 0.5,
    fontSize: F.BODY, fontFace: "Calibri", color: NAVY, italic: true, margin: 0
  });

  addFooter(slide, 11);
}

// ═══════════════════════════════════════════
// SLIDE 12: QUICK WINS
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "Quick Wins",
    "Immediate actions to reduce waste and improve performance");

  const wins = [
    { num: "1", title: "Add Phrase-Match Negative Keywords",
      desc: "Block DIY/templates, wrong services, jobs, neighbourhood disputes. Switch from exact to phrase match for broader protection.",
      impact: "£100-150/mo" },
    { num: "2", title: "Pause Neighbourhood Objections",
      desc: "Zero conversions, fragmenting campaign data. Consolidate volume into the main Planning Objections ad group.",
      impact: "£5-10/mo" },
    { num: "3", title: "Ad Schedule Bid Adjustments",
      desc: "Reduce bids during dead hours (1-5am) by 50-80%. Increase bids during peak hours (9am-5pm Mon-Fri).",
      impact: "£30-50/mo" },
    { num: "4", title: "Reduce Sunday Bids 20-30%",
      desc: `Sunday CPA (£${data.day_of_week.sunday_cpa}) is ${((data.day_of_week.sunday_cpa / data.day_of_week.avg_weekday_cpa - 1) * 100).toFixed(0)}% higher than weekdays. Apply a bid reduction to control costs.`,
      impact: "£35-50/mo" },
    { num: "5", title: "Tighten Geographic Targeting",
      desc: "Exclude consistently non-converting regions. Add location bid adjustments to focus budget on proven areas.",
      impact: "£200-380/mo" },
    { num: "6", title: "Adjust Tablet Bids to -30%",
      desc: "Weakest conversion rate (5.0%) and highest CPA. Increase bid reduction from the current -20%.",
      impact: "£15-25/mo" },
  ];

  // ── 2-column x 3-row card grid ──
  // Key fix: cards are tall enough for 2 lines of desc (1.05"), savings always bottom-right
  const leftCol = MARGIN;
  const rightCol = 6.95;
  const cardW = 6.05;
  const cardH = 1.05;
  const gap = 0.15;
  const yStart = 1.3;

  wins.forEach((win, i) => {
    const col = i % 2 === 0 ? leftCol : rightCol;
    const row = Math.floor(i / 2);
    const y = yStart + row * (cardH + gap);

    // Card bg
    slide.addShape(pres.shapes.RECTANGLE, {
      x: col, y, w: cardW, h: cardH,
      fill: { color: WHITE }, shadow: makeCardShadow(),
      line: { color: "E2E8F0", width: 0.5 }
    });

    // Number circle (blue, consistent)
    slide.addShape(pres.shapes.OVAL, {
      x: col + 0.15, y: y + 0.28, w: 0.45, h: 0.45,
      fill: { color: BLUE }
    });
    slide.addText(win.num, {
      x: col + 0.15, y: y + 0.28, w: 0.45, h: 0.45,
      fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: WHITE,
      align: "center", valign: "middle", margin: 0
    });

    // Title — single line
    slide.addText(win.title, {
      x: col + 0.72, y: y + 0.08, w: cardW - 2.6, h: 0.3,
      fontSize: F.BODY, fontFace: "Calibri", bold: true, color: NAVY, margin: 0, valign: "middle"
    });

    // Description — 2 lines allowed
    slide.addText(win.desc, {
      x: col + 0.72, y: y + 0.4, w: cardW - 2.6, h: 0.55,
      fontSize: F.BODY, fontFace: "Calibri", color: BLACK, margin: 0, valign: "top"
    });

    // Savings — always pinned to right side, vertically centred
    slide.addShape(pres.shapes.RECTANGLE, {
      x: col + cardW - 1.65, y: y + 0.15, w: 1.5, h: 0.75,
      fill: { color: "E6F4EA" }
    });
    slide.addText(win.impact, {
      x: col + cardW - 1.65, y: y + 0.15, w: 1.5, h: 0.75,
      fontSize: F.BODY, fontFace: "Calibri", bold: true, color: GREEN,
      align: "center", valign: "middle", margin: 0
    });
  });

  // ── Bottom: three summary stat cards ──
  const sumY = yStart + 3 * (cardH + gap) + 0.15;
  const sumW = (W - 2*MARGIN - 0.6) / 3;
  const sumH = 1.1;

  // Monthly savings
  slide.addShape(pres.shapes.RECTANGLE, {
    x: MARGIN, y: sumY, w: sumW, h: sumH,
    fill: { color: WHITE }, shadow: makeCardShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN, y: sumY, w: 0.06, h: sumH, fill: { color: GREEN } });
  slide.addText("Estimated Monthly Savings", {
    x: MARGIN + 0.2, y: sumY + 0.08, w: sumW - 0.3, h: 0.3,
    fontSize: F.BODY, fontFace: "Calibri", color: BLACK, margin: 0
  });
  slide.addText("£380-655/month", {
    x: MARGIN + 0.2, y: sumY + 0.4, w: sumW - 0.3, h: 0.5,
    fontSize: F.STAT, fontFace: "Calibri", bold: true, color: GREEN, margin: 0
  });

  // Annualised
  const s2x = MARGIN + sumW + 0.3;
  slide.addShape(pres.shapes.RECTANGLE, {
    x: s2x, y: sumY, w: sumW, h: sumH,
    fill: { color: WHITE }, shadow: makeCardShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: s2x, y: sumY, w: 0.06, h: sumH, fill: { color: BLUE } });
  slide.addText("Annualised Saving", {
    x: s2x + 0.2, y: sumY + 0.08, w: sumW - 0.3, h: 0.3,
    fontSize: F.BODY, fontFace: "Calibri", color: BLACK, margin: 0
  });
  slide.addText("£4,560-7,860/year", {
    x: s2x + 0.2, y: sumY + 0.4, w: sumW - 0.3, h: 0.5,
    fontSize: F.STAT, fontFace: "Calibri", bold: true, color: BLUE, margin: 0
  });

  // What's next
  const s3x = MARGIN + 2*(sumW + 0.3);
  slide.addShape(pres.shapes.RECTANGLE, {
    x: s3x, y: sumY, w: sumW, h: sumH,
    fill: { color: NAVY }
  });
  slide.addText("What's Next?", {
    x: s3x + 0.2, y: sumY + 0.08, w: sumW - 0.3, h: 0.3,
    fontSize: F.BODY, fontFace: "Calibri", color: WHITE, bold: true, margin: 0
  });
  slide.addText([
    { text: "Report 2: Account Structure & Issues", options: { breakLine: true, fontSize: F.BODY, color: WHITE } },
    { text: "Why costs increased after October 2025", options: { fontSize: F.BODY, color: GREEN } },
  ], {
    x: s3x + 0.2, y: sumY + 0.4, w: sumW - 0.3, h: 0.5,
    fontFace: "Calibri", margin: 0, valign: "top"
  });

  addFooter(slide, 12);
}

// ── Save ──
pres.writeFile({ fileName: OUTPUT }).then(() => {
  console.log(`Report saved to: ${OUTPUT}`);
}).catch(err => console.error("Error:", err));
