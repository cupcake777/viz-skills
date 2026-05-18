#' Compositional Stacked Bar Chart
#'
#' Stacked bar chart for compositional data (e.g., microbial phyla by body site).
#' Two modes: "fill" (proportions, default) and "stack" (absolute counts).
#' White borders separate segments for clean visual delineation.
#'
#' Required columns: sample_id, category, value
#' Optional columns: group

suppressPackageStartupMessages({
  library(ggplot2)
})

tryCatch(tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))),
         error = function(e) tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R")))

generate_mock_data <- function(n_sites = 6, n_phyla = 5, seed = 42) {
  set.seed(seed)

  sites <- c("Gut", "Skin", "Oral", "Lung", "Nasal", "Vaginal")
  phyla <- c("Firmicutes", "Bacteroidetes", "Proteobacteria", "Actinobacteria", "Fusobacteria")

  rows <- expand.grid(
    sample_id = sites,
    category  = phyla,
    stringsAsFactors = FALSE
  )

  # Realistic-ish compositional draws via Dirichlet
  rows$value <- NA_real_
  for (s in sites) {
    alpha <- runif(n_phyla, 0.5, 5)
    props <- rgamma(n_phyla, alpha)
    props <- props / sum(props)
    total <- runif(1, 800, 2000)
    rows$value[rows$sample_id == s] <- round(props * total, 1)
  }

  # Enrich Firmicutes in Gut, Actinobacteria in Skin
  rows$value[rows$sample_id == "Gut" & rows$category == "Firmicutes"] <-
    rows$value[rows$sample_id == "Gut" & rows$category == "Firmicutes"] * 2
  rows$value[rows$sample_id == "Skin" & rows$category == "Actinobacteria"] <-
    rows$value[rows$sample_id == "Skin" & rows$category == "Actinobacteria"] * 2.5

  # Re-normalise per site so fill mode looks clean
  for (s in sites) {
    idx <- rows$sample_id == s
    total <- sum(rows$value[idx])
    rows$value[idx] <- rows$value[idx] / total * runif(1, 800, 2000)
  }

  rows
}

plot_stacked_bar <- function(df,
                             sample_id = "sample_id",
                             category  = "category",
                             value     = "value",
                             mode      = c("fill", "stack"),
                             colors    = NATURE_COLORS,
                             base_size = 14) {

  mode <- match.arg(mode)

  # Order categories by overall abundance (largest at bottom)
  cat_order <- aggregate(df[[value]], list(cat = df[[category]]), sum)
  cat_order <- cat_order$cat[order(cat_order$x, decreasing = TRUE)]
  df[[category]] <- factor(df[[category]], levels = cat_order)

  # Order sites by dominant phylum proportion
  site_order <- aggregate(df[[value]], list(site = df[[sample_id]]), sum)
  site_order <- site_order$site[order(site_order$x, decreasing = TRUE)]
  df[[sample_id]] <- factor(df[[sample_id]], levels = site_order)

  position <- if (mode == "fill") "fill" else "stack"

  p <- ggplot(df, aes(
    x    = .data[[sample_id]],
    y    = .data[[value]],
    fill = .data[[category]]
  )) +
    geom_col(position = position, color = "white", linewidth = 0.3, width = 0.75) +
    scale_fill_manual(values = colors[seq_along(cat_order)]) +
    theme_sci(base_size = base_size) +
    theme(
      axis.text.x = element_text(angle = 45, hjust = 1),
      legend.key.height = unit(6, "pt"),
      legend.key.width  = unit(8, "pt")
    ) +
    labs(x = NULL, y = if (mode == "fill") "Relative Abundance" else "Absolute Abundance")

  p
}

# Demo ----
if (sys.nframe() == 0 || isTRUE(getOption("run_demo"))) {
  df <- generate_mock_data()

  p_fill  <- plot_stacked_bar(df, mode = "fill")
  p_stack <- plot_stacked_bar(df, mode = "stack")

  out <- template_out_dir()
  save_demo(p_fill,  name = "stacked_bar_fill_demo",  out_dir = out,
            width = 130, height = 100, units = "mm", dpi = 300)
  save_demo(p_stack, name = "stacked_bar_stack_demo", out_dir = out,
            width = 130, height = 100, units = "mm", dpi = 300)
  message("Demos saved to ", out)
}
