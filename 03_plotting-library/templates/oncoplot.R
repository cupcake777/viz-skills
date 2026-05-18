tryCatch(tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))),
         error = function(e) tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R")))
suppressPackageStartupMessages(library(ggplot2))

generate_mock_data <- function(seed = 42) {
  set.seed(seed); samples <- paste0("S", sprintf("%02d", 1:36)); genes <- c("TP53","KRAS","BRAF","PIK3CA","APC","SMAD4","PTEN","EGFR","NF1","CDKN2A"); freq <- c(.75,.55,.48,.35,.30,.25,.20,.18,.12,.08); types <- c("Missense","Nonsense","Frame shift","Splice","In-frame","Multi-hit")
  rows <- list(); k <- 1
  for (i in seq_along(genes)) { for (s in sample(samples, round(length(samples)*freq[i]))) { rows[[k]] <- data.frame(sample=s, gene=genes[i], mutation_type=sample(types,1)); k<-k+1 } }
  do.call(rbind, rows)
}

oncoplot <- function(df, sample_col="sample", gene_col="gene", type_col="mutation_type", top_n=10, base_size=16) {
  top_genes <- names(sort(table(df[[gene_col]]), decreasing=TRUE))[seq_len(min(top_n, length(unique(df[[gene_col]]))))]
  df <- df[df[[gene_col]] %in% top_genes,]
  sample_order <- names(sort(table(df[[sample_col]]), decreasing=TRUE))
  df[[sample_col]] <- factor(df[[sample_col]], levels=sample_order)
  df[[gene_col]] <- factor(df[[gene_col]], levels=rev(top_genes))
  ggplot(df, aes(.data[[sample_col]], .data[[gene_col]], fill=.data[[type_col]])) +
    geom_tile(width=.92, height=.82, colour="white", linewidth=.12) +
    scale_fill_manual(values=NATURE_COLORS) + labs(x=NULL, y=NULL) +
    theme_clean(base_size) + theme(axis.text.x=element_blank(), axis.ticks.x=element_blank(), legend.position="top", panel.background=element_rect(fill="#F5F5F5", colour=NA))
}

if (sys.nframe()==0) save_demo(oncoplot(generate_mock_data()), "oncoplot_demo", width=125, height=72)
