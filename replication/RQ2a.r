#!/usr/bin/env Rscript
library(readr)
library(ggplot2)
#==================================================
source("config.R")
#==================================================

#==================================================
# Preparation
#==================================================
pdf_w <- 11.7
pdf_h <- 4.1

results_loc <- "subjects/all/RQ2a.csv"
approaches <- c("Ekstazi+random","Fastazi-S","FAST-pw","Random")

budgets <- c("25%","50%","75%","100%")

#LOAD RESULTS FILE
raw_results <- read_delim(results_loc, ",", escape_double = FALSE, trim_ws = TRUE)

# Filtering
raw_results <- subset(raw_results, Suite %in% approaches)
raw_results <- subset(raw_results, Budget %in% budgets)

v_factor_levels <- unique(approaches)

raw_results$Budget_f = factor(raw_results$Budget, levels=c("25%","50%","75%","100%"))

#reorder
raw_results$Suite <- factor(raw_results$Suite, levels=c("Ekstazi+random","FAST-pw","Fastazi-S","Random"),
                            labels=c("Ekstazi","FAST","Fastazi","Random"))

#==================================================
# BOX PLOT - Per budget - all subjects together
#==================================================
pdf("RQ2a.pdf", width=pdf_w, height=pdf_h/1.5)
#
p <- ggplot(raw_results, aes(x=Suite, y=HitCount, fill=Suite)) + 
  geom_violin(trim=TRUE) +
  geom_boxplot(width=0.1) +
  facet_wrap(~Budget_f, ncol = 4) + #facet_wrap(~Budget, ncol = 5) +
  theme_bw() +
  theme(axis.title = element_blank(), axis.text.x = element_blank(), axis.ticks.x=element_blank(),
        legend.title = element_blank(), legend.position = 'bottom', legend.text = element_text(size = 12), legend.key.size = unit(0.45, 'cm')) +
  theme(panel.grid.minor = element_blank(), panel.grid.major.x = element_blank(),
        strip.text.x = element_text(size = 11.5),
        axis.text.y = element_text(size=10)) +
  theme(plot.margin=grid::unit(c(0,0,0,0), "mm")) +
  theme(legend.margin=margin(t=-0.4, r=0, b=0, l=0, unit="cm")) +
  scale_fill_manual(values = my.cols, labels=c("Ekstazi","FAST","Fastazi","Random"))
show(p)
dev.off()