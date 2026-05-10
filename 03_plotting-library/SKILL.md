---
name: plotting-library
description: "Curated scientific plotting implementation library. Use when a figure needs runnable code, catalog lookup, mock data, or a reusable house-style template. R is the preferred implementation language for static scientific figures. Existing Python scripts are legacy references, not design targets."
version: 2.0
tags: [plotting, visualization, R, ggplot2, templates, bioinformatics]
related_skills: [sci-fig]
canonical_source: https://github.com/cupcake777/viz-skills/tree/main/plotting-library
compatibility: Prefer R with ggplot2/ComplexHeatmap/patchwork/cowplot. Python is acceptable for interactive or specialized chart types, and legacy Python templates may be used as rough references.
---

# Plotting Library

This is the curated implementation layer for scientific figures. It provides
runnable templates, demo data, shared style files, and the chart catalog used by
`sci-fig`.

## Responsibility

Use this skill to:
- find whether a chart type already has a reviewed implementation
- rebuild a figure type into a high-quality R template
- adapt a reviewed template to real project data
- generate demo figures from mock data
- update the chart catalog after a template is reviewed and worth reusing

Do not use this skill to decide the scientific claim or slide story. Use
`sci-fig` for figure decisions and `academic-slides` for presentation structure.

## Source Of Truth

`catalog.yaml` is the chart registry. It should define:
- chart name and title
- data type and required columns
- template path
- tier/status
- demo output
- recommended use cases and tags

If a table in documentation disagrees with `catalog.yaml`, trust
`catalog.yaml`.

## R-First Execution Policy

Prefer R templates for static scientific figures.

Important: do not mechanically port old Python scripts. Many existing Python
files are simple placeholders. Use them only as rough references for inputs or
demo intent, then redesign the figure in R to the desired quality level.

R template standards:
- source `templates/base_plot.R` at the top
- keep every text element at 16pt or larger unless the user explicitly requests
  smaller journal-native typography
- include a small `generate_mock_data()` function or paired demo TSV
- expose a plotting function that accepts a data frame and key column names
- use `ggplot2` unless another R package is clearly better
- use `theme_sci()` from `base_plot.R` for the default house style
- use `ggrepel` for dense labels
- use `ComplexHeatmap` for advanced heatmaps
- export with `save_figure()` / `save_demo()` from `base_plot.R`
- set explicit width, height, units, and DPI
- avoid plot titles by default for manuscript-style figures

Python remains acceptable for:
- Plotly/HTML or interactive outputs
- network layouts, Sankey, UMAP, or specialized libraries
- projects where data and analysis are already Python-native

## Usage Pattern

1. Read `catalog.yaml` and match by `data_type`, required columns, and tags.
2. If a reviewed R template exists, adapt it.
3. If only a legacy Python template exists, treat it as reference and consider
   rebuilding the figure in R.
4. Replace demo data loading with the real input.
5. Render the figure at the preset size requested by `sci-fig`.
6. Save final outputs as PDF plus PNG unless the user requests otherwise.
7. Report the files generated and any assumptions about columns/statistics.

## Adding A Template

Add a template only when the chart pattern is reusable and visually strong
enough to represent the library.

Required steps:
1. Create `templates/{chart_name}.R` for static scientific figures, or a
   Python/HTML implementation only when the chart is genuinely interactive or
   library-specific.
2. Add demo input under `demo_data/` when mock data is not generated inside the
   script.
3. Render demo output locally.
4. Add or update the `catalog.yaml` entry.
5. Review the rendered demo before treating the template as reusable.

Template naming:
- file names use `snake_case`
- R is preferred for static figures: `templates/raincloud.R`
- Python is acceptable for special cases only when R is not the right execution
  layer.

## Current Layout

```text
plotting-library/
├── catalog.yaml
├── requirements.txt
├── demo_fig/
│   ├── *_demo.png
│   └── *_demo.pdf
├── demo_data/
├── style/
│   ├── color_palettes.R
│   └── matplotlibrc
├── templates/
│   ├── base_plot.R
│   └── *.R
```

Treat this directory as the skill-facing execution layer. Demo outputs live in
`demo_fig/`, and reusable code lives in `templates/`.

## Quality Checks

Before handing off a generated figure:
- verify that required columns were mapped correctly
- check text sizes against the selected preset
- check that labels do not overlap
- check that colors have stable semantic meaning
- check that exported files exist and match the requested format
- for PPT use, confirm that the PNG is readable at slide size

## Relationship To `sci-fig`

`sci-fig` decides what should be drawn and what quality bar applies.
`plotting-library` supplies the curated runnable implementation.
