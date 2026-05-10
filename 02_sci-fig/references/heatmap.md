# Heatmap

## When to Use
- **Data structure**: Matrix (features × samples or features × conditions). Typically gene expression, methylation, or any continuous measurement across multiple observations.
- **Analytical purpose**: Reveal patterns, clusters, and relationships across many features simultaneously. Show which genes/features behave similarly across conditions.
- **NOT for**: Comparing two variables (use scatter), showing distributions (use violin), or small datasets (<10 features — use bar/dot instead)

## Minimal Example

### R
```r
library(ComplexHeatmap)

Heatmap(mat, name = "z-score",
        col = circlize::colorRamp2(c(-2, 0, 2), c("#4477AA", "white", "#EE6677")))
```

### Python
```python
import seaborn as sns

sns.clustermap(df, cmap="RdBu_r", center=0, figsize=(8, 10),
               row_cluster=True, col_cluster=True)
```

---

## Full Recipe

### R (ComplexHeatmap — recommended for publication)
```r
library(ComplexHeatmap)
library(circlize)

sci_heatmap <- function(
  mat,                          # numeric matrix, rows = features, cols = samples
  row_anno_df = NULL,           # data.frame for row annotation (optional)
  col_anno_df = NULL,           # data.frame for column annotation (optional)
  scale_rows = TRUE,            # z-score rows
  colors = c("#4477AA", "white", "#EE6677"),  # low, mid, high
  color_range = c(-2, 0, 2),
  show_row_names = FALSE,       # usually too many genes
  show_col_names = TRUE,
  cluster_rows = TRUE,
  cluster_cols = TRUE,
  row_split = NULL,             # integer k or factor for row grouping
  col_split = NULL,
  name = "z-score",
  base_size = 16,                # change to 14 for presentation
  ...
) {

  # --- Scale if requested ---
  if (scale_rows) {
    mat <- t(scale(t(mat)))
    mat[is.na(mat)] <- 0  # handle zero-variance rows
  }

  # --- Color mapping ---
  col_fun <- colorRamp2(color_range, colors)

  # --- Column annotation ---
  col_ha <- NULL
  if (!is.null(col_anno_df)) {
    # Auto-assign colors from project palette
    anno_colors <- list()
    palette_pool <- c("#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE", "#AA3377")
    for (col_name in names(col_anno_df)) {
      levels <- unique(col_anno_df[[col_name]])
      anno_colors[[col_name]] <- setNames(
        palette_pool[seq_along(levels)],
        levels
      )
    }
    col_ha <- HeatmapAnnotation(
      df = col_anno_df,
      col = anno_colors,
      annotation_name_gp = gpar(fontsize = base_size, fontfamily = "Arial"),
      annotation_legend_param = list(
        labels_gp = gpar(fontsize = base_size - 1),
        title_gp = gpar(fontsize = base_size, fontface = "bold")
      )
    )
  }

  # --- Row annotation ---
  row_ha <- NULL
  if (!is.null(row_anno_df)) {
    anno_colors_row <- list()
    palette_pool2 <- c("#E64B35", "#4DBBD5", "#00A087", "#3C5488", "#F39B7F")
    for (col_name in names(row_anno_df)) {
      levels <- unique(row_anno_df[[col_name]])
      anno_colors_row[[col_name]] <- setNames(
        palette_pool2[seq_along(levels)],
        levels
      )
    }
    row_ha <- rowAnnotation(
      df = row_anno_df,
      col = anno_colors_row,
      annotation_name_gp = gpar(fontsize = base_size, fontfamily = "Arial")
    )
  }

  # --- Heatmap ---
  ht <- Heatmap(
    mat,
    name = name,
    col = col_fun,
    top_annotation = col_ha,
    left_annotation = row_ha,

    # Clustering
    cluster_rows = cluster_rows,
    cluster_columns = cluster_cols,
    row_split = row_split,
    column_split = col_split,

    # Display
    show_row_names = show_row_names,
    show_column_names = show_col_names,
    row_names_gp = gpar(fontsize = base_size - 2, fontface = "italic", fontfamily = "Arial"),
    column_names_gp = gpar(fontsize = base_size - 1, fontfamily = "Arial"),
    column_names_rot = 45,

    # Legend
    heatmap_legend_param = list(
      title = name,
      title_gp = gpar(fontsize = base_size, fontface = "bold", fontfamily = "Arial"),
      labels_gp = gpar(fontsize = base_size - 1, fontfamily = "Arial"),
      legend_height = unit(3, "cm")
    ),

    # Visual
    border = TRUE,
    row_gap = unit(1, "mm"),
    column_gap = unit(1, "mm"),

    ...
  )

  return(ht)
}

# --- Usage ---
# ht <- sci_heatmap(expr_matrix, col_anno_df = sample_info[, "condition", drop=FALSE])
#
# Publication export:
# pdf("heatmap_pub.pdf", width = 7.08, height = 8)
# draw(ht)
# dev.off()
#
# Presentation export:
# png("heatmap_ppt.png", width = 9, height = 6, units = "in", res = 200, bg = "transparent")
# draw(sci_heatmap(expr_matrix, col_anno_df = sample_info, base_size = 14))
# dev.off()
```

