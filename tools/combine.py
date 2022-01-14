'''
This file is part of an ICSE'22 submission that is currently under review.

================================================================

This script retrieves test suites selected/prioritized by 
Ekstazi/FAST and combines them into a single test suite.

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

from functions import read_file, save_file
from constants import *
import time

if __name__ == '__main__':
    working_dir = '.'
    if len(sys.argv) == 2:
        working_dir = sys.argv[1]
    
    selected_path = os.path.join(working_dir, "affected_tests.txt")

    prioritized_dir = os.path.join(working_dir, str_fast_pw)
    combined_dir = os.path.join(working_dir, str_fastazi_p)

    selected = read_file(selected_path)

    iteration_time = []
    for i in range(1, 31):
        # start = time.process_time()

        prioritized_path = os.path.join(prioritized_dir, str(i)+".txt")
        prioritized = read_file(prioritized_path)

        combined = []
        # Take the selected tests according to the prioritized order.
        for test in prioritized:
            if test in selected:
                combined.append(test)

        combined_path = os.path.join(combined_dir, str(i)+".txt")
        save_file(combined_path, combined)

        # iteration_time.append(time.process_time() - start)

    # output_path = os.path.join(working_dir, "time", str_fastazi_p+"_time.txt")
    # avg_time = sum(iteration_time)/len(iteration_time)
    # with open(output_path, "w") as output:
    #     output.write(str(avg_time))
