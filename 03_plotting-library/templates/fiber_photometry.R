#' Fiber Photometry Z-Score Heatmap
#'
#' Multi-trial z-score heatmap for fiber photometry GCaMP data.
#' Produces side-by-side Vehicle vs Drug panels via patchwork.
#' Supports per-mouse min-max normalization and event detection overlay.
#'
#' Based on GLP-1R reward circuit calcium imaging analysis.
#'
#' Required columns: time, mouse, z_score, condition
#' Condition levels: "Vehicle", "Drug"
#'
#' Features:
#' - geom_tile heatmap with scale_fill_gradient2 (fixed z-range)
#' - Per-mouse sorted-extreme normalization (not global min/max)
#' - Event detection: highlight regions where z > threshold for >= min_duration
#' - patchwork side-by-side Vehicle | Drug layout

tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))

suppressPackageStartupMessages({
  library(ggplot2)
  library(patchwork)
})

# Version-safe theme_sci: ggplot2 < 3.4 uses 'size' not 'linewidth'
if (packageVersion("ggplot2") < "3.4.0") {
  theme_sci <- function(base_size = 16, base_family = "Arial", grid = FALSE) {
    th <- theme_classic(base_size = base_size, base_family = base_family) +
      theme(
        axis.line = element_line(size = 0.35, colour = "grey25"),
        axis.ticks = element_line(size = 0.3, colour = "grey25"),
        axis.text = element_text(colour = "grey25"),
        legend.title = element_blank(),
        legend.key.height = unit(8, "pt"),
        legend.key.width = unit(10, "pt"),
        plot.title = element_blank(),
        plot.subtitle = element_blank(),
        plot.margin = margin(5, 6, 5, 5, "pt")
      )
    if (grid) {
      th <- th + theme(
        panel.grid.major = element_line(colour = "grey90", size = 0.25),
        panel.grid.minor = element_blank()
      )
    }
    th
  }
}

# ---------------------------------------------------------------------------
# Mock data generator
# ---------------------------------------------------------------------------

generate_mock_data <- function(n_mice = 8, n_timepoints = 200, seed = 42) {
  set.seed(seed)
  time_vec <- seq(-10, 20, length.out = n_timepoints)
  mice <- paste0("Mouse_", sprintf("%02d", 1:n_mice))
  conditions <- c("Vehicle", "Drug")

  rows <- list()
  for (m in mice) {
    for (cond in conditions) {
      # Baseline noise
      z <- rnorm(n_timepoints, mean = 0, sd = 0.8)

      # Drug condition: add a calcium transient event around t=2..6
      if (cond == "Drug") {
        event_mask <- time_vec >= 2 & time_vec <= 6
        # Variable onset per mouse for realism
        onset_shift <- runif(1, -1, 1)
        event_mask <- time_vec >= (2 + onset_shift) & time_vec <= (6 + onset_shift)
        event_amp <- runif(1, 2.5, 5.0)
        z[event_mask] <- z[event_mask] + event_amp * dnorm(
          time_vec[event_mask],
          mean = (4 + onset_shift),
          sd = 0.8
        ) / dnorm(0, 0, 0.8)
      }

      # Vehicle: occasional small noise bump
      if (cond == "Vehicle" && runif(1) > 0.5) {
        bump_center <- runif(1, -5, 15)
        bump_mask <- time_vec >= (bump_center - 1) & time_vec <= (bump_center + 1)
        z[bump_mask] <- z[bump_mask] + runif(1, 0.5, 1.5) *
          dnorm(time_vec[bump_mask], bump_center, 0.5) / dnorm(0, 0, 0.5)
      }

      rows[[length(rows) + 1]] <- data.frame(
        time      = time_vec,
        mouse     = m,
        z_score   = z,
        condition = cond,
        stringsAsFactors = FALSE
      )
    }
  }
  all_df <- do.call(rbind, rows)

  # Return named list so render_wrapper can spread as vehicle_df + drug_df
  # (normalization is applied inside fiber_photometry_plot)
  list(vehicle_df = all_df[all_df$condition == "Vehicle", ],
       drug_df    = all_df[all_df$condition == "Drug", ])
}

# ---------------------------------------------------------------------------
# Per-mouse min-max normalization using sorted extreme N values
# ---------------------------------------------------------------------------

normalize_per_mouse <- function(df, z_col = "z_score", mouse_col = "mouse",
                                 n_extreme = 10) {
  df[[z_col]] <- ave(df[[z_col]], df[[mouse_col]], FUN = function(x) {
    sorted <- sort(x)
    n <- min(n_extreme, length(sorted) %/% 2)
    lo <- mean(head(sorted, n))
    hi <- mean(tail(sorted, n))
    if (hi == lo) return(rep(0, length(x)))
    (x - lo) / (hi - lo) * 8 - 4   # map to [-4, 4]
  })
  df
}

# ---------------------------------------------------------------------------
# Event detection: highlight contiguous regions above threshold
# ---------------------------------------------------------------------------

