#!/bin/bash

# This scripts prepares subject repositories from Defects4J. 
# It controls versions that need to be skipped or inverted (see README.md).
# It also uses build_patcher.py to integrate Ekstazi into the project builds.

if [ $# != 4 ]; then
    echo "Usage:"
    echo "./run_fastazi.sh [start_version] [end_version] [project_id] [mvn/ant]"
    echo "start_version (int): The first version to run."
    echo "end_version (int): The last version to run."
    echo "project_id (str): The Defects4J project id (e.g. Chart, Csv, etc.)."
    echo "mvn/ant (str): Whether the project uses maven or ant for builds."

    exit 1
fi

if [ ${1} -lt 1 ]; then
    echo "Start version should be greater than 0."
    exit 2
fi

if [ ${4} != "ant" ] && [ ${4} != "mvn" ] && [ ${4} != "none" ]; then
    echo "Build system must be ant or mvn."
    exit 4
fi

start=${1}
end=${2}
project=${3}
build=${4}

rm -rf repos/${project}
mkdir repos
mkdir repos/${project}

skipped=0

# Closure has three versions that are irrelevant to us.
closure_skip=(21 137 146)

if [ ${project} = "Chart" ] || 
   [ ${project} = "Math" ] ||
   [ ${project} = "Closure" ] ||
   [ ${project} = "Lang" ] ||
   [ ${project} = "Time" ]; then

    # These five projects have bug IDs in reverse chronological order.

    for i in $(seq ${start} ${end}); do

        dir_ver=$(expr ${end} - ${i} + ${start} + ${skipped})
        project_dir=repos/${project}/${dir_ver}_fixed  

        if [[ ${project} = "Closure" && 
            ( ( ${i} = 21 ) || ( ${i} = 137 ) || ( ${i} = 146 ) ) ]]; then
            # skip this version
            echo "Skipping ${project} version ${i}."
        else
            defects4j checkout -p ${project} -v ${i}f -w ${project_dir}
        fi
        
        if [ -d ${project_dir} ]; then
            rm -rf ${project_dir}/.git

            if [ ${build} = "ant" ]; then
                if [ ${project} = "Chart" ]; then
                    # Chart's build.xml is in a subdirectory
                    python3 tools/build_patcher.py ${project_dir}/ant/build.xml ant
                else
                    python3 tools/build_patcher.py ${project_dir}/build.xml ant
                fi
            fi

            if [ ${build} = "mvn" ]; then
                python3 tools/build_patcher.py ${project_dir}/pom.xml mvn
            fi
        else
            skipped=$(expr ${skipped} + 1)
        fi
    done

else

    for i in $(seq ${start} ${end}); do
        dir_ver=$(expr ${i} - ${skipped})
        project_dir=repos/${project}/${dir_ver}_fixed
        defects4j checkout -p ${project} -v ${i}f -w ${project_dir}

        if [ -d ${project_dir} ]; then
            rm -rf ${project_dir}/.git

            if [ ${build} = "ant" ]; then
                python3 tools/build_patcher.py ${project_dir}/build.xml ant
            fi

            if [ ${build} = "mvn" ]; then
                if [ ${project} = "Gson" ]; then
                    # Gson's project is in a subdirectory
                    python3 tools/build_patcher.py ${project_dir}/gson/pom.xml mvn
                else
                    python3 tools/build_patcher.py ${project_dir}/pom.xml mvn
                fi
            fi
        else
            skipped=$(expr ${skipped} + 1)
        fi
    done

fi

echo ${skipped} > ${project}_skipped.txt

exit 0
