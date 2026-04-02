const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const data = JSON.parse(fs.readFileSync(path.join(__dirname, "analysis_report2.json"), "utf8"));
const CHART_DIR = path.join(__dirname, "charts");
const OUTPUT = path.join(__dirname, "reports", "02_account_structure_report_v2.pptx");

// ── Colours ──
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
pres.title = "Account Structure & Issues \u2014 Objection Experts";
const W = 13.33, MARGIN = 0.6;

function addStripeBar(slide, y, h) {
  const sW = W / 4;
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y, w: sW, h, fill: { color: BLUE } });
  slide.addShape(pres.shapes.RECTANGLE, { x: sW, y, w: sW, h, fill: { color: RED } });
  slide.addShape(pres.shapes.RECTANGLE, { x: sW*2, y, w: sW, h, fill: { color: AMBER } });
  slide.addShape(pres.shapes.RECTANGLE, { x: sW*3, y, w: sW, h, fill: { color: GREEN } });
}

function addFooter(slide, pageNum) {
  const barY = 6.92, barW = (W - 2*MARGIN) / 4;
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN, y: barY, w: barW, h: 0.03, fill: { color: BLUE } });
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN + barW, y: barY, w: barW, h: 0.03, fill: { color: RED } });
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN + barW*2, y: barY, w: barW, h: 0.03, fill: { color: AMBER } });
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN + barW*3, y: barY, w: barW, h: 0.03, fill: { color: GREEN } });
  slide.addImage({ path: LOGO_PATH, x: MARGIN, y: 7.0, w: 0.22, h: 0.22 });
  slide.addText([
    { text: "Christopher Hoole", options: { bold: true, color: NAVY } },
    { text: "  |  christopherhoole.com  |  Confidential", options: { color: BLACK } },
  ], { x: MARGIN + 0.3, y: 7.0, w: 6, h: 0.25, fontSize: F.FOOTER, fontFace: "Calibri", valign: "middle" });
  slide.addText(String(pageNum), {
    x: W - MARGIN - 0.5, y: 7.0, w: 0.5, h: 0.25,
    fontSize: F.FOOTER, color: NAVY, fontFace: "Calibri", align: "right", valign: "middle"
  });
}

function addStatCard(slide, x, y, w, h, value, label, accentColor) {
  slide.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: WHITE }, shadow: makeCardShadow(), line: { color: "E2E8F0", width: 0.5 } });
  slide.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.06, h, fill: { color: accentColor } });
  slide.addText(value, { x: x+0.2, y: y+0.1, w: w-0.3, h: 0.5, fontSize: F.STAT, fontFace: "Calibri", bold: true, color: accentColor, margin: 0 });
  slide.addText(label, { x: x+0.2, y: y+0.6, w: w-0.3, h: 0.35, fontSize: F.BODY, fontFace: "Calibri", color: BLACK, margin: 0 });
}

function addSlideTitle(slide, title, subtitle) {
  addStripeBar(slide, 0, 0.06);
  slide.addText(title, { x: MARGIN, y: 0.3, w: 7, h: 0.5, fontSize: F.TITLE, fontFace: "Calibri", bold: true, color: NAVY, margin: 0 });
  slide.addShape(pres.shapes.RECTANGLE, { x: W-MARGIN-3.6, y: 0.3, w: 3.6, h: 0.45, fill: { color: WHITE }, line: { color: BLUE, width: 1 } });
  slide.addText(`Data: ${TIMEFRAME_SHORT}`, { x: W-MARGIN-3.5, y: 0.32, w: 3.4, h: 0.4, fontSize: F.BODY, fontFace: "Calibri", color: BLUE, align: "center", valign: "middle", bold: true, margin: 0 });
  if (subtitle) {
    slide.addText(subtitle, { x: MARGIN, y: 0.85, w: 9, h: 0.3, fontSize: F.BODY, fontFace: "Calibri", color: RED, margin: 0 });
  }
}

const pre = data.before_after.pre;
const post = data.before_after.post;

// ═══════════════════════════════════════════
// SLIDE 1: TITLE
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: L_GREY };
  addStripeBar(slide, 0, 0.07);
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0.07, w: 0.12, h: 7.43, fill: { color: BLUE } });

  slide.addImage({ path: LOGO_PATH, x: 0.6, y: 0.5, w: 0.65, h: 0.65 });

  slide.addText("ACCOUNT STRUCTURE\n& ISSUES", {
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

  slide.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 5.5, w: 4.5, h: 0.5, fill: { color: WHITE }, line: { color: BLUE, width: 1 } });
  slide.addText(`Data period: Jan 2025 \u2014 Mar 2026 (15 months)`, {
    x: 0.7, y: 5.52, w: 4.3, h: 0.45,
    fontSize: F.BODY, fontFace: "Calibri", color: BLUE, bold: true, valign: "middle", margin: 0
  });

  // Right side — key stat
  const rX = 6.8, rW = 5.9;
  slide.addShape(pres.shapes.RECTANGLE, { x: rX, y: 0.5, w: rW, h: 2.5, fill: { color: WHITE }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: rX, y: 0.5, w: 0.08, h: 2.5, fill: { color: RED } });
  slide.addText(`CPA increased ${((post.cpa / pre.cpa - 1) * 100).toFixed(0)}%`, {
    x: rX + 0.3, y: 0.7, w: rW - 0.5, h: 0.9,
    fontSize: F.HERO - 4, fontFace: "Calibri", bold: true, color: RED, margin: 0
  });
  slide.addText("After Agency Change", {
    x: rX + 0.3, y: 1.5, w: rW - 0.5, h: 0.35,
    fontSize: F.SECTION, fontFace: "Calibri", color: NAVY, margin: 0
  });
  slide.addText(`From \u00A3${pre.cpa} to \u00A3${post.cpa} per conversion`, {
    x: rX + 0.3, y: 1.9, w: rW - 0.5, h: 0.3,
    fontSize: F.BODY, fontFace: "Calibri", color: BLACK, margin: 0
  });

  // Before/after mini cards
  const smW = (rW - 0.2) / 2;
  // Before
  slide.addShape(pres.shapes.RECTANGLE, { x: rX, y: 3.2, w: smW, h: 1.15, fill: { color: WHITE }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: rX, y: 3.2, w: 0.06, h: 1.15, fill: { color: GREEN } });
  slide.addText("Before (Jan-Sep 2025)", { x: rX+0.15, y: 3.25, w: smW-0.25, h: 0.25, fontSize: F.BODY, fontFace: "Calibri", color: GREEN, bold: true, margin: 0 });
  slide.addText(`CPA: \u00A3${pre.cpa}`, { x: rX+0.15, y: 3.55, w: smW-0.25, h: 0.35, fontSize: F.STAT-4, fontFace: "Calibri", bold: true, color: GREEN, margin: 0 });
  slide.addText(`Conv rate: ${pre.conv_rate}%`, { x: rX+0.15, y: 3.9, w: smW-0.25, h: 0.25, fontSize: F.BODY, fontFace: "Calibri", color: BLACK, margin: 0 });

  // After
  const sm2X = rX + smW + 0.2;
  slide.addShape(pres.shapes.RECTANGLE, { x: sm2X, y: 3.2, w: smW, h: 1.15, fill: { color: WHITE }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: sm2X, y: 3.2, w: 0.06, h: 1.15, fill: { color: RED } });
  slide.addText("After (Oct 2025-Mar 2026)", { x: sm2X+0.15, y: 3.25, w: smW-0.25, h: 0.25, fontSize: F.BODY, fontFace: "Calibri", color: RED, bold: true, margin: 0 });
  slide.addText(`CPA: \u00A3${post.cpa}`, { x: sm2X+0.15, y: 3.55, w: smW-0.25, h: 0.35, fontSize: F.STAT-4, fontFace: "Calibri", bold: true, color: RED, margin: 0 });
  slide.addText(`Conv rate: ${post.conv_rate}%`, { x: sm2X+0.15, y: 3.9, w: smW-0.25, h: 0.25, fontSize: F.BODY, fontFace: "Calibri", color: BLACK, margin: 0 });

  addStripeBar(slide, 7.0, 0.04);
}

