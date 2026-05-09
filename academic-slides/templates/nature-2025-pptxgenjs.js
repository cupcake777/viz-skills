// Nature 2025 Academic PPT Template (pptxgenjs)
// Generates 10-slide Part 1 background report from a single paper.
// Adaptable to any paper: swap figures, text, and color scheme.
//
// DESIGN PRINCIPLES (user-validated):
//   - 10-12 pages max for background sections (not 18+)
//   - High information density: left 1/3 text card + right 2/3 panel grid
//   - Crop panels from main figures (never embed full multi-panel figures)
//   - Strict aspect ratio preservation via fitImage()
//   - Left text card uses colored border/fill for visual structure
//   - Panel labels (a/b/c/d) as small gray italic in top-left corner
//
// Usage: node generate_ppt.js
// Input:  figures/ directory with cropped panel PNGs
// Output: PPTX file

const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

// === Color Palette (Nature Academic) ===
const C = {
  primary: "1F2937", secondary: "4B5563", accent: "E64B35",
  blue: "3C5488", green: "00A087", bg: "FFFFFF", light: "F9FAFB",
  border: "E5E7EB", caption: "6B7280", white: "FFFFFF",
};

// === Layout Constants (16:9 = 10" × 5.625") ===
const W = 10, H = 5.625;
const MARGIN = 0.55;     // page margins
const CONTENT_TOP = 1.05; // content starts below title bar

// === Figure Helpers ===

// Read PNG as base64 for embedding
function imgB64(figDir, fname) {
  const p = path.join(figDir, fname);
  if (!fs.existsSync(p)) return null;
  return "image/png;base64," + fs.readFileSync(p).toString("base64");
}

// Calculate display dimensions preserving aspect ratio
function fitImage(srcW, srcH, maxW, maxH) {
  const ratio = Math.min(maxW / srcW, maxH / srcH);
  return { w: srcW * ratio, h: srcH * ratio };
}

// Add image to slide preserving aspect ratio, centered in available area
function addImg(slide, figDir, fname, knownDims, x, y, maxW, maxH) {
  const b64 = imgB64(figDir, fname);
  if (!b64) return;
  const [srcW, srcH] = knownDims[fname];
  const { w, h } = fitImage(srcW, srcH, maxW, maxH);
  const xOffset = x + (maxW - w) / 2;
  const yOffset = y + (maxH - h) / 2;
  slide.addImage({ data: b64, x: xOffset, y: yOffset, w, h });
}

// === Title Bar Helper ===
// Creates consistent title bar on all content slides
function titleBar(slide, title) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: W, h: 0.85, fill: { color: C.light }
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: MARGIN, y: 0.85, w: 1.2, h: 0.04, fill: { color: C.accent }
  });
  slide.addText(title, {
    x: MARGIN, y: 0.1, w: 8.9, h: 0.65,
    fontSize: 22, fontFace: "Arial", color: C.primary, bold: true
  });
  return slide;
}

// === Pattern: Left Text Card + Right Figure Panels ===
// The core academic slide layout. Left side has a colored card with
// key points/formulas, right side shows 2-4 cropped figure panels.
//
// Usage:
//   const slide = titleBar(pres.addSlide(), "Finding 1: ...");
//   // Left card
//   slide.addShape(pres.shapes.RECTANGLE, {
//     x: 0.4, y: CONTENT_TOP, w: 3.2, h: 4.3,
//     fill: { color: "FFF5F5" }, line: { color: C.accent, width: 1 }
//   });
//   slide.addText([richText], { x: 0.55, y: CONTENT_TOP+0.1, w: 2.9, h: 4.1 });
//   // Right panels (2x2 grid)
//   addImg(slide, figDir, "Fig1a.png", knownDims, 3.8, CONTENT_TOP, 3.0, 2.3);
//   addImg(slide, figDir, "Fig1b.png", knownDims, 6.8, CONTENT_TOP, 3.0, 2.3);
//   addImg(slide, figDir, "Fig1c.png", knownDims, 3.8, 3.3, 3.0, 2.0);
//   addImg(slide, figDir, "Fig1d.png", knownDims, 6.8, 3.3, 3.0, 2.0);
//   // Panel labels
//   slide.addText("a", { x: 3.7, y: CONTENT_TOP, w: 0.3, h: 0.3, fontSize: 9, color: C.caption, italic: true });

