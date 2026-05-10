# Enrichment Dot Plot

## When to Use
- **Data structure**: Enrichment analysis output with columns for: term name, p-value (or adjusted p-value), enrichment ratio/fold change, and gene count
- **Analytical purpose**: Visualize pathway/GO/KEGG enrichment results — show significance, effect size, and gene count simultaneously
- **NOT for**: Simple category counts (use bar plot), single-gene results, or raw expression data

## Why Dot Plot Over Bar Plot for Enrichment?
Dot plots encode **three variables** simultaneously: x-position (enrichment ratio), color (p-value), and size (gene count). A bar plot can only show one. For enrichment results, this triple encoding is the standard.

## Minimal Example

### R
```r
library(ggplot2)

ggplot(df, aes(x = GeneRatio, y = reorder(Description, GeneRatio))) +
  geom_point(aes(size = Count, color = p.adjust)) +
  scale_color_viridis_c(direction = -1) +
  theme_classic()
```

### Python
```python
ax.scatter(df["GeneRatio"], df["Description"],
           s=df["Count"] * 10, c=df["p.adjust"],
           cmap="viridis_r", edgecolors="grey30", linewidths=0.3)
```

---

## Full Recipe

### R (production-ready)
```r
library(ggplot2)

sci_enrichment_dot <- function(
  df,
  x_col = "GeneRatio",         # enrichment ratio / fold enrichment
  y_col = "Description",       # term name
  size_col = "Count",          # number of genes in term
  color_col = "p.adjust",      # significance (will be -log10 transformed)
  top_n = 20,                  # max number of terms to show
  order_by = "p.adjust",       # how to rank terms: "p.adjust" or x_col
  x_label = "Gene ratio",
  size_label = "Gene count",
  color_label = expression(-log[10]~"(adjusted p)"),
  truncate_names = 50,         # max characters for term names
  colors = c("#F0F0F0", "#4477AA"),  # low → high significance
  base_size = 16
) {

  data <- df

  # --- Select top N terms ---
  if (order_by == "p.adjust" || order_by == color_col) {
    data <- data[order(data[[color_col]]), ]
  } else {
    data <- data[order(-data[[x_col]]), ]
  }
  data <- head(data, top_n)

  # --- Transform p-value ---
  data$neg_log10p <- -log10(data[[color_col]])

  # --- Truncate long term names ---
  data$term_display <- ifelse(
    nchar(data[[y_col]]) > truncate_names,
    paste0(substr(data[[y_col]], 1, truncate_names - 3), "..."),
    data[[y_col]]
  )

  # --- Order y-axis by enrichment ratio ---
  data$term_display <- factor(data$term_display,
                               levels = rev(data$term_display))

  # --- Plot ---
  p <- ggplot(data, aes(
    x = .data[[x_col]],
    y = term_display,
    size = .data[[size_col]],
    color = neg_log10p
  )) +
    geom_point() +

    # Color: sequential from light to deep
    scale_color_gradient(
      low = colors[1], high = colors[2],
      name = color_label
    ) +

    # Size: reasonable range
    scale_size_continuous(
      range = c(2, 7),
      name = size_label
    ) +

    labs(
      x = x_label,
      y = NULL
    ) +

    theme_classic(base_size = base_size) +
    theme(
      text = element_text(family = "Arial"),
      axis.text.y = element_text(size = base_size - 0.5, color = "grey20"),
      axis.text.x = element_text(color = "grey30"),
      legend.position = "right",
      legend.key.height = unit(0.4, "cm"),
      legend.key.width = unit(0.3, "cm"),
      legend.title = element_text(size = base_size - 1),
      legend.text = element_text(size = base_size - 1.5),
      plot.margin = margin(5, 5, 5, 5, "pt")
    ) +

    # X-axis starts at 0
    scale_x_continuous(expand = expansion(mult = c(0, 0.05)))

  return(p)
}

# --- Usage with clusterProfiler output ---
# library(clusterProfiler)
# ego <- enrichGO(gene = gene_list, OrgDb = org.Hs.eg.db, ont = "BP")
# p <- sci_enrichment_dot(as.data.frame(ego))
# ggsave("enrichment_pub.pdf", p, width = 120, height = 100, units = "mm", dpi = 300)

# --- Usage with custom enrichment table ---
# p <- sci_enrichment_dot(my_df,
#       x_col = "fold_enrichment", y_col = "pathway",
#       size_col = "n_genes", color_col = "fdr")
```

### Python (production-ready)
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