// ═══════════════════════════════════════════
// SLIDE 2: EXECUTIVE SUMMARY
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "Executive Summary", null);

  addStatCard(slide, MARGIN, 1.2, 2.8, 1.05, `\u00A3${pre.cpa} \u2192 \u00A3${post.cpa}`, "CPA Increase (+28%)", RED);
  addStatCard(slide, MARGIN+3.1, 1.2, 2.8, 1.05, `${pre.conv_rate}% \u2192 ${post.conv_rate}%`, "Conv Rate Decline", AMBER);
  addStatCard(slide, MARGIN+6.2, 1.2, 2.8, 1.05, `2-3 / 10`, "Avg Quality Score", RED);
  addStatCard(slide, MARGIN+9.3, 1.2, 2.8, 1.05, `No Target`, "CPA Guardrail", NAVY);

  slide.addText("Key Issues Identified", {
    x: MARGIN, y: 2.6, w: 6, h: 0.35,
    fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: NAVY, margin: 0
  });

  slide.addText([
    { text: `Average CPA increased 28% after the agency change in October 2025 (\u00A3${pre.cpa} \u2192 \u00A3${post.cpa}), with monthly CPA peaking at \u00A365 in March 2026`, options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: `Conversion rate dropped from ${pre.conv_rate}% to ${post.conv_rate}% \u2014 a 22% decline`, options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Bid strategy set to Maximise Conversions with no target CPA \u2014 the algorithm has no cost guardrails", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Email Click is counted as a Primary conversion, inflating reported numbers and misleading the algorithm", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: `Quality Scores of 2-3 out of 10 on most keywords \u2014 paying a significant premium on every click`, options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Auto-apply recommendations were enabled \u2014 Google made bid strategy changes without human oversight", options: { bullet: true, fontSize: F.BODY, color: BLACK } },
  ], {
    x: MARGIN + 0.1, y: 3.0, w: 11.5, h: 3.2,
    fontFace: "Calibri", paraSpaceAfter: 6, margin: 0, valign: "top"
  });

  addFooter(slide, 2);
}

// ═══════════════════════════════════════════
// SLIDE 3: THE BEFORE & AFTER STORY
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "The Before & After Story",
    "Performance comparison: pre vs post agency change (October 2025)");

  // Before card
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN, y: 1.3, w: 5.8, h: 4.5, fill: { color: "E6F4EA" }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN, y: 1.3, w: 0.08, h: 4.5, fill: { color: GREEN } });
  slide.addText("BEFORE", { x: MARGIN+0.3, y: 1.4, w: 5, h: 0.4, fontSize: F.STAT, fontFace: "Calibri", bold: true, color: GREEN, margin: 0 });
  slide.addText("January \u2014 September 2025 (40 weeks)", { x: MARGIN+0.3, y: 1.85, w: 5, h: 0.25, fontSize: F.BODY, fontFace: "Calibri", color: BLACK, margin: 0 });

  const preMetrics = [
    [`\u00A3${pre.cpa}`, "Cost Per Conversion"],
    [`${pre.conv_rate}%`, "Conversion Rate"],
    [`\u00A3${pre.avg_cpc}`, "Average CPC"],
    [`\u00A3${pre.avg_weekly_spend}`, "Avg Weekly Spend"],
    [`${pre.conversions}`, "Total Conversions"],
    [`${pre.clicks}`, "Total Clicks"],
  ];
  preMetrics.forEach(([val, label], i) => {
    const y = 2.3 + i * 0.6;
    slide.addText(val, { x: MARGIN+0.3, y, w: 2.2, h: 0.4, fontSize: F.STAT-2, fontFace: "Calibri", bold: true, color: GREEN, margin: 0 });
    slide.addText(label, { x: MARGIN+2.6, y: y+0.05, w: 3, h: 0.3, fontSize: F.BODY, fontFace: "Calibri", color: BLACK, margin: 0 });
  });

  // After card
  slide.addShape(pres.shapes.RECTANGLE, { x: 6.9, y: 1.3, w: 5.8, h: 4.5, fill: { color: "FCE8E6" }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: 6.9, y: 1.3, w: 0.08, h: 4.5, fill: { color: RED } });
  slide.addText("AFTER", { x: 7.2, y: 1.4, w: 5, h: 0.4, fontSize: F.STAT, fontFace: "Calibri", bold: true, color: RED, margin: 0 });
  slide.addText("October 2025 \u2014 March 2026 (25 weeks, post agency change)", { x: 7.2, y: 1.85, w: 5, h: 0.25, fontSize: F.BODY, fontFace: "Calibri", color: BLACK, margin: 0 });

  const postMetrics = [
    [`\u00A3${post.cpa}`, "Cost Per Conversion", `+${((post.cpa/pre.cpa-1)*100).toFixed(0)}%`],
    [`${post.conv_rate}%`, "Conversion Rate", `${((post.conv_rate/pre.conv_rate-1)*100).toFixed(0)}%`],
    [`\u00A3${post.avg_cpc}`, "Average CPC", `${((post.avg_cpc/pre.avg_cpc-1)*100).toFixed(0)}%`],
    [`\u00A3${post.avg_weekly_spend}`, "Avg Weekly Spend", `+${((post.avg_weekly_spend/pre.avg_weekly_spend-1)*100).toFixed(0)}%`],
    [`${post.conversions}`, "Total Conversions", `${((post.conversions/pre.conversions-1)*100).toFixed(0)}%`],
    [`${post.clicks}`, "Total Clicks", `${((post.clicks/pre.clicks-1)*100).toFixed(0)}%`],
  ];
  postMetrics.forEach(([val, label, change], i) => {
    const y = 2.3 + i * 0.6;
    slide.addText(val, { x: 7.2, y, w: 2.2, h: 0.4, fontSize: F.STAT-2, fontFace: "Calibri", bold: true, color: RED, margin: 0 });
    slide.addText(label, { x: 9.5, y: y+0.05, w: 2, h: 0.3, fontSize: F.BODY, fontFace: "Calibri", color: BLACK, margin: 0 });
    slide.addText(change, { x: 11.5, y: y+0.05, w: 1, h: 0.3, fontSize: F.BODY, fontFace: "Calibri", bold: true, color: RED, align: "right", margin: 0 });
  });

  // Bottom note
  slide.addText("Note: Post-October period is 25 weeks vs 40 weeks pre-October. Per-week metrics are used for fair comparison.", {
    x: MARGIN, y: 6.1, w: W-2*MARGIN, h: 0.3,
    fontSize: F.BODY, fontFace: "Calibri", color: NAVY, italic: true, margin: 0
  });

  addFooter(slide, 3);
}

