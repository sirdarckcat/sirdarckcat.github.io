#!/bin/bash
# T5 next sizes (run from run/): 20k-sweep anneals for 1,500 digits (491 moduli, from hb3527_a1) and 1,800 digits (574 moduli, from hb4657_rs1
# restricted to the moduli up to 4,201), two seeds each, one core each.
HB=../heatbath2; Q=1000003
$HB $Q ../hb3527_a1.txt 20000 1.8 10.0 1 x3527_b1.txt 2> x3527_b1.log &
$HB $Q ../hb3527_a1.txt 20000 1.8 10.0 2 x3527_b2.txt 2> x3527_b2.log &
$HB $Q restr4201.txt 20000 1.8 10.0 1 x4201_b1.txt 2> x4201_b1.log &
$HB $Q restr4201.txt 20000 1.8 10.0 2 x4201_b2.txt 2> x4201_b2.log &
wait
for f in x3527_b1 x3527_b2 x4201_b1 x4201_b2; do echo "$f: $(head -1 $f.txt | sed 's/.*rows in no class: \([0-9]*\).*/\1/') (start $(head -1 $f.log | sed 's/.*start: //'))"; done
