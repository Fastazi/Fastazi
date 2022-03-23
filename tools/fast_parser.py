'''
This file is part of an AST'22 submission that is currently under review.

================================================================

This script prepares a project for usage with FAST.
It retrieves the list of tests and, for each one, computes
and stores the LSH signature in a .lsh file.

It also utilizes .md5 files to avoid redundant computation
of hashes in subsequent versions of the same project.

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

from collections import defaultdict
import os
import re
import sys
import pickle
from hashlib import md5
from glob import glob
import lsh

from functions import fully_qualified_name

def parse_coverage_info(input_file):
    tc = ""

    with open(input_file) as fin:
        tc = re.sub("\s+", " ", fin.read()).strip()

    if tc == "":
        print (" ----->", "empty coverage:", input_file)
    return tc

def store_md5(md5_path, computed_md5):
    # Generate MD5 hash
    with open(md5_path, 'w') as f_md5:
        f_md5.write(computed_md5)

def compute_lsh(tc, lsh_path):
    r, b = 1, 10
    n = r * b
    hash_functions = [lsh.hashFamily(i) for i in range(n)]

    # Generate LSH hash
    with open(lsh_path, 'wb') as f_lsh:
        shingle = lsh.kShingle(tc, 5)
        minhash = lsh.tcMinhashing(shingle, hash_functions)
        pickle.dump(minhash, f_lsh)

def parseTests(working_dir):

    # Find all files that match the JUnit test pattern
    test_files = glob(os.path.join(working_dir,'**/*Test*.java'), recursive=True)
    # Create FAST hidden dir
    fast_dir = os.path.join(working_dir,'.fast')
    if not os.path.exists(fast_dir):
        os.mkdir(fast_dir)

    tcID = 1
    for test_file in test_files:
        # Extract the code from the test file
        tc = parse_coverage_info(test_file)
        f_name = fully_qualified_name(test_file)

        if (tc == '') or (f_name == ''):
            continue

        md5_path = os.path.join(fast_dir, f_name+'.md5')
        lsh_path = os.path.join(fast_dir, f_name+'.lsh')

        computed_md5 = md5(tc.encode('utf-8')).hexdigest()
        stored_md5 = ""
        if (os.path.isfile(md5_path)):
            # Read MD5 hash from file
            with open(md5_path, 'r') as f_md5:
                stored_md5 = f_md5.read()
        
        if stored_md5 != computed_md5:
            # file was added or changed since last revision
            store_md5(md5_path, computed_md5)
            compute_lsh(tc, lsh_path)

        tcID += 1

if __name__ == '__main__':

    working_dir = '.'
    if len(sys.argv) == 2:
        working_dir = sys.argv[1]
    
    print("Updating FAST dependencies...")
    parseTests(working_dir)
    
