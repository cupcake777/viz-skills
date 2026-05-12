#' Gene Trend Heatmap Over Pseudotime
#'
#' Expression heatmap showing gene dynamics along a continuous axis
#' (pseudotime, developmental stage, dose). Genes sorted by peak
#' activation time, z-score normalized. Inspired by Palantir
#' (Setty et al., Nature Biotechnology 2019).
#'
#' Required columns: gene, bin, value
#' Optional columns: branch

suppressPackageStartupMessages({
  library(ggplot2)
})

source(file.path(dirname(sys.frame(1)$ofile), "base_plot.R"))

generate_mock_data <- function(n_genes = 30, n_bins = 100, n_branches = 3, seed = 42) {
  set.seed(seed)

  branches <- paste0("Branch_", LETTERS[1:n_branches])
  genes_per_branch <- split(
    paste0("Gene_", sprintf("%02d", 1:n_genes)),
    rep(1:n_branches, each = ceiling(n_genes / n_branches), length.out = n_genes)
  )

  rows <- list()
  for (b in seq_len(n_branches)) {
    peak_times <- runif(length(genes_per_branch[[b]]), 0.1, 0.9)
    for (g in seq_along(genes_per_branch[[b]])) {
      t <- seq(0, 1, length.out = n_bins)
      # Bell curve peaked at peak_time
      expr <- exp(-((t - peak_times[g])^2) / (2 * 0.04)) + rnorm(n_bins, 0, 0.1)
      expr <- pmax(expr, 0)
      rows[[length(rows) + 1]] <- data.frame(
        gene = genes_per_branch[[b]][g],
        bin = t,
        value = expr,
        branch = branches[b],
        stringsAsFactors = FALSE
      )
    }
  }

  df <- do.call(rbind, rows)

  # Z-score per gene
  df$zscore <- ave(df$value, df$gene, FUN = function(x) {
    s <- sd(x)
    if (s == 0) rep(0, length(x)) else (x - mean(x)) / s
  })

  df
}

plot_gene_trend_heatmap <- function(df,
                                    gene = "gene",
                                    bin = "bin",
                                    value = "zscore",
                                    branch = "branch",
                                    palette = "RdBu",
                                    base_size = 14) {

  # Sort genes by peak activation time
  peak_time <- aggregate(df[[value]], list(gene = df[[gene]]), FUN = function(v) {
    which.max(v)
  })
  names(peak_time) <- c("gene", "peak_idx")
  # Get bin value at peak
  peak_time$peak <- sapply(peak_time$gene, function(g) {
    sub <- df[df[[gene]] == g, ]
    sub[[bin]][which.max(sub[[value]])]
  })
  gene_order <- as.character(peak_time$gene[order(peak_time$peak)])
  df[[gene]] <- factor(df[[gene]], levels = gene_order)

  p <- ggplot(df, aes(x = .data[[bin]], y = .data[[gene]], fill = .data[[value]])) +
    geom_tile() +
    scale_fill_distiller(palette = palette, direction = -1,
                         name = "Z-score", limits = c(-2, 2), oob = scales::squish) +
    theme_sci(base_size = base_size) +
    theme(
      axis.text.y = element_text(size = 5, colour = "grey25"),
      axis.text.x = element_text(size = 6),
      axis.ticks = element_blank(),
      axis.line = element_blank(),
      panel.border = element_rect(color = "grey50", size = 0.3, fill = NA),
      legend.key.height = unit(8, "pt"),
      legend.key.width = unit(4, "pt")
    ) +
    labs(x = "Pseudotime", y = NULL)

  # Facet by branch if available
  if (!is.null(branch) && branch %in% names(df)) {
    p <- p + facet_grid(rows = vars(.data[[branch]]), scales = "free_y", space = "free_y")
  }

  p
}

# Demo ----
if (sys.nframe() == 0 || isTRUE(getOption("run_demo"))) {
  df <- generate_mock_data()
  p <- plot_gene_trend_heatmap(df)

  out <- template_out_dir()
  save_demo(p, name = "gene_trend_heatmap_demo", out_dir = out,
            width = 160, height = 160, units = "mm", dpi = 300)
  message("Demo saved to ", file.path(out, "gene_trend_heatmap_demo.png"))
}
