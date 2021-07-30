#!/bin/bash

# This script can be used to calculate experiment metrics
# without re-running the whole experiment. Useful in cases
# where we want different metrics using the same source data.

projects=("Chart" "Cli" "Closure" "Codec" "Collections" "Compress" "Gson" "Jsoup" "JxPath" "Lang" "Math" "Time")
# It is important that the next two lines match the equivalent ones in run_multiple.sh
starts=(1  11 4   11 25 9  1  1  19 14 7   3)
ends=(  26 40 176 18 28 47 18 93 22 41 104 26)

cd ..

for i in $(seq 0 $(expr ${#projects[@]} - 1)); do
    project=${projects[i]}
    start=${starts[i]}
    end=${ends[i]}

    for j in $(seq ${start} ${end}); do
        results_dir=./repos/${project}/${j}_results
        python3 tools/ekstazi_shuffle.py ${results_dir}
    done

    skipped=$(cat ${project}_skipped.txt)
    if  [ ${project} = "Chart" ] || 
        [ ${project} = "Math" ] ||
        [ ${project} = "Closure" ] ||
        [ ${project} = "Lang" ] ||
        [ ${project} = "Time" ]; then
        start=$(expr ${start} + ${skipped})
    else
        end=$(expr ${end} - ${skipped})
    fi

    # python3 tools/metric.py ./repos ${start} ${end} ./metrics ${project}
    python3 tools/metric.py ./repos ${start} ${end} ./metrics ${project} all
    python3 tools/metric.py ./repos ${start} ${end} ./metrics ${project} selected
done

cd scripts/