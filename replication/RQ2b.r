#!/usr/bin/env Rscript
library(dplyr)
library(readr)
library(ggplot2)
library(gridExtra)
#==================================================
source("config.R")
#==================================================
get_legend<-function(myggplot){
  tmp <- ggplot_gtable(ggplot_build(myggplot))
  leg <- which(sapply(tmp$grobs, function(x) x$name) == "guide-box")
  legend <- tmp$grobs[[leg]]
  return(legend)
}
#==================================================
sink.reset <- function(){
  for(i in seq_len(sink.number())){
    sink(NULL)
  }
}
#==================================================
give.n <- function(x){
  return(c(y = mean(x), label = length(x)))
}


#==================================================
# Preparation
#==================================================
input_file = "budget_selected_avg.csv"
budgets <- c(0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0)
my.breaks = seq(0.1, 1, 0.1)

approaches <- c("Ekstazi+random","Fastazi-S","FAST-pw","Random")
v_factor_levels <- unique(approaches)
pdf_w <- 8.49
pdf_h <- 6.4

#==================================================
subjects = c("Chart", "Cli", "Closure", "Codec", "Collections", "Compress", "Gson", "Jsoup", "JxPath", "Lang", "Math", "Time")
plots <- list()

pdf("RQ2b.pdf", width=pdf_w, height=pdf_h, onefile=FALSE)

for(subject in subjects) {
  max_faults_ = as.numeric(max_faults[subject])

  results_loc <- paste("subjects", subject, input_file, sep="/")
  
  #LOAD RESULTS FILE
  raw_results <- read_delim(results_loc, ",", escape_double = FALSE, trim_ws = TRUE)
  
  # Convert 50% to 0.5...
  raw_results$Budget <- as.numeric(gsub("%", "", paste(raw_results$Budget)))/100
  
  # Filtering
  raw_results <- subset(raw_results, Suite %in% approaches)
  raw_results <- subset(raw_results, Budget %in% budgets)
  
  #reorder
  raw_results$Suite <- factor(raw_results$Suite, levels=c("Ekstazi+random","FAST-pw","Fastazi-S","Random"),
                              labels=c("Ekstazi","FAST","Fastazi","Random"))
  
  # group per budget (individual subjects)
  grouped = raw_results %>% 
    group_by(Project, Budget, Suite) %>% 
    summarise(RelBudget = round(mean(RelBudget), digits = 2), Hit = sum(Hit))
  
  sec = filter(grouped, Suite == "Ekstazi")$RelBudget
  
  #===
  p <- ggplot(grouped, aes(fill=Suite, y=Hit, x=Budget)) + 
    geom_bar(position="dodge", stat="identity") +
    scale_x_continuous(breaks = budgets, labels = NULL, sec.axis=sec_axis(~ . + 0, breaks = budgets, labels = sec)) +
    scale_y_continuous(breaks = c(0, round(max_faults_*0.25, digits = 0), round(max_faults_*0.5, digits = 0), round(max_faults_*0.75, digits = 0), round(max_faults_*1.0, digits = 0))) +
    expand_limits(y=c(0, max_faults_)) +
    theme_minimal()  +
    theme(axis.title.x = element_blank(), axis.text.x.top = element_text(angle = 45)) +
    theme(text = element_text(size = 10)) +
    theme(axis.title.y.left = element_text(size=11)) + 
    theme(legend.position = "bottom") +
    theme(plot.margin=grid::unit(c(0,0,0,0), "mm")) +
    theme(panel.grid.minor = element_blank()) +
    labs(y=subject) + #, x ="Dose (mg)", y = "Teeth length")
    theme(legend.title = element_blank(), legend.text = element_text(size = 9), legend.key.size = unit(0.25, 'cm')) +
    scale_fill_manual(values = my.cols, labels=c("Ekstazi","Fast","Fastazi","Random"))
  if(subject %in% c('Lang','Math','Time')){
    p <- p + scale_x_continuous(breaks = budgets, sec.axis=sec_axis(~ . + 0, breaks = budgets, labels = sec)) +
      theme(axis.line.x.bottom = element_line(size=0.5), axis.text.x.bottom = element_text(face="bold",size=8, angle = 0))
  }
  if(subject %in% c('Closure','Compress','JxPath','Time')){
    p <- p + scale_y_continuous(breaks = c(0, round(max_faults_*0.25, digits = 0), round(max_faults_*0.5, digits = 0), round(max_faults_*0.75, digits = 0), round(max_faults_*1.0, digits = 0)), sec.axis = dup_axis(labels = c(0, ".25", ".5", ".75", 1))) +
      theme(axis.line.y.right = element_line(size=0.5), axis.text.y.right = element_text(face = "bold", size=8), axis.title.y.right = element_blank())
  }
  #===
  legend <- get_legend(p)
  #---
  p <- p + theme(legend.position = 'none')
  #===
  
  # Grouped
  plots[[paste0(subject)]] <- p
  
  if(subject == 'Time'){
    plots[['legend']] <- legend
  }
}

print(length(plots))

grid.arrange(grobs=plots, ncol=3, nrow=5, layout_matrix = rbind(c(1,2,3), c(4,5,6), c(7,8,9), c(10,11,12), c(13,13,13)),
             widths = c(2.83, 2.83, 2.83), heights = c(1.8, 1.8, 1.8, 1.8, 0.2))
dev.off()