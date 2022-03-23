'''
This file is part of an AST'22 submission that is currently under review.

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
from constants import *
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
method = str_fast_pw

test_suite = {}
id_map = {}
total_time = {}

def bboxPrioritization(iteration):
    global working_dir
    global output_dir
    global id_map

    # Standard FAST parameters
    r, b = 1, 10
    
    print(" Run", iteration)
    
    if method == str_fast_pw:
        stime, ptime, prioritization = fast_pw(
                r, b, test_suite)
    else:
        def one_(x): return 1
        stime, ptime, prioritization = fast_(
                one_, r, b, test_suite)
            

    # writePrioritizedOutput(output_dir, prioritization, iteration)
    out_path = os.path.join(output_dir, str(iteration)+".txt")
    save_file(out_path, map(lambda p: id_map[p], prioritization))
    # out_path = os.path.join(output_dir, str(iteration)+"_ids.txt")
    # save_file(out_path, map(lambda p: "{}".format(p), prioritization))


    print("  Progress: 100%  ")
    print("  Running time:", stime + ptime)
    print("")
    return stime + ptime


if __name__ == "__main__":

    # if len(sys.argv) == 5:
    #     benchmark = sys.argv[4]
    # else:
    #     benchmark = "false"
    if len(sys.argv) > 4 and len(sys.argv) <= 6:
        num_iterations = int(sys.argv[4])
    else:
        num_iterations = 30
    if len(sys.argv) > 3 and len(sys.argv) <= 6:
        what_to_prioritize = sys.argv[1]
        working_dir = sys.argv[2]
        results_dir = sys.argv[3]
    else:
        print("Invalid number of arguments.")
        exit(1)

    fast_dir = os.path.join(working_dir,'.fast')

    if what_to_prioritize == "all":
        suite = str_fast_pw
        tests_path = "all_tests.txt"
    elif what_to_prioritize == "selected":
        suite = str_fastazi_s
        tests_path = "affected_tests.txt"
    else:
        print("Invalid argument for test suite.")
        exit(1)

    # ====
    path = os.path.join(results_dir, tests_path)
    if os.path.exists(path):
        tests = read_file(path)
        test_suite, id_map = loadTestSuite(tests, input_dir=fast_dir)

        # FAST-pw on entire test suite
        output_dir = os.path.join(results_dir, suite)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        num_cores = multiprocessing.cpu_count()
        with Pool(num_cores) as pool:
            running_time = pool.map(bboxPrioritization, range(1, num_iterations + 1))

        total_time = deepcopy(running_time)
    else:
        print("File not found: "+path)
        exit(1)

    # output_path = os.path.join(results_dir, "time", suite+"_time.txt")
    # avg_time = sum(running_time)/len(running_time)
    # with open(output_path, "w") as output:
    #     output.write(str(avg_time))

    # ====
    # path = os.path.join(results_dir, "affected_tests.txt")
    # if os.path.exists(path):
    #     tests = read_file(path)
    #     test_suite, id_map = loadTestSuite(tests, input_dir=fast_dir)

    #     # FAST-pw on selected test suite (a.k.a. Fastazi-S)
    #     output_dir = os.path.join(results_dir, str_fastazi_s)
    #     if not os.path.exists(output_dir):
    #         os.makedirs(output_dir)
    #     num_cores = multiprocessing.cpu_count()
    #     with Pool(num_cores) as pool:
    #         running_time = pool.map(bboxPrioritization, range(1, num_iterations + 1))

    #     total_time[str_fastazi_s] = deepcopy(running_time)
    # else:
    #     print("Could not use '"+display_names[str_fastazi_s]+"'.")

    # for suite, running_time in total_time.items():
    #     output_path = os.path.join(results_dir, "time", suite+"_time.txt")
    #     avg_time = sum(running_time)/len(running_time)
    #     with open(output_path, "w") as output:
    #         output.write(str(avg_time))

    # output_path = os.path.join(results_dir, "prioritization_time.csv")
    # with open(output_path, "w") as output:
    #     output.write("Suite, iteration, time")
    #     for suite, running_time in total_time.items():
    #         for i in range(0, len(running_time)):
    #             line = "{}".format(suite)
    #             line += ", {}".format(i+1)
    #             line += ", {}".format(running_time[i])
    #             line += "\n"
    #             output.write(line)