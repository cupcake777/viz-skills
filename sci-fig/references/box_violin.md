# Box & Violin Plot

## When to Use
- **Data structure**: Continuous variable measured across 2+ groups (e.g., expression by tissue, age by condition)
- **Analytical purpose**: Compare distributions between groups — show median, spread, shape, and outliers
- **NOT for**: Counts or proportions (use bar plot), relationships between two continuous variables (use scatter)

**Why not bar + error bar?** Bar plots hide the distribution shape. You can't see bimodality, skewness, or outliers. Violin + jitter shows everything.

## Minimal Example

### R
```r
library(ggplot2)

ggplot(df, aes(x = group, y = expression, fill = group)) +
  geom_violin(alpha = 0.6) +
  geom_boxplot(width = 0.15, outlier.shape = NA) +
  geom_jitter(width = 0.1, size = 0.5, alpha = 0.3) +
  theme_classic()
```

### Python
```python
import seaborn as sns

fig, ax = plt.subplots()
sns.violinplot(data=df, x="group", y="expression", inner=None, alpha=0.6, ax=ax)
sns.boxplot(data=df, x="group", y="expression", width=0.15,
            showcaps=False, boxprops=dict(alpha=0.8), ax=ax)
sns.stripplot(data=df, x="group", y="expression", size=1.5, alpha=0.3, ax=ax)
```

---

## Full Recipe

### R (production-ready)
```r
library(ggplot2)
library(ggbeeswarm)    # for better jitter than geom_jitter

sci_boxviolin <- function(
  df,
  x_col,                   # categorical grouping column
  y_col,                   # continuous value column
  fill_col = NULL,         # optional: different fill from x (for nested groups)
  colors = NULL,           # named vector of colors per group; NULL = project palette
  comparisons = NULL,      # list of pairs for stat comparisons, e.g. list(c("A","B"))
  method = "violin+box",   # "violin+box", "violin", "box", "box+jitter"
  show_points = TRUE,
  point_size = 0.6,
  alpha_violin = 0.6,
  alpha_points = 0.3,
  y_label = NULL,
  base_size = 7
) {

  fill_var <- if (!is.null(fill_col)) fill_col else x_col

  # Default project palette
  if (is.null(colors)) {
    n_groups <- length(unique(df[[fill_var]]))
    default_pal <- c("#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE", "#AA3377")
    colors <- setNames(default_pal[seq_len(n_groups)], unique(df[[fill_var]]))
  }

  p <- ggplot(df, aes(x = .data[[x_col]], y = .data[[y_col]], fill = .data[[fill_var]]))

  # --- Violin layer ---
  if (grepl("violin", method)) {
    p <- p + geom_violin(
      alpha = alpha_violin,
      color = NA,               # no outline on violin
      scale = "width",          # all violins same max width
      trim = TRUE
    )
  }

  # --- Box layer ---
  if (grepl("box", method)) {
    p <- p + geom_boxplot(
      width = if (grepl("violin", method)) 0.15 else 0.6,
      outlier.shape = NA,       # outliers shown by jitter instead
      color = "grey30",
      fill = if (grepl("violin", method)) "white" else NA,
      alpha = if (grepl("violin", method)) 0.8 else alpha_violin,
      linewidth = 0.3
    )
  }

  # --- Points layer ---
  if (show_points) {
    if (nrow(df) > 500) {
      # Many points: use smaller size, more transparency
      p <- p + geom_jitter(
        width = 0.1, size = point_size * 0.5,
        alpha = alpha_points * 0.5, color = "grey30", show.legend = FALSE
      )
    } else {
      # Fewer points: beeswarm for better separation
      p <- p + geom_quasirandom(
        size = point_size, alpha = alpha_points,
        color = "grey30", bandwidth = 0.8, show.legend = FALSE
      )
    }
  }

  # --- Statistical comparisons ---
  if (!is.null(comparisons)) {
    library(ggpubr)
    p <- p + stat_compare_means(
      comparisons = comparisons,
      method = "wilcox.test",
      label = "p.signif",       # *, **, ***, ns
      size = base_size / 2.5,
      tip.length = 0.01,
      step.increase = 0.08
    )
  }

  # --- Styling ---
  p <- p +
    scale_fill_manual(values = colors) +
    labs(
      x = NULL,
      y = if (!is.null(y_label)) y_label else y_col,
      fill = NULL
    ) +
    theme_classic(base_size = base_size) +
    theme(
      text = element_text(family = "Arial"),
      axis.text = element_text(color = "grey30"),
      axis.text.x = element_text(angle = 0),     # rotate if needed
      legend.position = if (x_col == fill_var) "none" else "right",
      plot.margin = margin(5, 5, 5, 5, "pt")
    )

  return(p)
}

# --- Usage ---
# p <- sci_boxviolin(df, x_col = "tissue", y_col = "expression",
#                    comparisons = list(c("Brain", "Liver")),
#                    y_label = "Expression (TPM)")
# ggsave("violin_pub.pdf", p, width = 85, height = 70, units = "mm", dpi = 300)
```

