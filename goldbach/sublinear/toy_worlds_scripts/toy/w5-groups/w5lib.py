#!/usr/bin/env python3
"""World 5 library: (1) k best points of a product (heap on a tree with <= 3 children), (2) the arc character,
(3) the rounded dynamic programme over partial sums with exact listing of the relaxed set R.
Pure python, exact integer arithmetic; meant for the small exhaustive tests (tests_small.py)."""
import heapq, math
from fractions import Fraction

# ---------- (1) World 1 ----------
def kbest_product(tables, k):
    """tables[i][c] = f_i(c).  Returns the k best (smallest) points of prod Z/r_i as (score, tuple of classes), in
    nondecreasing score, with a heap; every node has at most three children and exactly one parent."""
    m = len(tables)
    srt = [sorted(range(len(t)), key=lambda c: t[c]) for t in tables]           # classes by score
    val = [[tables[i][c] for c in srt[i]] for i in range(m)]
    gap = [val[i][1] - val[i][0] if len(val[i]) > 1 else math.inf for i in range(m)]
    order = sorted(range(m), key=lambda i: gap[i])                               # coordinates by first gap
    mm = sum(1 for i in range(m) if len(val[i]) > 1)                             # coordinates with a choice
    base = sum(v[0] for v in val)
    # node = (score, id, t, rank_t, parent id, kind)   t = position (1..mm) in `order` of the last nonzero rank
    nodes = [(base, 0, 0, None, None)]                                           # (score, t, rank, parent, kind)
    heap = [(base, 0)]; out = []; pushes = 0
    def rank_vector(nid):
        rk = [0] * m; chain = []
        while nid is not None: chain.append(nid); nid = nodes[nid][3]
        for nid in reversed(chain):                                              # replay from the root
            s, t, r, par, kind = nodes[nid]
            if kind == 'a' or kind == 'b': rk[order[t - 1]] = r
            elif kind == 'c': rk[order[t - 2]] = 0; rk[order[t - 1]] = 1
        return rk
    while heap and len(out) < k:
        s, nid = heapq.heappop(heap); _, t, r, par, kind = nodes[nid]
        rk = rank_vector(nid)
        out.append((s, tuple(srt[i][rk[i]] for i in range(m))))
        ch = []
        if t >= 1:
            i = order[t - 1]
            if r + 1 < len(val[i]): ch.append((s + val[i][r + 1] - val[i][r], t, r + 1, nid, 'a'))
        if t + 1 <= mm:
            i2 = order[t]
            ch.append((s + gap[i2], t + 1, 1, nid, 'b'))
            if t >= 1 and r == 1: ch.append((s - gap[order[t - 1]] + gap[i2], t + 1, 1, nid, 'c'))
        for c in ch:
            nodes.append(c); heapq.heappush(heap, (c[0], len(nodes) - 1)); pushes += 1
    return out, pushes

# ---------- (2) the arc ----------
def arc_data(mods):
    P = math.prod(mods)
    u = [pow(P // r % r, -1, r) for r in mods]
    return P, u
def crt_int(mods, x):                       # x = residue tuple -> integer in [0, P)
    P, u = arc_data(mods)
    return sum(c * ui * (P // r) for c, ui, r in zip(x, u, mods)) % P

# ---------- (3) rounded DP ----------
def rounded_dp(mods, tables, X, B):
    """rho_i(c) = floor(B * frac(c u_i / r_i)).  V[t][b] = min partial score over the first t coordinates with rounded
    sum b mod B.  Relaxed set R = {x : sum rho_i(x_i) mod B in {-(m-1),...,A-1}}, A = ceil(B X / P)."""
    P, u = arc_data(mods); m = len(mods); INF = math.inf
    rho = [[(B * ((c * ui) % r)) // r for c in range(r)] for ui, r in zip(u, mods)]
    V = [[INF] * B for _ in range(m + 1)]; V[0][0] = 0
    for t in range(m):
        cur, nxt = V[t], V[t + 1]
        for b in range(B):
            if cur[b] == INF: continue
            for c in range(mods[t]):
                b2 = (b + rho[t][c]) % B; v = cur[b] + tables[t][c]
                if v < nxt[b2]: nxt[b2] = v
    A = -((-B * X) // P)
    targets = sorted({b % B for b in range(-(m - 1), A)})
    return rho, V, targets
def list_relaxed(mods, tables, rho, V, targets, theta):
    """all x in R with S(x) <= theta, by backtracking on the stored tables; also counts the nodes visited"""
    m = len(mods); B = len(V[0]); out = []; visited = [0]
    def rec(t, b, budget, suffix):
        visited[0] += 1
        if t == 0:
            if b == 0 and budget >= 0: out.append(tuple(suffix[::-1]))
            return
        for c in range(mods[t - 1]):
            bp = (b - rho[t - 1][c]) % B; rest = budget - tables[t - 1][c]
            if V[t - 1][bp] <= rest:
                suffix.append(c); rec(t - 1, bp, rest, suffix); suffix.pop()
    for b in targets:
        if V[m][b] <= theta: rec(m, b, theta, [])
    return out, visited[0]
