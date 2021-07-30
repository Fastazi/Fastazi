defects4j checkout -p Chart -v 1f -w fast_benchmark

cp repos/Chart/26_results/all_tests.txt fast_benchmark 

python3 tools/fast_parser.py fast_benchmark
python3 tools/prioritize.py fast_benchmark fast_benchmark 24 true

# mv FAST/input/chart_v0/chart-bbox.txt FAST/input/chart_v0/chart-bbox.old
# cp fast_benchmark/.fast/bbox.txt FAST/input/chart_v0/chart-bbox.txt

# cd FAST
# rm -r output/chart_v0
# python py/prioritize.py chart_v0 bbox FAST-pw 24
# cd ..
