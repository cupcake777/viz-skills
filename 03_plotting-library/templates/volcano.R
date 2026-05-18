#' Volcano Plot
#'
#' R-first volcano template for differential expression / differential signal
#' results. Designed as a reusable house-style template rather than a port of
#' the older Python demo.
#'
#' Required columns: log2FC, pvalue
#' Optional columns: gene_label, qvalue

suppressPackageStartupMessages({
  library(ggplot2)
  library(ggrepel)
})

tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))

SAFE_COLORS <- c(
  up = "#D73027",
  down = "#4575B4",
  ns = "#D8DCE2"
)

generate_mock_data <- function(n = 3000, seed = 42) {
  set.seed(seed)

  log2fc <- rnorm(n, mean = 0, sd = 1.15)
  pvalue <- runif(n, min = 1e-2, max = 1)

  n_sig <- round(n * 0.12)
  sig_idx <- sample(seq_len(n), n_sig)
  up_idx <- sig_idx[seq_len(floor(n_sig / 2))]
  down_idx <- setdiff(sig_idx, up_idx)

  log2fc[up_idx] <- log2fc[up_idx] + runif(length(up_idx), 1.4, 3.3)
  log2fc[down_idx] <- log2fc[down_idx] - runif(length(down_idx), 1.4, 3.3)
  pvalue[sig_idx] <- 10 ^ runif(n_sig, min = -9, max = -2)

  data.frame(
    gene_label = paste0("Gene_", seq_len(n)),
    log2FC = log2fc,
    pvalue = pvalue,
    stringsAsFactors = FALSE
  )
}

theme_volcano <- function(base_size = 16) {
  theme_sci(base_size = base_size) +
    theme(
      legend.position = "top",
      legend.justification = "right",
      plot.margin = margin(5, 10, 5, 5, "pt")
    )
}

classify_volcano <- function(df, fc_col, p_col, fc_threshold, p_threshold) {
  df$neg_log10_p <- -log10(pmax(df[[p_col]], 1e-300))
  df$direction <- "ns"
  df$direction[df[[fc_col]] >= fc_threshold & df[[p_col]] <= p_threshold] <- "up"
  df$direction[df[[fc_col]] <= -fc_threshold & df[[p_col]] <= p_threshold] <- "down"
  df$direction <- factor(df$direction, levels = c("down", "up", "ns"))
  df
}

select_labels <- function(df, fc_col, label_col, top_n) {
  if (is.null(label_col) || !label_col %in% names(df) || top_n <= 0) {
    return(df[0, , drop = FALSE])
  }

  sig <- df[df$direction != "ns" & !is.na(df[[label_col]]), , drop = FALSE]
  if (nrow(sig) == 0) {
    return(sig)
  }

  sig$label_score <- sig$neg_log10_p * pmax(abs(sig[[fc_col]]), 0.25)
  per_side <- ceiling(top_n / 2)
  down <- sig[sig$direction == "down", , drop = FALSE]
  up <- sig[sig$direction == "up", , drop = FALSE]
  down <- down[order(down$label_score, decreasing = TRUE), , drop = FALSE]
  up <- up[order(up$label_score, decreasing = TRUE), , drop = FALSE]
  labels <- rbind(
    down[seq_len(min(per_side, nrow(down))), , drop = FALSE],
    up[seq_len(min(per_side, nrow(up))), , drop = FALSE]
  )
  labels[order(labels$label_score, decreasing = TRUE), , drop = FALSE]
}

volcano_plot <- function(
    df,
    fc_col = "log2FC",
    p_col = "pvalue",
    label_col = "gene_label",
    fc_threshold = 1,
    p_threshold = 0.05,
    top_n = 4,
    base_size = 16,
    point_size = 0.75,
    point_alpha = 0.78,
    label_size = NULL,
    colors = SAFE_COLORS,
    show_counts = TRUE,
    xlab = expression(log[2]~fold~change),
    ylab = expression(-log[10]~italic(P)),
    x_limits = NULL
) {
  stopifnot(fc_col %in% names(df), p_col %in% names(df))

  df <- classify_volcano(df, fc_col, p_col, fc_threshold, p_threshold)
  labels <- select_labels(df, fc_col, label_col, top_n)

  if (is.null(label_size)) {
    label_size <- base_size / ggplot2::.pt
  }

  if (is.null(x_limits)) {
    max_abs <- max(abs(df[[fc_col]]), na.rm = TRUE)
    x_limits <- c(-max_abs, max_abs) * 1.10
  }

  legend_labels <- c(
    down = if (show_counts) sprintf("Down (%d)", sum(df$direction == "down")) else "Down",
    up = if (show_counts) sprintf("Up (%d)", sum(df$direction == "up")) else "Up",
    ns = if (show_counts) sprintf("NS (%d)", sum(df$direction == "ns")) else "NS"
  )

  ggplot(df, aes(x = .data[[fc_col]], y = neg_log10_p)) +
    geom_point(
      aes(colour = direction),
      size = point_size,
      alpha = point_alpha,
      stroke = 0
    ) +
    geom_vline(
      xintercept = c(-fc_threshold, fc_threshold),
      colour = "grey55",
      linewidth = 0.28,
      linetype = "22"
    ) +
    geom_hline(
      yintercept = -log10(p_threshold),
      colour = "grey55",
      linewidth = 0.28,
      linetype = "22"
    ) +
    ggrepel::geom_text_repel(
      data = labels,
      aes(label = .data[[label_col]]),
      size = label_size,
      min.segment.length = 0,
      segment.size = 0.2,
      segment.alpha = 0.65,
      box.padding = 0.55,
      point.padding = 0.22,
      force = 3.0,
      force_pull = 0.2,
      max.overlaps = 20,
      xlim = c(x_limits[1] * 0.92, x_limits[2] * 0.92),
      seed = 42,
      show.legend = FALSE
    ) +
    scale_colour_manual(
      values = colors,
      breaks = c("down", "up", "ns"),
      labels = legend_labels
    ) +
    scale_x_continuous(limits = x_limits, expand = expansion(mult = c(0.02, 0.02))) +
    scale_y_continuous(expand = expansion(mult = c(0.01, 0.22))) +
    labs(x = xlab, y = ylab) +
    guides(colour = guide_legend(override.aes = list(size = 2.8, alpha = 1))) +
    theme_volcano(base_size = base_size)
}

save_volcano <- function(
    plot,
    name = "volcano_demo",
    out_dir = ".",
    width = 140,
    height = 105,
    units = "mm",
    dpi = 300,
    bg = "white"
) {
  dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
  pdf_path <- file.path(out_dir, paste0(name, ".pdf"))
  png_path <- file.path(out_dir, paste0(name, ".png"))

  ggsave(pdf_path, plot, width = width, height = height, units = units, dpi = dpi,
         device = cairo_pdf, bg = bg)
  ggsave(png_path, plot, width = width, height = height, units = units, dpi = dpi,
         bg = bg)
  invisible(c(pdf = pdf_path, png = png_path))
}

if (sys.nframe() == 0) {
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- sub("^--file=", "", args[grepl("^--file=", args)])
  script_dir <- if (length(file_arg) > 0) dirname(normalizePath(file_arg[1])) else getwd()
  out_dir <- file.path(dirname(script_dir), "demo_fig")

  demo <- generate_mock_data()

  p_pub <- volcano_plot(demo, top_n = 4, base_size = 16)
  save_volcano(p_pub, name = "volcano_demo", out_dir = out_dir)
}
