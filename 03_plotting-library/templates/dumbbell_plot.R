#' Dumbbell Plot (Paired Before-After Comparison)
#'
#' Show paired changes between two conditions with connecting segments
#' and endpoint markers. Each row is an item measured in two conditions.
#' Common in genomics (fold change), clinical (pre/post), and benchmark comparisons.
#'
#' Required columns: item, value, condition
#' Optional columns: group, label
#'
#' @seealso BBGunnarsson/dumbbellggplot, Gelman's paired comparison plots

suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
})

# Source base_plot.R — try HF Space path first, then local
tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))

generate_mock_data <- function(n_items = 10, seed = 42) {
  set.seed(seed)
  items <- paste0("Gene_", LETTERS[1:n_items])

  # Two conditions: pre and post treatment
  pre_values  <- runif(n_items, 1, 10)
  post_values <- pre_values + rnorm(n_items, mean = 1.5, sd = 1.5)
  post_values <- pmax(post_values, 0.5)

  df_pre <- data.frame(
    item = items,
    value = pre_values,
    condition = "Pre",
    stringsAsFactors = FALSE
  )
  df_post <- data.frame(
    item = items,
    value = post_values,
    condition = "Post",
    stringsAsFactors = FALSE
  )

  rbind(df_pre, df_post)
}

plot_dumbbell <- function(df,
                          item_col = "item",
                          value_col = "value",
                          condition_col = "condition",
                          group_col = NULL,
                          point_size = 3,
                          segment_alpha = 0.4,
                          segment_size = 1.2,
                          base_size = 14) {

  # Compute item order by the value of the first condition level
  condition_levels <- sort(unique(df[[condition_col]]))
  df[[condition_col]] <- factor(df[[condition_col]], levels = condition_levels)

  # Order items by spread to highlight large changes
  item_order <- df %>%
    group_by(!!sym(item_col)) %>%
    arrange(!!sym(value_col)) %>%
    summarise(spread = diff(!!sym(value_col)), .groups = "drop") %>%
    arrange(spread) %>%
    pull(!!sym(item_col))

  df[[item_col]] <- factor(df[[item_col]], levels = item_order)

  # Assign condition colors
  cond_colors <- NATURE_COLORS[1:length(condition_levels)]
  names(cond_colors) <- condition_levels

  p <- ggplot(df, aes(
    x = !!sym(value_col),
    y = !!sym(item_col),
    group = !!sym(item_col)
  )) +
    geom_line(aes(color = NULL), alpha = segment_alpha, linewidth = segment_size) +
    geom_point(aes(color = !!sym(condition_col)), size = point_size) +
    scale_color_manual(values = cond_colors, name = "Condition") +
    theme_sci(base_size = base_size) +
    theme(
      legend.position = "top",
      legend.justification = "right",
      axis.title.y = element_blank(),
      panel.grid.major.y = element_line(colour = "grey90", linewidth = 0.3)
    ) +
    labs(x = "Value", y = NULL)

  p
}

# Demo ----
if (sys.nframe() == 0 || isTRUE(getOption("run_demo"))) {
  df <- generate_mock_data()
  p <- plot_dumbbell(df)

  out <- template_out_dir()
  save_demo(p, name = "dumbbell_plot_demo", out_dir = out,
            width = 120, height = 90, units = "mm", dpi = 300)
  message("Demo saved to ", out)
}