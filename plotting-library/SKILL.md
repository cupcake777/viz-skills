---
name: plotting-library
description: Personal scientific plotting method library at /root/ops/plotting/. The EXECUTION layer for the sci-fig skill — enforces consistent style via shared matplotlibrc and runnable template scripts. sci-fig owns the knowledge/learning protocol, plotting-library owns the runnable code.
version: 1.3
tags: [plotting, visualization, matplotlib, bioinformatics]
related_skills: [sci-fig]
canonical_source: https://github.com/cupcake777/viz-skills/tree/main/plotting-library
compatibility: Requires Python 3.9+ with matplotlib, numpy, pandas, scipy, and various plotting libraries (seaborn, networkx, plotly, lifelines, etc.). See plotting/requirements.txt.
---
# Plotting Library

Personal scientific plotting method library at `/root/ops/plotting/`.

## Single Source of Truth: `catalog.yaml`

**All chart definitions live in `/root/ops/plotting/catalog.yaml`.** This file is the authoritative registry for:

- Chart name, title, description, data_type, columns, tags
- Tier (P0/P1/P2) and status (done/planned)
- Template path and demo image filename
- Recommended use cases and reference sites

The Gallery web app reads `catalog.yaml` **dynamically on every request** — no hardcoded `_demo_map`, no restart needed for new charts. If you need to know what charts exist, what their status is, or what data they need, **read catalog.yaml**, not this SKILL.md.

## Structure
```
plotting-library/           # BRAIN_PLOTTING_DIR=/root/ops/plotting
├── catalog.yaml            # ★ Single source of truth (charts, tiers, status)
├── requirements.txt        # Python deps
├── style/matplotlibrc      # Global style config (Nature palette)
├── *_demo.png              # Demo output images (served via Gallery)
├── gallery_feedback.jsonl  # User feedback (approve/suggest/reject)
├── templates/              # Standalone plot scripts
│   ├── volcano.py
│   ├── raincloud.py
│   └── ... (see catalog.yaml for full list)
└── demo_data/              # Mock data for each template
```

## Design Principles
- **Data-driven**: catalog.yaml defines data_type → recommended chart mapping
- **Self-contained**: each template has `generate_mock_data()` + `plot()` + `__main__`
- **Unified style**: `style/matplotlibrc` (Nature palette, font, DPI)
- **Easy extension**: add template file + update catalog.yaml → Gallery auto-discovers

## Usage Pattern
1. Check `catalog.yaml` for data_type → chart mapping
2. Copy relevant template, replace data path
3. Adjust parameters in top config section
4. Run `python my_plot.py`

## Style Loading
Templates use: `matplotlib.rc_file(str(STYLE_PATH), plt.rcParams)`
- STYLE_PATH auto-resolves relative to template file

## Adding New Charts
1. Create `templates/{name}.py` with `generate_mock_data()` + `plot()` + `__main__`
2. Run `python3 templates/{name}.py` to generate `{name}_demo.png`
3. Add entry to `catalog.yaml` under `charts:` with tier, status, data_type, etc.
4. Gallery auto-discovers — no restart needed. Only `templates.py` code changes require `sudo systemctl restart hermes-serve`

**Template naming:** `snake_case.py` (e.g., `raincloud.py`), demo PNG: `{name}_demo.png`

**Plotly templates** (e.g., sankey.py): output HTML, not PNG. Set `demo: null` in catalog.yaml.

## Key Parameters (per template top section)

See `catalog.yaml` for the full chart list. Common template parameters:

| Template | Key Params |
|----------|-----------|
| volcano | FC_THRESHOLD, P_THRESHOLD, LABEL_TOP_N |
| manhattan | GENOME_LINE (5e-8), SUGGESTIVE_LINE (1e-5) |
| apa_pattern | PATTERN_COLORS dict, P_THRESHOLD |
| heatmap_clustered | CMAP_DEFAULT, Z_SCORE_AXIS |
| grouped_bar | BAR_WIDTH, ADD_NUMBERS |
| enrichment_bubble | SHOW_TOP_N, BUBBLE_SCALE |
| correlation_heatmap | SHOW_UPPER, ANNOT_FONT_SIZE |
| box_violin | VIOLIN_ALPHA, SHOW_POINTS |
| ridgeline | RIDGE_SPACING, KDE_BW |
| raincloud | VIOLIN_WIDTH, BOX_WIDTH, RAIN_POINT_SIZE, ORIENTATION |
| network_graph | NODE_SIZE_SCALE, LAYOUT_SEED |
| pca_plot | CONFIDENCE_LEVEL(0.68), ELLIPSE_ALPHA |
| km_survival | LIFELINES_FALLBACK, SHOW_RISK_TABLE |
| roc_curve | DIAGONAL_LINE, FILL_AUC |
| upset_plot | MIN_INTERSECTION_SIZE |
| umap_plot | N_NEIGHBORS, MIN_DIST, HULL_ALPHA |
| enrichment_circos | MAX_TERMS, ANGLE_OFFSET |

