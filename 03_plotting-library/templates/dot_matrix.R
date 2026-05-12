#' Dot Matrix Plot (Size + Color Encoded)
#'
#' Two-metric dot matrix where point size encodes one metric and fill color
#' encodes another. Common in benchmark comparisons and gene-by-sample
#' summaries. Inspired by scib benchmark (Luecken et al., Nature Methods 2022)
#' and scanpy dotplot.
#'
#' Required columns: row_id, col_id, size_value, fill_value
#' Optional columns: row_group

suppressPackageStartupMessages({
  library(ggplot2)
})

source(file.path(dirname(sys.frame(1)$ofile), "base_plot.R"))

generate_mock_data <- function(n_methods = 8, n_metrics = 5, seed = 42) {
  set.seed(seed)

  methods <- paste0("Method_", LETTERS[1:n_methods])
  metrics <- c("Accuracy", "Precision", "Recall", "F1 Score", "AUPRC")
  groups <- c(rep("Batch Correction", 2), rep("Bio Conservation", 3))

  rows <- expand.grid(method = methods, metric = metrics, stringsAsFactors = FALSE)
  rows$size_value <- runif(nrow(rows), 0.2, 1)
  rows$fill_value <- runif(nrow(rows), 0.1, 0.95)
  rows$row_group <- rep(groups, each = n_methods)

  # Make some methods clearly better
  rows$fill_value[rows$method == "Method_A"] <- rows$fill_value[rows$method == "Method_A"] * 0.3 + 0.7
  rows$size_value[rows$method == "Method_A"] <- rows$size_value[rows$method == "Method_A"] * 0.3 + 0.7

  rows
}

plot_dot_matrix <- function(df,
                            row_id = "method",
                            col_id = "metric",
                            size_value = "size_value",
                            fill_value = "fill_value",
                            row_group = "row_group",
                            palette = "RdYlBu",
                            base_size = 14) {

  # Order rows by overall score
  row_order <- aggregate(df[[fill_value]], list(row = df[[row_id]]), mean)
  row_order <- row_order$row[order(row_order$x, decreasing = TRUE)]
  df[[row_id]] <- factor(df[[row_id]], levels = rev(row_order))

  p <- ggplot(df, aes(
    x = .data[[col_id]],
    y = .data[[row_id]],
    size = .data[[size_value]],
    fill = .data[[fill_value]]
  )) +
    geom_point(shape = 21, color = "grey30", stroke = 0.3) +
    scale_size_continuous(range = c(1, 8), name = "Score\nMagnitude") +
    scale_fill_distiller(palette = palette, direction = -1, name = "Score\nValue") +
    theme_sci(base_size = base_size) +
    theme(
      axis.text.x = element_text(angle = 45, hjust = 1),
      panel.grid.major = element_line(color = "grey92", size = 0.2),
      panel.grid.minor = element_blank(),
      legend.key.height = unit(6, "pt"),
      legend.key.width = unit(8, "pt")
    ) +
    labs(x = NULL, y = NULL)

  p
}

# Demo ----
if (sys.nframe() == 0 || isTRUE(getOption("run_demo"))) {
  df <- generate_mock_data()
  p <- plot_dot_matrix(df)

  out <- template_out_dir()
  save_demo(p, name = "dot_matrix_demo", out_dir = out,
            width = 130, height = 100, units = "mm", dpi = 300)
  message("Demo saved to ", file.path(out, "dot_matrix_demo.png"))
}
