source(file.path(dirname(normalizePath(sub("^--file=", "", commandArgs(FALSE)[grepl("^--file=", commandArgs(FALSE))][1]))), "base_plot.R"))
suppressPackageStartupMessages(library(ggplot2))

generate_mock_data <- function(seed=42){set.seed(seed); sets<-c("eQTL","sQTL","apaQTL","GWAS"); els<-paste0("Gene",1:300); do.call(rbind,lapply(els,function(e){data.frame(element=e,set_membership=sample(sets,sample(1:3,1))) }))}
upset_plot <- function(df, element_col="element", set_col="set_membership", base_size=16){combo<-aggregate(df[[set_col]],list(element=df[[element_col]]),function(x)paste(sort(unique(x)),collapse=" & ")); names(combo)<-c("element","combo"); tab<-sort(table(combo$combo),decreasing=TRUE); dd<-data.frame(combo=factor(names(tab),levels=rev(names(tab))),count=as.integer(tab)); ggplot(dd,aes(count,combo))+geom_col(fill="#3C5488",width=.72)+labs(x="Intersection size",y=NULL)+theme_clean(base_size)}
if(sys.nframe()==0) save_demo(upset_plot(generate_mock_data()),"upset_demo",width=105,height=78)
