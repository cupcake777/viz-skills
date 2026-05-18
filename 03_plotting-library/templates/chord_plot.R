#' Chord Diagram
#'
#' Circular chord diagram showing relationships/flows between sectors.
#' Uses the circlize package (base R graphics, not ggplot2).

# Source base_plot.R — try HF Space path first, then local
tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))
suppressPackageStartupMessages({library(circlize)})

#' Generate mock adjacency matrix for chord diagram
#'
#' Creates a square matrix of flow values between named sectors.
#' @param n_sectors Number of sectors (default 5)
#' @param seed Random seed for reproducibility
#' @return Named numeric matrix (n_sectors x n_sectors)
generate_mock_data <- function(n_sectors = 5, seed = 42) {
  set.seed(seed)
  sector_names <- c("Brain", "Heart", "Liver", "Kidney", "Lung",
                     "Muscle")[seq_len(min(n_sectors, 6))]
  mat <- matrix(sample(0:20, n_sectors * n_sectors, replace = TRUE),
                nrow = n_sectors, ncol = n_sectors)
  diag(mat) <- 0
  rownames(mat) <- sector_names
  colnames(mat) <- sector_names
  list(mat = mat)
}

#' Save base-R / circlize figure to PDF and PNG
#'
#' Wraps a plotting expression in pdf() / png() device calls.
#' @param expr A quoted or braced expression that produces the plot
#' @param name Output file basename (without extension)
#' @param out_dir Output directory
#' @param width Width in inches
#' @param height Height in inches
#' @param dpi Resolution for PNG
save_base_figure <- function(expr, name, out_dir = template_out_dir(),
                             width = 7, height = 7, dpi = 300) {
  dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
  pdf_path <- file.path(out_dir, paste0(name, ".pdf"))
  png_path <- file.path(out_dir, paste0(name, ".png"))
  pdf(pdf_path, width = width, height = height)
  eval(expr)
  dev.off()
  png(png_path, width = width, height = height, units = "in", res = dpi)
  eval(expr)
  dev.off()
  invisible(c(pdf = pdf_path, png = png_path))
}

#' Plot chord diagram from adjacency matrix
#'
#' Creates a chordDiagram using circlize with NATURE_COLORS for sectors.
#' @param mat Named adjacency matrix
#' @param sector_colors Named vector of colors for sectors (default NATURE_COLORS)
#' @param transparency Link transparency (default 0.4)
#' @param title Optional plot title
#' @return NULL (draws plot as side effect)
plot_chord <- function(mat, sector_colors = NULL, transparency = 0.4,
                       title = NULL) {
  n <- nrow(mat)
  if (is.null(sector_colors)) {
    sector_colors <- rep(NATURE_COLORS, length.out = n)
    names(sector_colors) <- rownames(mat)
  }
  circos.clear()
  circos.par(start.degree = 90, gap.degree = rep(c(2, 6), length.out = n),
             track.margin = c(0.005, 0.005))
  chordDiagram(mat,
               grid.col = sector_colors,
               transparency = transparency,
               annotationTrack = c("grid", "name"),
               annotationTrackHeight = c(0.04, 0.02),
               link.lwd = 0.5,
               link.lty = 1,
               link.border = "grey40")
  if (!is.null(title)) {
    title(main = title, cex.main = 1.0, line = -1)
  }
  circos.clear()
  invisible(NULL)
}

# ── Demo block ───────────────────────────────────────────────────────────
if (sys.nframe() == 0) {
  mat <- generate_mock_data(n_sectors = 5)
  save_base_figure(
    expr = quote(plot_chord(mat, title = "Tissue Interactions")),
    name = "chord_demo",
    width = 7, height = 7
  )
}
