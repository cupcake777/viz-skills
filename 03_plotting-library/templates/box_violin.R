source(file.path(dirname(normalizePath(sub("^--file=", "", commandArgs(FALSE)[grepl("^--file=", commandArgs(FALSE))][1]))), "base_plot.R"))
suppressPackageStartupMessages(library(ggplot2))

generate_mock_data <- function(seed = 42) {
  set.seed(seed)
  groups <- rep(c("Fetal", "Child", "Adult", "Aged"), each = 80)
  mu <- rep(c(0.35, 0.48, 0.62, 0.55), each = 80)
  data.frame(group = groups, value = pmin(pmax(rnorm(length(groups), mu, 0.12), 0), 1))
}

box_violin_plot <- function(df, group_col = "group", value_col = "value", base_size = 16) {
  ggplot(df, aes(.data[[group_col]], .data[[value_col]], fill = .data[[group_col]])) +
    geom_violin(width = 0.82, trim = FALSE, alpha = 0.55, colour = NA) +
    geom_boxplot(width = 0.18, outlier.shape = NA, linewidth = 0.35, alpha = 0.9) +
    geom_jitter(width = 0.08, size = 0.45, alpha = 0.35, colour = "grey25") +
    scale_fill_manual(values = NATURE_COLORS) +
    labs(x = NULL, y = "Value") +
    theme_clean(base_size) + theme(legend.position = "none")
}

if (sys.nframe() == 0) save_demo(box_violin_plot(generate_mock_data()), "box_violin_demo")
