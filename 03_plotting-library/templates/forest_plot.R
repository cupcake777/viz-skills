tryCatch(tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))),
         error = function(e) tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R")))
suppressPackageStartupMessages(library(ggplot2))

generate_mock_data <- function(seed = 42) {
  data.frame(
    variable = c("Age > 65", "Male", "Stage III/IV", "TP53 mutation", "BRAF mutation", "BMI > 30", "Smoking", "APA lengthening"),
    estimate = c(1.45, 1.12, 2.31, 1.87, 0.73, 0.91, 1.56, 1.68),
    ci_lower = c(1.10, 0.89, 1.72, 1.42, 0.55, 0.68, 1.12, 1.28),
    ci_upper = c(1.92, 1.41, 3.10, 2.46, 0.97, 1.22, 2.17, 2.20),
    pvalue = c(0.008, 0.224, 1e-5, 3e-4, 0.031, 0.542, 0.009, 2e-4)
  )
}

forest_plot <- function(df, var_col = "variable", est_col = "estimate", lower_col = "ci_lower", upper_col = "ci_upper", p_col = "pvalue", ref_line = 1, base_size = 16) {
  df <- df[rev(seq_len(nrow(df))), ]
  df[[var_col]] <- factor(df[[var_col]], levels = df[[var_col]])
  df$label <- sprintf("%.2f (%.2f-%.2f)", df[[est_col]], df[[lower_col]], df[[upper_col]])
  label_x <- max(df[[upper_col]], na.rm = TRUE) * 1.55
  ggplot(df, aes(.data[[est_col]], .data[[var_col]])) +
    geom_vline(xintercept = ref_line, linetype = "22", colour = "grey55", size = 0.35) +
    geom_errorbarh(aes(xmin = .data[[lower_col]], xmax = .data[[upper_col]]), height = 0.18, size = 0.45, colour = "#3C5488") +
    geom_point(shape = 18, size = 2.1, colour = "#D73027") +
    geom_text(aes(x = label_x, label = label), hjust = 0, size = base_size / ggplot2::.pt) +
    scale_x_log10() +
    coord_cartesian(xlim = c(min(df[[lower_col]]) * 0.82, max(df[[upper_col]]) * 2.9), clip = "off") +
    labs(x = "Hazard ratio (95% CI)", y = NULL) +
    theme_clean(base_size) + theme(plot.margin = margin(8, 95, 8, 8, "pt"))
}

if (sys.nframe() == 0) save_demo(forest_plot(generate_mock_data()), "forest_plot_demo", width = 180, height = 95)
