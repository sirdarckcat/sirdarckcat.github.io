#!/bin/bash
cd "$(dirname "$0")"
python3 m1_size.py > logs/m1_size_ABC.log 2>&1
python3 sq_family.py > logs/squares_family_A.log 2>&1
python3 nbr.py > logs/neighbours_success_seeded_ABC.log 2>&1
python3 funnel_eval.py B C > logs/funnel_out_of_sample_BC.log 2>&1
python3 bayes_an.py bayesA.bin > logs/bayes_bound_A.log 2>&1
python3 bayes_an.py bayesB.bin > logs/bayes_bound_B.log 2>&1
python3 fam_blk.py > logs/block_family_A.log 2>&1
python3 fam_blk2.py B 1000 > logs/block_family_B.log 2>&1
python3 fam_blk2.py C 900 > logs/block_family_C.log 2>&1
python3 half_prime.py A B C > logs/half_prime_ABC.log 2>&1
python3 nbr4_drive.py A 1000000000 1000 26,27,28,29,30,31,32 5 50 > logs/nbr4_A.log 2>&1
python3 nbr4_drive.py A 1000000000 1000 28,30,32 3,7 50,70 > logs/nbr4_A_J_cmin_grid.log 2>&1
echo done > logs/DONE
