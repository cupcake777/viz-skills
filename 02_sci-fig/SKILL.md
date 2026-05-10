---
name: sci-fig
description: "Scientific figure decision and quality-control skill. Use for planning, generating, revising, or critiquing scientific plots and figures. Triggers on plot, figure, chart, visualization, heatmap, volcano, scatter, bar, violin, enrichment, Manhattan, ggplot2, matplotlib, label overlap, unreadable figure, color problems, or requests to learn a figure style."
version: 4.0
tags: [plotting, visualization, bioinformatics, R, ggplot2, figures]
related_skills: [plotting-library, academic-slides]
canonical_source: https://github.com/cupcake777/viz-skills/tree/main/sci-fig
compatibility: R-first. Prefer ggplot2/ComplexHeatmap/patchwork/cowplot for static scientific figures; use Python only when the existing template or chart type makes it the better execution path.
---

# Scientific Figure Skill

This skill is the decision and quality layer for scientific figures. It decides
what to draw, how the figure should behave visually, and when to call an
execution layer. It is not the template library.

## Runtime Flow

Use this flow for every substantive figure task:

1. **Intake**: identify the data, scientific claim, target audience, and output
   preset: `publication`, `presentation`, `poster`, or `draft`.
2. **Classify task**:
   - `draw`: create a figure from data or summary results
   - `revise`: improve an existing figure or plotting code
   - `learn`: extract a reusable style or chart pattern from an example
3. **Select chart**: choose the chart type from claim and data structure before
   writing code.
4. **Execute**: call `plotting-library` when runnable code or a reusable template
   is needed. Prefer R static plots.
5. **QA**: check readability, statistical encoding, labels, colors, dimensions,
   and export format.
6. **Persist**: add or update templates only for `learn` tasks or when the user
   explicitly asks to save the pattern.

## Task Modes

### Draw

Use when the user wants a new figure from data, a result table, or analysis
output.

Required decisions:
- output preset and final size
- chart claim: distribution, comparison, trend, relationship, matrix, genomic
  signal, enrichment, overlap, composition, rank, trajectory, or survival
- statistical quantity shown on each visual channel
- whether an existing template exists in `plotting-library/catalog.yaml`

### Revise

Use when the user complains that a figure is ugly, crowded, unreadable, or
scientifically misleading.

Prioritize:
- wrong chart type
- label overlap or unreadable text
- missing units or unclear axes
- inconsistent project colors
- bar/error plots hiding continuous distributions
- figure dimensions that do not match the destination

### Learn

Use when the user provides a paper figure, website figure, or preferred example
and wants that style reused.

Follow `references/learning-protocol.md`. Learning is not complete until a
runnable template or template variant is rendered and reviewed. Do not save
unreviewed output as a reusable template.

## R-First Policy

Default to R for static scientific figures.

Preferred R stack:
- `ggplot2` for grammar-of-graphics figures
- `ComplexHeatmap` for serious heatmaps and annotations
- `patchwork` or `cowplot` for multi-panel assembly
- `ggrepel` for non-overlapping labels
- `ggsci`, `viridis`, or project palettes for colors
- `survival`/`survminer`, `forestplot`, or domain packages when appropriate

Use Python when:
- the existing maintained template is Python and already fits the task
- the chart is interactive or web-first, such as Plotly Sankey
- a mature Python library is clearly better for the chart
- the project data pipeline is already Python and avoiding conversion matters

## Non-Negotiable Figure Rules

- Select chart type from data and claim; do not default to bar plots.
- Do not use bar + error bar for continuous distributions; use points, violin,
  box, raincloud, ridge, or estimation plots as appropriate.
- Always set explicit width and height for final figures.
- Keep all text at 16pt or larger unless the user explicitly requests smaller
  journal-native typography.
- For final scientific figures, export vector PDF plus preview PNG unless the
  user asks otherwise.
- Manuscript-style figures should not carry plot titles or subtitles inside the
  panel; use captions/legends outside the graphic.
- Avoid rainbow/jet palettes.
- Use `ggrepel` or equivalent label-repelling methods for dense annotations.
- Keep project colors semantically stable across all figures and slides.

## Chart Selection Summary

| Claim | Typical data | Preferred chart |
|---|---|---|
| Distribution | one numeric variable across groups | violin/box/jitter, raincloud, ridge |
| Comparison | groups with counts, proportions, or estimates | dot/interval, box/violin, bar only for counts/proportions |
| Trend | ordered time/stage variable | line with CI, heatmap for many features |
| Relationship | two numeric variables | scatter with fit, hex/bin for dense data |
| Matrix | genes/features by samples | heatmap with annotation |
| Genomic signal | chr/pos/p-value | Manhattan or regional plot |
| Differential result | effect size and p-value | volcano or MA plot |
| Enrichment | term, p-value, ratio/count | dot/bubble plot |
| Overlap | multiple gene sets | UpSet; Venn only for 2-3 sets |
| Survival | time, event, group | Kaplan-Meier or forest plot |

Detailed chart guidance belongs in reference docs and the template catalog, not
in this entry file.

## Presets

Default preset is `publication` unless the figure is explicitly going into
slides. For PPT, use `presentation` and make text large enough for projection.

See `references/presets.md` for dimensions, font sizes, DPI, and export code.

## Handoff To Slides

When a figure is destined for slides:
- generate a presentation-sized export, not just a manuscript panel
- use transparent PNG when it must sit on a slide background
- increase axis, legend, and annotation text
- crop multi-panel figures into readable slide panels
- coordinate with `academic-slides` for layout and `powerpoint` for PPTX edits

See `../01_workflows/figure-to-slide.md`.

## References

Load only the reference needed for the task:

- `references/presets.md` - output sizes, DPI, and export settings
- `references/visual-standards.md` - typography, colors, anti-patterns, QA
- `references/learning-protocol.md` - learning a new figure style
- `references/volcano.md`, `heatmap.md`, `scatter.md`, `box_violin.md`,
  `barplot.md`, `enrichment_dot.md` - chart-specific recipes
- `references/gallery-workflow.md` and `gallery-feedback-loop.md` - optional
  gallery review workflow
