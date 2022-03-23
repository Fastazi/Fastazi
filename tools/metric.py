'''
This file is part of an AST'22 submission that is currently under review.

================================================================

This script is responsible for calculating metrics based on the
output of the Fastazi experiments.

================================================================

This is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as 
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this source.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys
import os
from functions import *
from constants import *

def calc_avg(results: dict, versions: list):

    avg = {}
    for version in versions:
        version_avg = {str_result: {}, str_len: 0}
        version_avg[str_len] = results[version][1]["100%"][str_fast_pw][str_len]
        for p in percentages:
            percentage_avg = {}
            percentage = str(int(p * 100))+"%"
            for suite in suites:
                suite_avg = {str_result:{}, str_misses: 0}
                fails = 0
                for metric in metrics:
                    metric_avg = {}
                    s = 0
                    c = 0
                    for iteration in iterations:
                        result = results[version][iteration][percentage][suite][metric]
                        if result != "NA":
                            s += result
                            c += 1
                        elif metric == str_ttff_abs:
                            fails += 1
                    metric_avg = s/c if c > 0 else "NA"
                    suite_avg[str_result][metric] = metric_avg
                suite_avg[str_misses] = fails
                percentage_avg[suite] = suite_avg
            version_avg[str_result][percentage] = percentage_avg
        avg[version] = version_avg

    return avg

if __name__ == '__main__':

    if len(sys.argv) == 7:
        repos_dir = sys.argv[1]
        initial_version = int(sys.argv[2])
        final_version = int(sys.argv[3])
        output_dir = sys.argv[4]
        project_id = sys.argv[5]
        budget_calculation = sys.argv[6]
    else:
        print("Incorrect number of arguments.")
        exit(1)

    print("Computing metrics for ", project_id)

    # results is indexed by version
    results = {}
    time = {}
    skipped = []
    first = True
    first_time = {}
    first_len = 0

    for version in range(initial_version, final_version+1):
        project_path = os.path.join(repos_dir, project_id, str(version)+"_fixed")
        results_path = os.path.join(repos_dir, project_id, str(version)+"_results")
        
        dirs = {}
        for suite in suites:
            dirs[suite] = os.path.join(results_path, suite)

        ekstazi_dir = os.path.join(results_path, "ekstazi_dir")
        fast_dir = os.path.join(results_path, "fast_dir")
        prioritized_path = os.path.join(dirs[str_fast_pw], "1.txt")
        if (not os.path.exists(ekstazi_dir) or
            not os.path.exists(fast_dir) or
            not os.path.exists(prioritized_path)):
            if budget_calculation == "all": 
                # Just to avoid duplicate output
                print(project_id, " version ", version, ": Selection and/or prioritization failed due to compilation error. Skipping metrics.")
            skipped.append(version)
            continue

        faults = get_failing_tests(os.path.join(project_path, "defects4j.build.properties"))

        all_tests = read_file(os.path.join(results_path, "all_tests.txt"))
        full_suite_len = len(all_tests)

        # version_results is indexed by iteration
        version_results = {}

        if first:
            first_time[version] = gather_time(results_path)
            first_len = full_suite_len
            first = False
        else:
            time[version] = gather_time(results_path)
        
        for iteration in range(1, 31):

            tests = {}
            for suite in suites:
                path = os.path.join(dirs[suite], str(iteration)+".txt")
                tests[suite] = read_file(path)
            iteration_results = {}
            
            for percentage in percentages:
                
                # percentage results are keyed by suite, then by metric
                percentage_results = {}

                # choose if the cut is based on full suite size or selection count
                if budget_calculation == "all":
                    cut = int(full_suite_len * percentage)
                else:
                    cut = int(len(tests[str_ekstazi]) * percentage)

                cuts = {}
                for suite in suites:
                    t = tests[suite]
                    cuts[suite] = t[:min(len(t), cut)]

                for suite in suites:
                    t = cuts[suite]

                    suite_len = len(t)
                    suite_adj = suite_len / full_suite_len if full_suite_len != 0 else "NA"
                    suite_apfd = apfd(t, faults)
                    suite_ttff = ttff_abs(t, faults)
                    suite_napfd = napfd(full_suite_len, suite_ttff)
                    suite_pttff = ttff(full_suite_len, suite_ttff)

                    # if iteration == 1 and suite == str_fast_pw and percentage == 1.0:
                    #     print(suite_apfd)
                    #     print(suite_napfd)
                    #     print(suite_ttff)
                    #     print(len(t))
                    #     print(t, faults)
                    suite_ttff = suite_ttff if suite_ttff > 0 else "NA"
                    suite_pttff = suite_pttff if suite_pttff > 0 else "NA"

                    percentage_results[suite] = {
                                                    str_adj: suite_adj,
                                                    str_len: suite_len,
                                                    str_napfd: suite_napfd,
                                                    str_ttff_abs: suite_ttff,
                                                    str_ttff: suite_pttff
                                                }
                
                iteration_results[str(int(percentage * 100))+"%"] = percentage_results
            
            version_results[iteration] = iteration_results
        
        results[version] = version_results

    output_dir = os.path.join(output_dir, project_id)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # exit(0)

    filename = "budget"
    filename += "_all" if budget_calculation == "all" else "_selected"
    filename += "_raw.csv"
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "w") as output:
        output.write("Project, Version, Iteration, Budget, Suite, Test count, APFDf, TTFF, pTTFF\n")

        for version, version_results in results.items():
            for iteration, iteration_results in version_results.items():
                for percentage, percentage_results in iteration_results.items():
                    for suite, suite_results in percentage_results.items():
                        line = "{}".format(project_id)
                        line += ",{}".format(version)
                        line += ",{}".format(iteration)
                        line += ",{}".format(percentage)
                        line += ",{}".format(display_names[suite])
                        line += ",{}".format(suite_results[str_len])
                        line += ",{}".format(suite_results[str_napfd])
                        line += ",{}".format(suite_results[str_ttff_abs])
                        line += ",{}".format(suite_results[str_ttff])
                        line += "\n"
                        output.write(line)


    avg = calc_avg(results, results.keys())
    
    filename = "budget"
    filename += "_all" if budget_calculation == "all" else "_selected"
    filename += "_avg.csv"
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "w") as output:
        output.write("Project, Version, Budget, Suite, RelBudget, Test count, APFDf, TTFF, pTTFF, Misses, Hit, HitCount\n")
        
        for version, version_results in avg.items():
            for percentage, percentage_results in version_results[str_result].items():
                for suite, suite_results in percentage_results.items():
                    line = "{}".format(project_id)
                    line += ",{}".format(version)
                    line += ",{}".format(percentage)
                    line += ",{}".format(display_names[suite])
                    result = suite_results[str_result]
                    line += ",{}".format(result[str_adj])
                    line += ",{}".format(result[str_len])
                    line += ",{}".format(result[str_napfd])
                    line += ",{}".format(result[str_ttff_abs] if suite_results[str_misses] == 0 else "NA")
                    line += ",{}".format(result[str_ttff] if suite_results[str_misses] == 0 else "NA")
                    line += ",{}".format(suite_results[str_misses])
                    line += ",{}".format(1 if suite_results[str_misses] == 0 else 0)
                    line += ",{}".format(30 - suite_results[str_misses])
                    line += "\n"
                    output.write(line)

    if budget_calculation == "all":
        output_path = os.path.join(output_dir, "raw.csv")
        with open(output_path, "w") as output:
            output.write("Project, Version, Iteration, Suite, Test count, APFDf, TTFF, pTTFF\n")

            for version, version_results in results.items():
                for iteration, iteration_results in version_results.items():
                    for suite, suite_results in iteration_results["100%"].items():
                        line = "{}".format(project_id)
                        line += ",{}".format(version)
                        line += ",{}".format(iteration)
                        line += ",{}".format(display_names[suite])
                        line += ",{}".format(suite_results[str_len])
                        line += ",{}".format(suite_results[str_napfd])
                        line += ",{}".format(suite_results[str_ttff_abs])
                        line += ",{}".format(suite_results[str_ttff])
                        line += "\n"
                        output.write(line)


        output_path = os.path.join(output_dir, "avg.csv")
        with open(output_path, "w") as output:
            output.write("Project, Version, Suite, Test count, APFDf, TTFF, pTTFF, Misses, Hit, HitCount\n")
            
            for version, version_results in avg.items():
                for suite, suite_results in version_results[str_result]["100%"].items():
                    line = "{}".format(project_id)
                    line += ",{}".format(version)
                    line += ",{}".format(display_names[suite])
                    results = suite_results[str_result]
                    line += ",{}".format(results[str_len])
                    line += ",{}".format(results[str_napfd])
                    line += ",{}".format(results[str_ttff_abs] if suite_results[str_misses] == 0 else "NA")
                    line += ",{}".format(results[str_ttff] if suite_results[str_misses] == 0 else "NA")
                    line += ",{}".format(suite_results[str_misses])
                    line += ",{}".format(1 if suite_results[str_misses] == 0 else 0)
                    line += ",{}".format(30 - suite_results[str_misses])
                    line += "\n"
                    output.write(line)


        output_path = os.path.join(output_dir, "time.csv")
        with open(output_path, "w") as output:
            output.write("Project, Version, Suite, Time\n")

            for version, version_results in time.items():
                for suite, result in version_results.items():
                    line = "{}".format(project_id)
                    line += ",{}".format(version)
                    line += ",{}".format(display_names[suite])
                    line += ",{}".format(result)
                    line += "\n"
                    output.write(line)


        output_path = os.path.join(output_dir, "time_init.csv")
        with open(output_path, "w") as output:
            output.write("Project, Version, Suite, Count, Time\n")

            for version, version_results in first_time.items():
                for suite, result in version_results.items():
                    line = "{}".format(project_id)
                    line += ",{}".format(version)
                    line += ",{}".format(display_names[suite])
                    line += ",{}".format(first_len)
                    line += ",{}".format(result)
                    line += "\n"
                    output.write(line)

        avg = time_avg(time)
        
        output_path = os.path.join(output_dir, "time_avg.csv")
        with open(output_path, "w") as output:
            output.write("Project, Suite, Time\n")

            for suite, result in avg.items():
                line = "{}".format(project_id)
                line += ",{}".format(display_names[suite])
                line += ",{:.4f}".format(result)
                line += "\n"
                output.write(line)