tryCatch(tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))),
         error = function(e) tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R")))
suppressPackageStartupMessages(library(ggplot2))

generate_mock_data <- function(seed=42){set.seed(seed); group<-rep(paste0("Cluster ",1:5),each=120); th<-runif(length(group),0,2*pi); r<-rep(c(1,1.5,2,1.2,1.8),each=120); data.frame(UMAP1=r*cos(th)+rnorm(length(group),0,.25),UMAP2=r*sin(th)+rnorm(length(group),0,.25),group_label=group)}
umap_plot <- function(df,x_col="UMAP1",y_col="UMAP2",group_col="group_label",base_size=16){ggplot(df,aes(.data[[x_col]],.data[[y_col]],colour=.data[[group_col]]))+geom_point(size=.45,alpha=.75)+scale_colour_manual(values=NATURE_COLORS)+labs(x="UMAP1",y="UMAP2")+theme_clean(base_size)+theme(legend.position="right")}
if(sys.nframe()==0) save_demo(umap_plot(generate_mock_data()),"umap_demo")