### Python (production-ready)
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def sci_boxviolin(
    df,
    x_col,
    y_col,
    hue_col=None,
    colors=None,
    method="violin+box",       # "violin+box", "violin", "box", "box+strip"
    show_points=True,
    comparisons=None,          # list of tuples, e.g. [("A","B")]
    y_label=None,
    figsize=(3.35, 2.76),
    dpi=300,
    font_size=7
):
    if colors is None:
        colors = ["#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE", "#AA3377"]

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    hue = hue_col if hue_col else x_col
    palette = dict(zip(df[hue].unique(), colors[:df[hue].nunique()]))

    # Violin
    if "violin" in method:
        sns.violinplot(
            data=df, x=x_col, y=y_col, hue=hue,
            inner=None, alpha=0.6, palette=palette,
            linewidth=0, scale="width", ax=ax, legend=False
        )

    # Box
    if "box" in method:
        box_width = 0.15 if "violin" in method else 0.6
        sns.boxplot(
            data=df, x=x_col, y=y_col, hue=hue,
            width=box_width, showcaps=False, whiskerprops=dict(linewidth=0.5),
            medianprops=dict(color="grey30", linewidth=1),
            boxprops=dict(facecolor="white" if "violin" in method else None,
                         edgecolor="grey30", linewidth=0.5),
            fliersize=0, ax=ax, legend=False
        )

    # Points
    if show_points:
        sns.stripplot(
            data=df, x=x_col, y=y_col, hue=hue,
            size=1.5 if len(df) > 500 else 2.5,
            alpha=0.15 if len(df) > 500 else 0.3,
            jitter=0.1, color="grey30", ax=ax, legend=False
        )

    # Statistical comparisons
    if comparisons:
        y_max = df[y_col].max()
        y_step = (df[y_col].max() - df[y_col].min()) * 0.08
        groups = df[x_col].unique().tolist()

        for i, (g1, g2) in enumerate(comparisons):
            d1 = df[df[x_col] == g1][y_col]
            d2 = df[df[x_col] == g2][y_col]
            _, p_val = stats.mannwhitneyu(d1, d2, alternative="two-sided")

            # Significance stars
            stars = "ns"
            if p_val < 0.001: stars = "***"
            elif p_val < 0.01: stars = "**"
            elif p_val < 0.05: stars = "*"

            x1, x2 = groups.index(g1), groups.index(g2)
            y_bar = y_max + y_step * (i + 1)
            ax.plot([x1, x1, x2, x2], [y_bar - y_step*0.2, y_bar, y_bar, y_bar - y_step*0.2],
                    lw=0.5, color="grey30")
            ax.text((x1 + x2) / 2, y_bar, stars,
                    ha="center", va="bottom", fontsize=font_size - 1)

    # Labels
    ax.set_xlabel("")
    ax.set_ylabel(y_label if y_label else y_col, fontsize=font_size)
    ax.tick_params(axis="both", labelsize=font_size - 1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    return fig, ax

# --- Usage ---
# fig, ax = sci_boxviolin(df, "tissue", "expression",
#                         comparisons=[("Brain", "Liver")],
#                         y_label="Expression (TPM)")
# fig.savefig("violin_pub.pdf", dpi=300, bbox_inches="tight")
```

---

## Parameters to Tune

| Parameter | Default | When to change |
|-----------|---------|---------------|
| `method` | "violin+box" | Use "box+jitter" for <30 samples per group; "violin" only if box adds clutter |
| `show_points` | TRUE | FALSE if n > 2000 per group (too dense) |
| `comparisons` | NULL | Add statistical comparison brackets between specific groups |
| `alpha_violin` | 0.6 | Lower to 0.3 if overlapping with nested groups |

---

## Pitfalls

| Problem | Solution |
|---------|----------|
| **Violin looks "flat" with few data points** | Switch to `method = "box+jitter"` for n < 30 |
| **X-axis labels overlap** | Rotate 45°: `axis.text.x = element_text(angle = 45, hjust = 1)` |
| **Jitter points escape the violin boundary** | Reduce `width` in geom_jitter; or use `geom_quasirandom` |
| **Too many groups (>8) on one axis** | Facet by a higher-level category instead |
| **Comparison brackets overlap** | Reduce number of comparisons; show only key contrasts |

---

## Variants

### Variant A: Paired data (before/after)
Connect matched samples with lines:
```r
ggplot(df, aes(x = condition, y = value)) +
  geom_violin(alpha = 0.4) +
  geom_point(size = 1, alpha = 0.5) +
  geom_line(aes(group = patient_id), alpha = 0.2, color = "grey40")
```

### Variant B: Half-violin (raincloud plot)
Shows distribution on one side, points on the other. Elegant for small-to-medium n.
Use `gghalves::geom_half_violin()` (R) or `PtitPrince` (Python).

### Variant C: Faceted by tissue/region
One panel per tissue, comparing conditions within each:
```r
p + facet_wrap(~ tissue, scales = "free_y", nrow = 1)
```

### Variant D: Nested groups (grouped violin)
Two categorical variables (e.g., tissue + condition). Use `fill_col` different from `x_col`:
```r
sci_boxviolin(df, x_col = "tissue", y_col = "expr", fill_col = "condition")
```
