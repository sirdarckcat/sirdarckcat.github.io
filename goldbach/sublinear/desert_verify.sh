#!/bin/bash
# (sublinear/desert_verify.sh) e.g. gcc -O3 -march=native -fopenmp -o desert_fast5 desert_fast5.c && bash desert_verify.sh ./desert_fast5 19 20 20
# verify a desert build against the table: D(1..LIM) found from scratch, counts n = 2..CLIM, proofs (next prime) n = 2..PLIM
B=$1; LIM=${2:-19}; CLIM=${3:-20}; PLIM=${4:-20}; T=${T:-4}
declare -A D=([1]=5 [2]=7 [3]=19 [4]=31 [5]=43 [6]=67 [7]=103 [8]=163 [9]=181 [10]=223 [11]=271 [12]=331 [13]=419 [14]=499 [15]=613 [16]=709 [17]=739 [18]=859 [19]=907 [20]=1051 [21]=1213)
declare -A C=([2]=2 [3]=1 [4]=2 [5]=2 [6]=6 [7]=6 [8]=1 [9]=2 [10]=1 [11]=17 [12]=9 [13]=2 [14]=1 [15]=3 [16]=2 [17]=2 [18]=4 [19]=2 [20]=1)
declare -A NX=([2]=11 [3]=23 [4]=37 [5]=47 [6]=71 [7]=107 [8]=167 [9]=191 [10]=227 [11]=277 [12]=337 [13]=421 [14]=503 [15]=617 [16]=719 [17]=743 [18]=863 [19]=911 [20]=1061 [21]=1217)
ok=1; out=$(mktemp)
for n in $(seq 1 $LIM); do OMP_NUM_THREADS=$T $B $n > $out.l 2>&1; cat $out.l >> $out; d=$(sed -n 's/.* D=\([0-9]*\) .*/\1/p' $out.l | head -1); [ "$d" = "${D[$n]}" ] || { echo "D($n): got '$d' want ${D[$n]}"; ok=0; }; done
python3 "$(dirname "$0")/desert_check.py" < $out | tail -1
for n in $(seq 2 $CLIM); do r=$(OMP_NUM_THREADS=$T $B $n ${D[$n]} 3 count 2>&1); c=$(echo "$r" | sed -n 's/.*optimal vectors=\([0-9]*\) above D=\([0-9]*\).*/\1 \2/p'); [ "$c" = "${C[$n]} 0" ] || { echo "count($n): got '$c' want ${C[$n]} 0"; ok=0; }; done
for n in $(seq 2 $PLIM); do r=$(OMP_NUM_THREADS=$T $B $n ${NX[$n]} 2>&1); echo "$r" | grep -q "NOT ATTAINED" || { echo "proof($n): $r"; ok=0; }; done
[ $ok = 1 ] && echo "VERIFY OK $B (D 1..$LIM, counts 2..$CLIM, proofs 2..$PLIM)" || echo "VERIFY FAILED $B"
rm -f $out $out.l
