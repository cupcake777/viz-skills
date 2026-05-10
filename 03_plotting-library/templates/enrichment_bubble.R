source(file.path(dirname(normalizePath(sub("^--file=", "", commandArgs(FALSE)[grepl("^--file=", commandArgs(FALSE))][1]))), "base_plot.R"))
suppressPackageStartupMessages(library(ggplot2))

generate_mock_data <- function(seed = 42) {
  set.seed(seed)
  terms <- paste("Pathway", LETTERS[1:12])
  data.frame(term = terms, pvalue = 10 ^ runif(12, -6, -1), gene_ratio = runif(12, 0.05, 0.35), count = sample(8:80, 12))
}

enrichment_bubble_plot <- function(df, term_col = "term", p_col = "pvalue", ratio_col = "gene_ratio", count_col = "count", top_n = 12, base_size = 16) {
  df <- df[order(df[[p_col]]), ][seq_len(min(top_n, nrow(df))), ]
  df[[term_col]] <- factor(df[[term_col]], levels = rev(df[[term_col]]))
  ggplot(df, aes(.data[[ratio_col]], .data[[term_col]])) +
    geom_point(aes(size = .data[[count_col]], colour = -log10(.data[[p_col]])), alpha = 0.88) +
    scale_colour_gradient(low = "#4DBBD5", high = "#E64B35") +
    scale_size_continuous(range = c(1.2, 4.8)) +
    labs(x = "Gene ratio", y = NULL, colour = expression(-log[10]~italic(P)), size = "Count") +
    theme_clean(base_size) + theme(legend.position = "right")
}

if (sys.nframe() == 0) save_demo(enrichment_bubble_plot(generate_mock_data()), "enrichment_bubble_demo", width = 105, height = 78)
