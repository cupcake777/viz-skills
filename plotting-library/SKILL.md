---
name: plotting-library
description: Personal scientific plotting method library at /root/ops/plotting/. The EXECUTION layer for the sci-fig skill — enforces consistent style via shared matplotlibrc and runnable template scripts. sci-fig owns the knowledge/learning protocol, plotting-library owns the runnable code.
version: 1.2
tags: [plotting, visualization, matplotlib, bioinformatics]
related_skills: [sci-fig]
canonical_source: https://github.com/cupcake777/viz-skills/tree/main/plotting-library
---
# Plotting Library

Personal scientific plotting method library at `/root/plotting-library/`.

## Structure
```
plotting-library/           # BRAIN_PLOTTING_DIR=/root/ops/plotting
├── catalog.yaml            # Data type → chart → template index
├── requirements.txt        # Python deps
├── style/matplotlibrc      # Global style config (Nature palette)
├── *_demo.png              # Demo output images (served via Gallery)
├── gallery_feedback.jsonl  # User feedback (approve/suggest/reject)
├── templates/              # Standalone plot scripts (17 total)
│   ├── volcano.py          # Differential expression
│   ├── manhattan.py         # QTL/GWAS
│   ├── heatmap_clustered.py # Expression matrix
│   ├── apa_pattern.py      # APA pattern scatter (custom)
│   ├── grouped_bar.py      # Grouped comparison
│   ├── enrichment_bubble.py # GO/KEGG enrichment
│   ├── sankey.py           # APA flow (Plotly — no PNG demo)
│   ├── correlation_heatmap.py  # Correlation matrix with clustering
│   ├── box_violin.py        # Combined violin+box plot
│   ├── ridgeline.py         # Joy/ridgeline density plot
│   ├── network_graph.py     # Gene interaction network
│   ├── pca_plot.py          # PCA 2D scatter with confidence ellipses
│   ├── umap_plot.py         # UMAP 2D scatter with convex hull
│   ├── km_survival.py       # Kaplan-Meier survival curves
│   ├── roc_curve.py         ROC curves with AUC
│   ├── upset_plot.py        # UpSet intersection plot
│   └── enrichment_circos.py # Circular enrichment bubble chart
└── demo_data/               # Mock data for each template
```

## Design Principles
- **Data-driven**: catalog.yaml defines data_type → recommended chart mapping
- **Self-contained**: each template has `generate_mock_data()` + `plot()` + `__main__`
- **Unified style**: `style/matplotlibrc` (Nature palette, font, DPI)
- **Easy extension**: add template file + update catalog.yaml

## Usage Pattern
1. Check `catalog.yaml` for data_type → chart mapping
2. Copy relevant template, replace data path
3. Adjust parameters in top config section
4. Run `python my_plot.py`

## Style Loading
Templates use: `matplotlib.rc_file(str(STYLE_PATH), plt.rcParams)`
- STYLE_PATH auto-resolves relative to template file

## Key Parameters (per template top section)
- volcano: FC_THRESHOLD, P_THRESHOLD, LABEL_TOP_N
- manhattan: GENOME_LINE (5e-8), SUGGESTIVE_LINE (1e-5)
- apa_pattern: PATTERN_COLORS dict, P_THRESHOLD
- heatmap_clustered: CMAP_DEFAULT, Z_SCORE_AXIS
- grouped_bar: BAR_WIDTH, ADD_NUMBERS
- enrichment_bubble: SHOW_TOP_N, BUBBLE_SCALE
- correlation_heatmap: SHOW_UPPER, ANNOT_FONT_SIZE
- box_violin: VIOLIN_ALPHA, SHOW_POINTS
- ridgeline: RIDGE_SPACING, KDE_BW
- network_graph: NODE_SIZE_SCALE, LAYOUT_SEED
- pca_plot: CONFIDENCE_LEVEL(0.68), ELLIPSE_ALPHA
- km_survival: LIFELINES_FALLBACK, SHOW_RISK_TABLE
- roc_curve: DIAGONAL_LINE, FILL_AUC
- upset_plot: MIN_INTERSECTION_SIZE
- umap_plot: N_NEIGHBORS, MIN_DIST, HULL_ALPHA
- enrichment_circos: MAX_TERMS, ANGLE_OFFSET

## Adding New Charts
1. Create `templates/new_chart.py` with `generate_mock_data()` + `plot()` + `__main__`
2. Run `python3 templates/new_chart.py` to generate `{name}_demo.png` in the plotting dir
3. Add entry to `catalog.yaml` under `charts:` with name, data_type, columns, description, tags, template
4. Add mapping to `_demo_map` in `/root/ops/brain/hermes/templates.py` (key=catalog name, value=demo PNG filename, or `None` if no PNG)
5. Restart hermes-serve: `sudo systemctl restart hermes-serve`
6. Verify: `python3 -c "from hermes.templates import gallery_page; print('OK')"` then curl the /gallery endpoint

