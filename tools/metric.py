'''
This file is part of an ICSE'22 submission that is currently under review.

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

# 1. CountHit (nº iterations - nº misses) OK
# 2. Budget Adj (selected tests / total tests)
# 3. Metrics are NA if hit = 0 OK


import sys
import os
# from metric import apfd, read_file, get_failing_tests
from functions import *

# str_ekstazi = "ekstazi_rand"
# str_fast_pw = "fast_pw"
# str_fast_1 = "fast_1"
# str_efast_pw = "efast_pw"
# str_efast_1 = "efast_1"
# str_fastazi_pw = "fastazi_pw"
# str_fastazi_1 = "fastazi_1"
# # str_remaining_pw = "remaining_pw"
# # str_remaining_1 = "remaining_1"
# str_random = "random"
# suites = [str_ekstazi, 
#           str_fast_pw, # str_fast_1, 
#           str_efast_pw, # str_efast_1,
#           str_fastazi_pw, # str_fastazi_1, 
#         #   str_remaining_pw, str_remaining_1,
#           str_random]

# display_names = {
#     str_ekstazi: "Ekstazi+random",
#     str_fast_pw: "FAST-pw",
#     str_fast_1: "FAST-1",
#     str_efast_pw: "Fastazi-S",
#     str_efast_1: "Fastazi-S_1",
#     str_fastazi_pw: "Fastazi-P",
#     str_fastazi_1: "Fastazi-P_1",
#     str_random: "Random",
#     "fast_preparation": "FAST preparation"
# }

# str_adj = "adj_budget"
# str_apfd = "apfd"
# str_ttff = "ttff"
# str_pttff = "pttff"
# str_len = "suite_len"
# metrics = [str_adj, str_len, str_apfd, str_ttff, str_pttff]

# str_result = "result"
# str_misses = "misses"

# percentages = [.10, .20, .25, .30, .40, .50, .60, .70, .75, .80, .90, 1]
# # percentages = [.25, .50, .75, 1]
# iterations = range(1, 31)

# def ttff(suite, faults):

#     count = 1
#     for test_case in suite:
#         for fault in faults:
#             if fault == test_case:
#                 return count
#         count += 1
    
#     return "NA"


# def pttff(full_suite_len, suite, faults):
#     temp_ttff = ttff(suite, faults)
#     if temp_ttff == "NA": return "NA"
#     return float(ttff(suite, faults)) / full_suite_len


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
                        elif metric == str_ttff:
                            fails += 1
                    metric_avg = s/c if c > 0 else "NA"
                    suite_avg[str_result][metric] = metric_avg
                suite_avg[str_misses] = fails
                percentage_avg[suite] = suite_avg
            version_avg[str_result][percentage] = percentage_avg
        avg[version] = version_avg

    return avg

# def read_number(file_path):
#     with open(file_path, "r") as f:
#         lines = f.readlines()
#         raw_number = lines[0].strip()
#         if ":" in raw_number:
#             raw_number = float(raw_number.split(":")[1])
#         else:
#             raw_number = float(raw_number)
#         return "{:.2f}".format(raw_number)

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
        # dirs[str_remaining] = os.path.join(results_path, str_remaining)

        # selected_dir = os.path.join(results_path, "selected")
        # prioritized_dir = os.path.join(results_path, "prioritized")
        # combined_dir = os.path.join(results_path, "combined")
        # random_dir = os.path.join(results_path, "random")

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
            # path = os.path.join(dirs[str_remaining], str(iteration)+".txt")
            # tests[str_remaining] = read_file(path)

            # selected_path = os.path.join(selected_dir, str(iteration)+".txt")
            # prioritized_path = os.path.join(prioritized_dir, str(iteration)+".txt")
            # combined_path = os.path.join(combined_dir, str(iteration)+".txt")
            # remaining_path = os.path.join(remaining_dir, str(iteration)+".txt")
            # random_path = os.path.join(random_dir, str(iteration)+".txt")

            # fast_all = read_file(prioritized_path)
            # ekstazi = read_file(selected_path)
            # combined = read_file(combined_path)
            # remaining = read_file(remaining_path)
            # random = read_file(random_path)

            # iteration results is indexed by percentage
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
                
                # Remaining is used to "fill" the suite
                # in case the budget is larger than Ekstazi's selection
                # t = tests[str_fastazi_pw]+tests[str_remaining_pw]
                # cuts[str_remaining_pw] = t[:min(len(t), cut)]

                # t = tests[str_fastazi_1]+tests[str_remaining_1]
                # cuts[str_remaining_1] = t[:min(len(t), cut)]

                # fast_all_cut = fast_all[:min(len(fast_all), cut)]
                # ekstazi_cut = ekstazi[:min(len(ekstazi), cut)]
                # combined_cut = combined[:min(len(combined), cut)]
                # random_cut = combined[:min(len(combined), cut)]

                # If selection is smaller than budget, add more tests
                # if False:
                #     t = cuts[str_ekstazi]
                #     if len(t) < cut:
                #         t += tests[str_remaining][:(cut-len(t))]
                #     t = cuts[str_ekstazi_fast]
                #     if len(t) < cut:
                #         t += tests[str_remaining][:(cut-len(t))]


                for suite in suites:
                    t = cuts[suite]

                    suite_len = len(t)
                    suite_adj = suite_len / full_suite_len if full_suite_len != 0 else "NA"
                    suite_apfd = apfd(t, faults)
                    suite_ttff = ttff(t, faults)
                    suite_apfdf = apfdf(full_suite_len, suite_ttff)
                    suite_pttff = pttff(full_suite_len, suite_ttff)
                    suite_ttff = suite_ttff if suite_ttff > 0 else "NA"
                    suite_pttff = suite_pttff if suite_pttff > 0 else "NA"

                    percentage_results[suite] = {
                                                    str_adj: suite_adj,
                                                    str_len: suite_len,
                                                    str_apfd: suite_apfd,
                                                    str_apfdf: suite_apfdf,
                                                    str_ttff: suite_ttff,
                                                    str_pttff: suite_pttff
                                                }
                
                iteration_results[str(int(percentage * 100))+"%"] = percentage_results
            
            version_results[iteration] = iteration_results
        
        results[version] = version_results

    output_dir = os.path.join(output_dir, project_id)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filename = "budget"
    filename += "_all" if budget_calculation == "all" else "_selected"
    filename += ".csv"
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "w") as output:
        output.write("Project, Version, Iteration, Budget, Suite, Test count, APFD, APFDf, TTFF, pTTFF\n")

        for version, version_results in results.items():
            for iteration, iteration_results in version_results.items():
                for percentage, percentage_results in iteration_results.items():
                    for suite, suite_results in percentage_results.items():
                        line = "{}".format(project_id)
                        line += ", {}".format(version)
                        line += ", {}".format(iteration)
                        line += ", {}".format(percentage)
                        line += ", {}".format(display_names[suite])
                        line += ", {}".format(suite_results[str_len])
                        line += ", {}".format(suite_results[str_apfd])
                        line += ", {}".format(suite_results[str_apfdf])
                        line += ", {}".format(suite_results[str_ttff])
                        line += ", {}".format(suite_results[str_pttff])
                        line += "\n"
                        output.write(line)


    avg = calc_avg(results, results.keys())
    
    filename = "budget"
    filename += "_all" if budget_calculation == "all" else "_selected"
    filename += "_avg.csv"
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "w") as output:
        output.write("Project, Version, Budget, Suite, RelBudget, Test count, APFD, APFDf, TTFF, pTTFF, Misses, Hit, HitCount\n")
        
        for version, version_results in avg.items():
            for percentage, percentage_results in version_results[str_result].items():
                for suite, suite_results in percentage_results.items():
                    line = "{}".format(project_id)
                    line += ", {}".format(version)
                    line += ", {}".format(percentage)
                    line += ", {}".format(display_names[suite])
                    result = suite_results[str_result]
                    line += ", {}".format(result[str_adj])
                    line += ", {}".format(result[str_len])
                    line += ", {}".format(result[str_apfd])
                    line += ", {}".format(result[str_apfdf])
                    line += ", {}".format(result[str_ttff] if suite_results[str_misses] == 0 else "NA")
                    line += ", {}".format(result[str_pttff] if suite_results[str_misses] == 0 else "NA")
                    line += ", {}".format(suite_results[str_misses])
                    line += ", {}".format(1 if suite_results[str_misses] == 0 else 0)
                    line += ", {}".format(30 - suite_results[str_misses])
                    line += "\n"
                    output.write(line)

    if budget_calculation == "all":
        output_path = os.path.join(output_dir, "raw.csv")
        with open(output_path, "w") as output:
            output.write("Project, Version, Iteration, Suite, Test count, APFD, APFDf, TTFF, pTTFF\n")

            for version, version_results in results.items():
                for iteration, iteration_results in version_results.items():
                    for suite, suite_results in iteration_results["100%"].items():
                        line = "{}".format(project_id)
                        line += ", {}".format(version)
                        line += ", {}".format(iteration)
                        line += ", {}".format(display_names[suite])
                        line += ", {}".format(suite_results[str_len])
                        line += ", {}".format(suite_results[str_apfd])
                        line += ", {}".format(suite_results[str_apfdf])
                        line += ", {}".format(suite_results[str_ttff])
                        line += ", {}".format(suite_results[str_pttff])
                        line += "\n"
                        output.write(line)


        output_path = os.path.join(output_dir, "avg.csv")
        with open(output_path, "w") as output:
            output.write("Project, Version, Suite, Test count, APFD, APFDf, TTFF, pTTFF, Misses, Hit, HitCount\n")
            
            for version, version_results in avg.items():
                for suite, suite_results in version_results[str_result]["100%"].items():
                    line = "{}".format(project_id)
                    line += ", {}".format(version)
                    line += ", {}".format(display_names[suite])
                    results = suite_results[str_result]
                    line += ", {}".format(results[str_len])
                    line += ", {}".format(results[str_apfd])
                    line += ", {}".format(results[str_apfdf])
                    line += ", {}".format(results[str_ttff] if suite_results[str_misses] == 0 else "NA")
                    line += ", {}".format(results[str_pttff] if suite_results[str_misses] == 0 else "NA")
                    line += ", {}".format(suite_results[str_misses])
                    line += ", {}".format(1 if suite_results[str_misses] == 0 else 0)
                    line += ", {}".format(30 - suite_results[str_misses])
                    line += "\n"
                    output.write(line)


        output_path = os.path.join(output_dir, "time.csv")
        with open(output_path, "w") as output:
            output.write("Project, Version, Suite, Time\n")

            for version, version_results in time.items():
                for suite, result in version_results.items():
                    line = "{}".format(project_id)
                    line += ", {}".format(version)
                    line += ", {}".format(display_names[suite])
                    line += ", {}".format(result)
                    line += "\n"
                    output.write(line)


        output_path = os.path.join(output_dir, "time_init.csv")
        with open(output_path, "w") as output:
            output.write("Project, Version, Suite, Count, Time\n")

            for version, version_results in first_time.items():
                for suite, result in version_results.items():
                    line = "{}".format(project_id)
                    line += ", {}".format(version)
                    line += ", {}".format(display_names[suite])
                    line += ", {}".format(first_len)
                    line += ", {}".format(result)
                    line += "\n"
                    output.write(line)

        avg = time_avg(time)
        
        output_path = os.path.join(output_dir, "time_avg.csv")
        with open(output_path, "w") as output:
            output.write("Project, Suite, Time\n")

            for suite, result in avg.items():
                line = "{}".format(project_id)
                line += ", {}".format(display_names[suite])
                line += ", {:.4f}".format(result)
                line += "\n"
                output.write(line)