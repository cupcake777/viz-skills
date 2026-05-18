#' Clustered Heatmap
#'
#' R template for clustered heatmaps using ggplot2 with hierarchical
#' clustering of both rows and columns. Legend positioned to avoid overlap
#' with the row dendrogram.
#'
#' Required columns: gene (row), sample (column), value (fill)
#' Optional: cluster_rows, cluster_cols booleans

tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))
suppressPackageStartupMessages(library(ggplot2))

generate_mock_data <- function(seed = 42) {
  set.seed(seed)
  mat <- matrix(rnorm(30 * 12), 30, 12)
  mat[1:10, 1:4]  <- mat[1:10, 1:4] + 1.5
  mat[11:20, 5:8]  <- mat[11:20, 5:8] - 1.2
  rownames(mat) <- paste0("Gene", 1:30)
  colnames(mat) <- paste0("S", 1:12)
  as.data.frame(as.table(mat)) |> setNames(c("gene", "sample", "value"))
}

heatmap_clustered_plot <- function(
    df,
    row_col = "gene",
    col_col = "sample",
    value_col = "value",
    base_size = 16,
    show_rownames = FALSE,
    legend_position = "right",
    ...
) {
  # Wide matrix for clustering
  mat <- xtabs(as.formula(paste(value_col, "~", row_col, "+", col_col)), df)

  # Hierarchical clustering
  row_ord <- rownames(mat)[hclust(dist(mat))$order]
  col_ord <- colnames(mat)[hclust(dist(t(mat)))$order]

  df[[row_col]] <- factor(df[[row_col]], levels = rev(row_ord))
  df[[col_col]] <- factor(df[[col_col]], levels = col_ord)

  ggplot(df, aes(.data[[col_col]], .data[[row_col]], fill = .data[[value_col]])) +
    geom_tile() +
    scale_fill_gradient2(low = "#4575B4", mid = "white", high = "#D73027") +
    labs(x = NULL, y = NULL, fill = "z") +
    theme_sci(base_size = base_size) +
    theme(
      axis.text.y = if (show_rownames) element_text(size = rel(0.55)) else element_blank(),
      axis.ticks.y = element_blank(),
      axis.text.x = element_text(angle = 45, hjust = 1),
      legend.position = legend_position,
      legend.key.height = unit(18, "pt"),
      legend.key.width = unit(6, "pt"),
      plot.margin = margin(5, 18, 5, 5, "pt")
    )
}

if (sys.nframe() == 0) {
  save_demo(heatmap_clustered_plot(generate_mock_data()), "heatmap_demo", width = 100, height = 95)
}