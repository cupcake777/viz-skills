#' Ternary Plot (Manual Implementation -- No ggtern Dependency)
#'
#' Three-component compositional data on an equilateral triangle.
#' Uses manual ternary-to-Cartesian transformation so no special
#' packages are needed.
#'
#' Transformation:
#'   x_cart = A + 0.5 * C
#'   y_cart = C * sqrt(3) / 2
#'
#' Vertex layout:  A=1 at (1,0), B=1 at (0,0), C=1 at (0.5, sqrt3/2)
#'
#' Required columns: A, B, C (three components summing to 1)
#' Optional columns: group (categorical colour), label

suppressPackageStartupMessages({
  library(ggplot2)
})

source(file.path(dirname(normalizePath(sub("^--file=", "",
  commandArgs(FALSE)[grepl("^--file=", commandArgs(FALSE))][1]))), "base_plot.R"))

# --- Mock data (Dirichlet-simulated) ------------------------------------

generate_mock_data <- function(n_samples = 40, seed = 42) {
  set.seed(seed)

  rdirichlet <- function(n, alpha) {
    k   <- length(alpha)
    mat <- matrix(rgamma(n * k, shape = alpha, rate = 1), ncol = k)
    mat / rowSums(mat)
  }

  group_params <- list(
    "Group A" = c(5, 2, 1),
    "Group B" = c(1, 5, 2),
    "Group C" = c(2, 1, 5)
  )

  per <- ceiling(n_samples / length(group_params))
  dfs <- mapply(function(g, a) {
    comps <- rdirichlet(per, a)
    data.frame(A = comps[, 1], B = comps[, 2], C = comps[, 3], group = g)
  }, names(group_params), group_params, SIMPLIFY = FALSE)

  df <- do.call(rbind, dfs)[seq_len(n_samples), ]
  df$x <- df$A + df$C / 2
  df$y <- df$C * sqrt(3) / 2
  df
}

# --- Grid lines at 0.2 intervals ---------------------------------------

make_grid_lines <- function() {
  gv <- seq(0.2, 0.8, by = 0.2)
  lines <- list()

  for (a in gv) {
    ce <- 1 - a
    lines <- c(lines, list(data.frame(
      x = c(a, a + ce / 2), y = c(0, ce * sqrt(3) / 2),
      grid_id = paste0("A=", a)
    )))
  }
  for (b in gv) {
    ce <- 1 - b
    lines <- c(lines, list(data.frame(
      x = c(1 - b, 1 - b - ce / 2), y = c(0, ce * sqrt(3) / 2),
      grid_id = paste0("B=", b)
    )))
  }
  for (cc in gv) {
    lines <- c(lines, list(data.frame(
      x = c(cc / 2, (1 - cc) + cc / 2), y = rep(cc * sqrt(3) / 2, 2),
      grid_id = paste0("C=", cc)
    )))
  }
  do.call(rbind, lines)
}

# --- Axis ticks and titles -----------------------------------------------

make_axis_labels <- function() {
  tv <- seq(0, 1, by = 0.2)
  s32 <- sqrt(3) / 2
  list(
    bottom = data.frame(x = tv, y = 0, label = sprintf("%.1f", tv)),
    right  = data.frame(x = 1 - tv / 2, y = tv * s32,
                        label = sprintf("%.1f", tv)),
    left   = data.frame(x = (1 - tv) / 2, y = (1 - tv) * s32,
                        label = sprintf("%.1f", tv)),
    titles = data.frame(
      x     = c(0.5, 0.75 + 0.08, 0.25 - 0.08),
      y     = c(-0.09, s32 / 2 + 0.06, s32 / 2 + 0.06),
      label = c("Component A", "Component C", "Component B"),
      angle = c(0, -60, 60)
    )
  )
}

# --- Plot function -------------------------------------------------------

plot_ternary <- function(df,
                         a_col = "A", b_col = "B", c_col = "C",
                         group_col = "group",
                         point_size = 3,
                         alpha = 0.8,
                         base_size = 14) {

  s32 <- sqrt(3) / 2
  tri <- data.frame(x = c(0, 1, 0.5, 0), y = c(0, 0, s32, 0))
  grid_df <- make_grid_lines()
  axis <- make_axis_labels()

  p <- ggplot() +
    # Grid
    geom_path(data = grid_df,
              aes(x = x, y = y, group = grid_id),
              color = "grey80", size = 0.3, linetype = "dashed") +
    # Triangle boundary
    geom_path(data = tri, aes(x = x, y = y),
              color = "black", size = 0.8) +
    # Data points
    geom_point(data = df,
               aes(x = .data[["x"]], y = .data[["y"]],
                   color = .data[[group_col]]),
               size = point_size, alpha = alpha) +
    # Axis tick labels
    geom_text(data = axis$bottom,
              aes(x = x, y = y, label = label), vjust = 1.5, size = 3.2) +
    geom_text(data = axis$right,
              aes(x = x, y = y, label = label), hjust = -0.3, size = 3.2) +
    geom_text(data = axis$left,
              aes(x = x, y = y, label = label), hjust = 1.3, size = 3.2) +
    # Axis titles
    geom_text(data = axis$titles,
              aes(x = x, y = y, label = label, angle = angle),
              size = 4.2, fontface = "bold") +
    scale_color_manual(values = NATURE_COLORS[1:3], name = "Group") +
    coord_equal(xlim = c(-0.15, 1.15), ylim = c(-0.15, s32 + 0.15)) +
    theme_void(base_size = base_size) +
    theme(
      legend.position  = "bottom",
      legend.title     = element_text(face = "bold"),
      legend.key.height = unit(6, "pt"),
      legend.key.width  = unit(8, "pt"),
      plot.margin       = margin(10, 10, 10, 10)
    ) +
    labs(x = NULL, y = NULL)

  p
}

# --- Demo ----------------------------------------------------------------
if (sys.nframe() == 0 || isTRUE(getOption("run_demo"))) {
  df <- generate_mock_data()
  p <- plot_ternary(df)

  out <- template_out_dir()
  save_demo(p, name = "ternary_plot_demo", out_dir = out,
            width = 120, height = 110, units = "mm", dpi = 300)
  message("Demo saved to ", file.path(out, "ternary_plot_demo.png"))
}