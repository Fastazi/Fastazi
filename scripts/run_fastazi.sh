# This scripts controls the flow of actions in order to
# run the Fastazi experiment on a single subject.

# Usage instructions

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

if [ ${4} != "ant" ] && [ ${4} != "mvn" ]; then
    echo "Build system must be ant or mvn."
    exit 4
fi


start=${1}
end=${2}
project=${3}
build=${4}

compile() {
    local run_tests=${@}

    if [ ${build} = "ant" ]; then
        # Run all the tests of the first version
        cd ${working_dir}

        if [ ${project} = "Chart" ]; then
            # Chart's build.xml is in an ant subdirectory
            cd ant
        fi

        if [ ${run_tests} = "test" ]; then
            ant test -silent > /dev/null
        else
            /usr/bin/time -o ${results_dir}/time/build_time.txt -f '%E' ant compile-tests -silent > /dev/null
        fi
  
        if [ ${project} = "Chart" ]; then
            cd ..
        fi
        cd ../..
    fi

    if [ ${build} = "mvn" ]; then
        # Run all the tests of the first version
        cd ${working_dir}

        if [ ${run_tests} = "test" ]; then
            mvn install > /dev/null
        else
            /usr/bin/time -o ${results_dir}/time/build_time.txt -f '%E' mvn install -DskipTests=true > /dev/null
        fi
        
        cd ../..
    fi
}

create_dirs() {
    local results_dir=${@}

    mkdir ${results_dir}
    mkdir ${results_dir}/ekstazi
    mkdir ${results_dir}/fast_pw
    mkdir ${results_dir}/fast_1
    mkdir ${results_dir}/efast_pw
    mkdir ${results_dir}/efast_1
    mkdir ${results_dir}/fastazi_pw
    mkdir ${results_dir}/fastazi_1
    mkdir ${results_dir}/remaining_pw
    mkdir ${results_dir}/remaining_1
    mkdir ${results_dir}/random
    mkdir ${results_dir}/time
}

echo "========================================="
echo "Cloning repositories"
echo "========================================="
./scripts/prepare_repos.sh ${1} ${2} ${3} ${4}

abs=$(pwd)
skipped=$(cat ${project}_skipped.txt)

working_dir=repos/temp
tools_dir=tools

if [ ${project} = "Chart" ] || 
   [ ${project} = "Math" ] ||
   [ ${project} = "Closure" ] ||
   [ ${project} = "Lang" ] ||
   [ ${project} = "Time" ]; then
    start=$(expr ${start} + ${skipped})
else
    end=$(expr ${end} - ${skipped})
fi

# Copy v1
if [ ${project} = "Gson" ]; then
    project_dir=${abs}/repos/${project}/${start}_fixed/gson
else
    project_dir=${abs}/repos/${project}/${start}_fixed
fi
results_dir=${abs}/repos/${project}/${start}_results
create_dirs ${results_dir}

rm -rf ${working_dir}
cp -r ${project_dir} ${working_dir}

i=${start}
echo "========================================="
echo "Compiling ${project} version ${1}"
echo "========================================="
compile "skip"
compile "test"

# Get Ekstazi selection
echo "========================================="
echo "Selecting tests for ${project} version ${1}"
echo "========================================="
/usr/bin/time -o ${results_dir}/time/selection_time.txt -f '%E' ls ${working_dir}/.ekstazi/ > ${results_dir}/all_tests.txt
sed -i -e 's/.clz//g' ${results_dir}/all_tests.txt
sed -i -e 's/test-results//g' ${results_dir}/all_tests.txt

cp ${results_dir}/all_tests.txt ${results_dir}/affected_tests.txt
# diff --unchanged-group-format="" ${results_dir}/unaffected_tests.txt ${results_dir}/all_tests.txt > ${results_dir}/affected_tests.txt

# Get FAST prioritization
echo "========================================="
echo "Prioritizing tests for ${project} version ${1}"
echo "========================================="
/usr/bin/time -o ${results_dir}/time/fast_preparation_time.txt -f '%E' python3 ${tools_dir}/fast_parser.py ${working_dir}
python3 ${tools_dir}/prioritize.py ${working_dir} ${results_dir} 30 false