// ═══════════════════════════════════════════
// SLIDE 4: CPA TREND
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "Cost Per Conversion Trend",
    `CPA volatility increased significantly after the agency change`);

  slide.addImage({ path: path.join(CHART_DIR, "cpa_over_time.png"), x: MARGIN, y: 1.3, w: 8.5, h: 4.2 });

  slide.addShape(pres.shapes.RECTANGLE, { x: 9.3, y: 1.3, w: 3.4, h: 4.2, fill: { color: L_GREY }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: 9.3, y: 1.3, w: 0.06, h: 4.2, fill: { color: NAVY } });

  slide.addText("Key Findings", { x: 9.55, y: 1.45, w: 3, h: 0.3, fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: NAVY, margin: 0 });
  slide.addText([
    { text: `Pre-Oct 2025 CPA: \u00A3${pre.cpa}`, options: { bold: true, breakLine: true, fontSize: F.BODY, color: GREEN } },
    { text: `Post-Oct 2025 CPA: \u00A3${post.cpa}`, options: { bold: true, breakLine: true, fontSize: F.BODY, color: RED } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "The chart shows clear CPA volatility after October. Some weeks spike above \u00A360-80 while others remain normal.", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: 'This matches the client\'s experience: "some weeks are fine, then the algorithm just goes crazy."', options: { breakLine: true, fontSize: F.BODY, color: BLACK, italic: true } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Root cause:", options: { bold: true, breakLine: true, fontSize: F.BODY, color: NAVY } },
    { text: "Maximise Conversions with no target CPA. The algorithm has no cost guardrail.", options: { fontSize: F.BODY, color: BLACK } },
  ], { x: 9.55, y: 1.85, w: 3, h: 3.5, fontFace: "Calibri", margin: 0, valign: "top", paraSpaceAfter: 2 });

  addFooter(slide, 4);
}

// ═══════════════════════════════════════════
// SLIDE 5: MONTHLY CPA BREAKDOWN
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "Monthly CPA Breakdown",
    "Month-by-month cost per conversion shows the full volatility picture");

  slide.addImage({ path: path.join(CHART_DIR, "monthly_cpa.png"), x: MARGIN, y: 1.3, w: 8.5, h: 4.2 });

  slide.addShape(pres.shapes.RECTANGLE, { x: 9.3, y: 1.3, w: 3.4, h: 4.2, fill: { color: L_GREY }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: 9.3, y: 1.3, w: 0.06, h: 4.2, fill: { color: NAVY } });

  slide.addText("Monthly Context", { x: 9.55, y: 1.45, w: 3, h: 0.3, fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: NAVY, margin: 0 });
  slide.addText([
    { text: "Best month:", options: { bold: true, breakLine: true, fontSize: F.BODY, color: GREEN } },
    { text: "April 2025: \u00A322 CPA", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Worst month:", options: { bold: true, breakLine: true, fontSize: F.BODY, color: RED } },
    { text: "March 2026: \u00A365 CPA", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Period averages:", options: { bold: true, breakLine: true, fontSize: F.BODY, color: NAVY } },
    { text: `Jan-Sep 2025: \u00A3${pre.cpa}`, options: { breakLine: true, fontSize: F.BODY, color: GREEN } },
    { text: `Oct 2025-Mar 2026: \u00A3${post.cpa}`, options: { breakLine: true, fontSize: F.BODY, color: RED } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "The averages mask significant month-to-month swings. Post-October, CPA ranges from \u00A327 to \u00A365 \u2014 this volatility is the core problem.", options: { fontSize: F.BODY, color: BLACK } },
  ], { x: 9.55, y: 1.85, w: 3, h: 3.5, fontFace: "Calibri", margin: 0, valign: "top", paraSpaceAfter: 2 });

  addFooter(slide, 5);
}

// ═══════════════════════════════════════════
// SLIDE 6: CONVERSION RATE TREND (was 5)
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "Conversion Rate Trend",
    `Conversion rate declined from ${pre.conv_rate}% to ${post.conv_rate}% after the agency change`);

  slide.addImage({ path: path.join(CHART_DIR, "conv_rate_over_time.png"), x: MARGIN, y: 1.3, w: 8.5, h: 4.2 });

  slide.addShape(pres.shapes.RECTANGLE, { x: 9.3, y: 1.3, w: 3.4, h: 4.2, fill: { color: L_GREY }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: 9.3, y: 1.3, w: 0.06, h: 4.2, fill: { color: NAVY } });

  slide.addText("Analysis", { x: 9.55, y: 1.45, w: 3, h: 0.3, fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: NAVY, margin: 0 });
  slide.addText([
    { text: `Pre-Oct 2025: ${pre.conv_rate}%`, options: { bold: true, breakLine: true, fontSize: F.BODY, color: GREEN } },
    { text: `Post-Oct 2025: ${post.conv_rate}%`, options: { bold: true, breakLine: true, fontSize: F.BODY, color: RED } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "A declining conversion rate means more clicks are being wasted \u2014 the traffic quality has deteriorated.", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Contributing factors:", options: { bold: true, breakLine: true, fontSize: F.BODY, color: NAVY } },
    { text: "Low Quality Scores reducing ad relevance", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Ad group fragmentation splitting data", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Negative keyword gaps letting irrelevant traffic through", options: { bullet: true, fontSize: F.BODY, color: BLACK } },
  ], { x: 9.55, y: 1.85, w: 3, h: 3.5, fontFace: "Calibri", margin: 0, valign: "top", paraSpaceAfter: 2 });

  addFooter(slide, 6);
}

