# Scatter Plot

## When to Use
- **Data structure**: Two continuous variables per observation, optionally with group labels
- **Analytical purpose**: Show correlation, relationship, or agreement between two measurements
- **NOT for**: Time series with natural ordering (use line plot), categorical comparisons (use box/violin)

## Minimal Example

### R
```r
ggplot(df, aes(x = var1, y = var2)) +
  geom_point(size = 1, alpha = 0.6) +
  geom_smooth(method = "lm", se = TRUE, color = "#E64B35", linewidth = 0.5) +
  theme_classic()
```

### Python
```python
plt.scatter(df["var1"], df["var2"], s=5, alpha=0.6, edgecolors="none")
```

---

## Full Recipe

### R (production-ready)
```r
library(ggplot2)
library(ggrepel)

sci_scatter <- function(
  df,
  x_col,
  y_col,
  color_col = NULL,          # optional: color by group
  label_col = NULL,          # optional: label specific points
  label_filter = NULL,       # logical vector or function to select labeled points
  top_n_labels = 10,
  colors = NULL,
  trend = "lm",              # "lm", "loess", or NULL
  show_cor = TRUE,           # show Pearson r on plot
  density_contour = FALSE,   # add density contours for large n
  x_label = NULL,
  y_label = NULL,
  point_size = 1,
  alpha = 0.6,
  base_size = 16
) {

  p <- ggplot(df, aes(x = .data[[x_col]], y = .data[[y_col]]))

  # --- Density handling for large datasets ---
  n <- nrow(df)
  if (n > 5000 && !density_contour) {
    # Auto-switch to hex bin for very large datasets
    p <- p + geom_hex(bins = 60) +
      scale_fill_viridis_c(option = "mako", name = "Count")
  } else if (density_contour) {
    p <- p +
      geom_point(size = point_size * 0.5, alpha = 0.1, color = "grey50") +
      geom_density_2d(color = "#4477AA", linewidth = 0.3)
  } else {
    # Standard scatter
    if (!is.null(color_col)) {
      p <- p + geom_point(aes(color = .data[[color_col]]),
                          size = point_size, alpha = alpha)
      if (is.null(colors)) {
        colors <- c("#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE", "#AA3377")
        n_grp <- length(unique(df[[color_col]]))
        colors <- setNames(colors[seq_len(n_grp)], unique(df[[color_col]]))
      }
      p <- p + scale_color_manual(values = colors)
    } else {
      p <- p + geom_point(size = point_size, alpha = alpha, color = "#4477AA")
    }
  }

  # --- Trend line ---
  if (!is.null(trend)) {
    p <- p + geom_smooth(
      method = trend,
      se = (trend == "lm"),
      color = "#E64B35",
      linewidth = 0.5,
      fill = "#E64B35",
      alpha = 0.15
    )
  }

  # --- Correlation annotation ---
  if (show_cor) {
    cor_test <- cor.test(df[[x_col]], df[[y_col]], method = "pearson")
    r_val <- round(cor_test$estimate, 3)
    p_val <- cor_test$p.value
    p_label <- ifelse(p_val < 2.2e-16, "< 2.2e-16", formatC(p_val, format = "e", digits = 1))

    p <- p + annotate(
      "text",
      x = min(df[[x_col]], na.rm = TRUE),
      y = max(df[[y_col]], na.rm = TRUE),
      label = paste0("r = ", r_val, "\np ", p_label),
      hjust = 0, vjust = 1,
      size = base_size / 2.8,
      color = "grey30",
      fontface = "italic"
    )
  }

  # --- Labels ---
  if (!is.null(label_col)) {
    if (!is.null(label_filter)) {
      to_label <- df[label_filter, ]
    } else {
      # Default: label points furthest from trend
      if (!is.null(trend) && trend == "lm") {
        fit <- lm(as.formula(paste(y_col, "~", x_col)), data = df)
        df$.resid <- abs(residuals(fit))
        to_label <- head(df[order(-df$.resid), ], top_n_labels)
      } else {
        to_label <- head(df, top_n_labels)
      }
    }

    p <- p + geom_text_repel(
      data = to_label,
      aes(label = .data[[label_col]]),
      size = base_size / 3,
      fontface = "italic",
      max.overlaps = 20,
      min.segment.length = 0,
      segment.size = 0.25,
      segment.color = "grey50"
    )
  }

  # --- Axis labels ---
  p <- p +
    labs(
      x = if (!is.null(x_label)) x_label else x_col,
      y = if (!is.null(y_label)) y_label else y_col
    ) +
    theme_classic(base_size = base_size) +
    theme(
      text = element_text(family = "Arial"),
      axis.text = element_text(color = "grey30"),
      plot.margin = margin(5, 5, 5, 5, "pt")
    )

  return(p)
}

# --- Usage ---
# p <- sci_scatter(df, "eQTL_beta_prenatal", "eQTL_beta_postnatal",
#                  color_col = "flip_status", label_col = "gene",
#                  x_label = "Effect size (prenatal)", y_label = "Effect size (postnatal)")
```

