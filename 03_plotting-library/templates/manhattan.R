#' Manhattan Plot
#'
#' R-first Manhattan plot template for GWAS results.
#' Uses gene names (not variant IDs) as labels, ggrepel for overlap avoidance,
#' and extended y-axis headroom to prevent label crowding at the top.
#'
#' Required columns: chr, pos, pvalue
#' Optional columns: gene (gene name for labels)

tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))
suppressPackageStartupMessages({library(ggplot2); library(ggrepel)})

generate_mock_data <- function(seed = 42) {
  set.seed(seed)
  chr <- rep(1:22, each = 350)
  pos <- unlist(lapply(rep(350, 22), function(n) sort(sample(1:1e8, n))))
  p <- runif(length(chr))
  idx <- sample(seq_along(p), 35)
  p[idx] <- 10 ^ runif(35, -9, -5)

  # Use meaningful gene names instead of rs IDs
  gene_pool <- c(
    "BRCA1", "TP53", "EGFR", "MYC", "KRAS", "PTEN", "APC", "RB1",
    "BRAF", "PIK3CA", "NF1", "CDKN2A", "SMAD4", "VHL", "MLH1",
    "ATM", "CHEK2", "PALB2", "RAD51", "ERBB2", "FGFR1", "MET",
    "NOTCH1", "CTNNB1", "AKT1", "MAP3K1", "CDH1", "FBXW7",
    "STK11", "TSC1", "ARID1A", "KDM5C", "NFE2L2", "KEAP1", "ARID2"
  )

  data.frame(
    chr = chr,
    pos = pos,
    pvalue = p,
    gene = rep(gene_pool, length.out = length(p)),
    stringsAsFactors = FALSE
  )
}

manhattan_plot <- function(
    df,
    chr_col = "chr",
    pos_col = "pos",
    p_col = "pvalue",
    label_col = "gene",
    sig_threshold = 5e-8,
    top_n = 8,
    base_size = 16,
    label_size = NULL,
    colors = c("#4B5563", "#9CA3AF"),
    xlab = "Chromosome",
    ylab = expression(-log[10]~italic(P))
) {
  df <- df[order(df[[chr_col]], df[[pos_col]]), ]
  chr_levels <- unique(df[[chr_col]])

  offsets <- c(0, cumsum(as.numeric(tapply(df[[pos_col]], df[[chr_col]], max)))[-length(chr_levels)])
  names(offsets) <- chr_levels
  df$x <- df[[pos_col]] + offsets[as.character(df[[chr_col]])]
  df$nlp <- -log10(pmax(df[[p_col]], 1e-300))

  centers <- aggregate(x ~ get(chr_col), df, function(z) mean(range(z)))
  names(centers) <- c("chr", "x")

  # Select top-N significant points for labelling
  top_peaks <- df[order(df$nlp, decreasing = TRUE)[1:min(top_n, nrow(df))], ]

  if (is.null(label_size)) {
    label_size <- base_size / ggplot2::.pt * 1.05
  }

  ggplot(df, aes(x, nlp)) +
    geom_point(aes(colour = factor(.data[[chr_col]] %% 2)), size = 0.35, alpha = 0.72) +
    geom_hline(
      yintercept = -log10(sig_threshold),
      linetype = "22", linewidth = 0.3, colour = "#D73027"
    ) +
    ggrepel::geom_text_repel(
      data = top_peaks,
      aes(x = x, y = nlp, label = .data[[label_col]]),
      size = label_size,
      min.segment.length = 0,
      segment.size = 0.18,
      box.padding = 0.5,
      point.padding = 0.2,
      force = 2.5,
      force_pull = 0.15,
      max.overlaps = 15,
      seed = 42,
      show.legend = FALSE
    ) +
    scale_colour_manual(values = colors, guide = "none") +
    scale_x_continuous(
      breaks = centers$x,
      labels = centers$chr,
      expand = expansion(mult = c(0.01, 0.01))
    ) +
    scale_y_continuous(expand = expansion(mult = c(0.02, 0.18))) +
    labs(x = xlab, y = ylab) +
    theme_sci(base_size = base_size) +
    theme(legend.position = "none")
}

if (sys.nframe() == 0) {
  save_demo(manhattan_plot(generate_mock_data()), "manhattan_demo", width = 180, height = 85)
}