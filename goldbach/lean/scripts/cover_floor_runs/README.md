# Output of the research session's `cover_floor` runs

Raw output files, produced on this branch's machine at the research session's request (24 November
2026) and not interpreted here. The program and its parameter file are that session's
(`goldbach/sublinear/cover_floor.c`, `cover_floor.py`, `cover_floor_betas_deep.txt` at commit
`29b8903` on branch `ccr-d4a17dd0-7uu03r`), compiled with

    gcc -O3 -march=native -fopenmp -o cover_floor cover_floor.c -lm

and run as

    COVER_FLOOR_REACH=20000 ./cover_floor Q 'odd<=463' cover_floor_betas_deep.txt 400000 100000 n89_Q<Q>_s<seed>.txt <seed>
    COVER_FLOOR_REACH=60000 ./cover_floor Q 'odd<=997' cover_floor_betas_deep.txt 400000 100000 n167_Q<Q>_s<seed>.txt <seed>

The files `n89C_Q<Q>.txt` are the runs started from that session's complete cover
(`goldbach/sublinear/complete_cover_15907.txt` at commit `2552688`):

    COVER_FLOOR_REACH=20000 ./cover_floor Q 'odd<=463' cover_floor_betas_deep.txt 1000000 250000 n89C_Q<Q>.txt 5 complete_cover_15907.txt

and `n89L_Q14500_s3.txt` is one ten times longer run from random vectors (4000000 sweeps, 1000000
of burn-in, target 14,500, seed 3). Eight such runs were planned; the research session called the
series off after the first, because the runs from the complete cover had settled the question.

Each file is self-describing (a header line, then the lines the program writes). The analysis is the
research session's (`python3 cover_floor.py --reach files...`).
