tryCatch(tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))),
         error = function(e) tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R")))
suppressPackageStartupMessages(library(ggplot2))

generate_mock_data <- function(seed=42){fpr<-seq(0,1,length.out=100); tpr<-pmin(1, fpr^.35 + sin(fpr*pi)*.03); data.frame(fpr=fpr,tpr=tpr,auc=0.86)}
roc_curve_plot <- function(df,x_col="fpr",y_col="tpr",auc_col="auc",base_size=16){auc<-if(auc_col %in% names(df)) unique(round(df[[auc_col]][1],2)) else NA; ggplot(df,aes(.data[[x_col]],.data[[y_col]]))+geom_abline(slope=1,intercept=0,linetype="22",colour="grey60",linewidth=.3)+geom_line(colour="#D73027",linewidth=.8)+annotate("text",x=.68,y=.18,label=paste0("AUC = ",auc),size=base_size/ggplot2::.pt)+coord_equal()+labs(x="False positive rate",y="True positive rate")+theme_clean(base_size)}
if(sys.nframe()==0) save_demo(roc_curve_plot(generate_mock_data()),"roc_demo")
