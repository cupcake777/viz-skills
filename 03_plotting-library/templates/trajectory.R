#' Trajectory Plot with Directional Arrows
#'
#' Visualization of cell trajectories on 2D embeddings with directional
#' arrows indicating differentiation paths. Inspired by Palantir
#' (Setty et al., Nature Biotechnology 2019).
#'
#' Required columns: x, y
#' Optional columns: pseudotime, branch, arrow_path

suppressPackageStartupMessages({
  library(ggplot2)
})

source(file.path(dirname(sys.frame(1)$ofile), "base_plot.R"))

generate_mock_data <- function(n_bg = 500, n_branch = 3, pts_per_branch = 80, seed = 42) {
  set.seed(seed)

  # Background cells in clusters
  bg <- data.frame(
    x = c(rnorm(200, -3, 0.8), rnorm(150, 0, 1), rnorm(150, 3, 0.8)),
    y = c(rnorm(200, 0, 0.8), rnorm(150, 2, 0.8), rnorm(150, 0, 0.8)),
    pseudotime = NA_real_,
    branch = NA_character_,
    is_bg = TRUE,
    stringsAsFactors = FALSE
  )

  branches <- list()
  branch_names <- c("Branch_A", "Branch_B", "Branch_C")
  angles <- c(pi / 3, pi / 2, 2 * pi / 3)
  colors <- c("#E64B35", "#4DBBD5", "#00A087")

  for (i in seq_len(n_branch)) {
    t <- seq(0, 4, length.out = pts_per_branch)
    curve_x <- t * cos(angles[i]) + rnorm(pts_per_branch, 0, 0.15)
    curve_y <- t * sin(angles[i]) + rnorm(pts_per_branch, 0, 0.15)
    branches[[i]] <- data.frame(
      x = curve_x,
      y = curve_y,
      pseudotime = t / max(t),
      branch = branch_names[i],
      is_bg = FALSE,
      stringsAsFactors = FALSE
    )
  }

  branch_df <- do.call(rbind, branches)
  rbind(bg, branch_df)
}

plot_trajectory <- function(df,
                            x = "x", y = "y",
                            pseudotime = "pseudotime",
                            branch = "branch",
                            arrow_paths = NULL,
                            point_size_bg = 1,
                            point_size_fg = 2,
                            base_size = 14) {

  bg <- df[df$is_bg, ]
  fg <- df[!df$is_bg, ]

  p <- ggplot() +
    # Background layer
    geom_point(
      data = bg,
      aes(x = .data[[x]], y = .data[[y]]),
      color = "#CFD5E2", size = point_size_bg, alpha = 0.5
    ) +
    # Foreground: trajectory cells colored by pseudotime
    geom_point(
      data = fg,
      aes(x = .data[[x]], y = .data[[y]], color = .data[[pseudotime]]),
      size = point_size_fg, alpha = 0.8
    ) +
    scale_color_viridis_c(option = "C", name = "Pseudotime") +
    theme_sci(base_size = base_size) +
    theme(
      axis.text = element_blank(),
      axis.ticks = element_blank(),
      axis.line = element_blank(),
      axis.title.x = element_text(margin = margin(t = 2)),
      axis.title.y = element_text(margin = margin(r = 2))
    ) +
    labs(x = "Embedding 1", y = "Embedding 2")

  # Add directional arrows along each branch
  if (!is.null(branch) && branch %in% names(fg)) {
    for (br in unique(fg[[branch]])) {
      br_df <- fg[fg[[branch]] == br, ]
      br_df <- br_df[order(br_df[[pseudotime]]), ]

      # Draw smooth path
      n_pts <- nrow(br_df)
      if (n_pts > 5) {
        # Arrow at midpoint and endpoint
        for (frac in c(0.5, 0.9)) {
          idx <- round(frac * n_pts)
          idx <- min(max(idx, 2), n_pts)
          dx <- br_df[[x]][idx] - br_df[[x]][idx - 1]
          dy <- br_df[[y]][idx] - br_df[[y]][idx - 1]
          p <- p + annotate(
            "segment",
            x = br_df[[x]][idx - 1], y = br_df[[y]][idx - 1],
            xend = br_df[[x]][idx], yend = br_df[[y]][idx],
            arrow = arrow(length = unit(0.15, "cm"), type = "closed"),
            color = "grey30", size = 0.8
          )
        }
      }
    }
  }

  p
}

# Demo ----
if (sys.nframe() == 0 || isTRUE(getOption("run_demo"))) {
  df <- generate_mock_data()
  p <- plot_trajectory(df)

  out <- template_out_dir()
  save_demo(p, name = "trajectory_demo", out_dir = out,
            width = 160, height = 130, units = "mm", dpi = 300)
  message("Demo saved to ", file.path(out, "trajectory_demo.png"))
}
