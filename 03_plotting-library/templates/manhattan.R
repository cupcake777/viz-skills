source(file.path(dirname(normalizePath(sub("^--file=", "", commandArgs(FALSE)[grepl("^--file=", commandArgs(FALSE))][1]))), "base_plot.R"))
suppressPackageStartupMessages({library(ggplot2); library(ggrepel)})

generate_mock_data <- function(seed = 42) {
  set.seed(seed); chr <- rep(1:22, each = 350); pos <- unlist(lapply(rep(350,22), function(n) sort(sample(1:1e8, n))))
  p <- runif(length(chr)); idx <- sample(seq_along(p), 35); p[idx] <- 10 ^ runif(35, -9, -5)
  data.frame(chr = chr, pos = pos, pvalue = p, snp_id = paste0("rs", seq_along(p)))
}

manhattan_plot <- function(df, chr_col = "chr", pos_col = "pos", p_col = "pvalue", label_col = "snp_id", base_size = 16) {
  df <- df[order(df[[chr_col]], df[[pos_col]]), ]; chr_levels <- unique(df[[chr_col]])
  offsets <- c(0, cumsum(as.numeric(tapply(df[[pos_col]], df[[chr_col]], max)))[-length(chr_levels)])
  names(offsets) <- chr_levels; df$x <- df[[pos_col]] + offsets[as.character(df[[chr_col]])]; df$nlp <- -log10(pmax(df[[p_col]], 1e-300))
  centers <- aggregate(x ~ get(chr_col), df, function(z) mean(range(z))); names(centers) <- c("chr", "x")
  labs <- df[order(df$nlp, decreasing = TRUE)[1:8], ]
  ggplot(df, aes(x, nlp, colour = factor(.data[[chr_col]] %% 2))) +
    geom_point(size = 0.35, alpha = 0.72) + geom_hline(yintercept = -log10(5e-8), linetype = "22", linewidth = 0.3, colour = "#D73027") +
    ggrepel::geom_text_repel(data = labs, aes(label = .data[[label_col]]), size = base_size / ggplot2::.pt, min.segment.length = 0, segment.size = 0.18, show.legend = FALSE) +
    scale_colour_manual(values = c("#4B5563", "#9CA3AF"), guide = "none") + scale_x_continuous(breaks = centers$x, labels = centers$chr, expand = expansion(mult = c(0.01, 0.01))) +
    labs(x = "Chromosome", y = expression(-log[10]~italic(P))) + theme_clean(base_size)
}

if (sys.nframe() == 0) save_demo(manhattan_plot(generate_mock_data()), "manhattan_demo", width = 180, height = 85)
