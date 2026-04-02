const pptxgen = require("pptxgenjs");
const path = require("path");

const CHART_DIR = path.join(__dirname, "charts");
const OUTPUT = path.join(__dirname, "reports", "bg_samples.pptx");
const LOGO_PATH = path.join(CHART_DIR, "act_logo.png");

const NAVY = "1A237E", BLUE = "4285F4", RED = "EA4335", AMBER = "FBBC05", GREEN = "34A853";
const WHITE = "FFFFFF", L_GREY = "F5F6FA", CHARCOAL = "2C3E50", BLACK = "1A1A1A";

let pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
const W = 13.33;

function addStripe(slide, y, h) {
  const s = W/4;
  slide.addShape(pres.shapes.RECTANGLE, {x:0,y,w:s,h,fill:{color:BLUE}});
  slide.addShape(pres.shapes.RECTANGLE, {x:s,y,w:s,h,fill:{color:RED}});
  slide.addShape(pres.shapes.RECTANGLE, {x:s*2,y,w:s,h,fill:{color:AMBER}});
  slide.addShape(pres.shapes.RECTANGLE, {x:s*3,y,w:s,h,fill:{color:GREEN}});
}

// ═══════════════════════════════════════════
// OPTION 1: White bg + navy accent panel right
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };
  addStripe(slide, 0, 0.07);

  slide.addText("OPTION 1: White + Navy Panel", {
    x: 0.6, y: 0.2, w: 6, h: 0.3,
    fontSize: 9, fontFace: "Calibri", color: CHARCOAL, italic: true, margin: 0
  });

  slide.addImage({ path: LOGO_PATH, x: 0.9, y: 0.6, w: 0.7, h: 0.7 });

  slide.addText("WASTE SPEND\nANALYSIS", {
    x: 0.9, y: 1.6, w: 6, h: 2.0,
    fontSize: 44, fontFace: "Calibri", bold: true, color: NAVY, margin: 0
  });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.9, y: 3.7, w: 2.5, h: 0.05, fill: { color: BLUE }
  });

  slide.addText("Objection Experts", {
    x: 0.9, y: 3.95, w: 6, h: 0.5,
    fontSize: 22, fontFace: "Calibri", color: BLUE, margin: 0
  });

  slide.addText([
    { text: "Prepared by Christopher Hoole", options: { breakLine: true, fontSize: 11, color: CHARCOAL } },
    { text: "Google Ads Specialist  |  March 2026", options: { breakLine: true, fontSize: 11, color: CHARCOAL } },
    { text: "christopherhoole.com", options: { fontSize: 11, color: BLUE } },
  ], { x: 0.9, y: 4.7, w: 6, h: 1.0, fontFace: "Calibri", margin: 0 });

  slide.addText("Data period: Jan 2025 — Mar 2026 (15 months)", {
    x: 0.9, y: 6.0, w: 5, h: 0.3,
    fontSize: 11, fontFace: "Calibri", color: CHARCOAL, margin: 0
  });

  // Navy panel on right
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 8.2, y: 0.07, w: 5.13, h: 7.43, fill: { color: NAVY }
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 8.2, y: 0.07, w: 0.06, h: 7.43, fill: { color: BLUE }
  });

  slide.addText("£7,836.55", {
    x: 8.5, y: 2.2, w: 4.5, h: 1.0,
    fontSize: 44, fontFace: "Calibri", bold: true, color: RED, align: "center", margin: 0
  });
  slide.addText("Identified Waste", {
    x: 8.5, y: 3.2, w: 4.5, h: 0.4,
    fontSize: 14, fontFace: "Calibri", color: WHITE, align: "center", margin: 0
  });
  const mx = 9.6;
  slide.addShape(pres.shapes.RECTANGLE, {x:mx,y:3.7,w:0.5,h:0.04,fill:{color:BLUE}});
  slide.addShape(pres.shapes.RECTANGLE, {x:mx+0.5,y:3.7,w:0.5,h:0.04,fill:{color:RED}});
  slide.addShape(pres.shapes.RECTANGLE, {x:mx+1,y:3.7,w:0.5,h:0.04,fill:{color:AMBER}});
  slide.addShape(pres.shapes.RECTANGLE, {x:mx+1.5,y:3.7,w:0.5,h:0.04,fill:{color:GREEN}});
  slide.addText("42.7% of total spend", {
    x: 8.5, y: 3.9, w: 4.5, h: 0.4,
    fontSize: 14, fontFace: "Calibri", color: BLUE, align: "center", margin: 0
  });
  slide.addText("out of £18,338.25 analysed", {
    x: 8.5, y: 4.4, w: 4.5, h: 0.3,
    fontSize: 11, fontFace: "Calibri", color: WHITE, align: "center", margin: 0, transparency: 30
  });
}

