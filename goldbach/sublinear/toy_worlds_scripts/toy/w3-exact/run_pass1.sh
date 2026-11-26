#!/bin/bash
# pass 1 (G, D for every monic N) for every instance; one core, sequential
cd "$(dirname "$0")"
for qn in "3 3" "3 4" "3 5" "3 6" "3 7" "3 8" "3 9" "3 10" "3 11" "3 12" "3 13" "3 14" "3 15" "3 16" \
          "5 3" "5 4" "5 5" "5 6" "5 7" "5 8" "5 9" "5 10" "5 11" \
          "7 3" "7 4" "7 5" "7 6" "7 7" "7 8" "7 9" \
          "9 3" "9 4" "9 5" "9 6" "9 7" "9 8" \
          "3 17" "5 12" "7 10" "9 9" "3 18"; do
  set -- $qn
  s=$(date +%s.%N); ./gfgold $1 $2 out_$1_$2; e=$(date +%s.%N); echo "$1 $2 $(echo "$e - $s" | bc) s" >> pass1_times.txt
done
echo done >> pass1_times.txt
