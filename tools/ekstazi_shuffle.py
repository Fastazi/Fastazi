'''
This file is part of an ICSE'22 submission that is currently under review.

================================================================

This script generates multiple shuffled orderings of the
list of test cases selected by Ekstazi.

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

import os
import sys
import random

from functions import read_file, save_file
from constants import *

def ekstazi_rand(working_dir):
    # Shuffle tests selected by Ekstazi
    selected_path = os.path.join(working_dir, "affected_tests.txt")
    output_dir = os.path.join(working_dir, str_ekstazi)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
   
    if os.path.exists(selected_path):
        selected = read_file(selected_path)
        # Create 30 permutations of the test suite.
        for i in range(1, 31):
            random.shuffle(selected)
            output_path = os.path.join(output_dir, str(i)+".txt")
            save_file(output_path, selected)

def randomize(working_dir):
    # Shuffle all tests
    tests_path = os.path.join(working_dir, "all_tests.txt")
    output_dir = os.path.join(working_dir, str_random)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if os.path.exists(tests_path):
        tests = read_file(tests_path)
        # Create 30 permutations of the test suite.
        for i in range(1, 31):
            random.shuffle(tests)
            output_path = os.path.join(output_dir, str(i)+".txt")
            save_file(output_path, tests)


if __name__ == '__main__':

    working_dir = '.'
    if len(sys.argv) == 2:
        working_dir = sys.argv[1]
    
    random.seed(2)

    ekstazi_rand(working_dir)
    randomize(working_dir)