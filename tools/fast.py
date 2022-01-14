'''
This file is part of an ICSE'22 submission that is currently under review.

It is a modified version of a file from the FAST test case prioritization tool. 
For more information visit: https://github.com/icse18-FAST/FAST.

================================================================

This file contains the core logic of FAST, including:
- Loading and storing test case signatures.
- The FAST-pw algorithm.

Modifications were made to:
- Pre-cache test case signatures (in fast_parser.py).
- Simplify logic/parameters that are unnecessary for Fastazi experiments.

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

from collections import defaultdict
from collections import OrderedDict
from struct import pack, unpack
import os
import random
import sys
import time
import pickle
from glob import glob
from copy import deepcopy

import lsh

'''
This function was modified to allow a list of selected
test cases to be received.
'''
def loadTestSuite(selected, input_dir):
    lsh_files = glob(os.path.join(input_dir, "*.lsh"))
    TS = OrderedDict()
    tcID = 1
    IDmap = {}
    for lshf in lsh_files:
        tcstr, _ = os.path.splitext(os.path.basename(lshf))

        if tcstr in selected:
            with open(lshf, 'rb') as f:
                TS[tcID] = pickle.load(f)
            IDmap[tcID] = tcstr
            tcID += 1

    return TS, IDmap

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


# lsh + pairwise comparison with candidate set
def fast_pw(r, b, test_suite):
    """INPUT
    (str)input_file: path of input file
    (int)r: number of rows
    (int)b: number of bands

    OUTPUT
    (list)P: prioritized test suite
    """
    n = r * b  # number of hash functions

    hashes = [lsh.hashFamily(i) for i in range(n)]

    mh_t = time.process_time()
    tcs_minhashes = deepcopy(test_suite)
    mh_time = time.process_time() - mh_t
    ptime_start = time.process_time()

    tcs = set(tcs_minhashes.keys())

    BASE = 0.5
    SIZE = int(len(tcs)*BASE) + 1

    bucket = lsh.LSHBucket(tcs_minhashes.items(), b, r, n)

    prioritized_tcs = [0]

    # First TC
    selected_tcs_minhash = lsh.tcMinhashing((0, set()), hashes)
    first_tc = random.choice(list(tcs_minhashes.keys()))
    for i in range(n):
        if tcs_minhashes[first_tc][i] < selected_tcs_minhash[i]:
            selected_tcs_minhash[i] = tcs_minhashes[first_tc][i]
    prioritized_tcs.append(first_tc)
    tcs -= set([first_tc])
    del tcs_minhashes[first_tc]

    iteration, total = 0, float(len(tcs_minhashes))
    while len(tcs_minhashes) > 0:
        iteration += 1
        if iteration % 100 == 0:
            sys.stdout.write("  Progress: {}%\r".format(
                round(100*iteration/total, 2)))
            sys.stdout.flush()

        if len(tcs_minhashes) < SIZE:
            bucket = lsh.LSHBucket(tcs_minhashes.items(), b, r, n)
            SIZE = int(SIZE*BASE) + 1

        sim_cand = lsh.LSHCandidates(bucket, (0, selected_tcs_minhash),
                                     b, r, n)
        filtered_sim_cand = sim_cand.difference(prioritized_tcs)
        candidates = tcs - filtered_sim_cand

        if len(candidates) == 0:
            selected_tcs_minhash = lsh.tcMinhashing((0, set()), hashes)
            sim_cand = lsh.LSHCandidates(bucket, (0, selected_tcs_minhash),
                                         b, r, n)
            filtered_sim_cand = sim_cand.difference(prioritized_tcs)
            candidates = tcs - filtered_sim_cand
            if len(candidates) == 0:
                candidates = tcs_minhashes.keys()

        selected_tc, max_dist = random.choice(tuple(candidates)), -1
        for candidate in tcs_minhashes:
            if candidate in candidates:
                dist = lsh.jDistanceEstimate(
                    selected_tcs_minhash, tcs_minhashes[candidate])
                if dist > max_dist:
                    selected_tc, max_dist = candidate, dist

        for i in range(n):
            if tcs_minhashes[selected_tc][i] < selected_tcs_minhash[i]:
                selected_tcs_minhash[i] = tcs_minhashes[selected_tc][i]

        prioritized_tcs.append(selected_tc)
        tcs -= set([selected_tc])
        del tcs_minhashes[selected_tc]

    ptime = time.process_time() - ptime_start

    return mh_time, ptime, prioritized_tcs[1:]


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def fast_(selsize, r, b, test_suite):
    """INPUT
    (str)input_file: path of input file
    (fun)selsize: size of candidate set
    (int)r: number of rows
    (int)b: number of bands

    OUTPUT
    (list)P: prioritized test suite
    """
    n = r * b  # number of hash functions

    hashes = [lsh.hashFamily(i) for i in range(n)]

    mh_t = time.process_time()
    tcs_minhashes = deepcopy(test_suite)
    mh_time = time.process_time() - mh_t
    ptime_start = time.process_time()

    tcs = set(tcs_minhashes.keys())

    BASE = 0.5
    SIZE = int(len(tcs)*BASE) + 1

    bucket = lsh.LSHBucket(tcs_minhashes.items(), b, r, n)

    prioritized_tcs = [0]

    # First TC
    selected_tcs_minhash = lsh.tcMinhashing((0, set()), hashes)
    first_tc = random.choice(list(tcs_minhashes.keys()))
    for i in range(n):
        if tcs_minhashes[first_tc][i] < selected_tcs_minhash[i]:
            selected_tcs_minhash[i] = tcs_minhashes[first_tc][i]
    prioritized_tcs.append(first_tc)
    tcs -= set([first_tc])
    del tcs_minhashes[first_tc]

    iteration, total = 0, float(len(tcs_minhashes))
    while len(tcs_minhashes) > 0:
        iteration += 1
        if iteration % 100 == 0:
            sys.stdout.write("  Progress: {}%\r".format(
                round(100*iteration/total, 2)))
            sys.stdout.flush()

        if len(tcs_minhashes) < SIZE:
            bucket = lsh.LSHBucket(tcs_minhashes.items(), b, r, n)
            SIZE = int(SIZE*BASE) + 1

        sim_cand = lsh.LSHCandidates(bucket, (0, selected_tcs_minhash),
                                     b, r, n)
        filtered_sim_cand = sim_cand.difference(prioritized_tcs)
        candidates = tcs - filtered_sim_cand

        if len(candidates) == 0:
            selected_tcs_minhash = lsh.tcMinhashing((0, set()), hashes)
            sim_cand = lsh.LSHCandidates(bucket, (0, selected_tcs_minhash),
                                         b, r, n)
            filtered_sim_cand = sim_cand.difference(prioritized_tcs)
            candidates = tcs - filtered_sim_cand
            if len(candidates) == 0:
                candidates = tcs_minhashes.keys()

        to_sel = min(selsize(len(candidates)), len(candidates))
        selected_tc_set = random.sample(tuple(candidates), to_sel)

        for selected_tc in selected_tc_set:
            for i in range(n):
                if tcs_minhashes[selected_tc][i] < selected_tcs_minhash[i]:
                    selected_tcs_minhash[i] = tcs_minhashes[selected_tc][i]

            prioritized_tcs.append(selected_tc)
            tcs -= set([selected_tc])
            del tcs_minhashes[selected_tc]

    ptime = time.process_time() - ptime_start

    return mh_time, ptime, prioritized_tcs[1:]
