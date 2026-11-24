#!/bin/bash
# (sublinear/cover_ub_validate.sh) usage: gcc -O3 -march=native -fopenmp -o cover_ub cover_ub.c; bash cover_ub_validate.sh ./cover_ub 2 27
# cover_ub proof mode against the D(n) table: Y = D(n) must find a cover (checked), Y = next prime after D(n) must say NO COVER
B=${1:-./cover_ub}; LO=${2:-2}; HI=${3:-27}
declare -A D=([2]=7 [3]=19 [4]=31 [5]=43 [6]=67 [7]=103 [8]=163 [9]=181 [10]=223 [11]=271 [12]=331 [13]=419 [14]=499 [15]=613 [16]=709 [17]=739 [18]=859 [19]=907 [20]=1051 [21]=1213 [22]=1279 [23]=1381 [24]=1471 [25]=1567 [26]=1669 [27]=1801)
nextp() { python3 -c "
import sys; d=int(sys.argv[1]); p=d+2
isp=lambda x: x>1 and all(x%k for k in range(2,int(x**.5)+1))
while not isp(p): p+=2
print(p)" $1; }
ok=1
for n in $(seq $LO $HI); do
  a=$(OMP_NUM_THREADS=${T:-4} $B $n ${D[$n]} proof); b=$(OMP_NUM_THREADS=${T:-4} $B $n $(nextp ${D[$n]}) proof)
  v=$(echo "$a" | python3 -c "
import sys, re
l = sys.stdin.read(); m = re.search(r'Y=(\d+) COVER FOUND', l); vec = re.search(r'vector:(.*)', l)
if not m or not vec: print('NOFOUND'); sys.exit()
Y = int(m.group(1)); cov = [tuple(map(int, t.split(':'))) for t in vec.group(1).split()]
P = [q for q in range(3, Y) if all(q % k for k in range(2, int(q ** .5) + 1))]
print('OK' if all(any(q % r == c for r, c in cov) for q in P) else 'BADVEC')")
  echo "$b" | grep -q "NO COVER" && nb=NOCOVER || nb=BAD
  t1=$(echo "$a" | sed 's/.*nodes=\([0-9]*\) .*/\1/'); t2=$(echo "$b" | sed 's/.*nodes=\([0-9]*\) .*seconds=\([0-9.]*\).*/\1 nodes \2 s/')
  echo "n=$n D=${D[$n]}: at D $v ($t1 nodes), at next prime $nb ($t2)"
  [ "$v" = OK ] && [ $nb = NOCOVER ] || ok=0
done
[ $ok = 1 ] && echo "VALIDATE OK ($LO..$HI)" || echo "VALIDATE FAILED"
