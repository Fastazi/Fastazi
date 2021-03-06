#!/bin/bash

# This scripts runs the Fastazi experiment on 
# multiple subjects using recommended settings.

projects=("Chart" "Cli" "Closure" "Codec" "Collections" "Compress" "Gson" "Jsoup" "JxPath" "Lang" "Math" "Time")
starts=(1  11 4   11 25 9  1  1  19 14 5   3)
ends=(  26 40 176 18 28 47 18 93 22 41 104 26)
builds=("ant" "mvn" "ant" "mvn" "mvn" "mvn" "mvn" "mvn" "mvn" "mvn" "mvn" "mvn")

for i in $(seq 0 $(expr ${#projects[@]} - 1)); do
    project=${projects[i]}
    start=${starts[i]}
    end=${ends[i]}
    build=${builds[i]}

    ./scripts/run_fastazi.sh ${start} ${end} ${project} ${build}
done

./scripts/combine_raw_files.sh

# R scripts