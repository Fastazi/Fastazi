# install.packages("rcompanion")
# install.packages("effsize")
# install.packages("readr")
# install.packages("ggplot2")
# install.packages("nortest") # ad.test
# install.packages("pgirmess") # kruskalmc
# install.packages("agricolae") # kruskal with tukey groups
# install.packages("rstatix") # dunn test, wilcox_test
install.packages("wesanderson")
# install.packages("RColorBrewer")

# library(readr)
# library(ggplot2)
# library(nortest, pos=17) # ad.test
# library(pgirmess) # kruskalmc
# library(agricolae) # kruskal with tukey groups
# library(rstatix) # dunn test, wilcox_test
# library(wesanderson)
# library(RColorBrewer)

library(wesanderson)

draft_mode <- FALSE

subjects <- c("Chart", "Cli", "Closure", "Codec", "Collections", "Compress", "Gson", "Jsoup", "JxPath", "Lang", "Math", "Time")
max_faults <- c(26, 30, 168, 8, 4, 39, 18, 93, 4, 28, 100, 23)
names(max_faults) <- subjects

# Colors
my.cols = c(wes_palette("Zissou1", n = 5)[2:3], wes_palette("Darjeeling1", n = 5)[2], wes_palette("Zissou1", n = 5)[5])
