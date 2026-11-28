#!/usr/bin/env python3
"""Test of the thinning law on the research session's canonical tables.

Usage: python3 -I thin.py ideal_tilt_213070.txt
(the file is goldbach/sublinear/ideal_tilt_213070.txt on branch ccr-d4a17dd0-7uu03r).

k_z(N) = number of rows q < Q with N - q free of prime factors <= z.  If the primes in
(z, z'] killed the rows left at depth z independently, each with probability 1 - theta,
theta = prod_{z < s <= z'} (1 - 1/s), then for every b'

    E[exp(-b' k_z')] = E[(1 - theta (1 - exp(-b')))^k_z] = Z_z(b),
                                        exp(-b) = 1 - theta (1 - exp(-b')),
    <k_z'>_b' = <k_z>_b * theta exp(-b') / (1 - theta + theta exp(-b')).

The tables give, for each depth, beta, <k>, sd and S(beta) = ln(states) + ln Z + beta <k>,
so ln Z(beta) = S - ln(states) - beta <k>.  For each pair of depths the script prints the
deeper table's ln Z and <k> next to the values the shallower table predicts.
"""
import sys, math, re
import numpy as np

def read_tables(path):
    blocks = {}; cur = None
    for line in open(path):
        m = re.match(r"# t(\d+)\.txt: .* z=(\d+) ", line)
        if m:
            cur = int(m.group(2)); blocks[cur] = {"rows": [], "cut": None, "cost": None}; continue
        if cur is None: continue
        m = re.match(r"# states ln=([\d.]+);.*p_z=([\d.]+);", line)
        if m:
            blocks[cur]["lnstates"] = float(m.group(1)); blocks[cur]["p"] = float(m.group(2)); continue
        m = re.match(r"\s+one expected success after e\^([\d.]+) tested N, down to k = (\d+) rows", line)
        if m:
            blocks[cur]["cost"] = float(m.group(1)); blocks[cur]["cut"] = int(m.group(2)); continue
        f = line.split()
        if len(f) >= 6 and not line.startswith("#") and "." in f[0]:
            try: v = [float(x) for x in f[:5]]
            except ValueError: continue
            if v[0] <= 5.0: blocks[cur]["rows"].append(v)
    tab = {}
    for z, b in blocks.items():
        a = np.array(b["rows"]); beta, k, sd, S = a[:, 0], a[:, 1], a[:, 2], a[:, 3]
        tab[z] = dict(beta=beta, k=k, sd=sd, lnZ=S - b["lnstates"] - beta * k, p=b["p"],
                      cut=b["cut"], cost=b["cost"])
    return tab

def primes_upto(n):
    sv = np.ones(n + 1, dtype=bool); sv[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if sv[i]: sv[i * i::i] = False
    return [int(x) for x in np.nonzero(sv)[0]]

def theta(P, z, z2):
    t = 1.0
    for s in P:
        if z < s <= z2: t *= 1 - 1 / s
    return t

if __name__ == "__main__":
    tab = read_tables(sys.argv[1]); P = primes_upto(60000); zs = sorted(tab)
    print("shallower z -> deeper z': at the deeper table's beta', the matching beta of the shallower one,")
    print("then ln Z and <k> of the deeper table: measured | predicted by independent thinning")
    for i, z in enumerate(zs):
        for z2 in zs[i + 1:]:
            th = theta(P, z, z2); par, ch = tab[z], tab[z2]
            print(f"\n{z} -> {z2}: theta = {th:.4f}; the shallower table is used up to beta = {-math.log(1 - th):.3f}")
            for target in (0.24, 0.48, 0.95, 1.45, 2.05, 3.10, 5.0):
                j = int(np.argmin(np.abs(ch["beta"] - target))); bp = ch["beta"][j]
                x = 1 - th * (1 - math.exp(-bp)); b = -math.log(x)
                lnZpred = float(np.interp(b, par["beta"], par["lnZ"]))
                kpar = float(np.interp(b, par["beta"], par["k"]))
                kpred = kpar * th * math.exp(-bp) / x
                print(f"  beta'={bp:4.2f}  beta={b:5.3f}   ln Z: {ch['lnZ'][j]:9.2f} | {lnZpred:9.2f}  ({ch['lnZ'][j] - lnZpred:+8.2f})"
                      f"    <k>: {ch['k'][j]:7.1f} | {kpred:7.1f}  (measured/predicted {ch['k'][j] / kpred:.4f})")