def sci_enrichment_dot(
    df, x_col="GeneRatio", y_col="Description",
    size_col="Count", color_col="p.adjust",
    top_n=20, order_by="p.adjust",
    x_label="Gene ratio", size_label="Gene count",
    color_label=r"$-\log_{10}$(adj. p)",
    truncate_names=50,
    colors=("lightgrey", "#4477AA"),
    figsize=(4.5, 5), dpi=300, font_size=7
):
    data = df.copy()

    # Select top N
    if order_by == "p.adjust" or order_by == color_col:
        data = data.nsmallest(top_n, color_col)
    else:
        data = data.nlargest(top_n, x_col)

    # Transform
    data["neg_log10p"] = -np.log10(data[color_col].clip(lower=1e-300))

    # Truncate names
    data["term_display"] = data[y_col].apply(
        lambda s: s[:truncate_names-3] + "..." if len(str(s)) > truncate_names else s
    )

    # Sort for y-axis (top of plot = most enriched)
    data = data.sort_values(x_col, ascending=True)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # Size scaling
    size_min, size_max = data[size_col].min(), data[size_col].max()
    sizes = 20 + (data[size_col] - size_min) / max(size_max - size_min, 1) * 180

    scatter = ax.scatter(
        data[x_col], data["term_display"],
        s=sizes, c=data["neg_log10p"],
        cmap=plt.cm.Blues, edgecolors="grey30", linewidths=0.3,
        vmin=data["neg_log10p"].min(), vmax=data["neg_log10p"].max()
    )

    # Color bar
    cbar = plt.colorbar(scatter, ax=ax, shrink=0.5, pad=0.02)
    cbar.set_label(color_label, fontsize=font_size - 1)
    cbar.ax.tick_params(labelsize=font_size - 2)

    # Size legend (manual)
    size_vals = np.linspace(size_min, size_max, 3, dtype=int)
    size_dots = 20 + (size_vals - size_min) / max(size_max - size_min, 1) * 180
    legend_elements = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="grey",
               markersize=np.sqrt(s), label=str(v))
        for s, v in zip(size_dots, size_vals)
    ]
    legend = ax.legend(
        handles=legend_elements, title=size_label,
        loc="lower right", frameon=False,
        fontsize=font_size - 2, title_fontsize=font_size - 1
    )

    # Axis
    ax.set_xlabel(x_label, fontsize=font_size)
    ax.set_ylabel("")
    ax.tick_params(axis="y", labelsize=font_size - 0.5)
    ax.tick_params(axis="x", labelsize=font_size - 1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(left=0)

    plt.tight_layout()
    return fig, ax

# --- Usage ---
# fig, ax = sci_enrichment_dot(enrichment_df)
# fig.savefig("enrichment_pub.pdf", dpi=300, bbox_inches="tight")
```

---

## Parameters to Tune

| Parameter | Default | When to change |
|-----------|---------|---------------|
| `top_n` | 20 | Reduce to 10–15 for PPT (readability); up to 30 for supplementary figures |
| `truncate_names` | 50 | Shorten for PPT (35–40 chars); lengthen for wide figures |
| `order_by` | "p.adjust" | Switch to x_col to sort by enrichment magnitude instead of significance |
| `colors` | light gray → blue | Match your project palette; use `c("#FFF5EB", "#E64B35")` for warm |
| `size range` | c(2, 7) | Narrow to c(2, 5) if size differences are subtle |

---

## Pitfalls

| Problem | Solution |
|---------|----------|
| **Term names too long, get cut off** | Increase plot width; lower `truncate_names`; or manually shorten terms before plotting |
| **All dots same color** (p-values very similar) | Use a narrower color range or switch to categorical significance (*, **, ***) |
| **Too many terms, plot is unreadable** | Reduce `top_n`; or group by GO category (BP, MF, CC) and facet |
| **GeneRatio is a string like "15/200"** | Parse it first: `df$GeneRatio <- sapply(strsplit(df$GeneRatio, "/"), function(x) as.numeric(x[1])/as.numeric(x[2]))` |
| **Redundant GO terms** | Use `simplify()` from clusterProfiler to remove semantic duplicates before plotting |

---

## Variants

### Variant A: Faceted by category (BP / MF / CC)
```r
p + facet_grid(ONTOLOGY ~ ., scales = "free_y", space = "free_y") +
  theme(strip.text = element_text(face = "bold"))
```

### Variant B: Side-by-side up/down enrichment
Two columns of dots — left for downregulated genes, right for upregulated:
```r
ggplot(data, aes(x = enrichment * ifelse(direction == "up", 1, -1),
                 y = reorder(term, abs(enrichment)))) +
  geom_point(aes(size = count, color = neg_log10p)) +
  geom_vline(xintercept = 0, linetype = "dashed")
```

### Variant C: Bar + dot hybrid (cnetplot style)
Show gene-pathway connections. Use `clusterProfiler::cnetplot()` or `enrichplot::dotplot()`.

### Variant D: Emoji/icon enrichment (for presentations)
Replace dot with category-specific shapes (diamond for metabolic, circle for signaling, etc.):
```r
ggplot(data, aes(x = ratio, y = term, shape = category, size = count, color = pval)) +
  geom_point() +
  scale_shape_manual(values = c(15, 16, 17, 18))   # square, circle, triangle, diamond
```
