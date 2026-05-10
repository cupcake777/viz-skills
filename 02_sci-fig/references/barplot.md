# Bar Plot

## When to Use
- **Data structure**: Counts, frequencies, or proportions across discrete categories
- **Analytical purpose**: Compare quantities or compositions across groups
- **ONLY for**: Counts, percentages, proportions, frequencies. The y-axis must represent a "how many" or "what fraction" question.
- **NOT for**: Continuous measurements like gene expression, protein levels, age, or any value where the distribution matters. Use violin/box plot instead.

> ⚠️ **The bar plot rule**: If your data has a meaningful distribution (variance, outliers, shape), a bar plot is hiding that information. Switch to violin + jitter.

## Minimal Example

### R
```r
ggplot(df, aes(x = category, y = count, fill = category)) +
  geom_col(width = 0.7) +
  theme_classic()
```

### Python
```python
ax.bar(df["category"], df["count"], width=0.7, color=colors)
```

---

## Full Recipe

### R (production-ready)
```r
library(ggplot2)

sci_barplot <- function(
  df,
  x_col,                    # categorical axis
  y_col,                    # numeric axis (counts/proportions)
  fill_col = NULL,          # optional: stacked or grouped fill
  colors = NULL,
  bar_type = "dodge",       # "dodge" (side-by-side), "stack", "fill" (proportional stack)
  show_values = FALSE,      # show count/pct on top of bars
  horizontal = FALSE,       # flip to horizontal (for long category names)
  order_by = "value",       # "value" (descending), "name" (alphabetical), "none"
  y_label = NULL,
  bar_width = 0.7,
  base_size = 16
) {

  data <- df

  # --- Ordering ---
  if (order_by == "value" && is.null(fill_col)) {
    data[[x_col]] <- reorder(data[[x_col]], -data[[y_col]])
  } else if (order_by == "name") {
    data[[x_col]] <- factor(data[[x_col]], levels = sort(unique(data[[x_col]])))
  }

  fill_var <- if (!is.null(fill_col)) fill_col else x_col

  # Default palette
  if (is.null(colors)) {
    n_grp <- length(unique(data[[fill_var]]))
    default_pal <- c("#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE", "#AA3377")
    colors <- setNames(default_pal[seq_len(n_grp)], unique(data[[fill_var]]))
  }

  p <- ggplot(data, aes(x = .data[[x_col]], y = .data[[y_col]], fill = .data[[fill_var]])) +
    geom_col(
      position = if (bar_type == "dodge") position_dodge(width = bar_width + 0.05)
                 else if (bar_type == "fill") "fill"
                 else "stack",
      width = bar_width,
      color = NA           # no bar borders (cleaner)
    ) +
    scale_fill_manual(values = colors)

  # --- Value labels on bars ---
  if (show_values) {
    if (bar_type == "dodge") {
      p <- p + geom_text(
        aes(label = .data[[y_col]]),
        position = position_dodge(width = bar_width + 0.05),
        vjust = -0.3,
        size = base_size / 3,
        color = "grey30"
      )
    }
  }

  # --- Proportional y-axis for stacked proportion ---
  if (bar_type == "fill") {
    p <- p + scale_y_continuous(labels = scales::percent_format())
  }

  # --- Axis ---
  p <- p +
    labs(
      x = NULL,
      y = if (!is.null(y_label)) y_label else y_col,
      fill = if (x_col == fill_var) NULL else fill_var
    ) +
    theme_classic(base_size = base_size) +
    theme(
      text = element_text(family = "Arial"),
      axis.text = element_text(color = "grey30"),
      legend.position = if (x_col == fill_var) "none" else "right",
      plot.margin = margin(5, 5, 5, 5, "pt")
    )

  # --- Horizontal flip ---
  if (horizontal) {
    p <- p + coord_flip()
  }

  # --- Y-axis starts at 0 ---
  if (bar_type != "fill") {
    p <- p + scale_y_continuous(expand = expansion(mult = c(0, 0.08)))
  }

  return(p)
}

# --- Usage ---
# Counts:
# p <- sci_barplot(df, "cell_type", "n_cells", y_label = "Number of cells")
#
# Stacked proportions:
# p <- sci_barplot(df, "sample", "fraction", fill_col = "cell_type", bar_type = "fill")
#
# Horizontal (long labels):
# p <- sci_barplot(df, "pathway", "gene_count", horizontal = TRUE, order_by = "value")
```