### Python (seaborn clustermap)
```python
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import zscore

def sci_heatmap(
    df,                         # DataFrame, rows=features, cols=samples
    col_anno=None,              # Series or dict mapping sample → group
    scale_rows=True,
    cmap="RdBu_r",
    center=0,
    vmin=-2, vmax=2,
    show_row_names=False,
    figsize=(7, 8),             # publication: (7, 8); ppt: (10, 6)
    dpi=300,
    font_size=7,                # publication: 7; ppt: 14
    row_cluster=True,
    col_cluster=True
):
    mat = df.copy()

    # Scale rows
    if scale_rows:
        mat = mat.apply(zscore, axis=1)
        mat = mat.fillna(0)

    # Column color annotation
    col_colors = None
    if col_anno is not None:
        if isinstance(col_anno, dict):
            col_anno = pd.Series(col_anno)
        palette = ["#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE", "#AA3377"]
        groups = col_anno.unique()
        lut = dict(zip(groups, palette[:len(groups)]))
        col_colors = col_anno.map(lut)

    # Plot
    g = sns.clustermap(
        mat,
        cmap=cmap,
        center=center,
        vmin=vmin, vmax=vmax,
        figsize=figsize,
        row_cluster=row_cluster,
        col_cluster=col_cluster,
        col_colors=col_colors,
        yticklabels=show_row_names,
        xticklabels=True,
        dendrogram_ratio=(0.1, 0.08),
        cbar_pos=(0.02, 0.8, 0.03, 0.15),
        tree_kws=dict(linewidths=0.5),
    )

    # Font adjustments
    g.ax_heatmap.set_xticklabels(
        g.ax_heatmap.get_xticklabels(),
        fontsize=font_size - 1, rotation=45, ha="right"
    )
    if show_row_names:
        g.ax_heatmap.set_yticklabels(
            g.ax_heatmap.get_yticklabels(),
            fontsize=font_size - 2, fontstyle="italic"
        )

    g.ax_heatmap.tick_params(axis="both", length=2, width=0.5)
    g.figure.set_dpi(dpi)

    return g

# --- Usage ---
# g = sci_heatmap(expr_df, col_anno=sample_info["condition"])
# g.savefig("heatmap_pub.pdf", dpi=300, bbox_inches="tight")
```

---

## Parameters to Tune

| Parameter | Default | When to change |
|-----------|---------|---------------|
| `scale_rows` | TRUE | Set FALSE if data is already normalized or you want absolute values |
| `color_range` | [-2, 0, 2] | Widen to [-3,0,3] for high-variance data; narrow for subtle patterns |
| `show_row_names` | FALSE | TRUE only if ≤50 features AND names are meaningful |
| `row_split` | NULL | Set to k (integer) for k-means grouping, or pass a factor for known groups |
| `column_names_rot` | 45 | Use 0 if names are short (≤5 chars); 90 if very long |

---

## Pitfalls

| Problem | Solution |
|---------|----------|
| **One extreme value dominates the color scale** | Clip outliers: `mat[mat > 3] <- 3; mat[mat < -3] <- -3` |
| **Row names illegible (too many genes)** | Don't show them. Use `show_row_names = FALSE` and annotate key genes with `row_annotation` or arrows |
| **Dendrogram overwhelms the figure** | Reduce `dendrogram_ratio` (Python) or set `show_row_dend = FALSE` (R) |
| **Sample annotation colors clash with heatmap** | Use distinct, muted annotation colors; keep the heatmap colorscale (diverging) separate from categorical annotations |
| **White bands appear between cells** | Set `border = TRUE` (R) or increase figure resolution |

---

## Variants

### Variant A: Split heatmap by gene cluster
Use `row_split = kmeans(mat, centers = 4)$cluster` in R to automatically group genes.
Shows distinct expression programs.

### Variant B: Heatmap with selected gene labels
Instead of showing all row names, annotate only specific genes:
```r
# R: Use mark annotation
row_ha <- rowAnnotation(
  marker = anno_mark(
    at = which(rownames(mat) %in% genes_of_interest),
    labels = genes_of_interest,
    labels_gp = gpar(fontsize = 6, fontface = "italic")
  )
)
```

### Variant C: Correlation heatmap
Square matrix, symmetric. Use `corrplot` (R) or `sns.heatmap` with mask for upper triangle.

### Variant D: Compact heatmap for PPT
Fewer features (top 50 most variable), larger fonts, no dendrogram, column annotation only.
Optimized for readability at presentation distance.
