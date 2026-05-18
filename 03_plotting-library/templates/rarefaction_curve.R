#' Rarefaction Curve (Species Accumulation by Subsampling)
#'
#' Rarefaction curves showing expected species richness as a function of
#' sampling effort. Uses manual repeated subsampling (no vegan dependency)
#' to estimate mean richness and 95% confidence intervals at each depth.
#' Based on Hurlbert (1971) and Gotelli & Colwell (2001, Ecology Letters).
#'
#' @param data  A data frame produced by `generate_mock_data()` or equivalent,
#'   with columns: sample_size, species_richness, group.
#' @param group_col  Column name identifying groups / sites.
#' @param ci_level  Confidence interval level for the ribbon (default 0.95).

suppressPackageStartupMessages({
  library(ggplot2)
})

# ── Source base_plot.R ─────────────────────────────────────────────────────────
tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))

# ── Mock data generator ──────────────────────────────────────────────────────
generate_mock_data <- function(n_groups = 4,
                               n_species = c(120, 95, 150, 80),
                               n_samples = c(500, 350, 600, 250),
                               group_names = c("Forest", "Grassland",
                                               "Wetland", "Desert"),
                               n_steps = 30,
                               n_reps = 100,
                               seed = 42) {
  set.seed(seed)
  n_groups <- min(n_groups, length(group_names))

  # Build a species pool per group and draw an abundance vector
  # for each, then subsample repeatedly at each depth.
  results <- vector("list", n_groups)

  for (g in seq_len(n_groups)) {
    S <- n_species[g]
    N <- n_samples[g]

    # Log-normal relative abundances for the species pool
    abund <- sort(rlnorm(S, meanlog = 2, sdlog = 1.5), decreasing = TRUE)
    abund <- abund / sum(abund)   # proportions

    # Pre-draw the full community of N individuals
    community <- sample(seq_len(S), size = N, replace = TRUE, prob = abund)

    # Subsampling depths (evenly spaced from small to N)
    depths <- unique(round(seq(5, N, length.out = n_steps)))

    richness_mat <- matrix(NA_integer_, nrow = length(depths), ncol = n_reps)

    for (i in seq_along(depths)) {
      d <- depths[i]
      for (r in seq_len(n_reps)) {
        drawn <- sample(community, size = d, replace = FALSE)
        richness_mat[i, r] <- length(unique(drawn))
      }
    }

    results[[g]] <- data.frame(
      group            = group_names[g],
      sample_size      = depths,
      species_richness = rowMeans(richness_mat),
      richness_sd      = apply(richness_mat, 1, sd),
      richness_lower   = apply(richness_mat, 1, quantile, probs = 0.025),
      richness_upper   = apply(richness_mat, 1, quantile, probs = 0.975),
      stringsAsFactors = FALSE
    )
  }

  do.call(rbind, results)
}

# ── Plotting function ────────────────────────────────────────────────────────
plot_rarefaction <- function(df,
                             group_col = "group",
                             ci_level = 0.95,
                             base_size = 14,
                             color_palette = NULL) {

  color_palette <- color_palette %||% NATURE_COLORS

  groups <- unique(df[[group_col]])
  pal <- setNames(color_palette[seq_along(groups)], groups)

  # Compute ribbon bounds (if not already present in df)
  if (!"richness_lower" %in% names(df) || !"richness_upper" %in% names(df)) {
    z <- qnorm(1 - (1 - ci_level) / 2)
    df$richness_lower <- df$species_richness - z * df$richness_sd
    df$richness_upper <- df$species_richness + z * df$richness_sd
    df$richness_lower <- pmax(df$richness_lower, 1)
  }

  p <- ggplot(df, aes(x = sample_size,
                       y = species_richness,
                       color = .data[[group_col]],
                       fill  = .data[[group_col]])) +
    geom_ribbon(aes(ymin = richness_lower, ymax = richness_upper),
                alpha = 0.18, colour = NA) +
    geom_line(size = 0.8) +
    geom_point(size = 1.2) +
    scale_color_manual(values = pal) +
    scale_fill_manual(values = pal) +
    theme_sci(base_size = base_size) +
    theme(
      legend.position = "right",
      legend.key.height = unit(10, "pt")
    ) +
    labs(
      x     = "Sample Size (Number of Individuals)",
      y     = "Observed Species Richness",
      color = "Site",
      fill  = "Site"
    )

  p
}

# ── Demo block ───────────────────────────────────────────────────────────────
if (sys.nframe() == 0 || isTRUE(getOption("run_demo"))) {
  message(">>> rarefaction_curve demo")

  df <- generate_mock_data()
  p  <- plot_rarefaction(df)

  out <- template_out_dir()
  save_demo(p, name = "rarefaction_curve_demo", out_dir = out,
            width = 160, height = 110, units = "mm", dpi = 300)
  message("Demo saved to ", file.path(out, "rarefaction_curve_demo.png"))
}
