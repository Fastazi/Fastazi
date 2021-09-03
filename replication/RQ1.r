#!/usr/bin/env Rscript
library(readr)
library(ggplot2)
library(nortest, pos=17) # ad.test
library(agricolae) # kruskal with tukey groups
library(rstatix) # dunn test, wilcox_test
#==================================================
source("config.R")
#==================================================
give.n <- function(x){
  return(c(y = mean(x), label = length(x)))
}
#==================================================

subject="all"
target_file = "avg.csv"

results_loc <- paste(subject, target_file, sep="/")

approaches <- c("Ekstazi+random","Fastazi-S","FAST-pw","Random")
v_factor_levels <- unique(approaches)


#==================================================
# Preparation
#==================================================
#LOAD RESULTS FILE
raw_results <- read_delim(results_loc, ",", escape_double = FALSE, trim_ws = TRUE)

raw_results <- subset(raw_results, Suite %in% approaches)

pdf_w <- 9
pdf_h <- 6

#reorder
raw_results$Suite <- factor(raw_results$Suite, levels=c("Ekstazi+random","FAST-pw","Fastazi-S","Random"),
                            labels=c("Ekstazi","FAST","Fastazi","Random"))

#==================================================
# Boxplots (TTFF)
#==================================================
pdf(sprintf("%s.pdf", 'TTFF'), width=pdf_w, height=pdf_h/2)
ggplot(data=subset(raw_results, !is.na(pTTFF)), aes(Suite, pTTFF, fill=Suite)) +
  geom_violin(trim=TRUE) +
  geom_boxplot(width=0.1) +
  theme_minimal()  +
  theme(legend.position="none", axis.title = element_blank(), text = element_text(size = 22)) +
  theme(panel.grid.minor = element_blank()) +
  scale_fill_manual(values = my.cols)
dev.off()

#==================================================
# Boxplots (APFD)
#==================================================
pdf(sprintf("%s.pdf", 'NAPFD'), width=pdf_w, height=pdf_h/2)
ggplot(data=subset(raw_results, !is.na(APFDf)), aes(Suite, APFDf, fill=Suite)) +
  geom_violin(trim=TRUE) +
  geom_boxplot(width=0.1) +
  theme_minimal() +
  theme(legend.position="none", axis.title = element_blank(), text = element_text(size = 22)) +
  theme(panel.grid.minor = element_blank()) +
  scale_fill_brewer(palette="Set2") +
  scale_fill_manual(values = my.cols)
dev.off()

#==================================================
# Normality Test
#==================================================
with(raw_results, ad.test(pTTFF))
with(raw_results, ad.test(APFDf))


cat("\n################################################################################\n")
cat(  "#                                     TTFF                                     #")
cat("\n################################################################################\n")
#Kruskal-Wallis rank sum test
with(raw_results, tapply(pTTFF, Suite, median, na.rm=TRUE))
kruskal.test(pTTFF ~ Suite, data=raw_results)

cat("\n----------\n")
cat(  "# Pairwise comparisons using Wilcoxon’s test")
cat("\n----------\n")
wilcox_test(raw_results, pTTFF ~ Suite, p.adjust.method = "bonferroni")
cat("\n==================================================\n")

out <- kruskal(raw_results$pTTFF, raw_results$Suite)
out

cat("\n################################################################################\n")
cat(  "#                                      NAPFD                                   #")
cat("\n################################################################################\n")
#Kruskal-Wallis rank sum test
with(raw_results, tapply(APFDf, Suite, median, na.rm=TRUE))
kruskal.test(APFDf ~ Suite, data=raw_results)

cat("\n----------\n")
cat(  "# Pairwise comparisons using Wilcoxon’s test")
cat("\n----------\n")
wilcox_test(raw_results, APFDf ~ Suite, p.adjust.method = "bonferroni")
cat("\n==================================================\n")

out <- kruskal(raw_results$APFDf, raw_results$Suite)
out