### Python (production-ready)
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from adjustText import adjust_text

def sci_scatter(
    df, x_col, y_col,
    color_col=None, label_col=None,
    top_n_labels=10,
    colors=None,
    trend="lm",
    show_cor=True,
    x_label=None, y_label=None,
    point_size=5, alpha=0.6,
    figsize=(3.35, 3.15), dpi=300, font_size=7
):
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    x, y = df[x_col].values, df[y_col].values

    # --- Large dataset handling ---
    if len(df) > 5000 and color_col is None:
        hb = ax.hexbin(x, y, gridsize=50, cmap="mako", mincnt=1)
        fig.colorbar(hb, ax=ax, label="Count", shrink=0.6)
    else:
        if color_col:
            if colors is None:
                pal = ["#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE", "#AA3377"]
                groups = df[color_col].unique()
                colors = dict(zip(groups, pal[:len(groups)]))
            for grp, grp_df in df.groupby(color_col):
                ax.scatter(grp_df[x_col], grp_df[y_col],
                          s=point_size, alpha=alpha, label=grp,
                          color=colors.get(grp, "#4477AA"), edgecolors="none")
            ax.legend(fontsize=font_size - 1, frameon=False)
        else:
            ax.scatter(x, y, s=point_size, alpha=alpha,
                      color="#4477AA", edgecolors="none")

    # --- Trend line ---
    if trend == "lm":
        mask = np.isfinite(x) & np.isfinite(y)
        slope, intercept, _, _, _ = stats.linregress(x[mask], y[mask])
        x_line = np.linspace(np.nanmin(x), np.nanmax(x), 100)
        ax.plot(x_line, slope * x_line + intercept,
                color="#E64B35", linewidth=0.8, zorder=3)

    # --- Correlation ---
    if show_cor:
        mask = np.isfinite(x) & np.isfinite(y)
        r, p_val = stats.pearsonr(x[mask], y[mask])
        p_str = f"< 2.2e-16" if p_val < 2.2e-16 else f"= {p_val:.1e}"
        ax.text(0.05, 0.95, f"r = {r:.3f}\np {p_str}",
                transform=ax.transAxes, fontsize=font_size - 1,
                va="top", ha="left", fontstyle="italic", color="grey30")

    # --- Labels ---
    if label_col:
        if trend == "lm":
            mask = np.isfinite(x) & np.isfinite(y)
            residuals = np.abs(y - (slope * x + intercept))
            residuals[~mask] = 0
            top_idx = np.argsort(residuals)[-top_n_labels:]
        else:
            top_idx = range(min(top_n_labels, len(df)))

        texts = []
        for idx in top_idx:
            row = df.iloc[idx]
            texts.append(ax.text(
                row[x_col], row[y_col], row[label_col],
                fontsize=font_size - 1, fontstyle="italic"
            ))
        if texts:
            adjust_text(texts, ax=ax,
                       arrowprops=dict(arrowstyle="-", color="grey", lw=0.4))

    ax.set_xlabel(x_label or x_col, fontsize=font_size)
    ax.set_ylabel(y_label or y_col, fontsize=font_size)
    ax.tick_params(labelsize=font_size - 1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    return fig, ax
```

---

## Parameters to Tune

| Parameter | Default | When to change |
|-----------|---------|---------------|
| `trend` | "lm" | Use "loess" for non-linear relationships; NULL if no trend expected |
| `density_contour` | FALSE | TRUE for n > 2000 where individual points are less meaningful |
| `top_n_labels` | 10 | 0 to disable; increase if figure has room |
| `alpha` | 0.6 | Lower to 0.1–0.2 for dense data; 0.8+ for sparse data |

---

## Pitfalls

| Problem | Solution |
|---------|----------|
| **Over-plotting (dense blob)** | Use hex bin, lower alpha, or 2D density contours |
| **Outlier stretches axes** | Clip axes with `xlim/ylim`; note "N outliers excluded" |
| **Correlation r is misleading** | Check for non-linearity (use loess), subgroups (color by group), or outliers driving r |
| **Diagonal reference line needed** (e.g., comparing two methods) | Add `geom_abline(slope=1, intercept=0, linetype="dashed")` |

---

## Variants

### Variant A: MA plot (log expression vs. fold change)
Standard for differential expression: x = average expression, y = log2FC.
Same scatter recipe, different axis semantics.

### Variant B: Effect size comparison across conditions
e.g., prenatal vs. postnatal eQTL betas. Add diagonal + color for flip status.

### Variant C: Bland-Altman / agreement plot
x = mean of two measurements, y = difference. For method comparison studies.

### Variant D: Marginal density scatter
Add density histograms on the margins:
```r
library(ggExtra)
p <- sci_scatter(df, "x", "y")
ggMarginal(p, type = "density", fill = "#4477AA", alpha = 0.3)
```