// ═══════════════════════════════════════════
// SLIDE 6: BID STRATEGY ANALYSIS
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "Bid Strategy Analysis",
    "Maximise Conversions with no stable target CPA");

  // Current strategy card
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN, y: 1.3, w: 5.8, h: 2.5, fill: { color: "FCE8E6" }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN, y: 1.3, w: 0.06, h: 2.5, fill: { color: RED } });
  slide.addText("Current Setup", { x: MARGIN+0.25, y: 1.4, w: 5, h: 0.3, fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: RED, margin: 0 });
  slide.addText([
    { text: "Strategy: Maximise Conversions", options: { bold: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Target CPA: None set", options: { bold: true, breakLine: true, fontSize: F.BODY, color: RED } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Without a target CPA, Google's algorithm has permission to spend any amount per conversion. This is the primary driver of the cost volatility.", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "The algorithm will chase conversions at any price, leading to unpredictable weekly costs.", options: { fontSize: F.BODY, color: BLACK } },
  ], { x: MARGIN+0.25, y: 1.75, w: 5.2, h: 1.9, fontFace: "Calibri", margin: 0, valign: "top" });

  // Timeline card
  slide.addShape(pres.shapes.RECTANGLE, { x: 6.8, y: 1.3, w: 5.9, h: 2.5, fill: { color: L_GREY }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: 6.8, y: 1.3, w: 0.06, h: 2.5, fill: { color: NAVY } });
  slide.addText("Bid Strategy Timeline", { x: 7.1, y: 1.4, w: 5, h: 0.3, fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: NAVY, margin: 0 });
  slide.addText([
    { text: "7 Oct 2025: ", options: { bold: true, color: NAVY } },
    { text: "Target CPA set to \u00A330", options: { breakLine: true, color: BLACK } },
    { text: "30 Oct 2025: ", options: { bold: true, color: NAVY } },
    { text: "Target CPA raised to \u00A338.65 (+29%)", options: { breakLine: true, color: RED } },
    { text: "Oct 2025: ", options: { bold: true, color: NAVY } },
    { text: "Auto-apply recommendations enabled", options: { breakLine: true, color: RED } },
    { text: "28 Mar 2026: ", options: { bold: true, color: NAVY } },
    { text: "Google auto-changed strategy to Max Conv Value (reversed same day)", options: { breakLine: true, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "The target CPA was raised within 3 weeks, and auto-apply gave Google control over bid strategy changes.", options: { bold: true, fontSize: F.BODY, color: NAVY } },
  ], { x: 7.1, y: 1.75, w: 5.4, h: 1.9, fontSize: F.BODY, fontFace: "Calibri", margin: 0, valign: "top" });

  // What it should be
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN, y: 4.1, w: W-2*MARGIN, h: 1.5, fill: { color: "E8F0FE" }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN, y: 4.1, w: 0.06, h: 1.5, fill: { color: BLUE } });
  slide.addText("What Should Happen", { x: MARGIN+0.25, y: 4.2, w: 5, h: 0.3, fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: BLUE, margin: 0 });
  slide.addText([
    { text: "Set a target CPA based on the pre-October baseline (\u00A325-30). This gives the algorithm a guardrail \u2014 it will still optimise for conversions, but won't overspend on low-quality clicks.", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Disable auto-apply recommendations. These allow Google to make bid strategy changes without human oversight.", options: { fontSize: F.BODY, color: BLACK } },
  ], { x: MARGIN+0.25, y: 4.55, w: W-2*MARGIN-0.5, h: 0.9, fontFace: "Calibri", margin: 0, valign: "top" });

  addFooter(slide, 7);
}

// ═══════════════════════════════════════════
// SLIDE 7: WHAT CHANGED AT TAKEOVER
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "What Changed at Takeover",
    "Key account changes made in September\u2014October 2025");

  // Timeline events as a vertical list
  const events = [
    { date: "25 Sep", desc: "Created new RSAs, call-only ads, call extension. Added 101 negative exact match keywords.", color: BLUE },
    { date: "3 Oct", desc: "Restructured ad groups \u2014 split into Planning Objection Letters, Consultants, Neighbourhood Objections. Mass-paused ~15 phrase match keywords.", color: AMBER },
    { date: "3 Oct", desc: "New ad copy created with spelling errors (later corrected): Planinng, Guidence, Counsil, Distruptive, propery.", color: RED },
    { date: "7 Oct", desc: "Target CPA set to \u00A330.", color: GREEN },
    { date: "9 Oct", desc: "Turned on Search Partners + Display Network, then reversed same day. Added 6 image extensions, removed 4 same day.", color: AMBER },
    { date: "9 Oct", desc: "Enabled auto-apply recommendations including bid strategy changes.", color: RED },
    { date: "13 Oct", desc: "Device bid adjustments: Mobile +30%, Desktop +10%, Tablet -20%. Ad schedule bid adjustments added.", color: BLUE },
    { date: "30 Oct", desc: "Raised Target CPA from \u00A330 to \u00A338.65 (+29%). Removed all headline pins from main RSA.", color: RED },
  ];

  // Two columns of events
  events.forEach((ev, i) => {
    const col = i < 4 ? MARGIN : 6.8;
    const row = i < 4 ? i : i - 4;
    const y = 1.3 + row * 1.25;

    slide.addShape(pres.shapes.RECTANGLE, { x: col, y, w: 5.9, h: 1.1, fill: { color: WHITE }, shadow: makeCardShadow(), line: { color: "E2E8F0", width: 0.5 } });
    slide.addShape(pres.shapes.RECTANGLE, { x: col, y, w: 0.06, h: 1.1, fill: { color: ev.color } });

    slide.addText(ev.date, { x: col+0.2, y: y+0.08, w: 1.2, h: 0.3, fontSize: F.BODY, fontFace: "Calibri", bold: true, color: ev.color, margin: 0 });
    slide.addText(ev.desc, { x: col+0.2, y: y+0.4, w: 5.4, h: 0.6, fontSize: F.BODY, fontFace: "Calibri", color: BLACK, margin: 0 });
  });

  // Bottom note
  slide.addText("Note: The account owner (Owen) has been actively adding negative keywords throughout both agency periods \u2014 demonstrating engagement and suggesting the agency wasn't doing this proactively.", {
    x: MARGIN, y: 6.15, w: W-2*MARGIN, h: 0.4,
    fontSize: F.BODY, fontFace: "Calibri", color: NAVY, italic: true, margin: 0
  });

  addFooter(slide, 8);
}

