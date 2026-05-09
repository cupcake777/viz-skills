# Export Presets

## How Presets Work

A preset defines the **output specifications** for a figure: dimensions, resolution, font sizes, and file format. Select one preset at project start; all figures in that project follow it.

If the user needs both publication and presentation figures → use `publication` as the base, then provide a one-line export override for PPT versions.

---

## Preset: `publication`

For journal submission. Meets Nature, Cell, Science, PLOS, and most Elsevier requirements.

### Dimensions

| Layout | Width | Height | Notes |
|--------|-------|--------|-------|
| Single column | 85mm (3.35in) | flexible, typically 60–85mm | Most panels, small figures |
| 1.5 column | 114mm (4.49in) | flexible | Medium complexity |
| Full width (2-col) | 180mm (7.08in) | flexible, max ~240mm (9.45in) | Multi-panel figures |

Height is flexible but should respect a reasonable aspect ratio (generally 0.6–1.0 × width).

### Specs

| Property | Value |
|----------|-------|
| DPI | 300 minimum; 600 for line art |
| Format | PDF (vector, preferred) or TIFF (raster, some journals require) |
| Font size | 7pt minimum (Nature standard); 6pt absolute floor |
| Font family | Arial or Helvetica |
| Line width | 0.5–1pt for axes; 0.25–0.5pt for grid/guides |
| Color mode | CMYK for print, RGB for online-only |

### R export
```r
# Single-column figure
ggsave("figure.pdf", plot, width = 85, height = 70, units = "mm", dpi = 300)

# Full-width multi-panel
ggsave("figure.pdf", plot, width = 180, height = 140, units = "mm", dpi = 300)

# TIFF (some journals require)
ggsave("figure.tiff", plot, width = 180, height = 140, units = "mm",
       dpi = 300, compression = "lzw")
```

### Python export
```python
# Single-column (85mm ≈ 3.35in)
fig.savefig("figure.pdf", dpi=300, bbox_inches="tight")
# Set figure size at creation:
fig, ax = plt.subplots(figsize=(3.35, 2.76))

# Full-width (180mm ≈ 7.08in)
fig, axes = plt.subplots(1, 2, figsize=(7.08, 3.5))
fig.savefig("figure.pdf", dpi=300, bbox_inches="tight")
```

---

## Preset: `presentation`

For PowerPoint / Keynote slides. Optimized for screen display at distance.

### Dimensions

| Layout | Width | Height | Notes |
|--------|-------|--------|-------|
| Full slide figure | 9in | 4.5in | Fills 16:9 slide with margins |
| Half slide (with text) | 5.5in | 4.5in | Figure on one side, text on other |
| Small inset | 4in | 3in | For data summary or supporting figure |

### Specs

| Property | Value |
|----------|-------|
| DPI | 150–200 (higher is unnecessary for screen) |
| Format | PNG (universal compatibility) |
| Font size | **16pt minimum** — nothing smaller, ever |
| Font family | Arial or Calibri |
| Line width | 1.5–2pt for axes; 1pt for grid |
| Background | Transparent (for flexible slide backgrounds) or white |

### Key differences from publication

| Property | Publication | Presentation |
|----------|------------|--------------|
| Font base size | 7pt | 16pt |
| Axis line width | 0.5pt | 1.5pt |
| Point size | 0.5–1pt | 2–3pt |
| Legend text | 6–7pt | 14–16pt |
| Annotation text | 6pt | 14pt |
| Figure title | Usually none (caption) | Usually none (slide title) |

### R export
```r
# Presentation theme (inherits from theme_sci)
theme_sci_ppt <- function() {
  theme_sci(base_size = 16) +
    theme(
      axis.line = element_line(linewidth = 0.8),
      axis.ticks = element_line(linewidth = 0.6),
      plot.margin = margin(10, 10, 10, 10, "pt")
    )
}

ggsave("figure_ppt.png", plot + theme_sci_ppt(),
       width = 9, height = 4.5, dpi = 200, bg = "transparent")
```

### Python export
```python
SCI_RC_PPT = {
    **SCI_RC,
    "font.size": 16,
    "axes.titlesize": 18,
    "axes.labelsize": 16,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "legend.fontsize": 14,
    "axes.linewidth": 1.5,
    "xtick.major.width": 1.0,
    "ytick.major.width": 1.0,
    "lines.linewidth": 2.0,
    "lines.markersize": 8,
    "figure.dpi": 200,
}

plt.rcParams.update(SCI_RC_PPT)
fig, ax = plt.subplots(figsize=(9, 4.5))
# ... plot ...
fig.savefig("figure_ppt.png", dpi=200, bbox_inches="tight", transparent=True)
```

---

## Preset: `poster`

For conference posters (typically printed at A0 or 48"×36").

### Dimensions

Variable — depends on poster layout. Individual figures are usually:

| Layout | Width | Height |
|--------|-------|--------|
| Quarter-poster panel | 10–12in | 8–10in |
| Half-width panel | 16–18in | 10–12in |

### Specs

| Property | Value |
|----------|-------|
| DPI | 300 |
| Format | PDF (vector) or PNG at 300 DPI |
| Font size | **24pt minimum** for axis labels; 20pt for tick labels |
| Line width | 2–3pt |

### R export
```r
theme_sci_poster <- function() {
  theme_sci(base_size = 24) +
    theme(
      axis.line = element_line(linewidth = 1.2),
      axis.ticks = element_line(linewidth = 0.8)
    )
}

ggsave("figure_poster.pdf", plot + theme_sci_poster(),
       width = 12, height = 9, dpi = 300)
```

---

## Preset: `draft`

For quick daily analysis. Minimal quality requirements — speed over polish.

### Specs

| Property | Value |
|----------|-------|
| DPI | 100 |
| Format | PNG |
| Dimensions | 8in × 6in (default) |
| Font size | 12pt minimum |
| Theme | Basic — can use default ggplot2/matplotlib theme |

### R export
```r
ggsave("quick_look.png", plot, width = 8, height = 6, dpi = 100)
```

### Python export
```python
fig.savefig("quick_look.png", dpi=100, bbox_inches="tight")
```

---

## Dual Export (Publication + Presentation)

When the user needs the same figure for both paper and slides, generate two versions from one plot object:

### R
```r
# Build the plot once
p <- ggplot(data, aes(x, y, color = group)) +
  geom_point() +
  scale_color_project()

# Publication version
ggsave("fig1_pub.pdf", p + theme_sci(base_size = 7),
       width = 85, height = 70, units = "mm", dpi = 300)

# Presentation version
ggsave("fig1_ppt.png", p + theme_sci_ppt(),
       width = 9, height = 4.5, dpi = 200, bg = "transparent")
```

### Python
```python
# Build the plot once, export twice
def save_dual(fig, name):
    # Publication
    fig.savefig(f"{name}_pub.pdf", dpi=300, bbox_inches="tight")
    # Presentation (re-apply PPT theme first)
    plt.rcParams.update(SCI_RC_PPT)
    fig.savefig(f"{name}_ppt.png", dpi=200, bbox_inches="tight", transparent=True)
```

Note: For Python, font sizes are set globally via rcParams, so the dual-export requires re-rendering the figure. In R, theme is applied per-plot so you can export twice from the same object cleanly.
