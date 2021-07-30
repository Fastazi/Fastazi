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
import time

if __name__ == '__main__':
    working_dir = '.'
    if len(sys.argv) == 3:
        working_dir = sys.argv[1]
        method = sys.argv[2]
    
    selected_path = os.path.join(working_dir, "affected_tests.txt")

    prioritized_dir = os.path.join(working_dir, "fast_"+method)
    combined_dir = os.path.join(working_dir, "fastazi_"+method)
    remaining_dir = os.path.join(working_dir, "remaining_"+method)

    selected = read_file(selected_path)

    iteration_time = []
    for i in range(1, 31):
        start = time.perf_counter()

        prioritized_path = os.path.join(prioritized_dir, str(i)+".txt")
        prioritized = read_file(prioritized_path)

        combined = []
        remaining = []
        for test in prioritized:
            if test in selected:
                combined.append(test)
            else:
                remaining.append(test)

        combined_path = os.path.join(combined_dir, str(i)+".txt")
        save_file(combined_path, combined)

        remaining_path = os.path.join(remaining_dir, str(i)+".txt")
        save_file(remaining_path, remaining)

        iteration_time.append(time.perf_counter() - start)

    output_path = os.path.join(working_dir, "time", "fastazi_"+method+"_time.txt")
    avg_time = sum(iteration_time)/len(iteration_time)
    with open(output_path, "w") as output:
        output.write(str(avg_time))
