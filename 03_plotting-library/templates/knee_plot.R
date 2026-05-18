#' Knee Plot (Ranked Abundance with Inflection)
#'
#' Log-log ranked abundance plot for cell barcode / UMI filtering.
#' Detects the inflection ("knee") point separating real cells from
#' background. Inspired by CellBender (Fleming et al., Nature Methods 2023)
#' and EmptyDrops (Lun et al., PLoS Comput Biol 2019).
#'
#' Required columns: barcode_id, umi_count
#' Optional columns: is_cell (logical), cell_prob (0-1)

suppressPackageStartupMessages({
  library(ggplot2)
})

tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R")))

find_knee <- function(log_counts, log_rank) {
  # Max curvature in log-log space
  n <- length(log_counts)
  if (n < 10) return(n)
  dx <- diff(log_rank)
  dy <- diff(log_counts)
  ds <- sqrt(dx^2 + dy^2)
  tx <- cumsum(dx / ds)
  ty <- cumsum(dy / ds)
  ddx <- diff(tx)
  ddy <- diff(ty)
  dds <- sqrt(ddx^2 + ddy^2)
  kappa <- abs(ddx * ty[-1] - ddy * tx[-1]) / (dds^3)
  kappa[is.na(kappa) | is.infinite(kappa)] <- 0
  which.max(kappa) + 1
}

generate_mock_data <- function(n_cells = 2500, n_empty = 7500, seed = 42) {
  set.seed(seed)

  # Real cells: higher UMI counts
  cell_counts <- rlnorm(n_cells, meanlog = 7, sdlog = 1.2)
  # Background: lower counts
  empty_counts <- rlnorm(n_empty, meanlog = 3, sdlog = 0.8)

  all_counts <- c(cell_counts, empty_counts)
  all_counts <- sort(all_counts, decreasing = TRUE)

  data.frame(
    barcode_id = seq_along(all_counts),
    umi_count = round(all_counts),
    is_cell = c(rep(TRUE, n_cells), rep(FALSE, n_empty))[order(c(
      seq_len(n_cells), n_cells + seq_len(n_empty)
    ), decreasing = TRUE)],
    cell_prob = c(
      runif(n_cells, 0.7, 1.0),
      runif(n_empty, 0, 0.3)
    ),
    stringsAsFactors = FALSE
  )
}

plot_knee <- function(df,
                      rank = "barcode_id",
                      count = "umi_count",
                      is_cell = "is_cell",
                      cell_prob = NULL,
                      show_inflection = TRUE,
                      base_size = 14) {

  df[[rank]] <- as.numeric(df[[rank]])
  df <- df[order(df[[count]], decreasing = TRUE), ]
  df[[rank]] <- seq_len(nrow(df))

  # Build aes conditionally (ggplot2 3.5+ forbids if() inside aes)
  point_aes <- aes(x = .data[[rank]], y = .data[[count]])
  has_is_cell <- !is.null(is_cell) && is_cell %in% names(df) && is.character(is_cell) && length(is_cell) == 1
  if (has_is_cell) {
    point_aes <- aes(x = .data[[rank]], y = .data[[count]], color = .data[[is_cell]])
  }

  p <- ggplot(df, point_aes) +
    geom_point(size = 0.5, alpha = 0.6, shape = 16) +
    scale_x_log10(labels = scales::comma) +
    scale_y_log10(labels = scales::comma) +
    annotation_logticks(sides = "bl", linewidth = 0.2)

  if (has_is_cell) {
    p <- p + scale_color_manual(values = c("TRUE" = "#E64B35", "FALSE" = "#CFD5E2"),
                                 name = "Cell", labels = c("Empty", "Cell"))
  } +
    theme_sci(base_size = base_size) +
    theme(
      legend.position = "top",
      legend.key.height = unit(6, "pt")
    ) +
    labs(x = "Barcode Rank", y = "UMI Count")

  # Mark inflection point
  if (show_inflection) {
    log_c <- log10(df[[count]])
    log_r <- log10(df[[rank]])
    knee_idx <- find_knee(log_c, log_r)
    if (knee_idx > 0 && knee_idx <= nrow(df)) {
      p <- p + annotate("vline", xintercept = df[[rank]][knee_idx],
                        linetype = "dashed", color = "#3C5488", linewidth = 0.5) +
        annotate("label",
                 x = df[[rank]][knee_idx] * 2,
                 y = df[[count]][1] * 0.3,
                 label = paste0("Knee (", scales::comma(df[[rank]][knee_idx]), ")"),
                 size = 3, color = "#3C5488", fill = "white", label.size = 0)
    }
  }

  p
}

# Demo ----
if (sys.nframe() == 0 || isTRUE(getOption("run_demo"))) {
  df <- generate_mock_data()
  p <- plot_knee(df)

  out <- template_out_dir()
  save_demo(p, name = "knee_plot_demo", out_dir = out,
            width = 140, height = 100, units = "mm", dpi = 300)
  message("Demo saved to ", file.path(out, "knee_plot_demo.png"))
}
