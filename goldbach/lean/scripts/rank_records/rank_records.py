#!/usr/bin/env python3
"""The running largest, second largest, ... values of the least Goldbach summand g(N).

    python3 -I rank_records.py cand.txt K [A B] > ranks.txt

cand.txt: lines "N g" for every even N with g(N) >= A ln(N)^2 - B, sorted by N (from lgs_scan).
Scanning N upwards, keep the K largest values seen so far (each with the first N that reached it;
equal values at different N are kept as separate entries).  An N *arrives at rank j* when g(N) is
larger than exactly j - 1 of the kept values: rank 1 is a new record, rank 2 a new runner-up, ...
The script lists the arrivals at each rank and checks that the K-th value stays above the threshold
of the scan (otherwise an arrival could have been missed).
"""
import math
import sys


def main():
    path, K = sys.argv[1], int(sys.argv[2])
    A = float(sys.argv[3]) if len(sys.argv) > 3 else 2.6
    B = float(sys.argv[4]) if len(sys.argv) > 4 else 250
    top = []                       # list of (g, N), decreasing in g, then increasing in N
    arrivals = [[] for _ in range(K + 1)]
    worst_margin = None
    for line in open(path):
        N, g = map(int, line.split())
        tau = A * math.log(N) ** 2 - B
        if len(top) == K:
            margin = top[-1][0] - tau
            if worst_margin is None or margin < worst_margin[0]:
                worst_margin = (margin, N)
            if g <= top[-1][0]:
                continue
        rank = 1 + sum(1 for (h, _) in top if h >= g)       # ties: the earlier N keeps the better rank
        if rank > K:
            continue
        top.insert(rank - 1, (g, N))
        del top[K:]
        arrivals[rank].append((N, g, [t[0] for t in top], [t[1] for t in top]))
    print(f"# arrivals by rank among the {K} largest values of g(N); threshold margin: the {K}-th value minus "
          f"the scan threshold was at least {worst_margin[0]:.0f} (at N = {worst_margin[1]})")
    for j in range(1, K + 1):
        print(f"\n## rank {j}: {len(arrivals[j])} arrivals   (N, g(N))")
        print(" ".join(f"({N},{g})" for N, g, _, _ in arrivals[j]))
    print("\n## final table")
    for j, (g, N) in enumerate(top, 1):
        print(f"{j} {N} {g}")


if __name__ == "__main__":
    main()
