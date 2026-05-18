# viz-skills — Scientific Figure Decision & Execution Library

This repo provides decision rules, color palettes, and runnable templates for publication-quality scientific figures. It serves two roles: a knowledge base for figure selection (sci-fig) and an execution library with R/Python templates (plotting-library).

## Quick Start Example

User asks: "Draw a volcano plot for my differential expression data."

1. Read `02_sci-fig/SKILL.md` — find the Claim type (differential_signal) and check the decision tree
2. Grep `03_plotting-library/catalog.yaml` for `id: volcano`
3. Use the `template:` field to locate the script: `03_plotting-library/templates/volcano.R`
4. Source `03_plotting-library/templates/base_plot.R` for house style
5. Replace `generate_mock_data()` with real data loading
6. Run: `Rscript templates/volcano.R`

## How to Find the Right Chart

The entry point is **`03_plotting-library/catalog.yaml`**. It is machine-readable and searchable.

Lookup algorithm:
1. Identify the user's analytical claim: distribution, comparison, trend, relationship, differential_signal, genomic_position, matrix_pattern, enrichment, overlap, composition, embedding, flow_network, trajectory, ranking, marker
2. Grep `catalog.yaml` for `claim_types` matching that claim, or grep for `id:` matching the chart name
3. Read the `default_palette:` field — use this palette for the chart unless the user specifies otherwise
4. Read the `best_for:` and `not_for:` fields — validate the chart fits the use case
5. Read the `template:` field — that's the script path relative to `03_plotting-library/`
6. Read the `required_fields:` and `optional_fields:` to understand column mappings
7. Check `status: done` — only `done` templates have runnable code; `planned` means no script exists yet

## Execution Rules

- **R-first**: Prefer `Rscript templates/<chart>.R` for all static scientific figures. Python is acceptable for Plotly/HTML interactive outputs or when no R template exists.
- **House style**: Always source `style/base_plot.R` (R) or load `style/matplotlibrc` (Python). Never set fonts/colors from scratch.
- **Dual output**: Every figure must produce both PDF (vector, publication) and PNG (preview). Use `save_figure()` from base_plot.R or `save_fig()` from base_plot.py.
- **No titles inside figures**: Figure titles belong in the document/presentation, not rendered inside the plot canvas.
- **No panel labels in code**: Panel annotations (A, B, C) are done in post-processing (Inkscape/AI), not in plotting code.

## Color Rules

Before choosing colors, read `02_sci-fig/references/color-palettes.md` — the single source of truth for all palettes.

Critical rules:
- Semantic colors are locked per role: blue=proposed/baseline, green=positive/gain, red=negative/loss, gray=NS. **Never remap these across charts in the same project.**
- Directional variables (up/down, gain/loss) use `#D55E00`/`#0072B2` (Okabe-Ito), NOT positive/negative colors.
- Use `get_palette("morandi")` as default project palette. Override with journal palettes (npg, nejm, lancet) only when the target journal requires it.
- **Never use rainbow/jet colormaps.** Use viridis (sequential) or roma/vik (diverging, CVD-safe).
- If `config/plot_config.yaml` exists in the project root, source it first — its palette overrides all defaults.

## What NOT to Do

- Do NOT create a new template from scratch if a `done` template exists for that chart type — adapt the existing one.
- Do NOT modify `catalog.yaml` without also re-running the template to generate an updated demo PNG.
- Do NOT use bar+error bar for continuous data — use violin/box/raincloud instead.
- Do NOT use >3-set Venn diagrams — use UpSet plots.
- Do NOT hardcode hex colors in templates — use `get_palette()` or semantic color mapping from `style/color_palettes.py`.

## Deep Reference Files

| Need | Read this |
|------|-----------|
| Chart selection decision tree, QA checklist, anti-patterns | `02_sci-fig/SKILL.md` |
| Template catalog, R/Python execution, color palettes, adding new charts | `03_plotting-library/SKILL.md` |
| Presentation design rules | `04_academic-slides/SKILL.md` |
| PPTX generation | `05_powerpoint/SKILL.md` |
| Cross-skill handoff (figure → slide → PPTX) | `01_workflows/figure-to-slide.md` |

## Project-Level Color Palettes

If this repo is used inside a project, lock the palette in `config/plot_config.yaml`:

```yaml
# config/plot_config.yaml
palette: morandi
continuous_colormap: mako
semantic:
  up: "#D55E00"
  down: "#0072B2"
  ns: "#BBBBBB"
```

Then load it before any plotting code:

```python
import yaml
from pathlib import Path
_cfg = Path("config/plot_config.yaml")
if _cfg.exists():
    PLOT_CONFIG = yaml.safe_load(_cfg.read_text())
    apply_palette(PLOT_CONFIG.get("palette", "morandi"))
```

```r
if (file.exists("config/plot_config.yaml")) {
  PLOT_CONFIG <- yaml::read_yaml("config/plot_config.yaml")
  use_pal(PLOT_CONFIG$palette %||% "morandi")
}
```