// ═══════════════════════════════════════════
// SLIDE 8: CONVERSION TRACKING ISSUES
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "Conversion Tracking Issues",
    "Email Click is inflating reported conversion numbers");

  const cv = data.conversion_actions;

  // Conversion actions table
  let tblH = [[
    { text: "Conversion Action", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY } },
    { text: "Type", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY, align: "center" } },
    { text: "Count", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY, align: "center" } },
    { text: "Designation", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY, align: "center" } },
    { text: "Issue?", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: F.BODY, align: "center" } },
  ]];

  const convRows = [
    ["Form Submission", "Website form", "464", "Primary", ""],
    ["Google Forwarding Number", "Phone call", "26", "Primary", ""],
    ["Email Click", "Email link click", "17", "Primary", "PROBLEM"],
    ["Phone Number Click", "Phone link click", "45", "Secondary", ""],
  ];
  let tblR = convRows.map((row, i) => {
    const isIssue = row[4] === "PROBLEM";
    const bg = isIssue ? "FCE8E6" : (i%2===0 ? L_GREY : WHITE);
    return row.map((cell, j) => ({
      text: cell,
      options: {
        fill: { color: bg }, fontSize: F.BODY, color: isIssue && j >= 3 ? RED : BLACK,
        bold: isIssue && j >= 3, align: j > 0 ? "center" : "left"
      }
    }));
  });

  slide.addTable([...tblH, ...tblR], {
    x: MARGIN, y: 1.3, w: W-2*MARGIN, h: 2.2,
    colW: [3.5, 2, 1.5, 2, 2.5],
    border: { type: "solid", pt: 0.5, color: "E2E8F0" },
    rowH: 0.42, margin: [4, 8, 4, 8],
  });

  // Impact cards
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN, y: 3.8, w: 5.8, h: 2.5, fill: { color: "FCE8E6" }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN, y: 3.8, w: 0.06, h: 2.5, fill: { color: RED } });
  slide.addText("The Problem", { x: MARGIN+0.25, y: 3.9, w: 5, h: 0.3, fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: RED, margin: 0 });
  slide.addText([
    { text: "Email Click is set as a Primary conversion and included in account-level goals.", options: { breakLine: true, fontSize: F.BODY, color: BLACK, bold: true } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "This is a micro-conversion \u2014 someone clicking an email link, not submitting a form or making a call. It's not a real lead.", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Because it's marked Primary, the bidding algorithm optimises toward these low-quality actions alongside genuine leads.", options: { fontSize: F.BODY, color: BLACK } },
  ], { x: MARGIN+0.25, y: 4.25, w: 5.2, h: 1.9, fontFace: "Calibri", margin: 0, valign: "top" });

  // Impact numbers
  slide.addShape(pres.shapes.RECTANGLE, { x: 6.8, y: 3.8, w: 5.9, h: 2.5, fill: { color: L_GREY }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: 6.8, y: 3.8, w: 0.06, h: 2.5, fill: { color: NAVY } });
  slide.addText("The Impact", { x: 7.1, y: 3.9, w: 5, h: 0.3, fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: NAVY, margin: 0 });
  slide.addText([
    { text: "Reported conversions: ", options: { color: BLACK } },
    { text: `${cv.total_reported}`, options: { bold: true, breakLine: true, color: BLACK } },
    { text: "Real conversions (forms + calls): ", options: { color: BLACK } },
    { text: `${cv.real_conversions}`, options: { bold: true, breakLine: true, color: GREEN } },
    { text: "Inflated by: ", options: { color: BLACK } },
    { text: `${cv.inflated_by} false conversions`, options: { bold: true, breakLine: true, color: RED } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: `Reported CPA: \u00A3${(18338/cv.total_reported).toFixed(0)}`, options: { breakLine: true, color: BLACK } },
    { text: `True CPA: \u00A3${(18338/cv.real_conversions).toFixed(0)}`, options: { bold: true, breakLine: true, color: RED } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "The true cost per lead is higher than reported.", options: { bold: true, color: NAVY } },
  ], { x: 7.1, y: 4.25, w: 5.4, h: 1.9, fontSize: F.BODY, fontFace: "Calibri", margin: 0, valign: "top" });

  addFooter(slide, 9);
}