### Python (production-ready)
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def sci_barplot(
    df, x_col, y_col,
    fill_col=None,
    colors=None,
    bar_type="dodge",         # "dodge", "stack", "fill"
    show_values=False,
    horizontal=False,
    order_by="value",         # "value", "name", "none"
    y_label=None,
    bar_width=0.7,
    figsize=(3.35, 2.76), dpi=300, font_size=7
):
    data = df.copy()

    if colors is None:
        colors = ["#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE", "#AA3377"]

    # Ordering
    if order_by == "value" and fill_col is None:
        data = data.sort_values(y_col, ascending=False)
    elif order_by == "name":
        data = data.sort_values(x_col)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    if fill_col is None:
        # Simple bar
        n = len(data)
        c = colors[:n] if n <= len(colors) else colors * (n // len(colors) + 1)
        bar_fn = ax.barh if horizontal else ax.bar
        bars = bar_fn(data[x_col], data[y_col], width=bar_width if not horizontal else None,
                      height=bar_width if horizontal else None, color=c[:n])

        if show_values:
            for bar, val in zip(bars, data[y_col]):
                if horizontal:
                    ax.text(val, bar.get_y() + bar.get_height()/2,
                            f" {val}", va="center", fontsize=font_size - 1)
                else:
                    ax.text(bar.get_x() + bar.get_width()/2, val,
                            f"{val}", ha="center", va="bottom", fontsize=font_size - 1)
    else:
        # Grouped or stacked
        groups = data[x_col].unique()
        fills = data[fill_col].unique()
        palette = dict(zip(fills, colors[:len(fills)]))
        x_pos = np.arange(len(groups))

        if bar_type == "dodge":
            n_fills = len(fills)
            width = bar_width / n_fills
            for i, fill_val in enumerate(fills):
                sub = data[data[fill_col] == fill_val].set_index(x_col).reindex(groups)
                offset = (i - n_fills / 2 + 0.5) * width
                ax.bar(x_pos + offset, sub[y_col].fillna(0),
                       width=width, label=fill_val, color=palette[fill_val])
        elif bar_type in ("stack", "fill"):
            bottom = np.zeros(len(groups))
            totals = data.groupby(x_col)[y_col].sum().reindex(groups).values if bar_type == "fill" else None
            for fill_val in fills:
                sub = data[data[fill_col] == fill_val].set_index(x_col).reindex(groups)
                vals = sub[y_col].fillna(0).values
                if bar_type == "fill":
                    vals = vals / totals
                ax.bar(x_pos, vals, width=bar_width, bottom=bottom,
                       label=fill_val, color=palette[fill_val])
                bottom += vals

        ax.set_xticks(x_pos)
        ax.set_xticklabels(groups, rotation=0 if max(len(str(g)) for g in groups) < 6 else 45,
                           ha="right" if max(len(str(g)) for g in groups) >= 6 else "center")
        ax.legend(fontsize=font_size - 1, frameon=False)

    # Axis
    if horizontal:
        ax.set_xlabel(y_label or y_col, fontsize=font_size)
        ax.set_ylabel("", fontsize=font_size)
    else:
        ax.set_xlabel("", fontsize=font_size)
        ax.set_ylabel(y_label or y_col, fontsize=font_size)

    if bar_type == "fill":
        ax.set_ylabel("Proportion", fontsize=font_size)
        from matplotlib.ticker import PercentFormatter
        ax.yaxis.set_major_formatter(PercentFormatter(1.0))

    ax.tick_params(labelsize=font_size - 1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Y starts at 0
    if not horizontal and bar_type != "fill":
        ax.set_ylim(bottom=0)

    plt.tight_layout()
    return fig, ax
```

---

## Parameters to Tune

| Parameter | Default | When to change |
|-----------|---------|---------------|
| `bar_type` | "dodge" | "stack" for composition; "fill" for proportional composition |
| `horizontal` | FALSE | TRUE when category names are long (pathways, GO terms) |
| `order_by` | "value" | "name" for ordered categories (chromosomes, time points); "none" for custom order |
| `show_values` | FALSE | TRUE for small datasets where exact numbers matter |
| `bar_width` | 0.7 | Narrower (0.5) for many categories; wider (0.85) for few |

---

## Pitfalls

| Problem | Solution |
|---------|----------|
| **Y-axis doesn't start at 0** | Always start at 0 for bar plots — truncating exaggerates differences |
| **Too many categories (>15)** | Switch to horizontal; or group into "Other"; or use dot/lollipop plot |
| **Using bar + error bar for continuous data** | **Stop.** Use violin + jitter instead. This is the #1 misuse of bar plots. |
| **Stacked bars hard to compare** | Non-baseline segments are hard to compare. Consider dodge or faceting |
| **Color has no meaning** | If all bars are the same group, use a single color. Don't rainbow for no reason. |

---

## Variants

### Variant A: Lollipop chart
Cleaner alternative to bar for ranking:
```r
ggplot(df, aes(x = reorder(category, value), y = value)) +
  geom_segment(aes(xend = category, y = 0, yend = value), color = "grey60", linewidth = 0.4) +
  geom_point(size = 2.5, color = "#4477AA") +
  coord_flip() + theme_classic()
```

### Variant B: Percent stacked (cell type composition)
Show cell type proportions per sample:
```r
sci_barplot(df, "sample", "fraction", fill_col = "cell_type", bar_type = "fill")
```

### Variant C: Diverging bar (up/down regulation counts)
Center at 0, bars go left/right:
```r
ggplot(df, aes(x = tissue, y = n_degs, fill = direction)) +
  geom_col(position = "identity") +   # not stacked
  coord_flip()
```
