#!/bin/sh
# Regenerates every number of the page into results_*.txt (about 4 minutes on a busy core).
cd "$(dirname "$0")"
python3 tests_small.py > results_tests_small.txt 2>&1
python3 real_w1.py > results_w1.txt 2>&1
python3 levels.py > results_levels.txt 2>&1
: > results_mitm.txt; : > results_dp.txt
for a in "3 0" "3 2" "4 1" "4 3" "5 2" "5 4" "6 5"; do set -- $a; python3 real_mitm.py $1 $2 $2 bf >> results_mitm.txt 2>&1; echo >> results_mitm.txt; done
LCAP=5 python3 real_mitm.py 7 6 6 >> results_mitm.txt 2>&1; echo >> results_mitm.txt
echo "---- uncertified, balanced lists (prod)" >> results_mitm.txt
for a in "5 1 2" "6 2 3" "7 4 4"; do python3 real_mitm.py $a prod >> results_mitm.txt 2>&1; echo >> results_mitm.txt; done
for a in "3 0" "3 2" "4 1" "4 3" "5 2" "5 4"; do set -- $a; python3 real_dp.py $1 $2 1 >> results_dp.txt 2>&1; python3 real_dp.py $1 $2 1 frozen >> results_dp.txt 2>&1; echo >> results_dp.txt; done
python3 real_dp.py 4 3 1/4 >> results_dp.txt 2>&1
python3 dz.py > results_dz.txt 2>&1
python3 ap_lists.py > results_ap_lists.txt 2>&1
python3 extras.py > results_extras.txt 2>&1
python3 spread.py > results_spread.txt 2>&1
echo done > results_done.txt
