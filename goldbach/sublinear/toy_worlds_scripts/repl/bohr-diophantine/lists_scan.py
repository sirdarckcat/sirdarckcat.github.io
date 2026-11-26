#!/usr/bin/env python3
"""(a) Lists of good classes at the first J later primes of the real cover: members of the real window agreeing with
all lists / with the most lists.  Three exact methods, same answers, different work:
  scan    : every k < K, J lookups                                   (work K*J)
  wheel   : lattice cosets k = c (mod r_a r_b [r_c]) with a small representative, then lookups
            (for 'at least t of J': a Turan family of pairs/triples, every t-subset of the primes contains one)
  arc-mitm: two half-lists sorted on the CRT arc, merge               (work prod|G|^(1/2) + output), exact in uint64 for J <= 7
"""
import sys, math, time, itertools, numpy as np
from base import *
LATER = [int(s) for s in primes_upto(700) if s > 463]
def lists(J, rho):
    out = []
    for s in LATER[:J]:
        f, g = tables(s); n = int(math.ceil(rho * s))
        order = np.argsort(-g, kind="stable")[:n]
        ind = np.zeros(s, dtype=np.uint8); ind[order] = 1
        out.append((s, np.sort(order), ind, g))
    return out
def scan(L):
    t = time.time(); tot = np.zeros(K, dtype=np.uint8)
    for s, G, ind, g in L: tot += np.resize(ind, K)
    return tot, time.time() - t
def crt_many(cls_list, mods):
    """all combinations of classes -> residues modulo prod(mods) (uint64 arrays)"""
    res = np.zeros(1, dtype=np.uint64); Pm = 1
    for G, s in zip(cls_list, mods):
        inv = pow(Pm, -1, s)
        # k = res + Pm * ((c - res) * inv mod s)
        r_ = (res % np.uint64(s)).astype(np.int64)
        tt = ((G[None, :].astype(np.int64) - r_[:, None]) % s * inv) % s
        res = (res[:, None] + np.uint64(Pm) * tt.astype(np.uint64)).ravel(); Pm *= s
    return res, Pm
def wheel_all(L, npin):
    """all members agreeing with every list: CRT on the first npin lists, lift into the window, lookups for the rest"""
    t = time.time(); work = 0
    res, Pm = crt_many([G for _, G, _, _ in L[:npin]], [s for s, _, _, _ in L[:npin]]); work += len(res)
    if Pm < K:
        reps = (K + Pm - 1) // Pm
        cand = (res[:, None] + np.uint64(Pm) * np.arange(reps, dtype=np.uint64)[None, :]).ravel(); cand = cand[cand < K]
    else: cand = res[res < K]
    for s, G, ind, g in L[npin:]:
        work += len(cand); cand = cand[ind[(cand % np.uint64(s)).astype(np.int64)] == 1]
    return np.sort(cand), work, time.time() - t
def wheel_atleast(L, tmin, size):
    """all members agreeing with at least tmin lists: Turan family of `size`-subsets (groups, all subsets inside a group)"""
    J = len(L); t = time.time(); work = 0
    ngroups = (tmin - 1) // (size - 1)                    # every tmin-subset has `size` elements in one group
    groups = [list(range(J))[i::ngroups] for i in range(ngroups)]
    fam = [c for gr in groups for c in itertools.combinations(gr, size)]
    found = []
    for T in fam:
        res, Pm = crt_many([L[i][1] for i in T], [L[i][0] for i in T]); work += len(res)
        if Pm < K:
            reps = (K + Pm - 1) // Pm
            cand = (res[:, None] + np.uint64(Pm) * np.arange(reps, dtype=np.uint64)[None, :]).ravel(); cand = cand[cand < K]
        else: cand = res[res < K]
        tot = np.full(len(cand), size, dtype=np.int16)
        for i, (s, G, ind, g) in enumerate(L):
            if i in T: continue
            tot += ind[(cand % np.uint64(s)).astype(np.int64)]
        work += len(cand) * (J - size)
        found.append(cand[tot >= tmin])
    return np.unique(np.concatenate(found)), work, len(fam), time.time() - t
