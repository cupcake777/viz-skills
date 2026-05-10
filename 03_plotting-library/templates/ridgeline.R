source(file.path(dirname(normalizePath(sub("^--file=", "", commandArgs(FALSE)[grepl("^--file=", commandArgs(FALSE))][1]))), "base_plot.R"))
suppressPackageStartupMessages(library(ggplot2))

generate_mock_data <- function(seed=42){set.seed(seed); groups<-rep(paste0("Stage ",1:6),each=160); data.frame(group=groups,value=rnorm(length(groups),rep(seq(-1,1,length.out=6),each=160),.55))}
ridgeline_plot <- function(df, group_col="group", value_col="value", base_size=16) {
  groups <- unique(df[[group_col]])
  dens <- do.call(rbind, lapply(seq_along(groups), function(i) {
    x <- df[[value_col]][df[[group_col]] == groups[i]]
    d <- density(x, n=180)
    data.frame(group=groups[i], x=d$x, density=d$y / max(d$y) * 0.78, y=i)
  }))
  dens$group <- factor(dens$group, levels=groups)
  ggplot(dens, aes(x=x, y=y, group=group, fill=group)) +
    geom_ribbon(aes(ymin=y, ymax=y+density), alpha=0.72, colour=NA) +
    geom_line(aes(y=y+density), linewidth=0.45, colour="grey25") +
    scale_y_continuous(breaks=seq_along(groups), labels=groups, expand=expansion(add=c(0.15,1.0))) +
    scale_fill_manual(values=NATURE_COLORS) +
    labs(x="Value", y=NULL) +
    theme_clean(base_size) +
    theme(legend.position="none", axis.line.y=element_blank(), axis.ticks.y=element_blank())
}
if(sys.nframe()==0) save_demo(ridgeline_plot(generate_mock_data()),"ridgeline_demo", width=120, height=95)
