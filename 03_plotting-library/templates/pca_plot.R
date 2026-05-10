source(file.path(dirname(normalizePath(sub("^--file=", "", commandArgs(FALSE)[grepl("^--file=", commandArgs(FALSE))][1]))), "base_plot.R"))
suppressPackageStartupMessages(library(ggplot2))

generate_mock_data <- function(seed = 42) {
  set.seed(seed); n <- 120; group <- rep(c("Batch 1", "Batch 2", "Batch 3"), each = 40)
  centers <- data.frame(x = c(-2, 1.5, 0.5), y = c(0, 1.2, -1.4))
  data.frame(PC1 = rnorm(n, centers$x[as.integer(factor(group))], 0.8), PC2 = rnorm(n, centers$y[as.integer(factor(group))], 0.65), group_label = group)
}

pca_plot <- function(df, x_col = "PC1", y_col = "PC2", group_col = "group_label", base_size = 16) {
  ggplot(df, aes(.data[[x_col]], .data[[y_col]], colour = .data[[group_col]], fill = .data[[group_col]])) +
    stat_ellipse(geom = "polygon", alpha = 0.12, linewidth = 0.35, show.legend = FALSE) +
    geom_point(size = 1.2, alpha = 0.82) +
    scale_colour_manual(values = NATURE_COLORS) + scale_fill_manual(values = NATURE_COLORS) +
    labs(x = "PC1", y = "PC2") + theme_clean(base_size) + theme(legend.position = "top")
}

if (sys.nframe() == 0) save_demo(pca_plot(generate_mock_data()), "pca_demo")