// === Pattern: Two Comparison Cards ===
// For presenting two contrasting concepts (GWAS vs Burden, etc.)
//
// Usage:
//   const s = titleBar(pres.addSlide(), "GWAS vs LoF Burden Test");
//   // Left card (blue theme)
//   s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.1, w: 4.3, h: 4.1, fill: { color: "F0F7FF" }, line: { color: C.blue, width: 1.5 } });
//   // Right card (red theme)
//   s.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 1.1, w: 4.3, h: 4.1, fill: { color: "FFF5F5" }, line: { color: C.accent, width: 1.5 } });

// === Pattern: Three Implication Cards ===
// For summary/takeaway slides with three parallel cards
//
// Usage:
//   const cards = [
//     { title: "Drug Targets", color: C.accent, bg: "FFF5F5", text: "..." },
//     { title: "Biology", color: C.blue, bg: "F0F7FF", text: "..." },
//     { title: "Methods", color: C.green, bg: "F0FDF4", text: "..." },
//   ];
//   cards.forEach((c, i) => {
//     const x = 0.5 + i * 3.1;
//     s.addShape(pres.shapes.RECTANGLE, { x, y: 1.05, w: 2.9, h: 2.2, fill: { color: c.bg }, line: { color: c.color, width: 1.5 } });
//     // ... add title and body text
//   });

// === PANEL CROPPING WORKFLOW ===
// Before generating PPT, crop panels from main figures:
//
// 1. Download hi-res figures (lw900 for Springer/Nature)
// 2. Determine panel layout (2x2, 1x3, 2-row, etc.)
// 3. Crop with PIL:
//    from PIL import Image
//    img = Image.open("Fig1_hires.png")
//    w, h = img.size
//    panels["Fig1a"] = img.crop((0, 0, w//2, h//2))
//    panels["Fig1b"] = img.crop((w//2, 0, w, h//2))
//    panels["Fig1c"] = img.crop((0, h//2, w//2, h))
//    panels["Fig1d"] = img.crop((w//2, h//2, w, h))
// 4. Record knownDims for each panel:
//    const knownDims = {
//      "Fig1a.png": [450, 395],
//      "Fig1b.png": [450, 395],
//      ...
//    };
// 5. Use addImg() with knownDims for aspect-ratio-preserving placement

// ================================================================
// CUSTOMIZE BELOW FOR YOUR PAPER
// ================================================================

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "Lab Meeting Report";
pres.title = "Paper Title Here";

// Panel dimensions — READ from your cropped panels!
const knownDims = {
  "Fig1a.png": [450, 395],
  "Fig1b.png": [450, 395],
  // ... add all panels
};
const figDir = path.join(__dirname, "figures");

// === SLIDE 1: Title Slide ===
{
  const s = pres.addSlide();
  s.background = { color: C.primary };
  s.addText("Paper Title\nHere", {
    x: 0.8, y: 0.6, w: 8.4, h: 2.2,
    fontSize: 30, fontFace: "Arial", color: C.white, bold: true,
    lineSpacingMultiple: 1.15
  });
  s.addShape(pres.shapes.LINE, { x: 0.8, y: 2.9, w: 3.0, h: 0, line: { color: C.accent, width: 3 } });
  s.addText("Authors et al.  •  Journal Year", {
    x: 0.8, y: 3.1, w: 8.4, h: 1.0,
    fontSize: 14, fontFace: "Arial", color: "9CA3AF"
  });
}

// === Add more slides using patterns above ===
// ... customize for your paper content

const outPath = path.join(__dirname, "output.pptx");
pres.writeFile({ fileName: outPath }).then(() => {
  console.log("PPT generated:", outPath);
}).catch(err => console.error("Error:", err));