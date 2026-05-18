#' Bee Swarm Plot (jittered strip chart + boxplot)
#'
#' Shows individual data points jittered horizontally (beeswarm-like) with a
#' thin boxplot overlay, using only base ggplot2.  No external beeswarm
#' packages required.
#'
#' @section Required columns (data.frame):
#'   \describe{
#'     \item{group}{Character or factor – categorical x-axis grouping.}
#'     \item{value}{Numeric – continuous y-axis measurement.}
#'   }
#'
#' @section Optional columns:
#'   \describe{
#'     \item{fill}{Character/factor – mapped to point & boxplot fill colour.}
#'   }
#'
#' @seealso \code{\link{base_plot.R}} for \code{theme_sci()}, \code{NATURE_COLORS},
#'   and \code{save_demo()}.

# Source base_plot.R — try HF Space path first, then local
tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))
suppressPackageStartupMessages({library(ggplot2)})

generate_mock_data <- function(seed = 42) {
  set.seed(seed)
  groups <- rep(c("A", "B", "C", "D", "E"), each = 60)
  mu     <- rep(c(3.2, 5.8, 4.5, 7.1, 6.0), each = 60)
  sigma  <- rep(c(0.8, 1.2, 0.6, 0.9, 1.0), each = 60)
  data.frame(
    group = factor(groups, levels = c("A", "B", "C", "D", "E")),
    value = rnorm(length(groups), mu, sigma)
  )
}

#' @param df          data.frame with at least \code{group} and \code{value}.
#' @param group_col   Column name for the x-axis grouping.
#' @param value_col   Column name for the y-axis values.
#' @param fill_col    Column mapped to fill colour (default: same as group_col).
#' @param base_size   Base font size for \code{theme_sci()}.
#' @param point_size  Size of individual jittered points.
#' @param alpha       Transparency of individual points.
#' @param jitter_width Width passed to \code{position_jitter()}.
#' @param palette     Colour palette vector (default: NATURE_COLORS).
#' @param show_box    Logical; overlay a boxplot (default TRUE).
#' @return A ggplot object.
plot_bee_swarm <- function(df,
                           group_col  = "group",
                           value_col  = "value",
                           fill_col   = group_col,
                           base_size  = 14,
                           point_size = 1.5,
                           alpha      = 0.6,
                           jitter_width = 0.2,
                           palette    = NATURE_COLORS,
                           show_box   = TRUE) {
  p <- ggplot(df, aes(x = .data[[group_col]], y = .data[[value_col]],
                       colour = .data[[group_col]])) +
    geom_point(
      position = position_jitter(width = jitter_width, seed = 42),
      size     = point_size,
      alpha    = alpha
    )

  if (show_box) {
    p <- p +
      geom_boxplot(
        aes(fill = .data[[fill_col]]),
        width          = 0.35,
        outlier.shape  = NA,
        alpha          = 0.30,
        colour         = "grey25",
        size           = 0.4
      )
  }

  p <- p +
    scale_colour_manual(values = palette) +
    scale_fill_manual(values = palette) +
    labs(x = NULL, y = "Value") +
    theme_sci(base_size = base_size) +
    theme(legend.position = "none")

  p
}

# ── Demo ──────────────────────────────────────────────────────────────────────
if (sys.nframe() == 0 || isTRUE(getOption("run_demo"))) {
  demo_data <- generate_mock_data()
  demo_plot <- plot_bee_swarm(demo_data)
  save_demo(demo_plot, "bee_swarm_demo")
}