// ═══════════════════════════════════════════
// OPTION 2: Navy top fading to white bottom
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: WHITE };

  // Simulate gradient with stacked rectangles (navy -> lighter bands)
  slide.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:W, h:2.5, fill:{color: NAVY} });
  slide.addShape(pres.shapes.RECTANGLE, { x:0, y:2.5, w:W, h:1.0, fill:{color: "2A3590"} });
  slide.addShape(pres.shapes.RECTANGLE, { x:0, y:3.5, w:W, h:0.8, fill:{color: "4A55B0"} });
  slide.addShape(pres.shapes.RECTANGLE, { x:0, y:4.3, w:W, h:0.7, fill:{color: "8B93D1"} });
  slide.addShape(pres.shapes.RECTANGLE, { x:0, y:5.0, w:W, h:0.6, fill:{color: "C5C9E8"} });
  slide.addShape(pres.shapes.RECTANGLE, { x:0, y:5.6, w:W, h:1.9, fill:{color: "E8EAFA"} });
  addStripe(slide, 0, 0.07);

  slide.addText("OPTION 2: Navy Gradient to White", {
    x: 0.6, y: 0.2, w: 6, h: 0.3,
    fontSize: 9, fontFace: "Calibri", color: WHITE, italic: true, margin: 0, transparency: 40
  });

  slide.addImage({ path: LOGO_PATH, x: 0.9, y: 0.5, w: 0.6, h: 0.6 });

  slide.addText("WASTE SPEND ANALYSIS", {
    x: 0.9, y: 1.2, w: 7, h: 0.8,
    fontSize: 44, fontFace: "Calibri", bold: true, color: WHITE, margin: 0
  });

  slide.addText("Objection Experts", {
    x: 0.9, y: 2.1, w: 7, h: 0.5,
    fontSize: 22, fontFace: "Calibri", color: BLUE, margin: 0
  });

  // Stats in the middle transition zone
  const cardY = 3.2;
  const cW = 2.6, cH = 1.2, gap = 0.3;

  // Stat cards
  [{v:"£7,836.55",l:"Identified Waste",c:RED}, {v:"42.7%",l:"Of Budget Wasted",c:AMBER}, {v:"552",l:"Conversions",c:GREEN}, {v:"£18,338",l:"Total Spend",c:BLUE}].forEach((s, i) => {
    const cx = 0.9 + i * (cW + gap);
    slide.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: cardY, w: cW, h: cH,
      fill: { color: WHITE },
      shadow: { type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.15 }
    });
    slide.addShape(pres.shapes.RECTANGLE, { x: cx, y: cardY, w: 0.05, h: cH, fill: { color: s.c } });
    slide.addText(s.v, {
      x: cx + 0.15, y: cardY + 0.15, w: cW - 0.25, h: 0.5,
      fontSize: 22, fontFace: "Calibri", bold: true, color: s.c, margin: 0
    });
    slide.addText(s.l, {
      x: cx + 0.15, y: cardY + 0.7, w: cW - 0.25, h: 0.3,
      fontSize: 11, fontFace: "Calibri", color: CHARCOAL, margin: 0
    });
  });

  slide.addText([
    { text: "Prepared by Christopher Hoole  |  Google Ads Specialist  |  March 2026", options: { breakLine: true, fontSize: 11, color: CHARCOAL } },
    { text: "christopherhoole.com  |  Data period: Jan 2025 — Mar 2026", options: { fontSize: 11, color: BLUE } },
  ], { x: 0.9, y: 5.8, w: 8, h: 0.7, fontFace: "Calibri", margin: 0 });
}

