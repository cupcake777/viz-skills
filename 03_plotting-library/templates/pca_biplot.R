#' PCA Biplot with Loading Arrows and Heatmap
#'
#' Produces a two-panel figure: (1) PCA score scatter with loading arrows
#' overlaid, and (2) a loading coefficient heatmap. Uses patchwork for layout.
#' Inspired by the glp1r-reward-circuit paper style.
#'
#' Input:
#'   df          - data.frame with PC scores + group column
#'   loading_df  - data.frame with feature loadings (long format)
#'   x_col       - name of x PC column (default "PC1")
#'   y_col       - name of y PC column (default "PC2")
#'   group_col   - name of grouping column
#'   feature_col - name of feature column in loading_df
#'   loading_x   - loading value column for x axis
#'   loading_y   - loading value column for y axis
#'
#' Returns: patchwork object (biplot / loading_heatmap)

# ── Source base_plot.R ──────────────────────────────────────────────────────────
tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))
suppressPackageStartupMessages({
  library(ggplot2)
  library(patchwork)
  library(scales)
})

# ── Mock data generator ─────────────────────────────────────────────────────────
generate_mock_data <- function(n = 60, n_groups = 3, n_features = 6, seed = 42) {
  set.seed(seed)
  groups <- rep(paste0("Group_", LETTERS[1:n_groups]), each = n / n_groups)

  # Simulate correlated feature matrix with group structure
  feat <- matrix(0, nrow = n, ncol = n_features)
  colnames(feat) <- paste0("Feature_", seq_len(n_features))
  # Group offsets to create separation
  offsets <- list(c(2, 1, -0.5, 0.3, -1, 0.8),
                  c(-1, 2, 1.5, -0.8, 0.5, -0.3),
                  c(-1.5, -1, 0.5, 1.2, 0.3, -0.6))
  for (g in seq_len(n_groups)) {
    idx <- which(as.integer(factor(groups)) == g)
    for (j in seq_len(n_features)) {
      feat[idx, j] <- rnorm(length(idx), mean = offsets[[g]][j], sd = 0.8)
    }
  }
  # Add correlated noise via random rotation
  rot <- matrix(rnorm(n_features^2), n_features, n_features)
  rot <- qr.Q(qr(rot))
  feat <- feat %*% rot
  # Preserve feature names lost by matrix multiplication
  colnames(feat) <- paste0("Feature_", seq_len(n_features))

  # Run PCA
  pca <- prcomp(feat, center = TRUE, scale. = TRUE)
  scores <- as.data.frame(pca$x[, 1:2])
  scores$group <- groups

  # Loadings (long format for heatmap)
  load_mat <- pca$rotation[, 1:2]
  loading_long <- expand.grid(
    feature = rownames(load_mat),
    component = colnames(load_mat),
    stringsAsFactors = FALSE
  )
  loading_long$loading <- as.vector(load_mat)

  # Also build arrow-style loading df
  loading_arrows <- data.frame(
    feature = rownames(load_mat),
    PC1 = load_mat[, 1],
    PC2 = load_mat[, 2],
    stringsAsFactors = FALSE
  )

  list(df = scores, loading_df = loading_arrows, loading_long = loading_long)
}

