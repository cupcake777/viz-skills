#' Density Scatter Plot
#'
#' Large-dataset scatter with density-based coloring to handle overplotting.
#' Adaptive point sizing and percentile-based color clipping. Inspired by
#' UMAP paper visualization (McInnes et al., 2018) and datashader approach.
#'
#' Required columns: x, y
#' Optional columns: group

suppressPackageStartupMessages({
  library(ggplot2)
  library(MASS)
})

tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R")))

generate_mock_data <- function(n = 5000, n_clusters = 4, seed = 42) {
  set.seed(seed)

  centers_x <- c(-3, 3, -2, 2)
  centers_y <- c(-2, -2, 2, 3)
  sizes <- c(0.8, 0.7, 0.6, 0.9)

  dfs <- list()
  for (i in seq_len(n_clusters)) {
    n_i <- round(n / n_clusters)
    dfs[[i]] <- data.frame(
      x = rnorm(n_i, centers_x[i], sizes[i]),
      y = rnorm(n_i, centers_y[i], sizes[i]),
      group = paste0("Cluster_", LETTERS[i]),
      stringsAsFactors = FALSE
    )
  }

  do.call(rbind, dfs)
}

plot_density_scatter <- function(df,
                                 x = "x", y = "y",
                                 group = NULL,
                                 point_size = NULL,
                                 alpha = 0.5,
                                 palette = "viridis",
                                 clip_percentile = 2,
                                 base_size = 14) {

  # Adaptive point sizing: 100 / sqrt(n)
  if (is.null(point_size)) {
    point_size <- max(0.3, 100 / sqrt(nrow(df)) * 0.05)
  }

  # Compute 2D density
  kde <- kde2d(df[[x]], df[[y]], n = 200)
  df$density <- approx(
    x = as.vector(kde$x[kde$x <= max(df[[x]]) & kde$x >= min(df[[x]])]),
    y = as.vector(kde$z),
    xout = df[[x]],
    rule = 2
  )$y

  # Actually do proper 2D interpolation
  library(akima)
  kde_df <- expand.grid(x = kde$x, y = kde$y)
  kde_df$z <- as.vector(kde$z)
  df$density <- interp2xyz(interp(kde_df$x, kde_df$y, kde_df$z,
                                   xo = df[[x]], yo = df[[y]]), data.frame = TRUE)$z

  # Percentile clipping
  lo <- quantile(df$density, clip_percentile / 100, na.rm = TRUE)
  hi <- quantile(df$density, 1 - clip_percentile / 100, na.rm = TRUE)
  df$density <- pmax(pmin(df$density, hi), lo)

  p <- ggplot(df, aes(x = .data[[x]], y = .data[[y]], color = density)) +
    geom_point(size = point_size, alpha = alpha) +
    scale_color_viridis_c(option = "D", name = "Density") +
    theme_sci(base_size = base_size) +
    labs(x = "Dimension 1", y = "Dimension 2")

  p
}

# Simpler version without akima dependency
plot_density_scatter_simple <- function(df,
                                        x = "x", y = "y",
                                        group = NULL,
                                        point_size = NULL,
                                        alpha = 0.5,
                                        palette = "viridis",
                                        base_size = 14) {

  if (is.null(point_size)) {
    point_size <- max(0.3, 100 / sqrt(nrow(df)) * 0.05)
  }

  if (!is.null(group) && group %in% names(df)) {
    p <- ggplot(df, aes(x = .data[[x]], y = .data[[y]], color = .data[[group]])) +
      geom_point(size = point_size, alpha = alpha) +
      scale_color_manual(values = NATURE_COLORS, name = NULL) +
      guides(color = guide_legend(override.aes = list(size = 2, alpha = 1)))
  } else {
    p <- ggplot(df, aes(x = .data[[x]], y = .data[[y]])) +
      geom_point(size = point_size, alpha = alpha, color = "#3C5488") +
      stat_density_2d(aes(fill = after_stat(level)), geom = "polygon",
                      alpha = 0.15, color = NA, n = 100) +
      scale_fill_viridis_c(name = "Density", option = "D")
  }

  p + theme_sci(base_size = base_size) +
    labs(x = "Dimension 1", y = "Dimension 2")
}

# Demo ----
if (sys.nframe() == 0 || isTRUE(getOption("run_demo"))) {
  df <- generate_mock_data()
  p <- plot_density_scatter_simple(df)

  out <- template_out_dir()
  save_demo(p, name = "density_scatter_demo", out_dir = out,
            width = 150, height = 120, units = "mm", dpi = 300)
  message("Demo saved to ", file.path(out, "density_scatter_demo.png"))
}
