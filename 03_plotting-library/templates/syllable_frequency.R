tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))
suppressPackageStartupMessages(library(ggplot2))

# ---- Mock data generator ---------------------------------------------------
generate_mock_data <- function(n_syllables = 10, n_mice = 6, seed = 42) {
  set.seed(seed)

  syllables <- paste0("S", sprintf("%02d", seq_len(n_syllables)))
  groups    <- c("Treatment", "Control")
  mice      <- paste0("M", sprintf("%02d", seq_len(n_mice)))

  # Build complete grid: mouse x syllable x group
  grid <- expand.grid(mouse = mice, syllable = syllables, group = groups,
                      stringsAsFactors = FALSE)

  # Simulate counts with group differences on a subset of syllables
  treatment_boost <- setNames(rep(0, n_syllables), syllables)
  boosted <- sample(syllables, 4)
  treatment_boost[boosted] <- runif(4, 2, 5)

  grid$count <- mapply(function(g, s) {
    mu <- if (g == "Treatment") 8 + treatment_boost[s] else 8
    rpois(1, lambda = max(mu, 1))
  }, grid$group, grid$syllable)

  # Summarise: mean + SEM per syllable x group
  stats <- aggregate(count ~ syllable + group, data = grid, FUN = function(x) {
    c(mean_freq = mean(x), sem = sd(x) / sqrt(length(x)))
  })
  # Flatten the matrix column produced by aggregate
  stats <- data.frame(
    syllable  = stats$syllable,
    group     = stats$group,
    mean_freq = stats$count[, "mean_freq"],
    sem       = stats$count[, "sem"]
  )

  list(df = stats, raw = grid)
}

# ---- Plot function ---------------------------------------------------------
syllable_frequency_plot <- function(df, x_col = "syllable", y_col = "mean_freq",
                                    group_col = "group", sem_col = "sem",
                                    group_offsets = c(Treatment = -0.15, Control = 0.15),
                                    dodge_width = 0.3, base_size = 16,
                                    palette = NULL, show_points = TRUE,
                                    point_alpha = 0.35, x_label = NULL,
                                    y_label = "Frequency (mean \u00b1 SEM)",
                                    raw = NULL) {

  palette <- palette %||% VIZ_PALETTES$nature[1:2]
  groups  <- unique(df[[group_col]])
  names(palette) <- groups[seq_along(palette)]

  # Manual dodge: apply per-group offset
  df$x_pos <- as.numeric(factor(df[[x_col]]))
  offsets  <- group_offsets[df[[group_col]]]
  df$x_pos <- df$x_pos + offsets

  p <- ggplot(df, aes(x = x_pos, y = .data[[y_col]], colour = .data[[group_col]])) +
    geom_point(size = 2.5) +
    geom_errorbar(aes(ymin = .data[[y_col]] - .data[[sem_col]],
                       ymax = .data[[y_col]] + .data[[sem_col]]),
                  width = 0.12, linewidth = 0.45) +
    scale_colour_manual(values = palette) +
    scale_x_continuous(
      breaks = seq_along(unique(df[[x_col]])),
      labels = unique(df[[x_col]])
    ) +
    labs(x = x_label %||% "Syllable", y = y_label) +
    theme_sci(base_size = base_size, grid = TRUE) +
    theme(legend.position = "top")

  # Overlay raw individual data points if provided
  if (show_points && !is.null(raw)) {
    raw$x_pos <- as.numeric(factor(raw[[x_col]])) + group_offsets[raw[[group_col]]]
    p <- p + geom_point(data = raw, aes(x = x_pos, y = .data[["count"]]),
                         size = 1.0, alpha = point_alpha, shape = 16,
                         show.legend = FALSE)
  }

  p
}

# ---- Run demo --------------------------------------------------------------
if (sys.nframe() == 0) {
  mock <- generate_mock_data()
  save_demo(syllable_frequency_plot(mock$df), "syllable_frequency_demo")

  # Also save demo TSV
  demo_path <- file.path(template_root_dir(), "demo_data", "syllable_frequency_demo.tsv")
  dir.create(dirname(demo_path), showWarnings = FALSE, recursive = TRUE)
  write.table(mock$df, demo_path, sep = "\t", row.names = FALSE, quote = FALSE)
}
