'''
This file is part of an ICSE'22 submission that is currently under review.

It is a modified version of a file from the FAST test case prioritization tool. 
For more information visit: https://github.com/icse18-FAST/FAST.

================================================================

This file is the entry point of FAST. It executes FAST in four modes:
- FAST_pw on the entire test suite;
- FAST_1 on the entire test suite;
- FAST_pw on the selected test suite;
- FAST_1 on the selected test suite.

Modifications were made to:
- Use the multiprocessing library to parallelize iterations.
- Output the prioritized test suite in a format compatible with Ekstazi.
- Simplify logic/parameters that are unnecessary for Fastazi experiments.

================================================================

This is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as 
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this source.  If not, see <http://www.gnu.org/licenses/>.
'''

# import math
import os
# import pickle
import sys
from copy import deepcopy

from fast import fast_pw, fast_, loadTestSuite
from functions import read_file, save_file
# import metric

import fast_parser

# Multiprocessing tools
import multiprocessing
from multiprocessing import Pool
# from functools import partial
# from contextlib import contextmanager


usage = """USAGE: python prioritize.py <working_dir> <results_dir> <repetitions> <benchmark>
OPTIONS:
  <working_dir>: project directory to prioritize.
    Must contain a .fast subdirectory created by fast_parser.py.
  <results_dir>: directory to store prioritized test suites.
  <repetitions>: number of prioritization to compute.
    options: positive integer value, e.g. 30.
  <benchmark>: only used for testing purposes. Default: False.
  
NOTE:
  STR, I-TSD are BB prioritization only.
  ART-D, ART-F, GT, GA, GA-S are WB prioritization only."""

working_dir = '.'
output_dir = '.'
method = "fast_pw"

test_suite = {}
id_map = {}
total_time = {}

def bboxPrioritization(iteration):
    global working_dir
    global output_dir
    global id_map

    # Standard FAST parameters
    k, r, b = 5, 1, 10
    
    print(" Run", iteration)
    
    if method == "fast_pw":
        stime, ptime, prioritization = fast_pw(
                r, b, test_suite, k=k)
    else:
        def one_(x): return 1
        stime, ptime, prioritization = fast_(
                one_, r, b, test_suite, k=k)
            

    # writePrioritizedOutput(output_dir, prioritization, iteration)
    out_path = os.path.join(output_dir, str(iteration)+".txt")
    save_file(out_path, map(lambda p: id_map[p], prioritization))


    print("  Progress: 100%  ")
    print("  Running time:", stime + ptime)
    # running_time[iteration] = stime + ptime
    print("")
    return stime + ptime

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# def writePrioritizedOutput(path, prioritization, iteration):
#     out_path = os.path.join(path, str(iteration)+".txt")
#     with open(out_path, "w") as out_file:
#         out_file.write("\n".join(prioritization))
#         for p in prioritization:
#             out_file.write(id_map[p]+"\n")

# def writePrioritization(path, name, ctype, run, prioritization):
#     fout = "{}/{}-{}-{}.pickle".format(path, name, ctype, run+1)
#     pickle.dump(prioritization, open(fout, "wb"))


# def writeOutput(outpath, ctype, res, javaFlag):
#     if javaFlag:
#         name, stimes, ptimes, apfds = res
#         fileout = "{}/{}-{}.tsv".format(outpath, name, ctype)
#         with open(fileout, "w") as fout:
#             fout.write("SignatureTime\tPrioritizationTime\tAPFD\n")
#             for st, pt, apfdlist in zip(stimes, ptimes, apfds):
#                 for apfd in apfdlist:
#                     tsvLine = "{}\t{}\t{}\n".format(st, pt, apfd)
#                     fout.write(tsvLine)
#     else:
#         name, stimes, ptimes, apfds = res
#         fileout = "{}/{}-{}.tsv".format(outpath, name, ctype)
#         with open(fileout, "w") as fout:
#             fout.write("SignatureTime\tPrioritizationTime\tAPFD\n")
#             for st, pt, apfd in zip(stimes, ptimes, apfds):
#                 tsvLine = "{}\t{}\t{}\n".format(st, pt, apfd)
#                 fout.write(tsvLine)

