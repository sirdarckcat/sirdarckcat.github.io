from vlib import W
for q, n in [(3, 18), (9, 9)]:
    w = W(q)
    with open(f"out/list_{q}_{n}.txt", "w") as fo:
        for sq in ([1] if q != 9 else [1, 2, 3, 6]):
            for N in w.family(n, sq): fo.write(f"fam{sq} {w.index(N)}\n")
