#!/bin/sh
# ptcover_fast must print exactly what ptcover_ref prints, and write the same PT_DUMP file, for the same seed.
# usage: ./test_identical.sh moduli_dir   (a directory with c3_moduli.txt c3_moduli_only.txt first88.txt m13.txt betas56.txt betas13.txt,
#        all in goldbach/fscan/cover of branch ccr-d4a17dd0-7uu03r)
D=${1:-.}
set -e
cd "$(dirname "$0")"
gcc -O3 -march=native -fopenmp -o ptcover_ref ptcover_ref.c -lm
gcc -O3 -march=native -fopenmp -o ptcover_fast ptcover_fast.c -lm
ok=1
for args in "10007 $D/m13.txt 3000 1 $D/betas13.txt" "10007 $D/m13.txt 3000 5 $D/betas13.txt" "122000 $D/c3_moduli.txt 400 3 $D/betas56.txt" \
            "150000 $D/first88.txt 300 2 $D/betas56.txt" "140000 $D/c3_moduli_only.txt 600 11 $D/betas56.txt"; do
    OMP_NUM_THREADS=4 ./ptcover_ref $args > /tmp/pt_a.txt 2>/dev/null
    OMP_NUM_THREADS=4 ./ptcover_fast $args > /tmp/pt_b.txt 2>/dev/null
    if cmp -s /tmp/pt_a.txt /tmp/pt_b.txt; then echo "identical: $args"; else echo "DIFFERENT: $args"; ok=0; fi
done
rm -f /tmp/pt_da.txt /tmp/pt_db.txt
PT_DUMP=/tmp/pt_da.txt PT_KDUMP=1075 OMP_NUM_THREADS=4 ./ptcover_ref 140000 $D/c3_moduli_only.txt 1500 9 $D/betas56.txt > /dev/null 2>&1
PT_DUMP=/tmp/pt_db.txt PT_KDUMP=1075 OMP_NUM_THREADS=4 ./ptcover_fast 140000 $D/c3_moduli_only.txt 1500 9 $D/betas56.txt > /dev/null 2>&1
if cmp -s /tmp/pt_da.txt /tmp/pt_db.txt; then echo "PT_DUMP files identical ($(wc -l < /tmp/pt_da.txt) covers)"; else echo "PT_DUMP files DIFFERENT"; ok=0; fi
[ $ok = 1 ] && echo ALL IDENTICAL || { echo FAILED; exit 1; }