// ═══════════════════════════════════════════
// OPTION 4: Light grey + bold coloured accents
// ═══════════════════════════════════════════
{
  let slide = pres.addSlide();
  slide.background = { color: L_GREY };
  addStripe(slide, 0, 0.07);

  slide.addText("OPTION 4: Light Grey + Bold Accents", {
    x: 0.6, y: 0.2, w: 6, h: 0.3,
    fontSize: 9, fontFace: "Calibri", color: CHARCOAL, italic: true, margin: 0
  });

  // Bold blue left accent strip
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0.07, w: 0.12, h: 7.43, fill: { color: BLUE }
  });

  slide.addImage({ path: LOGO_PATH, x: 0.6, y: 0.5, w: 0.65, h: 0.65 });

  slide.addText("WASTE SPEND\nANALYSIS", {
    x: 0.6, y: 1.4, w: 5.5, h: 1.8,
    fontSize: 44, fontFace: "Calibri", bold: true, color: NAVY, margin: 0
  });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 3.3, w: 2.5, h: 0.05, fill: { color: BLUE }
  });

  slide.addText("Objection Experts", {
    x: 0.6, y: 3.55, w: 5.5, h: 0.5,
    fontSize: 22, fontFace: "Calibri", color: BLUE, margin: 0
  });

  slide.addText([
    { text: "Prepared by Christopher Hoole", options: { breakLine: true, fontSize: 11, color: BLACK } },
    { text: "Google Ads Specialist  |  March 2026", options: { breakLine: true, fontSize: 11, color: CHARCOAL } },
    { text: "christopherhoole.com", options: { fontSize: 11, color: BLUE } },
  ], { x: 0.6, y: 4.3, w: 5.5, h: 1.0, fontFace: "Calibri", margin: 0 });

  slide.addText("Data period: Jan 2025 — Mar 2026 (15 months)", {
    x: 0.6, y: 5.5, w: 5, h: 0.3,
    fontSize: 11, fontFace: "Calibri", color: CHARCOAL, margin: 0
  });

  // Right side — 3 coloured stat cards stacked
  const rX = 6.8, rW = 5.9;

  // Red waste card (biggest)
  slide.addShape(pres.shapes.RECTANGLE, {
    x: rX, y: 0.5, w: rW, h: 2.5,
    fill: { color: WHITE },
    shadow: { type: "outer", blur: 10, offset: 3, angle: 135, color: "000000", opacity: 0.10 }
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: rX, y: 0.5, w: 0.08, h: 2.5, fill: { color: RED } });
  slide.addText("£7,836.55", {
    x: rX + 0.3, y: 0.7, w: rW - 0.5, h: 0.9,
    fontSize: 44, fontFace: "Calibri", bold: true, color: RED, margin: 0
  });
  slide.addText("Identified Waste", {
    x: rX + 0.3, y: 1.5, w: rW - 0.5, h: 0.35,
    fontSize: 14, fontFace: "Calibri", color: NAVY, margin: 0
  });
  slide.addText("42.7% of your £18,338 total spend", {
    x: rX + 0.3, y: 1.9, w: rW - 0.5, h: 0.3,
    fontSize: 11, fontFace: "Calibri", color: CHARCOAL, margin: 0
  });

  // Two smaller cards below
  const smW = (rW - 0.2) / 2;
  // Left: Conversions (green)
  slide.addShape(pres.shapes.RECTANGLE, {
    x: rX, y: 3.2, w: smW, h: 1.4,
    fill: { color: WHITE },
    shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.08 }
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: rX, y: 3.2, w: 0.06, h: 1.4, fill: { color: GREEN } });
  slide.addText("552", {
    x: rX + 0.2, y: 3.35, w: smW - 0.3, h: 0.5,
    fontSize: 22, fontFace: "Calibri", bold: true, color: GREEN, margin: 0
  });
  slide.addText("Total Conversions", {
    x: rX + 0.2, y: 3.9, w: smW - 0.3, h: 0.3,
    fontSize: 11, fontFace: "Calibri", color: CHARCOAL, margin: 0
  });

  // Right: Monthly savings (blue)
  slide.addShape(pres.shapes.RECTANGLE, {
    x: rX + smW + 0.2, y: 3.2, w: smW, h: 1.4,
    fill: { color: WHITE },
    shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.08 }
  });
  slide.addShape(pres.shapes.RECTANGLE, { x: rX + smW + 0.2, y: 3.2, w: 0.06, h: 1.4, fill: { color: BLUE } });
  slide.addText("£522/mo", {
    x: rX + smW + 0.4, y: 3.35, w: smW - 0.3, h: 0.5,
    fontSize: 22, fontFace: "Calibri", bold: true, color: BLUE, margin: 0
  });
  slide.addText("Est. Monthly Savings", {
    x: rX + smW + 0.4, y: 3.9, w: smW - 0.3, h: 0.3,
    fontSize: 11, fontFace: "Calibri", color: CHARCOAL, margin: 0
  });

  // Bottom colour bar accent
  addStripe(slide, 7.0, 0.04);
}

pres.writeFile({ fileName: OUTPUT }).then(() => {
  console.log(`Samples saved to: ${OUTPUT}`);
});
