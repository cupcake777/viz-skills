# Figure To Slide Workflow

Use this workflow when analysis figures need to become readable academic slides.
It coordinates `sci-fig`, `plotting-library`, `academic-slides`, and
`powerpoint`.

## Responsibility Split

```text
sci-fig
  decides whether the figure is appropriate and what preset is needed

plotting-library
  renders the figure, preferably with R for static scientific charts

academic-slides
  decides the slide claim, layout, density, caption, and panel arrangement

powerpoint
  edits or creates the actual .pptx file and verifies rendered slides
```

## Standard Flow

1. Define the slide-level claim in one sentence.
2. Decide whether the existing figure is readable in a slide context.
3. If not, regenerate with `sci-fig` preset `presentation`.
4. Prefer R rendering for static plots:
   - `ggplot2` for most charts
   - `ComplexHeatmap` for heatmaps
   - `patchwork`/`cowplot` for composed panels
5. Export slide figures as transparent PNG at 150-200 DPI.
6. Keep manuscript PDFs separately when publication output is also needed.
7. In `academic-slides`, place the figure to support the slide claim:
   - common default: left one-third text, right two-thirds figure
   - crop multi-panel figures into individual readable panels
   - keep aspect ratio; never stretch
8. Use `powerpoint` only for file mechanics: insert image, edit text boxes,
   generate deck, or verify the final PPTX.

## Figure Export Defaults

For slide figures:

```r
ggsave(
  filename = "figures/result_ppt.png",
  plot = p,
  width = 9,
  height = 4.5,
  units = "in",
  dpi = 200,
  bg = "transparent"
)
```

For half-slide figures:

```r
ggsave(
  filename = "figures/result_half_slide.png",
  plot = p,
  width = 5.5,
  height = 4.2,
  units = "in",
  dpi = 200,
  bg = "transparent"
)
```

## Slide Readability Rules

- Axis labels should usually be 16 pt or larger.
- Tick labels should usually be 14 pt or larger.
- Legends should be short and close to the data.
- Dense gene labels should be reduced to top hits and repelled with `ggrepel`.
- Multi-panel paper figures should be cropped into panels before placing.
- Every image should preserve aspect ratio.
- A slide should explain one claim, not archive a full paper figure.

## When To Regenerate Instead Of Reusing

Regenerate the figure when:
- text is too small after insertion into a slide
- the figure relies on a manuscript caption to be understood
- labels overlap at slide size
- a multi-panel figure contains unreadable subpanels
- colors conflict with the slide palette
- the figure needs transparent background or larger line widths

## Deliverables

For a slide-oriented figure task, report:
- source data or existing figure used
- R/Python script changed or generated
- exported PNG/PDF files
- PPTX file changed or created
- visual verification performed
