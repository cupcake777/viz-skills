# Figure Panel Cropping for Academic PPTs

## Why

Never embed full multi-panel figures (Fig 1a-f) as a single image — they're too small on a slide. Crop individual panels and arrange 2-4 per slide for readability.

## Workflow

### 1. Download high-res figures

```bash
# Springer/Nature: swap lw685 → lw900 for 900px wide
for i in 1 2 3 4 5; do
  curl -sL -o "Fig${i}_hires.png" \
    "https://media.springernature.com/lw900/springer-static/image/art%3A10.1038%2F{DOI_SUFFIX}/MediaObjects/{JOURNAL_CODE}_Fig${i}_HTML.png"
done
```

### 2. Crop panels with PIL

```python
from PIL import Image

img = Image.open("Fig1_hires.png")  # e.g. 900x790
w, h = img.size

# Common Nature layout: 2 rows (top/bottom halves)
top = img.crop((0, 0, w, h//2))
bottom = img.crop((0, h//2, w, h))

# Or 2x2 grid for 4-panel figures
tl = img.crop((0, 0, w//2, h//2))
tr = img.crop((w//2, 0, w, h//2))
bl = img.crop((0, h//2, w//2, h))
br = img.crop((w//2, h//2, w, h))

# Or 3 columns for wide single-row figures
third = w // 3
a = img.crop((0, 0, third, h))
b = img.crop((third, 0, 2*third, h))
c = img.crop((2*third, 0, w, h))

for name, panel in panels.items():
    panel.save(f"{name}.png")
```

### 3. Embed with aspect ratio preservation (pptxgenjs)

```javascript
function fitImage(srcW, srcH, maxW, maxH) {
  const ratio = Math.min(maxW / srcW, maxH / srcH);
  return { w: srcW * ratio, h: srcH * ratio };
}

// Usage: center the image in the available area
function addImagePreservingRatio(slide, fname, x, y, maxW, maxH) {
  const b64 = "image/png;base64," + fs.readFileSync(path.join(figDir, fname)).toString("base64");
  const [srcW, srcH] = knownDims[fname];
  const { w, h } = fitImage(srcW, srcH, maxW, maxH);
  const xOffset = x + (maxW - w) / 2;
  const yOffset = y + (maxH - h) / 2;
  slide.addImage({ data: b64, x: xOffset, y: yOffset, w, h });
}
```

### 4. Label panels

Add sub-panel labels (a/b/c/d) as small text in the top-left corner of each panel area:

```javascript
slide.addText("a", { x: 3.7, y: 1.0, w: 0.3, h: 0.3, fontSize: 9, color: "6B7280", italic: true });
```

## Slide Layout: Left Text + Right Panels

For academic PPTs, prefer this layout over full-width figures:

```
┌──────────────┬──────────────────────────────┐
│ Key insight  │  ┌──────────┐  ┌──────────┐  │
│ formulas     │  │ Panel a  │  │ Panel b  │  │
│ mechanism    │  └──────────┘  └──────────┘  │
│              │  ┌──────────┐  ┌──────────┐  │
│              │  │ Panel c  │  │ Panel d  │  │
│              │  └──────────┘  └──────────┘  │
│ (1/3 width)  │  (2/3 width, labels a/b/c/d)│
└──────────────┴──────────────────────────────┘
```

- Left column: 3.2" wide, colored card with formulas and key points
- Right area: 6.0"+ wide, 2x2 or 1x2 panel grid
- Panel labels in caption color at top-left of each panel

## Pitfalls

- **Never use `sizing: "cover"` in pptxgenjs** — it crops and can cut off panel labels
- **Always use `sizing: "contain"`** or manual `fitImage()` calculation — preserves entire content
- **Don't guess panel boundaries** — check the actual figure layout first (1x3, 2x2, 2x3, etc.)
- **Save a `knownDims` dict** of panel filenames → [width, height] so you don't need to re-read images at runtime