detect_events <- function(df, z_col = "z_score", time_col = "time",
                           mouse_col = "mouse", condition_col = "condition",
                           threshold = 2.0, min_duration = 0.5) {
  events <- list()
  for (m in unique(df[[mouse_col]])) {
    for (cond in unique(df[[condition_col]])) {
      sub <- df[df[[mouse_col]] == m & df[[condition_col]] == cond, ]
      sub <- sub[order(sub[[time_col]]), ]
      above <- sub[[z_col]] > threshold
      # Find contiguous runs
      rle_above <- rle(above)
      cum_pos <- cumsum(rle_above$lengths)
      starts <- c(1, cum_pos[-length(cum_pos)] + 1)
      for (i in seq_along(rle_above$values)) {
        if (!rle_above$values[i]) next
        idx_start <- starts[i]
        idx_end   <- cum_pos[i]
        t_start <- sub[[time_col]][idx_start]
        t_end   <- sub[[time_col]][idx_end]
        dur <- t_end - t_start
        if (dur >= min_duration) {
          events[[length(events) + 1]] <- data.frame(
            mouse     = m,
            condition = cond,
            t_start   = t_start,
            t_end     = t_end,
            duration  = dur,
            peak_z    = max(sub[[z_col]][idx_start:idx_end]),
            stringsAsFactors = FALSE
          )
        }
      }
    }
  }
  if (length(events) == 0) return(NULL)
  do.call(rbind, events)
}

# ---------------------------------------------------------------------------
# Main plotting function
# ---------------------------------------------------------------------------

fiber_photometry_plot <- function(
    vehicle_df,
    drug_df,
    time_col        = "time",
    mouse_col       = "mouse",
    z_col           = "z_score",
    condition_col   = "condition",
    z_range         = c(-4, 4),
    event_threshold = 2.0,
    min_duration    = 0.5,
    show_events     = TRUE,
    base_size       = 12
) {
  # Combine for event detection
  combined <- rbind(vehicle_df, drug_df)

  # Build heatmap panel for one condition
  build_panel <- function(df, panel_title) {
    # Order mice by mean z-score in event window (descending)
    event_window <- df[df[[time_col]] >= 2 & df[[time_col]] <= 6, ]
    if (nrow(event_window) > 0) {
      mouse_rank <- tapply(event_window[[z_col]], event_window[[mouse_col]], mean)
      mouse_order <- names(sort(mouse_rank, decreasing = TRUE))
    } else {
      mouse_order <- sort(unique(df[[mouse_col]]))
    }
    df[[mouse_col]] <- factor(df[[mouse_col]], levels = mouse_order)

    p <- ggplot(df, aes(x = .data[[time_col]], y = .data[[mouse_col]],
                         fill = .data[[z_col]])) +
      geom_tile(width = diff(range(df[[time_col]])) / length(unique(df[[time_col]])),
                height = 0.9) +
      scale_fill_gradient2(
        low = "#4575B4", mid = "white", high = "#D73027",
        limits = z_range, oob = scales::squish,
        name = "z-score"
      ) +
      labs(x = "Time (s)", y = NULL) +
      theme_sci(base_size = base_size) +
      theme(
        axis.text.y     = element_text(size = rel(0.65)),
        axis.ticks.y    = element_blank(),
        axis.text.x     = element_text(size = rel(0.7)),
        legend.key.height = unit(20, "pt"),
        legend.key.width  = unit(6, "pt"),
        plot.margin     = margin(5, 12, 5, 5, "pt"),
        plot.title      = element_text(size = base_size, hjust = 0.5,
                                        face = "bold", margin = margin(b = 4))
      ) +
      ggtitle(panel_title)

    # Event detection overlay
    if (show_events) {
      evt <- detect_events(df, z_col = z_col, time_col = time_col,
                           mouse_col = mouse_col, condition_col = condition_col,
                           threshold = event_threshold, min_duration = min_duration)
      if (!is.null(evt) && nrow(evt) > 0) {
        evt[[mouse_col]] <- factor(evt[[mouse_col]], levels = mouse_order)
        p <- p +
          geom_rect(data = evt,
                    aes(xmin = t_start, xmax = t_end,
                        ymin = as.numeric(.data[[mouse_col]]) - 0.45,
                        ymax = as.numeric(.data[[mouse_col]]) + 0.45),
                    inherit.aes = FALSE,
                    fill = NA, color = "black", size = 0.5, linetype = "dashed")
      }
    }
    p
  }

  p_vehicle <- build_panel(vehicle_df, "Vehicle")
  p_drug    <- build_panel(drug_df, "Drug")

  # patchwork side-by-side
  p_vehicle + p_drug +
    plot_layout(guides = "collect", widths = c(1, 1)) &
    theme(legend.position = "right")
}

# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

save_demo <- save_demo  # alias from base_plot.R

if (sys.nframe() == 0 || isTRUE(getOption("run_demo"))) {
  # Generate and export demo TSV (returns named list)
  mock <- generate_mock_data()
  all_df <- rbind(mock$vehicle_df, mock$drug_df)
  demo_path <- file.path(template_root_dir(), "demo_data", "fiber_photometry_demo.tsv")
  dir.create(dirname(demo_path), showWarnings = FALSE, recursive = TRUE)
  write.table(all_df, file = demo_path, sep = "\t", row.names = FALSE, quote = FALSE)
  message("Demo data saved to ", demo_path)

  # Normalize per mouse
  vehicle_df <- normalize_per_mouse(mock$vehicle_df)
  drug_df    <- normalize_per_mouse(mock$drug_df)

  # Plot
  p <- fiber_photometry_plot(vehicle_df, drug_df)

  out <- template_out_dir()
  save_figure(p, name = "fiber_photometry_demo", out_dir = out,
              width = 200, height = 120, units = "mm", dpi = 300)
  message("Demo figure saved to ", out)
}
