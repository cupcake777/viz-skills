source(file.path(dirname(normalizePath(sub("^--file=", "", commandArgs(FALSE)[grepl("^--file=", commandArgs(FALSE))][1]))), "base_plot.R"))
suppressPackageStartupMessages(library(ggplot2))

generate_mock_data <- function(seed = 42) { set.seed(seed); vars <- paste0("V",1:8); m <- cor(matrix(rnorm(200*8),200,8)); colnames(m)<-rownames(m)<-vars; as.data.frame(as.table(m)) |> setNames(c("var1","var2","correlation_coefficient")) }
correlation_heatmap_plot <- function(df, x_col="var1", y_col="var2", value_col="correlation_coefficient", base_size=16, show_values=FALSE) {
  p <- ggplot(df, aes(.data[[x_col]], .data[[y_col]], fill=.data[[value_col]])) +
    geom_tile(colour="white", linewidth=0.35) +
    scale_fill_gradient2(low="#4575B4", mid="white", high="#D73027", limits=c(-1,1)) +
    labs(x=NULL,y=NULL,fill="r") +
    coord_equal() +
    theme_clean(base_size) +
    theme(axis.text.x=element_text(angle=45,hjust=1), legend.position="right")
  if (show_values) {
    p <- p + geom_text(aes(label=sprintf("%.2f", .data[[value_col]])), size=base_size/ggplot2::.pt)
  }
  p
}
if (sys.nframe()==0) save_demo(correlation_heatmap_plot(generate_mock_data()), "correlation_heatmap_demo", width=110, height=95)