// ═══════════════════════════════════════════
// SLIDE 9: QUALITY SCORE ANALYSIS
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "Quality Score Analysis",
    `Average Quality Score: ${data.quality_scores.mean} out of 10`);

  slide.addImage({ path: path.join(CHART_DIR, "quality_score_dist.png"), x: MARGIN, y: 1.3, w: 7, h: 4.0 });

  slide.addShape(pres.shapes.RECTANGLE, { x: 8, y: 1.3, w: 4.7, h: 4.0, fill: { color: L_GREY }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: 8, y: 1.3, w: 0.06, h: 4.0, fill: { color: RED } });

  slide.addText("What This Means", { x: 8.3, y: 1.45, w: 4, h: 0.3, fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: NAVY, margin: 0 });
  slide.addText([
    { text: `${data.quality_scores.poor_pct}% of keywords`, options: { bold: true, breakLine: true, fontSize: F.BODY, color: RED } },
    { text: "have a Quality Score of 3 or below.", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Quality Score is Google's rating of your ad relevance (1-10). It directly impacts how much you pay per click.", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "The QS Tax:", options: { bold: true, breakLine: true, fontSize: F.BODY, color: RED } },
    { text: "At QS 2-3, you're paying an estimated 2-4x more per click than a competitor with QS 7-8 for the same keyword.", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Improving from QS 3 to QS 7 could reduce click costs by 30-50%.", options: { bold: true, fontSize: F.BODY, color: GREEN } },
  ], { x: 8.3, y: 1.85, w: 4.2, h: 3.3, fontFace: "Calibri", margin: 0, valign: "top", paraSpaceAfter: 2 });

  // QS components note
  slide.addText("Quality Score is determined by: Expected CTR + Ad Relevance + Landing Page Experience", {
    x: MARGIN, y: 5.6, w: W-2*MARGIN, h: 0.3,
    fontSize: F.BODY, fontFace: "Calibri", color: NAVY, margin: 0
  });

  addFooter(slide, 10);
}

// ═══════════════════════════════════════════
// SLIDE 10: ACCOUNT STRUCTURE
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "Account Structure Overview", null);

  // Campaign tree - simplified visual
  // GLO Campaign box
  slide.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 1.5, w: 3, h: 0.7, fill: { color: NAVY } });
  slide.addText("GLO Campaign (Search)", { x: 0.8, y: 1.5, w: 3, h: 0.4, fontSize: F.BODY, fontFace: "Calibri", color: WHITE, bold: true, align: "center", valign: "middle", margin: 0 });
  slide.addText("\u00A318,333 spend | 95% of budget", { x: 0.8, y: 1.9, w: 3, h: 0.3, fontSize: F.BODY, fontFace: "Calibri", color: WHITE, align: "center", margin: 0 });

  // Ad groups branching down
  const adGroups = [
    { name: "Planning Objections", spend: "\u00A317,413", pct: "95%", status: "Active", color: GREEN, y: 2.8 },
    { name: "Planning Objection Letters", spend: "\u00A3351", pct: "2%", status: "Low volume", color: AMBER, y: 3.8 },
    { name: "Planning Objection Consultants", spend: "\u00A3490", pct: "3%", status: "Low volume", color: AMBER, y: 4.8 },
    { name: "Neighbourhood Objections", spend: "\u00A379", pct: "0.4%", status: "0 conversions", color: RED, y: 5.8 },
  ];

  adGroups.forEach(ag => {
    // Connector line
    slide.addShape(pres.shapes.LINE, { x: 2.3, y: ag.y - 0.3, w: 0, h: 0.3, line: { color: "CBD5E1", width: 1 } });
    // Ad group card
    slide.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: ag.y, w: 3.4, h: 0.75, fill: { color: WHITE }, shadow: makeCardShadow(), line: { color: "E2E8F0", width: 0.5 } });
    slide.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: ag.y, w: 0.05, h: 0.75, fill: { color: ag.color } });
    slide.addText(ag.name, { x: 0.8, y: ag.y+0.05, w: 3, h: 0.3, fontSize: F.BODY, fontFace: "Calibri", bold: true, color: BLACK, margin: 0 });
    slide.addText(`${ag.spend} (${ag.pct}) \u2014 ${ag.status}`, { x: 0.8, y: ag.y+0.38, w: 3, h: 0.25, fontSize: F.BODY, fontFace: "Calibri", color: ag.color === RED ? RED : BLACK, margin: 0 });
  });

  // Other campaigns (dormant)
  slide.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 6.7, w: 3, h: 0.0, fill: { color: WHITE } }); // spacer

  // Right side - key findings
  slide.addShape(pres.shapes.RECTANGLE, { x: 5, y: 1.5, w: 7.7, h: 5.1, fill: { color: L_GREY }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: 5, y: 1.5, w: 0.06, h: 5.1, fill: { color: BLUE } });

  slide.addText("Structure Assessment", { x: 5.3, y: 1.6, w: 7, h: 0.3, fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: NAVY, margin: 0 });
  slide.addText([
    { text: "A simple structure isn't inherently bad for a \u00A31,500/month account.", options: { bold: true, breakLine: true, fontSize: F.BODY, color: NAVY } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "However, the October restructure created problems:", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Volume fragmentation: 95% of spend stays in one ad group. The other three never get enough data to optimise.", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Neighbourhood Objections has zero conversions \u2014 it should be paused.", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Multiple dormant campaigns (Lead Form Submissions, Planning Objection Letters campaign) add clutter.", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Other campaigns:", options: { bold: true, breakLine: true, fontSize: F.BODY, color: NAVY } },
    { text: "GLO - Core - PMax: Small Performance Max campaign (minimal spend)", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Lead Form Submissions: Dormant (\u00A30 spend)", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Planning Objection Letters (campaign): Appears dormant", options: { bullet: true, fontSize: F.BODY, color: BLACK } },
  ], { x: 5.3, y: 2.0, w: 7, h: 4.4, fontFace: "Calibri", margin: 0, valign: "top", paraSpaceAfter: 2 });

  addFooter(slide, 11);
}

