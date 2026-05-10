# viz-skills

`viz-skills` is a small skill suite for scientific visual communication. It
covers the full path from a result table or figure idea to publication-quality
graphics and readable academic slides.

The repository is deliberately split into focused skills:

- `sci-fig` decides what figure should be made and how to judge its quality.
- `plotting-library` provides runnable, reusable plotting templates.
- `academic-slides` turns results into talk structure and slide layouts.
- `powerpoint` handles `.pptx` file mechanics.

Use the smallest skill that owns the current problem. When a task crosses
boundaries, follow the workflow documents in `01_workflows/`.

## Repository Layout

```text
viz-skills/
├── 01_workflows/          # Cross-skill handoffs
│   └── figure-to-slide.md
├── 02_sci-fig/            # Figure planning, critique, chart choice, QA
│   ├── SKILL.md
│   └── references/
├── 03_plotting-library/   # R-first executable plotting templates
│   ├── SKILL.md
│   ├── catalog.yaml
│   ├── templates/
│   ├── demo_data/
│   └── *_demo.{png,pdf}
├── 04_academic-slides/    # Academic talk narrative and slide layout rules
│   ├── SKILL.md
│   ├── references/
│   └── templates/
└── 05_powerpoint/         # PPTX read, edit, create, and packaging mechanics
    ├── SKILL.md
    ├── references/
    └── scripts/
```

## Skill Map

| Skill | Owns | Does not own |
|---|---|---|
| `sci-fig` | Scientific figure intent, chart selection, visual standards, QA | Long runnable template code |
| `plotting-library` | Catalog lookup, R plotting templates, demo data, rendered demo outputs | Scientific claim selection or slide narrative |
| `academic-slides` | Group meeting and defense structure, slide claims, panel layout, Chinese academic presentation conventions | Low-level PPTX file editing |
| `powerpoint` | Reading, editing, generating, splitting, merging, and verifying `.pptx` files | Academic story or figure redesign decisions |

## Common Workflows

### Make Or Fix A Scientific Figure

```text
data/result -> sci-fig -> plotting-library -> PNG/PDF
```

1. Use `sci-fig` to identify the claim, audience, chart type, and output preset.
2. Use `plotting-library` when runnable code or a reusable template is needed.
3. Prefer R for static scientific figures.
4. Export final figures with explicit dimensions, usually PDF plus PNG.

### Turn Figures Into Slides

```text
data/result -> sci-fig -> plotting-library -> academic-slides -> powerpoint
```

1. Define one slide-level claim.
2. Decide whether the figure is readable at slide size.
3. Regenerate the figure with a presentation preset if needed.
4. Use `academic-slides` for layout, density, cropping, and slide text.
5. Use `powerpoint` only to create or edit the actual `.pptx`.

See [01_workflows/figure-to-slide.md](01_workflows/figure-to-slide.md).

### Edit A PPTX

```text
pptx file -> powerpoint -> verified pptx
```

Use `powerpoint` for extraction, image replacement, XML/python-pptx edits,
deck generation, and visual verification. If the requested change affects the
story or figure readability, bring in `academic-slides` or `sci-fig`.

## Trigger Guide

| User request | Start with | Add when needed |
|---|---|---|
| "Draw a volcano/heatmap/scatter/violin plot" | `sci-fig` | `plotting-library` |
| "Make this figure publication ready" | `sci-fig` | `plotting-library` |
| "Use an existing template" | `plotting-library` | `sci-fig` |
| "Make slides for group meeting/defense" | `academic-slides` | `powerpoint`, `sci-fig` |
| "Put these figures into PPT" | `academic-slides` | `sci-fig`, `plotting-library`, `powerpoint` |
| "Edit/read/create this .pptx" | `powerpoint` | `academic-slides` |
| "Learn this plot style" | `sci-fig` | `plotting-library` |

## Source Of Truth

- Figure decision workflow: `02_sci-fig/SKILL.md`
- Figure quality rules: `02_sci-fig/references/visual-standards.md`
- Figure presets and export sizes: `02_sci-fig/references/presets.md`
- Chart registry: `03_plotting-library/catalog.yaml`
- Shared plotting style helpers: `03_plotting-library/templates/base_plot.R`
- Academic slide rules: `04_academic-slides/SKILL.md`
- PPTX mechanics: `05_powerpoint/SKILL.md`
- Figure-to-slide handoff: `01_workflows/figure-to-slide.md`

If a high-level README conflicts with a skill entrypoint or catalog, trust the
more specific source of truth.

## Plotting Policy

Static scientific figures are R-first. The preferred stack is:

- `ggplot2` for most grammar-of-graphics plots
- `ComplexHeatmap` for serious heatmaps and annotations
- `patchwork` or `cowplot` for multi-panel composition
- `ggrepel` for dense labels
- project-specific palettes or colorblind-safe scientific palettes

Python remains acceptable for interactive outputs, Plotly, network/Sankey-style
figures, or project pipelines where Python is clearly the better execution path.

New reusable templates should live under `03_plotting-library/templates/` and be
registered in `03_plotting-library/catalog.yaml` only after they render cleanly.

## Install

Install individual skills rather than the whole repository at once:

```bash
npx skills add cupcake777/viz-skills sci-fig
npx skills add cupcake777/viz-skills plotting-library
npx skills add cupcake777/viz-skills academic-slides
npx skills add cupcake777/viz-skills powerpoint
```

## Maintenance Rules

- Keep `SKILL.md` files as routing and decision entrypoints.
- Put detailed chart recipes in `02_sci-fig/references/`.
- Put executable plotting code in `03_plotting-library/templates/`.
- Keep `03_plotting-library/catalog.yaml` aligned with templates and demo
  outputs.
- Do not duplicate long template tables across README, skill files, and
  references.
- For slide tasks, do not paste full manuscript figures blindly; crop or
  regenerate panels so they are readable on a 16:9 slide.
- Preserve aspect ratio for every figure inserted into PPT.