**Template naming conventions:**
- Python file: `snake_case.py` (e.g., `correlation_heatmap.py`, `km_survival.py`)
- Demo PNG: `{catalog_name}_demo.png` (e.g., `correlation_heatmap_demo.png`, `pca_demo.png`)
- Note: demo PNG names don't always match template names — `heatmap_clustered` template produces `heatmap_demo.png`, `pca_plot` produces `pca_demo.png`

**Special case — Plotly templates:** `sankey.py` uses plotly.graph_objects and outputs HTML, not PNG. In `_demo_map`, set value to `None` (no preview image). The `has_template` check still marks it as having a template.

## New Charts (APA/Neuroscience Priority)

### Tier 1: High Priority (Research Core)

**lifespan_trajectory** — PDUI/expression over developmental stages
- Data: `lifespan_trajectory` (gene, stage, value, brain_region)
- Key params: STAGE_ORDER (Fetal→Aged), TRAFFIC_LIGHT_COLORS, SMOOTH_WINDOW
- Mock: 6 genes × 6 stages × 4 brain regions

**brain_atlas_heatmap** — Multi-brain-region expression with anatomical labels
- Data: `brain_region_matrix` (gene, region, value)
- Key params: REGION_ORDER (anatomical: cortex→subcortex→cerebellum), ANNOTATION_FILE
- Mock: dendrogram-like annotation + expression matrix

**gene_structure_apa** — Gene structure with 3'UTR APA sites
- Data: `gene_apa_structure` (exon_starts, exon_ends, pas_positions, pas_types)
- Key params: PROXIMAL_COLOR, DISTAL_COLOR, INTRON_STYLE
- Mock: multi-exon gene with 2-3 PAS sites

### Tier 2: Medium Priority (Common Needs)

**dot_plot_seurat** — Seurat-style marker gene expression
- Data: `marker_expression` (gene, cluster, pct_expressed, avg_expr)
- Key params: DOT_SIZE_RANGE, COLOR_RANGE, CLUSTER_ORDER

**forest_plot** — Meta-analysis OR/HR with confidence intervals
- Data: `meta_analysis` (variable, estimate, ci_lower, ci_upper)
- Key params: REFERENCE_LINE(1.0), X_SCALE(log)

**lollipop** — Gene mutation/modification site annotation
- Data: `mutation_site` (position, type, count)
- Key params: MARKER_SIZE, DOMAIN_TRACK

**stacked_area** — Composition change over time
- Data: `composition_over_time` (timepoint, category, proportion)
- Key params: AREA_SORT(DESC), LABEL_THRESHOLD(0.05)

### Tier 3: Nice to Have

**chromosome_ideogram** — Genomic region annotation on chromosome
- Data: `genomic_region` (chr, start, end, label, category)
- Key params: CHR_HEIGHT, BAND_COLOR_MAP

### Template Implementation Status

| Template | Status | catalog.yaml | _demo_map |
|----------|--------|-------------|-----------|
| lifespan_trajectory | 📋 Planned | Pending | Pending |
| brain_atlas_heatmap | 📋 Planned | Pending | Pending |
| gene_structure_apa | 📋 Planned | Pending | Pending |
| dot_plot_seurat | 📋 Planned | Pending | Pending |
| forest_plot | 📋 Planned | Pending | Pending |
| lollipop | 📋 Planned | Pending | Pending |
| stacked_area | 📋 Planned | Pending | Pending |
| chromosome_ideogram | 📋 Planned | Pending | Pending |

When implementing a new template:
1. Create `templates/{name}.py` with `generate_mock_data()` + `plot()` + `__main__`
2. Run `python3 templates/{name}.py` to generate `{name}_demo.png`
3. Add entry to `catalog.yaml` under `charts:`
4. Add entry to `_demo_map` in `/root/ops/brain/hermes/templates.py`
5. `sudo systemctl restart hermes-serve`
6. Verify: `python3 -c "from hermes.templates import gallery_page; print('OK')"`

---

