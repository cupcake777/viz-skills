source(file.path(dirname(normalizePath(sub("^--file=", "", commandArgs(FALSE)[grepl("^--file=", commandArgs(FALSE))][1]))), "base_plot.R"))
suppressPackageStartupMessages(library(ggplot2))

generate_mock_data <- function(seed = 42) {
  set.seed(seed)
  groups <- rep(c("Control", "Treatment", "Rescue"), each = 90)
  mu <- rep(c(0, 0.65, 0.25), each = 90)
  data.frame(group = groups, value = rnorm(length(groups), mu, 0.55))
}

raincloud_plot <- function(df, group_col = "group", value_col = "value", base_size = 16) {
  df[[group_col]] <- factor(df[[group_col]], levels = unique(df[[group_col]]))
  ggplot(df, aes(.data[[group_col]], .data[[value_col]], fill = .data[[group_col]])) +
    geom_violin(width = 0.7, trim = FALSE, alpha = 0.5, colour = NA) +
    geom_boxplot(width = 0.16, outlier.shape = NA, alpha = 0.95, linewidth = 0.3) +
    geom_point(aes(colour = .data[[group_col]]), position = position_jitter(width = 0.12, height = 0), size = 0.45, alpha = 0.38) +
    stat_summary(fun = mean, geom = "point", shape = 23, size = 1.6, fill = "white", colour = "grey15") +
    scale_fill_manual(values = NATURE_COLORS) + scale_colour_manual(values = NATURE_COLORS) +
    labs(x = NULL, y = "Value") + theme_clean(base_size) + theme(legend.position = "none")
}

if (sys.nframe() == 0) save_demo(raincloud_plot(generate_mock_data()), "raincloud_demo")
