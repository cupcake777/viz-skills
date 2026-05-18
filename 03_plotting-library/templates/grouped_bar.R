tryCatch(tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))),
         error = function(e) tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R")))
suppressPackageStartupMessages(library(ggplot2))

generate_mock_data <- function(seed = 42) {
  set.seed(seed)
  expand.grid(group = c("Ctrl", "Treat"), category = c("A", "B", "C", "D")) |>
    transform(value = runif(8, 20, 80), error = runif(8, 3, 8))
}

grouped_bar_plot <- function(df, group_col = "group", category_col = "category", value_col = "value", error_col = "error", base_size = 16) {
  ggplot(df, aes(.data[[category_col]], .data[[value_col]], fill = .data[[group_col]])) +
    geom_col(position = position_dodge(0.72), width = 0.62, colour = "white", size = 0.15) +
    geom_errorbar(aes(ymin = .data[[value_col]] - .data[[error_col]], ymax = .data[[value_col]] + .data[[error_col]]), position = position_dodge(0.72), width = 0.18, size = 0.35) +
    scale_fill_manual(values = NATURE_COLORS) + labs(x = NULL, y = "Value") + theme_clean(base_size) + theme(legend.position = "top")
}

if (sys.nframe() == 0) save_demo(grouped_bar_plot(generate_mock_data()), "grouped_bar_demo")
