# Output of the research session's `cover_floor` runs

Raw output files, produced on this branch's machine at the research session's request (24 November
2026) and not interpreted here. The program and its parameter file are that session's
(`goldbach/sublinear/cover_floor.c`, `cover_floor.py`, `cover_floor_betas_deep.txt` at commit
`29b8903` on branch `ccr-d4a17dd0-7uu03r`), compiled with

    gcc -O3 -march=native -fopenmp -o cover_floor cover_floor.c -lm

and run as

    COVER_FLOOR_REACH=20000 ./cover_floor Q 'odd<=463' cover_floor_betas_deep.txt 400000 100000 n89_Q<Q>_s<seed>.txt <seed>
    COVER_FLOOR_REACH=60000 ./cover_floor Q 'odd<=997' cover_floor_betas_deep.txt 400000 100000 n167_Q<Q>_s<seed>.txt <seed>

Each file is self-describing (a header line, then the lines the program writes). The analysis is the
research session's (`python3 cover_floor.py --reach files...`).
