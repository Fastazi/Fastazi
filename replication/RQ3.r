# library(pgirmess) # kruskalmc
library(agricolae) # kruskal with tukey groups
library(rcompanion)  # multiVDA
library(effsize) # VD.A
library(rstatix) # wilcox_test

#==================================================
# Preparation
#==================================================
#LOAD RESULTS FILE
raw_results <- read.table("RQ3.csv", header=TRUE, sep=",")

#==================================================
# Normality Test (Time)
#==================================================
shapiro.test(raw_results$Time)

#==================================================
# Kruskal-Wallis Rank Sum Test (Time)
#==================================================
#Kruskal-Wallis rank sum test
#with(raw_results, tapply(TTFF, Suite, median, na.rm=TRUE))
kruskal.test(Time ~ Group, data=raw_results)

#Kruskal-Wallis rank sum test (MULTIPLE COMPARISON)
# kruskalmc(Time ~ Group, data=raw_results)

out <- kruskal(raw_results$Time, raw_results$Group)
out

cat("\n----------\n")
cat(  "# Pairwise comparisons using Wilcoxon’s test")
cat("\n----------\n")
wilcox_test(raw_results, Time ~ Group, p.adjust.method = "bonferroni")
cat("\n==================================================\n")

#==================================================
# Pairwise Vargha and Delaney's A and Cliff's delta
#==================================================
multiVDA(Time ~ Group, data=raw_results)

#==================================================
# VD.A: Vargha and Delaney A measure (small, >= 0.56; medium, >= 0.64; large, >= 0.71)
#==================================================
ekstazi <- subset(raw_results, Group == "Ekstazi")
fast <- subset(raw_results, Group == "Fast")
fastazi <- subset(raw_results, Group == "Fastazi")
cat("# FAST vs Ekstazi")
VD.A(fast$Time,ekstazi$Time)
cat("# FAST vs Fastazi")
VD.A(fast$Time,fastazi$Time)
cat("# Fastazi vs Ekstazi")
VD.A(fastazi$Time,ekstazi$Time)