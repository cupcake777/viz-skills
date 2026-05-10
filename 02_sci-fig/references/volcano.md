# Volcano Plot

## When to Use
- **Data structure**: Table with columns for log2 fold change, p-value (or adjusted p-value), and gene/feature ID
- **Analytical purpose**: Visualize differential expression — simultaneously showing magnitude (fold change) and significance (p-value)
- **NOT for**: Time series data, continuous relationships, categorical comparisons

## Minimal Example

### R
```r
library(ggplot2)

ggplot(df, aes(x = log2FoldChange, y = -log10(padj))) +
  geom_point(aes(color = significant), size = 0.8, alpha = 0.6) +
  scale_color_manual(values = c("grey70", "#E64B35")) +
  theme_classic()
```

### Python
```python
import matplotlib.pyplot as plt
import numpy as np

colors = np.where(df["significant"], "#E64B35", "#B0B0B0")
plt.scatter(df["log2FoldChange"], -np.log10(df["padj"]),
            c=colors, s=3, alpha=0.6, edgecolors="none")
```

---

## Full Recipe

### R (production-ready)
```r
library(ggplot2)
library(ggrepel)

volcano_plot <- function(
  df,
  x_col = "log2FoldChange",
  y_col = "padj",
  label_col = "gene",
  fc_cutoff = 1,
  p_cutoff = 0.05,
  top_n_labels = 15,
  colors = c("down" = "#4477AA", "ns" = "grey75", "up" = "#EE6677"),
  point_size = 0.8,
  label_size = 2.5,
  base_size = 16   # change to 16 for presentation preset
) {

  # --- Prepare data ---
  data <- df
  data$log2FC <- data[[x_col]]
  data$neg_log10p <- -log10(data[[y_col]])
  data$label <- data[[label_col]]

  data$group <- "ns"
  data$group[data[[y_col]] < p_cutoff & data$log2FC > fc_cutoff] <- "up"
  data$group[data[[y_col]] < p_cutoff & data$log2FC < -fc_cutoff] <- "down"
  data$group <- factor(data$group, levels = c("down", "ns", "up"))

  # Count for subtitle
  n_up <- sum(data$group == "up")
  n_down <- sum(data$group == "down")

  # Top genes to label (by significance among significant hits)
  sig_genes <- data[data$group != "ns", ]
  sig_genes <- sig_genes[order(sig_genes[[y_col]]), ]
  to_label <- head(sig_genes, top_n_labels)

  # --- Plot ---
  p <- ggplot(data, aes(x = log2FC, y = neg_log10p)) +

    # Points: non-significant first (background), significant on top
    geom_point(
      data = subset(data, group == "ns"),
      color = colors["ns"], size = point_size, alpha = 0.4
    ) +
    geom_point(
      data = subset(data, group != "ns"),
      aes(color = group), size = point_size, alpha = 0.7
    ) +
    scale_color_manual(values = colors, guide = "none") +

    # Threshold lines
    geom_vline(xintercept = c(-fc_cutoff, fc_cutoff),
               linetype = "dashed", color = "grey50", linewidth = 0.3) +
    geom_hline(yintercept = -log10(p_cutoff),
               linetype = "dashed", color = "grey50", linewidth = 0.3) +

    # Gene labels (ALWAYS use ggrepel, NEVER geom_text)
    geom_text_repel(
      data = to_label,
      aes(label = label),
      size = label_size,
      fontface = "italic",             # gene names are italic
      max.overlaps = 25,
      min.segment.length = 0,
      segment.size = 0.25,
      segment.color = "grey40",
      box.padding = 0.35,
      point.padding = 0.2,
      force = 2,
      force_pull = 0.5,
      max.iter = 20000
    ) +

    # Labels
    labs(
      x = expression(log[2]~"fold change"),
      y = expression(-log[10]~"(adjusted p-value)"),
      subtitle = paste0("Up: ", n_up, "  Down: ", n_down)
    ) +

    # Theme
    theme_classic(base_size = base_size) +
    theme(
      text = element_text(family = "Arial"),
      axis.text = element_text(color = "grey30"),
      plot.subtitle = element_text(size = base_size - 1, color = "grey40"),
      plot.margin = margin(5, 10, 5, 5, "pt")
    )

  return(p)
}

# --- Usage ---
# p <- volcano_plot(deseq_results, label_col = "gene_name")
# ggsave("volcano_pub.pdf", p, width = 85, height = 80, units = "mm", dpi = 300)
# ggsave("volcano_ppt.png", p + theme(text = element_text(size = 16)),
#        width = 9, height = 5, dpi = 200, bg = "transparent")
```

### Python (production-ready)
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text

