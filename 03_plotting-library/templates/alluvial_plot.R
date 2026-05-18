#' Alluvial Plot (Sankey-style Flow Diagram)
#'
#' Alluvial diagram showing categorical flows between multiple stages.
#' Useful for visualising transitions between cell types, treatment responses,
#' or multi-stage classification outcomes.
#'
#' Required columns: one axis column per stage plus a count/frequency column.
#' The axis columns are passed as a character vector via `axes`; the column
#' named in `freq_col` supplies the flow widths.
#'
#' Uses ggalluvial::geom_alluvium() + geom_stratum() + geom_text().

suppressPackageStartupMessages({
  library(ggplot2)
  library(ggalluvial)
})

tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))

# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------
generate_mock_data <- function(seed = 42) {
  set.seed(seed)

  tissues    <- c("Brain", "Liver", "Kidney", "Lung")
  cells      <- c("Epithelial", "Immune", "Stromal", "Neuronal")
  conditions <- c("Healthy", "Disease", "Treatment")

  # Biased distributions: each tissue skews toward certain cell types,
  # each cell type skews toward certain conditions.
  tissue_cell_probs <- list(
    Brain  = c(0.10, 0.20, 0.15, 0.55),
    Liver  = c(0.40, 0.30, 0.25, 0.05),
    Kidney = c(0.50, 0.20, 0.25, 0.05),
    Lung   = c(0.45, 0.30, 0.20, 0.05)
  )
  cell_cond_probs <- list(
    Epithelial = c(0.40, 0.35, 0.25),
    Immune     = c(0.25, 0.45, 0.30),
    Stromal    = c(0.35, 0.30, 0.35),
    Neuronal   = c(0.50, 0.25, 0.25)
  )

  rows <- list()
  for (t in tissues) {
    for (i in seq_along(cells)) {
      for (j in seq_along(conditions)) {
        n <- round(100 * tissue_cell_probs[[t]][i] *
                     cell_cond_probs[[cells[i]]][j] +
                     runif(1, 1, 8))
        rows <- c(rows, list(data.frame(
          Tissue    = t,
          CellType  = cells[i],
          Condition = conditions[j],
          Count     = n,
          stringsAsFactors = FALSE
        )))
      }
    }
  }
  do.call(rbind, rows)
}

# ---------------------------------------------------------------------------
# Plot function
# ---------------------------------------------------------------------------
plot_alluvial <- function(df,
                          axes      = c("Tissue", "CellType", "Condition"),
                          freq_col  = "Count",
                          colors    = NULL,
                          base_size = 14) {

  # Convert axis columns to factors (preserve column order as presented)
  for (col in axes) {
    df[[col]] <- factor(df[[col]])
  }

  # Collect all unique stratum levels across stages for colour mapping
  all_levels <- unique(unlist(lapply(axes, function(col) levels(df[[col]]))))
  n_cats <- length(all_levels)

  # Build extended colour palette: combine NATURE + SAFE, recycle if needed
  if (is.null(colors)) {
    colors <- c(NATURE_COLORS, SAFE_COLORS)
  }
  if (n_cats > length(colors)) {
    colors <- rep_len(colors, n_cats)
  }
  names(colors) <- NULL
  color_vals <- setNames(colors[seq_len(n_cats)], all_levels)

  # Build axis aesthetics dynamically: axis1=col1, axis2=col2, ...
  axis_aes_list <- setNames(as.list(axes), paste0("axis", seq_along(axes)))
  aes_args <- c(axis_aes_list, list(y = as.name(freq_col)))

  p <- ggplot(df, do.call(aes, aes_args)) +
    geom_alluvium(aes(fill = after_stat(stratum)),
                  alpha = 0.55, width = 0.45, decreasing = TRUE) +
    geom_stratum(width = 0.22, colour = "grey30", linewidth = 0.3) +
    geom_text(stat = "stratum",
              aes(label = after_stat(stratum)),
              size = base_size / ggplot2::.pt * 0.85) +
    scale_fill_manual(values = color_vals) +
    scale_x_discrete(expand = c(0.10, 0.10)) +
    scale_y_continuous(expand = c(0.02, 0)) +
    theme_sci(base_size = base_size) +
    theme(
      axis.text.y    = element_blank(),
      axis.ticks.y   = element_blank(),
      axis.title     = element_blank(),
      legend.position = "none"
    )

  p
}

# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if (sys.nframe() == 0 || isTRUE(getOption("run_demo"))) {
  df <- generate_mock_data()
  p  <- plot_alluvial(df)

  out <- template_out_dir()
  save_demo(p, name = "alluvial_plot_demo", out_dir = out,
            width = 160, height = 110, units = "mm", dpi = 300)
  message("Alluvial demo saved to ", out)
}
