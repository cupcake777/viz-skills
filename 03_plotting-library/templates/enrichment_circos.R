tryCatch(tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))),
         error = function(e) tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R")))
suppressPackageStartupMessages(library(ggplot2))

generate_mock_data <- function(seed=42){set.seed(seed); data.frame(term=paste("Term",1:16),pvalue=10^runif(16,-5,-1),gene_ratio=runif(16,.05,.35),count=sample(10:80,16),category=rep(c("BP","CC","MF","KEGG"),each=4))}
enrichment_circos_plot <- function(df,term_col="term",p_col="pvalue",count_col="count",cat_col="category",base_size=16){df<-df[order(df[[cat_col]],df[[p_col]]),]; df[[term_col]]<-factor(df[[term_col]],levels=df[[term_col]]); ggplot(df,aes(.data[[term_col]],.data[[count_col]],fill=.data[[cat_col]]))+geom_col(width=.8)+coord_polar()+scale_fill_manual(values=NATURE_COLORS)+labs(x=NULL,y=NULL)+theme_void(base_size=base_size)+theme(legend.position="right")}
if(sys.nframe()==0) save_demo(enrichment_circos_plot(generate_mock_data()),"enrichment_circos_demo",width=90,height=90)