# ── Main plot function ──────────────────────────────────────────────────────────
pca_biplot_plot <- function(
    df,
    loading_df,
    loading_long = NULL,
    x_col = "PC1",
    y_col = "PC2",
    group_col = "group",
    feature_col = "feature",
    loading_x = "PC1",
    loading_y = "PC2",
    value_col = "loading",
    component_col = "component",
    explained_var = NULL,
    arrow_mult = NULL,
    base_size = 16,
    palette = VIZ_PALETTES$nature,
    arrow_colour = "grey30",
    arrow_linewidth = 0.6,
    point_alpha = 0.5,
    point_size = 2,
    mean_point_size = 4,
    mean_stroke = 1.2,
    heatmap_width_ratio = 0.4,
    ...
) {
  # ── Biplot panel ───────────────────────────────────────────────────────────
  # Auto-scale loading arrows to data range
  data_range_x <- range(df[[x_col]], na.rm = TRUE)
  data_range_y <- range(df[[y_col]], na.rm = TRUE)
  loading_range_x <- range(loading_df[[loading_x]], na.rm = TRUE)
  loading_range_y <- range(loading_df[[loading_y]], na.rm = TRUE)

  if (is.null(arrow_mult)) {
    data_span <- min(diff(data_range_x), diff(data_range_y))
    load_span  <- max(diff(loading_range_x), diff(loading_range_y))
    arrow_mult <- (data_span / load_span) * 0.4
  }

  # Axis labels with optional % variance
  xlab_text <- x_col
  ylab_text <- y_col
  if (!is.null(explained_var)) {
    xlab_text <- paste0(x_col, " (", sprintf("%.1f", explained_var[1] * 100), "%)")
    ylab_text <- paste0(y_col, " (", sprintf("%.1f", explained_var[2] * 100), "%)")
  }

  # Group means for mean markers
  means <- aggregate(
    cbind(df[[x_col]], df[[y_col]]) ~ df[[group_col]],
    FUN = mean
  )
  names(means) <- c(group_col, x_col, y_col)

  p_scatter <- ggplot(df, aes(.data[[x_col]], .data[[y_col]],
                              colour = .data[[group_col]], fill = .data[[group_col]])) +
    geom_point(size = point_size, alpha = point_alpha, shape = 16) +
    # Mean points
    geom_point(data = means, size = mean_point_size, shape = 21,
               stroke = mean_stroke, colour = "black") +
    # Loading arrows
    geom_segment(
      data = loading_df,
      aes(x = 0, y = 0, xend = .data[[loading_x]] * arrow_mult,
          yend = .data[[loading_y]] * arrow_mult),
      arrow = arrow(length = unit(0.15, "cm"), type = "closed"),
      linewidth = arrow_linewidth, colour = arrow_colour, inherit.aes = FALSE
    ) +
    # Feature labels at arrow tips
    geom_text(
      data = loading_df,
      aes(x = .data[[loading_x]] * arrow_mult * 1.08,
          y = .data[[loading_y]] * arrow_mult * 1.08,
          label = .data[[feature_col]]),
      size = base_size / ggplot2::.pt * 0.75, colour = arrow_colour,
      inherit.aes = FALSE, fontface = "italic"
    ) +
    geom_hline(yintercept = 0, linetype = "dashed", linewidth = 0.25, colour = "grey70") +
    geom_vline(xintercept = 0, linetype = "dashed", linewidth = 0.25, colour = "grey70") +
    scale_colour_manual(values = palette) +
    scale_fill_manual(values = palette) +
    labs(x = xlab_text, y = ylab_text) +
    theme_sci(base_size = base_size) +
    theme(legend.position = "top")

  # ── Loading heatmap panel ──────────────────────────────────────────────────
  if (!is.null(loading_long)) {
    # Order features by first component loading
    feat_order <- loading_df[order(loading_df[[loading_x]]), feature_col]
    loading_long[[feature_col]] <- factor(loading_long[[feature_col]],
                                          levels = rev(feat_order))

    p_heat <- ggplot(loading_long,
                     aes(.data[[component_col]], .data[[feature_col]],
                         fill = .data[[value_col]])) +
      geom_tile(colour = "white", linewidth = 0.3) +
      scale_fill_gradient2(
        low = "red", mid = "white", high = "blue",
        midpoint = 0, oob = scales::squish
      ) +
      labs(x = NULL, y = NULL, fill = "Loading") +
      coord_equal() +
      theme_sci(base_size = base_size) +
      theme(
        axis.text.x = element_text(angle = 45, hjust = 1),
        legend.position = "right"
      )

    # Combine with patchwork
    p_scatter + p_heat +
      plot_layout(widths = c(1 - heatmap_width_ratio, heatmap_width_ratio)) +
      plot_annotation(tag_levels = "a") &
      theme(plot.tag = element_text(face = "bold", size = base_size))
  } else {
    p_scatter
  }
}

# ── Demo / __main__ ─────────────────────────────────────────────────────────────
if (sys.nframe() == 0 || identical(environment(), globalenv())) {
  d <- generate_mock_data()

  # Compute explained variance
  mock <- generate_mock_data()
  explained <- summary(prcomp(
    matrix(rnorm(60 * 6), 60, 6), center = TRUE, scale. = TRUE
  ))$importance[2, 1:2]

  p <- pca_biplot_plot(
    df = d$df,
    loading_df = d$loading_df,
    loading_long = d$loading_long,
    x_col = "PC1",
    y_col = "PC2",
    group_col = "group",
    feature_col = "feature",
    loading_x = "PC1",
    loading_y = "PC2",
    value_col = "loading",
    component_col = "component",
    base_size = 16
  )

  save_demo(p, "pca_biplot_demo", width = 170, height = 85)
}
