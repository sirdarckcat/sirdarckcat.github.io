#!/bin/bash
# pass 2: for every monic N, the rows-left counts s_t, o_t at the levels R (survival 10^-2 .. 10^-6 and the maximum)
cd "$(dirname "$0")"
./gfgold 3 15 lev_3_15 104 173 243 306 382 481
./gfgold 5 10 lev_5_10 45 69 95 123 155 206
./gfgold 7 9 lev_7_9 38 58 77 97 115 136
./gfgold 9 8 lev_9_8 33 49 66 83 103 122
./gfgold 5 11 lev_5_11 49 77 107 135 163 201
./gfgold 3 16 lev_3_16 111 187 265 336 405 476
./gfgold 3 12 lev_3_12 60 100 150 200 250 313
./gfgold 7 7 lev_7_7 20 30 40 50 60 78
./gfgold 9 6 lev_9_6 20 30 45 60 80 120
echo done > pass2_done.txt
