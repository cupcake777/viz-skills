#' Peri-Event Time Histogram / Raster
#'
#' Produces a two-panel figure aligned to a behavioural or stimulus event:
#'   TOP  – mean +/- SEM z-score trace with per-trial semi-transparent lines
#'   BOTTOM – heatmap of all trials (time x trial), ordered by trial index
#'
#' Inspired by dLight fibre-photometry recordings aligned to reward delivery
#' (GLP-1R reward-circuit study).
#'
#' @section Required columns (data.frame):
#'   \describe{
#'     \item{time}{Numeric – time relative to event onset (seconds).}
#'     \item{z_score}{Numeric – z-scored fluorescence (or any continuous signal).}
#'     \item{trial}{Integer or factor – trial identifier.}
#'   }
#'
#' @section Optional columns:
#'   \describe{
#'     \item{condition}{Character/factor – experimental condition for colouring.}
#'   }
#'
#' @seealso \code{\link{base_plot.R}} for \code{theme_sci()}, \code{NATURE_COLORS},
#'   and \code{save_demo()}.

# Source base_plot.R — try HF Space path first, then local
tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))
suppressPackageStartupMessages({
  library(ggplot2)
  library(patchwork)
})

# ---------------------------------------------------------------------------
# Mock data generator
# ---------------------------------------------------------------------------
generate_mock_data <- function(n_trials = 6, n_timepoints = 200,
                               event_time = 0, seed = 42) {
  set.seed(seed)
  time_seq <- seq(event_time - 50, event_time + 50, length.out = n_timepoints)
  trials <- paste0("T", sprintf("%02d", seq_len(n_trials)))

  rows <- lapply(seq_len(n_trials), function(i) {
    # Simulate a transient rise after event_time
    baseline <- rnorm(n_timepoints, mean = 0, sd = 0.3)
    # Add a Gaussian bump centred slightly after event for half the trials
    amp <- if (i <= n_trials / 2) runif(1, 1.5, 3.0) else runif(1, 0.2, 0.8)
    centre <- event_time + runif(1, 2, 8)
    bump   <- amp * exp(-((time_seq - centre)^2) / (2 * 4^2))
    # Small drift
    drift  <- cumsum(rnorm(n_timepoints, 0, 0.01))
    z      <- baseline + bump + drift
    condition <- if (i <= n_trials / 2) "Responsive" else "Non-responsive"
    data.frame(time = time_seq, z_score = z, trial = trials[i],
               condition = condition, stringsAsFactors = FALSE)
  })
  do.call(rbind, rows)
}