# Combine the results
echo "========================================="
echo "Combining results for ${project} version ${1}"
echo "========================================="
python3 ${tools_dir}/ekstazi_shuffle.py ${results_dir}
python3 ${tools_dir}/combine.py ${results_dir} pw
python3 ${tools_dir}/combine.py ${results_dir} 1

cp -r ${working_dir}/.ekstazi ${results_dir}/ekstazi_dir
cp -r ${working_dir}/.fast ${results_dir}/fast_dir


for i in $(seq $(expr ${start} + 1) ${end}); do
    
    prev_results_dir=${results_dir}

    if [ ${project} = "Gson" ]; then
        project_dir=${abs}/repos/${project}/${i}_fixed/gson
    else
        project_dir=${abs}/repos/${project}/${i}_fixed
    fi
    results_dir=${abs}/repos/${project}/${i}_results
    create_dirs ${results_dir}

    # Copy
    rm -rf ${working_dir}
    cp -r ${project_dir} ${working_dir}

    # Copy Ekstazi and FAST directories
    echo "========================================="
    echo "Copying previous Ekstazi and FAST directories to version ${i}"
    echo "========================================="
    cp -r ${prev_results_dir}/ekstazi_dir ${working_dir}/.ekstazi
    cp -r ${prev_results_dir}/fast_dir ${working_dir}/.fast

    echo "========================================="
    echo "Compiling ${project} version ${i}"
    echo "========================================="
    compile "skip"

    # Get Ekstazi selection
    echo "========================================="
    echo "Selecting tests for ${project} version ${i}"
    echo "========================================="
    /usr/bin/time -o ${results_dir}/time/selection_time.txt -f '%E' java -cp ${tools_dir}/org.ekstazi.core-5.3.0.jar org.ekstazi.check.AffectedChecker ${working_dir}/.ekstazi/ > ${results_dir}/unaffected_tests.txt

    echo "========================================="
    echo "Running tests for ${project} version ${i}"
    echo "========================================="
    compile "test"

    # Extract the list of affected tests [all_tests - unaffected_tests]
    ls ${working_dir}/.ekstazi/ > ${results_dir}/all_tests.txt
    sed -i -e 's/.clz//g' ${results_dir}/all_tests.txt
    sed -i -e 's/test-results//g' ${results_dir}/all_tests.txt
    diff --unchanged-group-format="" ${results_dir}/unaffected_tests.txt ${results_dir}/all_tests.txt > ${results_dir}/affected_tests.txt

    # Get FAST prioritization
    echo "========================================="
    echo "Prioritizing tests for ${project} version ${i}"
    echo "========================================="
    /usr/bin/time -o ${results_dir}/time/fast_preparation_time.txt -f '%E' python3 ${tools_dir}/fast_parser.py ${working_dir}
    python3 ${tools_dir}/prioritize.py ${working_dir} ${results_dir} 30 false

    # Combine the results
    echo "========================================="
    echo "Combining results for ${project} version ${i}"
    echo "========================================="
    python3 ${tools_dir}/ekstazi_shuffle.py ${results_dir}
    python3 ${tools_dir}/combine.py ${results_dir} pw
    python3 ${tools_dir}/combine.py ${results_dir} 1

    cp -r ${working_dir}/.ekstazi ${results_dir}/ekstazi_dir
    cp -r ${working_dir}/.fast ${results_dir}/fast_dir

done

# Calculate the metrics
echo "========================================="
echo "Calculating metrics for ${project}"
echo "========================================="
# python3 ${tools_dir}/metric.py ./repos ${start} ${end} ./metrics ${project}
python3 ${tools_dir}/metric.py ./repos ${start} ${end} ./metrics ${project} all
python3 ${tools_dir}/metric.py ./repos ${start} ${end} ./metrics ${project} selected

rm -rf ${working_dir}

exit 0
