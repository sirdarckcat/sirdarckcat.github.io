#!/bin/bash
# T5 (c): four anneals for the 629-moduli cover, one core each: the 5,113 recipe from greedy + descent (two seeds), and 20k sweeps
# from the 5,113 cover restricted to the moduli up to 4,657 (two seeds). heatbath2 (table weights).
HB=../heatbath2; Q=1000003
( $HB $Q gd4657.txt 3000 2.0 6.0 1 gd_a1.txt 2> gd_a1.log && $HB $Q gd_a1.txt 20000 1.8 10.0 1 gd_b1.txt 2> gd_b1.log ) &
( $HB $Q gd4657.txt 3000 2.0 6.0 2 gd_a2.txt 2> gd_a2.log && $HB $Q gd_a2.txt 20000 1.8 10.0 2 gd_b2.txt 2> gd_b2.log ) &
( $HB $Q restr4657.txt 20000 1.8 10.0 1 rs_b1.txt 2> rs_b1.log ) &
( $HB $Q restr4657.txt 20000 1.8 10.0 2 rs_b2.txt 2> rs_b2.log ) &
wait
for f in gd_a1 gd_a2 gd_b1 gd_b2 rs_b1 rs_b2; do echo "$f: $(head -1 $f.txt | sed 's/.*rows in no class: \([0-9]*\).*/\1/')"; done