# ---------------------------------------------------------------------------
# Core plotting function
# ---------------------------------------------------------------------------
#' @param df             data.frame with columns specified above.
#' @param time_col       Column name for time axis (default "time").
#' @param z_col          Column name for z-score signal (default "z_score").
#' @param trial_col      Column name for trial identifier (default "trial").
#' @param event_time     Numeric x-value marking the event (default 0).
#' @param baseline_window Numeric vector of length 2, baseline window limits
#'                        (default c(-30, 0)).
#' @param condition_col  Column name for condition grouping (default "condition").
#'                        Set to NULL to colour by trial instead.
#' @param alpha_traces   Transparency for per-trial lines (default 0.35).
#' @param palette        Colour vector for conditions/trials.
peri_event_raster_plot <- function(df,
                                   time_col = "time",
                                   z_col = "z_score",
                                   trial_col = "trial",
                                   event_time = 0,
                                   baseline_window = c(-30, 0),
                                   condition_col = "condition",
                                   alpha_traces = 0.35,
                                   palette = NULL) {

  palette <- palette %||% NATURE_COLORS

  # --- Compute mean + SEM across trials per timepoint -----------------------
  group_vars <- c(time_col)
  df[[trial_col]] <- as.factor(df[[trial_col]])

  mean_df <- aggregate(
    df[[z_col]], by = list(time = df[[time_col]]),
    FUN = function(x) c(mean = mean(x), sem = sd(x) / sqrt(length(x)))
  )
  mean_df <- data.frame(
    time = mean_df$time,
    mean = mean_df$x[, "mean"],
    sem  = mean_df$x[, "sem"]
  )

  # --- Baseline shading -----------------------------------------------------
  bl_rect <- data.frame(
    xmin = baseline_window[1], xmax = baseline_window[2],
    ymin = -Inf, ymax = Inf
  )

  # --- TOP PANEL: per-trial traces + mean -----------------------------------
  p_top <- ggplot() +
    # Baseline shading
    geom_rect(data = bl_rect,
              aes(xmin = xmin, xmax = xmax, ymin = ymin, ymax = ymax),
              fill = "grey85", alpha = 0.4, inherit.aes = FALSE) +
    # Per-trial traces
    geom_line(
      data = df,
      aes(x = .data[[time_col]], y = .data[[z_col]],
          group = .data[[trial_col]],
          colour = if (!is.null(condition_col) && condition_col %in% names(df))
                     as.factor(.data[[condition_col]]) else .data[[trial_col]]),
      alpha = alpha_traces, linewidth = 0.4
    ) +
    # Mean bold line
    geom_line(data = mean_df,
              aes(x = time, y = mean),
              colour = "black", linewidth = 0.9) +
    # SEM ribbon
    geom_ribbon(data = mean_df,
                aes(x = time, ymin = mean - sem, ymax = mean + sem),
                fill = "grey30", alpha = 0.2) +
    # Event marker
    geom_vline(xintercept = event_time, linetype = "dashed",
               colour = "grey30", linewidth = 0.4) +
    scale_colour_manual(values = palette) +
    labs(x = NULL, y = "z-score") +
    theme_sci() +
    theme(legend.position = "top",
          axis.text.x = element_blank(),
          axis.ticks.x = element_blank())

  # --- BOTTOM PANEL: heatmap of all trials ----------------------------------
  # Order trials for display
  trial_levels <- unique(df[[trial_col]])
  df[[trial_col]] <- factor(df[[trial_col]], levels = rev(trial_levels))

  p_bottom <- ggplot(df, aes(x = .data[[time_col]],
                              y = .data[[trial_col]],
                              fill = .data[[z_col]])) +
    geom_tile() +
    geom_vline(xintercept = event_time, linetype = "dashed",
               colour = "white", linewidth = 0.3) +
    scale_fill_gradientn(
      colours = c("#2166AC", "#67A9CF", "#F7F7F7", "#EF8A62", "#B2182B"),
      name = "z-score"
    ) +
    labs(x = "Time relative to event (s)", y = "Trial") +
    theme_sci() +
    theme(legend.position = "right",
          axis.text.y = element_text(size = rel(0.7)))

  # --- Combine with patchwork -----------------------------------------------
  p_top / p_bottom +
    plot_layout(heights = c(2, 1))
}

# ---------------------------------------------------------------------------
# Demo entry-point (wrapper around base_plot save_demo)
# ---------------------------------------------------------------------------
run_demo <- function() {
  df <- generate_mock_data()
  p  <- peri_event_raster_plot(df)
  # Use the save_demo from base_plot.R (sourced above)
  save_demo(p, name = "peri_event_raster_demo", width = 170,
            height = 140, units = "mm")
  # Also write demo TSV
  demo_dir <- file.path(template_root_dir(), "demo_data")
  dir.create(demo_dir, showWarnings = FALSE, recursive = TRUE)
  write.table(df, file = file.path(demo_dir, "peri_event_raster_demo.tsv"),
              sep = "\t", row.names = FALSE, quote = FALSE)
  message("Demo saved.")
}

# Run demo when executed with --demo flag
if ("--demo" %in% commandArgs(trailingOnly = TRUE)) {
  run_demo()
}