# def read_file(file_path):
#     test_cases = []
#     with open(file_path, "r") as f:
#         return map(lambda line: line.strip(), f.readlines())
#     return test_cases

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


if __name__ == "__main__":

    if len(sys.argv) == 5:
        benchmark = sys.argv[4]
    else:
        benchmark = "false"
    if len(sys.argv) > 3 and len(sys.argv) <= 5:
        num_iterations = int(sys.argv[3])
    else:
        num_iterations = 30
    if len(sys.argv) > 2 and len(sys.argv) <= 5:
        working_dir = sys.argv[1]
        results_dir = sys.argv[2]
    else:
        exit(0)

    # If selection failed, skip this version
    # if (not os.path.exists(os.path.join(working_dir, ".ekstazi"))):
    #     print("Selection failed, skipping prioritization")
    #     exit(0)

    # measure time
    # fast_parser.parseTests(working_dir)

    # ====
    fast_dir = os.path.join(working_dir,'.fast')
    all_path = os.path.join(results_dir, "all_tests.txt")
    all_tests = read_file(all_path)
    test_suite, id_map = loadTestSuite(all_tests, input_dir=fast_dir)

    # FAST-pw on entire test suite
    output_dir = os.path.join(results_dir, "fast_pw")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    num_cores = multiprocessing.cpu_count()
    with Pool(num_cores) as pool:
        running_time = pool.map(bboxPrioritization, range(1, num_iterations + 1))

    total_time["fast_pw"] = deepcopy(running_time)

    if benchmark == "true":
        # When benchmarking, we only want to run fast_pw.
        exit(0)

    # FAST-1 on entire test suite
    output_dir = os.path.join(results_dir, "fast_1")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    method = "fast_1"
    num_cores = multiprocessing.cpu_count()
    with Pool(num_cores) as pool:
        running_time = pool.map(bboxPrioritization, range(1, num_iterations + 1))

    total_time["fast_1"] = deepcopy(running_time)

    # ====
    selected_path = os.path.join(results_dir,"affected_tests.txt")
    if os.path.exists(selected_path):
        selected = read_file(selected_path)
        test_suite, id_map = loadTestSuite(selected, input_dir=fast_dir)

        # FAST-pw on selected test suite
        output_dir = os.path.join(results_dir, "efast_pw")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        method = "fast_pw"
        num_cores = multiprocessing.cpu_count()
        with Pool(num_cores) as pool:
            running_time = pool.map(bboxPrioritization, range(1, num_iterations + 1))

        total_time["efast_pw"] = deepcopy(running_time)

        # FAST-1 on selected test suite
        output_dir = os.path.join(results_dir, "efast_1")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        method = "fast_1"
        num_cores = multiprocessing.cpu_count()
        with Pool(num_cores) as pool:
            running_time = pool.map(bboxPrioritization, range(1, num_iterations + 1))

        total_time["efast_1"] = deepcopy(running_time)
    else:
        print("Could not use 'efast'.")

    for suite, running_time in total_time.items():
        output_path = os.path.join(results_dir, "time", suite+"_time.txt")
        avg_time = sum(running_time)/len(running_time)
        with open(output_path, "w") as output:
            output.write(str(avg_time))

    output_path = os.path.join(results_dir, "prioritization_time.csv")
    with open(output_path, "w") as output:
        output.write("Suite, iteration, time")
        for suite, running_time in total_time.items():
            for i in range(0, len(running_time)):
                line = "{}".format(suite)
                line += ", {}".format(i+1)
                line += ", {}".format(running_time[i])
                line += "\n"
                output.write(line)