// ═══════════════════════════════════════════
// SLIDE 11: AD COPY AUDIT
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "Ad Copy Audit",
    "3 RSAs + 1 call-only ad in the main ad group");

  // Ad performance table
  slide.addImage({ path: path.join(CHART_DIR, "ad_spend_distribution.png"), x: MARGIN, y: 1.3, w: 7, h: 3.5 });

  slide.addShape(pres.shapes.RECTANGLE, { x: 7.8, y: 1.3, w: 4.9, h: 3.5, fill: { color: L_GREY }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: 7.8, y: 1.3, w: 0.06, h: 3.5, fill: { color: NAVY } });

  slide.addText("Ad Performance", { x: 8.1, y: 1.45, w: 4.3, h: 0.3, fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: NAVY, margin: 0 });
  slide.addText([
    { text: "RSA 1 (keyword insertion): ", options: { bold: true, color: NAVY } },
    { text: "\u00A314,940 spend, CPA \u00A331.36", options: { breakLine: true, color: BLACK } },
    { text: "RSA 2 (Planning Objection Letter): ", options: { bold: true, color: NAVY } },
    { text: "\u00A31,604 spend, CPA \u00A343.07", options: { breakLine: true, color: BLACK } },
    { text: "RSA 3 (Planning Objection Help): ", options: { bold: true, color: NAVY } },
    { text: "\u00A3703 spend, CPA \u00A357.78", options: { breakLine: true, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "The keyword insertion RSA dominates (85% of spend) and has the best CPA. This is actually positive \u2014 it shows the algorithm learned which ad performs best.", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Having 3 RSAs is good practice \u2014 it allows testing. The opportunity is to improve the underperforming RSAs.", options: { fontSize: F.BODY, color: BLACK } },
  ], { x: 8.1, y: 1.85, w: 4.3, h: 2.8, fontSize: F.BODY, fontFace: "Calibri", margin: 0, valign: "top" });

  // Key issues
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN, y: 5.1, w: W-2*MARGIN, h: 1.3, fill: { color: "E8F0FE" }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN, y: 5.1, w: 0.06, h: 1.3, fill: { color: BLUE } });
  slide.addText("Observations", { x: MARGIN+0.25, y: 5.2, w: 5, h: 0.25, fontSize: F.BODY, fontFace: "Calibri", bold: true, color: NAVY, margin: 0 });
  slide.addText([
    { text: "Headline 1 uses {KeyWord:} insertion \u2014 can create awkward combinations with certain search terms", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Only Headline 14 is pinned (to position 3) \u2014 no headline pinning for positions 1-2", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Call-only ad has very low volume (49 clicks, 1 conversion) \u2014 insufficient data to evaluate", options: { bullet: true, fontSize: F.BODY, color: BLACK } },
  ], { x: MARGIN+0.25, y: 5.5, w: W-2*MARGIN-0.5, h: 0.8, fontFace: "Calibri", margin: 0, valign: "top", paraSpaceAfter: 3 });

  addFooter(slide, 12);
}

// ═══════════════════════════════════════════
// SLIDE 12: LANDING PAGE
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "Landing Page Assessment",
    "All ads point to the homepage (objectionexperts.com)");

  // Landing page mockup
  slide.addImage({ path: path.join(CHART_DIR, "landing_page_mockup.png"), x: MARGIN, y: 1.3, w: 5.5, h: 3.8, sizing: { type: "contain", w: 5.5, h: 3.8 } });
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN, y: 1.3, w: 5.5, h: 3.8, line: { color: "E2E8F0", width: 1 } });

  // Assessment
  slide.addShape(pres.shapes.RECTANGLE, { x: 6.6, y: 1.3, w: 6.1, h: 1.8, fill: { color: "E6F4EA" }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: 6.6, y: 1.3, w: 0.06, h: 1.8, fill: { color: GREEN } });
  slide.addText("Strengths", { x: 6.85, y: 1.4, w: 5.5, h: 0.25, fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: GREEN, margin: 0 });
  slide.addText([
    { text: "Clear headline and value proposition above the fold", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Strong trust signals: Trustpilot, RTPI qualified, Google reviews", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Social proof stats: 600+ objections, 25+ reviews, 85+ 5-star", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Lead form visible above the fold with clear CTA", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Testimonials, case studies, FAQ, and process explanation", options: { bullet: true, fontSize: F.BODY, color: BLACK } },
  ], { x: 6.85, y: 1.7, w: 5.6, h: 1.3, fontFace: "Calibri", margin: 0, valign: "top", paraSpaceAfter: 2 });

  slide.addShape(pres.shapes.RECTANGLE, { x: 6.6, y: 3.3, w: 6.1, h: 1.8, fill: { color: "E8F0FE" }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: 6.6, y: 3.3, w: 0.06, h: 1.8, fill: { color: BLUE } });
  slide.addText("Opportunities", { x: 6.85, y: 3.4, w: 5.5, h: 0.25, fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: BLUE, margin: 0 });
  slide.addText([
    { text: "A dedicated landing page (shorter, more focused) could improve QS and conversion rate", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Homepage has a lot of content below the fold \u2014 may distract from the primary CTA", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "A/B testing different landing page variants could yield conversion rate improvements", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "Mobile optimisation should be verified given 57% of traffic is mobile", options: { bullet: true, fontSize: F.BODY, color: BLACK } },
  ], { x: 6.85, y: 3.7, w: 5.6, h: 1.3, fontFace: "Calibri", margin: 0, valign: "top", paraSpaceAfter: 2 });

  slide.addText("Overall: This is a good landing page. The improvement opportunity is refinement, not overhaul.", {
    x: MARGIN, y: 5.4, w: W-2*MARGIN, h: 0.3,
    fontSize: F.BODY, fontFace: "Calibri", color: NAVY, bold: true, italic: true, margin: 0
  });

  addFooter(slide, 13);
}

// ═══════════════════════════════════════════
// SLIDE 13: AUDIENCE SETUP
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addSlideTitle(slide, "Audience Setup",
    "1,066 observation audiences applied \u2014 many are irrelevant");

  // Irrelevant examples
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN, y: 1.3, w: 5.8, h: 3.5, fill: { color: "FCE8E6" }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN, y: 1.3, w: 0.06, h: 3.5, fill: { color: RED } });
  slide.addText("Irrelevant Audiences Applied", { x: MARGIN+0.25, y: 1.4, w: 5, h: 0.3, fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: RED, margin: 0 });

  const irrelevant = [
    "GMC Motor Vehicles", "Horror Movie Fans", "Baseball Equipment",
    "Costumes", "Trips to Cincinnati", "Oil Changes",
    "Scooters & Mopeds", "Baseball Fans", "Bowling Equipment",
  ];
  slide.addText(irrelevant.map((a, i) => ({
    text: a, options: { bullet: true, breakLine: i < irrelevant.length - 1, fontSize: F.BODY, color: BLACK }
  })), { x: MARGIN+0.25, y: 1.8, w: 5.2, h: 2.8, fontFace: "Calibri", margin: 0, valign: "top", paraSpaceAfter: 4 });

  // Context
  slide.addShape(pres.shapes.RECTANGLE, { x: 6.8, y: 1.3, w: 5.9, h: 3.5, fill: { color: L_GREY }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: 6.8, y: 1.3, w: 0.06, h: 3.5, fill: { color: NAVY } });
  slide.addText("Context & Impact", { x: 7.1, y: 1.4, w: 5, h: 0.3, fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: NAVY, margin: 0 });
  slide.addText([
    { text: "These audiences are set to Observation mode, which means they don't restrict who sees the ads.", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "No money is being wasted.", options: { bold: true, breakLine: true, fontSize: F.BODY, color: GREEN } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "However, the selection shows a lack of strategic thinking. Relevant audiences for a planning objection service would include:", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Property buyers / home movers", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: NAVY } },
    { text: "Legal services seekers", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: NAVY } },
    { text: "Home improvement / renovation", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: NAVY } },
    { text: "Local council / planning related", options: { bullet: true, fontSize: F.BODY, color: NAVY } },
  ], { x: 7.1, y: 1.8, w: 5.4, h: 2.8, fontFace: "Calibri", margin: 0, valign: "top", paraSpaceAfter: 2 });

  // Bottom note
  slide.addText("Observation audiences are a data-gathering tool. The right audiences provide bid adjustment insights. The wrong audiences provide no actionable data.", {
    x: MARGIN, y: 5.1, w: W-2*MARGIN, h: 0.4,
    fontSize: F.BODY, fontFace: "Calibri", color: NAVY, italic: true, margin: 0
  });

  addFooter(slide, 14);
}

