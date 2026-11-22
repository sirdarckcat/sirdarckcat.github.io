#!/bin/bash
# selftest_ab.sh [OLDREV]   (default OLDREV = e383cbc)
# Correctness and speed of THIS directory against an older revision, on this machine; about 12 minutes.
# Needs git, gcc with OpenMP, python3 with gmpy2 (pip install gmpy2).  It builds in a temporary directory and does not
# touch your working tree.  Run it on a quiet machine, or pin it with:  CPU=3 ./selftest_ab.sh
#   1. test_fermat.py and stress_fermat.py (the Fermat kernel against pow(2, n-1, n), 118,000 + 10,000 numbers)
#   2. check_record.sh (the record N = 83668534093338795647672 must be reported, 111 rows proved composite)
#   3. check_small.py (end-to-end against brute force)
#   4. the Fermat kernel alone, old and new, 62/70/77-bit numbers (TSC cycles a number, min of 7 runs)
#   5. the whole scanner, interleaved, old revision, each later commit that changes code, the working tree (bench_ab.py,
#      TSC cycles a member)
#   6. the three score-table schemes (SCORE_MODE 0, 1, 2) of the working tree
OLD=${1:-e383cbc}
CPU=${CPU:-2}
HERE=$(cd "$(dirname "$0")" && pwd)
cd "$HERE"
T=$(mktemp -d /tmp/selftest_ab.XXXXXX)
CC=${CC:-gcc}; FLAGS=${FLAGS:--O3 -march=native}
RUN="env"; command -v taskset >/dev/null && RUN="taskset -c $CPU"
echo "== machine: $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2) | isa: $(grep -m1 '^flags' /proc/cpuinfo | grep -o -w -E 'avx2|avx512f|avx512bw|avx512ifma' | sort -u | tr '\n' ' ')| $($CC --version | head -1)"
echo "== old revision: $OLD  new: $(git -C "$HERE" rev-parse --short HEAD 2>/dev/null)$(git -C "$HERE" diff --quiet -- . 2>/dev/null || echo '+local changes')"
fail=0
echo "== 1. Fermat kernel against Python"
$CC $FLAGS -Wall -o $T/tf test_fermat.c || exit 1
python3 test_fermat.py 1 $T/tf 16 | tail -1 || fail=1
python3 stress_fermat.py $T/tf 1 16 | sed 's/^.*: structured/structured/' || fail=1
$CC -O2 -o $T/tfc test_fm_common.c && $T/tfc | tail -1 | grep -q " 0 mismatches" && echo "fm_common exponent words: 0 mismatches" || { echo "fm_common exponent words: FAILED"; fail=1; }
echo "== 2. the record"
$CC $FLAGS -fopenmp -Wno-unused-result -o $T/fscan fscan.c -lm || exit 1
./check_record.sh $T/fscan | tail -1 || fail=1
echo "== 3. end to end against brute force (check_small.py)"
FSCAN=$T/fscan python3 check_small.py 2>&1 | tail -2 | cut -c1-150 || fail=1
echo "== 4. the Fermat kernel alone (TSC cycles a number, setup included, min of 7)"
mkdir -p $T/old && for f in test_fermat.c fermat26.h fermat52.h fm_common.h; do git show $OLD:goldbach/fscan/$f > $T/old/$f 2>/dev/null || [ $f = fm_common.h ] || exit 1; done
$CC $FLAGS -o $T/tf_old $T/old/test_fermat.c || exit 1
for b in 62 70 77; do
  for k in old new; do
    exe=$T/tf; [ $k = old ] && exe=$T/tf_old
    best=$(for r in 1 2 3 4 5 6 7; do $RUN $exe --time $b | awk '{print $3}'; done | sort -n | head -1)
    printf "   %2d-bit %s: %s\n" $b $k $best
  done
done
echo "== 5. the whole scanner, interleaved (class 194 slice), one line a commit that changes the code, then the working tree"
REVS=$(git -C "$HERE" rev-list --reverse --abbrev-commit $OLD..HEAD -- fscan.c fermat26.h fermat52.h fm_common.h 2>/dev/null | tr '\n' ' ')
python3 bench_ab.py $OLD $REVS WORK --cpu $CPU --rounds 5 | tail -$(( $(echo $REVS | wc -w) + 4 )) || fail=1
echo "== 6. the score-table schemes of this working tree (SCORE_MODE 0 = periodic tables, 1 = offsets, 2 = packed offsets)"
python3 bench_ab.py WORK@-DSCORE_MODE=0 WORK@-DSCORE_MODE=1 WORK@-DSCORE_MODE=2 --cpu $CPU --rounds 5 | tail -4 || fail=1
[ $fail = 0 ] && echo "== ALL CHECKS PASSED" || echo "== SOMETHING FAILED (see above)"
rm -rf $T
exit $fail
