#' Feature Plot (Gene Expression on 2D Embedding)
#'
#' Overlay continuous gene expression values on a 2D embedding (UMAP, tSNE, etc.).
#' Points are colored by expression intensity using the viridis color scale.
#' Optionally faceted by a group/cluster label for side-by-side comparison.
#' Common in single-cell transcriptomics workflows (e.g., Seurat, Scanpy).
#'
#' Required columns: dim1, dim2, expression
#' Optional columns: group_label (for faceting), cell_id
#'
#' @seealso Seurat::FeaturePlot, scanpy.pl.umap(color=...)

suppressPackageStartupMessages({
  library(ggplot2)
})

tryCatch(tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))),
         error = function(e) tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R")))

generate_mock_data <- function(n_cells = 600, n_clusters = 5, seed = 42) {
  set.seed(seed)

  # Generate 5 cluster centers scattered in embedding space
  centers <- data.frame(
    x = c(-4, 3, -2, 5, 1),
    y = c(3, 4, -3, -2, 0)
  )

  cells_per_cluster <- n_cells / n_clusters
  cluster_ids <- rep(paste0("Cluster_", seq_len(n_clusters)), each = cells_per_cluster)

  # Generate cell coordinates with Gaussian scatter around centers
  dim1 <- numeric(n_cells)
  dim2 <- numeric(n_cells)
  for (i in seq_len(n_clusters)) {
    idx <- ((i - 1) * cells_per_cluster + 1):(i * cells_per_cluster)
    dim1[idx] <- rnorm(cells_per_cluster, centers$x[i], 0.8)
    dim2[idx] <- rnorm(cells_per_cluster, centers$y[i], 0.8)
  }

  # Simulate expression: high in one or two clusters, low elsewhere
  expression <- runif(n_cells, 0, 0.3)
  # Cluster 2 and 4 express the gene highly
  highlight <- cluster_ids %in% c("Cluster_2", "Cluster_4")
  expression[highlight] <- expression[highlight] + runif(sum(highlight), 0.5, 1.7)
  # Add some gradient within cluster 1
  in_c1 <- cluster_ids == "Cluster_1"
  expression[in_c1] <- expression[in_c1] + abs(dim2[in_c1]) * 0.15

  data.frame(
    cell_id = paste0("cell_", seq_len(n_cells)),
    dim1 = dim1,
    dim2 = dim2,
    expression = pmax(expression, 0),
    group_label = cluster_ids,
    stringsAsFactors = FALSE
  )
}

plot_feature <- function(df,
                         dim1 = "dim1",
                         dim2 = "dim2",
                         expr_col = "expression",
                         group_col = NULL,
                         point_size = 0.6,
                         alpha = 0.8,
                         base_size = 14) {

  p <- ggplot(df, aes(
    x = .data[[dim1]],
    y = .data[[dim2]],
    color = .data[[expr_col]]
  )) +
    geom_point(size = point_size, alpha = alpha) +
    scale_color_viridis_c(
      option = "D",
      name = "Expression",
      guide = guide_colorbar(
        barwidth = unit(6, "pt"),
        barheight = unit(36, "pt"),
        title.position = "top",
        title.hjust = 0.5
      )
    ) +
    theme_sci(base_size = base_size) +
    theme(
      axis.text = element_blank(),
      axis.ticks = element_blank(),
      axis.title = element_text(size = rel(0.85), colour = "grey40"),
      panel.border = element_rect(colour = "grey70", fill = NA, size = 0.3),
      plot.margin = margin(5, 5, 5, 5, "pt"),
      strip.background = element_rect(fill = "grey95", colour = "grey70", size = 0.3),
      strip.text = element_text(size = rel(0.8))
    ) +
    labs(x = "UMAP_1", y = "UMAP_2")

  # Optional faceting by group column
  if (!is.null(group_col) && group_col %in% names(df)) {
    p <- p + facet_wrap(
      as.formula(paste("~", group_col)),
      ncol = ceiling(sqrt(length(unique(df[[group_col]]))))
    )
  }

  p
}

# Demo ----
if (sys.nframe() == 0 || isTRUE(getOption("run_demo"))) {
  df <- generate_mock_data()

  # Panel A: full embedding colored by expression
  p_nofacet <- plot_feature(df, expr_col = "expression")

  # Panel B: faceted by cluster
  p_facet <- plot_feature(df, expr_col = "expression", group_col = "group_label")

  out <- template_out_dir()
  save_demo(p_nofacet, name = "feature_plot_demo", out_dir = out,
            width = 85, height = 72, units = "mm", dpi = 300)
  save_demo(p_facet, name = "feature_plot_facet_demo", out_dir = out,
            width = 160, height = 100, units = "mm", dpi = 300)
  message("Demo saved to ", out)
}