// ═══════════════════════════════════════════
// SLIDE 14: ISSUES SUMMARY
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: L_GREY };
  addStripeBar(slide, 0, 0.06);
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0.06, w: 0.12, h: 7.44, fill: { color: BLUE } });

  slide.addText("Issues Summary", { x: MARGIN, y: 0.3, w: 7, h: 0.5, fontSize: F.TITLE, fontFace: "Calibri", bold: true, color: NAVY, margin: 0 });
  slide.addShape(pres.shapes.RECTANGLE, { x: W-MARGIN-3.6, y: 0.3, w: 3.6, h: 0.45, fill: { color: WHITE }, line: { color: BLUE, width: 1 } });
  slide.addText(`Data: ${TIMEFRAME_SHORT}`, { x: W-MARGIN-3.5, y: 0.32, w: 3.4, h: 0.4, fontSize: F.BODY, fontFace: "Calibri", color: BLUE, align: "center", valign: "middle", bold: true, margin: 0 });

  // Three priority columns
  const colW = 3.8, colGap = 0.3;

  // CRITICAL
  const c1x = MARGIN;
  slide.addShape(pres.shapes.RECTANGLE, { x: c1x, y: 1.1, w: colW, h: 5.3, fill: { color: WHITE }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: c1x, y: 1.1, w: colW, h: 0.45, fill: { color: RED } });
  slide.addText("CRITICAL", { x: c1x, y: 1.1, w: colW, h: 0.45, fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
  slide.addText([
    { text: "No stable target CPA", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK, bold: true } },
    { text: "Algorithm has no cost guardrail", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Conversion tracking inflation", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK, bold: true } },
    { text: "Email Click counted as Primary", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Quality Scores of 2-3", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK, bold: true } },
    { text: "Paying 2-4x premium on clicks", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Auto-apply enabled", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK, bold: true } },
    { text: "Google making changes unsupervised", options: { fontSize: F.BODY, color: BLACK } },
  ], { x: c1x+0.2, y: 1.7, w: colW-0.4, h: 4.5, fontFace: "Calibri", margin: 0, valign: "top", paraSpaceAfter: 2 });

  // IMPORTANT
  const c2x = c1x + colW + colGap;
  slide.addShape(pres.shapes.RECTANGLE, { x: c2x, y: 1.1, w: colW, h: 5.3, fill: { color: WHITE }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: c2x, y: 1.1, w: colW, h: 0.45, fill: { color: AMBER } });
  slide.addText("IMPORTANT", { x: c2x, y: 1.1, w: colW, h: 0.45, fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: NAVY, align: "center", valign: "middle", margin: 0 });
  slide.addText([
    { text: "Negative keyword gaps", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK, bold: true } },
    { text: "Most use exact match only", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Volume fragmentation", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK, bold: true } },
    { text: "3 ad groups have insufficient data", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "CPA increase of 28%", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK, bold: true } },
    { text: `\u00A3${pre.cpa} \u2192 \u00A3${post.cpa} post-takeover`, options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "RSA testing opportunity", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK, bold: true } },
    { text: "2 of 3 RSAs underperforming", options: { fontSize: F.BODY, color: BLACK } },
  ], { x: c2x+0.2, y: 1.7, w: colW-0.4, h: 4.5, fontFace: "Calibri", margin: 0, valign: "top", paraSpaceAfter: 2 });

  // MINOR
  const c3x = c2x + colW + colGap;
  slide.addShape(pres.shapes.RECTANGLE, { x: c3x, y: 1.1, w: colW, h: 5.3, fill: { color: WHITE }, shadow: makeCardShadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x: c3x, y: 1.1, w: colW, h: 0.45, fill: { color: BLUE } });
  slide.addText("MINOR", { x: c3x, y: 1.1, w: colW, h: 0.45, fontSize: F.SECTION, fontFace: "Calibri", bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
  slide.addText([
    { text: "Irrelevant observation audiences", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK, bold: true } },
    { text: "No money wasted but no value either", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Dormant campaigns", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK, bold: true } },
    { text: "Lead Form, Planning Objection Letters", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Landing page refinement", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK, bold: true } },
    { text: "Good page, but a dedicated LP could improve QS", options: { breakLine: true, fontSize: F.BODY, color: BLACK } },
    { text: "", options: { breakLine: true, fontSize: 5 } },
    { text: "Call-only ad low volume", options: { bullet: true, breakLine: true, fontSize: F.BODY, color: BLACK, bold: true } },
    { text: "49 clicks, 1 conversion \u2014 inconclusive", options: { fontSize: F.BODY, color: BLACK } },
  ], { x: c3x+0.2, y: 1.7, w: colW-0.4, h: 4.5, fontFace: "Calibri", margin: 0, valign: "top", paraSpaceAfter: 2 });

  // Bottom CTA
  slide.addShape(pres.shapes.RECTANGLE, { x: MARGIN, y: 6.5, w: W-2*MARGIN, h: 0.35, fill: { color: NAVY } });
  slide.addText("Next: Report 3 \u2014 Restructure & Growth Plan", {
    x: MARGIN+0.3, y: 6.5, w: W-2*MARGIN-0.6, h: 0.35,
    fontSize: F.BODY, fontFace: "Calibri", color: GREEN, bold: true, align: "center", valign: "middle", margin: 0
  });

  addFooter(slide, 15);
}

// ── Save ──
pres.writeFile({ fileName: OUTPUT }).then(() => {
  console.log(`Report 2 saved to: ${OUTPUT}`);
}).catch(err => console.error("Error:", err));
