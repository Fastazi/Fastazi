#!/bin/bash
cd metrics

#Subjects
Subjects=("Chart"  "Cli"  "Closure"  "Codec"  "Compress"  "Collections"  "Gson"  "Jsoup"  "JxPath"  "Lang"  "Math"  "Time")

#Preparation
mkdir -p all
mkdir aux_raw
mkdir aux_avg
mkdir aux_time
mkdir aux_time_avg
mkdir aux_budget_all
mkdir aux_budget_all_avg
mkdir aux_budget_selected
mkdir aux_budget_selected_avg


#Copy raw.csv and avg.csv files
for subject in ${Subjects[*]}; do
  echo "Copying raw.csv for subject "$subject
  cp $subject/raw.csv aux_raw/$subject"_raw".csv
  cp $subject/avg.csv aux_avg/$subject"_avg".csv
  cp $subject/time.csv aux_time/$subject"_time".csv
  cp $subject/time_avg.csv aux_time_avg/$subject"_time_avg".csv
  # ---------------------------------------- budget all ----------------------------------------
  cp $subject/budget_all_raw.csv aux_budget_all/$subject"_budget_all".csv
  cp $subject/budget_all_avg.csv aux_budget_all_avg/$subject"_budget_all_avg".csv
  # ---------------------------------------- budget selected ----------------------------------------
  cp $subject/budget_selected_raw.csv aux_budget_selected/$subject"_budget_selected".csv
  cp $subject/budget_selected_avg.csv aux_budget_selected_avg/$subject"_budget_selected_avg".csv
done

head -n 1 aux_raw/Chart_raw.csv > all/raw.csv && tail -n+2 -q aux_raw/*.csv >> all/raw.csv
head -n 1 aux_avg/Chart_avg.csv > all/avg.csv && tail -n+2 -q aux_avg/*.csv >> all/avg.csv
head -n 1 aux_time/Chart_time.csv > all/time.csv && tail -n+2 -q aux_time/*.csv >> all/time.csv
head -n 1 aux_time_avg/Chart_time_avg.csv > all/time_avg.csv && tail -n+2 -q aux_time_avg/*.csv >> all/time_avg.csv
# ---------------------------------------- budget all ----------------------------------------
head -n 1 aux_budget_all/Chart_budget_all.csv > all/budget_all.csv && tail -n+2 -q aux_budget_all/*.csv >> all/budget_all.csv
head -n 1 aux_budget_all_avg/Chart_budget_all_avg.csv > all/budget_all_avg.csv && tail -n+2 -q aux_budget_all_avg/*.csv >> all/budget_all_avg.csv
# ---------------------------------------- budget selected ----------------------------------------
head -n 1 aux_budget_selected/Chart_budget_selected.csv > all/budget_selected.csv && tail -n+2 -q aux_budget_selected/*.csv >> all/budget_selected.csv
head -n 1 aux_budget_selected_avg/Chart_budget_selected_avg.csv > all/budget_selected_avg.csv && tail -n+2 -q aux_budget_selected_avg/*.csv >> all/budget_selected_avg.csv


echo "all.csv generated. Done!"

rm -rf aux_raw
rm -rf aux_avg
rm -rf aux_time
rm -rf aux_time_avg
rm -rf aux_budget_all
rm -rf aux_budget_all_avg
rm -rf aux_budget_selected
rm -rf aux_budget_selected_avg

cd ..