def arc_mitm(L):
    """all members agreeing with every list, by sorting two half-lists on the arc; exact for prod s < 2^63"""
    J = len(L); h = J // 2; t = time.time()
    a, PA = crt_many([G for _, G, _, _ in L[:h]], [s for s, _, _, _ in L[:h]])
    b, PB = crt_many([G for _, G, _, _ in L[h:]], [s for s, _, _, _ in L[h:]])
    P = PA * PB; assert P < 2 ** 63
    eA = PB * pow(PB, -1, PA) % P; eB = PA * pow(PA, -1, PB) % P
    # positions on Z/P: x = a*eA + b*eB mod P ; python ints for the multiplications mod P (object arrays avoided: split multiply)
    def mulmod(v, e):
        out = np.empty(len(v), dtype=np.uint64)
        vv = v.tolist()
        for i in range(len(vv)): out[i] = vv[i] * e % P
        return out
    xa = mulmod(a, eA); xb = np.sort(mulmod(b, eB))
    lo = (np.uint64(P) - xa) % np.uint64(P)                # need xb in [lo, lo+K) mod P
    i0 = np.searchsorted(xb, lo, side="left"); i1 = np.searchsorted(xb, lo + np.uint64(K), side="left")
    sol = []
    for i in np.nonzero(i1 > i0)[0]:
        for j in range(i0[i], i1[i]): sol.append((int(xa[i]) + int(xb[j])) % P)
    # wrap-around: lo + K > P
    wrap = np.nonzero(lo + np.uint64(K) > np.uint64(P))[0]
    for i in wrap:
        j1 = np.searchsorted(xb, int(lo[i]) + K - P, side="left")
        for j in range(j1): sol.append((int(xa[i]) + int(xb[j])) % P)
    return np.array(sorted(sol), dtype=np.uint64), len(a) + len(b), time.time() - t
if __name__ == "__main__":
    print(f"K = {K}; later primes {LATER[:12]}")
    for rho in (0.05, 0.10, 0.20):
        for J in (4, 6, 8, 10, 12):
            L = lists(J, rho); sizes = [len(G) for _, G, _, _ in L]
            lnP = sum(math.log(s) for s, _, _, _ in L); D = lnP - math.log(K)
            dens = sum(math.log(n) for n in sizes) / D if D > 0 else float("inf")
            tot, ts = scan(L); mx = int(tot.max()); hist = np.bincount(tot, minlength=J + 1)
            allk = np.nonzero(tot == J)[0]
            print(f"\nrho {rho:.2f} J {J}: list sizes {sizes[0]}..{sizes[-1]}; D = ln(P_J/K) = {D:.2f}; knapsack density ln prod|G| / D = {dens:.2f}; expected members in all lists {K * math.prod(n / s for n, (s, _, _, _) in zip(sizes, L)):.2f}")
            print(f"  scan: {ts:.2f} s, work K*J = {K * J:.2e}; max agreement {mx}; members by agreement (top 4): {[(a, int(hist[a])) for a in range(J, max(J - 4, -1), -1)]}")
            for npin in (2, 3):
                w, work, tw = wheel_all(L, npin)
                print(f"  wheel on {npin} lists (all J agree): {len(w)} members, identical to scan: {np.array_equal(w, allk.astype(np.uint64))}; work {work:.2e}; {tw:.3f} s")
            if J <= 7:
                m, work, tm = arc_mitm(L)
                print(f"  arc meet-in-the-middle (all J agree): {len(m)} members, identical: {np.array_equal(m, allk.astype(np.uint64))}; lists {work:.2e}; {tm:.3f} s")
            else:
                print(f"  arc meet-in-the-middle: half-lists of {math.prod(sizes[:J // 2]):.2e} and {math.prod(sizes[J // 2:]):.2e} (not run above 7 primes: more than the scan from 5e6)")
            # at least t of J: the level where the window has between 1 and ~1000 members
            for tmin in range(mx, max(mx - 2, 2), -1):
                want = np.nonzero(tot >= tmin)[0].astype(np.uint64)
                for size in (2, 3):
                    if (tmin - 1) // (size - 1) < 1: continue
                    got, work, nf, tw = wheel_atleast(L, tmin, size)
                    print(f"  at least {tmin} of {J}: {len(want)} members; Turan family of {nf} {'pairs' if size == 2 else 'triples'}: identical {np.array_equal(got, want)}; work {work:.2e} ({work / (K * J):.4f} of the scan); {tw:.2f} s")
