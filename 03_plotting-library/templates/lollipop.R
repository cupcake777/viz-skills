source(file.path(dirname(normalizePath(sub("^--file=", "", commandArgs(FALSE)[grepl("^--file=", commandArgs(FALSE))][1]))), "base_plot.R"))
suppressPackageStartupMessages({library(ggplot2); library(ggrepel)})

generate_mock_data <- function(seed = 42) {
  sites <- data.frame(position=c(72,175,220,245,248,273,282,342), count=c(3,5,12,8,28,45,15,2), type=c("Missense","Missense","Truncating","Missense","Missense","Missense","Missense","Truncating"), label=c("P72L","E175K","R220*","G245S","R248W","R273H","E285K","Q342*"))
  domains <- data.frame(start=c(1,95,290), end=c(94,289,393), domain=c("TAD", "DNA-binding", "Tetramer"))
  list(sites=sites, domains=domains, protein_length=393)
}

lollipop_plot <- function(df, domains=NULL, protein_length=NULL, pos_col="position", count_col="count", type_col="type", label_col="label", base_size=16) {
  if (is.null(protein_length)) protein_length <- max(df[[pos_col]], na.rm=TRUE) * 1.08
  domain_layer <- if (!is.null(domains)) geom_rect(data=domains, aes(xmin=start, xmax=end, ymin=-max(df[[count_col]])*.08, ymax=-max(df[[count_col]])*.03, fill=domain), inherit.aes=FALSE, alpha=.85) else NULL
  label_df <- df[order(df[[count_col]], decreasing=TRUE)[seq_len(min(6,nrow(df)))],]
  ggplot(df, aes(.data[[pos_col]], .data[[count_col]], colour=.data[[type_col]])) +
    domain_layer +
    geom_segment(aes(xend=.data[[pos_col]], y=0, yend=.data[[count_col]]), linewidth=.45) +
    geom_point(size=2.1) +
    ggrepel::geom_text_repel(data=label_df, aes(label=.data[[label_col]]), size=base_size/ggplot2::.pt, min.segment.length=0, segment.size=.18, show.legend=FALSE) +
    scale_colour_manual(values=NATURE_COLORS) + scale_fill_manual(values=NATURE_COLORS, guide="none") +
    coord_cartesian(xlim=c(0, protein_length), clip="off") + labs(x="Amino acid position", y="Mutation count") + theme_clean(base_size) + theme(legend.position="top")
}

if (sys.nframe()==0) { d<-generate_mock_data(); save_demo(lollipop_plot(d$sites,d$domains,d$protein_length), "lollipop_demo", width=120, height=70) }