## Known Pitfalls
- **matplotlib style loading**: Use `matplotlib.rc_file(str(STYLE_PATH), plt.rcParams)` NOT `plt.rc_params_from_file()` (that function requires `from matplotlib import rc_params_from_file`). Safer: wrap in try/except.
- **pandas applymap deprecated**: Use `df.map()` instead of `df.applymap()` (pandas ≥2.1).
- **numpy array shape mismatch**: When indexing with boolean masks, compute `n_sig = len(sig_idx)` first, then `sig_idx[:n_sig//2]` and `sig_idx[n_sig//2:]` — don't use the original `n` for slicing the subset.
- **km_survival tight_layout warning**: If using risk table subplots, `plt.tight_layout()` may warn about incompatible Axes. Use `plt.subplots_adjust()` instead for manual spacing.
- **network_graph layout**: Uses `networkx.spring_layout()` if available, falls back to circular layout. Ensure `networkx` is installed for best results.
- **sankey.py depends on plotly**: `sankey.py` requires `plotly.graph_objects` which is NOT in the standard install. This template generates HTML output, not PNG. In the Gallery `_demo_map`, set value to `None` for no preview image.
- **Brain service must restart**: Template changes in `plotting/` dir and `templates.py` require `sudo systemctl restart hermes-serve` to take effect (production mode has no --reload).
- **credentials**: HF write token stored at `/root/ops/.secrets/` (chattr+i locked)
## Pitfalls (discovered during development)
1. **matplotlib style loading**: Do NOT use `import matplotlib.rc_params_from_file` or `plt.rc_params_from_file()`. Correct call: `matplotlib.rc_file(str(STYLE_PATH), plt.rcParams)` — loads rc file and updates rcParams in-place.
2. **pandas applymap deprecated**: Use `df.map(lambda x: ...)` instead of `df.applymap()` (removed in pandas 3.x). For row/col-specific maps use `df.map()` on Series.
3. **numpy broadcasting in mock data**: When indexing arrays like `arr[idx[:half]] += rng.uniform(1.5, 4, ???)`, the size of the random array must match `len(idx[:half])`, NOT the total array length. Use `n_sig = len(significant_idx); half = n_sig // 2`.
4. **scipy required for seaborn clustermap**: `sns.clustermap()` silently fails without scipy. Add `scipy>=1.10` to requirements.

## Brain Web Gallery Integration

The plotting library is served as an interactive gallery in the Brain web app at `/gallery`.

**Architecture:**
- `BRAIN_PLOTTING_DIR=/root/ops/plotting` env var (set in hermes-serve systemd service)
- `catalog.yaml` defines chart metadata (name, title, data_type, description, tags)
- `_demo_map` in `templates.py` maps catalog names to demo PNG filenames
- `StaticFiles` mount at `/gallery/static` serves demo PNGs from the plotting dir
- Template `.py` files in `templates/` directory (catalog `template:` field resolves to these)
- `has_template` check looks for BOTH `{name}.py` and the catalog `template:` path
- Feedback API: `POST /api/gallery/feedback` writes to `gallery_feedback.jsonl`

**_demo_map (17 entries):**
```python
_demo_map = {
    "volcano": "volcano_demo.png",
    "manhattan": "manhattan_demo.png",
    "heatmap_clustered": "heatmap_demo.png",
    "apa_pattern": "apa_pattern_demo.png",
    "enrichment_bubble": "enrichment_bubble_demo.png",
    "grouped_bar": "grouped_bar_demo.png",
    "correlation_heatmap": "correlation_heatmap_demo.png",
    "apa_sankey": None,  # plotly-based, no PNG demo
    "enrichment_circos": "enrichment_circos_demo.png",
    "box_violin": "box_violin_demo.png",
    "ridgeline": "ridgeline_demo.png",
    "network_graph": "network_graph_demo.png",
    "upset_plot": "upset_demo.png",
    "pca_plot": "pca_demo.png",
    "umap_plot": "umap_demo.png",
    "km_survival": "km_survival_demo.png",
    "roc_curve": "roc_demo.png",
}
```

**After adding a new template or demo image:** `sudo systemctl restart hermes-serve`

## Relationship to sci-fig Skill

**This skill provides executable scripts + mock data.** For chart type selection guidance, visual standards (color palettes, typography, presets), R+Python production recipes, QA checklists, and the figure learning protocol (deconstruct → save variant → reuse), use the **sci-fig** skill instead.

Division of labor:
- `plotting-library` → Run `python template.py` directly, generates real plots from real data, has HF gallery
- `sci-fig` → Knowledge base for WHAT to plot, HOW to style it, and LEARNING from example figures

When generating a figure, load BOTH: sci-fig for chart selection + style rules, then plotting-library for copy-paste Python scripts.

## Reference Sites
- R2Omics: https://www.r2omics.cn/docs/gallery/ (R-based, 68 charts, copy-paste code)
- HiPlot: https://hiplot.cn/ (280+ charts, interactive Vue/Shiny, tag-based)