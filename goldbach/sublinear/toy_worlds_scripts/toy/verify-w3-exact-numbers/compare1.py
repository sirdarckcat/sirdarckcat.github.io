import os, collections, math, sys
TH = "../w3-exact/"
def mine(q, n):
    gh = {}; gh0 = {}; dh = {}; dh0 = {}; top = []; hdr = None; lst = []
    for line in open(f"out/v_{q}_{n}.txt"):
        t = line.split()
        if t[0] == "q": hdr = dict(zip(t[0::2], (int(x) for x in t[1::2])))
        elif t[0] == "GH": gh[int(t[1])] = int(t[2]); 
        if t[0] == "GH" and int(t[3]): gh0[int(t[1])] = int(t[3])
        if t[0] == "DH":
            dh[int(t[1])] = int(t[2])
            if int(t[3]): dh0[int(t[1])] = int(t[3])
        if t[0] == "TOP": top.append((int(t[1]), int(t[2])))
        if t[0] == "LIST": lst.append((t[1], int(t[2]), int(t[4]), int(t[6])))
    return hdr, gh, gh0, dh, dh0, top, lst
def theirs(q, n):
    gh = collections.Counter(); gh0 = collections.Counter(); dh = collections.Counter(); top = []
    for line in open(TH + f"out_{q}_{n}.txt"):
        t = line.split()
        if t[0] == "GH" and int(t[1]) <= n:
            gh[int(t[2])] += int(t[3])
            if int(t[1]) == 0: gh0[int(t[2])] += int(t[3])
        if t[0] == "DH" and int(t[1]) <= n: dh[int(t[2])] += int(t[3])
        if t[0] == "TOP": top.append((int(t[1]), int(t[2])))
    return dict(gh), dict(gh0), dict(dh), top
if __name__ == "__main__":
    inst = [(3, n) for n in range(3, 19)] + [(5, n) for n in range(3, 13)] + [(7, n) for n in range(3, 11)] + [(9, n) for n in range(3, 10)]
    bad = 0; done = 0
    print("q n | Gmax (#) second | Dmax (#) | exceptions | mean G | best G with N'=0 | G-hist==theirs D-hist==theirs N'=0-hist==theirs top-attainers==theirs")
    for q, n in inst:
        if not os.path.exists(f"out/v_{q}_{n}.txt"): print(q, n, "not yet"); continue
        hdr, gh, gh0, dh, dh0, top, lst = mine(q, n)
        if sum(gh.values()) != q ** n: print(q, n, "incomplete"); continue
        done += 1
        tg, tg0, td, ttop = theirs(q, n)
        gs = sorted(gh, reverse=True); Gmax = gs[0]; Dmax = max(dh)
        mean = sum(g * c for g, c in gh.items()) / q ** n
        # necklace / moebius checks
        def mu(k):
            r = 1; d = 2
            while d * d <= k:
                if k % d == 0:
                    k //= d
                    if k % d == 0: return 0
                    r = -r
                d += 1
            if k > 1: r = -r
            return r
        neck = sum(mu(d) * q ** (n // d) for d in range(1, n + 1) if n % d == 0) // n
        okc = hdr["irr_n"] == neck and hdr["odd"] == (q ** n - q ** (n - 1)) // 2 and hdr["squarefree"] == q ** n - q ** (n - 1)
        mytop = sorted(v for v, g in top if g == Gmax); thtop = sorted(v for v, g in ttop if g == Gmax)
        pp = 3 if q == 9 else q
        if n % pp: gh0 = {}
        eq = (gh == tg, dh == td, gh0 == tg0, mytop == thtop if gh[Gmax] <= 300 else "n/a")
        if not all(eq) or not okc: bad += 1
        exc = gh.get(hdr["nrows"], 0)
        print(f"{q} {n:2d} | {Gmax} ({gh[Gmax]}) {gs[1]} | {Dmax} ({dh[Dmax]}) | {exc} | {mean:.2f} | {max(gh0) if gh0 else None} | {eq} tablechecks {okc}")
    print("instances done", done, "with any mismatch", bad)
