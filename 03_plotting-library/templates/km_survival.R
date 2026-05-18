tryCatch(tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))),
         error = function(e) tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R")))
suppressPackageStartupMessages({library(ggplot2); library(survival)})

generate_mock_data <- function(seed=42){set.seed(seed); n<-180; group<-rep(c("Low","High"),each=n/2); time<-rexp(n,rate=rep(c(.055,.035),each=n/2)); event<-rbinom(n,1,.72); data.frame(time=pmin(time,60),event=event,group=group)}
km_survival_plot <- function(df,time_col="time",event_col="event",group_col="group",base_size=16){fit<-survfit(as.formula(paste0("Surv(",time_col,",",event_col,")~",group_col)),df); s<-summary(fit); dd<-data.frame(time=s$time,surv=s$surv,group=sub(".*=","",s$strata)); ggplot(dd,aes(time,surv,colour=group))+geom_step(linewidth=.65)+scale_colour_manual(values=NATURE_COLORS)+labs(x="Time",y="Survival probability")+coord_cartesian(ylim=c(0,1))+theme_clean(base_size)+theme(legend.position="top")}
if(sys.nframe()==0) save_demo(km_survival_plot(generate_mock_data()),"km_survival_demo")