## Brain Web Gallery Integration

The plotting library is served as an interactive gallery in the Brain web app at `/gallery`.

**Architecture:**
- `BRAIN_PLOTTING_DIR=/root/ops/plotting` env var (set in hermes-serve systemd service)
- `catalog.yaml` is the **single source of truth** — Gallery reads it dynamically each request
- `StaticFiles` mount at `/gallery/static` serves demo PNGs from the plotting dir
- Template `.py` files in `templates/` directory (catalog `template:` field resolves to these)
- `has_template` check looks for BOTH `{name}.py` and the catalog `template:` path
- Feedback API: `POST /api/gallery/feedback` writes to `gallery_feedback.jsonl`

**Hot reload:** Gallery reads catalog.yaml on every request. Adding a new chart = update catalog.yaml + add demo PNG = instant. No restart needed. Only `templates.py` code changes require `sudo systemctl restart hermes-serve`.

## Feedback Loop (gallery_feedback.jsonl)

Users can approve/suggest/reject charts in the Gallery. Feedback writes to `gallery_feedback.jsonl`:

```json
{"action":"approve","chart":"raincloud","timestamp":"2026-05-09T07:51:00"}
{"action":"suggest","chart":"volcano","suggestion":"add gradient color option","timestamp":"2026-05-09T07:52:00"}
{"action":"reject","chart":"box_violin","timestamp":"2026-05-09T07:53:00"}
```

**Agent should periodically read this file and process suggestions:**
1. `cat /root/ops/plotting/gallery_feedback.jsonl` — review feedback
2. For `suggest`: modify template → re-run demo → update Gallery
3. For `reject`: evaluate whether to fix or remove from catalog
4. After processing, truncate the file (or move processed entries to an archive)

## Relationship to sci-fig Skill

**This skill provides executable scripts + mock data.** For chart type selection guidance, visual standards (color palettes, typography, presets), R+Python production recipes, QA checklists, and the figure learning protocol (deconstruct → save variant → reuse), use the **sci-fig** skill instead.

Division of labor:
- `plotting-library` → Run `python template.py` directly, generates real plots from real data
- `sci-fig` → Knowledge base for WHAT to plot, HOW to style it, and LEARNING from example figures

When generating a figure, load BOTH: sci-fig for chart selection + style rules, then plotting-library for copy-paste Python scripts.

## Reference Sites
- **Sci-fig skill** → `references/site-survey.md` — comprehensive 3-site comparison (SRplot/ChiPlot/Bioincloud)
- R2Omics: https://www.r2omics.cn/docs/gallery/ (R-based, 68 charts, copy-paste code)
- HiPlot: https://hiplot.cn/ (280+ charts, interactive Vue/Shiny, tag-based)

## Known Pitfalls

1. **matplotlib style loading**: Use `matplotlib.rc_file(str(STYLE_PATH), plt.rcParams)` — NOT `plt.rc_params_from_file()`. Wrap in try/except.
2. **pandas applymap deprecated**: Use `df.map()` instead of `df.applymap()` (pandas ≥2.1).
3. **numpy broadcasting in mock data**: Index array sizes must match. Use `n_sig = len(significant_idx)`.
4. **scipy required for seaborn clustermap**: Add `scipy>=1.10` to requirements.
5. **raincloud box plot**: Use `plt.Rectangle()` manually — don't use `ax.boxplot()` because it conflicts with KDE-based violin positioning.
6. **raincloud orientation**: vertical=violin LEFT, rain RIGHT; horizontal=violin BOTTOM, rain TOP.
7. **sankey.py requires plotly**: Not in standard install. Set `demo: null` in catalog.
8. **Credentials**: HF write token at `/root/ops/.secrets/` (chattr+i locked).
9. **Brain UI CSS铁律**: templates.py两区域 — _DARK_CSS (plain string用{}), 其余page body (f-string用{{}}). patch前必须确认区域。