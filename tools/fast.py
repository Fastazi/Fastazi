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


# def loadTestSuitev2(input_dir):
#     lsh_files = glob(os.path.join(input_dir, "*.lsh"))
#     TS = OrderedDict()
#     tcID = 0
#     IDmap = {}
#     for lshf in lsh_files:
#         tcstr, _ = os.path.splitext(os.path.basename(lshf))

#         with open(lshf, 'rb') as f:
#             TS[tcID] = pickle.load(f)
#         IDmap[tcID] = tcstr
#         tcID += 1
    
#     return TS, IDmap

# def loadTestSuite(input_file, bbox=False, k=5):
#     """INPUT
#     (str)input_file: path of input file

#     OUTPUT
#     (dict)TS: key=tc_ID, val=set(covered lines)
#     """
#     TS = defaultdict()
#     with open(input_file) as fin:
#         tcID = 1
#         for tc in fin:
#             if bbox:
#                 TS[tcID] = tc[:-1]
#             else:
#                 TS[tcID] = set(tc[:-1].split())
#             tcID += 1
#     shuffled = TS.items()
#     random.shuffle(shuffled)
#     TS = OrderedDict(shuffled)
#     if bbox:
#         TS = lsh.kShingles(TS, k)
#     return TS


# def storeSignatures(input_file, sigfile, hashes, k=5):
#     with open(sigfile, "w") as sigfile:
#         with open(input_file) as fin:
#             tcID = 1
#             for tc in fin:
#                 if bbox:
#                     # shingling
#                     tc_ = tc[:-1]
#                     tc_shingles = set()
#                     for i in range(len(tc_) - k + 1):
#                         tc_shingles.add(hash(tc_[i:i + k]))

#                     sig = lsh.tcMinhashing((tcID, set(tc_shingles)), hashes)
#                 else:
#                     tc_ = tc[:-1].split()
#                     sig = lsh.tcMinhashing((tcID, set(tc_)), hashes)
#                 for hash_ in sig:
#                     sigfile.write(repr(unpack('>d', hash_)[0]))
#                     sigfile.write(" ")
#                 sigfile.write("\n")
#                 tcID += 1


# def loadSignatures(input_file):
#     """INPUT
#     (str)input_file: path of input file

#     OUTPUT
#     (dict)TS: key=tc_ID, val=set(covered lines), sigtime"""
#     sig = {}
#     start = time.perf_counter()
#     with open(input_file, "r") as fin:
#         tcID = 1
#         for tc in fin:
#             sig[tcID] = [pack('>d', float(i)) for i in tc[:-1].split()]
#             tcID += 1
#     return sig, time.perf_counter() - start


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


# lsh + pairwise comparison with candidate set
def fast_pw(r, b, test_suite, k=5):
    """INPUT
    (str)input_file: path of input file
    (int)r: number of rows
    (int)b: number of bands
    (bool)bbox: True if BB prioritization
    (int)k: k-shingle size (for BB prioritization)
    (bool)memory: if True keep signature in memory and do not store them to file

    OUTPUT
    (list)P: prioritized test suite
    """
    random.seed(2)
    n = r * b  # number of hash functions

    hashes = [lsh.hashFamily(i) for i in range(n)]

    # test_suite = loadTestSuitev2(input_dir=input_file)
    # print(test_suite)
    # test_suite = loadTestSuite(input_file, bbox=bbox, k=k)
    # generate minhashes signatures
    mh_t = time.perf_counter()
    tcs_minhashes = deepcopy(test_suite)
    # tcs_minhashes = {tc[0]: lsh.tcMinhashing(tc, hashes)
                    #  for tc in test_suite.items()}
    mh_time = time.perf_counter() - mh_t
    ptime_start = time.perf_counter()

    # else:
    #     # loading input file and generating minhashes signatures
    #     sigfile = input_file.replace(".txt", ".sig")
    #     sigtimefile = "{}_sigtime.txt".format(input_file.split(".")[0])
    #     if not os.path.exists(sigfile):
    #         mh_t = time.perf_counter()
    #         storeSignatures(input_file, sigfile, hashes, bbox, k)
    #         mh_time = time.perf_counter() - mh_t
    #         with open(sigtimefile, "w") as fout:
    #             fout.write(repr(mh_time))
    #     else:
    #         with open(sigtimefile, "r") as fin:
    #             mh_time = eval(fin.read().replace("\n", ""))

    #     ptime_start = time.perf_counter()
    #     tcs_minhashes, load_time = loadSignatures(sigfile)

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

    ptime = time.perf_counter() - ptime_start

    return mh_time, ptime, prioritized_tcs[1:]


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def fast_(selsize, r, b, test_suite, k=5):
    """INPUT
    (str)input_file: path of input file
    (fun)selsize: size of candidate set
    (int)r: number of rows
    (int)b: number of bands
    (bool)bbox: True if BB prioritization
    (int)k: k-shingle size (for BB prioritization)
    (bool)memory: if True keep signature in memory and do not store them to file

    OUTPUT
    (list)P: prioritized test suite
    """
    random.seed(2)
    n = r * b  # number of hash functions

    hashes = [lsh.hashFamily(i) for i in range(n)]

    # test_suite = loadTestSuitev2(input_dir=input_file)
    # test_suite = loadTestSuite(input_file, bbox=bbox, k=k)
    # generate minhashes signatures
    mh_t = time.perf_counter()
    tcs_minhashes = deepcopy(test_suite)
    mh_time = time.perf_counter() - mh_t
    ptime_start = time.perf_counter()

    # else:
    #     # loading input file and generating minhashes signatures
    #     sigfile = input_file.replace(".txt", ".sig")
    #     sigtimefile = "{}_sigtime.txt".format(input_file.split(".")[0])
    #     if not os.path.exists(sigfile):
    #         mh_t = time.perf_counter()
    #         storeSignatures(input_file, sigfile, hashes, bbox, k)
    #         mh_time = time.perf_counter() - mh_t
    #         with open(sigtimefile, "w") as fout:
    #             fout.write(repr(mh_time))
    #     else:
    #         with open(sigtimefile, "r") as fin:
    #             mh_time = eval(fin.read().replace("\n", ""))

    #     ptime_start = time.perf_counter()
    #     tcs_minhashes, load_time = loadSignatures(sigfile)

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

    ptime = time.perf_counter() - ptime_start

    return mh_time, ptime, prioritized_tcs[1:]