def volcano_plot(
    df,
    x_col="log2FoldChange",
    y_col="padj",
    label_col="gene",
    fc_cutoff=1.0,
    p_cutoff=0.05,
    top_n_labels=15,
    colors={"down": "#4477AA", "ns": "#B0B0B0", "up": "#EE6677"},
    point_size=3,
    label_size=6,
    figsize=(3.35, 3.15),    # publication single-column
    dpi=300
):
    data = df.copy()
    data["log2FC"] = data[x_col]
    data["neg_log10p"] = -np.log10(data[y_col].clip(lower=1e-300))

    # Classify
    data["group"] = "ns"
    data.loc[(data[y_col] < p_cutoff) & (data["log2FC"] > fc_cutoff), "group"] = "up"
    data.loc[(data[y_col] < p_cutoff) & (data["log2FC"] < -fc_cutoff), "group"] = "down"

    n_up = (data["group"] == "up").sum()
    n_down = (data["group"] == "down").sum()

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # Plot non-significant (background)
    ns = data[data["group"] == "ns"]
    ax.scatter(ns["log2FC"], ns["neg_log10p"],
               c=colors["ns"], s=point_size, alpha=0.4, edgecolors="none", zorder=1)

    # Plot significant (foreground)
    for grp in ["down", "up"]:
        sub = data[data["group"] == grp]
        ax.scatter(sub["log2FC"], sub["neg_log10p"],
                   c=colors[grp], s=point_size, alpha=0.7, edgecolors="none", zorder=2)

    # Threshold lines
    ax.axvline(-fc_cutoff, ls="--", lw=0.5, color="grey")
    ax.axvline(fc_cutoff, ls="--", lw=0.5, color="grey")
    ax.axhline(-np.log10(p_cutoff), ls="--", lw=0.5, color="grey")

    # Labels — top N significant genes
    sig = data[data["group"] != "ns"].nsmallest(top_n_labels, y_col)
    texts = []
    for _, row in sig.iterrows():
        texts.append(ax.text(
            row["log2FC"], row["neg_log10p"], row[label_col],
            fontsize=label_size, fontstyle="italic", zorder=3
        ))

    if texts:
        adjust_text(
            texts, ax=ax,
            arrowprops=dict(arrowstyle="-", color="grey", lw=0.4),
            force_text=(0.5, 0.8),
            force_points=(0.3, 0.5),
            expand_text=(1.2, 1.4),
            max_move=None
        )

    # Axis labels
    ax.set_xlabel(r"$\log_2$ fold change", fontsize=label_size + 1)
    ax.set_ylabel(r"$-\log_{10}$ (adjusted p-value)", fontsize=label_size + 1)
    ax.set_title(f"Up: {n_up}   Down: {n_down}", fontsize=label_size, color="grey")

    # Clean axes
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    return fig, ax

# --- Usage ---
# fig, ax = volcano_plot(deseq_df, label_col="gene_name")
# fig.savefig("volcano_pub.pdf", dpi=300, bbox_inches="tight")
```

---

## Parameters to Tune

| Parameter | Default | When to change |
|-----------|---------|---------------|
| `fc_cutoff` | 1 | Lower to 0.5 for subtle effects; raise to 2 for stringent filtering |
| `p_cutoff` | 0.05 | Use 0.01 or FDR threshold appropriate for your study |
| `top_n_labels` | 15 | Reduce if labels still overlap; increase if figure has space |
| `colors` | Blue/gray/red | Match your project palette |
| `point_size` | 0.8 (R) / 3 (py) | Increase for fewer points; decrease for dense data |

---

## Pitfalls

| Problem | Solution |
|---------|----------|
| **Labels overlap despite ggrepel** | Reduce `top_n_labels` to 10 or less; increase `max.iter` to 50000; increase `force` |
| **P-values of 0 break the y-axis** | Clip: `pmin(padj, 1e-300)` in R or `.clip(lower=1e-300)` in Python |
| **Too many significant genes, plot is a red blob** | Increase `fc_cutoff`; use alpha=0.3; or add density contours for non-significant |
| **Asymmetric x-axis** | Force symmetric: `xlim(c(-max_fc, max_fc))` |
| **Gene names not italic** | Use `fontface = "italic"` in ggrepel / `fontstyle="italic"` in matplotlib |

---

## Variants

### Variant A: Two-color minimal (up/down only, no gray)
Use when you want maximum contrast and only care about significant genes.
Change: set `alpha = 0` for ns group, or filter them out entirely.

### Variant B: Three-tier significance
Color by significance level (p < 0.05, p < 0.01, p < 1e-5) instead of binary.
Change: create 5 groups instead of 3, use a sequential palette within up/down.

### Variant C: Labeled with functional categories
Color or shape by gene category (e.g., transcription factors, kinases, receptors).
Change: add a `shape` or `fill` aesthetic; use `scale_shape_manual`.

### Variant D: Side-by-side comparison
Two volcano plots (e.g., two tissues, two timepoints) aligned on the same y-axis.
Use `patchwork` (R) or `subplots` (Python) with shared y-axis limits.
